# -*- coding: utf-8 -*-
"""
验证服务实现模块

提供数据验证相关的具体实现
"""

import os
import re
import logging
from typing import Any, Tuple, List, Dict

from battery_analysis.main.services.validation_service_interface import IValidationService


class ValidationService(IValidationService):
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
            error_msg = "测试信息不能为空"
            self.logger.error(error_msg)
            return False, error_msg
        
        # 检查必要字段
        required_fields = [
            (0, "项目名称"),
            (2, "电池类型"),
            (3, "标称容量"),
            (16, "软件版本")
        ]
        
        for index, field_name in required_fields:
            if index >= len(test_info) or not test_info[index]:
                error_msg = f"{field_name}不能为空"
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
        
        self.logger.info("测试信息验证通过")
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
            error_msg = "文件路径不能为空"
            self.logger.error(error_msg)
            return False, error_msg
        
        if not os.path.exists(file_path):
            error_msg = f"文件不存在: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg
        
        if not os.path.isfile(file_path):
            error_msg = f"路径不是文件: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg
        
        try:
            # 检查文件是否可访问
            with open(file_path, 'r', encoding='utf-8') as f:
                pass
        except (OSError, IOError) as e:
            error_msg = f"文件访问失败: {e}"
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
            error_msg = "目录路径不能为空"
            self.logger.error(error_msg)
            return False, error_msg
        
        if not os.path.exists(directory_path):
            error_msg = f"目录不存在: {directory_path}"
            self.logger.error(error_msg)
            return False, error_msg
        
        if not os.path.isdir(directory_path):
            error_msg = f"路径不是目录: {directory_path}"
            self.logger.error(error_msg)
            return False, error_msg
        
        try:
            # 检查目录是否可访问
            os.listdir(directory_path)
        except OSError as e:
            error_msg = f"目录访问失败: {e}"
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
            error_msg = f"无效的数字值: {value}"
            self.logger.error(error_msg)
            return False, error_msg
        
        if min_val is not None and num_value < min_val:
            error_msg = f"数值不能小于 {min_val}"
            self.logger.error(error_msg)
            return False, error_msg
        
        if max_val is not None and num_value > max_val:
            error_msg = f"数值不能大于 {max_val}"
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
            error_msg = "邮箱地址不能为空"
            self.logger.error(error_msg)
            return False, error_msg
        
        # 简单的邮箱格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            error_msg = f"无效的邮箱地址格式: {email}"
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
            error_msg = "电话号码不能为空"
            self.logger.error(error_msg)
            return False, error_msg
        
        # 简单的电话号码格式验证（支持中国手机号）
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            error_msg = f"无效的电话号码格式: {phone}"
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
            error_msg = "电池类型不能为空"
            self.logger.error(error_msg)
            return False, error_msg
        
        # 定义有效的电池类型
        valid_battery_types = [
            "磷酸铁锂", "三元锂", "钴酸锂", "锰酸锂", "钛酸锂",
            "镍氢", "镍镉", "铅酸", "锂离子", "锂聚合物"
        ]
        
        if battery_type not in valid_battery_types:
            error_msg = f"无效的电池类型: {battery_type}。有效类型包括: {', '.join(valid_battery_types)}"
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
            error_msg = "容量值不能为空"
            self.logger.error(error_msg)
            return False, error_msg
        
        # 验证是否为有效的数值
        return self.validate_numeric_value(capacity, min_val=0.1, max_val=10000)