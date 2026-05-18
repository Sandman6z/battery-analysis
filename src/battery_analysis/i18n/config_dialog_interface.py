"""
i18n 配置对话框接口

定义 i18n 包与 main 层之间的依赖反转接口，
消除 i18n 包对 main 层的直接依赖。
"""

from abc import ABC, abstractmethod


class IConfigPathProvider(ABC):
    """配置路径提供者接口——由 main 层实现，注入到 i18n 对话框中使用"""

    @abstractmethod
    def get_config_path(self) -> str:
        """返回当前配置文件路径，不可用时返回空字符串"""
        ...
