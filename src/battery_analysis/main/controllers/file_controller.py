# -*- coding: utf-8 -*-
"""
文件控制器模块
负责处理文件操作相关的业务逻辑
"""
import os
import sys
import logging
from PyQt6 import QtCore as QC


class FileController(QC.QObject):
    """
    文件控制器类
    负责文件路径管理、配置文件读取等文件操作
    """
    # 定义信号
    config_loaded = QC.pyqtSignal(dict)  # 配置加载完成信号
    error_occurred = QC.pyqtSignal(str)  # 错误发生信号

    def __init__(self):
        """
        初始化文件控制器
        """
        super().__init__()
        
        # 获取服务容器
        from battery_analysis.main.services.service_container import get_service_container
        self.service_container = get_service_container()
        
        # 获取文件服务
        self.file_service = self.service_container.get("file")
        self.config_service = self.service_container.get("config")
        
        self.project_path = self._get_project_path()
        self.config = None

    def _get_project_path(self):
        """
        获取项目根目录路径

        Returns:
            str: 项目根目录路径
        """
        # 获取当前脚本所在目录的父目录作为项目路径
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            project_path = os.path.dirname(sys.executable)
        else:
            # 开发环境
            project_path = os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        return project_path

    def get_project_path(self):
        """
        获取项目路径

        Returns:
            str: 项目路径
        """
        return self.project_path

    def load_config(self, config_file_name="setting.ini"):
        """
        加载配置文件

        Args:
            config_file_name: 配置文件名

        Returns:
            dict: 配置信息字典，如果加载失败返回None
        """
        # 使用配置服务加载配置文件
        if not self.config_service:
            error_msg = "配置服务不可用"
            logging.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None

        try:
            # 使用配置服务加载配置
            success = self.config_service.load_config(config_file_name)
            if not success:
                error_msg = f"未找到配置文件: {config_file_name}"
                logging.error(error_msg)
                self.error_occurred.emit(error_msg)
                return None

            # 获取配置字典
            config_dict = {}
            
            # 获取所有配置节
            config = self.config_service.get_all_sections()
            for section_name in config:
                section_dict = {}
                section_options = self.config_service.get_section_options(section_name)
                for option in section_options:
                    value = self.config_service.get_config_value(f"{section_name}/{option}")
                    section_dict[option] = value
                config_dict[section_name] = section_dict

            self.config_loaded.emit(config_dict)
            return config_dict
        except Exception as e:
            error_msg = f"加载配置文件失败: {e}"
            logging.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None

    def get_config_value(self, section, option, default=None):
        """
        获取配置值

        Args:
            section: 配置节
            option: 配置项
            default: 默认值

        Returns:
            str: 配置值，如果不存在返回默认值
        """
        if not self.config_service:
            return default

        try:
            return self.config_service.get_config_value(f"{section}/{option}", default)
        except Exception as e:
            logging.warning("获取配置值失败: %s", e)
            return default

    def validate_directory(self, directory_path):
        """
        验证目录是否存在且可访问

        Args:
            directory_path: 目录路径

        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not directory_path:
            return False, "目录路径不能empty"

        if not os.path.exists(directory_path):
            return False, f"目录不存在: {directory_path}"

        if not os.path.isdir(directory_path):
            return False, f"路径不是目录: {directory_path}"

        try:
            # 检查目录是否可访问
            os.listdir(directory_path)
            return True, ""
        except OSError as e:
            return False, f"目录访问失败: {e}"

    def ensure_directory_exists(self, directory_path):
        """
        确保目录存在，如果不存在则创建

        Args:
            directory_path: 目录路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            return True, ""
        except OSError as e:
            error_msg = f"创建目录失败: {e}"
            logging.error(error_msg)
            return False, error_msg

    def get_valid_output_path(self, input_path, default_output=None):
        """
        获取有效的输出路径

        Args:
            input_path: 输入路径
            default_output: 默认输出路径

        Returns:
            str: 有效的输出路径
        """
        if default_output and os.path.exists(default_output):
            return default_output

        # 如果输入路径是目录，使用其上级目录作为输出路径
        if os.path.isdir(input_path):
            parent_dir = os.path.dirname(input_path)
            if parent_dir:
                return parent_dir

        # 默认使用当前工作目录
        return os.getcwd()
