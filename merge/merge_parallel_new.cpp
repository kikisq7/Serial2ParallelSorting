#include <algorithm>
#include <cstddef>
#include <vector>

#include "../parallel_utils.hpp"

static void merge_runs(const std::vector<int>& src, std::vector<int>& dest,
                       std::size_t left, std::size_t mid, std::size_t right) {
    std::size_t i = left;
    std::size_t j = mid;
    std::size_t k = left;

    while (i < mid && j < right) {
        if (src[i] <= src[j]) {
            dest[k++] = src[i++];
        } else {
            dest[k++] = src[j++];
        }
    }

    while (i < mid) {
        dest[k++] = src[i++];
    }

    while (j < right) {
        dest[k++] = src[j++];
    }
}

static void parallel_merge_segment(std::vector<int>& buf) {
    if (buf.size() <= 1) {
        return;
    }

    std::vector<int> src = buf;
    std::vector<int> dest(src.size(), 0);

    std::size_t width = 1;

    while (width < src.size()) {
        const std::size_t merge_count =
            (src.size() + 2 * width - 1) / (2 * width);

        parallel_for_chunks(merge_count, [&](std::size_t begin, std::size_t end) {
            for (std::size_t task_idx = begin; task_idx < end; ++task_idx) {
                const std::size_t run_left = task_idx * 2 * width;
                const std::size_t run_mid = std::min(run_left + width, src.size());
                const std::size_t run_right = std::min(run_left + 2 * width, src.size());

                if (run_mid < run_right) {
                    merge_runs(src, dest, run_left, run_mid, run_right);
                } else {
                    for (std::size_t idx = run_left; idx < run_right; ++idx) {
                        dest[idx] = src[idx];
                    }
                }
            }
        });

        src.swap(dest);
        width *= 2;
    }

    buf = std::move(src);
}

void parallelMergeSort(std::vector<int>& arr, int left, int right) {
    if (left >= right) {
        return;
    }

    std::vector<int> segment(arr.begin() + left, arr.begin() + right + 1);
    parallel_merge_segment(segment);
    std::copy(segment.begin(), segment.end(), arr.begin() + left);
}
