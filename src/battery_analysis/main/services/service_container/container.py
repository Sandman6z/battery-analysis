# -*- coding: utf-8 -*-
"""
服务容器 — 简单工厂模式

替换原有的带拓扑排序/依赖图解析的复杂 DI 容器。
服务实例通过 create_services() 显式创建，按名访问。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Any


# ── Services 数据类 ──────────────────────────────────────────────


@dataclass
class Services:
    """应用中所有共享服务的具名容器。"""
    config: Any = None
    environment: Any = None
    file: Any = None
    progress: Any = None
    validation: Any = None
    application: Any = None
    main_controller: Any = None
    file_controller: Any = None
    validation_controller: Any = None

    def get(self, name: str) -> Any:
        """按字符串名获取服务（保持向后兼容）。

        通用属性查找：直接返回对应字段值，不再经 _name_map 白名单；
        未知名称或未设置字段返回 None（如 get('application') 现返回字段默认值）。
        """
        return getattr(self, name, None)


# ── ServiceContainer 兼容包装 ────────────────────────────────────


class ServiceContainer:
    """向下兼容的容器包装。

    旧代码通过 get_service_container().get("name") 获取服务。
    使用增量构造：先创建无依赖的服务并写入 _impl，
    再创建可能回调容器的服务。
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._services_initialized = False
        self._impl: Optional[Services] = None

    def _initialize_services(self):
        if self._services_initialized:
            return
        self._services_initialized = True

        # 1) 创建空容器（让回调不会因 _impl is None 而崩溃）
        self._impl = Services()

        # 2) 创建无回调依赖的叶子服务
        from battery_analysis.main.services.config_service import ConfigService
        from battery_analysis.main.services.environment_service import EnvironmentService
        from battery_analysis.main.services.file_service import FileService
        from battery_analysis.main.services.progress_service import ProgressService
        from battery_analysis.main.services.validation_service import ValidationService

        self._impl.config = ConfigService()
        self._impl.environment = EnvironmentService()
        self._impl.file = FileService()
        self._impl.progress = ProgressService()
        self._impl.validation = ValidationService()

        # 3) 创建可能回调容器的服务（此时 _impl 已有叶子服务，get("file") 等正常返回）
        from battery_analysis.main.controllers.file_controller import FileController
        from battery_analysis.main.controllers.main_controller import MainController
        from battery_analysis.main.controllers.validation_controller import ValidationController

        self._impl.file_controller = FileController()
        self._impl.main_controller = MainController()
        self._impl.validation_controller = ValidationController()

        self.logger.info("Services initialized incrementally: %s", type(self._impl).__name__)

    def get(self, name: str) -> Any:
        if not self._services_initialized:
            self._initialize_services()
        return self._impl.get(name) if self._impl else None

    def has(self, name: str) -> bool:
        return self.get(name) is not None


# ── 全局访问点 ────────────────────────────────────────────────────

_global_container: Optional[ServiceContainer] = None


def get_service_container() -> ServiceContainer:
    global _global_container
    if _global_container is None:
        _global_container = ServiceContainer()
    return _global_container


def set_service_container(container: ServiceContainer):
    global _global_container
    _global_container = container
