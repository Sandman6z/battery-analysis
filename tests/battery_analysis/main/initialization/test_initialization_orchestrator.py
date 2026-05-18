from unittest.mock import Mock
from battery_analysis.main.initialization.initialization_orchestrator import (
    InitializationOrchestrator,
)


class TestInitializationOrchestrator:
    def setup_method(self):
        self.orchestrator = InitializationOrchestrator()

    def _register_dummy_step(self, name="test", priority=50, phase="test"):
        step = Mock()
        step.get_name.return_value = name
        step.get_priority.return_value = priority
        step.can_execute.return_value = True
        step.execute.return_value = True
        self.orchestrator.register_step(step, phase=phase)
        return step

    def test_get_total_steps_empty(self):
        assert self.orchestrator.get_total_steps() == 0

    def test_get_pending_steps_empty(self):
        assert self.orchestrator.get_pending_steps() == []

    def test_get_phases_returns_empty_dict_initially(self):
        assert self.orchestrator.get_phases() == {}

    def test_register_step_adds_to_phase(self):
        self._register_dummy_step("s1", phase="env")
        assert self.orchestrator.get_total_steps() == 1
        phases = self.orchestrator.get_phases()
        assert "env" in phases
        assert len(phases["env"]) == 1

    def test_register_steps_batch(self):
        steps = [Mock(), Mock()]
        for s in steps:
            s.get_name.return_value = "s"
            s.get_priority.return_value = 50
            s.can_execute.return_value = True
            s.execute.return_value = True
        self.orchestrator.register_steps(steps, phase="core")
        assert self.orchestrator.get_total_steps() == 2

    def test_execute_all_runs_all_steps(self):
        s1 = self._register_dummy_step("s1", phase="a")
        s2 = self._register_dummy_step("s2", phase="b")
        main_window = Mock()
        result = self.orchestrator.execute_all(main_window)
        assert result is True
        s1.execute.assert_called_once_with(main_window)
        s2.execute.assert_called_once_with(main_window)

    def test_execute_all_phase_order(self):
        """验证阶段按注册顺序执行"""
        call_order = []
        s1 = Mock()
        s1.get_name.return_value = "s1"
        s1.get_priority.return_value = 10
        s1.can_execute.return_value = True
        s1.execute.side_effect = lambda mw: call_order.append("s1")

        s2 = Mock()
        s2.get_name.return_value = "s2"
        s2.get_priority.return_value = 10
        s2.can_execute.return_value = True
        s2.execute.side_effect = lambda mw: call_order.append("s2")

        self.orchestrator.register_step(s1, phase="first")
        self.orchestrator.register_step(s2, phase="second")
        self.orchestrator.execute_all(Mock())
        # s1 (phase "first") 应当在 s2 (phase "second") 之前
        assert call_order == ["s1", "s2"]

    def test_execute_all_step_failure(self):
        s1 = self._register_dummy_step("ok", phase="p")
        s2 = self._register_dummy_step("fail", phase="p")
        s2.execute.return_value = False
        main_window = Mock()
        result = self.orchestrator.execute_all(main_window)
        assert result is False

    def test_clear(self):
        self._register_dummy_step(phase="p")
        self.orchestrator.clear()
        assert self.orchestrator.get_total_steps() == 0
        assert self.orchestrator.get_phases() == {}

    def test_get_step_by_name(self):
        self._register_dummy_step("target", phase="p")
        step = self.orchestrator.get_step("target")
        assert step is not None
        assert step.get_name() == "target"

    def test_get_step_not_found(self):
        assert self.orchestrator.get_step("nonexistent") is None

    def test_get_executed_steps_after_run(self):
        s = self._register_dummy_step("s1", phase="p")
        self.orchestrator.execute_all(Mock())
        executed = self.orchestrator.get_executed_steps()
        assert "s1" in executed
        assert executed["s1"] is True
