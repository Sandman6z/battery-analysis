"""
对话框组件

负责处理应用程序中的各种对话框
"""

import logging
from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC
from PyQt6 import QtGui as QG
from battery_analysis.i18n.language_manager import _


class Dialogs:
    """
    对话框类，负责处理应用程序中的各种对话框
    """
    
    def __init__(self, main_window):
        """
        初始化对话框组件
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def handle_exit(self) -> None:
        """
        处理退出操作
        """
        reply = QW.QMessageBox.question(
            self.main_window,
            _("exit_title", "退出"),
            _("exit_message", "确定要退出应用程序吗？"),
            QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
            QW.QMessageBox.StandardButton.No
        )
        
        if reply == QW.QMessageBox.StandardButton.Yes:
            # 确保关闭所有相关进程和资源
            QW.QApplication.quit()
    
    def handle_about(self) -> None:
        """
        处理关于对话框
        """
        from battery_analysis import __version__
        about_text = f"""
Battery Analyzer v{__version__}

电池分析应用程序，用于分析电池测试数据。

© 2026 Battery Analysis Team
"""
        QW.QMessageBox.about(self.main_window, _("about_title", "关于"), about_text)
    
    def show_preferences(self) -> None:
        """
        显示首选项对话框
        """
        try:
            from battery_analysis.i18n.preferences_dialog import PreferencesDialog
            dialog = PreferencesDialog(self.main_window)
            # 使用独立的事件循环，确保对话框能正常显示
            result = dialog.exec()
            if result == QW.QDialog.DialogCode.Accepted:
                self.on_preferences_applied()
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.error("显示首选项对话框失败: %s", e)
            QW.QMessageBox.warning(
                self.main_window,
                _("warning_title", "警告"),
                _("failed_to_show_preferences", "无法显示首选项对话框。")
            )
    
    def on_preferences_applied(self) -> None:
        """
        处理首选项应用事件
        """
        # 这里可以添加首选项应用后的处理逻辑
        self.logger.info("首选项已应用")
    
    def show_user_manual(self) -> None:
        """
        显示用户手册
        """
        try:
            from battery_analysis.ui.user_manual_dialog import UserManualDialog
            dialog = UserManualDialog(self.main_window)
            dialog.exec()
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.error("显示用户手册失败: %s", e)
            QW.QMessageBox.warning(
                self.main_window,
                _("warning_title", "警告"),
                _("failed_to_show_manual", "无法显示用户手册。")
            )
    
    def show_online_help(self) -> None:
        """
        显示在线帮助
        """
        try:
            from PyQt6.QtGui import QDesktopServices
            from PyQt6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl("https://example.com/battery-analyzer/help"))
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.error("打开在线帮助失败: %s", e)
            QW.QMessageBox.warning(
                self.main_window,
                _("warning_title", "警告"),
                _("failed_to_open_help", "无法打开在线帮助。")
            )
    
    def show_analysis_complete_dialog(self):
        """
        显示分析完成对话框
        """
        # 创建自定义对话框，确保所有按钮都能正确显示
        dialog = QW.QDialog(self.main_window)
        dialog.setWindowTitle(_("analysis_complete_title", "分析完成"))
        dialog.setWindowModality(QC.Qt.WindowModality.ApplicationModal)
        
        # 设置布局
        layout = QW.QVBoxLayout(dialog)
        
        # 添加消息文本
        message_label = QW.QLabel(_("analysis_complete_text", "电池分析已成功完成！\n\n报告已生成到指定输出路径。"))
        message_label.setAlignment(QC.Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        layout.addSpacing(20)
        
        # 添加图标
        icon_label = QW.QLabel()
        icon_label.setPixmap(QW.QMessageBox.standardIcon(QW.QMessageBox.Icon.Information).scaled(48, 48))
        icon_label.setAlignment(QC.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        layout.addSpacing(20)
        
        # 创建按钮布局
        button_layout = QW.QHBoxLayout()
        button_layout.addStretch()
        
        # 打开报告按钮
        open_report_button = QW.QPushButton(_("open_report", "打开报告"))
        open_report_button.clicked.connect(lambda: self._handle_dialog_button_click(dialog, "open_report"))
        button_layout.addWidget(open_report_button)
        button_layout.addSpacing(10)
        
        # 打开路径按钮
        open_path_button = QW.QPushButton(_("open_path", "打开路径"))
        open_path_button.clicked.connect(lambda: self._handle_dialog_button_click(dialog, "open_path"))
        button_layout.addWidget(open_path_button)
        button_layout.addSpacing(10)
        
        # 确定按钮
        ok_button = QW.QPushButton(_("ok", "确定"))
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 设置对话框大小
        dialog.setFixedSize(400, 220)
        
        # 显示对话框
        dialog.exec()
        
    def _handle_dialog_button_click(self, dialog, button_type):
        """
        处理对话框按钮点击事件
        """
        try:
            if button_type == "open_report":
                if hasattr(self.main_window, '_open_report'):
                    self.main_window._open_report()
            elif button_type == "open_path":
                if hasattr(self.main_window, '_open_report_path'):
                    self.main_window._open_report_path()
            # 关闭对话框
            dialog.accept()
        except Exception as e:
            self.logger.error("处理对话框按钮点击失败: %s", e)
            QW.QMessageBox.critical(
                self.main_window,
                _("error_title", "错误"),
                f"处理按钮点击失败: {str(e)}"
            )
    
    def show_visualizer_error(self, error_msg: str):
        """
        显示可视化工具错误对话框
        
        Args:
            error_msg: 错误信息
        """
        QW.QMessageBox.critical(
            self.main_window,
            _("visualizer_error_title", "可视化工具错误"),
            _("visualizer_error_message", "运行可视化工具失败:\n\n{}").format(error_msg)
        )
    
    def handle_data_error_recovery(self, error_msg: str):
        """
        处理数据错误恢复
        
        Args:
            error_msg: 错误信息
            
        Returns:
            bool: 是否继续分析
        """
        self.logger.error("数据错误: %s", error_msg)
        
        # 创建一个自定义对话框
        dialog = QW.QDialog(self.main_window)
        dialog.setWindowTitle(_("data_error_title", "数据错误"))
        dialog.setFixedSize(450, 250)
        dialog.setWindowModality(QC.Qt.WindowModality.ApplicationModal)
        
        # 设置布局
        layout = QW.QVBoxLayout(dialog)
        
        # 错误标题
        title_label = QW.QLabel(_("data_error_title", "数据错误"))
        title_font = QG.QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        layout.addSpacing(10)
        
        # 错误信息
        error_label = QW.QLabel(_("data_error_message", "分析数据时出现错误:\n\n{}").format(error_msg))
        error_label.setWordWrap(True)
        layout.addWidget(error_label)
        layout.addSpacing(15)
        
        # 建议解决方案
        details_label = QW.QLabel(_("data_error_suggestions", "建议解决方案:\n\n"))
        details_label.setWordWrap(True)
        details_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(details_label)
        
        # 按钮布局
        button_layout = QW.QHBoxLayout()
        button_layout.addStretch()
        
        # 选项1: 重新选择数据目录
        retry_button = QW.QPushButton(_("retry_option", "重新选择数据目录"))
        retry_button.clicked.connect(lambda: self._handle_error_option(dialog, "retry"))
        button_layout.addWidget(retry_button)
        
        # 选项2: 使用默认配置
        default_button = QW.QPushButton(_("default_option", "使用默认配置"))
        default_button.clicked.connect(lambda: self._handle_error_option(dialog, "default"))
        button_layout.addWidget(default_button)
        
        # 选项3: 取消操作
        cancel_button = QW.QPushButton(_("cancel_option", "取消"))
        cancel_button.clicked.connect(lambda: self._handle_error_option(dialog, "cancel"))
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 存储用户选择
        self._error_option = None
        
        # 显示对话框
        dialog.exec()
        
        # 处理用户选择
        if self._error_option == "retry":
            # 重新选择数据目录
            if hasattr(self.main_window, '_open_data_directory_dialog'):
                self.main_window._open_data_directory_dialog()
            return True
        elif self._error_option == "default":
            # 使用默认配置，继续分析
            return True
        else:
            # 取消操作
            return False
    
    def _handle_error_option(self, dialog, option):
        """
        处理错误选项
        
        Args:
            dialog: 对话框实例
            option: 用户选择的选项
        """
        self._error_option = option
        dialog.accept()
