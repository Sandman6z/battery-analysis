# -*- coding: utf-8 -*-
"""
服务上下文管理器

确保资源正确释放的多服务上下文管理
"""

import logging

from battery_analysis.main.services.service_container.container import get_service_container


def _cleanup_service(service, service_name, container):
    """尝试关闭或停止服务"""
    cleanup = getattr(service, 'close', None) or getattr(service, 'shutdown', None)
    if cleanup:
        try:
            cleanup()
            container.logger.debug("Service %s cleaned up", service_name)
        except Exception as e:
            container.logger.error("Failed to cleanup service %s: %s", service_name, e)


class ServiceContext:
    """
    服务上下文管理器，确保资源正确释放

    示例用法：

    with ServiceContext('file') as file_service:
        file_service.create_directory('output')
    """

    def __init__(self, service_name):
        self.service_name = service_name
        self.service = None
        self.container = get_service_container()

    def __enter__(self):
        self.service = self.container.get(self.service_name)
        if self.service:
            self.container.logger.debug("Service %s acquired through context manager", self.service_name)
        else:
            self.container.logger.warning("Failed to acquire service %s through context manager", self.service_name)
        return self.service

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.service:
            _cleanup_service(self.service, self.service_name, self.container)
        return False


class MultiServiceContext:
    """
    多服务上下文管理器，同时管理多个服务的资源

    示例用法：

    with MultiServiceContext(['file', 'config']) as services:
        file_service, config_service = services['file'], services['config']
    """

    def __init__(self, service_names):
        self.service_names = service_names
        self.services = {}
        self.container = get_service_container()

    def __enter__(self):
        for service_name in self.service_names:
            service = self.container.get(service_name)
            if service:
                self.services[service_name] = service
                self.container.logger.debug("Service %s acquired through multi-service context", service_name)
            else:
                self.container.logger.warning("Failed to acquire service %s through multi-service context", service_name)
        return self.services

    def __exit__(self, exc_type, exc_val, exc_tb):
        for service_name, service in self.services.items():
            _cleanup_service(service, service_name, self.container)
        self.services.clear()
        return False
