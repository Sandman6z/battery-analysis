"""可增删的行级列表编辑器（配置对话框通用组件）"""

from PyQt6 import QtCore as QC
from PyQt6 import QtWidgets as QW


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
            btn_add.setFixedSize(32, 32)
            btn_remove = QW.QPushButton("×")
            btn_remove.setFixedSize(32, 32)
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
        return [
            self._lw.item(i).text().strip()
            for i in range(self._lw.count())
            if self._lw.item(i).text().strip()
        ]
