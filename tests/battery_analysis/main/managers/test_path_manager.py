import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.managers.path_manager import PathManager


class TestPathManager:
    def setup_method(self):
        self.manager = PathManager()

    def test_get_data_path(self):
        result = self.manager.get_data_path()
        assert isinstance(result, str)

    def test_get_report_path(self):
        result = self.manager.get_report_path()
        assert isinstance(result, str)

    def test_get_config_path(self):
        result = self.manager.get_config_path()
        assert isinstance(result, str)

    def test_ensure_paths_exist(self):
        result = self.manager.ensure_paths_exist()
        assert result is True