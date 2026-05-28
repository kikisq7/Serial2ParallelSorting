import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Optional

_MAX_WORKERS = max(2, int(os.environ.get("SORTING_PY_MAX_WORKERS", "8")))
_EXECUTOR_LOCK = threading.Lock()
_EXECUTORS: dict[int, ThreadPoolExecutor] = {}


def get_thread_count(task_count: int, max_workers: Optional[int] = None) -> int:
    if task_count <= 0:
        return 0
    hardware_workers = os.cpu_count() or 1
    requested_workers = 2 if task_count > 1 else 1
    out = max(1, min(max(hardware_workers, requested_workers), _MAX_WORKERS, task_count))
    if max_workers is not None:
        out = max(1, min(out, max(1, int(max_workers))))
    return out


def parallel_ranges(task_count: int, max_workers: Optional[int] = None) -> List[range]:
    workers = get_thread_count(task_count, max_workers)
    if workers == 0:
        return []
    base, extra = divmod(task_count, workers)
    ranges: List[range] = []
    start = 0
    for worker in range(workers):
        length = base + (1 if worker < extra else 0)
        stop = start + length
        ranges.append(range(start, stop))
        start = stop
    return ranges


def _get_executor(worker_count: int) -> ThreadPoolExecutor:
    with _EXECUTOR_LOCK:
        executor = _EXECUTORS.get(worker_count)
        if executor is None:
            executor = ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="sorting")
            _EXECUTORS[worker_count] = executor
        return executor


def run_in_threads(
    task_count: int,
    worker: Callable[[range], None],
    max_workers: Optional[int] = None,
) -> None:
    ranges = parallel_ranges(task_count, max_workers)
    if len(ranges) <= 1:
        if ranges:
            worker(ranges[0])
        return

    executor = _get_executor(len(ranges))
    list(executor.map(worker, ranges))


def run_in_threads_indexed(task_count: int, worker: Callable[[int, range], None]) -> None:
    ranges = parallel_ranges(task_count)
    if len(ranges) <= 1:
        if ranges:
            worker(0, ranges[0])
        return

    executor = _get_executor(len(ranges))
    list(executor.map(lambda p: worker(p[0], p[1]), enumerate(ranges)))
