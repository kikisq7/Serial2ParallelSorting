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
end

function print_array(arr)
    for v in arr
        print("$v ")
    end
    println()
end

if abspath(PROGRAM_FILE) == @__FILE__
    arr = [64, 34, 25, 12, 22, 11, 90]
    print("Original array: ")
    print_array(arr)
    bubble_sort!(arr)
    print("Sorted array: ")
    print_array(arr)
end


