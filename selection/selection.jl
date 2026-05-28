function selection_sort!(arr::Vector)
    n = length(arr)
    for i in 1:(n - 1)
        min_idx = i
        for j in (i + 1):n
            if arr[j] < arr[min_idx]
                min_idx = j
            end
        end
        if min_idx != i
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
        end
    end
    return arr
end
