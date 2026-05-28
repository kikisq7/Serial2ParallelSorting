using Base.Threads
using Polyester

const _SEL_MIN_CHUNK_ELEMS = 512

function batch_selection_local_mins!(arr, lo::Int, hi::Int, local_mins::Vector{Int}, nchunks::Int)
    nt = length(local_mins)
    span = hi - lo + 1
    @assert span >= 1
    chunks = max(1, min(nchunks, span, nt))
    base, extra = divrem(span, chunks)
    @batch for chunk in 1:chunks
        @inbounds begin
            len = base + (chunk <= extra ? 1 : 0)
            chunk_lo = lo + (chunk - 1) * base + min(chunk - 1, extra)
            chunk_hi = chunk_lo + len - 1
            min_idx = chunk_lo
            for j in (chunk_lo + 1):chunk_hi
                if arr[j] < arr[min_idx]
                    min_idx = j
                end
            end
            local_mins[chunk] = min_idx
        end
    end
end

function serial_argmin_segment(arr, lo::Int, hi::Int)::Int
    @inbounds min_idx = lo
    @inbounds for j in (lo + 1):hi
        if arr[j] < arr[min_idx]
            min_idx = j
        end
    end
    return min_idx
end

function parallel_selection_sort!(arr::Vector)
    n = length(arr)
    n <= 1 && return arr
    nt = max(1, nthreads())
    local_mins = Vector{Int}(undef, nt)

    @inbounds for i in 1:(n - 1)
        span = n - i + 1
        raw_chunks = cld(span, _SEL_MIN_CHUNK_ELEMS)
        chunks = max(1, min(nt, raw_chunks))
        if chunks == 1
            min_idx = serial_argmin_segment(arr, i, n)
        else
            batch_selection_local_mins!(arr, i, n, local_mins, chunks)
            min_idx = local_mins[1]
            for chunk in 2:chunks
                candidate = local_mins[chunk]
                if arr[candidate] < arr[min_idx] || (arr[candidate] == arr[min_idx] && candidate < min_idx)
                    min_idx = candidate
                end
            end
        end
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    end
    return arr
end
