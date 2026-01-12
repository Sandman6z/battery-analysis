# -*- coding: utf-8 -*-
"""
数据处理器初始化步骤
"""

from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.main.business_logic.data_processor import DataProcessor


class ProcessorsInitializationStep(InitializationStep):
    """数据处理器初始化步骤"""
    
    def __init__(self):
        """初始化数据处理器初始化步骤"""
        super().__init__("processors", priority=60)
    
    def execute(self, main_window) -> bool:
        """
        执行数据处理器初始化
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        try:
            # 初始化数据处理器（使用优化的pandas版本）
            main_window.data_processor = DataProcessor(main_window)
            self.logger.info("数据处理器初始化完成")
            return True
        except Exception as e:
            self.logger.exception("数据处理器初始化失败")
            return False
    
    def can_execute(self, main_window) -> bool:
        """
        检查是否可以执行此步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否可以执行
        """
        return hasattr(main_window, 'config_manager')
