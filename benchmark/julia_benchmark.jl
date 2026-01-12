#!/usr/bin/env julia

using Statistics

push!(LOAD_PATH, abspath(joinpath(@__DIR__, "..")))

include(joinpath(@__DIR__, "..", "bubble", "bubble_parallel.jl"))
include(joinpath(@__DIR__, "..", "insertion", "insertion_parallel_new.jl"))
include(joinpath(@__DIR__, "..", "merge", "merge_parallel_new.jl"))
include(joinpath(@__DIR__, "..", "quick", "quick_parallel.jl"))
include(joinpath(@__DIR__, "..", "selection", "selection_parallel_new.jl"))

include(joinpath(@__DIR__, "..", "bubble", "bubble.jl"))
include(joinpath(@__DIR__, "..", "insertion", "insertion.jl"))
include(joinpath(@__DIR__, "..", "merge", "merge.jl"))
include(joinpath(@__DIR__, "..", "quick", "quick.jl"))
include(joinpath(@__DIR__, "..", "selection", "selection.jl"))
# const TEST_SIZES = [10^7, 10^8]
const TEST_SIZES = [10^4]
const ITER = 3
const WARMUP = 1

function read_data(n::Int, iteration::Union{Int, Nothing} = nothing)
    if iteration !== nothing
        # Try numbered dataset file first
        path = joinpath(@__DIR__, "..", "test_data", "data_$(n)_$(iteration + 1).txt")
        if isfile(path)
            open(path, "r") do io
                return parse.(Int, split(readline(io)))
            end
        end
    end
    # Fallback to default file
    path = joinpath(@__DIR__, "..", "test_data", "data_$(n).txt")
    open(path, "r") do io
        return parse.(Int, split(readline(io)))
    end
end

function time_once(f)
    t0 = time_ns()
    f()
    return time_ns() - t0
end

function bench_algo(name::String, f::Function, size::Int; inplace::Bool=false)
    times = Int[]

    # Warmup with first dataset
    warmup_data = read_data(size, 0)
    for _ in 1:WARMUP
        x = copy(warmup_data)
        if inplace
            f(x)
        else
            _ = f(x)
        end
    end

    for iteration in 1:ITER
        # Load different dataset for each iteration
        data = read_data(size, iteration - 1)
        x = copy(data)
        dt = time_once(() -> begin
            if inplace
                f(x)
            else
                _ = f(x)
            end
        end)
        push!(times, dt)
    end

    mean_ns = round(mean(times))
    median_ns = round(median(times))
    std_ns = length(times) > 1 ? round(std(times)) : 0
    (; name, mean_ns, median_ns, std_ns, min_ns = minimum(times), max_ns = maximum(times))
end

function main()
    println("Julia Parallel vs Serial Sorting Algorithm Benchmark")
    println("====================================================")

    algos = [
        ("bubble_parallel", (x)->bubble_sort_parallel!(x), "bubble_serial", (x)->bubble_sort!(x), true),
        ("insertion_parallel", (x)->parallel_insertion_sort!(x), "insertion_serial", (x)->insertion_sort!(x), true),
        ("merge_parallel", (x)->parallel_mergesort(x), "merge_serial", (x)->mergesort(x), false),
        ("quick_parallel", (x)->quicksort_parallel(x), "quick_serial", (x)->quicksort!(x), true),
        ("selection_parallel", (x)->parallel_selection_sort!(x), "selection_serial", (x)->selection_sort!(x), true),
    ]

    for n in TEST_SIZES
        println("\n--- Size: $n ---")

        println("Benchmarking builtin_sort...")
        builtin_res = bench_algo("builtin_sort", x->sort(x), n, inplace=false)

        for (parallel_name, parallel_func, serial_name, serial_func, inplace) in algos
            println("Benchmarking $parallel_name...")
            try
                parallel_res = bench_algo(parallel_name, parallel_func, n, inplace=inplace)
                
                println("Benchmarking $serial_name...")
                serial_res = bench_algo(serial_name, serial_func, n, inplace=inplace)
                
                parallel_vs_serial = serial_res.mean_ns / parallel_res.mean_ns
                parallel_vs_serial_text = parallel_vs_serial > 1 ? "(parallel faster)" : "(serial faster)"
                
                println("\nComparing $parallel_name vs $serial_name vs builtin_sort:")
                println("  $parallel_name: $(round(parallel_res.mean_ns/1e6, digits=6)) ms")
                println("  $serial_name: $(round(serial_res.mean_ns/1e6, digits=6)) ms")
                println("  builtin_sort: $(round(builtin_res.mean_ns/1e6, digits=6)) ms")
                println("  $parallel_name vs $serial_name: $(round(parallel_vs_serial, digits=2))x $parallel_vs_serial_text")
                
                parallel_vs_builtin = builtin_res.mean_ns / parallel_res.mean_ns
                serial_vs_builtin = builtin_res.mean_ns / serial_res.mean_ns
                println("  builtin_sort vs $parallel_name: $(round(parallel_vs_builtin, digits=2))x")
                println("  builtin_sort vs $serial_name: $(round(serial_vs_builtin, digits=2))x")
                println()
            catch e
                println("ERROR: Failed to benchmark $parallel_name / $serial_name")
                println("  ", e)
                println()
            end
        end
    end
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end