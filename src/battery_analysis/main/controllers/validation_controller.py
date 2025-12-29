# -*- coding: utf-8 -*-
"""
验证控制器模块
负责处理输入验证相关的业务逻辑
"""
import os
import re
from PyQt6 import QtCore as QC


class ValidationController(QC.QObject):
    """
    验证控制器类
    负责各种输入验证和数据校验
    """
    # 定义信号
    validation_error = QC.pyqtSignal(str)  # 验证错误信号
    validation_success = QC.pyqtSignal()  # 验证成功信号

    def __init__(self):
        """
        初始化验证控制器
        """
        super().__init__()
        
        # 获取服务容器
        from battery_analysis.main.services.service_container import get_service_container
        self.service_container = get_service_container()
        
        # 获取验证服务
        self.validation_service = self.service_container.get("validation")

    def validate_test_info(self, test_info):
        """
        验证测试信息的完整性和有效性

        Args:
            test_info: 测试信息列表

        Returns:
            tuple: (是否有效, 错误消息)
        """
        if self.validation_service:
            # 使用验证服务
            is_valid, error_msg = self.validation_service.validate_test_info(test_info)
            if not is_valid:
                self.validation_error.emit(error_msg)
            else:
                self.validation_success.emit()
            return is_valid, error_msg
        else:
            # 降级到原来的逻辑
            error_msg = "验证服务不可用"
            self.validation_error.emit(error_msg)
            return False, error_msg

    def validate_input_data(self, input_path):
        """
        验证输入数据的有效性

        Args:
            input_path: 输入数据路径

        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not input_path:
            error_msg = "输入数据路径不能为空"
            self.validation_error.emit(error_msg)
            return False, error_msg

        # 使用验证服务验证目录路径
        if self.validation_service:
            is_valid, error_msg = self.validation_service.validate_directory_path(input_path)
            if not is_valid:
                self.validation_error.emit(error_msg)
                return False, error_msg
        else:
            # 降级逻辑
            if not os.path.exists(input_path):
                error_msg = f"输入数据路径不存在: {input_path}"
                self.validation_error.emit(error_msg)
                return False, error_msg

            if not os.path.isdir(input_path):
                error_msg = f"输入数据路径必须是目录: {input_path}"
                self.validation_error.emit(error_msg)
                return False, error_msg

        # 检查目录中是否包含必要的文件
        try:
            files = os.listdir(input_path)
            # 检查是否至少有一个xlsx或csv文件
            has_data_file = any(file.endswith('.xlsx')
                                or file.endswith('.csv') for file in files)
            if not has_data_file:
                error_msg = f"输入目录中未找到数据文件(.xlsx或.csv)"
                self.validation_error.emit(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"读取输入目录失败: {e}"
            self.validation_error.emit(error_msg)
            return False, error_msg

        self.validation_success.emit()
        return True, ""

    def validate_output_path(self, output_path):
        """
        验证输出路径的有效性

        Args:
            output_path: 输出路径

        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not output_path:
            error_msg = "输出路径不能为空"
            self.validation_error.emit(error_msg)
            return False, error_msg

        # 检查输出目录是否可写
        try:
            # 如果目录不存在，尝试创建
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            # 测试写入权限
            test_file = os.path.join(output_path, "test_write_access.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            error_msg = f"输出目录不可写: {e}"
            self.validation_error.emit(error_msg)
            return False, error_msg

        self.validation_success.emit()
        return True, ""

    def validate_all_inputs(self, test_info, input_path, output_path):
        """
        验证所有输入

        Args:
            test_info: 测试信息列表
            input_path: 输入数据路径
            output_path: 输出路径

        Returns:
            tuple: (是否全部有效, 错误消息)
        """
        # 验证测试信息
        valid, error_msg = self.validate_test_info(test_info)
        if not valid:
            return False, error_msg

        # 验证输入数据
        valid, error_msg = self.validate_input_data(input_path)
        if not valid:
            return False, error_msg

        # 验证输出路径
        valid, error_msg = self.validate_output_path(output_path)
        if not valid:
            return False, error_msg

        return True, ""

    def sanitize_file_name(self, file_name):
        """
        清理文件名，移除或替换无效字符

        Args:
            file_name: 原始文件名

        Returns:
            str: 清理后的文件名
        """
        # 定义Windows系统中不允许的字符
        invalid_chars = '<>:"/\\|?*'
        sanitized = ''.join(
            c if c not in invalid_chars else '_' for c in file_name)
        return sanitized