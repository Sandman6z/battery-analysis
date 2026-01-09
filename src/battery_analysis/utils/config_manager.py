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
    """
    
    def __init__(self):
        """
        初始化配置管理器
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._config = configparser.ConfigParser()
    
    def read_config(self, config_path: str) -> bool:
        """
        读取配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            bool: 是否读取成功
        """
        try:
            self._config.read(config_path, encoding='utf-8')
            self.logger.info(f"配置文件读取成功: {config_path}")
            return True
        except (configparser.Error, IOError, OSError, UnicodeDecodeError) as e:
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
            # 确保目录存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                self._config.write(f)
            self.logger.info(f"配置文件写入成功: {config_path}")
            return True
        except (configparser.Error, IOError, OSError, UnicodeEncodeError) as e:
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
            # 解析键
            if '/' in key:
                section, option = key.split('/', 1)
            else:
                section = 'DEFAULT'
                option = key
            
            # 获取值
            if self._config.has_section(section) and self._config.has_option(section, option):
                value = self._config.get(section, option)
                
                # 尝试转换数据类型
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
            # 解析键
            if '/' in key:
                section, option = key.split('/', 1)
            else:
                section = 'DEFAULT'
                option = key
            
            # 确保配置节存在
            if not self._config.has_section(section):
                self._config.add_section(section)
            
            # 转换值为字符串
            str_value = str(value)
            
            # 设置值
            self._config.set(section, option, str_value)
            
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
            # 解析键
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
    
    def _is_float(self, value: str) -> bool:
        """
        检查字符串是否可以转换为浮点数
        
        Args:
            value: 要检查的字符串
            
        Returns:
            bool: 是否可以转换为浮点数
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
