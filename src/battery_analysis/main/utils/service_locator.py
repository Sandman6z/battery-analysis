# -*- coding: utf-8 -*-
"""
服务定位器工具

负责统一管理服务和控制器的获取，实现依赖注入
"""

# 标准库导入
import logging


class ServiceLocator:
    """
    服务定位器类，用于获取服务和控制器实例
    """
    
    def __init__(self, main_window):
        """
        初始化服务定位器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def get_service(self, service_name):
        """
        懒加载获取服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            服务实例或None
        """
        if service_name not in self.main_window._services:
            try:
                self.main_window._services[service_name] = self.main_window._service_container.get(service_name)
            except (TypeError, AttributeError, OSError, ValueError, ImportError) as e:
                self.logger.warning("Failed to get service %s: %s", service_name, e)
                self.main_window._services[service_name] = None
        return self.main_window._services[service_name]
    
    def get_controller(self, controller_name):
        """
        懒加载获取控制器
        
        Args:
            controller_name: 控制器名称
            
        Returns:
            控制器实例或None
        """
        if controller_name not in self.main_window._controllers:
            try:
                self.main_window._controllers[controller_name] = self.main_window._service_container.get(controller_name)
            except (TypeError, AttributeError, OSError, ValueError, ImportError) as e:
                self.logger.warning("Failed to get controller %s: %s", controller_name, e)
                self.main_window._controllers[controller_name] = None
        return self.main_window._controllers[controller_name]