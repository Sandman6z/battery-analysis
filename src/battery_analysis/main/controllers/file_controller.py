# -*- coding: utf-8 -*-
"""
文件控制器模块
负责处理文件操作相关的业务逻辑
"""
import os
import sys
import logging
import configparser
from PyQt6 import QtCore as QC

from battery_analysis.utils.config_utils import find_config_file


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
            project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
        # 使用通用配置文件查找函数
        config_path = find_config_file(config_file_name)
        
        if not config_path or not os.path.exists(config_path):
            error_msg = f"未找到配置文件: {config_file_name}"
            logging.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None
        
        try:
            config = configparser.ConfigParser()
            config.read(config_path, encoding="utf-8")
            self.config = config
            
            # 将配置转换为字典
            config_dict = {}
            for section in config.sections():
                config_dict[section] = {}
                for option in config.options(section):
                    config_dict[section][option] = config.get(section, option)
            
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
        if not self.config:
            return default
        
        try:
            return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
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
            return False, "目录路径不能为空"
        
        if not os.path.exists(directory_path):
            return False, f"目录不存在: {directory_path}"
        
        if not os.path.isdir(directory_path):
            return False, f"路径不是目录: {directory_path}"
        
        try:
            # 检查目录是否可访问
            os.listdir(directory_path)
            return True, ""
        except Exception as e:
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
        except Exception as e:
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
