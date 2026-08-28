from unittest.mock import Mock

from battery_analysis.main.managers.report_manager import ReportManager


class TestReportManager:
    def setup_method(self):
        self.main_window = Mock()
        self.manager = ReportManager(self.main_window)

    def test_init(self):
        assert self.manager.main_window == self.main_window
