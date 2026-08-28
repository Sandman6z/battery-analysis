"""
服务容器模块

提供 Services 数据类和向后兼容的 ServiceContainer 包装，
替代原有的复杂 DI 容器（拓扑排序、依赖图解析等）。
"""

from battery_analysis.main.services.service_container.container import (
    ServiceContainer,
    Services,
    get_service_container,
    set_service_container,
)

__all__ = [
    "ServiceContainer",
    "Services",
    "get_service_container",
    "set_service_container",
]
