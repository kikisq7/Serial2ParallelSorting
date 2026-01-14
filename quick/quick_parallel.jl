using Polyester
using Base.Threads

function quicksort_seq(arr)
    if length(arr) <= 1
        return copy(arr)
    end
    pivot = arr[end]
    left = [x for x in arr[1:end-1] if x <= pivot]
    right = [x for x in arr[1:end-1] if x > pivot]
    return vcat(quicksort_seq(left), [pivot], quicksort_seq(right))
end

function quicksort_parallel(arr::Vector{T}; depth::Int=3, cutoff::Int=1_000) where {T}
    if length(arr) <= cutoff || depth <= 0
        return quicksort_seq(arr)
    end
    pivot = arr[end]
    left = T[x for x in arr[1:end-1] if x <= pivot]
    right = T[x for x in arr[1:end-1] if x > pivot]

    # Use @spawn for the two recursive calls (appropriate for just 2 tasks)
    left_task = @spawn quicksort_parallel(left; depth=depth-1, cutoff=cutoff)
    right_result = quicksort_parallel(right; depth=depth-1, cutoff=cutoff)
    left_result = fetch(left_task)
    
    return vcat(left_result, [pivot], right_result)
end

function print_array(arr)
    for v in arr
        print("$v ")
    end
    println()
end

if abspath(PROGRAM_FILE) == @__FILE__
    data = [10, 7, 8, 9, 1, 5, 12, 4, 6, 3, 11, 2]
    print("Original array: ")
    print_array(data)
    out = quicksort_parallel(data; depth=3, cutoff=2)
    print("Sorted array: ")
    print_array(out)
    @assert out == sort(data)
end


