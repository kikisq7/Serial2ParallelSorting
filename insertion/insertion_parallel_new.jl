using Base.Threads
using Polyester

const _INSERT_MIN_UPPER_PARALLEL = 9216
const _INSERT_MIN_ELEMS_PER_CHUNK = 512

function batch_count_leq!(arr, upper::Int, key, partial::Vector{Int}, nchunks::Int)
    nt = length(partial)
    fill!(partial, 0)
    upper <= 0 && return partial
    chunks = max(1, min(nchunks, upper, nt))
    base, extra = divrem(upper, chunks)
    @batch for chunk in 1:chunks
        @inbounds begin
            len = base + (chunk <= extra ? 1 : 0)
            lo = (chunk - 1) * base + min(chunk - 1, extra) + 1
            hi = lo + len - 1
            c = 0
            for j in lo:hi
                if arr[j] <= key
                    c += 1
                end
            end
            partial[chunk] = c
        end
    end
    return partial
end

@inline function serial_count_leq(arr, upper::Int, key)::Int
    c = 0
    @inbounds for j in 1:upper
        c += arr[j] <= key ? 1 : 0
    end
    return c
end

function parallel_insertion_sort!(arr::Vector{T}) where {T}
    n = length(arr)
    n <= 1 && return arr
    nt = max(1, nthreads())
    partial = zeros(Int, nt)

    @inbounds for i in 2:n
        key = arr[i]
        upper = i - 1
        if upper < _INSERT_MIN_UPPER_PARALLEL
            s = serial_count_leq(arr, upper, key)
        else
            chunks = max(1, min(nt, cld(upper, _INSERT_MIN_ELEMS_PER_CHUNK)))
            batch_count_leq!(arr, upper, key, partial, chunks)
            s = partial[1]
            @inbounds for k in 2:chunks
                s += partial[k]
            end
        end
        position = s + 1
        position == i && continue

        segment = copy(arr[position:i-1])
        copyto!(arr, position + 1, segment, 1, length(segment))
        arr[position] = key
    end
    return arr
end
