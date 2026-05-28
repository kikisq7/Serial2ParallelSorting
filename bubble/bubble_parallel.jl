using Polyester
using Base.Threads: nthreads

"""Odd–even (transposition) bubble sort phases; stop after two successive idle phases."""

function serial_adjacent_swaps!(arr, start::Int, pair_count::Int)::Bool
    any_swap = false
    @inbounds for pair_idx in 1:pair_count
        j = start + 2 * (pair_idx - 1)
        if arr[j] > arr[j + 1]
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
            any_swap = true
        end
    end
    return any_swap
end

# Few coarse parallel chunks; each chunk runs many pair-swaps serially (no cross-thread atomics).
const _BUBBLE_SERIAL_PAIR_THRESHOLD = 2048
const _BUBBLE_MIN_PAIRS_PER_CHUNK = 768

function batch_adjacent_swaps_chunked!(arr, start::Int, pair_count::Int, chunk_sw::Vector{UInt8})::Bool
    nt = nthreads()
    nchunks = max(1, min(nt, cld(pair_count, _BUBBLE_MIN_PAIRS_PER_CHUNK), pair_count))
    if nchunks == 1
        return serial_adjacent_swaps!(arr, start, pair_count)
    end

    base, extra = divrem(pair_count, nchunks)
    @batch for c in 1:nchunks
        len = base + (c <= extra ? 1 : 0)
        lo = (c - 1) * base + min(c - 1, extra) + 1
        hi = lo + len - 1
        local_sw = false
        @inbounds for pair_idx in lo:hi
            j = start + 2 * (pair_idx - 1)
            if arr[j] > arr[j + 1]
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                local_sw = true
            end
        end
        chunk_sw[c] = local_sw ? UInt8(1) : UInt8(0)
    end
    @inbounds for c in 1:nchunks
        chunk_sw[c] != 0 && return true
    end
    return false
end

@inline function phase_adjacent_swaps!(arr, start::Int, pair_count::Int, chunk_sw::Vector{UInt8})::Bool
    pair_count <= 0 && return false
    if pair_count ≤ _BUBBLE_SERIAL_PAIR_THRESHOLD
        return serial_adjacent_swaps!(arr, start, pair_count)
    end
    return batch_adjacent_swaps_chunked!(arr, start, pair_count, chunk_sw)
end

function bubble_sort_parallel!(arr)
    n = length(arr)
    n <= 1 && return arr

    nt = max(1, nthreads())
    chunk_sw = Vector{UInt8}(undef, nt)

    no_swap_prev = false
    @inbounds for phase in 1:n
        start = isodd(phase) ? 1 : 2
        pair_count = (n - start + 1) ÷ 2
        swapped = phase_adjacent_swaps!(arr, start, pair_count, chunk_sw)
        if !swapped
            if no_swap_prev
                break
            end
            no_swap_prev = true
        else
            no_swap_prev = false
        end
    end

    return arr
end
