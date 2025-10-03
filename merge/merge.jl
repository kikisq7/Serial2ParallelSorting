#!/usr/bin/env julia

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


function mergesort(arr::Vector)
    n = length(arr)
    if n <= 1
        return arr
    end

    mid = n ÷ 2
    left = arr[1:mid]
    right = arr[mid+1:n]

    left_sorted = mergesort(left) 
    right_sorted = mergesort(right)

    return merge(left_sorted, right_sorted)
end


arr = [7, 6, 5, 9, 8, 4, 3, 1, 2, 0]
sorted_arr = mergesort(arr)
println(sorted_arr)