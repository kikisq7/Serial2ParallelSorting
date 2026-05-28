#include <iostream>
#include <vector>
#include "parallel_utils.hpp"

void bubble_sort(std::vector<int>& arr) {
    int n = static_cast<int>(arr.size());
    for (int i = 0; i < n; ++i) {
        bool swapped = false;
        for (int j = 0; j < n - i - 1; ++j) {
            if (arr[j] > arr[j + 1]) {
                std::swap(arr[j], arr[j + 1]);
                swapped = true;
            }
        }
        if (!swapped) {
            break;
        }
    }
}

void bubble_sort_parallel(std::vector<int>& arr) {
    const std::size_t n = arr.size();
    if (n < 2) {
        return;
    }

    for (std::size_t phase = 0; phase < n; ++phase) {
        const std::size_t start = phase % 2;
        const std::size_t pair_count = (n - start) / 2;
        parallel_for_chunks(pair_count, [&](std::size_t begin, std::size_t end) {
            for (std::size_t pair_idx = begin; pair_idx < end; ++pair_idx) {
                const std::size_t j = start + 2 * pair_idx;
                if (arr[j] > arr[j + 1]) {
                    std::swap(arr[j], arr[j + 1]);
                }
            }
        });
    }
}

#ifndef BENCHMARK_MODE
void print_array(const std::vector<int>& arr) {
    for (const auto& v : arr) {
        std::cout << v << " ";
    }
    std::cout << std::endl;
}

int main() {
    std::vector<int> arr{64, 34, 25, 12, 22, 11, 90};
    std::cout << "Original array: ";
    print_array(arr);
    bubble_sort_parallel(arr);
    std::cout << "Sorted array: ";
    print_array(arr);
    return 0;
}
#endif
