"""报告管理类"""

import logging
import os
import re
from pathlib import Path

from PyQt6 import QtWidgets as QW

from battery_analysis.main.business_logic.version_manager import parse_version


class ReportManager:
    """报告管理类"""

    def __init__(self, main_window=None):
        """
        初始化报告管理器

        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

    # ── 工具方法 ────────────────────────────────────────────────

    def _get_output_path(self) -> str:
        if self.main_window:
            return self.main_window.lineEdit_OutputPath.text()
        return ""

    def _get_version(self) -> str:
        if self.main_window:
            return self.main_window.lineEdit_Version.text()
        return ""

    # ── 业务方法 ────────────────────────────────────────────────

    def open_report(self, dialog=None, *, report_path=None):
        """打开实际交付的报告，或当前输出根内精确匹配版本的报告。"""
        try:
            if report_path is not None:
                target_docx = Path(report_path)
                if not target_docx.is_file():
                    self._warn("Warning", f"Report not found: {target_docx}")
                    return
            else:
                output_path = Path(self._get_output_path())
                if not output_path.is_dir():
                    self._warn("Warning", f"Invalid output path: {output_path}")
                    return
                version = parse_version(self._get_version())
                matches = []
                for docx_file in output_path.glob("*.docx"):
                    match = re.search(r"_v(\d+(?:\.\d+){1,2})\.docx$", docx_file.name)
                    if match and parse_version(match.group(1)) == version:
                        matches.append(docx_file)
                if not matches:
                    self._info("Information", f"No matching docx report file found\nSearch path: {output_path}")
                    return
                target_docx = max(matches, key=lambda path: path.stat().st_mtime)
            os.startfile(str(target_docx))
            if dialog:
                dialog.accept()
        except (OSError, ValueError) as e:
            self._critical("Error", f"Failed to open report: {e!s}")
            self.logger.error("Failed to open report: %s", e)

    def open_report_path(self, dialog=None, *, output_path=None):
        """
        打开报告所在的文件夹

        Args:
            dialog: 父对话框，可选
        """
        output_path_str = self._get_output_path() if output_path is None else output_path

        try:
            output_path = Path(output_path_str)

            if not output_path.exists() or not output_path.is_dir():
                self._warn("Warning", f"Invalid output path: {output_path}")
                return

            # 直接打开输出路径
            try:
                os.startfile(str(output_path))
            except Exception as popen_error:
                self.logger.error("Failed to open report folder: %s", popen_error)
                self._critical("Error", f"Failed to open folder: {popen_error!s}")

            # 关闭对话框（如果提供）
            if dialog:
                dialog.accept()
        except Exception as e:
            self._critical("Error", f"Failed to open folder: {e!s}")
            self.logger.error("Failed to open report folder: %s", e)

    # ── UI 助手 ──────────────────────────────────────────────────

    def _warn(self, title, msg):
        if self.main_window:
            QW.QMessageBox.warning(self.main_window, title, msg)

    def _info(self, title, msg):
        if self.main_window:
            QW.QMessageBox.information(self.main_window, title, msg)

    def _critical(self, title, msg):
        if self.main_window:
            QW.QMessageBox.critical(self.main_window, title, msg)

    def show_analysis_complete_dialog(self):
        """
        显示分析完成对话框，包含"打开报告"、"打开路径"和"确定"按钮
        """
        dialog = QW.QDialog(self.main_window)
        dialog.setWindowTitle("Analysis Complete")
        dialog.setFixedSize(450, 150)
        dialog.setWindowFlags(
            QW.Qt.WindowType.Window
            | QW.Qt.WindowType.WindowTitleHint
            | QW.Qt.WindowType.WindowCloseButtonHint
        )

        layout = QW.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 添加状态文本标签
        status_label = QW.QLabel("Battery analysis completed!")
        status_label.setAlignment(QW.Qt.AlignmentFlag.AlignCenter)
        status_label.setWordWrap(True)
        layout.addWidget(status_label)

        # 添加底部按钮布局
        button_layout = QW.QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(QW.Qt.AlignmentFlag.AlignCenter)

        # 添加打开报告按钮
        open_report_button = QW.QPushButton("Open Report")
        open_report_button.setMinimumHeight(32)
        open_report_button.setMinimumWidth(120)
        open_report_button.clicked.connect(lambda: self.open_report(dialog))
        button_layout.addWidget(open_report_button)

        # 添加打开路径按钮
        open_path_button = QW.QPushButton("Open Path")
        open_path_button.setMinimumHeight(32)
        open_path_button.setMinimumWidth(120)
        open_path_button.clicked.connect(lambda: self.open_report_path(dialog))
        button_layout.addWidget(open_path_button)

        # 添加确定按钮
        ok_button = QW.QPushButton("OK")
        ok_button.setMinimumHeight(32)
        ok_button.setMinimumWidth(120)
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()
