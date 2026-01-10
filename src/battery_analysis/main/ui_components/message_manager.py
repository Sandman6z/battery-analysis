# -*- coding: utf-8 -*-
"""
消息管理器

负责统一管理应用中的消息提示，包括信息、警告和错误消息
"""

# 第三方库导入
from PyQt6 import QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _


class MessageManager:
    """
    消息管理器类，用于统一管理应用中的消息提示
    """
    
    def __init__(self, parent):
        """
        初始化消息管理器
        
        Args:
            parent: 父窗口实例
        """
        self.parent = parent
    
    def show_message(self, title: str, message: str) -> None:
        """
        显示信息消息框
        
        Args:
            title: 消息框标题
            message: 消息内容
        """
        QW.QMessageBox.information(self.parent, title, message)
    
    def show_warning(self, title: str, message: str) -> None:
        """
        显示警告消息框
        
        Args:
            title: 消息框标题
            message: 警告内容
        """
        QW.QMessageBox.warning(self.parent, title, message)
    
    def show_error(self, title: str, message: str) -> None:
        """
        显示错误消息框
        
        Args:
            title: 消息框标题
            message: 错误内容
        """
        QW.QMessageBox.critical(self.parent, title, message)