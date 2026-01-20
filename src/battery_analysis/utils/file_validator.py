# -*- coding: utf-8 -*-
"""
文件验证工具模块

提供文件和目录验证的公共功能
"""

import os
import logging
from typing import Tuple, Optional


class FileValidator:
    """
    文件验证器类
    提供文件和目录验证的公共功能
    """
    
    def __init__(self):
        """
        初始化文件验证器
        """
        self.logger = logging.getLogger(__name__)
    
    def validate_filename(self, filename: str) -> Tuple[bool, str]:
        """
        验证文件名的有效性
        
        Args:
            filename: 文件名
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # 验证文件名长度
        if len(filename) > 255:
            return False, f"文件名过长: {filename} 超过255个字符"
        
        # 验证文件名是否包含无效字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in filename:
                return False, f"文件名包含无效字符: {filename} 包含 '{char}'"
        
        # 验证文件名是否包含中文
        for char in filename:
            if '\u4e00' <= char <= '\u9fff':
                return False, f"文件名包含中文: {filename} 不允许包含中文字符"
        
        # 验证文件名是否为保留文件名
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        base_name = filename.split('.')[0].upper()
        if base_name in reserved_names:
            return False, f"文件名无效: {filename} 是保留文件名"
        
        return True, ""
    
    def validate_file_extension(self, filename: str, expected_extensions: list) -> Tuple[bool, str]:
        """
        验证文件扩展名的有效性
        
        Args:
            filename: 文件名
            expected_extensions: 期望的文件扩展名列表
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # 获取文件扩展名
        file_ext = os.path.splitext(filename)[1].lower()
        
        # 验证文件扩展名
        if file_ext not in expected_extensions:
            return False, f"文件格式错误: {filename} 不是有效的{', '.join(expected_extensions)}文件"
        
        return True, ""
    
    def validate_file_exists(self, file_path: str) -> Tuple[bool, str]:
        """
        验证文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not os.path.exists(file_path):
            return False, f"选择的文件不存在:\n{file_path}"
        
        return True, ""
    
    def validate_file_not_empty(self, file_path: str) -> Tuple[bool, str]:
        """
        验证文件是否为空
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if os.path.getsize(file_path) == 0:
            return False, f"文件为空: {os.path.basename(file_path)}"
        
        return True, ""
    
    def validate_directory_exists(self, directory_path: str) -> Tuple[bool, str]:
        """
        验证目录是否存在
        
        Args:
            directory_path: 目录路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not os.path.exists(directory_path):
            return False, f"目录不存在:\n{directory_path}"
        
        if not os.path.isdir(directory_path):
            return False, f"路径不是目录:\n{directory_path}"
        
        return True, ""
    
    def validate_directory_name(self, directory_name: str) -> Tuple[bool, str]:
        """
        验证目录名的有效性
        
        Args:
            directory_name: 目录名
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # 验证目录名长度
        if len(directory_name) > 255:
            return False, f"目录名过长: {directory_name} 超过255个字符"
        
        # 验证目录名是否包含无效字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in directory_name:
                return False, f"目录名包含无效字符: {directory_name} 包含 '{char}'"
        
        # 验证目录名是否包含中文
        for char in directory_name:
            if '\u4e00' <= char <= '\u9fff':
                return False, f"目录名包含中文: {directory_name} 不允许包含中文字符"
        
        # 验证目录名是否为保留文件名
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        if directory_name.upper() in reserved_names:
            return False, f"目录名无效: {directory_name} 是保留名称"
        
        return True, ""
    
    def validate_excel_filename(self, filename: str) -> Tuple[bool, str]:
        """
        验证Excel文件名的有效性
        
        Args:
            filename: 文件名
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # 验证文件扩展名
        is_valid, error_msg = self.validate_file_extension(filename, ['.xlsx'])
        if not is_valid:
            return is_valid, error_msg
        
        # 验证文件名
        is_valid, error_msg = self.validate_filename(filename)
        if not is_valid:
            return is_valid, error_msg
        
        # 验证文件名是否符合预期格式
        base_name = filename.replace('.xlsx', '')
        
        # 检查是否包含批次日期代码 (DC开头)
        if 'DC' not in base_name:
            return False, f"文件名格式错误: {filename} 缺少批次日期代码 (DC开头)"
        
        # 检查是否包含脉冲电流信息
        if 'mA' not in base_name:
            return False, f"文件名格式错误: {filename} 缺少电流信息 (mA)"
        
        # 检查是否包含必要的分隔符
        if ',' not in base_name:
            return False, f"文件名格式错误: {filename} 缺少必要的分隔符 (, )"
        
        # 检查是否包含温度信息（支持多种格式）
        has_temperature = False
        # 检查是否包含°C或C
        if '°C' in base_name or 'C' in base_name:
            has_temperature = True
        # 检查是否包含括号格式的温度信息
        elif '(' in base_name and ')' in base_name:
            has_temperature = True
        
        if not has_temperature:
            return False, f"文件名格式错误: {filename} 缺少温度信息"
        
        return True, ""
    
    def validate_xml_filename(self, filename: str) -> Tuple[bool, str]:
        """
        验证XML文件名的有效性
        
        Args:
            filename: 文件名
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # 验证文件扩展名
        is_valid, error_msg = self.validate_file_extension(filename, ['.xml'])
        if not is_valid:
            return is_valid, error_msg
        
        # 验证文件名
        is_valid, error_msg = self.validate_filename(filename)
        if not is_valid:
            return is_valid, error_msg
        
        return True, ""
    
    def validate_full_path(self, path: str) -> Tuple[bool, str]:
        """
        验证完整路径的有效性
        
        Args:
            path: 完整路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # 验证路径长度 (Windows限制为260字符)
        if len(path) > 260:
            return False, f"路径过长: {path} 超过260个字符"
        
        # 验证路径是否包含无效字符（允许Windows路径中的冒号和反斜杠）
        invalid_chars = '<>|?*'
        for char in invalid_chars:
            if char in path:
                return False, f"路径包含无效字符: {path} 包含 '{char}'"
        
        return True, ""
    
    def validate_path_length(self, path: str) -> Tuple[bool, str]:
        """
        验证路径长度
        
        Args:
            path: 路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # Windows路径长度限制
        if len(path) > 260:
            return False, f"路径过长: {path} 超过260个字符"
        
        return True, ""
    
    def validate_directory_structure(self, directory: str) -> Tuple[bool, str]:
        """
        验证目录结构
        
        Args:
            directory: 目录路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # 验证目录是否存在
        is_valid, error_msg = self.validate_directory_exists(directory)
        if not is_valid:
            return is_valid, error_msg
        
        # 验证目录名
        dir_name = os.path.basename(directory)
        is_valid, error_msg = self.validate_directory_name(dir_name)
        if not is_valid:
            return is_valid, error_msg
        
        return True, ""
    
    def validate_input_directory(self, directory: str) -> Tuple[bool, str]:
        """
        验证输入目录
        
        Args:
            directory: 输入目录路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # 验证目录结构
        is_valid, error_msg = self.validate_directory_structure(directory)
        if not is_valid:
            return is_valid, error_msg
        
        # 验证目录是否为2_xlsx
        if os.path.basename(directory) != "2_xlsx":
            return False, f"输入路径不是2_xlsx目录: {directory}"
        
        # 验证目录是否可读
        if not os.access(directory, os.R_OK):
            return False, f"无法读取目录: {directory}"
        
        return True, ""
    
    def validate_output_directory(self, directory: str) -> Tuple[bool, str]:
        """
        验证输出目录
        
        Args:
            directory: 输出目录路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # 验证路径长度
        is_valid, error_msg = self.validate_path_length(directory)
        if not is_valid:
            return is_valid, error_msg
        
        # 验证目录名
        dir_name = os.path.basename(directory)
        is_valid, error_msg = self.validate_directory_name(dir_name)
        if not is_valid:
            return is_valid, error_msg
        
        # 如果目录存在，验证是否为目录且可写
        if os.path.exists(directory):
            if not os.path.isdir(directory):
                return False, f"路径不是目录: {directory}"
            if not os.access(directory, os.W_OK):
                return False, f"无法写入目录: {directory}"
        else:
            # 如果目录不存在，验证父目录是否存在且可写
            parent_dir = os.path.dirname(directory)
            if parent_dir and not os.path.exists(parent_dir):
                return False, f"父目录不存在: {parent_dir}"
            if parent_dir and not os.access(parent_dir, os.W_OK):
                return False, f"无法在父目录中创建目录: {parent_dir}"
        
        return True, ""
    
    def validate_path_access(self, path: str, access_type: str = 'r') -> Tuple[bool, str]:
        """
        验证路径的访问权限
        
        Args:
            path: 路径
            access_type: 访问类型 ('r' 读, 'w' 写, 'x' 执行)
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not os.path.exists(path):
            return False, f"路径不存在: {path}"
        
        # 验证读权限
        if 'r' in access_type and not os.access(path, os.R_OK):
            return False, f"无法读取路径: {path}"
        
        # 验证写权限
        if 'w' in access_type and not os.access(path, os.W_OK):
            return False, f"无法写入路径: {path}"
        
        # 验证执行权限
        if 'x' in access_type and not os.access(path, os.X_OK):
            return False, f"无法执行路径: {path}"
        
        return True, ""
