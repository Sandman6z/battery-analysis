"""
数据错误恢复模块

处理数据加载错误时为用户提供恢复选项（重新选择目录、使用默认配置、取消）
"""

import logging
from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC
from PyQt6 import QtGui as QG

logger = logging.getLogger(__name__)


class DataErrorRecoveryHandler:
    """处理数据相关错误的恢复选项"""

    def __init__(self, main_window):
        self.main_window = main_window
        self._error_option = None

    def handle_error_recovery(self, error_msg: str):
        """处理数据错误，显示恢复选项对话框"""
        logger.error("处理数据错误恢复: %s", error_msg)

        dialog = QW.QDialog(self.main_window)
        dialog.setWindowTitle("数据加载错误 - 恢复选项")
        dialog.setModal(True)
        dialog.resize(500, 300)
        dialog.setWindowModality(QC.Qt.WindowModality.ApplicationModal)

        layout = QW.QVBoxLayout(dialog)

        title_label = QW.QLabel("无法加载电池数据，请选择如何继续:")
        title_font = QG.QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        layout.addSpacing(10)

        error_label = QW.QLabel(f"错误详情: {error_msg}")
        error_label.setWordWrap(True)
        error_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(error_label)
        layout.addSpacing(15)

        details_label = QW.QLabel("请选择以下恢复选项之一:")
        details_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(details_label)

        button_layout = QW.QHBoxLayout()
        button_layout.addStretch()

        retry_button = QW.QPushButton("重新选择数据目录")
        retry_button.clicked.connect(lambda: self._handle_option(dialog, "retry"))
        button_layout.addWidget(retry_button)

        default_button = QW.QPushButton("使用默认配置")
        default_button.clicked.connect(lambda: self._handle_option(dialog, "default"))
        button_layout.addWidget(default_button)

        cancel_button = QW.QPushButton("取消")
        cancel_button.clicked.connect(lambda: self._handle_option(dialog, "cancel"))
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self._error_option = None
        dialog.exec()

        if self._error_option == "retry":
            self._open_data_directory_dialog()
        elif self._error_option == "default":
            pass
        else:
            pass

    def _handle_option(self, dialog, option):
        self._error_option = option
        dialog.accept()

    def _open_data_directory_dialog(self):
        from battery_analysis.i18n.language_manager import _

        self.main_window.statusBar_BatteryAnalysis.showMessage(
            _("selecting_data_directory", "选择数据目录...")
        )

        directory = QW.QFileDialog.getExistingDirectory(
            self.main_window,
            _("select_data_directory", "选择数据目录"),
            self.main_window.lineEdit_InputPath.text()
        )

        if directory:
            self.main_window.lineEdit_InputPath.setText(directory)
            if hasattr(self.main_window, 'data_processor'):
                self.main_window.data_processor.analyze_data()

        self.main_window.statusBar_BatteryAnalysis.showMessage(
            _("status_ready", "状态:就绪")
        )
