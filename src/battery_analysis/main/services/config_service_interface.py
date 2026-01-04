# -*- coding: utf-8 -*-
"""
配置服务接口模块

定义配置相关的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path


class IConfigService(ABC):
    """
    配置服务接口
    提供配置文件读取、写入和管理功能
    """
    
    @abstractmethod
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，格式为"section/key"或"key"
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        pass
    
    @abstractmethod
    def set_config_value(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            bool: 设置是否成功
        """
        pass
    
    @abstractmethod
    def save_config(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def load_config(self, config_path: Optional[str] = None) -> bool:
        """
        从文件加载配置
        
        Args:
            config_path: 配置文件路径，None表示使用默认路径
            
        Returns:
            bool: 加载是否成功
        """
        pass
    
    @abstractmethod
    def get_config_sections(self) -> List[str]:
        """
        获取所有配置节名称
        
        Returns:
            List[str]: 配置节名称列表
        """
        pass
    
    @abstractmethod
    def get_section_config(self, section: str) -> Dict[str, Any]:
        """
        获取指定配置节的所有键值对
        
        Args:
            section: 配置节名称
            
        Returns:
            Dict[str, Any]: 配置节内容
        """
        pass
    
    @abstractmethod
    def has_config_key(self, key: str) -> bool:
        """
        检查配置键是否存在
        
        Args:
            key: 配置键
            
        Returns:
            bool: 键是否存在
        """
        pass
    
    @abstractmethod
    def find_config_file(self, file_name: str = "setting.ini") -> Optional[Path]:
        """
        查找配置文件路径
        
        Args:
            file_name: 配置文件名称
            
        Returns:
            Optional[Path]: 配置文件路径，如果未找到则返回None
        """
        pass
