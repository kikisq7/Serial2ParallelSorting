#include <algorithm>
#include <vector>

void parallelInsertionSort(std::vector<int>& arr, int left, int right) {
    if (left >= right) {
        return;
    }

    const int n = right - left + 1;
    std::vector<int> output(static_cast<std::size_t>(n));

#ifdef _OPENMP
#pragma omp parallel for schedule(static)
#endif
    for (int offset = 0; offset < n; ++offset) {
        const int i = left + offset;
        const int value = arr[static_cast<std::size_t>(i)];
        int rank = 0;

        for (int j = left; j <= right; ++j) {
            const int other = arr[static_cast<std::size_t>(j)];
            if (other < value || (other == value && j < i)) {
                ++rank;
            }
        }

        output[static_cast<std::size_t>(rank)] = value;
    }

    std::copy(output.begin(), output.end(), arr.begin() + left);
}
