using Polyester

@inline function partition!(arr, low, high)
    @inbounds pivot = arr[high]
    i = low - 1
    @inbounds for j in low:(high - 1)
        if arr[j] <= pivot
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
        end
    end
    @inbounds arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
end

function batch_partition_frontier!(arr, current, pivots, valid)
    @batch for idx in 1:length(current)
        @inbounds local_low, local_high = current[idx]
        if local_low < local_high
            pivots[idx] = partition!(arr, local_low, local_high)
            valid[idx] = 1
        end
    end
end

function quicksort_parallel_inplace_frontier!(arr)
    low, high = 1, length(arr)
    low >= high && return arr
    current = Tuple{Int, Int}[(low, high)]

    while !isempty(current)
        m = length(current)
        pivots = zeros(Int, m)
        valid = zeros(UInt8, m)

        batch_partition_frontier!(arr, current, pivots, valid)

        next_ranges = Tuple{Int, Int}[]
        sizehint!(next_ranges, max(16, 2 * m))
        @inbounds for idx in 1:m
            valid[idx] == 0 && continue
            local_low, local_high = current[idx]
            pivot_idx = pivots[idx]
            if local_low < pivot_idx - 1
                push!(next_ranges, (local_low, pivot_idx - 1))
            end
            if pivot_idx + 1 < local_high
                push!(next_ranges, (pivot_idx + 1, local_high))
            end
        end
        current = next_ranges
    end
    return arr
end

function quicksort_parallel(arr::AbstractVector{Int})
    n = length(arr)
    work = Vector{Int}(undef, n)
    copyto!(work, arr)
    quicksort_parallel_inplace_frontier!(work)
    return work
end
