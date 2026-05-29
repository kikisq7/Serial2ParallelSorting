using Polyester

function _partition_segment!(segment::Vector)
    pivot = segment[end]
    pivot_index = 0
    for j in 1:(length(segment) - 1)
        if segment[j] < pivot
            pivot_index += 1
            segment[pivot_index], segment[j] = segment[j], segment[pivot_index]
        end
    end
    pivot_index += 1
    segment[pivot_index], segment[end] = segment[end], segment[pivot_index]
    return pivot_index
end

function quicksort_parallel(arr::Vector)
    work = copy(arr)
    n = length(work)
    n < 2 && return work

    segments = Tuple{Int, Int}[(1, n)]
    while !isempty(segments)
        active_segments = Tuple{Int, Int}[]
        partitioned = Vector{Vector{eltype(work)}}()
        for (low, high) in segments
            if low < high
                push!(active_segments, (low, high))
                push!(partitioned, work[low:high])
            end
        end

        isempty(active_segments) && break

        pivot_offsets = Vector{Int}(undef, length(active_segments))
        @batch for idx in eachindex(partitioned)
            pivot_offsets[idx] = _partition_segment!(partitioned[idx])
        end

        next_segments = Tuple{Int, Int}[]
        for idx in eachindex(active_segments)
            low, high = active_segments[idx]
            work[low:high] = partitioned[idx]

            pivot_index = low + pivot_offsets[idx] - 1
            if low < pivot_index - 1
                push!(next_segments, (low, pivot_index - 1))
            end
            if pivot_index + 1 < high
                push!(next_segments, (pivot_index + 1, high))
            end
        end
        segments = next_segments
    end

    return work
end
