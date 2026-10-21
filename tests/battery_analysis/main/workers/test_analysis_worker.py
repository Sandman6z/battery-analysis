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

    def test_existing_version_directory_is_never_deleted(self, tmp_path):
        output = tmp_path / "reports"
        output.mkdir()
        old = output / "v1.0"
        old.mkdir()
        (old / "keep.txt").write_bytes(b"original")
        worker = AnalysisWorker()
        worker.set_info("project", "input", str(output), [None] * 16 + ["1.0"])
        success = QSignalSpy(worker.signals.analysis_succeeded)
        worker.run()
        assert (old / "keep.txt").read_bytes() == b"original"
        assert not success
        assert worker.str_error_xlsx

    def test_failed_writer_removes_only_this_run(self, tmp_path, monkeypatch):
        from battery_analysis.utils import file_writer
        from battery_analysis.utils.processors import battery_analysis

        output = tmp_path / "reports"
        output.mkdir()
        previous = output / "previous"
        previous.mkdir()
        (previous / "keep.txt").write_text("safe")

        class Engine:
            def __init__(self, **kwargs):
                pass

            def UBA_GetErrorLog(self):
                return ""

            def UBA_GetBatteryInfo(self):
                return [[[]], ["battery"], ["2024-10-19 23:55:00", ""], "", ""]

        class FailedWriter:
            def __init__(self, *, result_dir, **kwargs):
                (output / "Example__DCbatch_TD20241019_v1.0.docx").write_bytes(b"partial")
                (tmp_path / "reports" / "20241019_v1.0" / "partial.csv").write_text("partial")

            def UFW_GetErrorLog(self):
                return "writer failed"

        monkeypatch.setattr(battery_analysis, "BatteryAnalysis", Engine)
        monkeypatch.setattr(file_writer, "FileWriter", FailedWriter)
        info = [""] * 19
        info[4], info[2], info[5], info[16] = "Example", "", "batch", "1.0"
        worker = AnalysisWorker()
        worker.set_info("project", "input", str(output), info)
        success = QSignalSpy(worker.signals.analysis_succeeded)
        visualizer = QSignalSpy(worker.signals.start_visualizer)
        worker.run()
        assert not success
        assert not visualizer
        assert not (output / "20241019_v1.0").exists()
        assert not (output / "Example__DCbatch_TD20241019_v1.0.docx").exists()
        assert (previous / "keep.txt").read_text() == "safe"

    @pytest.mark.parametrize("cancel_at_completion", [False, True])
    def test_success_signal_only_after_all_artifacts(self, tmp_path, monkeypatch, cancel_at_completion):
        from battery_analysis.utils import file_writer
        from battery_analysis.utils.processors import battery_analysis

        class Engine:
            def __init__(self, **kwargs):
                pass

            def UBA_GetErrorLog(self):
                return ""

            def UBA_GetBatteryInfo(self):
                return [[[]], ["good"], ["2024-10-19 23:55:00", "2024-10-19 23:56:00"], "", ""]

        Engine.warning_summary = "Non-judgment cutoff data unavailable: 2 slots across 1 file."

        class Writer:
            def __init__(self, *, result_dir, **kwargs):
                from pathlib import Path

                p = Path(result_dir)
                for name in ("Result.xlsx", "Sample.xlsx", "Result.csv", "Result.json",
                             "Info_Image.csv", "Info_Plot.json"):
                    (p / name).write_text("report")
                for prefix in ("Image_FilteredLoadVoltageOverCharge",
                               "Image_UnfilteredLoadVoltageOverCharge"):
                    for ext in (".png", ".svg"):
                        (p / (prefix + ext)).write_bytes(b"image")
                (p.parent / "Example__DCbatch_TD20241019_v1.0.docx").write_bytes(b"word")

            def UFW_GetErrorLog(self):
                return ""

        monkeypatch.setattr(battery_analysis, "BatteryAnalysis", Engine)
        monkeypatch.setattr(file_writer, "FileWriter", Writer)
        output = tmp_path / "reports"
        output.mkdir()
        info = [""] * 19
        info[4], info[2], info[5], info[16] = "Example", "", "batch", "1.0"
        worker = AnalysisWorker()
        worker.set_info("project", "input", str(output), info)
        success = QSignalSpy(worker.signals.analysis_succeeded)
        statuses = QSignalSpy(worker.signals.info)
        renamed = QSignalSpy(worker.signals.rename_path)
        visualizer = QSignalSpy(worker.signals.start_visualizer)
        observed = []
        worker.signals.start_visualizer.connect(
            lambda: observed.append((worker.delivered_result_dir, (output / "20241019_v1.0" / "Info_Image.csv").is_file(), len(success)))
        )
        if cancel_at_completion:
            worker.signals.progress.connect(lambda value, status: worker.request_cancel() if value == 100 and not worker.b_cancel_requested else None)
        worker.run()
        if cancel_at_completion:
            assert not success
            assert not visualizer
            assert not (output / "20241019_v1.0").exists()
            return
        assert len(success) == 1
        assert len(visualizer) == 1
        assert observed == [(str(output) + "/20241019_v1.0", True, 1)]
        assert statuses[-1][2] == "status:success\n" + Engine.warning_summary
        assert renamed[0] == ["20241019"]
        assert (output / "20241019_v1.0" / "Result.xlsx").exists()

    def test_cancelled_before_run_reports_cancelled(self):
        """queued-cancel 回归：排队期间被取消，调度后应报 cancelled 而非 success"""
        worker = AnalysisWorker()
        worker.set_info("path", "input", "output", ["info"])
        spy_info = QSignalSpy(worker.signals.info)
        spy_thread_end = QSignalSpy(worker.signals.thread_end)
        visualizer = QSignalSpy(worker.signals.start_visualizer)
        worker.request_cancel()
        worker.run()
        assert len(spy_info) > 0
        assert spy_info[-1] == [False, 0, "status:cancelled"]
        assert len(spy_thread_end) == 1  # 取消也发 thread_end，确保 is_analysis_running 重置
        assert not visualizer


def test_set_info_freezes_nested_test_info():
    from battery_analysis.domain.entities.test_info import TestInfo

    info = TestInfo(battery_type="Coin Cell", current_levels=[3, 6], voltage_levels=[2.5])
    worker = AnalysisWorker()
    worker.set_info("project", "input", "output", info)
    info.battery_type = "Pouch Cell"
    info.current_levels.append(9)
    assert worker.list_test_info.battery_type == "Coin Cell"
    assert worker.list_test_info.current_levels == [3, 6]
