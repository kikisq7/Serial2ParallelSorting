#!/usr/bin/env python3

import copy
import os
import statistics
import sys
import time
from typing import Any, Callable, Dict, List, Optional

# Add parent directory to path to import sorting modules
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_ROOT)

# Import parallel sorting functions
try:
    from insertion.insertion_parallel_new import parallel_insertion_sort
except ImportError:
    parallel_insertion_sort = None

try:
    from merge.merge_parallel_new import parallel_merge_sort
except ImportError:
    parallel_merge_sort = None

try:
    from quick.quick_parallel import quicksort_parallel
except ImportError:
    quicksort_parallel = None

try:
    from selection.selection_parallel_new import parallel_selection_sort
except ImportError:
    parallel_selection_sort = None

# Import serial sorting functions
try:
    from insertion.insertion import insertionSort
except ImportError:
    insertionSort = None

try:
    from merge.merge import mergeSort
except ImportError:
    mergeSort = None

try:
    from quick.quick import quicksort
except ImportError:
    quicksort = None

try:
    from selection.selection import selection_sort
except ImportError:
    selection_sort = None

# Benchmark configuration
BENCHMARK_ITERATIONS = 3
WARMUP_ITERATIONS = 1
NS_PER_SEC = 1_000_000_000
MS_PER_NS = 1_000_000

def load_test_data(size: int) -> List[int]:
    data_path = os.path.join(REPO_ROOT, "test_data", f"data_{size}.txt")
    with open(data_path, 'r') as f:
        return [int(x) for x in f.read().split()]

def _invoke_algorithm(algorithm_name: str, algorithm_func: Callable, data: List[int]) -> None:
    test_data = copy.deepcopy(data)
    
    if algorithm_name in ["selection_parallel", "selection_serial"]:
        algorithm_func(test_data)
    elif algorithm_name in ["merge_parallel", "merge_serial"]:
        algorithm_func(test_data, 0, len(test_data) - 1)
    elif algorithm_name == "quick_parallel":
        algorithm_func(test_data, max_workers=2)
    elif algorithm_name == "quick_serial":
        algorithm_func(test_data, 0, len(test_data) - 1)
    else:
        algorithm_func(test_data)


def benchmark_algorithm(algorithm_name: str, algorithm_func: Optional[Callable], data: List[int]) -> Dict[str, Any]:
    if algorithm_func is None:
        return {
            "error": f"Algorithm {algorithm_name} not available",
            "mean_time": float('inf'),
            "mean_time_ns": float('inf')
        }
    
    try:
        for _ in range(WARMUP_ITERATIONS):
            _invoke_algorithm(algorithm_name, algorithm_func, data)
        
        times = []
        for _ in range(BENCHMARK_ITERATIONS):
            start_time = time.perf_counter() * NS_PER_SEC
            _invoke_algorithm(algorithm_name, algorithm_func, data)
            end_time = time.perf_counter() * NS_PER_SEC
            times.append(end_time - start_time)
        
        mean_time_ns = statistics.mean(times)
        median_time_ns = statistics.median(times)
        std_time_ns = statistics.stdev(times) if len(times) > 1 else 0
        
        return {
            "mean_time": f"{mean_time_ns / MS_PER_NS:.6f} ms",
            "mean_time_ns": mean_time_ns,
            "median_time": f"{median_time_ns / MS_PER_NS:.6f} ms",
            "median_time_ns": median_time_ns,
            "std_time": f"{std_time_ns / MS_PER_NS:.6f} ms",
            "std_time_ns": std_time_ns,
            "min_time": f"{min(times) / MS_PER_NS:.6f} ms",
            "min_time_ns": min(times),
            "max_time": f"{max(times) / MS_PER_NS:.6f} ms",
            "max_time_ns": max(times),
            "iterations": BENCHMARK_ITERATIONS
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "mean_time": float('inf'),
            "mean_time_ns": float('inf')
        }

def _format_result(algorithm_name: str, result: Dict[str, Any]) -> str:
    if result.get("mean_time_ns") != float('inf'):
        return f"{algorithm_name}: {result['mean_time']}"
    error = result.get("error", "Unknown error")
    return f"{algorithm_name}: ERROR - {error}"


def _compare_results(name1: str, result1: Dict[str, Any],
                     name2: str, result2: Dict[str, Any]) -> None:
    time1 = result1.get("mean_time_ns", float('inf'))
    time2 = result2.get("mean_time_ns", float('inf'))
    
    print(f"  {_format_result(name1, result1)}")
    print(f"  {_format_result(name2, result2)}")
    
    if time1 != float('inf') and time2 != float('inf'):
        speedup = time2 / time1 if time1 > 0 else 0
        faster = f"({name1} faster)" if speedup > 1 else f"({name2} faster)"
        print(f"  Speedup: {speedup:.2f}x {faster}")


def main() -> None:
    print("Python Parallel Sorting Algorithm Benchmark (Fast Version)")
    print("=" * 60)
    
    # test_sizes = [10**7, 10**8]
    test_sizes = [10**5]
    
    sorting_algorithms = [
        ("insertion_parallel", parallel_insertion_sort, "insertion_serial", insertionSort),
        ("merge_parallel", parallel_merge_sort, "merge_serial", mergeSort),
        ("quick_parallel", quicksort_parallel, "quick_serial", quicksort),
        ("selection_parallel", parallel_selection_sort, "selection_serial", selection_sort)
    ]
    
    for size in test_sizes:
        print(f"\n--- Size: {size} ---")
        data = load_test_data(size)
        
        print("Benchmarking builtin_sort...")
        builtin_result = benchmark_algorithm("builtin_sort", sorted, data)
        
        for parallel_name, parallel_func, serial_name, serial_func in sorting_algorithms:
            print(f"Benchmarking {parallel_name}...")
            parallel_result = benchmark_algorithm(parallel_name, parallel_func, data)
            
            print(f"Benchmarking {serial_name}...")
            serial_result = benchmark_algorithm(serial_name, serial_func, data)
            
            print(f"\nComparing {parallel_name} vs {serial_name} vs builtin_sort:")
            _compare_results(parallel_name, parallel_result, serial_name, serial_result)
            
            builtin_time = builtin_result.get("mean_time_ns", float('inf'))
            parallel_time = parallel_result.get("mean_time_ns", float('inf'))
            serial_time = serial_result.get("mean_time_ns", float('inf'))
            
            if builtin_time != float('inf'):
                print(f"  {_format_result('builtin_sort', builtin_result)}")
                if parallel_time != float('inf'):
                    parallel_vs_builtin = builtin_time / parallel_time if parallel_time > 0 else 0
                    faster = f"({parallel_name} faster)" if parallel_vs_builtin < 1 else "(builtin_sort faster)"
                    print(f"  builtin_sort vs {parallel_name}: {parallel_vs_builtin:.2f}x {faster}")
                if serial_time != float('inf'):
                    serial_vs_builtin = builtin_time / serial_time if serial_time > 0 else 0
                    faster = f"({serial_name} faster)" if serial_vs_builtin < 1 else "(builtin_sort faster)"
                    print(f"  builtin_sort vs {serial_name}: {serial_vs_builtin:.2f}x {faster}")
            print()
    
    print("\nBenchmark completed!")

if __name__ == "__main__":
    main()
