#include <algorithm>
#include <vector>

namespace merge_parallel_detail {

void mergeBlock(const std::vector<int>& source, std::vector<int>& dest, int left, int mid, int right) {
    int i = left;
    int j = mid;
    int k = left;

    while (i < mid && j < right) {
        if (source[static_cast<std::size_t>(i)] <= source[static_cast<std::size_t>(j)]) {
            dest[static_cast<std::size_t>(k++)] = source[static_cast<std::size_t>(i++)];
        } else {
            dest[static_cast<std::size_t>(k++)] = source[static_cast<std::size_t>(j++)];
        }
    }

    while (i < mid) {
        dest[static_cast<std::size_t>(k++)] = source[static_cast<std::size_t>(i++)];
    }
    while (j < right) {
        dest[static_cast<std::size_t>(k++)] = source[static_cast<std::size_t>(j++)];
    }
}

}  // namespace merge_parallel_detail

void parallelMergeSort(std::vector<int>& arr, int left, int right) {
    if (left >= right) {
        return;
    }

    std::vector<int> source(arr.begin() + left, arr.begin() + right + 1);
    std::vector<int> dest(source.size());
    const int n = static_cast<int>(source.size());

    for (int width = 1; width < n; width *= 2) {
        const int block_count = (n + 2 * width - 1) / (2 * width);

#ifdef _OPENMP
#pragma omp parallel for schedule(static)
#endif
        for (int block = 0; block < block_count; ++block) {
            const int lo = block * 2 * width;
            const int mid = std::min(lo + width, n);
            const int hi = std::min(lo + 2 * width, n);
            merge_parallel_detail::mergeBlock(source, dest, lo, mid, hi);
        }

        source.swap(dest);
    }

    std::copy(source.begin(), source.end(), arr.begin() + left);
}
