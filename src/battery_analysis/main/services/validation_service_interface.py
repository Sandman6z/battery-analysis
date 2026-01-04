# -*- coding: utf-8 -*-
"""
验证服务接口模块

提供数据验证相关的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Any, Tuple, List, Dict


class IValidationService(ABC):
    """
    验证服务接口
    提供各种数据验证功能
    """
    
    @abstractmethod
    def validate_test_info(self, test_info: List[str]) -> Tuple[bool, str]:
        """
        验证测试信息的完整性和有效性
        
        Args:
            test_info: 测试信息列表
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass
    
    @abstractmethod
    def validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        """
        验证文件路径的有效性
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass
    
    @abstractmethod
    def validate_directory_path(self, directory_path: str) -> Tuple[bool, str]:
        """
        验证目录路径的有效性
        
        Args:
            directory_path: 目录路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass
    
    @abstractmethod
    def validate_numeric_value(self, value: Any, min_val: float = None, max_val: float = None) -> Tuple[bool, str]:
        """
        验证数值是否在有效范围内
        
        Args:
            value: 要验证的值
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass
    
    @abstractmethod
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """
        验证邮箱地址格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass
    
    @abstractmethod
    def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """
        验证电话号码格式
        
        Args:
            phone: 电话号码
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass
    
    @abstractmethod
    def validate_battery_type(self, battery_type: str) -> Tuple[bool, str]:
        """
        验证电池类型是否有效
        
        Args:
            battery_type: 电池类型
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass
    
    @abstractmethod
    def validate_capacity_value(self, capacity: str) -> Tuple[bool, str]:
        """
        验证容量值是否有效
        
        Args:
            capacity: 容量值
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass
