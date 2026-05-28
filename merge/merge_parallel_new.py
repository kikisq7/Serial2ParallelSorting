from parallel_utils import run_in_threads


def _merge_runs(src, dest, left, mid, right):
    i = left
    j = mid
    k = left
    while i < mid and j < right:
        if src[i] <= src[j]:
            dest[k] = src[i]
            i += 1
        else:
            dest[k] = src[j]
            j += 1
        k += 1
    while i < mid:
        dest[k] = src[i]
        i += 1
        k += 1
    while j < right:
        dest[k] = src[j]
        j += 1
        k += 1


def parallel_merge_sort(arr, left=0, right=None):
    if right is None:
        right = len(arr) - 1
    if left >= right:
        return arr

    src = list(arr[left : right + 1])
    dest = [0] * len(src)
    width = 1
    n = len(src)

    while width < n:
        merge_count = (n + 2 * width - 1) // (2 * width)

        def worker(task_range):
            for task_idx in task_range:
                run_left = task_idx * 2 * width
                run_mid = min(run_left + width, n)
                run_right = min(run_left + 2 * width, n)
                if run_mid < run_right:
                    _merge_runs(src, dest, run_left, run_mid, run_right)
                else:
                    for idx in range(run_left, run_right):
                        dest[idx] = src[idx]

        run_in_threads(merge_count, worker)
        src, dest = dest, src
        width *= 2

    arr[left : right + 1] = src
    return arr
