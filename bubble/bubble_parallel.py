"""Parallel odd–even transposition bubble sort.

On POSIX (fork), multiprocessing escapes the GIL so independent pair-swaps within
a phase can run in parallel. On Windows only the threaded fallback is used."""

from __future__ import annotations

import multiprocessing as mp
import os
import sys
from typing import List

from parallel_utils import run_in_threads


_MP_BUF = None


def _mp_bubble_init(shared) -> None:
    global _MP_BUF
    _MP_BUF = shared


def _mp_bubble_chunk(pair_lo: int, pair_hi: int, phase: int) -> bool:
    buf = _MP_BUF
    start = phase % 2
    swapped_local = False
    for pair_idx in range(pair_lo, pair_hi):
        j = start + 2 * pair_idx
        if buf[j] > buf[j + 1]:
            buf[j], buf[j + 1] = buf[j + 1], buf[j]
            swapped_local = True
    return swapped_local


def _split_pair_chunks(pair_count: int, workers: int) -> List[tuple[int, int]]:
    if workers <= 0:
        workers = 1
    if workers > pair_count:
        workers = max(1, pair_count)

    chunks: List[tuple[int, int]] = []
    base, extra = divmod(pair_count, workers)
    start = 0
    for w in range(workers):
        length = base + (1 if w < extra else 0)
        if length == 0:
            continue
        stop = start + length
        chunks.append((start, stop))
        start = stop
    return chunks


def _bubble_threaded_odd_even(arr, n):
    """Threaded fallback; good when GIL dominates (often slower than serial on CPythons)."""
    import threading

    no_swap_prev = False
    for phase in range(n):
        start = phase % 2
        pair_count = (n - start) // 2
        if pair_count <= 0:
            any_swap = False
        else:
            swapped = threading.Event()

            def worker(task_range):
                for pair_idx in task_range:
                    j = start + 2 * pair_idx
                    if arr[j] > arr[j + 1]:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
                        swapped.set()

            run_in_threads(pair_count, worker)
            any_swap = swapped.is_set()

        if not any_swap:
            if no_swap_prev:
                break
            no_swap_prev = True
        else:
            no_swap_prev = False


def bubble_sort_parallel(arr):
    """In-place odd-even bubble sort."""
    n = len(arr)
    if n <= 1:
        return arr

    use_mp = sys.platform != "win32" and os.environ.get("SORTING_PY_BUBBLE_MP", "1") != "0"

    if use_mp:
        cpus = mp.cpu_count() or 4
        try:
            mw = max(1, min(cpus, int(os.environ.get("SORTING_PY_MAX_WORKERS", "8"))))
        except ValueError:
            mw = min(cpus, 8)

        ctx = mp.get_context("fork")
        shared = ctx.Array("i", arr, lock=False)
        _mp_bubble_init(shared)

        worker_count = max(1, min(mw, cpus))

        with ctx.Pool(
            processes=worker_count,
            initializer=_mp_bubble_init,
            initargs=(shared,),
            maxtasksperchild=None,
        ) as pool:
            no_swap_prev = False
            for phase in range(n):
                start = phase % 2
                pair_count = (n - start) // 2
                if pair_count <= 0:
                    any_swap = False
                else:
                    chunk_workers = min(worker_count, pair_count)
                    chunks = _split_pair_chunks(pair_count, chunk_workers)
                    tasks = [(lo, hi, phase) for lo, hi in chunks]
                    if not tasks:
                        any_swap = False
                    elif len(tasks) == 1:
                        lo, hi = tasks[0][0], tasks[0][1]
                        any_swap = _mp_bubble_chunk(lo, hi, phase)
                    else:
                        any_swap = any(pool.starmap(_mp_bubble_chunk, tasks))

                if not any_swap:
                    if no_swap_prev:
                        break
                    no_swap_prev = True
                else:
                    no_swap_prev = False

        arr[:] = list(shared)
        return arr

    _bubble_threaded_odd_even(arr, n)
    return arr
