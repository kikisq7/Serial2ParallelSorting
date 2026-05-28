#include <algorithm>
#include <cstddef>
#include <iterator>
#include <vector>

#include "../parallel_utils.hpp"

static void insertion_parallel_segment(std::vector<int>& arr) {
    const std::size_t n = arr.size();
    if (n < 2) {
        return;
    }

    std::vector<std::size_t> counts;
    counts.reserve(std::min<std::size_t>(n, 512U));

    for (std::size_t i = 1; i < n; ++i) {
        const int key = arr[i];
        const auto ranges = chunk_ranges(static_cast<std::size_t>(i));
        counts.assign(ranges.size(), 0);

        parallel_for_chunks(ranges.size(), [&](std::size_t begin, std::size_t end) {
            for (std::size_t range_idx = begin; range_idx < end; ++range_idx) {
                std::size_t local = 0;
                for (std::size_t j = ranges[range_idx].first; j < ranges[range_idx].second; ++j) {
                    if (arr[j] <= key) {
                        ++local;
                    }
                }
                counts[range_idx] = local;
            }
        });

        std::size_t position = 0;
        for (std::size_t count : counts) {
            position += count;
        }
        if (position == i) {
            continue;
        }

        std::vector<int> segment(arr.begin() + static_cast<std::ptrdiff_t>(position),
                                arr.begin() + static_cast<std::ptrdiff_t>(i));

        parallel_for_chunks(segment.size(), [&](std::size_t begin, std::size_t end) {
            for (std::size_t offset = begin; offset < end; ++offset) {
                arr[position + offset + 1] = segment[offset];
            }
        });

        arr[position] = key;
    }
}

void parallelInsertionSort(std::vector<int>& arr, int left, int right) {
    if (left >= right) {
        return;
    }
    std::vector<int> segment(arr.begin() + left, arr.begin() + right + 1);
    insertion_parallel_segment(segment);
    std::copy(segment.begin(), segment.end(), arr.begin() + left);
}
