#!/usr/bin/env julia

function insertion_sort!(arr::Vector)
    n = length(arr)
    for i in 2:n
        key = arr[i]
        j = i - 1

        while j >= 1 && arr[j] > key
            arr[j+1] = arr[j]
            j -= 1
        end
        arr[j+1] = key
    end
    return arr
end

my_array = [5, 2, 8, 1, 9, 4]
println("Original array: ", my_array)
insertion_sort!(my_array)
println("Sorted array: ", my_array)