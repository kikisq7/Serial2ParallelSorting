"""
Attempt 1: Failed to generate working sort algorihtm
"""
# import concurrent.futures
# import math

# def insertionSort(arr):
#     for i in range(1, len(arr)):
#         key = arr[i]
#         j = i - 1
#         while j >= 0 and key < arr[j]:
#             arr[j + 1] = arr[j]
#             j -= 1
#         arr[j + 1] = key

# def parallelInsertionSort(arr):
#     num_threads = 4  # Adjust based on the size of the array or system capabilities
#     chunk_size = math.ceil(len(arr) / num_threads)

#     # Function to apply insertion sort on a chunk of the array
#     def sort_chunk(start, end):
#         insertionSort(arr[start:end])

#     with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
#         futures = []
#         for i in range(0, len(arr), chunk_size):
#             futures.append(executor.submit(sort_chunk, i, min(i + chunk_size, len(arr))))

#         # Wait for all sorting tasks to complete
#         concurrent.futures.wait(futures)

#     # Merging step (this part would normally still require sequential merging)
#     # After sorting each chunk, we need to merge them into the sorted list
#     sorted_arr = []
#     indices = [0] * num_threads
#     while len(sorted_arr) < len(arr):
#         min_val = float('inf')
#         min_idx = -1

#         # Find the minimum element from the current chunks
#         for i in range(num_threads):
#             start_idx = i * chunk_size
#             end_idx = min((i + 1) * chunk_size, len(arr))
#             if indices[i] < (end_idx - start_idx):
#                 element = arr[start_idx + indices[i]]
#                 if element < min_val:
#                     min_val = element
#                     min_idx = i

#         # Add the minimum element to the result and update the index
#         sorted_arr.append(min_val)
#         indices[min_idx] += 1

#     return sorted_arr

# # Example usage:
# arr = [5, 2, 9, 1, 5, 6]
# sorted_arr = parallelInsertionSort(arr)
# print(sorted_arr)

"""
Attempt 2: Still doesn't work, not combining chunks properly
"""
# import concurrent.futures
# import math

# def insertionSort(arr):
#     """Perform insertion sort on a given array."""
#     for i in range(1, len(arr)):
#         key = arr[i]
#         j = i - 1
#         while j >= 0 and key < arr[j]:
#             arr[j + 1] = arr[j]
#             j -= 1
#         arr[j + 1] = key

# def parallelInsertionSort(arr):
#     """Parallel version of insertion sort."""
#     num_threads = 4  # Number of threads
#     chunk_size = math.ceil(len(arr) / num_threads)

#     # Function to sort a chunk of the array
#     def sort_chunk(start, end):
#         insertionSort(arr[start:end])

#     # Step 1: Split the array into chunks and sort them in parallel
#     with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
#         futures = []
#         for i in range(0, len(arr), chunk_size):
#             futures.append(executor.submit(sort_chunk, i, min(i + chunk_size, len(arr))))

#         # Wait for all sorting tasks to finish
#         concurrent.futures.wait(futures)

#     # Step 2: Merge sorted chunks into the final sorted array
#     def merge_sorted_chunks(arr):
#         """Merge sorted chunks in a sequential manner."""
#         # We merge two chunks at a time
#         sorted_arr = []
#         indices = [0] * num_threads
#         chunks = [arr[i:i + chunk_size] for i in range(0, len(arr), chunk_size)]

#         while len(sorted_arr) < len(arr):
#             min_val = float('inf')
#             min_idx = -1

#             # Find the minimum element from each chunk
#             for i in range(num_threads):
#                 start_idx = i * chunk_size
#                 end_idx = min((i + 1) * chunk_size, len(arr))
#                 if indices[i] < len(chunks[i]):
#                     element = chunks[i][indices[i]]
#                     if element < min_val:
#                         min_val = element
#                         min_idx = i

#             # Add the smallest element to the sorted array and update the index
#             sorted_arr.append(min_val)
#             indices[min_idx] += 1

#         return sorted_arr

#     # After sorting chunks, merge them
#     sorted_arr = merge_sorted_chunks(arr)
#     return sorted_arr


# # Example usage
# arr = [5, 2, 9, 1, 5, 6, 3, 8, 7, 4]
# sorted_arr = parallelInsertionSort(arr)
# print(sorted_arr)rul

"""
Attempt 3: Resorts to merge sort impelmetnation that is parallelized.
Throughout generation, made point that it believed insertion sort would be difficult to parallelize.
"Converting the serial insertionSort algorithm into a parallel version is tricky because insertionSort depends on previous elements being sorted correctly before the next element is placed."


"""

import concurrent.futures

# Merge Sort Implementation
def merge(left, right):
    """Merge two sorted arrays into one sorted array."""
    sorted_array = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            sorted_array.append(left[i])
            i += 1
        else:
            sorted_array.append(right[j])
            j += 1
    # Append any remaining elements
    sorted_array.extend(left[i:])
    sorted_array.extend(right[j:])
    return sorted_array

def parallel_merge_sort(arr):
    """Perform parallel merge sort."""
    
    # Base case for recursion
    if len(arr) <= 1:
        return arr
    
    # Split array into two halves
    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]
    
    # Use ThreadPoolExecutor to sort the halves in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Recursively sort both halves in parallel
        left_future = executor.submit(parallel_merge_sort, left)
        right_future = executor.submit(parallel_merge_sort, right)
        
        # Wait for both halves to be sorted
        left_sorted = left_future.result()
        right_sorted = right_future.result()
    
    # Merge the sorted halves
    return merge(left_sorted, right_sorted)

# Example usage:
arr = [5, 2, 9, 1, 5, 6, 3, 8, 7, 4]
sorted_arr = parallel_merge_sort(arr)
print(sorted_arr)
