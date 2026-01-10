# -*- coding: utf-8 -*-
"""
测试配置文件管理器

负责处理测试配置文件的选择、验证和处理逻辑
"""

# 标准库导入
import logging
import os

# 第三方库导入
import PyQt6.QtWidgets as QW


class TestProfileManager:
    """
    测试配置文件管理器
    负责处理测试配置文件的选择、验证和处理逻辑
    """
    
    def __init__(self, main_window):
        """
        初始化测试配置文件管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def select_testprofile(self):
        """
        选择测试配置文件并处理相关逻辑
        """
        try:
            # 1. 选择测试配置文件
            selected_file = self.main_window.path_manager.select_test_profile()
            
            if not selected_file:
                return
            
            # 2. 验证测试配置文件
            if not self.main_window.path_manager.validate_test_profile(selected_file):
                return
            
            # 3. 显示选中的文件路径
            self.main_window.lineEdit_TestProfile.setText(selected_file)
            
            # 4. 获取父目录
            parent_dir = self.main_window.path_manager.get_parent_directory(selected_file)
            if not parent_dir:
                return
            
            # 5. 设置输入路径
            self.main_window.path_manager.set_input_path(parent_dir)
            
            # 6. 设置输出路径
            if not self.main_window.path_manager.set_output_path(parent_dir):
                return
            
            # 7. 发出版本设置信号
            self.main_window.sigSetVersion.emit()
            
            # 8. 更新当前目录
            self.main_window.current_directory = parent_dir
            self.logger.info("设置当前目录为项目根目录: %s", parent_dir)
            
            # 9. 根据XML文件名自动检测温度类型
            self._detect_temperature_type_from_xml(selected_file)
            
        except (OSError, ValueError, TypeError, RuntimeError, FileNotFoundError, PermissionError) as e:
            self.logger.error("选择Test Profile时发生错误: %s", e)
            QW.QMessageBox.critical(
                self.main_window,
                "错误",
                f"处理Test Profile时发生错误:\n{str(e)}",
                QW.QMessageBox.StandardButton.Ok
            )
    
    def _detect_temperature_type_from_xml(self, xml_path: str) -> None:
        """
        根据XML文件名自动检测温度类型
        
        Args:
            xml_path: XML文件的完整路径
        """
        try:
            # 使用温度处理器检测温度类型
            from battery_analysis.main.handlers.temperature_handler import TemperatureType
            temperature_type = self.main_window.temperature_handler.detect_temperature_type_from_xml(xml_path)
            
            # 获取文件名用于日志
            file_name = os.path.basename(xml_path)
            
            # 使用温度处理器更新UI
            self.main_window.temperature_handler.update_temperature_ui(temperature_type)
            
            # 记录日志
            if temperature_type.value == "Freezer Temperature":
                self.logger.info("检测到冷冻温度测试配置文件: %s", file_name)
            else:
                self.logger.info("检测到常温测试配置文件: %s", file_name)
                
        except (AttributeError, ValueError) as e:
            self.logger.warning("检测温度类型时发生错误: %s", e)
