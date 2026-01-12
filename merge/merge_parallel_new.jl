#!/usr/bin/env julia

using Polyester

function merge(left::Vector, right::Vector)
    result = eltype(left)[]
    i, j = 1, 1 # Pointers for left and right arrays

    while i <= length(left) && j <= length(right)
        if left[i] <= right[j]
            push!(result, left[i])
            i += 1
        else
            push!(result, right[j])
            j += 1
        end
    end

    while i <= length(left)
        push!(result, left[i])
        i += 1
    end

    while j <= length(right)
        push!(result, right[j])
        j += 1
    end

    return result
end

function sequential_mergesort(arr::Vector)
    n = length(arr)
    if n <= 1
        return arr
    end
    
    mid = n ÷ 2
    left = arr[1:mid]
    right = arr[mid+1:n]
    
    left_sorted = sequential_mergesort(left)
    right_sorted = sequential_mergesort(right)
    
    return merge(left_sorted, right_sorted)
end

function parallel_mergesort(arr::Vector)
    n = length(arr)
    if n <= 1
        return arr
    end
    
    # For small arrays, use sequential merge sort
    if n < 200
        return sequential_mergesort(arr)
    end
    
    # Bottom-up approach: divide into chunks and sort all in parallel
    # Adaptive chunk size: aim for 3-8 chunks depending on array size
    target_chunks = min(8, max(3, n ÷ 250))  # 3-8 chunks, roughly
    chunk_size = max(150, n ÷ target_chunks)
    num_chunks = (n + chunk_size - 1) ÷ chunk_size  # Ceiling division
    
    # Create chunks
    chunks = Vector{Vector{eltype(arr)}}(undef, num_chunks)
    for i in 1:num_chunks
        start_idx = (i - 1) * chunk_size + 1
        end_idx = min(i * chunk_size, n)
        chunks[i] = arr[start_idx:end_idx]
    end
    
    # Sort all chunks in parallel using Polyester
    @batch for i in 1:num_chunks
        chunks[i] = sequential_mergesort(chunks[i])
    end
    
    # Merge chunks sequentially
    while length(chunks) > 1
        merged_chunks = Vector{Vector{eltype(arr)}}()
        i = 1
        while i <= length(chunks)
            if i + 1 <= length(chunks)
                # Merge two adjacent chunks
                push!(merged_chunks, merge(chunks[i], chunks[i+1]))
                i += 2
            else
                # Last chunk if odd number
                push!(merged_chunks, chunks[i])
                i += 1
            end
        end
        chunks = merged_chunks
    end
    
    return chunks[1]
end

if abspath(PROGRAM_FILE) == @__FILE__
    # Example usage
    arr = [7, 6, 5, 9, 8, 4, 3, 1, 2, 0, 12, 11, 10, 15, 14, 13]
    println("Original array: ", arr)
    sorted_arr = parallel_mergesort(arr)
    println("Sorted array: ", sorted_arr)
end