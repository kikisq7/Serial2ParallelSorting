from parallel_utils import parallel_ranges, run_in_threads_indexed


def parallel_selection_sort(arr):
    n = len(arr)
    if n <= 1:
        return arr

    for i in range(n - 1):
        local_ranges = parallel_ranges(n - i)
        local_mins = [i] * len(local_ranges)

        def worker(range_index, task_range):
            if task_range.start >= task_range.stop:
                return
            min_idx = i + task_range.start
            for offset in range(task_range.start + 1, task_range.stop):
                candidate_idx = i + offset
                if arr[candidate_idx] < arr[min_idx]:
                    min_idx = candidate_idx
            local_mins[range_index] = min_idx

        run_in_threads_indexed(n - i, worker)
        min_idx = min(local_mins, key=lambda idx: (arr[idx], idx))
        arr[i], arr[min_idx] = arr[min_idx], arr[i]

    return arr
