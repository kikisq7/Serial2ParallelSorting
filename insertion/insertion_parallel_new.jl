using Polyester

function parallel_insertion_sort!(arr::Vector)
    n = length(arr)
    n < 2 && return arr

    output = similar(arr)
    @batch for i in 1:n
        value = arr[i]
        rank = 1
        for j in 1:n
            other = arr[j]
            if other < value || (other == value && j < i)
                rank += 1
            end
        end
        output[rank] = value
    end

    copyto!(arr, output)
    return arr
end
