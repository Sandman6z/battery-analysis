import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.initialization.steps.basic_attributes_step import BasicAttributesInitializationStep


class TestBasicAttributesInitializationStep:
    def setup_method(self):
        self.step = BasicAttributesInitializationStep()

    def test_execute(self):
        main_window = Mock()
        result = self.step.execute(main_window)
        assert result is True

    def test_get_name(self):
        result = self.step.get_name()
        assert result == "basic_attributes"

    def test_get_priority(self):
        result = self.step.get_priority()
        assert result == 10

    def test_can_execute(self):
        main_window = Mock()
        result = self.step.can_execute(main_window)
        assert result is True