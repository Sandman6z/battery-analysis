# -*- coding: utf-8 -*-
"""
命令管理器初始化步骤
"""

from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.main.managers.command_manager import CommandManager


class CommandManagerInitializationStep(InitializationStep):
    """命令管理器初始化步骤"""
    
    def __init__(self):
        """初始化命令管理器初始化步骤"""
        super().__init__("command_manager", priority=85)
    
    def execute(self, main_window) -> bool:
        """
        执行命令管理器初始化
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        try:
            # 初始化命令管理器
            main_window.command_manager = CommandManager(main_window)
            self.logger.info("命令管理器初始化完成")
            return True
        except Exception as e:
            self.logger.exception("命令管理器初始化失败")
            return False
    
    def can_execute(self, main_window) -> bool:
        """
        检查是否可以执行此步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否可以执行
        """
        return hasattr(main_window, 'presenter') and hasattr(main_window, 'analysis_runner')
