#!/usr/bin/env julia
using Base.Threads

#=
However, like in C++, insertion sort is inherently sequential — each step depends on the previous elements being in order. So, directly parallelizing insertion sort isn't effective due to data dependencies.

✅ Solution: Use a Parallel-Friendly Algorithm

To gain real parallel performance, especially on large data, it's much better to use algorithms designed for parallel execution.

Instead of attempting to parallelize insertion sort directly, you can:

Use Shell sort (parallelizable generalization of insertion sort).

Use Merge sort or Bitonic sort, which are much more parallelizable.
=#

# LLM chose to use merge sort instead.
function merge!(arr, left, mid, right)
    left_part = copy(arr[left:mid])
    right_part = copy(arr[mid+1:right])

    i = j = 1
    k = left

    while i <= length(left_part) && j <= length(right_part)
        if left_part[i] <= right_part[j]
            arr[k] = left_part[i]
            i += 1
        else
            arr[k] = right_part[j]
            j += 1
        end
        k += 1
    end

    while i <= length(left_part)
        arr[k] = left_part[i]
        
        i += 1
        k += 1
    end

    while j <= length(right_part)
        arr[k] = right_part[j]
        j += 1
        k += 1
    end
end

function parallel_merge_sort!(arr, left, right; threshold=1000)
    if left < right
        mid = div(left + right, 2)

        if right - left < threshold
            # Small enough to run sequentially
            parallel_merge_sort!(arr, left, mid)
            parallel_merge_sort!(arr, mid + 1, right)
        else
            t1 = Threads.@spawn parallel_merge_sort!(arr, left, mid)
            t2 = Threads.@spawn parallel_merge_sort!(arr, mid + 1, right)
            wait(t1)
            wait(t2)
        end

        merge!(arr, left, mid, right)
    end
    return arr
end

# User-friendly wrapper
function parallel_merge_sort!(arr::Vector)
    parallel_merge_sort!(arr, 1, length(arr))
end

arr = [5, 2, 8, 1, 9, 4, 12, 3, 7, 0]
println("Original array: ", arr)
parallel_merge_sort!(arr)
println("Sorted array: ", arr)