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
    return merge(mergesort(left), mergesort(right))
end
