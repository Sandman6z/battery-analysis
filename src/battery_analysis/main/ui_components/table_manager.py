# -*- coding: utf-8 -*-
"""
表格管理器模块
负责处理测试信息表格的设置和保存功能
"""

import re
from typing import Any
from PyQt6.QtWidgets import QTableWidgetItem


class TableManager:
    """
    表格管理器
    负责测试信息表格的设置和保存功能
    """
    
    def __init__(self, main_window: Any) -> None:
        """
        初始化表格管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = main_window.logger
        
    def set_table(self) -> None:
        """
        根据配置文件设置测试信息表格
        """
        self.main_window.checker_table.clear()
        # 不再重新创建QSettings实例，而是重新读取配置
        # 这样可以确保使用与初始化when相同的配置文件路径和设置
        self.main_window.config.sync()  # 确保配置文件被正确加载

        # 使用正则表达式匹配TestInformation组
        test_info_pattern = re.compile(r"^TestInformation\.(\w+)\.(\w+)$")
        
        # 创建字典映射：(location, laboratory) -> group_name
        test_info_map = {}
        
        # 遍历所有子组，提取有效的TestInformation组
        for group in self.main_window.config.childGroups():
            match = test_info_pattern.match(group)
            if match:
                location, laboratory = match.groups()
                test_info_map[(location, laboratory)] = group

        if not test_info_map:
            self.main_window.checker_table.set_error("No TestInformation in setting.ini")
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                "[Error]: No TestInformation in setting.ini")
            return

        self.main_window.test_information = ""
        # 获取当前选择的测试位置
        tester_location = self.main_window.comboBox_TesterLocation.currentText().replace(" ", "")
        
        # 查找匹配的TestInformation组
        for (location, laboratory), group_name in test_info_map.items():
            if (laboratory in tester_location) and (location in tester_location):
                self.main_window.test_information = group_name
                break

        if not self.main_window.test_information:
            self.main_window.checker_table.set_error(
                "Can't find matched TestInformation section in setting.ini")
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                "[Error]: Can't find matched TestInformation section in setting.ini")
            return

        def set_item(item_data, row: int, col: int) -> None:
            item_text = ", ".join(item_data) if item_data else ""
            qt_item = QTableWidgetItem(item_text)
            self.main_window.tableWidget_TestInformation.setItem(row, col, qt_item)

        # 使用字典映射配置键到行号，简化代码
        config_row_map = {
            f"{self.main_window.test_information}/TestEquipment": 0,
            f"{self.main_window.test_information}/SoftwareVersions.BTSServerVersion": 1,
            f"{self.main_window.test_information}/SoftwareVersions.BTSClientVersion": 2,
            f"{self.main_window.test_information}/SoftwareVersions.BTSDAVersion": 3,
            f"{self.main_window.test_information}/MiddleMachines.Model": 4,
            f"{self.main_window.test_information}/MiddleMachines.HardwareVersion": 5,
            f"{self.main_window.test_information}/MiddleMachines.SerialNumber": 6,
            f"{self.main_window.test_information}/MiddleMachines.FirmwareVersion": 7,
            f"{self.main_window.test_information}/MiddleMachines.DeviceType": 8,
            f"{self.main_window.test_information}/TestUnits.Model": 9,
            f"{self.main_window.test_information}/TestUnits.HardwareVersion": 10,
            f"{self.main_window.test_information}/TestUnits.FirmwareVersion": 11
        }
        
        # 遍历字典，设置表格项
        for config_key, row in config_row_map.items():
            set_item(self.main_window.get_config(config_key), row, 2)

    def save_table(self) -> None:
        """
        保存表格数据到配置文件
        """
        # set focus on pushButton_Run for saving the input text
        self.main_window.pushButton_Run.setFocus()

        def set_item(config_key: str, row: int, col: int):
            item = self.main_window.tableWidget_TestInformation.item(row, col)
            if item is None:
                self.main_window.config.setValue(f"{config_key}", "")
                return
            list_item_text = item.text().split(",")
            for i in range(len(list_item_text)):
                list_item_text[i] = list_item_text[i].strip()
            if len(list_item_text) == 1:
                self.main_window.config.setValue(f"{config_key}", list_item_text[0])
            else:
                self.main_window.config.setValue(f"{config_key}", list_item_text)

        if self.main_window.test_information != "":
            set_item(f"{self.main_window.test_information}/TestEquipment", 0, 2)
            set_item(
                f"{self.main_window.test_information}/SoftwareVersions.BTSServerVersion", 1, 2)
            set_item(
                f"{self.main_window.test_information}/SoftwareVersions.BTSClientVersion", 2, 2)
            set_item(
                f"{self.main_window.test_information}/SoftwareVersions.BTSDAVersion", 3, 2)
            set_item(f"{self.main_window.test_information}/MiddleMachines.Model", 4, 2)
            set_item(
                f"{self.main_window.test_information}/MiddleMachines.HardwareVersion", 5, 2)
            set_item(
                f"{self.main_window.test_information}/MiddleMachines.SerialNumber", 6, 2)
            set_item(
                f"{self.main_window.test_information}/MiddleMachines.FirmwareVersion", 7, 2)
            set_item(f"{self.main_window.test_information}/MiddleMachines.DeviceType", 8, 2)
            set_item(f"{self.main_window.test_information}/TestUnits.Model", 9, 2)
            set_item(
                f"{self.main_window.test_information}/TestUnits.HardwareVersion", 10, 2)
            set_item(
                f"{self.main_window.test_information}/TestUnits.FirmwareVersion", 11, 2)

        set_item("TestInformation/TestEquipment", 0, 2)
        set_item("TestInformation/SoftwareVersions.BTSServerVersion", 1, 2)
        set_item("TestInformation/SoftwareVersions.BTSClientVersion", 2, 2)
        set_item("TestInformation/SoftwareVersions.BTSDAVersion", 3, 2)
        set_item("TestInformation/middleMachines.Model", 4, 2)
        set_item("TestInformation/middleMachines.HardwareVersion", 5, 2)
        set_item("TestInformation/middleMachines.SerialNumber", 6, 2)
        set_item("TestInformation/middleMachines.FirmwareVersion", 7, 2)
        set_item("TestInformation/middleMachines.DeviceType", 8, 2)
        set_item("TestInformation/TestUnits.Model", 9, 2)
        set_item("TestInformation/TestUnits.HardwareVersion", 10, 2)
        set_item("TestInformation/TestUnits.FirmwareVersion", 11, 2)
