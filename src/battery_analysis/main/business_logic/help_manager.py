# -*- coding: utf-8 -*-
"""
帮助管理器

负责处理应用程序的帮助功能，包括用户手册和在线帮助
"""

import logging
import os
import subprocess
from pathlib import Path

# 第三方库导入
from PyQt6 import QtCore as QC
from PyQt6 import QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _
from battery_analysis.main.utils.file_utils import FileUtils


class HelpManager:
    """
    帮助管理器类，负责处理应用程序的帮助功能
    """
    
    def __init__(self, main_window):
        """
        初始化帮助管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def show_user_manual(self) -> None:
        """
        显示用户手册
        """
        try:
            # 使用FileUtils获取所有可能的手册路径
            manual_paths = FileUtils.get_manual_paths(self.main_window.current_directory)
            
            manual_found = False
            for manual_path in manual_paths:
                if manual_path.exists() and manual_path.is_file():
                    try:
                        # 使用安全的文件打开方式
                        os.startfile(str(manual_path))
                        manual_found = True
                        self.logger.info("成功打开用户手册: %s", manual_path)
                        break
                    except (OSError, ValueError, RuntimeError, PermissionError) as open_error:
                        self.logger.warning("打开手册文件失败 %s: %s", manual_path, open_error)
                        continue
            
            if not manual_found:
                # 如果找不到手册文件，显示提示并提供解决方案
                QW.QMessageBox.information(
                    self.main_window,
                    "用户手册",
                    "未找到用户手册文件。\n\n" +
                    "请确保以下文件存在：\n" +
                    "• docs/user_manual.pdf\n" +
                    "• user_manual.pdf\n\n" +
                    "如需帮助，请联系技术支持。",
                    QW.QMessageBox.StandardButton.Ok
                )
                
        except (OSError, TypeError, ValueError, RuntimeError) as e:
            self.logger.error("打开用户手册失败: %s", e)
            QW.QMessageBox.warning(
                self.main_window,
                _("error", "错误"),
                f"{_('cannot_open_user_manual', '无法打开用户手册')}: {str(e)}",
                QW.QMessageBox.StandardButton.Ok
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
                _("failed_to_open_help", "无法打开在线帮助。"),
                QW.QMessageBox.StandardButton.Ok
            )
