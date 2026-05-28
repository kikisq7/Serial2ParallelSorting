using Polyester

function parallel_mergesort(arr::Vector)
    n = length(arr)
    n < 2 && return copy(arr)

    source = copy(arr)
    dest = similar(source)
    width = 1

    while width < n
        w = width
        block_count = cld(n, 2 * w)
        @batch for block in 0:(block_count - 1)
            left = block * 2 * w + 1
            mid = min(left + w, n + 1)
            right = min(left + 2 * w, n + 1)
            i = left
            j = mid
            k = left

            while i < mid && j < right
                if source[i] <= source[j]
                    dest[k] = source[i]
                    i += 1
                else
                    dest[k] = source[j]
                    j += 1
                end
                k += 1
            end

            while i < mid
                dest[k] = source[i]
                i += 1
                k += 1
            end

            while j < right
                dest[k] = source[j]
                j += 1
                k += 1
            end
        end
        source, dest = dest, source
        width *= 2
    end

    return source
end
