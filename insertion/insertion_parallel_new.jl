#!/usr/bin/env julia

using Polyester

function insertion_sort_sequential!(arr::Vector, start_idx::Int, end_idx::Int)
    for i in (start_idx + 1):end_idx
        key = arr[i]
        j = i - 1
        
        while j >= start_idx && arr[j] > key
            arr[j+1] = arr[j]
            j -= 1
        end
        arr[j+1] = key
    end
    return arr
end

function merge_sorted_chunks!(arr::Vector{T}, chunks::Vector{Vector{T}}, start_idx::Int) where T
    # Merge all sorted chunks back into the array
    idx = start_idx
    chunk_ptrs = ones(Int, length(chunks))
    
    while true
        # Find the minimum element among all chunk heads
        min_chunk = 0
        min_val::Union{T, Nothing} = nothing
        
        # Find first available chunk to initialize min_val
        for i in 1:length(chunks)
            if chunk_ptrs[i] <= length(chunks[i])
                min_val = chunks[i][chunk_ptrs[i]]
                min_chunk = i
                break
            end
        end
        
        if min_chunk == 0 || min_val === nothing
            break  # All chunks exhausted
        end
        
        # Find the actual minimum
        for i in (min_chunk + 1):length(chunks)
            if chunk_ptrs[i] <= length(chunks[i])
                val = chunks[i][chunk_ptrs[i]]
                if val < min_val
                    min_val = val
                    min_chunk = i
                end
            end
        end
        
        arr[idx] = min_val
        chunk_ptrs[min_chunk] += 1
        idx += 1
    end
end

function parallel_insertion_sort!(arr::Vector)
    n = length(arr)
    if n <= 1
        return arr
    end
    
    # For small arrays, use sequential insertion sort
    if n < 200
        return insertion_sort_sequential!(arr, 1, n)
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
        chunks[i] = insertion_sort_sequential!(chunks[i], 1, length(chunks[i]))
    end
    
    # Merge chunks back into the array
    merge_sorted_chunks!(arr, chunks, 1)
    
    return arr
end

if abspath(PROGRAM_FILE) == @__FILE__
    # Example usage
    my_array = [5, 2, 8, 1, 9, 4, 7, 3, 6, 12, 11, 10]
    println("Original array: ", my_array)
    parallel_insertion_sort!(my_array)
    println("Sorted array: ", my_array)
end
