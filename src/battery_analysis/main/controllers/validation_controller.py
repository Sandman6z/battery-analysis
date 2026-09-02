"""
验证控制器模块
负责处理输入验证相关的业务逻辑
"""

import os

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

        # 降级到原来的逻辑
        error_msg = "Validation service unavailable"
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
            error_msg = "Input data path cannot be empty"
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
                error_msg = f"Input data path does not exist: {input_path}"
                self.validation_error.emit(error_msg)
                return False, error_msg

            if not os.path.isdir(input_path):
                error_msg = f"Input data path must be a directory: {input_path}"
                self.validation_error.emit(error_msg)
                return False, error_msg

        # 检查目录中是否包含必要的文件
        try:
            files = os.listdir(input_path)
            # 检查是否至少有一个xlsx或csv文件
            has_data_file = any(file.endswith(".xlsx") or file.endswith(".csv") for file in files)
            if not has_data_file:
                error_msg = "No data files (.xlsx or .csv) found in input directory"
                self.validation_error.emit(error_msg)
                return False, error_msg
        except (OSError, TypeError, ValueError) as e:
            error_msg = f"Failed to read input directory: {e}"
            self.validation_error.emit(error_msg)
            return False, error_msg

        self.validation_success.emit()
        return True, ""

