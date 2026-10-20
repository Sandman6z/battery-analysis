from battery_analysis.main.controllers.main_controller import MainController


class TestMainController:
    def setup_method(self):
        self.controller = MainController()

    def test_set_project_context(self):
        self.controller.set_project_context(
            project_path="/test/project", input_path="/test/input", output_path="/test/output"
        )
        assert self.controller.project_path == "/test/project"
        assert self.controller.input_path == "/test/input"
        assert self.controller.output_path == "/test/output"

    def test_set_test_info(self):
        test_info = [{"name": "test1"}, {"name": "test2"}]
        self.controller.set_test_info(test_info)
        assert self.controller.test_info == test_info

    def test_start_analysis_missing_params(self):
        result = self.controller.start_analysis()
        assert result is False
        assert self.controller.is_analysis_running is False

    def test_cancel_analysis_not_running(self):
        result = self.controller.cancel_analysis()
        assert result is False

    def test_is_running_initially(self):
        assert self.controller.is_running() is False

    def test_anomaly_confirmation_defaults_stop_then_abort(self, monkeypatch):
        """两次确认：第一次默认停止；第二次默认中止；中途取消同样停止。"""
        from unittest.mock import MagicMock

        from PyQt6.QtWidgets import QMessageBox

        from battery_analysis.main.controllers import main_controller as module

        class Worker:
            b_cancel_requested = False
            def __init__(self):
                self.result = None
            def confirm_anomalies(self, allowed):
                self.result = allowed

        worker = Worker()
        self.controller.current_worker = worker
        question = MagicMock()
        monkeypatch.setattr(
            module,
            "QW",
            MagicMock(QMessageBox=MagicMock(question=question, StandardButton=QMessageBox.StandardButton)),
        )

        # 路径 1：第一次确认即停止
        question.return_value = QMessageBox.StandardButton.Yes
        self.controller._on_anomalies_request([{"file": "a.ndax", "type": "file_error", "reason": "x"}])
        assert worker.result is False
        assert question.call_count == 1

        # 路径 2：第一次不停止、第二次确认继续 → 放行
        question.reset_mock()
        question.side_effect = [QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes]
        self.controller._on_anomalies_request([{"file": "a.ndax", "type": "file_error", "reason": "x"}])
        assert worker.result is True
        assert question.call_count == 2

        # 路径 3：第一次继续、第二次中止 → 停止
        question.reset_mock()
        question.side_effect = [QMessageBox.StandardButton.No, QMessageBox.StandardButton.No]
        self.controller._on_anomalies_request([{"file": "a.ndax", "type": "missing_pulse", "current": 6}])
        assert worker.result is False

        # 路径 4：worker 已取消 → 直接停止，不弹框
        question.reset_mock()
        question.side_effect = None
        worker.b_cancel_requested = True
        self.controller._on_anomalies_request([{"file": "a.ndax", "type": "file_error", "reason": "x"}])
        assert worker.result is False
        question.assert_not_called()
