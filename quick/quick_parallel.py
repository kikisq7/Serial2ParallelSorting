from parallel_utils import run_in_threads


def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quicksort_parallel(arr, max_workers=2):
    work = list(arr)
    low, high = 0, len(work) - 1
    if low >= high:
        return work
    current = [(low, high)]

    while current:
        pivots = [0] * len(current)
        valid = [0] * len(current)

        def worker(task_range):
            for idx in task_range:
                local_low, local_high = current[idx]
                if local_low < local_high:
                    pivots[idx] = partition(work, local_low, local_high)
                    valid[idx] = 1

        run_in_threads(len(current), worker, max_workers=max_workers)

        next_ranges = []
        for idx, (local_low, local_high) in enumerate(current):
            if not valid[idx]:
                continue
            pivot_idx = pivots[idx]
            if local_low < pivot_idx - 1:
                next_ranges.append((local_low, pivot_idx - 1))
            if pivot_idx + 1 < local_high:
                next_ranges.append((pivot_idx + 1, local_high))
        current = next_ranges

    return work
