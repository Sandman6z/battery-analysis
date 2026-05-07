# -*- coding: utf-8 -*-
"""
配置管理工具类
提供统一的配置文件读取、解析、管理功能
"""

import configparser
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging


class ConfigManager:
    """
    配置管理工具类
    提供统一的配置文件读取、解析、管理功能

    支持基于文件修改时间的缓存，避免重复读取未变更的文件。
    """

    def __init__(self):
        """
        初始化配置管理器
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._config = configparser.ConfigParser(interpolation=None)
        # 保留选项名称的原始大小写（写入 INI 文件时可保持原样）
        self._config.optionxform = str
        # 文件修改时间缓存，用于跳过未变更文件的重复读取
        self._cache_mtime: Dict[str, float] = {}
        # 缓存全量解析结果 (section -> {key: value})
        self._cache_data: Dict[str, Dict[str, Dict[str, str]]] = {}

    def read_config(self, config_path: str, use_cache: bool = True) -> bool:
        """
        读取配置文件，支持基于 mtime 的缓存

        Args:
            config_path: 配置文件路径
            use_cache: 是否使用缓存（仅当文件未修改时跳过读取）

        Returns:
            bool: 是否读取成功
        """
        try:
            path = Path(config_path)
            if not path.exists():
                self.logger.warning(f"配置文件不存在: {config_path}")
                return False

            current_mtime = path.stat().st_mtime

            # 如果文件未修改且缓存命中，跳过真正读取
            if (use_cache
                    and config_path in self._cache_mtime
                    and self._cache_mtime[config_path] == current_mtime):
                self.logger.debug(f"配置文件未变更，使用缓存: {config_path}")
                return True

            self._config.read(config_path, encoding='utf-8')

            # 更新缓存
            self._cache_mtime[config_path] = current_mtime
            data = {}
            for section in self._config.sections():
                data[section] = dict(self._config.items(section))
            if self._config.defaults():
                data['DEFAULT'] = dict(self._config.defaults())
            self._cache_data[config_path] = data

            self.logger.info(f"配置文件读取成功: {config_path}")
            return True
        except (configparser.Error, IOError, OSError, UnicodeDecodeError, PermissionError) as e:
            self.logger.error(f"配置文件读取失败: {str(e)}")
            return False

    def write_config(self, config_path: str) -> bool:
        """
        写入配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            bool: 是否写入成功
        """
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                self._config.write(f)

            # 写入后清除该文件的缓存，下次读取会重新加载
            self._cache_mtime.pop(str(config_path), None)
            self._cache_data.pop(str(config_path), None)

            self.logger.info(f"配置文件写入成功: {config_path}")
            return True
        except (configparser.Error, IOError, OSError, UnicodeEncodeError, PermissionError) as e:
            self.logger.error(f"配置文件写入失败: {str(e)}")
            return False

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，格式为"section/key"或"key"
            default: 默认值

        Returns:
            Any: 配置值
        """
        try:
            if '/' in key:
                section, option = key.split('/', 1)
            else:
                section = 'DEFAULT'
                option = key

            if self._config.has_section(section) and self._config.has_option(section, option):
                value = self._config.get(section, option)

                if value.lower() in ('true', 'false'):
                    return value.lower() == 'true'
                elif value.isdigit():
                    return int(value)
                elif self._is_float(value):
                    return float(value)
                else:
                    return value
            else:
                return default

        except (configparser.Error, ValueError, TypeError, IndexError) as e:
            self.logger.error(f"获取配置值失败: {str(e)}")
            return default

    def get_value_raw(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取配置值的原始字符串，不做类型转换

        Args:
            key: 配置键，格式为"section/key"或"key"
            default: 默认值

        Returns:
            Optional[str]: 原始字符串值
        """
        try:
            if '/' in key:
                section, option = key.split('/', 1)
            else:
                section = 'DEFAULT'
                option = key

            if self._config.has_section(section) and self._config.has_option(section, option):
                return self._config.get(section, option)
            return default
        except (configparser.Error, ValueError, TypeError, IndexError) as e:
            self.logger.error(f"获取原始配置值失败: {str(e)}")
            return default

    def set_value(self, key: str, value: Any) -> bool:
        """
        设置配置值

        Args:
            key: 配置键
            value: 配置值

        Returns:
            bool: 设置是否成功
        """
        try:
            if '/' in key:
                section, option = key.split('/', 1)
            else:
                section = 'DEFAULT'
                option = key

            if not self._config.has_section(section):
                self._config.add_section(section)

            self._config.set(section, option, str(value))

            return True

        except (configparser.Error, TypeError, ValueError) as e:
            self.logger.error(f"设置配置值失败: {str(e)}")
            return False

    def has_key(self, key: str) -> bool:
        """
        检查配置键是否存在

        Args:
            key: 配置键

        Returns:
            bool: 键是否存在
        """
        try:
            if '/' in key:
                section, option = key.split('/', 1)
            else:
                section = 'DEFAULT'
                option = key

            return self._config.has_section(section) and self._config.has_option(section, option)
        except (configparser.Error, ValueError, TypeError, IndexError) as e:
            self.logger.error(f"检查配置键失败: {str(e)}")
            return False

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取指定配置节的所有键值对

        Args:
            section: 配置节名称

        Returns:
            Dict[str, Any]: 配置节内容
        """
        try:
            if not self._config.has_section(section):
                return {}

            return dict(self._config.items(section))
        except (configparser.Error, ValueError, TypeError) as e:
            self.logger.error(f"获取配置节失败: {str(e)}")
            return {}

    def get_sections(self) -> List[str]:
        """
        获取所有配置节名称

        Returns:
            List[str]: 配置节名称列表
        """
        try:
            return self._config.sections()
        except (configparser.Error, ValueError, TypeError) as e:
            self.logger.error(f"获取配置节列表失败: {str(e)}")
            return []

    def get_all_values(self) -> Dict[str, Dict[str, str]]:
        """
        获取所有配置节及其键值对（不包含 DEFAULT 节）

        Returns:
            Dict[str, Dict[str, str]]: {section_name: {key: value}}
        """
        result = {}
        for section in self._config.sections():
            result[section] = dict(self._config.items(section))
        return result

    def clear_cache(self, config_path: Optional[str] = None) -> None:
        """
        清除配置缓存

        Args:
            config_path: 指定文件路径则清除该文件缓存，None 则清除所有
        """
        if config_path:
            self._cache_mtime.pop(config_path, None)
            self._cache_data.pop(config_path, None)
        else:
            self._cache_mtime.clear()
            self._cache_data.clear()

    def _is_float(self, value: str) -> bool:
        """
        检查字符串是否可以转换为浮点数
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
