# Python program for parallel implementation of Merge Sort
import concurrent.futures
from typing import List

def merge(arr: List[int], left: int, mid: int, right: int) -> None:
    """Merge two sorted subarrays"""
    n1 = mid - left + 1
    n2 = right - mid

    # Create temp arrays
    L = [0] * n1
    R = [0] * n2

    # Copy data to temp arrays L[] and R[]
    for i in range(n1):
        L[i] = arr[left + i]
    for j in range(n2):
        R[j] = arr[mid + 1 + j]
        
    i = 0  
    j = 0  
    k = left  

    # Merge the temp arrays back
    # into arr[left..right]
    while i < n1 and j < n2:
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1

    # Copy the remaining elements of L[],
    # if there are any
    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1

    # Copy the remaining elements of R[], 
    # if there are any
    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1

def parallel_merge_sort(arr: List[int], left: int, right: int) -> None:
    """Parallel merge sort implementation"""
    if left >= right:
        return
    
    # For small arrays, use sequential merge sort
    if right - left < 100:
        mid = (left + right) // 2
        parallel_merge_sort(arr, left, mid)
        parallel_merge_sort(arr, mid + 1, right)
        merge(arr, left, mid, right)
        return

    mid = (left + right) // 2
    
    # Sort both halves in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(parallel_merge_sort, arr, left, mid)
        future2 = executor.submit(parallel_merge_sort, arr, mid + 1, right)
        
        # Wait for both halves to complete
        future1.result()
        future2.result()
    
    # Merge the sorted halves
    merge(arr, left, mid, right)

def print_array(arr: List[int]) -> None:
    """Print array elements"""
    for val in arr:
        print(val, end=" ")
    print()

# Driver code
if __name__ == "__main__":
    arr = [38, 27, 43, 10, 15, 8, 22, 5, 12, 3, 18, 7]
    
    print("Original array: ", end="")
    print_array(arr)
    
    parallel_merge_sort(arr, 0, len(arr) - 1)
    
    print("Sorted array: ", end="")
    print_array(arr)
