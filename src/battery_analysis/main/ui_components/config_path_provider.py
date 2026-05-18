"""
配置路径提供者——main 层对 IConfigPathProvider 的实现

通过服务容器获取 ConfigService 以查找配置文件路径。
"""

from battery_analysis.i18n.config_dialog_interface import IConfigPathProvider


class ConfigPathProvider(IConfigPathProvider):
    """从主层服务容器获取配置路径的适配器"""

    def get_config_path(self) -> str:
        from battery_analysis.main.services.service_container import get_service_container
        container = get_service_container()
        svc = container.get("config")
        if svc is None:
            return ""
        cfg_path = svc.find_config_file()
        return str(cfg_path) if cfg_path else ""
