from unittest.mock import Mock

from battery_analysis.main.managers.analysis_runner import AnalysisRunner


class TestAnalysisRunner:
    def setup_method(self):
        self.main_window = Mock()
        self.runner = AnalysisRunner(self.main_window)

    def test_init(self):
        assert self.runner.main_window == self.main_window

    def test_run_analysis(self):
        self.main_window.save_table = Mock()
        self.main_window.init_widgetcolor = Mock()
        self.runner.run_analysis()
        self.main_window.save_table.assert_called_once()
        self.main_window.init_widgetcolor.assert_called_once()
