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

    @staticmethod
    def _validate_name(name: str, label: str) -> Tuple[bool, str]:
        """验证名称（文件/目录）的基本规则：长度、无效字符、中文、保留名"""
        if len(name) > 255:
            return False, f"{label}名过长: {name} 超过255个字符"
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in name:
                return False, f"{label}名包含无效字符: {name} 包含 '{char}'"
        for char in name:
            if '一' <= char <= '鿿':
                return False, f"{label}名包含中文: {name} 不允许包含中文字符"
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                          'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                          'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        base_name = name.split('.')[0].upper()
        if base_name in reserved_names:
            return False, f"{label}名无效: {name} 是保留名称"
        return True, ""

    def validate_filename(self, filename: str) -> Tuple[bool, str]:
        """验证文件名的有效性"""
        return self._validate_name(filename, "文件")

    def validate_file_extension(self, filename: str, expected_extensions: list) -> Tuple[bool, str]:
        """
        验证文件扩展名的有效性

        Args:
            filename: 文件名
            expected_extensions: 期望的文件扩展名列表

        Returns:
            tuple: (是否有效, 错误消息)
        """
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in expected_extensions:
            return False, f"文件格式错误: {filename} 不是有效的{', '.join(expected_extensions)}文件"
        return True, ""

    def validate_file_exists(self, file_path: str) -> Tuple[bool, str]:
        """验证文件是否存在"""
        if not os.path.exists(file_path):
            return False, f"选择的文件不存在:\n{file_path}"
        return True, ""

    def validate_file_not_empty(self, file_path: str) -> Tuple[bool, str]:
        """验证文件是否为空"""
        if os.path.getsize(file_path) == 0:
            return False, f"文件为空: {os.path.basename(file_path)}"
        return True, ""

    def validate_directory_exists(self, directory_path: str) -> Tuple[bool, str]:
        """验证目录是否存在"""
        if not os.path.exists(directory_path):
            return False, f"目录不存在:\n{directory_path}"
        if not os.path.isdir(directory_path):
            return False, f"路径不是目录:\n{directory_path}"
        return True, ""

    def validate_directory_name(self, directory_name: str) -> Tuple[bool, str]:
        """验证目录名的有效性"""
        return self._validate_name(directory_name, "目录")

    def validate_excel_filename(self, filename: str) -> Tuple[bool, str]:
        """
        验证Excel文件名的有效性

        Args:
            filename: 文件名

        Returns:
            tuple: (是否有效, 错误消息)
        """
        is_valid, error_msg = self.validate_file_extension(filename, ['.xlsx'])
        if not is_valid:
            return is_valid, error_msg
        is_valid, error_msg = self.validate_filename(filename)
        if not is_valid:
            return is_valid, error_msg

        base_name = filename.replace('.xlsx', '')
        if 'DC' not in base_name:
            return False, f"文件名格式错误: {filename} 缺少批次日期代码 (DC开头)"
        if 'mA' not in base_name:
            return False, f"文件名格式错误: {filename} 缺少电流信息 (mA)"
        if ',' not in base_name:
            return False, f"文件名格式错误: {filename} 缺少必要的分隔符 (, )"

        has_temperature = False
        if '°C' in base_name or 'C' in base_name:
            has_temperature = True
        elif '(' in base_name and ')' in base_name:
            has_temperature = True
        if not has_temperature:
            return False, f"文件名格式错误: {filename} 缺少温度信息"

        return True, ""

    def validate_xml_filename(self, filename: str) -> Tuple[bool, str]:
        """验证XML文件名的有效性"""
        is_valid, error_msg = self.validate_file_extension(filename, ['.xml'])
        if not is_valid:
            return is_valid, error_msg
        return self.validate_filename(filename)

    def validate_full_path(self, path: str) -> Tuple[bool, str]:
        """验证完整路径的有效性"""
        if len(path) > 260:
            return False, f"路径过长: {path} 超过260个字符"
        invalid_chars = '<>|?*'
        for char in invalid_chars:
            if char in path:
                return False, f"路径包含无效字符: {path} 包含 '{char}'"
        return True, ""

    def validate_path_length(self, path: str) -> Tuple[bool, str]:
        """验证路径长度"""
        if len(path) > 260:
            return False, f"路径过长: {path} 超过260个字符"
        return True, ""

    def validate_directory_structure(self, directory: str) -> Tuple[bool, str]:
        """验证目录结构"""
        is_valid, error_msg = self.validate_directory_exists(directory)
        if not is_valid:
            return is_valid, error_msg
        dir_name = os.path.basename(directory)
        return self.validate_directory_name(dir_name)

    def validate_input_directory(self, directory: str) -> Tuple[bool, str]:
        """验证输入目录"""
        is_valid, error_msg = self.validate_directory_structure(directory)
        if not is_valid:
            return is_valid, error_msg
        if os.path.basename(directory) != "2_xlsx":
            return False, f"输入路径不是2_xlsx目录: {directory}"
        if not os.access(directory, os.R_OK):
            return False, f"无法读取目录: {directory}"
        return True, ""

    def validate_output_directory(self, directory: str) -> Tuple[bool, str]:
        """验证输出目录"""
        is_valid, error_msg = self.validate_path_length(directory)
        if not is_valid:
            return is_valid, error_msg
        dir_name = os.path.basename(directory)
        is_valid, error_msg = self.validate_directory_name(dir_name)
        if not is_valid:
            return is_valid, error_msg
        if os.path.exists(directory):
            if not os.path.isdir(directory):
                return False, f"路径不是目录: {directory}"
            if not os.access(directory, os.W_OK):
                return False, f"无法写入目录: {directory}"
        else:
            parent_dir = os.path.dirname(directory)
            if parent_dir and not os.path.exists(parent_dir):
                return False, f"父目录不存在: {parent_dir}"
            if parent_dir and not os.access(parent_dir, os.W_OK):
                return False, f"无法在父目录中创建目录: {parent_dir}"
        return True, ""

    def validate_path_access(self, path: str, access_type: str = 'r') -> Tuple[bool, str]:
        """验证路径的访问权限"""
        if not os.path.exists(path):
            return False, f"路径不存在: {path}"
        if 'r' in access_type and not os.access(path, os.R_OK):
            return False, f"无法读取路径: {path}"
        if 'w' in access_type and not os.access(path, os.W_OK):
            return False, f"无法写入路径: {path}"
        if 'x' in access_type and not os.access(path, os.X_OK):
            return False, f"无法执行路径: {path}"
        return True, ""
