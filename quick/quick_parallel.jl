using Polyester

function quicksort_parallel(arr::Vector)
    work = copy(arr)
    n = length(work)
    n < 2 && return work

    segments = Tuple{Int, Int}[(1, n)]
    while !isempty(segments)
        left_children = Vector{Tuple{Int, Int}}(undef, length(segments))
        right_children = Vector{Tuple{Int, Int}}(undef, length(segments))
        has_left = falses(length(segments))
        has_right = falses(length(segments))

        @batch for idx in eachindex(segments)
            low, high = segments[idx]
            if low < high
                pivot = work[high]
                pivot_index = low - 1
                for j in low:(high - 1)
                    if work[j] < pivot
                        pivot_index += 1
                        work[pivot_index], work[j] = work[j], work[pivot_index]
                    end
                end
                pivot_index += 1
                work[pivot_index], work[high] = work[high], work[pivot_index]

                if low < pivot_index - 1
                    left_children[idx] = (low, pivot_index - 1)
                    has_left[idx] = true
                end
                if pivot_index + 1 < high
                    right_children[idx] = (pivot_index + 1, high)
                    has_right[idx] = true
                end
            end
        end

        next_segments = Tuple{Int, Int}[]
        for idx in eachindex(segments)
            has_left[idx] && push!(next_segments, left_children[idx])
            has_right[idx] && push!(next_segments, right_children[idx])
        end
        segments = next_segments
    end

    return work
end
