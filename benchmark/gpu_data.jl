# GPU-backed random data for large Sorting benchmarks (no huge JSON uploads).
# CUDA.randn on GPU → copyto! CPU → map to Ints in [0, n*10).
# Fallback: chunked CPU RNG. Set FORCE_CPU_DATA=1 to skip GPU.
using Random
using CUDA

function _cpu_fill_ints_chunked(n::Int, seed::UInt64)::Vector{Int}
    rng = Random.MersenneTwister(seed)
    out = Vector{Int}(undef, n)
    modv = max(1, n * 10)
    chunk = 1_000_000
    @inbounds for i in 1:chunk:n
        j = min(i + chunk - 1, n)
        for k in i:j
            out[k] = rand(rng, 0:(modv - 1))
        end
    end
    return out
end

function _gpu_randn_to_ints(n::Int, seed::UInt64)::Vector{Int}
    CUDA.seed!(seed)
    g = CUDA.randn(Float64, n)
    h = Vector{Float64}(undef, n)
    copyto!(h, g)
    modv = max(1, n * 10)
    out = Vector{Int}(undef, n)
    @inbounds for i in 1:n
        out[i] = mod(abs(floor(Int, h[i] * 1.0e12)), modv)
    end
    return out
end

function alloc_and_fill_int_cpu(n::Int, seed::UInt64)::Vector{Int}
    if get(ENV, "FORCE_CPU_DATA", "0") == "1"
        return _cpu_fill_ints_chunked(n, seed)
    end
    if CUDA.functional()
        try
            return _gpu_randn_to_ints(n, seed)
        catch e
            @warn "GPU allocation failed; using CPU RNG" exception = e
        end
    end
    return _cpu_fill_ints_chunked(n, seed)
end
