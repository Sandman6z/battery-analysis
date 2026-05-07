from unittest.mock import Mock
from battery_analysis.main.initialization.initialization_orchestrator import InitializationOrchestrator


class TestInitializationOrchestrator:
    def setup_method(self):
        self.orchestrator = InitializationOrchestrator()

    def test_get_total_steps_empty(self):
        assert self.orchestrator.get_total_steps() == 0

    def test_get_pending_steps_empty(self):
        assert self.orchestrator.get_pending_steps() == []

    def test_clear(self):
        self.orchestrator.clear()
        assert self.orchestrator.get_total_steps() == 0