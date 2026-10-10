"""设备信息编辑页面"""

import copy

from PyQt6 import QtWidgets as QW

from battery_analysis.i18n.language_manager import _
from battery_analysis.main.ui_components.config_dialog.equipment_edit_dialog import (
    _EquipmentEditDialog,
)


class _EquipmentPage(QW.QWidget):
    """设备信息编辑页面"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog
        self._data: dict[str, dict] = {}

        layout = QW.QVBoxLayout(self)

        self._table = QW.QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["No.", "Location", "Test Equipment", "Model"])
        self._table.verticalHeader().hide()
        self._table.setColumnWidth(0, 120)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSelectionBehavior(QW.QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.doubleClicked.connect(self._on_edit_row)
        # 设置表头背景颜色，避免黑色看不清
        self._table.setStyleSheet("QTableWidget::item { padding: 4px; } QHeaderView::section { background-color: #4a90d9; color: white; padding: 4px; border: 1px solid #357abd; }")

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
            self._table.setItem(
                row, 3, QW.QTableWidgetItem(info.get("testUnits", {}).get("model", ""))
            )

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
