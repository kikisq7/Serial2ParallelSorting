#include <algorithm>
#include <iostream>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

static const int CUTOFF = 2000;

int partition(std::vector<int>& a, int low, int high) {
    int pivot = a[high];
    int i = low - 1;
    for (int j = low; j < high; ++j) {
        if (a[j] <= pivot) {
            ++i;
            std::swap(a[i], a[j]);
        }
    }
    std::swap(a[i + 1], a[high]);
    return i + 1;
}

void quicksort_parallel(std::vector<int>& a, int low, int high) {
    if (low >= high) return;
    int n = high - low + 1;
    if (n <= CUTOFF) {
        std::sort(a.begin() + low, a.begin() + high + 1);
        return;
    }

    int pi = partition(a, low, high);

    #pragma omp task shared(a) if (high - low > CUTOFF)
    quicksort_parallel(a, low, pi - 1);

    #pragma omp task shared(a) if (high - low > CUTOFF)
    quicksort_parallel(a, pi + 1, high);
}

void quicksort_parallel_entry(std::vector<int>& a) {
    #pragma omp parallel
    {
        #pragma omp single nowait
        quicksort_parallel(a, 0, static_cast<int>(a.size()) - 1);
    }
}

#if !defined(SORTING_LIBRARY) && !defined(BENCHMARK_MODE)
void print_array(const std::vector<int>& arr) {
    for (const auto& v : arr) std::cout << v << ' ';
    std::cout << '\n';
}
#endif

#if !defined(SORTING_LIBRARY) && !defined(BENCHMARK_MODE)
int main() {
    std::vector<int> data{10, 7, 8, 9, 1, 5, 12, 4, 6, 3, 11, 2};
    std::cout << "Original array: ";
    print_array(data);
    quicksort_parallel_entry(data);
    std::cout << "Sorted array: ";
    print_array(data);
    auto check = data;
    std::sort(check.begin(), check.end());
    if (check != data) {
        std::cerr << "Parallel quicksort failed" << std::endl;
        return 1;
    }
    return 0;
}
#endif
