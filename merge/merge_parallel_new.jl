using Polyester

function _merge_block(source::AbstractVector{Int}, left::Int, mid::Int, right::Int)
    buf = Vector{Int}(undef, right - left)
    i = left
    j = mid
    k = 1

    while i < mid && j < right
        if source[i] <= source[j]
            buf[k] = source[i]
            i += 1
        else
            buf[k] = source[j]
            j += 1
        end
        k += 1
    end

    while i < mid
        buf[k] = source[i]
        i += 1
        k += 1
    end

    while j < right
        buf[k] = source[j]
        j += 1
        k += 1
    end

    return buf
end

function parallel_mergesort(arr::Vector{Int})
    n = length(arr)
    n < 2 && return copy(arr)

    source = copy(arr)
    dest = similar(source)
    width = 1

    while width < n
        w = width
        block_count = cld(n, 2 * w)
        merged = Vector{Vector{Int}}(undef, block_count)

        @batch for block in 1:block_count
            left = (block - 1) * 2 * w + 1
            mid = min(left + w, n + 1)
            right = min(left + 2 * w, n + 1)
            merged[block] = _merge_block(source, left, mid, right)
        end

        for block in 1:block_count
            left = (block - 1) * 2 * w + 1
            right = min(left + 2 * w, n + 1)
            len = right - left
            dest[left:(left + len - 1)] = merged[block]
        end

        source, dest = dest, source
        width *= 2
    end

    return source
end
