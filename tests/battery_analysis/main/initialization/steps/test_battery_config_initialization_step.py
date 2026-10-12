from unittest.mock import Mock

from battery_analysis.main.initialization.steps.battery_config_initialization_step import (
    BatteryConfigInitializationStep,
)


def _make_main_window(pulse_current, cutoff_voltage):
    main_window = Mock()

    def get_config(key):
        if key == "BatteryConfig/PulseCurrent":
            return list(pulse_current)
        if key == "BatteryConfig/CutOffVoltage":
            return list(cutoff_voltage)
        return []

    main_window.config_manager.get_config.side_effect = get_config
    return main_window


class TestBatteryConfigInitializationStep:
    def setup_method(self):
        self.step = BatteryConfigInitializationStep()

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

    def test_execute_keeps_fractional_currents(self):
        """Freezer 档 7.5mA 不得被截断为 7"""
        main_window = _make_main_window(["15", "13", "7.5", "3"], ["2.6", "2.25"])
        assert self.step.execute(main_window) is True
        assert main_window.listCurrentLevel == [15, 13, 7.5, 3]
        assert main_window.listVoltageLevel == [2.6, 2.25]

    def test_execute_normalizes_integral_floats_to_int(self):
        main_window = _make_main_window(["30.0", "26.0", "15.0", "6.0"], ["2.6"])
        assert self.step.execute(main_window) is True
        assert main_window.listCurrentLevel == [30, 26, 15, 6]

    def test_execute_empty_config_uses_default(self):
        """配置为空时兜底 config_defaults 的档位"""
        main_window = _make_main_window([], ["2.6"])
        assert self.step.execute(main_window) is True
        assert main_window.listCurrentLevel == [30, 26, 15, 6]
