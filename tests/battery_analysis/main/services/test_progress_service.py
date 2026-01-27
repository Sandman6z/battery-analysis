import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.services.progress_service import ProgressService


class TestProgressService:
    def setup_method(self):
        self.service = ProgressService()

    def test_update_progress(self):
        progress = 50
        status = "Test status"
        result = self.service.update_progress(progress, status)
        assert result is True

    def test_get_progress(self):
        result = self.service.get_progress()
        assert isinstance(result, dict)

    def test_reset_progress(self):
        result = self.service.reset_progress()
        assert result is True