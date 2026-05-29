from parallel_utils import run_in_threads


def bubble_sort_parallel(arr):
    n = len(arr)
    if n < 2:
        return arr

    for phase in range(n):
        start = phase % 2
        pair_count = (n - start) // 2

        def compare_swap(indices):
            for pair_idx in indices:
                j = start + 2 * pair_idx
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

        run_in_threads(pair_count, compare_swap)

    return arr
