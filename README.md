# Serial2ParallelSorting

A comprehensive collection of sorting algorithms implemented in both serial and parallel versions across three programming languages: C++, Julia, and Python.

## Algorithms Implemented

- **Insertion Sort**
- **Merge Sort** 
- **Selection Sort**

## Languages

- **C++** - Using `std::async` and `std::future` for parallel execution
- **Julia** - Using `@threads` macro from `Base.Threads`
- **Python** - Using `concurrent.futures.ThreadPoolExecutor`

## Project Structure

```
Serial2ParallelSorting/
├── insertion/
│   ├── insertion.cpp              # Serial C++ implementation
│   ├── insertion_parallel.cpp     # Original parallel C++ implementation
│   ├── insertion_parallel_new.cpp # New parallel C++ implementation
│   ├── insertion.jl               # Serial Julia implementation
│   ├── insertion_parallel.jl      # Original parallel Julia implementation
│   ├── insertion_parallel_new.jl  # New parallel Julia implementation
│   ├── insertion.py               # Serial Python implementation
│   ├── insertion_parallel.py      # Original parallel Python implementation
│   └── insertion_parallel_new.py  # New parallel Python implementation
├── merge/
│   ├── merge.cpp                  # Serial C++ implementation
│   ├── merge_parallel.cpp         # Original parallel C++ implementation
│   ├── merge_parallel_new.cpp     # New parallel C++ implementation
│   ├── merge.jl                   # Serial Julia implementation
│   ├── merge_parallel.jl          # Original parallel Julia implementation
│   ├── merge_parallel_new.jl      # New parallel Julia implementation
│   ├── merge.py                   # Serial Python implementation
│   ├── merge_parallel.py          # Original parallel Python implementation
│   └── merge_parallel_new.py      # New parallel Python implementation
└── selection/
    ├── selection.cpp              # Serial C++ implementation
    ├── selection_parallel.cpp     # Original parallel C++ implementation
    ├── selection_parallel_new.cpp # New parallel C++ implementation
    ├── selection.jl               # Serial Julia implementation
    ├── selection_parallel.jl      # Original parallel Julia implementation
    ├── selection_parallel_new.jl  # New parallel Julia implementation
    ├── selection.py               # Serial Python implementation
    ├── selection_parallel.py      # Original parallel Python implementation
    └── selection_parallel_new.py  # New parallel Python implementation
```

## Parallel Implementation Strategy

All parallel implementations use a **divide-and-conquer** approach:

1. **Divide**: Split the array into smaller chunks
2. **Conquer**: Sort chunks in parallel using multiple threads
3. **Combine**: Merge the sorted chunks back together

### Key Features

- **Threshold-based optimization**: Small arrays use sequential sorting to avoid parallel overhead
- **Thread-safe operations**: All implementations handle concurrent access safely
- **Language-specific optimizations**: Each implementation leverages the best parallel features of its language

## Compilation and Execution

### C++
```bash
# Compile with threading support
g++ -std=c++17 -pthread -O2 <filename>.cpp -o <executable>

# Run
./<executable>
```

### Julia
```bash
# Run directly
julia <filename>.jl
```

### Python
```bash
# Run with Python 3
python3 <filename>.py
```

## Performance Considerations

- Parallel implementations are most effective on multi-core systems
- For small arrays, sequential versions may be faster due to parallel overhead
- The threshold values can be tuned based on system specifications

## Testing

All implementations have been tested and produce correct sorted outputs. Each algorithm maintains the same correctness guarantees as its serial counterpart while potentially offering improved performance through parallelization.

## Contributing

Feel free to contribute improvements, optimizations, or additional sorting algorithms to this repository.
