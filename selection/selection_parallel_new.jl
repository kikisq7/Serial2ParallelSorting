using Base.Threads
using Polyester

function _selection_ranges(lo::Int, hi::Int, parts::Int)
    hi < lo && return UnitRange{Int}[]
    total = hi - lo + 1
    actual = min(max(parts, 1), total)
    ranges = Vector{UnitRange{Int}}(undef, actual)
    base, extra = divrem(total, actual)
    start = lo

    for idx in 1:actual
        len = base + (idx <= extra ? 1 : 0)
        stop = start + len - 1
        ranges[idx] = start:stop
        start = stop + 1
    end

    return ranges
end

function parallel_selection_sort!(arr::Vector)
    n = length(arr)
    n < 2 && return arr

    for i in 1:(n - 1)
        ranges = _selection_ranges(i, n, Threads.nthreads())
        local_min = fill(i, length(ranges))

        @batch for ridx in eachindex(ranges)
            min_idx = first(ranges[ridx])
            for j in ranges[ridx]
                if arr[j] < arr[min_idx]
                    min_idx = j
                end
            end
            local_min[ridx] = min_idx
        end

        min_idx = local_min[1]
        for idx in local_min
            if arr[idx] < arr[min_idx]
                min_idx = idx
            end
        end

        if min_idx != i
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
        end
    end

    return arr
end
