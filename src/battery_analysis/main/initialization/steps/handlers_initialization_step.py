# -*- coding: utf-8 -*-
"""
处理器初始化步骤
"""

from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.main.handlers.temperature_handler import TemperatureHandler
from battery_analysis.main.managers.report_manager import ReportManager
from battery_analysis.main.managers.path_manager import PathManager
from battery_analysis.main.managers.test_profile_manager import TestProfileManager
from battery_analysis.main.managers.environment_manager import EnvironmentManager
from battery_analysis.main.managers.visualization_manager import VisualizationManager
from battery_analysis.main.managers.analysis_runner import AnalysisRunner
from battery_analysis.main.business_logic.validation_manager import ValidationManager


class HandlersInitializationStep(InitializationStep):
    """处理器初始化步骤"""
    
    def __init__(self):
        """初始化处理器初始化步骤"""
        super().__init__("handlers", priority=70)
    
    def execute(self, main_window) -> bool:
        """
        执行处理器初始化
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        try:
            # 初始化自定义管理器和处理器
            main_window.temperature_handler = TemperatureHandler(main_window)
            main_window.report_manager = ReportManager(main_window)
            main_window.path_manager = PathManager(main_window)
            main_window.test_profile_manager = TestProfileManager(main_window)
            main_window.environment_manager = EnvironmentManager(main_window)
            main_window.visualization_manager = VisualizationManager(main_window)
            main_window.analysis_runner = AnalysisRunner(main_window)
            
            # 初始化验证管理器
            main_window.validation_manager = ValidationManager(main_window)
            
            self.logger.info("处理器初始化完成")
            return True
        except Exception as e:
            self.logger.exception("处理器初始化失败")
            return False
    
    def can_execute(self, main_window) -> bool:
        """
        检查是否可以执行此步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否可以执行
        """
        return hasattr(main_window, 'data_processor')
