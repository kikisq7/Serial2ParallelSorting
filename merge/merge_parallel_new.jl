#!/usr/bin/env julia

using Base.Threads

function merge(left::Vector, right::Vector)
    result = eltype(left)[]
    i, j = 1, 1 # Pointers for left and right arrays

    while i <= length(left) && j <= length(right)
        if left[i] <= right[j]
            push!(result, left[i])
            i += 1
        else
            push!(result, right[j])
            j += 1
        end
    end

    while i <= length(left)
        push!(result, left[i])
        i += 1
    end

    while j <= length(right)
        push!(result, right[j])
        j += 1
    end

    return result
end

function parallel_mergesort(arr::Vector)
    n = length(arr)
    if n <= 1
        return arr
    end
    
    # For small arrays, use sequential merge sort
    if n < 100
        mid = n ÷ 2
        left = arr[1:mid]
        right = arr[mid+1:n]
        
        left_sorted = parallel_mergesort(left)
        right_sorted = parallel_mergesort(right)
        
        return merge(left_sorted, right_sorted)
    end

    mid = n ÷ 2
    left = arr[1:mid]
    right = arr[mid+1:n]

    # Sort both halves in parallel
    left_sorted = Vector{eltype(arr)}()
    right_sorted = Vector{eltype(arr)}()
    
    @threads for i in 1:2
        if i == 1
            left_sorted = parallel_mergesort(left)
        else
            right_sorted = parallel_mergesort(right)
        end
    end

    return merge(left_sorted, right_sorted)
end

# Example usage
arr = [7, 6, 5, 9, 8, 4, 3, 1, 2, 0, 12, 11, 10, 15, 14, 13]
println("Original array: ", arr)
sorted_arr = parallel_mergesort(arr)
println("Sorted array: ", sorted_arr)
