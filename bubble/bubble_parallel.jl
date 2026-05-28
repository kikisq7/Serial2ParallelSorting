using Polyester

function bubble_sort_parallel!(arr::Vector)
    n = length(arr)
    n < 2 && return arr

    for phase in 0:(n - 1)
        start = 1 + (phase % 2)
        @batch for j in start:2:(n - 1)
            if arr[j] > arr[j + 1]
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
            end
        end
    end

    return arr
end
