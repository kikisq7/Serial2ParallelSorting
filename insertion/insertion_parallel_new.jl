#!/usr/bin/env julia

using Base.Threads

function insertion_sort_sequential!(arr::Vector, start_idx::Int, end_idx::Int)
    for i in (start_idx + 1):end_idx
        key = arr[i]
        j = i - 1
        
        while j >= start_idx && arr[j] > key
            arr[j+1] = arr[j]
            j -= 1
        end
        arr[j+1] = key
    end
    return arr
end

function parallel_insertion_sort!(arr::Vector, start_idx::Int = 1, end_idx::Int = length(arr))
    if start_idx >= end_idx
        return arr
    end
    
    # For small arrays, use sequential insertion sort
    if end_idx - start_idx < 100
        return insertion_sort_sequential!(arr, start_idx, end_idx)
    end
    
    # Divide the array into two halves
    mid = start_idx + (end_idx - start_idx) ÷ 2
    
    # Sort both halves in parallel
    @threads for i in 1:2
        if i == 1
            parallel_insertion_sort!(arr, start_idx, mid)
        else
            parallel_insertion_sort!(arr, mid + 1, end_idx)
        end
    end
    
    # Merge the two sorted halves
    temp = similar(arr, end_idx - start_idx + 1)
    i, j, k = start_idx, mid + 1, 1
    
    while i <= mid && j <= end_idx
        if arr[i] <= arr[j]
            temp[k] = arr[i]
            i += 1
        else
            temp[k] = arr[j]
            j += 1
        end
        k += 1
    end
    
    while i <= mid
        temp[k] = arr[i]
        i += 1
        k += 1
    end
    
    while j <= end_idx
        temp[k] = arr[j]
        j += 1
        k += 1
    end
    
    # Copy back to original array
    arr[start_idx:end_idx] = temp
    
    return arr
end

# Example usage
my_array = [5, 2, 8, 1, 9, 4, 7, 3, 6, 12, 11, 10]
println("Original array: ", my_array)
parallel_insertion_sort!(my_array)
println("Sorted array: ", my_array)
