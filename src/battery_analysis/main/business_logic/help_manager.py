"""
帮助管理器

负责处理应用程序的帮助功能，包括用户手册和在线帮助
"""

import logging
import os

# 第三方库导入
from PyQt6 import QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _
from battery_analysis.main.utils.file_utils import FileUtils


class HelpManager:
    """
    帮助管理器类，负责处理应用程序的帮助功能
    """

    def __init__(self, main_window=None):
        """
        初始化帮助管理器

        Args:
            main_window: 主窗口实例（旧接口）
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

    def show_user_manual(self) -> None:
        """
        显示用户手册（在线文档）
        """
        try:
            from PyQt6.QtCore import QUrl
            from PyQt6.QtGui import QDesktopServices

            QDesktopServices.openUrl(QUrl("https://sandman6z.github.io/battery-analysis/QUICK_START/"))
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.error("Failed to open user manual: %s", e)
            QW.QMessageBox.warning(
                self.main_window,
                _("Error"),
                f"{_('Cannot open user manual')}: {e!s}",
                QW.QMessageBox.StandardButton.Ok,
            )

    def show_online_help(self) -> None:
        """
        显示在线帮助
        """
        try:
            from PyQt6.QtCore import QUrl
            from PyQt6.QtGui import QDesktopServices

            QDesktopServices.openUrl(QUrl("https://sandman6z.github.io/battery-analysis/"))
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.error("Failed to open online help: %s", e)
            QW.QMessageBox.warning(
                self.main_window,
                _("Warning"),
                _("Failed to open online help."),
                QW.QMessageBox.StandardButton.Ok,
            )
