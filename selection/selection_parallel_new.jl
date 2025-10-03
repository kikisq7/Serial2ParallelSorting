#!/usr/bin/env julia

using Base.Threads

function selection_sort_sequential!(arr::Vector, start_idx::Int, end_idx::Int)
    for i in start_idx:end_idx
        min_idx = i
        
        for j in (i + 1):end_idx
            if arr[j] < arr[min_idx]
                min_idx = j
            end
        end
        
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    end
    return arr
end

function parallel_selection_sort!(arr::Vector, start_idx::Int = 1, end_idx::Int = length(arr))
    if start_idx >= end_idx
        return arr
    end
    
    # For small arrays, use sequential selection sort
    if end_idx - start_idx < 50
        return selection_sort_sequential!(arr, start_idx, end_idx)
    end
    
    # Find minimum element in the range
    min_idx = start_idx
    for i in (start_idx + 1):end_idx
        if arr[i] < arr[min_idx]
            min_idx = i
        end
    end
    
    # Swap minimum with first element
    arr[start_idx], arr[min_idx] = arr[min_idx], arr[start_idx]
    
    # Recursively sort the rest in parallel
    if start_idx + 1 < end_idx
        # Divide the remaining array into two parts
        mid = start_idx + 1 + (end_idx - start_idx - 1) ÷ 2
        
        # Sort both parts in parallel
        @threads for i in 1:2
            if i == 1
                parallel_selection_sort!(arr, start_idx + 1, mid)
            else
                parallel_selection_sort!(arr, mid + 1, end_idx)
            end
        end
    end
    
    return arr
end

# Example usage
my_array = [64, 25, 12, 22, 11, 8, 5, 3, 1, 9, 7, 4]
println("Original array: ", my_array)
parallel_selection_sort!(my_array)
println("Sorted array: ", my_array)

my_array_2 = [5, 2, 8, 1, 9, 4, 7, 3, 6]
println("Original array: ", my_array_2)
parallel_selection_sort!(my_array_2)
println("Sorted array: ", my_array_2)
