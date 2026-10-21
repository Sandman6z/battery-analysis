"""Pure worker-budget boundaries and non-sampling CPU discovery."""

from unittest.mock import Mock

import pytest

from battery_analysis.utils import concurrency_policy as policy


@pytest.mark.parametrize(("cpus", "budget"), [(1, 1), (2, 1), (4, 3), (8, 6), (16, 12), (128, 96)])
def test_conversion_worker_budget_cpu_reservation(cpus, budget):
    assert policy.conversion_worker_budget(200, cpus) == budget


@pytest.mark.parametrize("cpus", [1, 2, 4, 8, 16, 128])
@pytest.mark.parametrize("tasks", [0, 1, 2, 200])
def test_conversion_worker_budget_task_clipping(cpus, tasks):
    budget = policy.conversion_worker_budget(200, cpus)
    assert policy.conversion_worker_budget(tasks, cpus) == min(tasks, budget)


@pytest.mark.parametrize(("is_windows", "expected"), [(True, 61), (False, 96)])
def test_conversion_worker_budget_windows_limit(is_windows, expected):
    assert policy.conversion_worker_budget(200, 128, is_windows=is_windows) == expected
    assert policy.conversion_worker_budget(2, 128, is_windows=is_windows) == 2


@pytest.mark.parametrize(("requested", "expected"), [(None, 6), (0, 6), (1, 1), (4, 4), (99, 6)])
def test_conversion_worker_budget_explicit_upper_bound(requested, expected):
    assert policy.conversion_worker_budget(100, 8, requested) == expected
    assert policy.conversion_worker_budget(1, 8, requested) == 1
    assert policy.conversion_worker_budget(100, 128, 999, is_windows=True) == 61


@pytest.mark.parametrize("tasks", [0, 10])
@pytest.mark.parametrize(
    ("requested", "error"),
    [(-1, ValueError), (True, TypeError), (False, TypeError), (1.5, TypeError), ("2", TypeError)],
)
def test_conversion_worker_budget_invalid_limits_even_without_tasks(tasks, requested, error):
    with pytest.raises(error, match="max_workers"):
        policy.conversion_worker_budget(tasks, 8, requested)


@pytest.mark.parametrize(
    ("tasks", "cpus", "error"),
    [
        (-1, 8, ValueError),
        (True, 8, TypeError),
        (1.0, 8, TypeError),
        (1, 0, ValueError),
        (1, -1, ValueError),
        (1, True, TypeError),
        (1, 8.0, TypeError),
    ],
)
def test_conversion_worker_budget_invalid_counts(tasks, cpus, error):
    with pytest.raises(error):
        policy.conversion_worker_budget(tasks, cpus)


def test_get_conversion_worker_count_prefers_process_cpus(monkeypatch):
    process_count, host_count = Mock(return_value=4), Mock(return_value=128)
    monkeypatch.setattr(policy.os, "process_cpu_count", process_count, raising=False)
    monkeypatch.setattr(policy.os, "cpu_count", host_count)
    assert policy.get_conversion_worker_count(200) == 3
    process_count.assert_called_once_with()
    host_count.assert_not_called()


@pytest.mark.parametrize(
    ("process_cpus", "host_cpus", "expected"),
    [
        (None, 8, 6),
        (None, None, 1),
        (0, 0, 1),
    ],
)
def test_get_conversion_worker_count_cpu_fallbacks(monkeypatch, process_cpus, host_cpus, expected):
    monkeypatch.setattr(policy.os, "process_cpu_count", lambda: process_cpus, raising=False)
    monkeypatch.setattr(policy.os, "cpu_count", lambda: host_cpus)
    assert policy.get_conversion_worker_count(100) == expected


def test_get_conversion_worker_count_missing_process_api(monkeypatch):
    monkeypatch.delattr(policy.os, "process_cpu_count", raising=False)
    monkeypatch.setattr(policy.os, "cpu_count", lambda: 2)
    assert policy.get_conversion_worker_count(100) == 1


def test_get_conversion_worker_count_windows(monkeypatch):
    monkeypatch.setattr(policy.os, "process_cpu_count", lambda: 128, raising=False)
    monkeypatch.setattr(policy.sys, "platform", "win32")
    assert policy.get_conversion_worker_count(200, 1000) == 61
