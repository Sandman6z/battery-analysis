"""
配置管理对话框
提供左侧分类列表、右侧编辑器的 UI，用于管理应用的数据字典配置。
"""

import copy
import logging
from typing import Any, Dict, List, Optional
from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC
from PyQt6 import QtGui as QG

from battery_analysis.i18n.language_manager import _
from battery_analysis.utils.config_defaults import DEFAULT_CONFIG


class ConfigDialog(QW.QDialog):
    """配置管理主对话框"""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._config_service = main_window._get_service("config")
        if self._config_service is None:
            raise RuntimeError("ConfigService not available — cannot open Configuration dialog")

        # 从 ConfigService 加载当前数据（深拷贝，取消保存才写回）
        self._working_data = copy.deepcopy(self._config_service.get_config_value(""))

        self.setWindowTitle(_("config_dialog_title", "Configuration"))
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._populate_data()

    def _setup_ui(self):
        """设置对话框布局"""
        layout = QW.QVBoxLayout(self)

        # 顶部横向选项卡
        self._tabs = QW.QTabWidget()
        self._page_battery = _BatteryConfigPage(self)
        self._page_test = _TestConfigPage(self)
        self._page_equipment = _EquipmentPage(self)
        self._tabs.addTab(self._page_battery, _("cat_battery", "Battery Config"))
        self._tabs.addTab(self._page_test, _("cat_test", "Test Config"))
        self._tabs.addTab(self._page_equipment, _("cat_equipment", "Equipment"))

        # 底部按钮栏
        btn_layout = QW.QHBoxLayout()
        btn_reset = QW.QPushButton(_("reset_defaults", "Reset Defaults"))
        btn_reset.clicked.connect(self._on_reset_defaults)
        btn_save = QW.QPushButton(_("save", "Save"))
        btn_save.clicked.connect(self._on_save)
        btn_cancel = QW.QPushButton(_("cancel", "Cancel"))
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)

        layout.addWidget(self._tabs)
        layout.addLayout(btn_layout)

    def _on_reset_defaults(self):
        """重置为默认值"""
        reply = QW.QMessageBox.question(
            self, _("confirm_reset", "Reset Defaults"),
            _("confirm_reset_msg", "Reset all configuration to default values? This cannot be undone."),
            QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No
        )
        if reply == QW.QMessageBox.StandardButton.Yes:
            self._working_data = copy.deepcopy(DEFAULT_CONFIG)
            self._populate_data()

    def _on_save(self):
        """保存配置并关闭"""
        try:
            # 从各页面收集数据
            self._page_battery.collect_data()
            self._page_test.collect_data()
            self._page_equipment.collect_data()

            # 直接替换整个配置数据，避免 dot-path 展开损坏包含点号的键
            self._config_service.replace_all_config(self._working_data)
            self._config_service.save_config()
            self.accept()
        except Exception as e:
            self.logger.error("保存配置失败: %s", e)
            QW.QMessageBox.critical(
                self, _("error", "Error"),
                f"{_('save_failed', 'Failed to save configuration')}: {e}"
            )

    def _populate_data(self):
        """用 _working_data 填充各页面"""
        self._page_battery.load_data(self._working_data.get("battery", {}))
        self._page_test.load_data(self._working_data.get("test", {}))
        self._page_equipment.load_data(self._working_data.get("test", {}).get("equipment", {}))

class _BatteryConfigPage(QW.QWidget):
    """电池配置编辑页面"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog

        layout = QW.QFormLayout(self)

        # 电池类型
        self._list_types = self._make_list_group("Battery Types")
        layout.addRow(self._list_types)

        # 构造方式
        self._list_construction = self._make_list_group("Construction Methods")
        layout.addRow(self._list_construction)

        # 规格型号（按类型分组：Coin Cell / Pouch Cell）
        self._spec_page = QW.QTabWidget()
        self._spec_coin = QW.QListWidget()
        self._spec_pouch = QW.QListWidget()
        self._spec_page.addTab(self._spec_coin, "Coin Cell")
        self._spec_page.addTab(self._spec_pouch, "Pouch Cell")
        spec_group = QW.QGroupBox("Specifications")
        spec_vbox = QW.QVBoxLayout(spec_group)
        spec_vbox.addWidget(self._spec_page)
        spec_btn_row = QW.QHBoxLayout()
        btn_add_spec = QW.QPushButton("+")
        btn_remove_spec = QW.QPushButton("×")
        spec_btn_row.addWidget(btn_add_spec)
        spec_btn_row.addWidget(btn_remove_spec)
        spec_btn_row.addStretch()
        spec_vbox.addLayout(spec_btn_row)
        btn_add_spec.clicked.connect(lambda: self._add_list_item(
            self._spec_page.currentWidget()))
        btn_remove_spec.clicked.connect(lambda: self._remove_list_item(
            self._spec_page.currentWidget()))
        layout.addRow(spec_group)

        # 规格方式
        self._list_spec_method = self._make_list_group("Specification Methods")
        layout.addRow(self._list_spec_method)

        # 制造商
        self._list_mfrs = self._make_list_group("Manufacturers")
        layout.addRow(self._list_mfrs)

        # Rules（文本框）
        self._text_rules = QW.QPlainTextEdit()
        self._text_rules.setPlaceholderText(
            "One rule per line, format: Type/Method/Capacity/MinCapacity/Required%/Voltage")
        layout.addRow("Rules:", self._text_rules)

        # 脉冲电流
        self._list_pulse = self._make_list_group("Pulse Currents")
        layout.addRow(self._list_pulse)

        # 截止电压
        self._list_voltage = self._make_list_group("Cut-off Voltages")
        layout.addRow(self._list_voltage)

    def _make_list_group(self, title: str) -> QW.QGroupBox:
        group = QW.QGroupBox(title)
        vbox = QW.QVBoxLayout(group)
        lw = QW.QListWidget()
        lw.setAlternatingRowColors(True)
        lw.itemDoubleClicked.connect(lambda item: lw.editItem(item))
        btn_row = QW.QHBoxLayout()
        btn_add = QW.QPushButton("+")
        btn_add.setFixedWidth(30)
        btn_remove = QW.QPushButton("×")
        btn_remove.setFixedWidth(30)
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_remove)
        btn_row.addStretch()
        vbox.addWidget(lw)
        vbox.addLayout(btn_row)
        btn_add.clicked.connect(lambda: self._add_list_item(lw))
        btn_remove.clicked.connect(lambda: self._remove_list_item(lw))
        return group

    def _add_list_item(self, lw):
        """在列表末尾添加可编辑项"""
        item = QW.QListWidgetItem("")
        item.setFlags(item.flags() | QC.Qt.ItemFlag.ItemIsEditable)
        lw.addItem(item)
        lw.editItem(item)

    def _remove_list_item(self, lw):
        """删除选中项"""
        for item in lw.selectedItems():
            lw.takeItem(lw.row(item))

    def load_data(self, data: dict):
        """从数据填充页面"""
        self._fill_list(self._list_types, data.get("types", []))
        self._fill_list(self._list_construction, data.get("constructionMethods", []))
        self._fill_list(self._spec_coin, data.get("specifications", {}).get("Coin Cell", []))
        self._fill_list(self._spec_pouch, data.get("specifications", {}).get("Pouch Cell", []))
        self._fill_list(self._list_spec_method, data.get("specificationMethods", []))
        self._fill_list(self._list_mfrs, data.get("manufacturers", []))
        self._text_rules.setPlainText("\n".join(data.get("rules", [])))
        self._fill_list(self._list_pulse, [str(v) for v in data.get("pulseCurrents", [])])
        self._fill_list(self._list_voltage, [str(v) for v in data.get("cutOffVoltages", [])])

    def _fill_list(self, lw, items: list):
        if isinstance(lw, QW.QGroupBox):
            lw = lw.findChild(QW.QListWidget)
        if lw is None:
            return
        lw.clear()
        for item in items:
            li = QW.QListWidgetItem(str(item))
            li.setFlags(li.flags() | QC.Qt.ItemFlag.ItemIsEditable)
            lw.addItem(li)

    def _read_list(self, group_or_lw) -> list:
        if isinstance(group_or_lw, QW.QGroupBox):
            lw = group_or_lw.findChild(QW.QListWidget)
        else:
            lw = group_or_lw
        if lw is None:
            return []
        return [lw.item(i).text().strip() for i in range(lw.count()) if lw.item(i).text().strip()]

    def collect_data(self):
        """将页面数据写回 _working_data"""
        battery = self._dialog._working_data.setdefault("battery", {})
        battery["types"] = self._read_list(self._list_types)
        battery["constructionMethods"] = self._read_list(self._list_construction)
        battery["specifications"] = {
            "Coin Cell": self._read_list(self._spec_coin),
            "Pouch Cell": self._read_list(self._spec_pouch),
        }
        battery["specificationMethods"] = self._read_list(self._list_spec_method)
        battery["manufacturers"] = self._read_list(self._list_mfrs)
        battery["rules"] = [r.strip() for r in self._text_rules.toPlainText().split("\n") if r.strip()]
        battery["pulseCurrents"] = self._parse_float_list(self._read_list(self._list_pulse))
        battery["cutOffVoltages"] = self._parse_float_list(self._read_list(self._list_voltage))

    @staticmethod
    def _parse_float_list(raw: list) -> list:
        """安全转换字符串列表为浮点数，跳过无效值"""
        result = []
        for v in raw:
            try:
                result.append(float(v))
            except ValueError:
                logging.getLogger(__name__).warning("Ignoring non-float value: %s", v)
        return result


class _TestConfigPage(QW.QWidget):
    """测试配置编辑页面"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog

        layout = QW.QFormLayout(self)
        self._list_tested_by = self._make_list_widget("Tested By")
        layout.addRow(self._list_tested_by)

    def _make_list_widget(self, title: str) -> QW.QGroupBox:
        group = QW.QGroupBox(title)
        vbox = QW.QVBoxLayout(group)
        lw = QW.QListWidget()
        lw.setAlternatingRowColors(True)
        lw.itemDoubleClicked.connect(lambda item: lw.editItem(item))
        btn_row = QW.QHBoxLayout()
        btn_add = QW.QPushButton("+")
        btn_add.setFixedWidth(30)
        btn_remove = QW.QPushButton("×")
        btn_remove.setFixedWidth(30)
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_remove)
        btn_row.addStretch()
        vbox.addWidget(lw)
        vbox.addLayout(btn_row)
        btn_add.clicked.connect(lambda: self._add_item(lw))
        btn_remove.clicked.connect(lambda: self._remove_item(lw))
        return group

    def _add_item(self, lw):
        item = QW.QListWidgetItem("")
        item.setFlags(item.flags() | QC.Qt.ItemFlag.ItemIsEditable)
        lw.addItem(item)
        lw.editItem(item)

    def _remove_item(self, lw):
        for item in lw.selectedItems():
            lw.takeItem(lw.row(item))

    def _fill_list(self, lw, items: list):
        if isinstance(lw, QW.QGroupBox):
            lw = lw.findChild(QW.QListWidget)
        if lw is None:
            return
        lw.clear()
        for item in items:
            li = QW.QListWidgetItem(str(item))
            li.setFlags(li.flags() | QC.Qt.ItemFlag.ItemIsEditable)
            lw.addItem(li)

    def _read_list(self, obj) -> list:
        if isinstance(obj, QW.QGroupBox):
            lw = obj.findChild(QW.QListWidget)
            if lw:
                return [lw.item(i).text().strip() for i in range(lw.count()) if lw.item(i).text().strip()]
        return []

    @staticmethod
    def _location_from_equipment(loc_key: str, test_equipment: str) -> str:
        """从 equipment 键和 testEquipment 值生成 tester location 字符串

        Format: 提取型号 + ({lab}) + site，保证 site 和 lab 作为子串出现在结果中，
        满足 table_manager 的 substring 匹配。
        """
        parts = loc_key.split(".")
        if len(parts) != 2:
            return loc_key
        site, lab = parts
        model = test_equipment.replace("NEWARE Battery Testing System ", "").strip()
        lab_display = lab + "." if lab == "Qual" else lab
        return f"{model} ({lab_display}), {site}"

    def load_data(self, data: dict):
        # Tester locations 从 equipment 数据自动生成，不再编辑
        equipment = self._dialog._working_data.get("test", {}).get("equipment", {})
        locations = []
        for loc_key, info in equipment.items():
            eq = info.get("testEquipment", "")
            locations.append(self._location_from_equipment(loc_key, eq))
        # 写回 working_data 供后续 collect_data 使用
        self._dialog._working_data.setdefault("test", {})["locations"] = locations

        self._fill_list(self._list_tested_by.findChild(QW.QListWidget), data.get("testedBy", []))

    def collect_data(self):
        test = self._dialog._working_data.setdefault("test", {})
        # 从当前 equipment 重新生成 locations
        equipment = test.get("equipment", {})
        locations = []
        for loc_key, info in equipment.items():
            eq = info.get("testEquipment", "")
            locations.append(self._location_from_equipment(loc_key, eq))
        test["locations"] = locations
        test["testedBy"] = self._read_list(self._list_tested_by)


class _EquipmentPage(QW.QWidget):
    """设备信息编辑页面"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog
        self._data: Dict[str, dict] = {}

        layout = QW.QVBoxLayout(self)

        # 表格
        self._table = QW.QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Location", "Test Equipment", "Model"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSelectionBehavior(QW.QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.doubleClicked.connect(self._on_edit_row)

        btn_row = QW.QHBoxLayout()
        btn_add = QW.QPushButton("+ Add Location")
        btn_copy = QW.QPushButton("Copy")
        btn_edit = QW.QPushButton("Edit")
        btn_remove = QW.QPushButton("× Remove")
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_copy)
        btn_row.addWidget(btn_edit)
        btn_row.addWidget(btn_remove)
        btn_row.addStretch()

        btn_add.clicked.connect(self._on_add_location)
        btn_copy.clicked.connect(self._on_copy_location)
        btn_edit.clicked.connect(self._on_edit_selected)
        btn_remove.clicked.connect(self._on_remove_location)

        layout.addWidget(self._table)
        layout.addLayout(btn_row)

    def load_data(self, data: dict):
        self._data = data
        self._refresh_table()

    def _refresh_table(self):
        self._table.setRowCount(0)
        for loc_key, info in self._data.items():
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QW.QTableWidgetItem(loc_key))
            self._table.setItem(row, 1, QW.QTableWidgetItem(
                info.get("testEquipment", "")))
            self._table.setItem(row, 2, QW.QTableWidgetItem(
                info.get("testUnits", {}).get("model", "")))

    def _on_edit_row(self, index):
        self._edit_location(index.row())

    def _on_edit_selected(self):
        rows = self._table.selectionModel().selectedRows()
        if rows:
            self._edit_location(rows[0].row())

    def _edit_location(self, row: int):
        loc_key = self._table.item(row, 0).text()
        info = self._data.get(loc_key, {})
        dialog = _EquipmentEditDialog(loc_key, info, self)
        if dialog.exec():
            new_key, new_info = dialog.get_data()
            if new_key != loc_key:
                del self._data[loc_key]
            self._data[new_key] = new_info
            self._refresh_table()

    def _on_add_location(self):
        dialog = _EquipmentEditDialog("", {}, self)
        if dialog.exec():
            key, info = dialog.get_data()
            if key and key not in self._data:
                self._data[key] = info
                self._refresh_table()

    def _on_copy_location(self):
        """复制选中行，生成新的 location key"""
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        loc_key = self._table.item(row, 0).text()
        info = self._data.get(loc_key)
        if info is None:
            return

        new_key = loc_key + " (Copy)"
        suffix = 1
        while new_key in self._data:
            suffix += 1
            new_key = f"{loc_key} (Copy {suffix})"

        self._data[new_key] = copy.deepcopy(info)
        self._refresh_table()

    def _on_remove_location(self):
        rows = self._table.selectionModel().selectedRows()
        for index in sorted(rows, reverse=True):
            loc_key = self._table.item(index.row(), 0).text()
            self._data.pop(loc_key, None)
        self._refresh_table()

    def collect_data(self):
        self._dialog._working_data.setdefault("test", {})["equipment"] = self._data


class _EquipmentEditDialog(QW.QDialog):
    """设备信息编辑对话框"""

    def __init__(self, loc_key: str, data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Equipment Info" if loc_key else "Add Equipment Info")
        self.setMinimumWidth(500)

        layout = QW.QVBoxLayout(self)

        form = QW.QFormLayout()

        self._edit_key = QW.QLineEdit(loc_key)
        form.addRow("Location Key:", self._edit_key)

        self._edit_equipment = QW.QLineEdit(data.get("testEquipment", ""))
        form.addRow("Test Equipment:", self._edit_equipment)

        # Software Versions
        sv = data.get("softwareVersions", {})
        self._edit_sv_server = QW.QLineEdit(sv.get("btsServer", ""))
        self._edit_sv_client = QW.QLineEdit(sv.get("btsClient", ""))
        self._edit_sv_da = QW.QLineEdit(sv.get("btsda", ""))
        form.addRow("BTS Server:", self._edit_sv_server)
        form.addRow("BTS Client:", self._edit_sv_client)
        form.addRow("BTSDA:", self._edit_sv_da)

        # Middle Machines
        mm = data.get("middleMachines", {})
        self._edit_mm_model = QW.QLineEdit(mm.get("model", ""))
        self._edit_mm_hw = QW.QLineEdit(mm.get("hardwareVersion", ""))
        self._edit_mm_sn = QW.QLineEdit(mm.get("serialNumber", ""))
        self._edit_mm_fw = QW.QLineEdit(mm.get("firmwareVersion", ""))
        self._edit_mm_dt = QW.QLineEdit(mm.get("deviceType", ""))
        form.addRow("MM Model:", self._edit_mm_model)
        form.addRow("MM HW Ver:", self._edit_mm_hw)
        form.addRow("MM S/N:", self._edit_mm_sn)
        form.addRow("MM FW Ver:", self._edit_mm_fw)
        form.addRow("MM Device Type:", self._edit_mm_dt)

        # Test Units
        tu = data.get("testUnits", {})
        self._edit_tu_model = QW.QLineEdit(tu.get("model", ""))
        self._edit_tu_hw = QW.QLineEdit(tu.get("hardwareVersion", ""))
        self._edit_tu_fw = QW.QLineEdit(tu.get("firmwareVersion", ""))
        form.addRow("TU Model:", self._edit_tu_model)
        form.addRow("TU HW Ver:", self._edit_tu_hw)
        form.addRow("TU FW Ver:", self._edit_tu_fw)

        layout.addLayout(form)

        btn_layout = QW.QHBoxLayout()
        btn_ok = QW.QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QW.QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def get_data(self) -> tuple:
        key = self._edit_key.text().strip()
        info = {
            "testEquipment": self._edit_equipment.text().strip(),
            "softwareVersions": {
                "btsServer": self._edit_sv_server.text().strip(),
                "btsClient": self._edit_sv_client.text().strip(),
                "btsda": self._edit_sv_da.text().strip(),
            },
            "middleMachines": {
                "model": self._edit_mm_model.text().strip(),
                "hardwareVersion": self._edit_mm_hw.text().strip(),
                "serialNumber": self._edit_mm_sn.text().strip(),
                "firmwareVersion": self._edit_mm_fw.text().strip(),
                "deviceType": self._edit_mm_dt.text().strip(),
            },
            "testUnits": {
                "model": self._edit_tu_model.text().strip(),
                "hardwareVersion": self._edit_tu_hw.text().strip(),
                "firmwareVersion": self._edit_tu_fw.text().strip(),
            },
        }
        return key, info
