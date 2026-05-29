from parallel_utils import parallel_ranges
from concurrent.futures import ThreadPoolExecutor


def _partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quicksort_parallel(arr, low=0, high=None, max_workers=None):
    work = list(arr)
    if high is None:
        high = len(work) - 1
    if low >= high:
        return work

    segments = [(low, high)]
    while segments:
        ranges = parallel_ranges(len(segments), max_workers=max_workers)
        next_segments_by_range = [[] for _ in ranges]

        def partition_range(args):
            range_index, segment_range = args
            children = next_segments_by_range[range_index]
            for segment_index in segment_range:
                lo, hi = segments[segment_index]
                if lo < hi:
                    pivot_index = _partition(work, lo, hi)
                    if lo < pivot_index - 1:
                        children.append((lo, pivot_index - 1))
                    if pivot_index + 1 < hi:
                        children.append((pivot_index + 1, hi))

        if len(ranges) == 1:
            partition_range((0, ranges[0]))
        else:
            with ThreadPoolExecutor(max_workers=len(ranges)) as executor:
                list(executor.map(partition_range, enumerate(ranges)))

        segments = [segment for children in next_segments_by_range for segment in children]

    return work
