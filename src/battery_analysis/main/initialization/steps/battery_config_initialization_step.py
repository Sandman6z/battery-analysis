# -*- coding: utf-8 -*-
"""
电池配置初始化步骤

负责初始化电流和电压级别配置
"""

from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.utils.config_parser import safe_int_convert, safe_float_convert


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
            self.logger.info("开始初始化电池配置")
            
            # 获取配置
            listPulseCurrent = main_window.get_config("BatteryConfig/PulseCurrent")
            listCutoffVoltage = main_window.get_config("BatteryConfig/CutoffVoltage")

            # 处理可能包含浮点数的电流值
            try:
                main_window.listCurrentLevel = [safe_int_convert(listPulseCurrent[c].strip())
                                                for c in range(len(listPulseCurrent))]
            except (ValueError, TypeError):
                # 如果转换失败，使用默认值
                main_window.listCurrentLevel = [0] * len(listPulseCurrent)
                self.logger.warning("电流值转换失败，使用默认值")

            main_window.listVoltageLevel = [
                safe_float_convert(listCutoffVoltage[c].strip()) for c in range(len(listCutoffVoltage))]
            
            self.logger.info("电池配置初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"电池配置初始化失败: {e}")
            return False
