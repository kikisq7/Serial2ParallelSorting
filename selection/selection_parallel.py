# parallelizes inner loop of selection sort

from concurrent.futures import ProcessPoolExecutor

def find_min_index(arr_slice, offset):
    """
    Find the index of the minimum element in the slice,
    returning the index relative to the full array.
    """
    min_idx = 0
    for i in range(1, len(arr_slice)):
        if arr_slice[i] < arr_slice[min_idx]:
            min_idx = i
    return min_idx + offset

def selection_sort_parallel(arr):
    n = len(arr)
    for i in range(n - 1):
        # Parallel part: find the min index from i to n-1
        with ProcessPoolExecutor() as executor:
            # Only split if large enough to benefit
            if n - i > 1000:
                # Divide the remaining unsorted part into chunks
                num_chunks = 4
                chunk_size = (n - i) // num_chunks
                futures = []
                for c in range(num_chunks):
                    start = i + c * chunk_size
                    end = i + (c + 1) * chunk_size if c != num_chunks - 1 else n
                    futures.append(executor.submit(find_min_index, arr[start:end], start))

                # Get min index from among the chunks
                min_idx = i
                for future in futures:
                    idx = future.result()
                    if arr[idx] < arr[min_idx]:
                        min_idx = idx
            else:
                # Fallback to sequential for small segments
                min_idx = i
                for j in range(i + 1, n):
                    if arr[j] < arr[min_idx]:
                        min_idx = j

        arr[i], arr[min_idx] = arr[min_idx], arr[i]

def print_array(arr):
    for val in arr:
        print(val, end=" ")
    print()

if __name__ == "__main__":
    arr = [64, 25, 12, 22, 11, 100, 4000, 2400]
    
    print("Original array: ", end="")
    print_array(arr)
    
    selection_sort_parallel(arr)
    
    print("Sorted array: ", end="")
    print_array(arr)
