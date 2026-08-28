"""
环境服务模块

提供环境检测和适配功能
"""

import logging
from typing import Any

from battery_analysis.utils.environment_utils import EnvironmentType, get_environment_detector


class EnvironmentService:
    """
    环境服务类
    提供环境检测和适配功能
    """

    def __init__(self):
        """
        初始化环境服务
        """
        self.logger = logging.getLogger(__name__)
        self.env_detector = None
        self.env_info = {}
        self.is_initialized = False
        # 暴露EnvironmentType以便其他组件使用
        self.EnvironmentType = EnvironmentType

    def initialize(self) -> bool:
        """
        初始化环境服务

        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("Initializing EnvironmentService...")

            # 初始化环境检测器
            self.env_detector = get_environment_detector()
            self.env_info = self.env_detector.get_environment_info()

            # 环境适配处理
            self._handle_environment_adaptation()

            self.is_initialized = True
            self.logger.info(
                "EnvironmentService initialized for %s",
                self.env_info.get("environment_type", "unknown"),
            )
            return True

        except (ImportError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Failed to initialize EnvironmentService: %s", e)
            return False

    def _handle_environment_adaptation(self):
        """
        处理环境适配逻辑（各环境特化方法待实现）
        """
        env_type = self.env_info.get("environment_type")
        self.logger.debug("Current environment type: %s", env_type)

    def get_environment_info(self) -> dict[str, Any]:
        """
        获取环境信息

        Returns:
            Dict[str, Any]: 环境信息
        """
        return self.env_info.copy()

    def get_environment_detector(self):
        """
        获取环境检测器

        Returns:
            环境检测器对象
        """
        return self.env_detector

    def get_environment_type(self) -> EnvironmentType | None:
        """
        获取环境类型

        Returns:
            EnvironmentType: 环境类型
        """
        return self.env_info.get("environment_type")

    def is_ide_environment(self) -> bool:
        """
        检查是否为IDE环境

        Returns:
            bool: 是否为IDE环境
        """
        return self.get_environment_type() == EnvironmentType.IDE

    def is_container_environment(self) -> bool:
        """
        检查是否为容器环境

        Returns:
            bool: 是否为容器环境
        """
        return self.get_environment_type() == EnvironmentType.CONTAINER

    def is_production_environment(self) -> bool:
        """
        检查是否为生产环境

        Returns:
            bool: 是否为生产环境
        """
        return self.get_environment_type() == EnvironmentType.PRODUCTION

    def is_development_environment(self) -> bool:
        """
        检查是否为开发环境

        Returns:
            bool: 是否为开发环境
        """
        return self.get_environment_type() == EnvironmentType.DEVELOPMENT

    def get_platform_info(self) -> dict[str, Any]:
        """
        获取平台信息

        Returns:
            Dict[str, Any]: 平台信息
        """
        return {
            "platform": self.env_info.get("platform"),
            "python_version": self.env_info.get("python_version"),
            "gui_available": self.env_info.get("gui_available", False),
            "display_available": self.env_info.get("display_available", False),
        }

    def shutdown(self):
        """
        关闭环境服务
        """
        self.logger.info("Shutting down EnvironmentService...")
        self.is_initialized = False
