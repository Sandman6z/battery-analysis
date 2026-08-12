"""
配置管理对话框
提供左侧分类导航、右侧编辑器的 master-detail UI，用于管理应用的数据字典配置。
"""

import copy
import logging
from typing import Dict

from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC

from battery_analysis.i18n.language_manager import _
from battery_analysis.utils.battery_classifier import derive_specifications
from battery_analysis.utils.config_defaults import DEFAULT_CONFIG

RULE_COLUMNS = [
    "Specification", "Spec Method", "Datasheet Capacity",
    "Calculation Capacity", "Required Useable Capacity", "Coefficient",
]


class ConfigDialog(QW.QDialog):
    """配置管理主对话框（master-detail 布局）"""

    _CATEGORIES = ["Battery", "Test", "Equipment"]

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._config_service = main_window._get_service("config")
        if self._config_service is None:
            raise RuntimeError("ConfigService not available — cannot open Configuration dialog")

        # 从 ConfigService 加载当前数据（深拷贝，取消保存才写回）
        raw_data = self._config_service.get_config_value("")
        self._working_data = copy.deepcopy(raw_data) if isinstance(raw_data, dict) else {}

        self.setWindowTitle(_("Configuration"))
        self.setMinimumSize(760, 560)
        self._setup_ui()
        self._populate_data()

    def _setup_ui(self):
        layout = QW.QVBoxLayout(self)

        # 左导航 + 右堆叠（master-detail）
        splitter = QW.QSplitter(QC.Qt.Orientation.Horizontal)
        self._nav = QW.QListWidget()
        self._nav.setFixedWidth(150)
        for name in self._CATEGORIES:
            QW.QListWidgetItem(_(name), self._nav)
        self._nav.setCurrentRow(0)

        self._stack = QW.QStackedWidget()
        self._page_battery = _BatteryConfigPage(self)
        self._page_test = _TestConfigPage(self)
        self._page_equipment = _EquipmentPage(self)
        self._stack.addWidget(self._page_battery)
        self._stack.addWidget(self._page_test)
        self._stack.addWidget(self._page_equipment)
        self._nav.currentRowChanged.connect(self._stack.setCurrentIndex)

        splitter.addWidget(self._nav)
        splitter.addWidget(self._stack)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, 1)

        # 底部按钮栏
        btn_layout = QW.QHBoxLayout()
        btn_reset = QW.QPushButton(_("Reset Defaults"))
        btn_reset.clicked.connect(self._on_reset_defaults)
        btn_save = QW.QPushButton(_("Save"))
        btn_save.clicked.connect(self._on_save)
        btn_cancel = QW.QPushButton(_("Cancel"))
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _on_reset_defaults(self):
        reply = QW.QMessageBox.question(
            self, _("Reset Defaults"),
            _("Reset all configuration to default values? This cannot be undone."),
            QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
        )
        if reply == QW.QMessageBox.StandardButton.Yes:
            self._working_data = copy.deepcopy(DEFAULT_CONFIG)
            self._populate_data()

    def _on_save(self):
        try:
            self._page_battery.collect_data()
            self._page_equipment.collect_data()
            self._page_test.collect_data()
            self._config_service.replace_all_config(self._working_data)
            self._config_service.save_config()
            self.accept()
        except Exception as e:
            self.logger.error("Failed to save configuration: %s", e)
            QW.QMessageBox.critical(
                self, _("Error"),
                f"{_('Failed to save configuration')}: {e}"
            )

    def _populate_data(self):
        wd = self._working_data if isinstance(self._working_data, dict) else {}
        self._page_battery.load_data(wd.get("battery", {}))
        self._page_test.load_data(wd.get("test", {}))
        self._page_equipment.load_data(wd.get("test", {}).get("equipment", {}))


class _ListEditor(QW.QGroupBox):
    """可增删的行级列表编辑器（Manufacturers 等列表类配置使用）"""

    def __init__(self, title: str, editable: bool = True):
        super().__init__(title)
        vbox = QW.QVBoxLayout(self)
        self._lw = QW.QListWidget()
        self._lw.setAlternatingRowColors(True)
        self._lw.setMinimumHeight(110)
        if editable:
            self._lw.itemDoubleClicked.connect(lambda item: self._lw.editItem(item))
        vbox.addWidget(self._lw)
        if editable:
            btn_row = QW.QHBoxLayout()
            btn_add = QW.QPushButton("+")
            btn_add.setFixedSize(22, 22)
            btn_remove = QW.QPushButton("×")
            btn_remove.setFixedSize(22, 22)
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_remove)
            btn_row.addStretch()
            vbox.addLayout(btn_row)
            btn_add.clicked.connect(self._add_item)
            btn_remove.clicked.connect(self._remove_item)

    def _add_item(self):
        item = QW.QListWidgetItem("")
        item.setFlags(item.flags() | QC.Qt.ItemFlag.ItemIsEditable)
        self._lw.addItem(item)
        self._lw.editItem(item)

    def _remove_item(self):
        for item in self._lw.selectedItems():
            self._lw.takeItem(self._lw.row(item))

    def set_items(self, items) -> None:
        self._lw.clear()
        for value in items:
            item = QW.QListWidgetItem(str(value))
            item.setFlags(item.flags() | QC.Qt.ItemFlag.ItemIsEditable)
            self._lw.addItem(item)

    def items(self) -> list:
        return [self._lw.item(i).text().strip() for i in range(self._lw.count())
                if self._lw.item(i).text().strip()]


class _RulesEditor(QW.QGroupBox):
    """Rules 表格编辑器——每一行一条规则，6 列与 rule_parts[0..5] 对应"""

    def __init__(self, title: str = "Rules"):
        super().__init__(title)
        vbox = QW.QVBoxLayout(self)
        self._table = QW.QTableWidget(0, len(RULE_COLUMNS))
        self._table.setHorizontalHeaderLabels(RULE_COLUMNS)
        self._table.verticalHeader().hide()
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSelectionBehavior(QW.QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setMinimumHeight(150)
        vbox.addWidget(self._table)

        btn_row = QW.QHBoxLayout()
        btn_add = QW.QPushButton("+ Add Rule")
        btn_remove = QW.QPushButton("× Remove")
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_remove)
        btn_row.addStretch()
        vbox.addLayout(btn_row)
        btn_add.clicked.connect(self._add_row)
        btn_remove.clicked.connect(self._remove_rows)

    def _add_row(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        for col in range(len(RULE_COLUMNS)):
            self._table.setItem(row, col, QW.QTableWidgetItem(""))
        self._table.setCurrentCell(row, 0)
        self._table.editItem(self._table.item(row, 0))

    def _remove_rows(self):
        rows = sorted({idx.row() for idx in self._table.selectionModel().selectedRows()},
                      reverse=True)
        for row in rows:
            self._table.removeRow(row)

    def set_rules(self, rules: list) -> None:
        self._table.setRowCount(0)
        for rule in rules:
            parts = rule.split("/")
            row = self._table.rowCount()
            self._table.insertRow(row)
            for col in range(len(RULE_COLUMNS)):
                value = parts[col] if col < len(parts) else ""
                self._table.setItem(row, col, QW.QTableWidgetItem(value))

    def rules(self) -> list:
        result = []
        for row in range(self._table.rowCount()):
            parts = []
            for col in range(len(RULE_COLUMNS)):
                item = self._table.item(row, col)
                parts.append(item.text().strip() if item else "")
            if any(parts):
                result.append("/".join(parts))
        return result


class _BatteryConfigPage(QW.QWidget):
    """电池配置编辑页面（逐条化 + Specifications 派生只读）"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog

        main_layout = QW.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QW.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QW.QFrame.Shape.NoFrame)

        content = QW.QWidget()
        layout = QW.QVBoxLayout(content)

        # ── Test Data Dictionary ──
        dict_group = QW.QGroupBox(_("Test Data Dictionary"))
        dict_layout = QW.QVBoxLayout(dict_group)

        self._list_types = _ListEditor(_("Battery Types"), editable=False)
        dict_layout.addWidget(self._list_types)

        self._rules_editor = _RulesEditor(_("Rules"))
        dict_layout.addWidget(self._rules_editor)

        # Specifications（从 Rules 派生，只读展示，无增删按钮）
        self._spec_page = QW.QTabWidget()
        self._spec_coin = QW.QListWidget()
        self._spec_coin.setSelectionMode(QW.QAbstractItemView.SelectionMode.NoSelection)
        self._spec_pouch = QW.QListWidget()
        self._spec_pouch.setSelectionMode(QW.QAbstractItemView.SelectionMode.NoSelection)
        self._spec_page.addTab(self._spec_coin, "Coin Cell")
        self._spec_page.addTab(self._spec_pouch, "Pouch Cell")
        self._spec_page.setMinimumHeight(140)
        spec_group = QW.QGroupBox(_("Specifications"))
        spec_vbox = QW.QVBoxLayout(spec_group)
        spec_vbox.addWidget(self._spec_page)
        dict_layout.addWidget(spec_group)

        self._list_construction = _ListEditor(_("Construction Methods"))
        dict_layout.addWidget(self._list_construction)

        self._list_spec_method = _ListEditor(_("Specification Methods"))
        dict_layout.addWidget(self._list_spec_method)

        self._list_mfrs = _ListEditor(_("Manufacturers"))
        dict_layout.addWidget(self._list_mfrs)

        layout.addWidget(dict_group)

        # ── Test Parameters ──
        params_group = QW.QGroupBox(_("Test Parameters"))
        params_layout = QW.QVBoxLayout(params_group)

        self._list_pulse = _ListEditor(_("Pulse Currents"))
        params_layout.addWidget(self._list_pulse)

        self._list_voltage = _ListEditor(_("Cut-off Voltages"))
        params_layout.addWidget(self._list_voltage)

        layout.addWidget(params_group)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Rules 变更时自动刷新 Specifications
        model = self._rules_editor._table.model()
        model.rowsInserted.connect(self._on_rules_changed)
        model.rowsRemoved.connect(self._on_rules_changed)
        model.dataChanged.connect(self._on_rules_changed)

    def _on_rules_changed(self):
        self._refresh_specs_from_rules(self._rules_editor.rules())

    def _refresh_specs_from_rules(self, rules: list) -> None:
        self._spec_coin.clear()
        self._spec_pouch.clear()
        specs = derive_specifications(rules)
        for spec in specs.get("Coin Cell", []):
            self._spec_coin.addItem(spec)
        for spec in specs.get("Pouch Cell", []):
            self._spec_pouch.addItem(spec)

    def load_data(self, data: dict) -> None:
        rules = data.get("rules", [])
        self._list_types.set_items(data.get("types", []))
        self._list_construction.set_items(data.get("constructionMethods", []))
        self._rules_editor.set_rules(rules)
        self._refresh_specs_from_rules(rules)
        self._list_spec_method.set_items(data.get("specificationMethods", []))
        self._list_mfrs.set_items(data.get("manufacturers", []))
        self._list_pulse.set_items([str(v) for v in data.get("pulseCurrents", [])])
        self._list_voltage.set_items([str(v) for v in data.get("cutOffVoltages", [])])

    def collect_data(self) -> None:
        battery = self._dialog._working_data.setdefault("battery", {})
        battery["types"] = self._list_types.items()
        battery["constructionMethods"] = self._list_construction.items()
        rules = self._rules_editor.rules()
        battery["rules"] = rules
        # Specifications 从 Rules 自动派生，不直接读取 UI
        battery["specifications"] = derive_specifications(rules)
        battery["specificationMethods"] = self._list_spec_method.items()
        battery["manufacturers"] = self._list_mfrs.items()
        battery["pulseCurrents"] = self._parse_float_list(self._list_pulse.items())
        battery["cutOffVoltages"] = self._parse_float_list(self._list_voltage.items())

    @staticmethod
    def _parse_float_list(raw: list) -> list:
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

        layout = QW.QVBoxLayout(self)
        self._list_tested_by = _ListEditor(_("Tested By"))
        layout.addWidget(self._list_tested_by)
        layout.addStretch()

    @staticmethod
    def _location_from_equipment(loc_key: str, test_equipment: str) -> str:
        parts = loc_key.split(".")
        if len(parts) != 2:
            return loc_key
        site, lab = parts
        prefix = "NEWARE Battery Testing System "
        model = test_equipment[len(prefix):].strip() if test_equipment.startswith(prefix) else test_equipment.strip()
        lab_display = lab + "." if lab == "Qual" else lab
        return f"{model} ({lab_display}), {site}"

    def load_data(self, data: dict) -> None:
        # Tester locations 从 equipment 数据自动生成
        equipment = self._dialog._working_data.get("test", {}).get("equipment", {})
        locations = []
        for loc_key, info in equipment.items():
            locations.append(self._location_from_equipment(loc_key, info.get("testEquipment", "")))
        self._dialog._working_data.setdefault("test", {})["locations"] = locations
        self._list_tested_by.set_items(data.get("testedBy", []))

    def collect_data(self) -> None:
        test = self._dialog._working_data.setdefault("test", {})
        equipment = test.get("equipment", {})
        locations = []
        for loc_key, info in equipment.items():
            locations.append(self._location_from_equipment(loc_key, info.get("testEquipment", "")))
        test["locations"] = locations
        test["testedBy"] = self._list_tested_by.items()


class _EquipmentPage(QW.QWidget):
    """设备信息编辑页面"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog
        self._data: Dict[str, dict] = {}

        layout = QW.QVBoxLayout(self)

        self._table = QW.QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["No.", "Location", "Test Equipment", "Model"])
        self._table.verticalHeader().hide()
        self._table.setColumnWidth(0, 120)
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

    def load_data(self, data: dict) -> None:
        self._data = data if isinstance(data, dict) else {}
        self._refresh_table()

    def _refresh_table(self) -> None:
        self._table.setRowCount(0)
        for i, (loc_key, info) in enumerate(self._data.items()):
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QW.QTableWidgetItem(str(i + 1)))
            self._table.setItem(row, 1, QW.QTableWidgetItem(loc_key))
            self._table.setItem(row, 2, QW.QTableWidgetItem(info.get("testEquipment", "")))
            self._table.setItem(row, 3, QW.QTableWidgetItem(info.get("testUnits", {}).get("model", "")))

    def _on_edit_row(self, index):
        self._edit_location(index.row())

    def _on_edit_selected(self):
        rows = self._table.selectionModel().selectedRows()
        if rows:
            self._edit_location(rows[0].row())

    def _edit_location(self, row: int):
        loc_key = self._table.item(row, 1).text()
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
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        loc_key = self._table.item(row, 1).text()
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
            loc_key = self._table.item(index.row(), 1).text()
            self._data.pop(loc_key, None)
        self._refresh_table()

    def collect_data(self) -> None:
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

        sv = data.get("softwareVersions", {})
        self._edit_sv_server = QW.QLineEdit(sv.get("btsServer", ""))
        self._edit_sv_client = QW.QLineEdit(sv.get("btsClient", ""))
        self._edit_sv_da = QW.QLineEdit(sv.get("btsda", ""))
        form.addRow("BTS Server:", self._edit_sv_server)
        form.addRow("BTS Client:", self._edit_sv_client)
        form.addRow("BTSDA:", self._edit_sv_da)

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
