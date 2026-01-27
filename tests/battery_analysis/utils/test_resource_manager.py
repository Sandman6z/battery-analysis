import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.resource_manager import ResourceManager


class TestResourceManager:
    def setup_method(self):
        self.manager = ResourceManager()

    def test_get_resource_path(self):
        resource_name = "test_resource"
        result = self.manager.get_resource_path(resource_name)
        assert isinstance(result, str)

    def test_load_resource(self):
        resource_name = "test_resource"
        result = self.manager.load_resource(resource_name)
        assert result is not None

    def test_list_resources(self):
        result = self.manager.list_resources()
        assert isinstance(result, list)