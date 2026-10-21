"""Both NDAX pool entry points must use the same bounded worker count (no processes)."""

from concurrent.futures import Future
from unittest.mock import Mock

import pytest

from battery_analysis.ndax import converter, worker
from battery_analysis.utils import concurrency_policy as policy


@pytest.fixture
def mock_pools(monkeypatch):
    def submit(_convert, _source, output):
        future = Future()
        future.set_result(str(output))
        return future

    pools = []
    for module in (converter, worker):
        executor = Mock()
        executor.__enter__ = Mock(return_value=executor)
        executor.__exit__ = Mock(return_value=False)
        executor.submit.side_effect = submit
        factory = Mock(return_value=executor)
        monkeypatch.setattr(module, "ProcessPoolExecutor", factory)
        pools.append(factory)
    return pools


def run_both_entries(tmp_path, task_count, requested):
    source = tmp_path / "1_ndax"
    source.mkdir()
    paths = [source / f"sample_{index}.ndax" for index in range(task_count)]
    for path in paths:
        path.touch()
    api_result = converter.convert_batch(source, max_workers=requested)
    gui_results = []
    conversion = worker.ConvertWorker(paths, tmp_path / "2_xlsx", max_workers=requested)
    conversion.finished_signal.connect(gui_results.append)
    conversion.run()
    assert len(gui_results) == 1
    for key in ("success", "skipped", "failed"):
        # as_completed deliberately does not promise result ordering.
        assert sorted(gui_results[0][key]) == sorted(api_result[key])
    assert len(api_result["success"]) == task_count
    assert not api_result["failed"]
    return api_result


@pytest.mark.parametrize(("cpus", "budget"), [(1, 1), (2, 1), (4, 3), (8, 6), (16, 12), (128, 96)])
@pytest.mark.parametrize("requested", [None, 0, 1, 4, 1000])
def test_both_conversion_entries_share_safe_budget(
    tmp_path, monkeypatch, mock_pools, cpus, budget, requested
):
    monkeypatch.setattr(policy.os, "process_cpu_count", lambda: cpus, raising=False)
    monkeypatch.setattr(policy.sys, "platform", "linux")
    run_both_entries(tmp_path, 100, requested)
    expected = min(budget, requested) if requested else budget
    for pool in mock_pools:
        pool.assert_called_once_with(max_workers=expected)
        assert pool.return_value.submit.call_count == 100


@pytest.mark.parametrize("task_count", [0, 1, 2, 100])
@pytest.mark.parametrize(("platform", "budget"), [("win32", 61), ("linux", 96)])
def test_both_conversion_entries_clip_pending_and_windows(
    tmp_path, monkeypatch, mock_pools, task_count, platform, budget
):
    monkeypatch.setattr(policy.os, "process_cpu_count", lambda: 128, raising=False)
    monkeypatch.setattr(policy.sys, "platform", platform)
    run_both_entries(tmp_path, task_count, None)
    for pool in mock_pools:
        if task_count:
            pool.assert_called_once_with(max_workers=min(task_count, budget))
        else:
            pool.assert_not_called()


@pytest.mark.parametrize("force", [False, True])
def test_conversion_entries_use_only_pending_files(tmp_path, monkeypatch, mock_pools, force):
    monkeypatch.setattr(policy.os, "process_cpu_count", lambda: 128, raising=False)
    source, output = tmp_path / "1_ndax", tmp_path / "2_xlsx"
    source.mkdir()
    output.mkdir()
    path = source / "existing.ndax"
    path.touch()
    (output / "existing.xlsx").touch()
    assert converter.convert_batch(source) == {
        "success": [],
        "skipped": ["existing.ndax"],
        "failed": [],
    }
    results = []
    conversion = worker.ConvertWorker([path], output, force)
    conversion.finished_signal.connect(results.append)
    conversion.run()
    mock_pools[0].assert_not_called()
    if force:
        mock_pools[1].assert_called_once_with(max_workers=1)
        assert results[0]["success"] == ["existing.ndax"]
    else:
        mock_pools[1].assert_not_called()
        assert results[0]["skipped"] == ["existing.ndax"]


@pytest.mark.parametrize("has_files", [False, True])
@pytest.mark.parametrize(
    ("requested", "error"),
    [(-1, ValueError), (True, TypeError), (False, TypeError), (2.0, TypeError), ("2", TypeError)],
)
def test_conversion_entries_reject_invalid_limits_before_pool(
    tmp_path, mock_pools, has_files, requested, error
):
    path = tmp_path / "sample.ndax"
    if has_files:
        path.touch()
    with pytest.raises(error, match="max_workers"):
        converter.convert_batch(tmp_path, max_workers=requested)
    with pytest.raises(error, match="max_workers"):
        worker.ConvertWorker([path] if has_files else [], tmp_path, max_workers=requested)
    for pool in mock_pools:
        pool.assert_not_called()
