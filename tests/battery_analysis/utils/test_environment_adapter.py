import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.utils.environment_adapter import EnvironmentAdapter


class TestEnvironmentAdapter:
    def setup_method(self):
        self.adapter = EnvironmentAdapter()

    def test_get_environment_variable(self):
        variable_name = "TEST_VAR"
        result = self.adapter.get_environment_variable(variable_name)
        assert isinstance(result, str)

    def test_set_environment_variable(self):
        variable_name = "TEST_VAR"
        variable_value = "test_value"
        result = self.adapter.set_environment_variable(variable_name, variable_value)
        assert result is True

    def test_delete_environment_variable(self):
        variable_name = "TEST_VAR"
        result = self.adapter.delete_environment_variable(variable_name)
        assert result is True