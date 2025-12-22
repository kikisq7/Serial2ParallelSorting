function partition!(arr, low, high)
    pivot = arr[high]
    i = low - 1
    for j in low:(high - 1)
        if arr[j] <= pivot
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
        end
    end
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
end

function quicksort!(arr, low::Int=1, high::Int=length(arr))
    if low < high
        pi = partition!(arr, low, high)
        quicksort!(arr, low, pi - 1)
        quicksort!(arr, pi + 1, high)
    end
    return arr
end

function print_array(arr)
    for v in arr
        print("$v ")
    end
    println()
end

if abspath(PROGRAM_FILE) == @__FILE__
    arr = [10, 7, 8, 9, 1, 5]
    print("Original array: ")
    print_array(arr)
    quicksort!(arr)
    print("Sorted array: ")
    print_array(arr)
end


