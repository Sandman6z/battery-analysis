import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.initialization.steps.presenters_initialization_step import PresentersInitializationStep


class TestPresentersInitializationStep:
    def setup_method(self):
        self.step = PresentersInitializationStep()

    def test_execute(self):
        main_window = Mock()
        result = self.step.execute(main_window)
        assert isinstance(result, bool)

    def test_get_name(self):
        result = self.step.get_name()
        assert isinstance(result, str)

    def test_get_priority(self):
        result = self.step.get_priority()
        assert isinstance(result, int)

    def test_can_execute(self):
        main_window = Mock()
        result = self.step.can_execute(main_window)
        assert result is True