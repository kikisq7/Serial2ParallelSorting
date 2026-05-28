using Base.Threads

function selection_sort_parallel!(arr::Vector{T}) where T
    n = length(arr)

    for i in 1:n-1
        min_val = arr[i]
        min_idx = i

        # Shared variables for parallel min search
        lock = ReentrantLock()
        
        @threads for j in (i+1):n
            if arr[j] < min_val
                lock() do
                    if arr[j] < min_val
                        min_val = arr[j]
                        min_idx = j
                    end
                end
            end
        end

        # Swap the found min with current position
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    end

    return arr
end

# -------------------------------
# ✅ Example usage
my_array = [64, 25, 12, 22, 11]
println("Original array: ", my_array)
selection_sort_parallel!(my_array)
println("Sorted array: ", my_array)

my_array_2 = [5, 2, 8, 1, 9, 4]
println("Original array: ", my_array_2)
selection_sort_parallel!(my_array_2)
println("Sorted array: ", my_array_2)
