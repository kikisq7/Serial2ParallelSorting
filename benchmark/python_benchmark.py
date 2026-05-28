#!/usr/bin/env python3

import copy
import os
import statistics
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_ROOT)

try:
    from bubble.bubble_parallel import bubble_sort_parallel
except ImportError:
    bubble_sort_parallel = None

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

try:
    from bubble.bubble import bubble_sort
except ImportError:
    bubble_sort = None

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

BENCHMARK_ITERATIONS = 3
WARMUP_ITERATIONS = 1
NS_PER_SEC = 1_000_000_000
MS_PER_NS = 1_000_000


def parse_test_sizes() -> List[int]:
    raw = os.environ.get("BENCHMARK_SIZES", "").strip()
    if not raw:
        return [
            10**3,
            10**4,
            2 * 10**4,
            4 * 10**4,
            8 * 10**4,
            10**5,
            2 * 10**5,
            4 * 10**5,
            8 * 10**5,
            10**6,
        ]
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def load_test_data(size: int, iteration: Optional[int] = None) -> List[int]:
    if iteration is not None:
        data_path = os.path.join(REPO_ROOT, "test_data", f"data_{size}_{iteration + 1}.txt")
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                return [int(x) for x in f.read().split()]
    data_path = os.path.join(REPO_ROOT, "test_data", f"data_{size}.txt")
    with open(data_path, "r") as f:
        return [int(x) for x in f.read().split()]


def _invoke_algorithm(algorithm_name: str, algorithm_func: Callable, data: List[int]) -> None:
    if algorithm_name in ["bubble_parallel", "bubble_serial", "selection_parallel", "selection_serial"]:
        algorithm_func(data)
    elif algorithm_name in ["merge_parallel", "merge_serial"]:
        algorithm_func(data, 0, len(data) - 1)
    elif algorithm_name == "quick_parallel":
        out = algorithm_func(data, max_workers=2)
        if list(out) != sorted(data):
            raise ValueError("quick_parallel produced wrong order")
    elif algorithm_name == "quick_serial":
        algorithm_func(data, 0, len(data) - 1)
    elif algorithm_name == "builtin_sort":
        _ = sorted(data)
    else:
        algorithm_func(data)


def _verify_sorted(algorithm_name: str, algorithm_func: Callable, data: List[int]) -> None:
    exp = sorted(data)
    if algorithm_name == "quick_parallel":
        out = algorithm_func(list(data), max_workers=2)
        if list(out) != exp:
            raise ValueError(f"{algorithm_name} correctness failed")
        return
    d = copy.deepcopy(data)
    _invoke_algorithm(algorithm_name, algorithm_func, d)
    if algorithm_name == "builtin_sort":
        return
    if d != exp:
        raise ValueError(f"{algorithm_name} correctness failed")


def time_one_ns(algorithm_name: str, algorithm_func: Callable, data: List[int]) -> float:
    d = copy.deepcopy(data)
    t0 = time.perf_counter() * NS_PER_SEC
    if algorithm_name == "quick_parallel":
        _ = algorithm_func(d, max_workers=2)
    else:
        _invoke_algorithm(algorithm_name, algorithm_func, d)
    t1 = time.perf_counter() * NS_PER_SEC
    return t1 - t0


def _stats_from_times(name: str, times: List[float]) -> Dict[str, Any]:
    mean_time_ns = statistics.mean(times)
    median_time_ns = statistics.median(times)
    std_time_ns = statistics.stdev(times) if len(times) > 1 else 0.0
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
        "iterations": len(times),
        "name": name,
    }


def paired_parallel_serial_benchmark(
    parallel_name: str,
    parallel_func: Optional[Callable],
    serial_name: str,
    serial_func: Optional[Callable],
    size: int,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if parallel_func is None:
        e = {"error": f"{parallel_name} not available", "mean_time_ns": float("inf")}
        return e, dict(e)
    if serial_func is None:
        e = {"error": f"{serial_name} not available", "mean_time_ns": float("inf")}
        return dict(e), e

    times_p: List[float] = []
    times_s: List[float] = []
    for iteration in range(BENCHMARK_ITERATIONS):
        data = load_test_data(size, iteration)
        _verify_sorted(parallel_name, parallel_func, data)
        _verify_sorted(serial_name, serial_func, data)
        for _ in range(WARMUP_ITERATIONS):
            time_one_ns(parallel_name, parallel_func, data)
            time_one_ns(serial_name, serial_func, data)
        times_p.append(time_one_ns(parallel_name, parallel_func, data))
        times_s.append(time_one_ns(serial_name, serial_func, data))

    return _stats_from_times(parallel_name, times_p), _stats_from_times(serial_name, times_s)


def benchmark_builtin_sorted(size: int) -> Dict[str, Any]:
    times: List[float] = []
    for iteration in range(BENCHMARK_ITERATIONS):
        data = load_test_data(size, iteration)
        for _ in range(WARMUP_ITERATIONS):
            _ = sorted(data)
        t0 = time.perf_counter() * NS_PER_SEC
        _ = sorted(data)
        t1 = time.perf_counter() * NS_PER_SEC
        times.append(t1 - t0)
    return _stats_from_times("builtin_sort", times)


def _format_result(algorithm_name: str, result: Dict[str, Any]) -> str:
    err = result.get("error")
    if err:
        return f"{algorithm_name}: ERROR - {err}"
    if result.get("mean_time_ns") not in (float("inf"), None):
        return f"{algorithm_name}: {result['mean_time']}"
    return f"{algorithm_name}: ERROR - Unknown error"


def _compare_results(name1: str, result1: Dict[str, Any], name2: str, result2: Dict[str, Any]) -> None:
    print(f"  {_format_result(name1, result1)}")
    print(f"  {_format_result(name2, result2)}")
    t1 = result1.get("mean_time_ns", float("inf"))
    t2 = result2.get("mean_time_ns", float("inf"))
    if t1 != float("inf") and t2 != float("inf") and t1 > 0:
        speedup = t2 / t1
        faster = f"({name1} faster)" if speedup > 1 else f"({name2} faster)"
        print(f"  Speedup: {speedup:.2f}x {faster}")


def main() -> None:
    test_sizes = parse_test_sizes()
    print("Python Parallel Sorting Algorithm Benchmark")
    print(f"BENCHMARK_SIZES={','.join(str(s) for s in test_sizes)}")
    print("=" * 60)

    sorting_algorithms = [
        ("bubble_parallel", bubble_sort_parallel, "bubble_serial", bubble_sort),
        ("insertion_parallel", parallel_insertion_sort, "insertion_serial", insertionSort),
        ("merge_parallel", parallel_merge_sort, "merge_serial", mergeSort),
        ("quick_parallel", quicksort_parallel, "quick_serial", quicksort),
        ("selection_parallel", parallel_selection_sort, "selection_serial", selection_sort),
    ]

    for size in test_sizes:
        print(f"\n--- Size: {size} ---")

        try:
            builtin_result = benchmark_builtin_sorted(size)
        except Exception as e:
            builtin_result = {"error": str(e), "mean_time_ns": float("inf")}

        for parallel_name, parallel_func, serial_name, serial_func in sorting_algorithms:
            print(f"Benchmarking {parallel_name} vs {serial_name} (paired datasets)...")
            try:
                parallel_result, serial_result = paired_parallel_serial_benchmark(
                    parallel_name, parallel_func, serial_name, serial_func, size
                )
            except Exception as e:
                parallel_result = {"error": str(e), "mean_time_ns": float("inf")}
                serial_result = {"error": str(e), "mean_time_ns": float("inf")}

            print(f"\nComparing {parallel_name} vs {serial_name} vs builtin_sort:")
            _compare_results(parallel_name, parallel_result, serial_name, serial_result)

            builtin_time = builtin_result.get("mean_time_ns", float("inf"))
            parallel_time = parallel_result.get("mean_time_ns", float("inf"))
            serial_time = serial_result.get("mean_time_ns", float("inf"))

            if builtin_time != float("inf"):
                print(f"  {_format_result('builtin_sort', builtin_result)}")
                if parallel_time != float("inf") and parallel_time > 0:
                    parallel_vs_builtin = builtin_time / parallel_time
                    faster = f"({parallel_name} faster)" if parallel_vs_builtin < 1 else "(builtin_sort faster)"
                    print(f"  builtin_sort vs {parallel_name}: {parallel_vs_builtin:.2f}x {faster}")
                if serial_time != float("inf") and serial_time > 0:
                    serial_vs_builtin = builtin_time / serial_time
                    faster = f"({serial_name} faster)" if serial_vs_builtin < 1 else "(builtin_sort faster)"
                    print(f"  builtin_sort vs {serial_name}: {serial_vs_builtin:.2f}x {faster}")
            print()

    print("\nBenchmark completed!")


if __name__ == "__main__":
    main()
