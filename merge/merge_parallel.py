import multiprocessing
import ctypes

def merge(arr, left, mid, right):
    n1 = mid - left + 1
    n2 = right - mid

    L = [arr[left + i] for i in range(n1)]
    R = [arr[mid + 1 + j] for j in range(n2)]

    i = j = 0
    k = left

    while i < n1 and j < n2:
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1

    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1

    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1


def parallel_merge_sort(arr, left, right, depth=0, max_depth=2):
    if left < right:
        mid = (left + right) // 2

        if depth < max_depth:
            left_proc = multiprocessing.Process(
                target=parallel_merge_sort,
                args=(arr, left, mid, depth + 1, max_depth)
            )
            right_proc = multiprocessing.Process(
                target=parallel_merge_sort,
                args=(arr, mid + 1, right, depth + 1, max_depth)
            )

            left_proc.start()
            right_proc.start()
            left_proc.join()
            right_proc.join()
        else:
            # Fallback to serial merge sort
            parallel_merge_sort(arr, left, mid, depth + 1, max_depth)
            parallel_merge_sort(arr, mid + 1, right, depth + 1, max_depth)

        merge(arr, left, mid, right)


if __name__ == "__main__":
    # Input array
    original = [38, 27, 43, 10, 82, 5, 7, 11, 55, 31]

    # Shared memory array
    shared_array = multiprocessing.Array(ctypes.c_int, original)

    # Perform parallel merge sort
    parallel_merge_sort(shared_array, 0, len(shared_array) - 1)

    # Convert back to list and print
    sorted_arr = list(shared_array)
    print("Sorted array:", sorted_arr)
