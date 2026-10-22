"""Rules 表格编辑器（按 Coin Cell / Pouch Cell 分栏）"""

from PyQt6 import QtWidgets as QW

from battery_analysis.main.ui_components.config_dialog.constants import (
    RULE_COLUMNS,
    SPEC_METHOD_COL,
)
from battery_analysis.utils.battery_classifier import (
    classify_spec,
    extract_capacity,
    extract_spec_name,
)


class _RulesEditor(QW.QGroupBox):
    """Rules 表格编辑器——按电池类型分成 Coin Cell / Pouch Cell 两个分栏，
    每一行一条规则，6 列与 rule_parts[0..5] 对应"""

    def __init__(self, title: str = "Rules"):
        super().__init__(title)
        self._methods: list[str] = []
        vbox = QW.QVBoxLayout(self)

        # 分栏形式与 Specifications 一致：Coin Cell / Pouch Cell
        self._tabs = QW.QTabWidget()
        self._table_coin = self._make_table()
        self._table_pouch = self._make_table()
        self._tabs.addTab(self._table_coin, "Coin Cell")
        self._tabs.addTab(self._table_pouch, "Pouch Cell")
        self._tabs.setMinimumHeight(180)
        vbox.addWidget(self._tabs)
        self._tables = [self._table_coin, self._table_pouch]

        btn_row = QW.QHBoxLayout()
        btn_add = QW.QPushButton("+ Add Rule")
        btn_remove = QW.QPushButton("× Remove")
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_remove)
        btn_row.addStretch()
        vbox.addLayout(btn_row)
        btn_add.clicked.connect(self._add_row)
        btn_remove.clicked.connect(self._remove_rows)

    @staticmethod
    def _make_table() -> QW.QTableWidget:
        table = QW.QTableWidget(0, len(RULE_COLUMNS))
        table.setHorizontalHeaderLabels(RULE_COLUMNS)
        vertical_header = table.verticalHeader()
        horizontal_header = table.horizontalHeader()
        if vertical_header is not None:
            vertical_header.hide()
        if horizontal_header is not None:
            horizontal_header.setStretchLastSection(True)
        table.setSelectionBehavior(QW.QAbstractItemView.SelectionBehavior.SelectRows)
        table.setMinimumHeight(150)
        # 设置表头背景颜色，避免黑色看不清
        table.setStyleSheet("QTableWidget::item { padding: 4px; } QHeaderView::section { background-color: #4a90d9; color: white; padding: 4px; border: 1px solid #357abd; }")
        return table

    def table_models(self) -> list:
        """两个表格的 model，供上层连接变更信号"""
        return [table.model() for table in self._tables]

    def set_methods(self, methods: list) -> None:
        """设置 Spec Method 列下拉框的可选项（来自 battery.specificationMethods，
        该列不可手输，只能从已有 method 中选择）"""
        self._methods = [str(m).strip() for m in methods if str(m).strip()]
        for table in self._tables:
            for row in range(table.rowCount()):
                widget = table.cellWidget(row, SPEC_METHOD_COL)
                if isinstance(widget, QW.QComboBox):
                    value = widget.currentText().strip()
                else:
                    item = table.item(row, SPEC_METHOD_COL)
                    value = item.text().strip() if item else ""
                self._set_method_combo(table, row, value)

    def _make_method_combo(self, value: str) -> QW.QComboBox:
        combo = QW.QComboBox()
        combo.setEditable(False)
        combo.addItems(self._methods)
        if value:
            idx = combo.findText(value)
            if idx < 0:
                # 规则里已有但方法列表缺失的值：保留显示，避免静默丢数据
                combo.addItem(value)
                idx = combo.findText(value)
            combo.setCurrentIndex(idx)
        else:
            combo.setCurrentIndex(-1)
        return combo

    def _set_method_combo(self, table: QW.QTableWidget, row: int, value: str = "") -> None:
        table.setItem(row, SPEC_METHOD_COL, None)
        table.setCellWidget(row, SPEC_METHOD_COL, self._make_method_combo(value))

    @staticmethod
    def _cell_type(rule: str) -> str:
        """按型号名/容量判定规则归属的分栏（与 derive_specifications 同源）"""
        return classify_spec(extract_spec_name(rule), extract_capacity(rule))

    def _active_table(self) -> QW.QTableWidget:
        return self._tables[self._tabs.currentIndex()]

    def _add_row(self):
        table = self._active_table()
        row = table.rowCount()
        table.insertRow(row)
        for col in range(len(RULE_COLUMNS)):
            table.setItem(row, col, QW.QTableWidgetItem(""))
        self._set_method_combo(table, row)
        table.setCurrentCell(row, 0)
        table.editItem(table.item(row, 0))

    def _remove_rows(self):
        table = self._active_table()
        rows = sorted(
            {idx.row() for idx in table.selectionModel().selectedRows()}, reverse=True
        )
        for row in rows:
            table.removeRow(row)

    def _fill_table(self, table: QW.QTableWidget, rules: list) -> None:
        table.setRowCount(0)
        for rule in rules:
            parts = rule.split("/")
            row = table.rowCount()
            table.insertRow(row)
            for col in range(len(RULE_COLUMNS)):
                value = parts[col] if col < len(parts) else ""
                table.setItem(row, col, QW.QTableWidgetItem(value))
            method = parts[SPEC_METHOD_COL] if len(parts) > SPEC_METHOD_COL else ""
            self._set_method_combo(table, row, method)

    @staticmethod
    def _read_table(table: QW.QTableWidget) -> list:
        result = []
        for row in range(table.rowCount()):
            parts = []
            for col in range(len(RULE_COLUMNS)):
                widget = table.cellWidget(row, col)
                if isinstance(widget, QW.QComboBox):
                    parts.append(widget.currentText().strip())
                    continue
                item = table.item(row, col)
                parts.append(item.text().strip() if item else "")
            if any(parts):
                result.append("/".join(parts))
        return result

    def set_rules(self, rules: list) -> None:
        coin: list[str] = []
        pouch: list[str] = []
        for rule in rules:
            (pouch if self._cell_type(rule) == "Pouch Cell" else coin).append(rule)
        self._fill_table(self._table_coin, coin)
        self._fill_table(self._table_pouch, pouch)

    def rules(self) -> list:
        """合并两个分栏的规则（Coin Cell 在前，Pouch Cell 在后）"""
        return self._read_table(self._table_coin) + self._read_table(self._table_pouch)
