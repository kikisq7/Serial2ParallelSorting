#!/usr/bin/env julia

using BenchmarkTools
using Statistics
using Base.Sort
using Base.Threads

push!(LOAD_PATH, abspath(joinpath(@__DIR__, "..")))

const _USE_CUDA_DATA = get(ENV, "USE_CUDA_DATA", "0") == "1"
if _USE_CUDA_DATA
    include(joinpath(@__DIR__, "gpu_data.jl"))
end

function parse_test_sizes()
    s = get(ENV, "BENCHMARK_SIZES", "")
    if !isempty(strip(s))
        return [parse(Int, strip(x)) for x in split(s, ',') if !isempty(strip(x))]
    end
    return [
        10^3,
        10^4,
        2 * 10^4,
        4 * 10^4,
        8 * 10^4,
        10^5,
        2 * 10^5,
        4 * 10^5,
        8 * 10^5,
        10^6,
    ]
end

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

const TEST_SIZES = parse_test_sizes()
const ITER = 3
const WARMUP = 1

const PARALLEL_THREADS = 32

function read_data(n::Int, iteration::Union{Int, Nothing} = nothing)
    if _USE_CUDA_DATA
        seed = UInt64(42 + (iteration === nothing ? 0 : iteration + 1))
        return alloc_and_fill_int_cpu(n, seed)
    end
    if iteration !== nothing
        path = joinpath(@__DIR__, "..", "test_data", "data_$(n)_$(iteration + 1).txt")
        if isfile(path)
            open(path, "r") do io
                return parse.(Int, split(readline(io)))
            end
        end
    end
    path = joinpath(@__DIR__, "..", "test_data", "data_$(n).txt")
    open(path, "r") do io
        return parse.(Int, split(readline(io)))
    end
end

"""inplace=true: mutating sort (or returns nothing). inplace=false: returns a sorted vector."""
function verify_sorted!(f::Function, data::Vector{Int}, inplace::Bool)
    work = copy(data)
    if inplace
        f(work)
        issorted(work) || error("Correctness failed (in-place sort not ordered)")
    else
        out = f(work)
        (out === nothing) && error("Correctness failed (expected a return value for out-of-place verify)")
        issorted(out) || error("Correctness failed (out-of-place sort not ordered)")
    end
    return nothing
end

function summarize_times(iter_medians::Vector{Float64}, name::String)
    mean_ns = round(mean(iter_medians))
    median_ns = round(median(iter_medians))
    std_ns = length(iter_medians) > 1 ? round(std(iter_medians)) : 0
    (; name, mean_ns, median_ns, std_ns, min_ns = round(minimum(iter_medians)), max_ns = round(maximum(iter_medians)))
end

# Serial and parallel (and baselines) measured on identical `data` each iteration.
function bench_paired_parallel_block(
    n::Int,
    parallel_func,
    serial_func,
    julia_alg_func,
    builtin_f;
    parallel_ip::Bool,
    serial_ip::Bool,
    julia_ip::Bool,
    parallel_name::String,
    serial_name::String,
    julia_alg_name::String,
)
    p_med = Float64[]
    s_med = Float64[]
    j_med = Float64[]
    b_med = Float64[]

    for iteration in 1:ITER
        data = read_data(n, iteration - 1)
        verify_sorted!(parallel_func, data, parallel_ip)
        verify_sorted!(serial_func, data, serial_ip)
        verify_sorted!(julia_alg_func, data, julia_ip)
        verify_sorted!(builtin_f, data, false)

        for _ in 1:WARMUP
            w = copy(data)
            parallel_func(w)
            w = copy(data)
            serial_func(w)
            w = copy(data)
            julia_alg_func(w)
            w = copy(data)
            builtin_f(w)
        end

        tp = @benchmark ($parallel_func)(work) setup = (work = copy($data)) evals = 1 seconds = 1.0
        ts = @benchmark ($serial_func)(work) setup = (work = copy($data)) evals = 1 seconds = 1.0
        tj = @benchmark ($julia_alg_func)(work) setup = (work = copy($data)) evals = 1 seconds = 1.0
        tb = @benchmark ($builtin_f)(work) setup = (work = copy($data)) evals = 1 seconds = 1.0
        push!(p_med, median(tp.times))
        push!(s_med, median(ts.times))
        push!(j_med, median(tj.times))
        push!(b_med, median(tb.times))
    end

    parallel_res = summarize_times(p_med, parallel_name)
    serial_res = summarize_times(s_med, serial_name)
    julia_alg_res = summarize_times(j_med, "builtin_$(julia_alg_name)")
    builtin_res = summarize_times(b_med, "builtin_sort")

    parallel_vs_serial = serial_res.mean_ns / parallel_res.mean_ns
    parallel_vs_serial_text = parallel_vs_serial > 1 ? "(parallel faster)" : "(serial faster)"

    println("\nComparing $parallel_name vs $serial_name vs builtin_sort(alg=$julia_alg_name) vs builtin_sort(default):")
    println("  $parallel_name: $(round(parallel_res.mean_ns/1e6, digits=6)) ms")
    println("  $serial_name: $(round(serial_res.mean_ns/1e6, digits=6)) ms")
    println("  builtin_sort(alg=$julia_alg_name): $(round(julia_alg_res.mean_ns/1e6, digits=6)) ms")
    println("  builtin_sort(default): $(round(builtin_res.mean_ns/1e6, digits=6)) ms")
    println("  $parallel_name vs $serial_name: $(round(parallel_vs_serial, digits=2))x $parallel_vs_serial_text")

    parallel_vs_julia_alg = julia_alg_res.mean_ns / parallel_res.mean_ns
    serial_vs_julia_alg = julia_alg_res.mean_ns / serial_res.mean_ns
    println("  builtin_sort(alg=$julia_alg_name) vs $parallel_name: $(round(parallel_vs_julia_alg, digits=2))x")
    println("  builtin_sort(alg=$julia_alg_name) vs $serial_name: $(round(serial_vs_julia_alg, digits=2))x")

    parallel_vs_builtin = builtin_res.mean_ns / parallel_res.mean_ns
    serial_vs_builtin = builtin_res.mean_ns / serial_res.mean_ns
    julia_alg_vs_builtin = builtin_res.mean_ns / julia_alg_res.mean_ns
    println("  builtin_sort(default) vs $parallel_name: $(round(parallel_vs_builtin, digits=2))x")
    println("  builtin_sort(default) vs $serial_name: $(round(serial_vs_builtin, digits=2))x")
    println("  builtin_sort(default) vs builtin_sort(alg=$julia_alg_name): $(round(julia_alg_vs_builtin, digits=2))x")
    println()
end

function run_benchmarks()
    println("Julia Parallel vs Serial Sorting Algorithm Benchmark")
    println("=" ^ 60)
    println("Thread count: $(Threads.nthreads())  BENCHMARK_SIZES=$(join(TEST_SIZES, ','))")

    if Threads.nthreads() != PARALLEL_THREADS
        @warn "Expected $PARALLEL_THREADS thread(s) for parallel implementations, but got $(Threads.nthreads())"
        println("Run with: julia -t $PARALLEL_THREADS $(basename(@__FILE__))")
    end

    # parallel_ip / serial_ip / julia_ip: how each implementation treats the buffer (see verify_sorted!)
    algos = [
        ("bubble_parallel", bubble_sort_parallel!, "bubble_serial", bubble_sort!, true, true, true, InsertionSort, true),
        ("insertion_parallel", parallel_insertion_sort!, "insertion_serial", insertion_sort!, true, true, true, InsertionSort, true),
        ("merge_parallel", parallel_mergesort, "merge_serial", mergesort, false, false, false, MergeSort, false),
        ("quick_parallel", quicksort_parallel, "quick_serial", quicksort!, false, true, false, QuickSort, false),
        ("selection_parallel", parallel_selection_sort!, "selection_serial", selection_sort!, true, true, true, InsertionSort, true),
    ]

    builtin_f = x -> sort(x)

    for n in TEST_SIZES
        println("\n--- Size: $n ---")

        for (parallel_name, parallel_func, serial_name, serial_func, p_ip, s_ip, j_ip, julia_alg) in algos
            println("Benchmarking $parallel_name vs $serial_name (paired datasets)...")
            try
                julia_alg_name = string(julia_alg)
                julia_alg_func = j_ip ? (x -> sort!(x, alg = julia_alg)) : (x -> sort(x, alg = julia_alg))
                bench_paired_parallel_block(
                    n, parallel_func, serial_func, julia_alg_func, builtin_f;
                    parallel_ip = p_ip,
                    serial_ip = s_ip,
                    julia_ip = j_ip,
                    parallel_name = parallel_name,
                    serial_name = serial_name,
                    julia_alg_name = julia_alg_name,
                )
            catch e
                println("ERROR: Failed to benchmark $parallel_name / $serial_name")
                println("  ", e)
                println()
            end
        end
    end

    println("\nBenchmark complete!")
end

function main()
    mode = length(ARGS) > 0 ? ARGS[1] : "default"

    if mode in ("default", "both", "parallel", "all")
        run_benchmarks()
    elseif mode == "serial"
        @warn "serial-only mode is deprecated; running paired parallel vs serial benchmark instead"
        run_benchmarks()
    else
        error("Unknown mode: $mode. Use default (no args) or 'all'")
    end
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
