from unittest.mock import Mock, patch
from battery_analysis.main.controllers.main_controller import MainController


class TestMainController:
    def setup_method(self):
        self.controller = MainController()

    def test_set_project_context(self):
        self.controller.set_project_context(
            project_path="/test/project",
            input_path="/test/input",
            output_path="/test/output"
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