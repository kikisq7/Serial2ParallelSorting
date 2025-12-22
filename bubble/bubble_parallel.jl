using Base.Threads

function phase!(arr::Vector{T}, start::Int) where {T}
    n = length(arr)
    if n < 2
        return false
    end
    swapped = false

    # Snapshot to avoid read/write conflicts
    snap = copy(arr)

    @threads for k in 0:((n - 1 - start) ÷ 2)
        i = start + 2k
        if i + 1 <= n && snap[i] > snap[i + 1]
            # Apply swap after comparisons; thread-safe writes to distinct indices
            arr[i], arr[i + 1] = arr[i + 1], arr[i]
        end
    end

    # Detect if any swap occurred
    for i in start:2:(n - 1)
        if arr[i] != snap[i]
            swapped = true
            break
        end
    end
    return swapped
end

function bubble_sort_parallel!(arr::Vector{T}) where {T}
    n = length(arr)
    if n <= 1
        return arr
    end
    swapped = true
    while swapped
        swapped = false
        swapped |= phase!(arr, 1)  # even indices in Julia (1-based)
        swapped |= phase!(arr, 2)  # odd indices in Julia (1-based)
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
    arr = [64, 34, 25, 12, 22, 11, 90, 5, 3, 8, 7, 2]
    print("Original array: ")
    print_array(arr)
    bubble_sort_parallel!(arr)
    print("Sorted array: ")
    print_array(arr)
    @assert arr == sort(arr)
end


