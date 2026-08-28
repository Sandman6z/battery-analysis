import os
from unittest.mock import Mock

from battery_analysis.main.managers.path_manager import PathManager


class TestPathManager:
    def setup_method(self):
        self.main_window = Mock()
        self.manager = PathManager(self.main_window)

    def test_get_parent_directory(self):
        result = self.manager.get_parent_directory(os.getcwd())
        assert result is not None
