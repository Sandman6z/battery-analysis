# -*- coding: utf-8 -*-
"""
配置服务实现模块

提供配置文件读取、写入和管理功能的实现
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from battery_analysis.main.services.config_service_interface import IConfigService
from battery_analysis.utils.base_service import BaseService
from battery_analysis.utils.config_manager import ConfigManager


class ConfigService(BaseService, IConfigService):
    """
    配置服务实现类
    提供配置文件读取、写入和管理功能

    作为系统内配置文件(setting.ini)的唯一入口，所有模块均应通过此服务读取配置。
    """

    def __init__(self):
        """
        初始化配置服务
        """
        BaseService.__init__(self)
        self._config_manager = ConfigManager()
        self._config_path = None
        self._loaded = False

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，格式为"section/key"或"key"
            default: 默认值

        Returns:
            Any: 配置值
        """
        try:
            if not self._loaded:
                self.load_config()

            return self._config_manager.get_value(key, default)

        except Exception as e:
            self.logger.error("获取配置值失败: %s", e)
            return default

    def get_config_value_raw(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取配置值的原始字符串（不做类型转换）

        Args:
            key: 配置键，格式为"section/key"或"key"
            default: 默认值

        Returns:
            Optional[str]: 原始字符串值
        """
        try:
            if not self._loaded:
                self.load_config()
            return self._config_manager.get_value_raw(key, default)
        except Exception as e:
            self.logger.error("获取原始配置值失败: %s", e)
            return default

    def set_config_value(self, key: str, value: Any) -> bool:
        """
        设置配置值

        Args:
            key: 配置键
            value: 配置值

        Returns:
            bool: 设置是否成功
        """
        try:
            return self._config_manager.set_value(key, value)

        except Exception as e:
            self.logger.error("设置配置值失败: %s", e)
            return False

    def save_config(self) -> bool:
        """
        保存配置到文件

        Returns:
            bool: 保存是否成功
        """
        try:
            if self._config_path and self._loaded:
                success = self._config_manager.write_config(str(self._config_path))
                if success:
                    self.logger.info("配置已保存到: %s", self._config_path)
                return success
            else:
                self.logger.warning("无法保存配置：未指定配置路径或配置未加载")
                return False

        except Exception as e:
            self.logger.error("保存配置失败: %s", e)
            return False

    def load_config(self, config_path: Optional[str] = None, use_cache: bool = True) -> bool:
        """
        从文件加载配置

        Args:
            config_path: 配置文件路径，None表示使用默认路径
            use_cache: 是否使用缓存（仅当文件未修改时跳过重读）

        Returns:
            bool: 加载是否成功
        """
        try:
            if config_path:
                self._config_path = Path(config_path)
            else:
                self._config_path = self.find_config_file()

            if not self._config_path or not self._config_path.exists():
                self.logger.warning("配置文件不存在: %s", self._config_path)
                self._loaded = False
                return False

            success = self._config_manager.read_config(str(self._config_path), use_cache=use_cache)
            if success:
                self._loaded = True
                self.logger.info("配置已加载: %s", self._config_path)
            else:
                self._loaded = False

            return success

        except Exception as e:
            self.logger.error("加载配置失败: %s", e)
            self._loaded = False
            return False

    def reload_config(self) -> bool:
        """
        重新加载配置（清除缓存后强制重读）

        Returns:
            bool: 加载是否成功
        """
        self.clear_cache()
        self._loaded = False
        return self.load_config(use_cache=False)

    def clear_cache(self) -> None:
        """
        清除内部配置缓存
        当配置文件可能已变更时调用
        """
        self._config_manager.clear_cache()

    def get_config_sections(self) -> List[str]:
        """
        获取所有配置节名称

        Returns:
            List[str]: 配置节名称列表
        """
        try:
            if not self._loaded:
                self.load_config()
            return self._config_manager.get_sections()
        except Exception as e:
            self.logger.error("获取配置节失败: %s", e)
            return []

    def get_all_sections(self) -> List[str]:
        """
        获取所有配置节名称（别名方法）

        Returns:
            List[str]: 配置节名称列表
        """
        return self.get_config_sections()

    def get_all_values(self) -> Dict[str, Dict[str, str]]:
        """
        获取所有配置节及其键值对

        Returns:
            Dict[str, Dict[str, str]]: {section: {key: value}}
        """
        try:
            if not self._loaded:
                self.load_config()
            return self._config_manager.get_all_values()
        except Exception as e:
            self.logger.error("获取全部配置值失败: %s", e)
            return {}

    def get_section_options(self, section: str) -> List[str]:
        """
        获取指定配置节的所有选项名称

        Args:
            section: 配置节名称

        Returns:
            List[str]: 选项名称列表
        """
        try:
            if not self._loaded:
                self.load_config()

            section_config = self._config_manager.get_section(section)
            return list(section_config.keys())
        except Exception as e:
            self.logger.error("获取配置节选项失败: %s", e)
            return []

    def get_section_config(self, section: str) -> Dict[str, Any]:
        """
        获取指定配置节的所有键值对

        Args:
            section: 配置节名称

        Returns:
            Dict[str, Any]: 配置节内容
        """
        try:
            if not self._loaded:
                self.load_config()

            return self._config_manager.get_section(section)
        except Exception as e:
            self.logger.error("获取配置节失败: %s", e)
            return {}

    def has_config_key(self, key: str) -> bool:
        """
        检查配置键是否存在

        Args:
            key: 配置键

        Returns:
            bool: 键是否存在
        """
        try:
            if not self._loaded:
                self.load_config()

            return self._config_manager.has_key(key)
        except Exception as e:
            self.logger.error("检查配置键失败: %s", e)
            return False

    def find_config_file(self, file_name: str = "setting.ini", use_cache: bool = False) -> Optional[Path]:
        """
        查找配置文件路径

        Args:
            file_name: 配置文件名称
            use_cache: 是否使用缓存的配置文件路径，默认为False

        Returns:
            Optional[Path]: 配置文件路径，如果未找到则返回None
        """
        try:
            from battery_analysis.utils.config_utils import find_config_file
            result = find_config_file(file_name, use_cache=use_cache)
            return Path(result) if result else None
        except (ImportError, ValueError, TypeError, OSError) as e:
            self.logger.error("查找配置文件失败: %s", e)
            return None
