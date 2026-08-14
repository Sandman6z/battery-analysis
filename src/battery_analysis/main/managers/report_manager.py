"""报告管理类"""
import os
from pathlib import Path
import logging
from PyQt6 import QtWidgets as QW
from battery_analysis.main.app_context import AppContext, UIBridge


class ReportManager:
    """报告管理类"""

    def __init__(self, main_window=None, ctx: AppContext = None):
        """
        初始化报告管理器

        Args:
            main_window: 主窗口实例（旧接口，过渡用）
            ctx: 应用上下文（新接口）
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        # 优先使用 ctx，否则从 main_window 构造
        self._ui: UIBridge = ctx.ui if ctx and ctx.ui else \
            (self._make_bridge(main_window) if main_window else None)
        self._parent_widget = main_window  # 对话框需要 parent

    @staticmethod
    def _make_bridge(mw) -> UIBridge:
        from battery_analysis.main.app_context import UIBridgeImpl
        return UIBridgeImpl(mw)

    def _parent(self):
        return self._parent_widget

    # ── 工具方法 ────────────────────────────────────────────────

    def _get_output_path(self) -> str:
        if self._ui:
            return self._ui.get_lineedit_text("OutputPath")
        if self.main_window:
            return self.main_window.lineEdit_OutputPath.text()
        return ""

    def _get_version(self) -> str:
        if self._ui:
            return self._ui.get_lineedit_text("Version")
        if self.main_window:
            return self.main_window.lineEdit_Version.text()
        return ""

    # ── 业务方法 ────────────────────────────────────────────────

    def open_report(self, dialog=None):
        """
        打开生成的docx格式报告

        Args:
            dialog: 父对话框，可选
        """
        output_path_str = self._get_output_path()
        version = self._get_version()

        try:
            output_path = Path(output_path_str)

            if not output_path.exists() or not output_path.is_dir():
                self._warn("Warning", f"Invalid output path: {output_path}")
                return

            # 搜索docx文件（word报告保存在输出目录的上一级）
            docx_files = list(output_path.parent.rglob("*.docx"))

            if not docx_files:
                self._info("Information", f"No docx report file found\nSearch path: {output_path.parent}")
                return

            # 找到与当前版本匹配的报告
            target_docx = None
            for docx_file in docx_files:
                if f"_v{version}" in docx_file.name:
                    target_docx = docx_file
                    break

            # 如果没有匹配版本，使用最新的报告
            if not target_docx and docx_files:
                target_docx = sorted(docx_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]

            # 打开报告
            if target_docx:
                target_path = str(target_docx)
                try:
                    os.startfile(target_path)
                except Exception as popen_error:
                    self.logger.error("Failed to open report: %s", popen_error)
                    self._critical("Error", f"Failed to open report: {str(popen_error)}")

                # 关闭对话框（如果提供）
                if dialog:
                    dialog.accept()
        except Exception as e:
            self._critical("Error", f"Failed to open report: {str(e)}")
            self.logger.error("Failed to open report: %s", e)

    def open_report_path(self, dialog=None):
        """
        打开报告所在的文件夹

        Args:
            dialog: 父对话框，可选
        """
        output_path_str = self._get_output_path()

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
                self._critical("Error", f"Failed to open folder: {str(popen_error)}")

            # 关闭对话框（如果提供）
            if dialog:
                dialog.accept()
        except Exception as e:
            self._critical("Error", f"Failed to open folder: {str(e)}")
            self.logger.error("Failed to open report folder: %s", e)
    
    # ── UI 助手 ──────────────────────────────────────────────────

    def _warn(self, title, msg):
        if self._ui:
            self._ui.show_warning(title, msg)
        elif self.main_window:
            QW.QMessageBox.warning(self.main_window, title, msg)

    def _info(self, title, msg):
        if self._ui:
            self._ui.show_message(title, msg)
        elif self.main_window:
            QW.QMessageBox.information(self.main_window, title, msg)

    def _critical(self, title, msg):
        if self._ui:
            self._ui.show_critical(title, msg)
        elif self.main_window:
            QW.QMessageBox.critical(self.main_window, title, msg)

    def show_analysis_complete_dialog(self):
        """
        显示分析完成对话框，包含"打开报告"、"打开路径"和"确定"按钮
        """
        dialog = QW.QDialog(self.main_window)
        dialog.setWindowTitle("Analysis Complete")
        dialog.setFixedSize(450, 150)
        dialog.setWindowFlags(
            QW.Qt.WindowType.Window | 
            QW.Qt.WindowType.WindowTitleHint |
            QW.Qt.WindowType.WindowCloseButtonHint
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
