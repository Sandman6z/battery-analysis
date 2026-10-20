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
        from unittest.mock import Mock

        class Worker:
            b_cancel_requested = False
            def __init__(self):
                self.result = None
            def confirm_anomalies(self, allowed):
                self.result = allowed

        worker = Worker()
        self.controller.current_worker = worker
        question = Mock()
        monkeypatch.setattr(self.controller, "_show_anomaly_dialog", question)

        # 路径 1：第一次确认即停止
        question.return_value = False
        self.controller._on_anomalies_request([{"file": "a.ndax", "type": "file_error", "reason": "x"}])
        assert worker.result is False
        assert question.call_count == 1

        # 路径 2：第一次不停止、第二次确认继续 → 放行
        question.reset_mock()
        question.side_effect = [True, True]
        self.controller._on_anomalies_request([{"file": "a.ndax", "type": "file_error", "reason": "x"}])
        assert worker.result is True
        assert question.call_count == 2

        # 路径 3：第一次继续、第二次中止 → 停止
        question.reset_mock()
        question.side_effect = [True, False]
        self.controller._on_anomalies_request([{"file": "a.ndax", "type": "missing_pulse", "current": 6, "voltage": 1.8}])
        assert worker.result is False

        # 路径 4：worker 已取消 → 直接停止，不弹框
        question.reset_mock()
        question.side_effect = None
        worker.b_cancel_requested = True
        self.controller._on_anomalies_request([{"file": "a.ndax", "type": "file_error", "reason": "x"}])
        assert worker.result is False
        question.assert_not_called()

    def test_missing_pulse_dialog_shows_voltage_and_count(self, monkeypatch):
        from unittest.mock import Mock

        worker = Mock(b_cancel_requested=False)
        self.controller.current_worker = worker
        dialog = Mock(return_value=False)
        monkeypatch.setattr(self.controller, "_show_anomaly_dialog", dialog)
        self.controller._on_anomalies_request([
            {"file": "a.ndax", "type": "missing_pulse", "current": 15, "voltage": 2.5},
            {"file": "a.ndax", "type": "missing_pulse", "current": 15, "voltage": 2.2},
        ])
        _, prompt, lines, _ = dialog.call_args.args
        assert "Missing/invalid slots: 2; affected files: 1" in prompt
        assert "15 mA / 2.5 V" in lines[0]
        assert "15 mA / 2.2 V" in lines[1]
        worker.confirm_anomalies.assert_called_once_with(False)

    def test_anomaly_dialog_scrolls_and_fits_screen(self):
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QApplication, QDialog, QPlainTextEdit, QPushButton

        app = QApplication.instance() or QApplication([])
        observed = {}

        def inspect_and_close():
            dialog = app.activeModalWidget()
            details = dialog.findChild(QPlainTextEdit)
            observed["height"] = dialog.height()
            observed["screen_height"] = dialog.screen().availableGeometry().height()
            observed["scroll_max"] = details.verticalScrollBar().maximum()
            observed["buttons"] = [b.text() for b in dialog.findChildren(QPushButton)]
            dialog.reject()

        QTimer.singleShot(0, inspect_and_close)
        result = self.controller._show_anomaly_dialog(
            "Analysis anomalies", "Stop the entire batch?", [f"file {i}: missing_pulse" for i in range(500)], "Review consequences"
        )
        assert result is False
        assert observed["height"] <= observed["screen_height"] * 2 / 3 + 1
        assert observed["scroll_max"] > 0
        assert "Stop batch" in observed["buttons"]
        assert "Review consequences" in observed["buttons"]
