using Polyester

function phase!(arr::Vector{T}, start::Int) where {T}
    n = length(arr)
    if n < 2
        return false
    end
    
    swapped = false
    range_max = (n - 1 - start) ÷ 2
    
    # Only parallelize if we have enough work to justify overhead
    # Each task should handle at least ~50 comparisons to amortize overhead
    min_work_per_task = 50
    if range_max > min_work_per_task * 4  # Need at least 4 tasks worth of work
        # Chunk the work: each @batch iteration handles multiple comparisons
        num_tasks = min(Threads.nthreads() * 4, range_max ÷ min_work_per_task)
        num_tasks = max(1, num_tasks)  # At least 1 task
        chunk_size = max(1, range_max ÷ num_tasks)
        
        local_swapped = Ref(false)
        @batch for task_id in 0:(num_tasks-1)
            task_start = task_id * chunk_size
            task_end = min((task_id + 1) * chunk_size - 1, range_max)
            
            for k in task_start:task_end
                i = start + 2*k
                if i + 1 <= n && arr[i] > arr[i + 1]
                    # Apply swap - thread-safe since each task handles distinct indices
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    local_swapped[] = true
                end
            end
        end
        swapped = local_swapped[]
    else
        # Sequential for small ranges to avoid overhead
        for k in 0:range_max
            i = start + 2*k
            if i + 1 <= n && arr[i] > arr[i + 1]
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = true
            end
        end
    end
    
    return swapped
end

function bubble_sort_parallel!(arr::Vector{T}) where {T}
    n = length(arr)
    if n <= 1
        return arr
    end
    swapped = true
    while swapped
        swapped = false
        swapped |= phase!(arr, 1)  # even indices in Julia (1-based)
        swapped |= phase!(arr, 2)  # odd indices in Julia (1-based)
    end
    return arr
end

function print_array(arr)
    for v in arr
        print("$v ")
    end
    println()
end

if abspath(PROGRAM_FILE) == @__FILE__
    arr = [64, 34, 25, 12, 22, 11, 90, 5, 3, 8, 7, 2]
    print("Original array: ")
    print_array(arr)
    bubble_sort_parallel!(arr)
    print("Sorted array: ")
    print_array(arr)
    @assert arr == sort(arr)
end


