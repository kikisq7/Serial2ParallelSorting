def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quicksort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    if low < high:
        pi = partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)


def print_array(arr):
    for v in arr:
        print(v, end=" ")
    print()


if __name__ == "__main__":
    arr = [10, 7, 8, 9, 1, 5]
    print("Original array: ", end="")
    print_array(arr)
    quicksort(arr)
    print("Sorted array: ", end="")
    print_array(arr)


