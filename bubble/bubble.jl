function bubble_sort!(arr)
    n = length(arr)
    for i in 1:n
        swapped = false
        for j in 1:(n - i)
            if arr[j] > arr[j + 1]
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = true
            end
        end
        if !swapped
            break
        end
    end
    return nothing
end
