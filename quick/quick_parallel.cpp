#include <utility>
#include <vector>

namespace quick_parallel_detail {

int partition(std::vector<int>& arr, int low, int high) {
    const int pivot = arr[static_cast<std::size_t>(high)];
    int i = low - 1;

    for (int j = low; j < high; ++j) {
        if (arr[static_cast<std::size_t>(j)] < pivot) {
            ++i;
            std::swap(arr[static_cast<std::size_t>(i)], arr[static_cast<std::size_t>(j)]);
        }
    }

    std::swap(arr[static_cast<std::size_t>(i + 1)], arr[static_cast<std::size_t>(high)]);
    return i + 1;
}

}  // namespace quick_parallel_detail

void quicksort_parallel_entry(std::vector<int>& arr) {
    if (arr.size() < 2) {
        return;
    }

    std::vector<std::pair<int, int>> segments{{0, static_cast<int>(arr.size()) - 1}};

    while (!segments.empty()) {
        const int segment_count = static_cast<int>(segments.size());
        std::vector<std::pair<int, int>> left_children(static_cast<std::size_t>(segment_count));
        std::vector<std::pair<int, int>> right_children(static_cast<std::size_t>(segment_count));
        std::vector<char> has_left(static_cast<std::size_t>(segment_count), 0);
        std::vector<char> has_right(static_cast<std::size_t>(segment_count), 0);

#ifdef _OPENMP
#pragma omp parallel for schedule(static)
#endif
        for (int idx = 0; idx < segment_count; ++idx) {
            const int low = segments[static_cast<std::size_t>(idx)].first;
            const int high = segments[static_cast<std::size_t>(idx)].second;
            if (low < high) {
                const int pivot = quick_parallel_detail::partition(arr, low, high);
                if (low < pivot - 1) {
                    left_children[static_cast<std::size_t>(idx)] = {low, pivot - 1};
                    has_left[static_cast<std::size_t>(idx)] = 1;
                }
                if (pivot + 1 < high) {
                    right_children[static_cast<std::size_t>(idx)] = {pivot + 1, high};
                    has_right[static_cast<std::size_t>(idx)] = 1;
                }
            }
        }

        std::vector<std::pair<int, int>> next_segments;
        next_segments.reserve(segments.size() * 2);
        for (int idx = 0; idx < segment_count; ++idx) {
            if (has_left[static_cast<std::size_t>(idx)]) {
                next_segments.push_back(left_children[static_cast<std::size_t>(idx)]);
            }
            if (has_right[static_cast<std::size_t>(idx)]) {
                next_segments.push_back(right_children[static_cast<std::size_t>(idx)]);
            }
        }
        segments.swap(next_segments);
    }
}
