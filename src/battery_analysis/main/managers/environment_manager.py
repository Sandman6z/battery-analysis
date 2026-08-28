"""环境管理器模块"""

import logging


class EnvironmentManager:
    """环境信息管理器"""

    def __init__(self, main_window=None):
        """
        初始化环境管理器

        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._env_info = {}  # 当无 main_window 时使用本地存储

    def _get_env_service(self):
        if self.main_window:
            return self.main_window._get_service("environment")
        return None

    def _get_env_info_dict(self):
        """获取 env_info 字典（main_window 优先）。"""
        if self.main_window and hasattr(self.main_window, "env_info"):
            return self.main_window.env_info
        return self._env_info

    def _set_env_info_dict(self, value):
        if self.main_window and hasattr(self.main_window, "env_info"):
            self.main_window.env_info = value
        self._env_info = value

    def initialize_environment_info(self):
        """初始化环境信息"""
        try:
            env_svc = self._get_env_service()
            if env_svc:
                if hasattr(env_svc, "env_info"):
                    self._set_env_info_dict(env_svc.env_info)
                elif hasattr(env_svc, "initialize"):
                    if env_svc.initialize() and hasattr(env_svc, "env_info"):
                        self._set_env_info_dict(env_svc.env_info)
        except (AttributeError, TypeError, ImportError, OSError) as e:
            self.logger.warning("Failed to initialize environment service: %s", e)

    def ensure_env_info_keys(self):
        """确保环境信息包含必要的键"""
        env_info = self._get_env_info_dict()

        if "environment_type" not in env_info:
            try:
                env_svc = self._get_env_service()
                if env_svc and hasattr(env_svc, "EnvironmentType"):
                    env_info["environment_type"] = env_svc.EnvironmentType.DEVELOPMENT
                else:
                    from battery_analysis.utils.environment_utils import EnvironmentType

                    env_info["environment_type"] = EnvironmentType.DEVELOPMENT
            except (AttributeError, TypeError, ImportError) as e:
                self.logger.warning("Failed to get EnvironmentType: %s", e)
                from battery_analysis.utils.environment_utils import EnvironmentType

                env_info["environment_type"] = EnvironmentType.DEVELOPMENT

        if "gui_available" not in env_info:
            env_info["gui_available"] = True

        self._set_env_info_dict(env_info)

    def initialize_all(self):
        """初始化所有环境信息"""
        self.initialize_environment_info()
        self.ensure_env_info_keys()
