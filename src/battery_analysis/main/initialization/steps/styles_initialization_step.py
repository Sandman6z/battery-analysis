# -*- coding: utf-8 -*-
"""
样式加载初始化步骤
"""

import PyQt6.QtWidgets as QW
from battery_analysis.main.initialization.initialization_step import InitializationStep


class StylesInitializationStep(InitializationStep):
    """样式加载初始化步骤"""
    
    def __init__(self):
        """初始化样式加载初始化步骤"""
        super().__init__("styles", priority=100)
    
    def execute(self, main_window) -> bool:
        """
        执行样式加载初始化
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        try:
            from battery_analysis.ui.styles import style_manager
            app = QW.QApplication.instance()
            if app:
                style_manager.apply_global_style(app, "modern")
            self.logger.info("样式加载完成")
            return True
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("Failed to load QSS styles: %s", e)
            return True  # 样式加载失败不影响应用启动
    
    def can_execute(self, main_window) -> bool:
        """
        检查是否可以执行此步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否可以执行
        """
        return True
