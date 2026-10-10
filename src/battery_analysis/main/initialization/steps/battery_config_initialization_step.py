"""
电池配置初始化步骤

负责初始化电流和电压级别配置
"""

from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.utils.config_defaults import DEFAULT_CONFIG
from battery_analysis.utils.config_parser import safe_float_convert
from battery_analysis.utils.pulse_currents import normalize_current_levels


class BatteryConfigInitializationStep(InitializationStep):
    """
    电池配置初始化步骤
    """

    def __init__(self):
        """
        初始化电池配置步骤
        """
        super().__init__(name="battery_config", priority=90)

    def execute(self, main_window) -> bool:
        """
        执行电池配置初始化

        Args:
            main_window: 主窗口实例

        Returns:
            是否执行成功
        """
        try:
            self.logger.info("Starting battery configuration initialization")

            # 获取配置
            listPulseCurrent = main_window.config_manager.get_config("BatteryConfig/PulseCurrent")
            listCutoffVoltage = main_window.config_manager.get_config("BatteryConfig/CutOffVoltage")

            # 脉冲电流配置为空时使用默认档位
            if not listPulseCurrent:
                listPulseCurrent = [str(v) for v in DEFAULT_CONFIG["battery"]["pulseCurrents"]]
                self.logger.warning("Pulse current config is empty, using default: %s", listPulseCurrent)

            # 处理可能包含浮点数的电流值（如 Freezer 档 7.5mA，需保留小数，整数档规整为 int）
            try:
                main_window.listCurrentLevel = normalize_current_levels(
                    safe_float_convert(listPulseCurrent[c]) for c in range(len(listPulseCurrent))
                )
            except (ValueError, TypeError):
                # 如果转换失败，使用默认值
                main_window.listCurrentLevel = [0] * len(listPulseCurrent)
                self.logger.warning("Failed to convert current values, using defaults")

            main_window.listVoltageLevel = [
                safe_float_convert(listCutoffVoltage[c].strip())
                for c in range(len(listCutoffVoltage))
            ]

            self.logger.info("Battery configuration initialization complete")
            return True
        except Exception as e:
            self.logger.error(f"Battery configuration initialization failed: {e}")
            return False
