#include <algorithm>
#include <vector>

void parallelSelectionSort(std::vector<int>& arr, int left, int right) {
    if (left >= right) {
        return;
    }

    for (int i = left; i < right; ++i) {
        int min_idx = i;

#ifdef _OPENMP
#pragma omp parallel
        {
            int local_min = i;
#pragma omp for nowait schedule(static)
            for (int j = i; j <= right; ++j) {
                if (arr[static_cast<std::size_t>(j)] < arr[static_cast<std::size_t>(local_min)]) {
                    local_min = j;
                }
            }
#pragma omp critical
            {
                if (arr[static_cast<std::size_t>(local_min)] < arr[static_cast<std::size_t>(min_idx)]) {
                    min_idx = local_min;
                }
            }
        }
#else
        for (int j = i + 1; j <= right; ++j) {
            if (arr[static_cast<std::size_t>(j)] < arr[static_cast<std::size_t>(min_idx)]) {
                min_idx = j;
            }
        }
#endif

        if (min_idx != i) {
            std::swap(arr[static_cast<std::size_t>(i)], arr[static_cast<std::size_t>(min_idx)]);
        }
    }
}
