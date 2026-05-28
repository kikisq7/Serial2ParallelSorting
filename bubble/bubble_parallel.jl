using Polyester

function bubble_sort_parallel!(arr::Vector)
    n = length(arr)
    n < 2 && return arr

    for phase in 0:(n - 1)
        start = 1 + (phase % 2)
        pair_count = div(n - start, 2) + 1
        @batch for pair_idx in 0:(pair_count - 1)
            j = start + 2 * pair_idx
            if j < n && arr[j] > arr[j + 1]
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
            end
        end
    end

    return arr
end
