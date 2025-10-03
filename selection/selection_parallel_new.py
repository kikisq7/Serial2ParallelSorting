# Python program for parallel implementation of Selection Sort
import concurrent.futures
from typing import List

def selection_sort_sequential(arr: List[int], start: int, end: int) -> None:
    """Sequential selection sort for a subarray"""
    for i in range(start, end):
        min_idx = i
        
        for j in range(i + 1, end + 1):
            if arr[j] < arr[min_idx]:
                min_idx = j
        
        arr[i], arr[min_idx] = arr[min_idx], arr[i]

def parallel_selection_sort(arr: List[int], start: int = 0, end: int = None) -> None:
    """Parallel selection sort using divide and conquer approach"""
    if end is None:
        end = len(arr) - 1
    
    if start >= end:
        return
    
    # For small arrays, use sequential selection sort
    if end - start < 50:
        selection_sort_sequential(arr, start, end)
        return
    
    # Find minimum element in the range
    min_idx = start
    for i in range(start + 1, end + 1):
        if arr[i] < arr[min_idx]:
            min_idx = i
    
    # Swap minimum with first element
    arr[start], arr[min_idx] = arr[min_idx], arr[start]
    
    # Recursively sort the rest in parallel
    if start + 1 < end:
        # Divide the remaining array into two parts
        mid = start + 1 + (end - start - 1) // 2
        
        # Sort both parts in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(parallel_selection_sort, arr, start + 1, mid)
            future2 = executor.submit(parallel_selection_sort, arr, mid + 1, end)
            
            # Wait for both parts to complete
            future1.result()
            future2.result()

def print_array(arr: List[int]) -> None:
    """Print array elements"""
    for val in arr:
        print(val, end=" ")
    print()

# Driver code
if __name__ == "__main__":
    arr = [64, 25, 12, 22, 11, 8, 5, 3, 1, 9, 7, 4]
    
    print("Original array: ", end="")
    print_array(arr)
    
    parallel_selection_sort(arr)
    
    print("Sorted array: ", end="")
    print_array(arr)
