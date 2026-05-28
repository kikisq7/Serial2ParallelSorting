function _partition!(arr::Vector, low::Int, high::Int)
    pivot = arr[high]
    i = low - 1
    for j in low:(high - 1)
        if arr[j] < pivot
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
        end
    end
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
end

function quicksort!(arr::Vector, low::Int = 1, high::Int = length(arr))
    if low < high
        pivot_index = _partition!(arr, low, high)
        quicksort!(arr, low, pivot_index - 1)
        quicksort!(arr, pivot_index + 1, high)
    end
    return arr
end
