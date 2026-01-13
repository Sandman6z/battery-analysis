# -*- coding: utf-8 -*-
"""
环境初始化步骤
"""

import sys
from pathlib import Path
from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.main.utils import EnvironmentAdapter


class EnvironmentInitializationStep(InitializationStep):
    """环境初始化步骤"""
    
    def __init__(self):
        """初始化环境初始化步骤"""
        super().__init__("environment", priority=30)
    
    def execute(self, main_window) -> bool:
        """
        执行环境初始化
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        try:
            # 初始化环境信息
            main_window.env_info = {}
            
            # 初始化环境适配器（在env_info初始化之后）
            main_window.environment_adapter = EnvironmentAdapter(main_window)
            # 使用环境适配器初始化环境检测器
            main_window.env_detector = main_window.environment_adapter.initialize_environment_detector()
            
            # 从环境检测器获取环境信息
            if hasattr(main_window, 'env_detector') and main_window.env_detector:
                main_window.env_info = main_window.env_detector.get_environment_info()
            elif main_window.environment_adapter.env_service:
                # 从环境服务获取环境信息
                main_window.env_info = main_window.environment_adapter.env_service.get_environment_info()

            # 环境适配处理 - 使用环境适配器
            main_window.environment_adapter.handle_environment_adaptation()

            if sys.platform == "win32":
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("bt")

            # 获取项目根路径
            project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            main_window.current_directory = str(project_root)
            main_window.path = str(project_root)
            
            self.logger.info("环境初始化完成")
            return True
        except Exception as e:
            self.logger.exception("环境初始化失败")
            return False
    
    def can_execute(self, main_window) -> bool:
        """
        检查是否可以执行此步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否可以执行
        """
        return True
