"""
对话框管理器模块

这个模块实现了电池分析应用的对话框管理功能，包括：
- 退出确认对话框
- 关于对话框
- 首选项对话框
- 信息/警告/错误对话框
- 文件选择对话框
"""

# 标准库导入
import logging

# 第三方库导入
import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _
from battery_analysis.main.ui_components.config_path_provider import ConfigPathProvider
from battery_analysis.main.ui_components.preferences_dialog import PreferencesDialog


class DialogManager:
    """
    对话框管理器类，负责各种对话框的处理
    """

    def __init__(self, main_window=None):
        """
        初始化对话框管理器

        Args:
            main_window: 主窗口实例（旧接口）
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

    def handle_exit(self):
        """
        处理退出操作，显示确认对话框
        """
        reply = QW.QMessageBox.question(
            self.main_window,
            _("Confirm Exit"),
            _("Are you sure you want to exit the application?"),
            QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
            QW.QMessageBox.StandardButton.No,
        )

        if reply == QW.QMessageBox.StandardButton.Yes:
            self.main_window.close()

    def handle_about(self):
        """
        显示关于对话框
        """
        import time

        about_text = _(
            "<h3>Battery Analyzer</h3>"
            "<p>Version: v{version}</p>"
            "<p>Battery analysis tool for battery performance testing and data analysis.</p>"
            "<p>© {year} Sandman Zhang, Shane Zhao</p>"
        ).format(version=self.main_window.version, year=time.localtime().tm_year)

        QW.QMessageBox.about(self.main_window, _("About Battery Analyzer"), about_text)

    def show_preferences(self):
        """
        显示首选项对话框
        """
        try:
            preferences_dialog = PreferencesDialog(
                self.main_window, config_provider=ConfigPathProvider()
            )

            # 连接首选项应用信号
            preferences_dialog.preferences_applied.connect(self.main_window.on_preferences_applied)

            # 显示对话框
            preferences_dialog.exec()

        except (OSError, ValueError, ImportError) as e:
            self.logger.error("Error showing preferences dialog: %s", e)
            QW.QMessageBox.critical(
                self.main_window, _("Error"), f"{_('Failed to show preferences dialog')}: {e!s}"
            )

    def show_user_manual(self):
        """打开 GitHub Wiki 用户手册，与 Help 菜单使用同一入口。"""
        from battery_analysis.main.business_logic.help_manager import HelpManager

        HelpManager(self.main_window).show_user_manual()

    def show_online_help(self):
        """
        显示在线帮助
        """
        try:
            # 打开在线帮助网页
            help_url = "https://sandman6z.github.io/battery-analysis/"
            QG.QDesktopServices.openUrl(QC.QUrl(help_url))
        except (OSError, ValueError, RuntimeError, TypeError) as e:
            logging.error("Failed to open online help: %s", e)
            QW.QMessageBox.information(
                self.main_window,
                _("Online Help"),
                _("Unable to open online help. Please check your network connection or contact technical support.\n\nHelp Center URL: {url}").format(
                    url="https://sandman6z.github.io/battery-analysis/"
                ),
                QW.QMessageBox.StandardButton.Ok,
            )

    def show_critical_message(self, title, message):
        """
        显示关键错误消息对话框

        Args:
            title: 对话框标题
            message: 错误消息
        """
        QW.QMessageBox.critical(self.main_window, title, message, QW.QMessageBox.StandardButton.Ok)

    def show_warning_message(self, title, message):
        """
        显示警告消息对话框

        Args:
            title: 对话框标题
            message: 警告消息
        """
        QW.QMessageBox.warning(self.main_window, title, message, QW.QMessageBox.StandardButton.Ok)

    def show_information_message(self, title, message):
        """
        显示信息消息对话框

        Args:
            title: 对话框标题
            message: 信息消息
        """
        QW.QMessageBox.information(
            self.main_window, title, message, QW.QMessageBox.StandardButton.Ok
        )

    def show_question_message(
        self,
        title,
        message,
        buttons=QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
        default_button=QW.QMessageBox.StandardButton.No,
    ):
        """
        显示问题对话框

        Args:
            title: 对话框标题
            message: 问题消息
            buttons: 对话框按钮
            default_button: 默认按钮

        Returns:
            用户的选择
        """
        return QW.QMessageBox.question(self.main_window, title, message, buttons, default_button)
