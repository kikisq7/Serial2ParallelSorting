#include <utility>
#include <vector>

#include "../parallel_utils.hpp"

static int qp_partition(std::vector<int>& arr, int low, int high) {
    const int pivot = arr[high];
    int i = low - 1;
    for (int j = low; j < high; ++j) {
        if (arr[j] < pivot) {
            ++i;
            std::swap(arr[i], arr[j]);
        }
    }
    std::swap(arr[i + 1], arr[high]);
    return i + 1;
}

static void parallel_quicksort_range(std::vector<int>& arr, int low, int high) {
    if (low >= high) {
        return;
    }
    std::vector<std::pair<int, int>> current{{low, high}};

    std::vector<int> pivots;
    std::vector<unsigned char> valid;
    pivots.reserve(arr.size());
    valid.reserve(arr.size());

    while (!current.empty()) {
        pivots.resize(current.size(), 0);
        valid.resize(current.size(), static_cast<unsigned char>(0));

        parallel_for_chunks(current.size(), [&](std::size_t begin, std::size_t end) {
            for (std::size_t idx = begin; idx < end; ++idx) {
                const auto& range = current[idx];
                if (range.first < range.second) {
                    pivots[idx] = qp_partition(arr, range.first, range.second);
                    valid[idx] = 1;
                }
            }
        });

        std::vector<std::pair<int, int>> next_ranges;
        next_ranges.reserve(current.size() * 2);

        for (std::size_t idx = 0; idx < current.size(); ++idx) {
            if (valid[idx] == 0) {
                continue;
            }
            const int range_low = current[idx].first;
            const int range_high = current[idx].second;
            const int pivot_idx = pivots[idx];

            if (range_low < pivot_idx - 1) {
                next_ranges.emplace_back(range_low, pivot_idx - 1);
            }
            if (pivot_idx + 1 < range_high) {
                next_ranges.emplace_back(pivot_idx + 1, range_high);
            }
        }

        current.swap(next_ranges);
    }
}

void quicksort_parallel_entry(std::vector<int>& arr) {
    if (arr.size() < 2) {
        return;
    }
    parallel_quicksort_range(arr, 0, static_cast<int>(arr.size()) - 1);
}
