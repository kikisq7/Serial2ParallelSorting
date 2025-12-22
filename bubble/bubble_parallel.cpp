#include <algorithm>
#include <iostream>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

// Odd-even transposition sort (parallelizable variant of bubble sort)
void bubble_sort_parallel(std::vector<int>& arr) {
    const int n = static_cast<int>(arr.size());
    if (n <= 1) return;
    bool swapped = true;
    while (swapped) {
        swapped = false;
        // Even phase: compare (0,1), (2,3), ...
        #pragma omp parallel for reduction(|| : swapped) schedule(static) if(n > 100)
        for (int i = 0; i + 1 < n; i += 2) {
            if (arr[i] > arr[i + 1]) {
                std::swap(arr[i], arr[i + 1]);
                swapped = true;
            }
        }
        // Odd phase: compare (1,2), (3,4), ...
        #pragma omp parallel for reduction(|| : swapped) schedule(static) if(n > 100)
        for (int i = 1; i + 1 < n; i += 2) {
            if (arr[i] > arr[i + 1]) {
                std::swap(arr[i], arr[i + 1]);
                swapped = true;
            }
        }
    }
}

#ifndef BENCHMARK_MODE
#ifndef SORTING_LIBRARY
void print_array(const std::vector<int>& arr) {
    for (const auto& v : arr) std::cout << v << ' ';
    std::cout << '\n';
}

int main() {
    std::vector<int> arr{64, 34, 25, 12, 22, 11, 90, 5, 3, 8, 7, 2};
    std::cout << "Original array: ";
    print_array(arr);
    bubble_sort_parallel(arr);
    std::cout << "Sorted array: ";
    print_array(arr);
    // Simple correctness check
    auto check = arr;
    std::sort(check.begin(), check.end());
    if (arr != check) {
        std::cerr << "Parallel bubble sort failed" << std::endl;
        return 1;
    }
    return 0;
}
#endif
#endif  // BENCHMARK_MODE