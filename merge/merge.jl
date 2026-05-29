function _merge!(arr::Vector, left::Int, mid::Int, right::Int)
    left_part = arr[left:mid]
    right_part = arr[(mid + 1):right]
    i = 1
    j = 1
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

function _mergesort!(arr::Vector, left::Int, right::Int)
    if left < right
        mid = left + div(right - left, 2)
        _mergesort!(arr, left, mid)
        _mergesort!(arr, mid + 1, right)
        _merge!(arr, left, mid, right)
    end
    return arr
end

function mergesort(arr::Vector)
    work = copy(arr)
    _mergesort!(work, 1, length(work))
    return work
end
