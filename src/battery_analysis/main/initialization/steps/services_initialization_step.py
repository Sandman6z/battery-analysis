# -*- coding: utf-8 -*-
"""
服务初始化步骤
"""

from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.main.services.service_container import get_service_container


class ServicesInitializationStep(InitializationStep):
    """服务初始化步骤"""
    
    def __init__(self):
        """初始化服务初始化步骤"""
        super().__init__("services", priority=20)
    
    def execute(self, main_window) -> bool:
        """
        执行服务初始化
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        try:
            # 获取服务容器
            main_window._service_container = get_service_container()
            self.logger.info("服务容器初始化完成")
            return True
        except Exception as e:
            self.logger.exception("服务容器初始化失败")
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
