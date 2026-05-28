function partition_ranges(lo::Int, hi::Int, parts::Int)
    hi < lo && return UnitRange{Int}[]

    total = hi - lo + 1
    actual = max(1, min(parts, total))
    ranges = Vector{UnitRange{Int}}(undef, actual)

    base, extra = divrem(total, actual)
    start = lo
    for worker in 1:actual
        length = base + (worker <= extra ? 1 : 0)
        stop = start + length - 1
        ranges[worker] = start:stop
        start = stop + 1
    end

    return ranges
end
