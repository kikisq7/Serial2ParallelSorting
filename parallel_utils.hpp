#pragma once

#include <algorithm>
#include <condition_variable>
#include <cstddef>
#include <functional>
#include <mutex>
#include <thread>
#include <utility>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

inline constexpr std::size_t SORTING_TARGET_TASKS_PER_WORKER = 2048;

inline std::size_t sorting_thread_count(std::size_t task_count) {
    if (task_count == 0) {
        return 0;
    }
    const unsigned int hardware_threads = std::thread::hardware_concurrency();
    const std::size_t workers = hardware_threads == 0 ? 1U : static_cast<std::size_t>(hardware_threads);
    const std::size_t chunk_limited_workers =
        (task_count + SORTING_TARGET_TASKS_PER_WORKER - 1) / SORTING_TARGET_TASKS_PER_WORKER;
    const std::size_t requested_workers = std::max<std::size_t>(task_count > 1 ? 2U : 1U, chunk_limited_workers);
    return std::max<std::size_t>(1, std::min({workers, task_count, requested_workers}));
}

inline std::vector<std::pair<std::size_t, std::size_t>> chunk_ranges(std::size_t task_count) {
    const std::size_t workers = sorting_thread_count(task_count);
    std::vector<std::pair<std::size_t, std::size_t>> ranges;
    if (workers == 0) {
        return ranges;
    }

    ranges.reserve(workers);
    const std::size_t base = task_count / workers;
    const std::size_t extra = task_count % workers;
    std::size_t start = 0;

    for (std::size_t worker = 0; worker < workers; ++worker) {
        const std::size_t length = base + (worker < extra ? 1U : 0U);
        const std::size_t stop = start + length;
        ranges.emplace_back(start, stop);
        start = stop;
    }

    return ranges;
}

class SortingThreadTeam {
public:
    explicit SortingThreadTeam(std::size_t thread_count) {
        workers_.reserve(thread_count);
        for (std::size_t worker_index = 0; worker_index < thread_count; ++worker_index) {
            workers_.emplace_back([this, worker_index]() { worker_loop(worker_index); });
        }
    }

    SortingThreadTeam(const SortingThreadTeam&) = delete;
    SortingThreadTeam& operator=(const SortingThreadTeam&) = delete;

    ~SortingThreadTeam() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            stopping_ = true;
            work_ready_.notify_all();
        }
        for (auto& worker : workers_) {
            if (worker.joinable()) {
                worker.join();
            }
        }
    }

    template <typename Worker>
    void run(const std::vector<std::pair<std::size_t, std::size_t>>& ranges, Worker&& worker) {
        std::unique_lock<std::mutex> lock(mutex_);
        idle_.wait(lock, [this]() { return !busy_; });

        busy_ = true;
        ranges_ = &ranges;
        task_ = [&worker](std::size_t begin, std::size_t end) { worker(begin, end); };
        remaining_ = ranges.size();
        ++generation_;
        work_ready_.notify_all();

        completed_.wait(lock, [this]() { return remaining_ == 0; });

        task_ = nullptr;
        ranges_ = nullptr;
        busy_ = false;
        lock.unlock();
        idle_.notify_one();
    }

private:
    void worker_loop(std::size_t worker_index) {
        std::size_t seen_generation = 0;
        std::unique_lock<std::mutex> lock(mutex_);

        while (true) {
            work_ready_.wait(lock, [this, seen_generation]() { return stopping_ || generation_ != seen_generation; });
            if (stopping_) {
                return;
            }

            const std::size_t current_generation = generation_;
            const auto* ranges = ranges_;
            const auto task = task_;
            const bool has_work = ranges != nullptr && worker_index < ranges->size();
            std::pair<std::size_t, std::size_t> range{0, 0};
            if (has_work) {
                range = (*ranges)[worker_index];
            }
            seen_generation = current_generation;

            lock.unlock();
            if (has_work) {
                task(range.first, range.second);
            }
            lock.lock();

            if (has_work) {
                --remaining_;
                if (remaining_ == 0) {
                    completed_.notify_one();
                }
            }
        }
    }

    std::vector<std::thread> workers_;
    std::mutex mutex_;
    std::condition_variable work_ready_;
    std::condition_variable completed_;
    std::condition_variable idle_;
    bool stopping_ = false;
    bool busy_ = false;
    std::size_t generation_ = 0;
    std::size_t remaining_ = 0;
    const std::vector<std::pair<std::size_t, std::size_t>>* ranges_ = nullptr;
    std::function<void(std::size_t, std::size_t)> task_;
};

inline SortingThreadTeam& sorting_thread_team() {
    static SortingThreadTeam team([]() -> std::size_t {
        const unsigned int hardware_threads = std::thread::hardware_concurrency();
        return hardware_threads == 0 ? 1U : static_cast<std::size_t>(hardware_threads);
    }());
    return team;
}

template <typename Worker>
inline void parallel_for_chunks(std::size_t task_count, Worker&& worker) {
#ifdef _OPENMP
    if (task_count == 0) {
        return;
    }
    if (task_count == 1) {
        worker(0, 1);
        return;
    }
#pragma omp parallel for schedule(static)
    for (std::ptrdiff_t t = 0; t < static_cast<std::ptrdiff_t>(task_count); ++t) {
        const std::size_t b = static_cast<std::size_t>(t);
        worker(b, b + 1);
    }
#else
    const auto ranges = chunk_ranges(task_count);
    if (ranges.empty()) {
        return;
    }
    if (ranges.size() == 1) {
        worker(ranges.front().first, ranges.front().second);
        return;
    }
    sorting_thread_team().run(ranges, std::forward<Worker>(worker));
#endif
}
