# -*- coding: utf-8 -*-
"""
服务容器模块

提供依赖注入和服务生命周期管理功能
实现控制反转和单例模式
"""

from battery_analysis.main.services.service_container.interfaces import IServiceContainer
from battery_analysis.main.services.service_container.container import (
    ServiceContainer,
    get_service_container,
    set_service_container,
)
from battery_analysis.main.services.service_container.context import (
    ServiceContext,
    MultiServiceContext,
)

__all__ = [
    "IServiceContainer",
    "ServiceContainer",
    "get_service_container",
    "set_service_container",
    "ServiceContext",
    "MultiServiceContext",
]
