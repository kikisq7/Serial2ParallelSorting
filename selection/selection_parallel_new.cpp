#include <algorithm>
#include <cstddef>
#include <vector>

#include "../parallel_utils.hpp"

static void parallel_selection_segment(std::vector<int>& arr) {
    const std::size_t n = arr.size();
    if (n < 2) {
        return;
    }

    std::vector<std::size_t> local_mins;
    local_mins.reserve(std::min<std::size_t>(n, 512U));

    for (std::size_t i = 0; i + 1 < n; ++i) {
        const auto ranges = chunk_ranges(static_cast<std::size_t>(n - i));
        local_mins.assign(ranges.size(), i);

        parallel_for_chunks(ranges.size(), [&](std::size_t begin, std::size_t end) {
            for (std::size_t range_idx = begin; range_idx < end; ++range_idx) {
                const std::size_t range_begin = i + ranges[range_idx].first;
                const std::size_t range_end = i + ranges[range_idx].second;
                std::size_t min_idx = range_begin;

                for (std::size_t j = range_begin + 1; j < range_end; ++j) {
                    if (arr[j] < arr[min_idx]) {
                        min_idx = j;
                    }
                }
                local_mins[range_idx] = min_idx;
            }
        });

        std::size_t min_idx = local_mins.front();
        for (std::size_t candidate : local_mins) {
            if (arr[candidate] < arr[min_idx]) {
                min_idx = candidate;
            }
        }
        std::swap(arr[i], arr[min_idx]);
    }
}

void parallelSelectionSort(std::vector<int>& arr, int left, int right) {
    if (left >= right) {
        return;
    }
    std::vector<int> segment(arr.begin() + left, arr.begin() + right + 1);
    parallel_selection_segment(segment);
    std::copy(segment.begin(), segment.end(), arr.begin() + left);
}
