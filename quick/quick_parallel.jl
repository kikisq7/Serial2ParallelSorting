using Polyester

function _partition_segment!(segment::Vector{Int})
    low = 1
    high = length(segment)
    pivot = segment[high]
    pivot_index = low - 1
    for j in low:(high - 1)
        if segment[j] < pivot
            pivot_index += 1
            segment[pivot_index], segment[j] = segment[j], segment[pivot_index]
        end
    end
    pivot_index += 1
    segment[pivot_index], segment[high] = segment[high], segment[pivot_index]
    return pivot_index
end

function quicksort_parallel(arr::Vector{Int})
    work = copy(arr)
    n = length(work)
    n < 2 && return work

    segments = Tuple{Int, Int}[(1, n)]
    while !isempty(segments)
        segment_count = length(segments)
        partitioned = Vector{Vector{Int}}(undef, segment_count)
        pivot_locals = Vector{Int}(undef, segment_count)
        active = Vector{Int}(undef, 0)

        for idx in 1:segment_count
            low, high = segments[idx]
            if low < high
                partitioned[idx] = copy(@view work[low:high])
                push!(active, idx)
            end
        end

        @batch for pos in eachindex(active)
            idx = active[pos]
            pivot_locals[idx] = _partition_segment!(partitioned[idx])
        end

        left_children = Vector{Tuple{Int, Int}}(undef, segment_count)
        right_children = Vector{Tuple{Int, Int}}(undef, segment_count)
        has_left = falses(segment_count)
        has_right = falses(segment_count)

        for idx in active
            low, high = segments[idx]
            work[low:high] = partitioned[idx]
            pivot_local = pivot_locals[idx]
            global_pivot = low + pivot_local - 1
            if low < global_pivot - 1
                left_children[idx] = (low, global_pivot - 1)
                has_left[idx] = true
            end
            if global_pivot + 1 < high
                right_children[idx] = (global_pivot + 1, high)
                has_right[idx] = true
            end
        end

        next_segments = Tuple{Int, Int}[]
        for idx in 1:segment_count
            has_left[idx] && push!(next_segments, left_children[idx])
            has_right[idx] && push!(next_segments, right_children[idx])
        end
        segments = next_segments
    end

    return work
end
