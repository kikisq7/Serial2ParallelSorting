#!/usr/bin/env julia
using Base.Threads

# Sequential merge
function merge(left::Vector, right::Vector)
    result = eltype(left)[]
    i, j = 1, 1

    while i <= length(left) && j <= length(right)
        if left[i] <= right[j]
            push!(result, left[i])
            i += 1
        else
            push!(result, right[j])
            j += 1
        end
    end

    append!(result, @view left[i:end])
    append!(result, @view right[j:end])
    return result
end

# Parallel merge sort using threads
function parallel_merge_sort(arr::Vector{T}, depth=0) where T
    n = length(arr)
    if n <= 1
        return arr
    end

    mid = div(n, 2)
    left_half = arr[1:mid]
    right_half = arr[mid+1:end]

    if depth < 3 && n > 1_000
        # Spawn parallel tasks if depth is small and input is large enough
        left_task = Threads.@spawn parallel_merge_sort(left_half, depth + 1)
        right_sorted = parallel_merge_sort(right_half, depth + 1)
        left_sorted = fetch(left_task)
    else
        # Fallback to serial recursion
        left_sorted = parallel_merge_sort(left_half, depth + 1)
        right_sorted = parallel_merge_sort(right_half, depth + 1)
    end

    return merge(left_sorted, right_sorted)
end

arr = [7, 6, 5, 9, 8, 4, 3, 1, 2, 0]
sorted_arr = parallel_merge_sort(arr)
println(sorted_arr)
