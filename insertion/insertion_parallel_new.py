from parallel_utils import run_in_threads


def parallel_insertion_sort(arr):
    n = len(arr)
    if n < 2:
        return arr

    output = [None] * n

    def rank_items(indices):
        for i in indices:
            value = arr[i]
            rank = 0
            for j, other in enumerate(arr):
                if other < value or (other == value and j < i):
                    rank += 1
            output[rank] = value

    run_in_threads(n, rank_items)
    arr[:] = output
    return arr
