from concurrent.futures import ProcessPoolExecutor


def _quicksort_seq(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[-1]
    left = [x for x in arr[:-1] if x <= pivot]
    right = [x for x in arr[:-1] if x > pivot]
    return _quicksort_seq(left) + [pivot] + _quicksort_seq(right)


def _quicksort_parallel(arr, depth, cutoff, max_workers):
    if len(arr) <= cutoff or depth <= 0:
        return _quicksort_seq(arr)

    pivot = arr[-1]
    left = [x for x in arr[:-1] if x <= pivot]
    right = [x for x in arr[:-1] if x > pivot]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        left_future = executor.submit(_quicksort_parallel, left, depth - 1, cutoff, max_workers)
        right_future = executor.submit(_quicksort_parallel, right, depth - 1, cutoff, max_workers)
        left_sorted = left_future.result()
        right_sorted = right_future.result()
    return left_sorted + [pivot] + right_sorted


def quicksort_parallel(arr, max_workers=4, depth=3, cutoff=1_000):
    return _quicksort_parallel(list(arr), depth, cutoff, max_workers)


def print_array(arr):
    for v in arr:
        print(v, end=" ")
    print()


if __name__ == "__main__":
    data = [10, 7, 8, 9, 1, 5, 12, 4, 6, 3, 11, 2]
    print("Original array: ", end="")
    print_array(data)
    out = quicksort_parallel(data, max_workers=4, depth=3, cutoff=2)
    print("Sorted array: ", end="")
    print_array(out)
    assert out == sorted(data)


