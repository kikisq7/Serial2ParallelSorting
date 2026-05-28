from parallel_utils import parallel_ranges, run_in_threads, run_in_threads_indexed


def parallel_insertion_sort(arr):
    n = len(arr)
    if n <= 1:
        return arr

    for i in range(1, n):
        key = arr[i]
        task_count = i
        counts = [0] * len(parallel_ranges(task_count))

        def count_worker(index, task_range):
            local = 0
            for j in task_range:
                if arr[j] <= key:
                    local += 1
            counts[index] = local

        run_in_threads_indexed(task_count, count_worker)
        position = sum(counts)
        if position == i:
            continue

        segment = arr[position:i]
        shift_count = len(segment)

        def shift_worker(task_range):
            for offset in task_range:
                arr[position + offset + 1] = segment[offset]

        run_in_threads(shift_count, shift_worker)
        arr[position] = key

    return arr
