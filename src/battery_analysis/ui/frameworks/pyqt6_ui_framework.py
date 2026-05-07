# -*- coding: utf-8 -*-
"""
PyQt6 UI框架实现

基于PyQt6的UI框架抽象接口实现
"""

import logging
from typing import Any, Optional, Dict, List
from battery_analysis.ui.interfaces.iuiframework import IUIFramework, MessageBoxType


class PyQt6UIFramework(IUIFramework):
    """PyQt6 UI框架实现"""
    
    def __init__(self):
        """初始化UI框架"""
        self.logger = logging.getLogger(__name__)
        self._app = None
    
    def create_application(self, args: Optional[List[str]] = None) -> Any:
        """创建应用程序实例"""
        try:
            from PyQt6.QtWidgets import QApplication
            
            if args is None:
                args = []
            
            # 检查是否已有QApplication实例
            if QApplication.instance() is None:
                self._app = QApplication(args)
            else:
                self._app = QApplication.instance()
                
            self.logger.info("PyQt6应用程序实例创建成功")
            return self._app
            
        except ImportError as e:
            self.logger.error("PyQt6未安装或无法导入: %s", e)
            raise
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建PyQt6应用程序实例失败: %s", e)
            raise
    
    def create_main_window(self) -> Any:
        """创建主窗口"""
        try:
            from PyQt6.QtWidgets import QMainWindow
            
            main_window = QMainWindow()
            self.logger.info("PyQt6主窗口创建成功")
            return main_window
            
        except ImportError as e:
            self.logger.error("PyQt6组件无法导入: %s", e)
            raise
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建PyQt6主窗口失败: %s", e)
            raise
    
    def create_progress_dialog(self, parent: Optional[Any] = None) -> Any:
        """创建进度对话框"""
        try:
            from PyQt6.QtWidgets import QProgressDialog
            
            if parent is None:
                parent = self._app.activeWindow() if self._app else None
            
            progress_dialog = QProgressDialog("处理中...", "取消", 0, 100, parent)
            progress_dialog.setWindowModality(True)
            progress_dialog.setWindowTitle("进度")
            
            self.logger.info("PyQt6进度对话框创建成功")
            return progress_dialog
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建PyQt6进度对话框失败: %s", e)
            raise
    
    def show_message_box(self, 
                        parent: Optional[Any],
                        title: str, 
                        message: str, 
                        msg_type: MessageBoxType) -> Any:
        """显示消息框"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            if parent is None:
                parent = self._app.activeWindow() if self._app else None
            
            message_box = QMessageBox(parent)
            message_box.setWindowTitle(title)
            message_box.setText(message)
            
            # 设置消息框类型
            if msg_type == MessageBoxType.INFORMATION:
                message_box.setIcon(QMessageBox.Icon.Information)
            elif msg_type == MessageBoxType.WARNING:
                message_box.setIcon(QMessageBox.Icon.Warning)
            elif msg_type == MessageBoxType.CRITICAL:
                message_box.setIcon(QMessageBox.Icon.Critical)
            elif msg_type == MessageBoxType.QUESTION:
                message_box.setIcon(QMessageBox.Icon.Question)
            
            message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            self.logger.info("PyQt6消息框显示: %s", title)
            return message_box
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建PyQt6消息框失败: %s", e)
            raise
    
    def create_file_dialog(self, 
                          parent: Optional[Any],
                          caption: str,
                          directory: str = "",
                          filter_pattern: str = "") -> Any:
        """创建文件选择对话框"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            if parent is None:
                parent = self._app.activeWindow() if self._app else None
            
            file_dialog = QFileDialog(parent, caption, directory, filter_pattern)
            
            self.logger.info("PyQt6文件对话框创建成功: %s", caption)
            return file_dialog
            
        except (AttributeError, TypeError, ValueError, OSError) as e:
            self.logger.error("创建PyQt6文件对话框失败: %s", e)
            raise
    
    def create_label(self, parent: Any, text: str) -> Any:
        """创建标签控件"""
        try:
            from PyQt6.QtWidgets import QLabel
            
            label = QLabel(text, parent)
            self.logger.info("PyQt6标签创建成功: %s", text)
            return label
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建PyQt6标签失败: %s", e)
            raise
    
    def create_button(self, parent: Any, text: str) -> Any:
        """创建按钮控件"""
        try:
            from PyQt6.QtWidgets import QPushButton
            
            button = QPushButton(text, parent)
            self.logger.info("PyQt6按钮创建成功: %s", text)
            return button
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建PyQt6按钮失败: %s", e)
            raise
    
    def create_input_field(self, parent: Any, placeholder: str = "") -> Any:
        """创建输入框控件"""
        try:
            from PyQt6.QtWidgets import QLineEdit
            
            line_edit = QLineEdit(parent)
            if placeholder:
                line_edit.setPlaceholderText(placeholder)
            
            self.logger.info("PyQt6输入框创建成功: %s", placeholder)
            return line_edit
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建PyQt6输入框失败: %s", e)
            raise
    
    def create_table_widget(self, parent: Any, rows: int, columns: int) -> Any:
        """创建表格控件"""
        try:
            from PyQt6.QtWidgets import QTableWidget
            
            table = QTableWidget(rows, columns, parent)
            self.logger.info("PyQt6表格创建成功: %sx%s", rows, columns)
            return table
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建PyQt6表格失败: %s", e)
            raise
    
    def set_layout(self, parent: Any, layout: Any) -> None:
        """设置布局管理器"""
        try:
            parent.setLayout(layout)
            self.logger.info("PyQt6布局设置成功")
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("设置PyQt6布局失败: %s", e)
            raise
    
    def exec_application(self, app: Any) -> int:
        """运行应用程序"""
        try:
            result = app.exec()
            self.logger.info("PyQt6应用程序运行结束")
            return result
        except (AttributeError, TypeError, RuntimeError) as e:
            self.logger.error("运行PyQt6应用程序失败: %s", e)
            raise
