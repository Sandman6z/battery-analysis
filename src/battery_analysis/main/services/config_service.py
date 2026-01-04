# -*- coding: utf-8 -*-
"""
配置服务实现模块

提供配置文件读取、写入和管理功能的实现
"""

import logging
import configparser
from pathlib import Path
from typing import Dict, Any, Optional, List
from battery_analysis.main.services.config_service_interface import IConfigService


class ConfigService(IConfigService):
    """
    配置服务实现类
    提供配置文件读取、写入和管理功能
    """
    
    def __init__(self):
        """
        初始化配置服务
        """
        self.logger = logging.getLogger(__name__)
        self._config = configparser.ConfigParser()
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
            # 确保配置已加载
            if not self._loaded:
                self.load_config()
            
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
                self.logger.warning("配置键 '%s' 不存在，返回默认值: %s", key, default)
                return default
                
        except Exception as e:
            self.logger.error("获取配置值失败: %s", e)
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
            
            self.logger.debug("设置配置: %s = %s", key, value)
            return True
            
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
                # 确保目录存在
                self._config_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 写入文件
                with open(self._config_path, 'w', encoding='utf-8') as f:
                    self._config.write(f)
                
                self.logger.info("配置已保存到: %s", self._config_path)
                return True
            else:
                self.logger.warning("无法保存配置：未指定配置路径或配置未加载")
                return False
                
        except Exception as e:
            self.logger.error("保存配置失败: %s", e)
            return False
    
    def load_config(self, config_path: Optional[str] = None) -> bool:
        """
        从文件加载配置
        
        Args:
            config_path: 配置文件路径，None表示使用默认路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            # 查找配置文件路径
            if config_path:
                self._config_path = Path(config_path)
            else:
                self._config_path = self.find_config_file()
            
            if not self._config_path or not self._config_path.exists():
                self.logger.warning("配置文件不存在: %s", self._config_path)
                self._loaded = False
                return False
            
            # 清空当前配置
            self._config.clear()
            
            # 读取配置文件
            self._config.read(self._config_path, encoding='utf-8')
            
            self._loaded = True
            self.logger.info("配置已加载: %s", self._config_path)
            return True
            
        except Exception as e:
            self.logger.error("加载配置失败: %s", e)
            self._loaded = False
            return False
    
    def get_config_sections(self) -> List[str]:
        """
        获取所有配置节名称
        
        Returns:
            List[str]: 配置节名称列表
        """
        try:
            if not self._loaded:
                self.load_config()
            return self._config.sections()
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
            
            if not self._config.has_section(section):
                return []
            
            return self._config.options(section)
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
            
            if not self._config.has_section(section):
                return {}
            
            return dict(self._config.items(section))
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
            
            # 解析键
            if '/' in key:
                section, option = key.split('/', 1)
            else:
                section = 'DEFAULT'
                option = key
            
            return self._config.has_section(section) and self._config.has_option(section, option)
        except Exception as e:
            self.logger.error("检查配置键失败: %s", e)
            return False
    
    def find_config_file(self, file_name: str = "setting.ini") -> Optional[Path]:
        """
        查找配置文件路径
        
        Args:
            file_name: 配置文件名称
            
        Returns:
            Optional[Path]: 配置文件路径，如果未找到则返回None
        """
        try:
            from battery_analysis.utils.config_utils import find_config_file
            result = find_config_file(file_name)
            return Path(result) if result else None
        except Exception as e:
            self.logger.error("查找配置文件失败: %s", e)
            return None
    
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