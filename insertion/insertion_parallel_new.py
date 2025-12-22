# Python program for parallel implementation of Insertion Sort
import concurrent.futures
import threading
from typing import List

def insertion_sort_sequential(arr: List[int], start: int, end: int) -> None:
    """Sequential insertion sort for a subarray"""
    for i in range(start + 1, end + 1):
        key = arr[i]
        j = i - 1
        
        while j >= start and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

def parallel_insertion_sort(arr: List[int], start: int = 0, end: int = None) -> None:
    """Parallel insertion sort using divide and conquer approach"""
    if end is None:
        end = len(arr) - 1
    
    if start >= end:
        return
    
    # For small arrays, use sequential insertion sort
    if end - start < 100:
        insertion_sort_sequential(arr, start, end)
        return
    
    # Divide the array into two halves
    mid = start + (end - start) // 2
    
    # Sort both halves in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(parallel_insertion_sort, arr, start, mid)
        future2 = executor.submit(parallel_insertion_sort, arr, mid + 1, end)
        
        # Wait for both halves to complete
        future1.result()
        future2.result()
    
    # Merge the two sorted halves
    temp = [0] * (end - start + 1)
    i, j, k = start, mid + 1, 0
    
    while i <= mid and j <= end:
        if arr[i] <= arr[j]:
            temp[k] = arr[i]
            i += 1
        else:
            temp[k] = arr[j]
            j += 1
        k += 1
    
    while i <= mid:
        temp[k] = arr[i]
        i += 1
        k += 1
    
    while j <= end:
        temp[k] = arr[j]
        j += 1
        k += 1
    
    # Copy back to original array
    for i in range(k):
        arr[start + i] = temp[i]

def print_array(arr: List[int]) -> None:
    """Print array elements"""
    for val in arr:
        print(val, end=" ")
    print()

# Driver method
if __name__ == "__main__":
    arr = [12, 11, 13, 5, 6, 7, 8, 1, 9, 2, 4, 3, 400]
    
    print("Original array: ", end="")
    print_array(arr)
    
    parallel_insertion_sort(arr)
    
    print("Sorted array: ", end="")
    print_array(arr)
