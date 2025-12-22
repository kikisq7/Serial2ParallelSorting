from concurrent.futures import ProcessPoolExecutor
from itertools import repeat


def _compare_pairs(snapshot, indices):
    swaps = []
    for i in indices:
        if snapshot[i] > snapshot[i + 1]:
            swaps.append(i)
    return swaps


def _compare_pairs_with_snapshot(args):
    snapshot, indices = args
    return _compare_pairs(snapshot, indices)


def _phase_parallel(arr, start, max_workers):
    n = len(arr)
    if n < 2:
        return False

    # Take a snapshot to avoid concurrent writes during comparisons
    snapshot = list(arr)
    pair_indices = list(range(start, n - 1, 2))
    if not pair_indices:
        return False

    # Chunk indices for workers
    num_workers = max_workers if max_workers > 0 else 1
    chunk_size = max(1, (len(pair_indices) + num_workers - 1) // num_workers)
    chunks = [pair_indices[i : i + chunk_size] for i in range(0, len(pair_indices), chunk_size)]

    swaps_collected = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(_compare_pairs_with_snapshot, zip(repeat(snapshot), chunks)))
        for res in results:
            swaps_collected.extend(res)

    if not swaps_collected:
        return False

    # Apply swaps serially to avoid races
    for i in swaps_collected:
        if arr[i] > arr[i + 1]:
            arr[i], arr[i + 1] = arr[i + 1], arr[i]
    return True


def bubble_sort_parallel(arr, max_workers=4):
    n = len(arr)
    if n <= 1:
        return arr

    swapped = True
    while swapped:
        swapped = False
        swapped |= _phase_parallel(arr, 0, max_workers)
        swapped |= _phase_parallel(arr, 1, max_workers)
    return arr


def print_array(arr):
    for v in arr:
        print(v, end=" ")
    print()


if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90, 5, 3, 8, 7, 2]
    print("Original array: ", end="")
    print_array(data)
    bubble_sort_parallel(data, max_workers=4)
    print("Sorted array: ", end="")
    print_array(data)
    assert data == sorted(data)


