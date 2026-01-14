using Polyester
using Base.Threads

function phase!(arr::Vector{T}, start::Int) where {T}
    n = length(arr)
    if n < 2
        return false
    end
    
    range_max = (n - 1 - start) ÷ 2
    
    swapped_flags = zeros(Bool, Threads.nthreads())
    
    # Calculate minbatch: ensure each thread gets enough work to amortize overhead
    # Recommended range: 20-100 iterations per thread
    minbatch = max(20, range_max ÷ (Threads.nthreads() * 4))
    
    # Use @batch directly on iteration space - let Polyester handle chunking
    @batch minbatch=minbatch for k in 0:range_max
        i = start + 2*k
        if i + 1 <= n && arr[i] > arr[i + 1]
            arr[i], arr[i + 1] = arr[i + 1], arr[i]
            swapped_flags[Threads.threadid()] = true
        end
    end
    
    # Reduce thread-local flags to single boolean
    swapped = any(swapped_flags)
    
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

