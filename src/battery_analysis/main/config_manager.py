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
from battery_analysis.main.user_settings_manager import UserSettingsManager


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
        self.user_settings_manager = None
        
        # 初始化配置
        self._initialize_config()
        
        # 初始化用户设置管理器
        self.user_settings_manager = UserSettingsManager(self.config_path)
    
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
            # 使用用户设置管理器加载配置
            user_config = self.user_settings_manager.load_user_settings()
            
            # 更新UI控件
            # 电池类型相关设置
            if user_config.get("BatteryType"):
                index = self.main_window.comboBox_BatteryType.findText(user_config["BatteryType"])
                if index >= 0:
                    self.main_window.comboBox_BatteryType.setCurrentIndex(index)

            if user_config.get("ConstructionMethod"):
                index = self.main_window.comboBox_ConstructionMethod.findText(
                    user_config["ConstructionMethod"])
                if index >= 0:
                    self.main_window.comboBox_ConstructionMethod.setCurrentIndex(index)

            if user_config.get("SpecificationType"):
                index = self.main_window.comboBox_Specification_Type.findText(
                    user_config["SpecificationType"])
                if index >= 0:
                    self.main_window.comboBox_Specification_Type.setCurrentIndex(index)

            if user_config.get("SpecificationMethod"):
                index = self.main_window.comboBox_Specification_Method.findText(
                    user_config["SpecificationMethod"])
                if index >= 0:
                    self.main_window.comboBox_Specification_Method.setCurrentIndex(
                        index)

            if user_config.get("Manufacturer"):
                index = self.main_window.comboBox_Manufacturer.findText(user_config["Manufacturer"])
                if index >= 0:
                    self.main_window.comboBox_Manufacturer.setCurrentIndex(index)

            if user_config.get("TesterLocation"):
                index = self.main_window.comboBox_TesterLocation.findText(
                    user_config["TesterLocation"])
                if index >= 0:
                    self.main_window.comboBox_TesterLocation.setCurrentIndex(index)

            if user_config.get("TestedBy"):
                index = self.main_window.comboBox_TestedBy.findText(user_config["TestedBy"])
                if index >= 0:
                    self.main_window.comboBox_TestedBy.setCurrentIndex(index)
                else:
                    # 如果找不到匹配项，直接设置文本（用于自定义输入的情况）
                    self.main_window.comboBox_TestedBy.setCurrentText(user_config["TestedBy"])
                
            # 加载ReportedBy设置
            if user_config.get("ReportedBy"):
                index = self.main_window.comboBox_ReportedBy.findText(user_config["ReportedBy"])
                if index >= 0:
                    self.main_window.comboBox_ReportedBy.setCurrentIndex(index)
                else:
                    # 如果找不到匹配项，直接设置文本（用于自定义输入的情况）
                    self.main_window.comboBox_ReportedBy.setCurrentText(user_config["ReportedBy"])

            # 加载温度设置
            if user_config.get("TemperatureType"):
                self.main_window.comboBox_Temperature.setCurrentText(user_config["TemperatureType"])
                # 同时更新spinBox的启用状态
                if user_config["TemperatureType"] == "Freezer Temperature":
                    self.main_window.spinBox_Temperature.setEnabled(True)
                else:
                    self.main_window.spinBox_Temperature.setEnabled(False)
            
            # 加载冷冻温度数值设置
            if user_config.get("FreezerTemperature"):
                try:
                    self.main_window.spinBox_Temperature.setValue(int(user_config["FreezerTemperature"]))
                except (ValueError, TypeError):
                    # 如果用户配置中的值无效，使用Qt控件的默认值0
                    logging.warning("用户配置中的冷冻温度值无效，使用默认值0")

            # 加载输出路径设置
            if user_config.get("OutputPath"):
                self.main_window.lineEdit_OutputPath.setText(user_config["OutputPath"])
                # 更新控制器的输出路径
                main_controller = self.main_window._get_controller("main_controller")
                if main_controller:
                    main_controller.set_project_context(
                        output_path=user_config["OutputPath"])
        except (AttributeError, TypeError, KeyError, OSError) as e:
            logging.error("加载用户设置失败: %s", e)
    
    def save_user_settings(self):
        """
        保存用户配置
        """
        try:
            # 收集当前UI控件的值
            user_settings = {
                "BatteryType": self.main_window.comboBox_BatteryType.currentText(),
                "ConstructionMethod": self.main_window.comboBox_ConstructionMethod.currentText(),
                "SpecificationType": self.main_window.comboBox_Specification_Type.currentText(),
                "SpecificationMethod": self.main_window.comboBox_Specification_Method.currentText(),
                "Manufacturer": self.main_window.comboBox_Manufacturer.currentText(),
                "TesterLocation": self.main_window.comboBox_TesterLocation.currentText(),
                "TestedBy": self.main_window.comboBox_TestedBy.currentText(),
                "ReportedBy": self.main_window.comboBox_ReportedBy.currentText(),
                "TemperatureType": self.main_window.comboBox_Temperature.currentText(),
                "FreezerTemperature": self.main_window.spinBox_Temperature.value(),
                "OutputPath": self.main_window.lineEdit_OutputPath.text()
            }
            
            # 使用用户设置管理器保存配置
            self.user_settings_manager.save_user_settings(user_settings)
            
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
