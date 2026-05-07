from unittest.mock import Mock
from battery_analysis.main.managers.test_profile_manager import TestProfileManager


class TestTestProfileManager:
    def setup_method(self):
        self.main_window = Mock()
        self.manager = TestProfileManager(self.main_window)

    def test_init(self):
        assert self.manager.main_window == self.main_window