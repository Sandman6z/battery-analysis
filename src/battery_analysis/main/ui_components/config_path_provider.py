"""
配置路径提供者——main 层对 IConfigPathProvider 的实现

通过服务容器获取 ConfigService 以查找配置文件路径。
"""

from abc import ABC, abstractmethod

from battery_analysis.utils.config_utils import _get_custom_config_path


class IConfigPathProvider(ABC):
    """配置路径提供者接口——由 main 层实现，注入到首选项对话框中使用"""

    @abstractmethod
    def get_config_path(self) -> str:
        """返回当前配置文件路径，不可用时返回空字符串"""
        ...


class ConfigPathProvider(IConfigPathProvider):
    """从主层服务容器获取配置路径的适配器"""

    def get_config_path(self) -> str:
        # 优先查找自定义路径
        custom = _get_custom_config_path()
        if custom:
            return custom
        # 回退到 ConfigService
        from battery_analysis.main.services.service_container import get_service_container

        container = get_service_container()
        svc = container.get("config")
        if svc is None:
            return ""
        cfg_path = svc.find_config_file()
        return str(cfg_path) if cfg_path else ""
