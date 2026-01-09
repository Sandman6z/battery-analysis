# -*- coding: utf-8 -*-
"""
环境管理器

负责处理应用程序的环境信息和适配
"""

import logging

# 本地应用/库导入
from battery_analysis.utils.environment_utils import EnvironmentType


class EnvironmentManager:
    """
    环境管理器类，负责处理应用程序的环境信息和适配
    """
    
    def __init__(self, main_window):
        """
        初始化环境管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def _initialize_environment_info(self):
        """
        初始化环境信息
        """
        try:
            environment_service = self.main_window._get_service("environment")
            if environment_service:
                if hasattr(environment_service, 'env_info'):
                    self.main_window.env_info = environment_service.env_info
                elif hasattr(environment_service, 'initialize'):
                    if environment_service.initialize() and hasattr(environment_service, 'env_info'):
                        self.main_window.env_info = environment_service.env_info
        except (AttributeError, TypeError, ImportError, OSError) as e:
            self.logger.warning("Failed to initialize environment service: %s", e)
    
    def _ensure_env_info_keys(self):
        """
        确保环境信息包含必要的键
        """
        if 'environment_type' not in self.main_window.env_info:
            try:
                environment_service = self.main_window._get_service("environment")
                if environment_service and hasattr(environment_service, 'EnvironmentType'):
                    self.main_window.env_info['environment_type'] = environment_service.EnvironmentType.DEVELOPMENT
                else:
                    # 降级到直接导入
                    from battery_analysis.utils.environment_utils import EnvironmentType
                    self.main_window.env_info['environment_type'] = EnvironmentType.DEVELOPMENT
            except (AttributeError, TypeError, ImportError) as e:
                self.logger.warning("Failed to get EnvironmentType: %s", e)
                from battery_analysis.utils.environment_utils import EnvironmentType
                self.main_window.env_info['environment_type'] = EnvironmentType.DEVELOPMENT
        
        if 'gui_available' not in self.main_window.env_info:
            self.main_window.env_info['gui_available'] = True
