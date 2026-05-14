import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.resource_manager import ResourceManager


class TestResourceManager:
    def setup_method(self):
        self.manager = ResourceManager()

    def test_get_optimal_process_count(self):
        result = self.manager.get_optimal_process_count()
        assert isinstance(result, int)
        assert result >= 1

    def test_get_processing_context(self):
        result = self.manager.get_processing_context()
        ctx_name = result.get_start_method()
        assert ctx_name == 'spawn'
