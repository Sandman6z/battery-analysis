# -*- coding: utf-8 -*-
"""
验证服务实现模块

提供数据验证相关的具体实现
"""

import os
import re
import logging
from typing import Any, Tuple, List, Dict



class ValidationService:
    """
    验证服务实现类
    提供各种数据验证功能
    """
    
    def __init__(self):
        """
        初始化验证服务
        """
        self.logger = logging.getLogger(__name__)
    
    def validate_test_info(self, test_info: List[str]) -> Tuple[bool, str]:
        """
        验证测试信息的完整性和有效性
        
        Args:
            test_info: 测试信息列表
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not test_info:
            error_msg = "Test information cannot be empty"
            self.logger.error(error_msg)
            return False, error_msg
        
        # 检查必要字段
        required_fields = [
            (0, "Project Name"),
            (2, "Battery Type"),
            (3, "Rated Capacity"),
            (16, "Software Version")
        ]
        
        for index, field_name in required_fields:
            if index >= len(test_info) or not test_info[index]:
                error_msg = f"{field_name} cannot be empty"
                self.logger.error(error_msg)
                return False, error_msg
        
        # 验证电池类型
        battery_type = test_info[2]
        is_valid, error_msg = self.validate_battery_type(battery_type)
        if not is_valid:
            return False, error_msg
        
        # 验证容量值
        capacity = test_info[3]
        is_valid, error_msg = self.validate_capacity_value(capacity)
        if not is_valid:
            return False, error_msg
        
        self.logger.info("Test information validation passed")
        return True, ""
    
    def validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        """
        验证文件路径的有效性
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not file_path:
            error_msg = "File path cannot be empty"
            self.logger.error(error_msg)
            return False, error_msg
        
        if not os.path.exists(file_path):
            error_msg = f"File does not exist: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg
        
        if not os.path.isfile(file_path):
            error_msg = f"Path is not a file: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg
        
        try:
            # 检查文件是否可访问
            with open(file_path, 'r', encoding='utf-8') as f:
                pass
        except (OSError, IOError) as e:
            error_msg = f"File access failed: {e}"
            self.logger.error(error_msg)
            return False, error_msg
        
        return True, ""
    
    def validate_directory_path(self, directory_path: str) -> Tuple[bool, str]:
        """
        验证目录路径的有效性
        
        Args:
            directory_path: 目录路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not directory_path:
            error_msg = "Directory path cannot be empty"
            self.logger.error(error_msg)
            return False, error_msg
        
        if not os.path.exists(directory_path):
            error_msg = f"Directory does not exist: {directory_path}"
            self.logger.error(error_msg)
            return False, error_msg
        
        if not os.path.isdir(directory_path):
            error_msg = f"Path is not a directory: {directory_path}"
            self.logger.error(error_msg)
            return False, error_msg
        
        try:
            # 检查目录是否可访问
            os.listdir(directory_path)
        except OSError as e:
            error_msg = f"Directory access failed: {e}"
            self.logger.error(error_msg)
            return False, error_msg
        
        return True, ""
    
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
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            error_msg = f"Invalid numeric value: {value}"
            self.logger.error(error_msg)
            return False, error_msg
        
        if min_val is not None and num_value < min_val:
            error_msg = f"Value cannot be less than {min_val}"
            self.logger.error(error_msg)
            return False, error_msg
        
        if max_val is not None and num_value > max_val:
            error_msg = f"Value cannot be greater than {max_val}"
            self.logger.error(error_msg)
            return False, error_msg
        
        return True, ""
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """
        验证邮箱地址格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not email:
            error_msg = "Email address cannot be empty"
            self.logger.error(error_msg)
            return False, error_msg
        
        # 简单的邮箱格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            error_msg = f"Invalid email address format: {email}"
            self.logger.error(error_msg)
            return False, error_msg
        
        return True, ""
    
    def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """
        验证电话号码格式
        
        Args:
            phone: 电话号码
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not phone:
            error_msg = "Phone number cannot be empty"
            self.logger.error(error_msg)
            return False, error_msg
        
        # 简单的电话号码格式验证（支持中国手机号）
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            error_msg = f"Invalid phone number format: {phone}"
            self.logger.error(error_msg)
            return False, error_msg
        
        return True, ""
    
    def validate_battery_type(self, battery_type: str) -> Tuple[bool, str]:
        """
        验证电池类型是否有效
        
        Args:
            battery_type: 电池类型
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not battery_type:
            error_msg = "Battery type cannot be empty"
            self.logger.error(error_msg)
            return False, error_msg
        
        # 定义有效的电池类型
        valid_battery_types = [
            "磷酸铁锂", "三元锂", "钴酸锂", "锰酸锂", "钛酸锂",
            "镍氢", "镍镉", "铅酸", "锂离子", "锂聚合物"
        ]
        
        if battery_type not in valid_battery_types:
            error_msg = f"Invalid battery type: {battery_type}. Valid types include: {', '.join(valid_battery_types)}"
            self.logger.error(error_msg)
            return False, error_msg
        
        return True, ""
    
    def validate_capacity_value(self, capacity: str) -> Tuple[bool, str]:
        """
        验证容量值是否有效
        
        Args:
            capacity: 容量值
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not capacity:
            error_msg = "Capacity value cannot be empty"
            self.logger.error(error_msg)
            return False, error_msg
        
        # 验证是否为有效的数值
        return self.validate_numeric_value(capacity, min_val=0.1, max_val=10000)
