using Polyester

@inline function merge_runs!(src::AbstractVector{T}, dest::AbstractVector{T}, left::Int, mid::Int, right::Int) where {T}
    i = left
    j = mid + 1
    k = left
    @inbounds while i <= mid && j <= right
        if src[i] <= src[j]
            dest[k] = src[i]
            i += 1
        else
            dest[k] = src[j]
            j += 1
        end
        k += 1
    end
    @inbounds while i <= mid
        dest[k] = src[i]
        i += 1
        k += 1
    end
    @inbounds while j <= right
        dest[k] = src[j]
        j += 1
        k += 1
    end
end

function batch_merge_pass!(src, dest, width::Int, n::Int, merge_count::Int)
    @batch for task_idx in 1:merge_count
        @inbounds begin
            left = 1 + (task_idx - 1) * 2 * width
            mid = min(left + width - 1, n)
            right = min(left + 2 * width - 1, n)
            if mid < right
                merge_runs!(src, dest, left, mid, right)
            else
                @inbounds for idx in left:right
                    dest[idx] = src[idx]
                end
            end
        end
    end
end

function parallel_mergesort(arr::Vector{T}) where {T}
    n = length(arr)
    n <= 1 && return copy(arr)
    src = similar(arr)
    copyto!(src, arr)
    dest = similar(src)
    width = 1
    while width < n
        merge_count = cld(n, 2 * width)
        batch_merge_pass!(src, dest, width, n, merge_count)
        src, dest = dest, src
        width *= 2
    end
    return src
end
