import pytest
from PyQt6.QtTest import QSignalSpy

from battery_analysis.main.workers.analysis_worker import AnalysisWorker
from battery_analysis.main.workers.task_runner import TaskCancelled


class TestAnalysisWorker:
    def setup_method(self):
        self.worker = AnalysisWorker()

    def test_set_info(self):
        self.worker.set_info("path", "input", "output", ["info"])
        assert self.worker.str_path == "path"

    def test_request_cancel(self):
        self.worker.request_cancel()
        assert self.worker.b_cancel_requested is True

    def test_signals_are_task_signals(self):
        # 信号集合为扩展后的 TaskSignals（含 info/thread_end/rename_path/start_visualizer）
        assert self.worker.signals.info
        assert self.worker.signals.thread_end
        assert self.worker.signals.rename_path
        assert self.worker.signals.start_visualizer
        assert self.worker.signals.progress  # progress_update 语义由 progress 承担

    def test_request_cancel_sets_cancelled_and_emits(self):
        worker = AnalysisWorker()
        spy = QSignalSpy(worker.signals.cancelled)
        worker.request_cancel()
        assert worker.b_cancel_requested is True
        assert worker._cancelled is True
        assert len(spy) == 1  # cancelled 信号在请求时立即发射

    def test_emit_progress_raises_task_cancelled_when_cancelled(self):
        worker = AnalysisWorker()
        worker._cancelled = True  # b_cancel_requested 保持 False
        with pytest.raises(TaskCancelled):
            worker._emit_progress(50, "x")

    def test_cancelled_before_run_reports_cancelled(self):
        """queued-cancel 回归：排队期间被取消，调度后应报 cancelled 而非 success"""
        worker = AnalysisWorker()
        worker.set_info("path", "input", "output", ["info"])
        spy_info = QSignalSpy(worker.signals.info)
        spy_thread_end = QSignalSpy(worker.signals.thread_end)
        worker.request_cancel()
        worker.run()
        assert len(spy_info) > 0
        assert spy_info[-1] == [False, 0, "status:cancelled"]
        assert len(spy_thread_end) == 0  # 取消不发 thread_end
