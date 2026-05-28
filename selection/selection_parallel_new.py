from parallel_utils import parallel_ranges
from concurrent.futures import ThreadPoolExecutor


def parallel_selection_sort(arr, left=0, right=None):
    if right is None:
        right = len(arr) - 1
    if left >= right:
        return arr

    for i in range(left, right):
        ranges = parallel_ranges(right - i + 1)

        def local_min(index_range):
            min_idx = i
            for offset in index_range:
                j = i + offset
                if arr[j] < arr[min_idx]:
                    min_idx = j
            return min_idx

        if len(ranges) == 1:
            candidates = [local_min(ranges[0])]
        else:
            with ThreadPoolExecutor(max_workers=len(ranges)) as executor:
                candidates = list(executor.map(local_min, ranges))

        min_idx = min(candidates, key=lambda idx: (arr[idx], idx))
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]

    return arr
