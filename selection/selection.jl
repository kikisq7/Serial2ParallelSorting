function selection_sort!(arr::Vector)
    n = length(arr)

    for i in 1:n
        min_idx = i

        for j in (i + 1):n
            if arr[j] < arr[min_idx]
                min_idx = j
            end
        end

        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    end
    return arr
end

# Example usage:
my_array = [64, 25, 12, 22, 11]
println("Original array: ", my_array)
selection_sort!(my_array)
println("Sorted array: ", my_array)

my_array_2 = [5, 2, 8, 1, 9, 4]
println("Original array: ", my_array_2)
selection_sort!(my_array_2)
println("Sorted array: ", my_array_2)