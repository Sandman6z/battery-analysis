"""
用户设置管理模块

这个模块负责处理用户配置的加载和保存，包括：
- 电池类型设置
- 温度设置
- 输出路径设置
- 其他用户可配置选项
"""

import os
import logging
import configparser
from typing import Any

# 第三方库导入
import PyQt6.QtCore as QC
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _


class UserSettingsManager:
    """
    用户设置管理器，负责处理用户配置的加载和保存
    """
    
    def __init__(self, main_window):
        """
        初始化用户设置管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
    def save_settings(self) -> None:
        """
        保存当前设置到用户配置文件
        """
        try:
            # 显示保存状态
            self.main_window.statusBar_BatteryAnalysis.showMessage(_("saving_settings", "正在保存设置..."))

            # 创建用户配置文件路径（与原始配置文件同目录，使用不同名称）
            user_config_path = os.path.join(os.path.dirname(
                self.main_window.config_path), "user_settings.ini") if self.main_window.b_has_config else None

            if user_config_path:
                # 创建用户配置QSettings实例
                user_settings = QC.QSettings(
                    user_config_path, QC.QSettings.Format.IniFormat)

                # 保存用户可修改的设置项
                # 电池类型相关设置
                battery_type = self.main_window.comboBox_BatteryType.currentText()
                if battery_type:
                    user_settings.setValue(
                        "UserConfig/BatteryType", battery_type)

                construction_method = self.main_window.comboBox_ConstructionMethod.currentText()
                if construction_method:
                    user_settings.setValue(
                        "UserConfig/ConstructionMethod", construction_method)

                specification_type = self.main_window.comboBox_Specification_Type.currentText()
                if specification_type:
                    user_settings.setValue(
                        "UserConfig/SpecificationType", specification_type)

                specification_method = self.main_window.comboBox_Specification_Method.currentText()
                if specification_method:
                    user_settings.setValue(
                        "UserConfig/SpecificationMethod", specification_method)

                manufacturer = self.main_window.comboBox_Manufacturer.currentText()
                if manufacturer:
                    user_settings.setValue(
                        "UserConfig/Manufacturer", manufacturer)

                tester_location = self.main_window.comboBox_TesterLocation.currentText()
                if tester_location:
                    user_settings.setValue(
                        "UserConfig/TesterLocation", tester_location)

                tested_by = self.main_window.comboBox_TestedBy.currentText()
                if tested_by:
                    user_settings.setValue("UserConfig/TestedBy", tested_by)
                
                # 保存ReportedBy设置
                reported_by = self.main_window.comboBox_ReportedBy.currentText()
                if reported_by:
                    user_settings.setValue("UserConfig/ReportedBy", reported_by)

                # 温度设置 - 使用comboBox_Temperature的值代替lineEdit_Temperature
                temperature_type = self.main_window.comboBox_Temperature.currentText()
                if temperature_type == "Freezer Temperature":
                    temperature = f"{temperature_type}:{self.main_window.spinBox_Temperature.value()}"
                else:
                    temperature = temperature_type
                user_settings.setValue(
                    "UserConfig/Temperature", temperature)
                
                # 保存温度类型设置
                temperature_type = self.main_window.comboBox_Temperature.currentText()
                user_settings.setValue(
                    "UserConfig/TemperatureType", temperature_type)
                
                # 保存冷冻温度数值设置（无论是否启用）
                freezer_temp = self.main_window.spinBox_Temperature.value()
                user_settings.setValue(
                    "UserConfig/FreezerTemperature", freezer_temp)

                # 输出路径设置
                output_path = self.main_window.lineEdit_OutputPath.text()
                if output_path:
                    user_settings.setValue(
                        "UserConfig/OutputPath", output_path)

                # 同步保存到内存中的配置实例
                self.main_window.config = user_settings

                self.main_window.statusBar_BatteryAnalysis.showMessage(_("settings_saved", "设置已保存"))
                QW.QMessageBox.information(
                    self.main_window,
                    "保存设置",
                    "当前配置已成功保存到用户配置文件。",
                    QW.QMessageBox.StandardButton.Ok
                )
            else:
                # 如果没有原始配置文件，显示错误消息
                QW.QMessageBox.warning(
                    self.main_window,
                    "错误",
                    "无法找到配置文件路径，无法保存设置。",
                    QW.QMessageBox.StandardButton.Ok
                )
                self.main_window.statusBar_BatteryAnalysis.showMessage(_("save_settings_failed", "保存设置失败"))

        except (IOError, OSError, PermissionError, ValueError, TypeError, configparser.Error) as e:
            logging.error("保存设置失败: %s", e)
            QW.QMessageBox.warning(
                self.main_window,
                "错误",
                f"无法保存设置: {str(e)}",
                QW.QMessageBox.StandardButton.Ok
            )
            self.main_window.statusBar_BatteryAnalysis.showMessage(_("save_settings_failed", "保存设置失败"))
    
    def _load_user_settings(self) -> None:
        """
        加载用户设置
        """
        try:
            # 创建用户配置文件路径
            user_config_path = os.path.join(os.path.dirname(
                self.main_window.config_path), "user_settings.ini") if self.main_window.b_has_config else None
            
            if user_config_path and os.path.exists(user_config_path):
                # 加载用户配置
                user_settings = QC.QSettings(
                    user_config_path, QC.QSettings.Format.IniFormat)
                
                # 加载电池类型设置
                battery_type = user_settings.value("UserConfig/BatteryType")
                if battery_type:
                    index = self.main_window.comboBox_BatteryType.findText(battery_type)
                    if index >= 0:
                        self.main_window.comboBox_BatteryType.setCurrentIndex(index)
                
                # 加载结构方法设置
                construction_method = user_settings.value("UserConfig/ConstructionMethod")
                if construction_method:
                    index = self.main_window.comboBox_ConstructionMethod.findText(construction_method)
                    if index >= 0:
                        self.main_window.comboBox_ConstructionMethod.setCurrentIndex(index)
                
                # 加载规格类型设置
                specification_type = user_settings.value("UserConfig/SpecificationType")
                if specification_type:
                    index = self.main_window.comboBox_Specification_Type.findText(specification_type)
                    if index >= 0:
                        self.main_window.comboBox_Specification_Type.setCurrentIndex(index)
                
                # 加载规格方法设置
                specification_method = user_settings.value("UserConfig/SpecificationMethod")
                if specification_method:
                    index = self.main_window.comboBox_Specification_Method.findText(specification_method)
                    if index >= 0:
                        self.main_window.comboBox_Specification_Method.setCurrentIndex(index)
                
                # 加载制造商设置
                manufacturer = user_settings.value("UserConfig/Manufacturer")
                if manufacturer:
                    index = self.main_window.comboBox_Manufacturer.findText(manufacturer)
                    if index >= 0:
                        self.main_window.comboBox_Manufacturer.setCurrentIndex(index)
                
                # 加载测试位置设置
                tester_location = user_settings.value("UserConfig/TesterLocation")
                if tester_location:
                    index = self.main_window.comboBox_TesterLocation.findText(tester_location)
                    if index >= 0:
                        self.main_window.comboBox_TesterLocation.setCurrentIndex(index)
                
                # 加载测试者设置
                tested_by = user_settings.value("UserConfig/TestedBy")
                if tested_by:
                    index = self.main_window.comboBox_TestedBy.findText(tested_by)
                    if index >= 0:
                        self.main_window.comboBox_TestedBy.setCurrentIndex(index)
                
                # 加载报告者设置
                reported_by = user_settings.value("UserConfig/ReportedBy")
                if reported_by:
                    index = self.main_window.comboBox_ReportedBy.findText(reported_by)
                    if index >= 0:
                        self.main_window.comboBox_ReportedBy.setCurrentIndex(index)
                
                # 加载温度设置
                temperature = user_settings.value("UserConfig/Temperature")
                if temperature:
                    # 解析温度值
                    if ":" in temperature:
                        temp_type, temp_value = temperature.split(":")
                        index = self.main_window.comboBox_Temperature.findText(temp_type)
                        if index >= 0:
                            self.main_window.comboBox_Temperature.setCurrentIndex(index)
                            try:
                                self.main_window.spinBox_Temperature.setValue(float(temp_value))
                            except ValueError:
                                pass
                    else:
                        index = self.main_window.comboBox_Temperature.findText(temperature)
                        if index >= 0:
                            self.main_window.comboBox_Temperature.setCurrentIndex(index)
                
                # 加载输出路径设置
                output_path = user_settings.value("UserConfig/OutputPath")
                if output_path:
                    self.main_window.lineEdit_OutputPath.setText(output_path)
            
        except (IOError, OSError, ValueError, TypeError) as e:
            self.logger.warning("加载用户设置失败: %s", e)
