# -*- coding: utf-8 -*-
"""
可视化器接口定义

定义可视化器必须实现的接口方法，实现依赖倒置原则
"""

from abc import ABC, abstractmethod
from typing import Optional, Any


class IVisualizer(ABC):
    """
    可视化器接口
    
    定义了所有可视化器必须实现的方法
    """

    @abstractmethod
    def show_figure(self, data_path: Optional[str] = None) -> bool:
        """
        显示图表
        
        Args:
            data_path: 可选的数据路径
            
        Returns:
            bool: 是否成功显示
        """
        pass

    @abstractmethod
    def load_data(self, data_path: str) -> bool:
        """
        加载数据
        
        Args:
            data_path: 数据路径
            
        Returns:
            bool: 是否成功加载数据
        """
        pass

    @abstractmethod
    def clear_data(self) -> None:
        """
        清除所有数据，回到初始状态
        """
        pass

    @abstractmethod
    def is_data_loaded(self) -> bool:
        """
        检查是否有数据已加载
        
        Returns:
            bool: 是否已加载数据
        """
        pass

    @abstractmethod
    def get_status_info(self) -> dict:
        """
        获取状态信息
        
        Returns:
            dict: 状态信息字典
        """
        pass

    @abstractmethod
    def set_config(self, config: dict) -> None:
        """
        设置配置
        
        Args:
            config: 配置字典
        """
        pass

    @abstractmethod
    def get_config(self) -> dict:
        """
        获取当前配置
        
        Returns:
            dict: 当前配置字典
        """
        pass