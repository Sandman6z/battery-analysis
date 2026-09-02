"""
文件控制器模块
负责处理文件操作相关的业务逻辑
"""

import logging
import os
import sys

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
        if getattr(sys, "frozen", False):
            # 打包后的环境
            project_path = os.path.dirname(sys.executable)
        else:
            # 开发环境
            project_path = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
        return project_path

    def get_project_path(self):
        """
        获取项目路径

        Returns:
            str: 项目路径
        """
        return self.project_path

    def load_config(self):
        """
        加载配置文件（由 ConfigService 自动解析 %APPDATA%/battery-analysis/config.json）

        Returns:
            dict: 配置信息字典，如果加载失败返回None
        """
        # 使用配置服务加载配置文件
        if not self.config_service:
            error_msg = "Config service unavailable"
            logging.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None

        try:
            # 使用配置服务加载配置
            success = self.config_service.load_config()
            if not success:
                error_msg = "Config file not found"
                logging.error(error_msg)
                self.error_occurred.emit(error_msg)
                return None

            # 获取配置字典
            config_dict = {}

            # 获取所有配置节
            config = self.config_service.get_config_sections()
            for section_name in config:
                section_dict = {}
                section_options = self.config_service.get_section_options(section_name)
                for option in section_options:
                    value = self.config_service.get_config_value(f"{section_name}/{option}")
                    section_dict[option] = value
                config_dict[section_name] = section_dict

            self.config_loaded.emit(config_dict)
            return config_dict
        except (OSError, UnicodeDecodeError, TypeError, AttributeError) as e:
            error_msg = f"Failed to load config file: {e}"
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
        except (AttributeError, TypeError, ValueError, KeyError) as e:
            logging.warning("Failed to get config value: %s", e)
            return default

