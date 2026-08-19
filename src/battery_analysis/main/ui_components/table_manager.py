# -*- coding: utf-8 -*-
"""
表格管理器模块
负责处理测试信息表格的设置和保存功能

从 test.equipment（JSON config）读取测试信息，与 ConfigDialog 共用数据源。
"""

import logging
from typing import Any
from PyQt6.QtWidgets import QTableWidgetItem


class TableManager:
    """
    表格管理器
    负责测试信息表格的设置和保存功能
    """

    def __init__(self, main_window: Any = None, ctx=None) -> None:
        """
        初始化表格管理器

        Args:
            main_window: 主窗口实例（旧接口）
            ctx: AppContext（新接口）
        """
        self.main_window = main_window
        self._ctx = ctx
        self.logger = main_window.logger if main_window else logging.getLogger(__name__)

    def _get_config_service(self):
        """获取 ConfigService 实例"""
        return self.main_window._get_service("config")

    def set_table(self) -> None:
        """
        根据 equipment 配置设置测试信息表格
        """
        self.main_window.checker_table.clear()

        # 获取当前选择的测试位置
        tester_location = self.main_window.comboBox_TesterLocation.currentText()
        if not tester_location:
            self.main_window.test_information = ""
            return

        # 直接从 test.equipment 读取
        cs = self._get_config_service()
        equipment = cs.get_config_value("test.equipment", {}) if cs else {}
        if not isinstance(equipment, dict):
            equipment = {}

        # 匹配 equipment key → 显示字符串 → combo box 选中项
        matched_info = None
        for loc_key, info in equipment.items():
            parts = loc_key.split(".")
            if len(parts) != 2:
                continue
            site, lab = parts
            eq = info.get("testEquipment", "")
            model = eq.replace("NEWARE Battery Testing System ", "").strip()
            lab_display = lab + "." if lab == "Qual" else lab
            display = f"{model} ({lab_display}), {site}"
            if display == tester_location:
                matched_info = info
                self.main_window.test_information = loc_key
                break

        # fallback: 旧版 substring 匹配
        if matched_info is None:
            stripped = tester_location.replace(" ", "")
            for loc_key, info in equipment.items():
                parts = loc_key.split(".")
                if len(parts) == 2:
                    site, lab = parts
                    if site in stripped and lab in stripped:
                        matched_info = info
                        self.main_window.test_information = loc_key
                        break

        if matched_info is None:
            self.main_window.checker_table.set_error(
                "Equipment config not found")
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                "[Error]: Equipment config not found")
            return

        def set_item(item_data, row: int, col: int) -> None:
            item_text = ", ".join(item_data) if item_data else ""
            qt_item = QTableWidgetItem(item_text)
            self.main_window.tableWidget_TestInformation.setItem(row, col, qt_item)

        sv = matched_info.get("softwareVersions", {})
        mm = matched_info.get("middleMachines", {})
        tu = matched_info.get("testUnits", {})

        set_item([matched_info.get("testEquipment", "")], 0, 2)
        set_item([sv.get("btsServer", "")], 1, 2)
        set_item([sv.get("btsClient", "")], 2, 2)
        set_item([sv.get("btsda", "")], 3, 2)
        set_item([mm.get("model", "")], 4, 2)
        set_item([mm.get("hardwareVersion", "")], 5, 2)
        set_item([mm.get("serialNumber", "")], 6, 2)
        set_item([mm.get("firmwareVersion", "")], 7, 2)
        set_item([mm.get("deviceType", "")], 8, 2)
        set_item([tu.get("model", "")], 9, 2)
        set_item([tu.get("hardwareVersion", "")], 10, 2)
        set_item([tu.get("firmwareVersion", "")], 11, 2)

    def save_table(self) -> None:
        """
        保存表格数据到 equipment 配置（与 ConfigDialog 共用同一数据源）
        """
        # set focus on pushButton_Run for saving the input text
        self.main_window.pushButton_Run.setFocus()

        if not self.main_window.test_information:
            return

        cs = self._get_config_service()
        if not cs:
            return

        equipment = cs.get_config_value("test.equipment", {})
        if not isinstance(equipment, dict):
            equipment = {}

        loc_key = self.main_window.test_information
        info = equipment.get(loc_key)
        if info is None:
            return

        def read_cell(row, col):
            item = self.main_window.tableWidget_TestInformation.item(row, col)
            if item is None:
                return ""
            return ", ".join(x.strip() for x in item.text().split(","))

        info["testEquipment"] = read_cell(0, 2)
        info.setdefault("softwareVersions", {})["btsServer"] = read_cell(1, 2)
        info.setdefault("softwareVersions", {})["btsClient"] = read_cell(2, 2)
        info.setdefault("softwareVersions", {})["btsda"] = read_cell(3, 2)
        info.setdefault("middleMachines", {})["model"] = read_cell(4, 2)
        info.setdefault("middleMachines", {})["hardwareVersion"] = read_cell(5, 2)
        info.setdefault("middleMachines", {})["serialNumber"] = read_cell(6, 2)
        info.setdefault("middleMachines", {})["firmwareVersion"] = read_cell(7, 2)
        info.setdefault("middleMachines", {})["deviceType"] = read_cell(8, 2)
        info.setdefault("testUnits", {})["model"] = read_cell(9, 2)
        info.setdefault("testUnits", {})["hardwareVersion"] = read_cell(10, 2)
        info.setdefault("testUnits", {})["firmwareVersion"] = read_cell(11, 2)

        cs.set_config_value("test.equipment", equipment)
        cs.save_config()
