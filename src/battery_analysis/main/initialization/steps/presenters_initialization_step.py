# -*- coding: utf-8 -*-
"""
Presenter初始化步骤
"""

from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.main.presenters.main_presenter import MainPresenter


class PresentersInitializationStep(InitializationStep):
    """Presenter初始化步骤"""
    
    def __init__(self):
        """初始化Presenter初始化步骤"""
        super().__init__("presenters", priority=80)
    
    def execute(self, main_window) -> bool:
        """
        执行Presenter初始化
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        try:
            # 初始化Presenter
            main_window.presenter = MainPresenter(main_window)
            main_window.presenter.initialize()
            self.logger.info("Presenter初始化完成")
            return True
        except Exception as e:
            self.logger.exception("Presenter初始化失败")
            return False
    
    def can_execute(self, main_window) -> bool:
        """
        检查是否可以执行此步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否可以执行
        """
        return hasattr(main_window, 'validation_manager')
