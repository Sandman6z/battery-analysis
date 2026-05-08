# -*- coding: utf-8 -*-
"""
服务上下文管理器

确保资源正确释放的多服务上下文管理
"""

import logging

from battery_analysis.main.services.service_container.container import get_service_container


class ServiceContext:
    """
    服务上下文管理器，确保资源正确释放

    示例用法：

    with ServiceContext('file') as file_service:
        # 使用文件服务
        file_service.create_directory('output')
    # 退出上下文时自动处理资源
    """

    def __init__(self, service_name, auto_release: bool = True):
        """
        初始化服务上下文管理器

        Args:
            service_name: 服务名称
            auto_release: 是否在退出上下文时自动释放资源，默认True
        """
        self.service_name = service_name
        self.auto_release = auto_release
        self.service = None
        self.container = get_service_container()

    def __enter__(self):
        """
        进入上下文，获取服务实例

        Returns:
            服务实例
        """
        self.service = self.container.get(self.service_name)
        if self.service:
            # 记录服务获取
            self.container.logger.debug("Service %s acquired through context manager", self.service_name)
        else:
            self.container.logger.warning("Failed to acquire service %s through context manager", self.service_name)
        return self.service

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文，处理资源释放

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常回溯

        Returns:
            bool: 是否抑制异常
        """
        if self.service:
            try:
                # 检查服务是否有close方法
                if hasattr(self.service, 'close'):
                    try:
                        self.service.close()
                        self.container.logger.debug("Service %s closed", self.service_name)
                    except Exception as e:
                        self.container.logger.error("Failed to close service %s: %s", self.service_name, e)
                # 检查服务是否有shutdown方法
                elif hasattr(self.service, 'shutdown'):
                    try:
                        self.service.shutdown()
                        self.container.logger.debug("Service %s shutdown", self.service_name)
                    except Exception as e:
                        self.container.logger.error("Failed to shutdown service %s: %s", self.service_name, e)

                # 如果启用自动释放，从容器中移除实例
                if self.auto_release:
                    # 注意：这里不直接删除实例，而是依赖容器的资源释放机制
                    # 这样可以确保依赖该服务的其他组件不受影响
                    pass

            except Exception as e:
                self.container.logger.error("Error in service context exit: %s", e)

        # 不抑制异常
        return False


class MultiServiceContext:
    """
    多服务上下文管理器，同时管理多个服务的资源

    示例用法：

    with MultiServiceContext(['file', 'config']) as services:
        file_service, config_service = services['file'], services['config']
        # 使用多个服务
    # 退出上下文时自动处理所有资源
    """

    def __init__(self, service_names, auto_release: bool = True):
        """
        初始化多服务上下文管理器

        Args:
            service_names: 服务名称列表
            auto_release: 是否在退出上下文时自动释放资源，默认True
        """
        self.service_names = service_names
        self.auto_release = auto_release
        self.services = {}
        self.container = get_service_container()

    def __enter__(self):
        """
        进入上下文，获取所有服务实例

        Returns:
            dict: 服务名称到服务实例的映射
        """
        for service_name in self.service_names:
            service = self.container.get(service_name)
            if service:
                self.services[service_name] = service
                self.container.logger.debug("Service %s acquired through multi-service context", service_name)
            else:
                self.container.logger.warning("Failed to acquire service %s through multi-service context", service_name)
        return self.services

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文，处理所有资源释放

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常回溯

        Returns:
            bool: 是否抑制异常
        """
        for service_name, service in self.services.items():
            try:
                # 检查服务是否有close方法
                if hasattr(service, 'close'):
                    try:
                        service.close()
                        self.container.logger.debug("Service %s closed", service_name)
                    except Exception as e:
                        self.container.logger.error("Failed to close service %s: %s", service_name, e)
                # 检查服务是否有shutdown方法
                elif hasattr(service, 'shutdown'):
                    try:
                        service.shutdown()
                        self.container.logger.debug("Service %s shutdown", service_name)
                    except Exception as e:
                        self.container.logger.error("Failed to shutdown service %s: %s", service_name, e)
            except Exception as e:
                self.container.logger.error("Error in multi-service context exit for %s: %s", service_name, e)

        # 清空服务字典
        self.services.clear()

        # 不抑制异常
        return False
