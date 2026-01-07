"""
配置管理器模块

这个模块实现了电池分析应用的配置管理功能，包括：
- 配置文件的查找和加载
- 配置值的读取和解析
- 用户设置的加载和保存
- 配置变更的处理
"""

# 标准库导入
import logging
import os
from pathlib import Path
from typing import Any, List, Optional

# 第三方库导入
import PyQt6.QtCore as QC

# 本地应用/库导入
from battery_analysis.utils.config_parser import safe_float_convert, safe_int_convert


class ConfigManager:
    """
    配置管理器类，负责配置文件的读取和写入
    """
    
    def __init__(self, main_window):
        """
        初始化配置管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self.config = None
        self.config_path = None
        self.b_has_config = True
        
        # 初始化配置
        self._initialize_config()
    
    def _initialize_config(self):
        """
        初始化配置文件
        """
        # 改进的配置文件路径查找逻辑（使用配置服务）
        try:
            config_service = self.main_window._get_service("config")
            if config_service:
                config_path_result = config_service.find_config_file()
                self.config_path = str(config_path_result) if config_path_result else None
            else:
                # 降级到直接导入
                from battery_analysis.utils.config_utils import find_config_file
                self.config_path = find_config_file()
        except (AttributeError, TypeError, ImportError, OSError) as e:
            self.logger.warning("Failed to get config service: %s", e)
            # 降级到直接导入
            from battery_analysis.utils.config_utils import find_config_file
            self.config_path = find_config_file()
        
        # 添加对None值的检查，避免TypeError
        if self.config_path is None or not Path(self.config_path).exists():
            self.b_has_config = False
            # 创建默认配置设置
            self.config = QC.QSettings()
        else:
            self.b_has_config = True
            self.config = QC.QSettings(
                self.config_path,
                QC.QSettings.Format.IniFormat
            )
    
    def get_config(self, config_key: str) -> List[str]:
        """
        获取配置值并处理为列表格式
        
        Args:
            config_key: 配置键
            
        Returns:
            配置值列表
        """
        # 获取配置值并处理为列表格式，移除所有DEBUG打印以避免UI卡死
        # 如果没有配置文件，直接返回空列表
        if not self.b_has_config:
            return []

        try:
            value = self.config.value(config_key)
            if isinstance(value, list):
                list_value = []
                for item in value:
                    if item != "":
                        list_value.append(item)
            elif isinstance(value, str):
                # 处理逗号分隔的字符串，例如："item1", "item2", "item3"
                if "," in value:
                    # 先去除首尾空格
                    value = value.strip()
                    # 分割字符串
                    items = value.split(",")
                    list_value = []
                    for item in items:
                        # 去除每个项的首尾空格和引号
                        cleaned_item = item.strip().strip('"')
                        if cleaned_item:
                            list_value.append(cleaned_item)
                else:
                    # 单个值，直接添加
                    list_value = [value.strip().strip('"')]
            else:
                list_value = []
            return list_value
        except (AttributeError, TypeError, ValueError, KeyError, OSError) as e:
            logging.error("读取配置 %s 失败: %s", config_key, e)
            return []
    
    def load_user_settings(self):
        """
        加载用户配置文件中的设置
        """
        try:
            user_config_path = os.path.join(os.path.dirname(
                self.config_path), "user_settings.ini") if self.b_has_config else None

            if user_config_path and os.path.exists(user_config_path):
                # 创建用户配置QSettings实例
                user_settings = QC.QSettings(
                    user_config_path, QC.QSettings.Format.IniFormat)

                # 加载电池类型相关设置
                battery_type = user_settings.value("UserConfig/BatteryType")
                if battery_type:
                    index = self.main_window.comboBox_BatteryType.findText(battery_type)
                    if index >= 0:
                        self.main_window.comboBox_BatteryType.setCurrentIndex(index)

                construction_method = user_settings.value(
                    "UserConfig/ConstructionMethod")
                if construction_method:
                    index = self.main_window.comboBox_ConstructionMethod.findText(
                        construction_method)
                    if index >= 0:
                        self.main_window.comboBox_ConstructionMethod.setCurrentIndex(index)

                specification_type = user_settings.value(
                    "UserConfig/SpecificationType")
                if specification_type:
                    index = self.main_window.comboBox_Specification_Type.findText(
                        specification_type)
                    if index >= 0:
                        self.main_window.comboBox_Specification_Type.setCurrentIndex(index)

                specification_method = user_settings.value(
                    "UserConfig/SpecificationMethod")
                if specification_method:
                    index = self.main_window.comboBox_Specification_Method.findText(
                        specification_method)
                    if index >= 0:
                        self.main_window.comboBox_Specification_Method.setCurrentIndex(
                            index)

                manufacturer = user_settings.value("UserConfig/Manufacturer")
                if manufacturer:
                    index = self.main_window.comboBox_Manufacturer.findText(manufacturer)
                    if index >= 0:
                        self.main_window.comboBox_Manufacturer.setCurrentIndex(index)

                tester_location = user_settings.value(
                    "UserConfig/TesterLocation")
                if tester_location:
                    index = self.main_window.comboBox_TesterLocation.findText(
                        tester_location)
                    if index >= 0:
                        self.main_window.comboBox_TesterLocation.setCurrentIndex(index)

                tested_by = user_settings.value("UserConfig/TestedBy")
                if tested_by:
                    index = self.main_window.comboBox_TestedBy.findText(tested_by)
                    if index >= 0:
                        self.main_window.comboBox_TestedBy.setCurrentIndex(index)
                    else:
                        # 如果找不到匹配项，直接设置文本（用于自定义输入的情况）
                        self.main_window.comboBox_TestedBy.setCurrentText(tested_by)
                
                # 加载ReportedBy设置
                reported_by = user_settings.value("UserConfig/ReportedBy")
                if reported_by:
                    index = self.main_window.comboBox_ReportedBy.findText(reported_by)
                    if index >= 0:
                        self.main_window.comboBox_ReportedBy.setCurrentIndex(index)
                    else:
                        # 如果找不到匹配项，直接设置文本（用于自定义输入的情况）
                        self.main_window.comboBox_ReportedBy.setCurrentText(reported_by)

                # 加载温度设置
                temperature = user_settings.value("UserConfig/Temperature")
                if temperature:
                    # 同时更新comboBox_Temperature
                    if "Freezer" in temperature:
                        self.main_window.comboBox_Temperature.setCurrentText("Freezer Temperature")
                        # 从温度字符串中提取数值并设置到spinBox
                        import re
                        temp_value = re.search(r"(\d+)", temperature)
                        if temp_value:
                            self.main_window.spinBox_Temperature.setValue(int(temp_value.group(1)))
                    else:
                        self.main_window.comboBox_Temperature.setCurrentText("Room Temperature")
                
                # 加载温度类型设置（如果存在）
                temperature_type = user_settings.value("UserConfig/TemperatureType")
                if temperature_type:
                    self.main_window.comboBox_Temperature.setCurrentText(temperature_type)
                    # 同时更新spinBox的启用状态
                    if temperature_type == "Freezer Temperature":
                        self.main_window.spinBox_Temperature.setEnabled(True)
                    else:
                        self.main_window.spinBox_Temperature.setEnabled(False)
                
                # 加载冷冻温度数值设置
                freezer_temp = user_settings.value("UserConfig/FreezerTemperature")
                if freezer_temp:
                    try:
                        self.main_window.spinBox_Temperature.setValue(int(freezer_temp))
                    except (ValueError, TypeError):
                        pass

                # 加载输出路径设置
                output_path = user_settings.value("UserConfig/OutputPath")
                if output_path:
                    self.main_window.lineEdit_OutputPath.setText(output_path)
                    # 更新控制器的输出路径
                    main_controller = self.main_window._get_controller("main_controller")
                    if main_controller:
                        main_controller.set_project_context(
                            output_path=output_path)
        except (AttributeError, TypeError, KeyError, OSError) as e:
            logging.error("加载用户设置失败: %s", e)
    
    def save_user_settings(self):
        """
        保存用户配置
        """
        try:
            user_config_path = os.path.join(os.path.dirname(
                self.config_path), "user_settings.ini") if self.b_has_config else None

            if user_config_path:
                # 创建用户配置QSettings实例
                user_settings = QC.QSettings(
                    user_config_path, QC.QSettings.Format.IniFormat)

                # 保存电池类型相关设置
                user_settings.setValue("UserConfig/BatteryType", 
                                      self.main_window.comboBox_BatteryType.currentText())
                user_settings.setValue("UserConfig/ConstructionMethod", 
                                      self.main_window.comboBox_ConstructionMethod.currentText())
                user_settings.setValue("UserConfig/SpecificationType", 
                                      self.main_window.comboBox_Specification_Type.currentText())
                user_settings.setValue("UserConfig/SpecificationMethod", 
                                      self.main_window.comboBox_Specification_Method.currentText())
                user_settings.setValue("UserConfig/Manufacturer", 
                                      self.main_window.comboBox_Manufacturer.currentText())
                user_settings.setValue("UserConfig/TesterLocation", 
                                      self.main_window.comboBox_TesterLocation.currentText())
                user_settings.setValue("UserConfig/TestedBy", 
                                      self.main_window.comboBox_TestedBy.currentText())
                user_settings.setValue("UserConfig/ReportedBy", 
                                      self.main_window.comboBox_ReportedBy.currentText())
                
                # 保存温度设置
                user_settings.setValue("UserConfig/TemperatureType", 
                                      self.main_window.comboBox_Temperature.currentText())
                
                # 保存冷冻温度数值设置
                user_settings.setValue("UserConfig/FreezerTemperature", 
                                      self.main_window.spinBox_Temperature.value())
                
                # 保存输出路径设置
                user_settings.setValue("UserConfig/OutputPath", 
                                      self.main_window.lineEdit_OutputPath.text())
                
                # 同步保存到文件
                user_settings.sync()
                self.logger.info("用户设置已保存")
        except (AttributeError, TypeError, KeyError, OSError) as e:
            logging.error("保存用户设置失败: %s", e)
    
    def get_current_config_path(self) -> Optional[str]:
        """
        获取当前配置文件路径
        
        Returns:
            配置文件路径
        """
        return self.config_path
    
    def has_config(self) -> bool:
        """
        检查是否有配置文件
        
        Returns:
            是否有配置文件
        """
        return self.b_has_config
    
    def reload_config(self):
        """
        重新加载配置文件
        """
        self._initialize_config()
        self.logger.info("配置文件已重新加载")
