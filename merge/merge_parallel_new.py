from parallel_utils import run_in_threads


def _merge_block(source, dest, left, mid, right):
    i, j, k = left, mid, left
    while i < mid and j < right:
        if source[i] <= source[j]:
            dest[k] = source[i]
            i += 1
        else:
            dest[k] = source[j]
            j += 1
        k += 1

    while i < mid:
        dest[k] = source[i]
        i += 1
        k += 1

    while j < right:
        dest[k] = source[j]
        j += 1
        k += 1


def parallel_merge_sort(arr, left, right):
    if left >= right:
        return arr

    data = arr[left : right + 1]
    n = len(data)
    buffer = [None] * n
    width = 1
    source = data
    dest = buffer

    while width < n:
        block_count = (n + 2 * width - 1) // (2 * width)

        def merge_blocks(blocks):
            for block in blocks:
                lo = block * 2 * width
                mid = min(lo + width, n)
                hi = min(lo + 2 * width, n)
                _merge_block(source, dest, lo, mid, hi)

        run_in_threads(block_count, merge_blocks)
        source, dest = dest, source
        width *= 2

    arr[left : right + 1] = source[:]
    return arr
