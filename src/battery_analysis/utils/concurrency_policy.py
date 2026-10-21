"""Shared, non-sampling worker budget for NDAX conversion pools."""

import os
import sys


def conversion_worker_budget(
    task_count: int,
    cpu_count: int,
    max_workers: int | None = None,
    *,
    is_windows: bool = False,
) -> int:
    """Return a worker count, not a CPU-utilization limit; zero means no pool.

    Use 75% of available logical CPUs, reserving one CPU up to four CPUs and
    two otherwise (a single-CPU machine still needs one worker). A positive
    max_workers is only a requested upper bound. None and legacy 0 mean auto.
    Booleans/non-integers raise TypeError; negative limits raise ValueError.
    """
    if isinstance(task_count, bool) or not isinstance(task_count, int):
        raise TypeError("task_count must be an integer")
    if task_count < 0:
        raise ValueError("task_count must be non-negative")
    if isinstance(cpu_count, bool) or not isinstance(cpu_count, int):
        raise TypeError("cpu_count must be an integer")
    if cpu_count < 1:
        raise ValueError("cpu_count must be positive")
    if max_workers is not None:
        if isinstance(max_workers, bool) or not isinstance(max_workers, int):
            raise TypeError("max_workers must be an integer or None")
        if max_workers < 0:
            raise ValueError("max_workers must be non-negative")

    reserved = 1 if cpu_count <= 4 else 2
    budget = max(1, min(cpu_count * 3 // 4, cpu_count - reserved))
    workers = min(task_count, budget)
    if max_workers:
        workers = min(workers, max_workers)
    if is_windows:
        workers = min(workers, 61)  # ProcessPoolExecutor's Windows limit.
    return workers


def get_conversion_worker_count(task_count: int, max_workers: int | None = None) -> int:
    """Apply the shared budget using CPUs available to this process, then host CPUs."""
    process_cpu_count = getattr(os, "process_cpu_count", None)
    cpu_count = (process_cpu_count() if process_cpu_count else None) or os.cpu_count() or 1
    return conversion_worker_budget(
        task_count, cpu_count, max_workers, is_windows=sys.platform == "win32"
    )
