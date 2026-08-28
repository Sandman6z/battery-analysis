"""TaskRunner 单元测试——执行/错误/进度/协作式取消"""

from unittest.mock import Mock, patch

from PyQt6.QtTest import QSignalSpy

from battery_analysis.main.workers.task_runner import TaskManager, TaskRunner


def test_success_emits_finished_with_result():
    runner = TaskRunner(lambda progress_callback=None, **kwargs: 42)
    spy = QSignalSpy(runner.signals.finished)
    spy_error = QSignalSpy(runner.signals.error)
    runner.run()
    assert len(spy_error) == 0
    assert len(spy) == 1
    assert spy[0][0] == 42


def test_error_emits_error_with_message():
    def boom(progress_callback=None, **kwargs):
        raise ValueError("kaboom")

    runner = TaskRunner(boom)
    spy = QSignalSpy(runner.signals.error)
    runner.run()
    assert len(spy) == 1
    assert "kaboom" in spy[0][0]


def test_progress_callback_forwards_to_progress_signal():
    received = []

    def task(progress_callback=None, **kwargs):
        progress_callback(50, "halfway")
        return "done"

    # 用户传入的 progress_callback 与 progress 信号应走同一链路（都收到回调）
    runner = TaskRunner(task, progress_callback=lambda pct, msg: received.append((pct, msg)))
    spy = QSignalSpy(runner.signals.progress)
    runner.run()
    assert len(spy) == 1
    assert spy[0][0] == 50
    assert spy[0][1] == "halfway"
    assert received == [(50, "halfway")]


def test_cancelled_before_run_emits_cancelled():
    runner = TaskRunner(lambda progress_callback=None, **kwargs: "never runs")
    spy = QSignalSpy(runner.signals.cancelled)
    runner.cancel()
    runner.run()
    assert len(spy) == 1  # cancel() 是 cancelled 的唯一发射者


def test_cancel_mid_execution_raises_at_next_progress_point():
    calls = []

    def task(progress_callback=None, **kwargs):
        progress_callback(10, "start")
        calls.append("after first progress")
        progress_callback(20, "second")
        calls.append("after second progress")
        return "done"

    runner = TaskRunner(task)
    spy_cancelled = QSignalSpy(runner.signals.cancelled)
    spy_finished = QSignalSpy(runner.signals.finished)

    # 任务刚启动后（run() 入口检查之后）、第一次 progress_callback 前收到取消请求：
    # 取消点在第一次 progress_callback 处拦截（TaskCancelled），任务体不继续执行。
    runner.signals.started.connect(lambda: runner.cancel())
    runner.run()
    assert len(spy_cancelled) == 1
    assert len(spy_finished) == 0
    assert calls == []


def test_cancel_after_last_progress_suppresses_finished():
    def task(progress_callback=None, **kwargs):
        progress_callback(100, "done")  # 最后一次 progress
        runner.cancel()  # 之后取消（finished 应被抑制）
        return "result"

    runner = TaskRunner(task)
    spy = QSignalSpy(runner.signals.finished)
    spy_cancelled = QSignalSpy(runner.signals.cancelled)
    runner.run()
    assert len(spy) == 0  # finished 被抑制
    assert len(spy_cancelled) == 1


def test_no_progress_task_completes_but_finished_suppressed():
    calls = []
    runner = TaskRunner(lambda progress_callback=None, **kwargs: calls.append("ran") or "result")
    spy = QSignalSpy(runner.signals.finished)
    runner.signals.started.connect(lambda: runner.cancel())
    runner.run()
    assert calls == ["ran"]  # task 无取消点，仍跑完
    assert len(spy) == 0  # finished 被抑制


def test_cancelled_runner_removed_from_active():
    """cancel() 后 runner 从 _active 移除（cancelled → _on_done 连接）"""
    mock_pool = Mock()
    with patch(
        "battery_analysis.main.workers.task_runner.QC.QThreadPool.globalInstance",
        return_value=mock_pool,
    ):
        mgr = TaskManager()
        runner = TaskRunner(lambda progress_callback=None, **kwargs: None)
        mgr.submit(runner)
    assert mgr.active_count == 1
    runner.cancel()
    assert mgr.active_count == 0
