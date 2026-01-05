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


class TkinterUIFramework(IUIFramework):
    """Tkinter UI框架实现"""
    
    def __init__(self):
        """初始化UI框架"""
        self.logger = logging.getLogger(__name__)
        self._root = None
    
    def create_application(self, args: Optional[List[str]] = None) -> Any:
        """创建应用程序实例"""
        try:
            import tkinter as tk
            
            self._root = tk.Tk()
            self.logger.info("Tkinter应用程序实例创建成功")
            return self._root
            
        except ImportError as e:
            self.logger.error("Tkinter无法导入: %s", e)
            raise
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建Tkinter应用程序实例失败: %s", e)
            raise
    
    def create_main_window(self) -> Any:
        """创建主窗口"""
        # 对于Tkinter，root窗口就是主窗口
        return self._root
    
    def create_progress_dialog(self, parent: Optional[Any] = None) -> Any:
        """创建进度对话框"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            if parent is None:
                parent = self._root
            
            dialog = tk.Toplevel(parent)
            dialog.title("进度")
            dialog.geometry("300x100")
            dialog.resizable(False, False)
            
            label = tk.Label(dialog, text="处理中...")
            label.pack(pady=10)
            
            progress = ttk.Progressbar(dialog, mode='determinate')
            progress.pack(pady=5, padx=20, fill='x')
            
            self.logger.info("Tkinter进度对话框创建成功")
            return dialog
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建Tkinter进度对话框失败: %s", e)
            raise
    
    def show_message_box(self, 
                        parent: Optional[Any],
                        title: str, 
                        message: str, 
                        msg_type: MessageBoxType) -> Any:
        """显示消息框"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            if parent is None:
                parent = self._root
            
            # 根据消息类型显示不同的消息框
            if msg_type == MessageBoxType.INFORMATION:
                result = messagebox.showinfo(title, message, parent=parent)
            elif msg_type == MessageBoxType.WARNING:
                result = messagebox.showwarning(title, message, parent=parent)
            elif msg_type == MessageBoxType.CRITICAL:
                result = messagebox.showerror(title, message, parent=parent)
            elif msg_type == MessageBoxType.QUESTION:
                result = messagebox.askquestion(title, message, parent=parent)
            else:
                result = messagebox.showinfo(title, message, parent=parent)
            
            self.logger.info("Tkinter消息框显示: %s", title)
            return result
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建Tkinter消息框失败: %s", e)
            raise
    
    def create_file_dialog(self, 
                          parent: Optional[Any],
                          caption: str,
                          directory: str = "",
                          filter_pattern: str = "") -> Any:
        """创建文件选择对话框"""
        try:
            from tkinter import filedialog
            
            if parent is None:
                parent = self._root
            
            # Tkinter文件对话框不支持复杂的过滤器
            file_path = filedialog.askopenfilename(
                title=caption,
                initialdir=directory
            )
            
            self.logger.info("Tkinter文件对话框创建成功: %s", caption)
            return file_path
            
        except (AttributeError, TypeError, ValueError, OSError) as e:
            self.logger.error("创建Tkinter文件对话框失败: %s", e)
            raise
    
    def create_label(self, parent: Any, text: str) -> Any:
        """创建标签控件"""
        try:
            import tkinter as tk
            
            label = tk.Label(parent, text=text)
            self.logger.info("Tkinter标签创建成功: %s", text)
            return label
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建Tkinter标签失败: %s", e)
            raise
    
    def create_button(self, parent: Any, text: str) -> Any:
        """创建按钮控件"""
        try:
            import tkinter as tk
            
            button = tk.Button(parent, text=text)
            self.logger.info("Tkinter按钮创建成功: %s", text)
            return button
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建Tkinter按钮失败: %s", e)
            raise
    
    def create_input_field(self, parent: Any, placeholder: str = "") -> Any:
        """创建输入框控件"""
        try:
            import tkinter as tk
            
            entry = tk.Entry(parent)
            if placeholder:
                # Tkinter Entry不支持placeholder，需要特殊处理
                entry.insert(0, placeholder)
                entry.config(fg='grey')
                entry.bind('<FocusIn>', lambda e: self._clear_placeholder(entry, placeholder))
                entry.bind('<FocusOut>', lambda e: self._set_placeholder(entry, placeholder))
            
            self.logger.info("Tkinter输入框创建成功: %s", placeholder)
            return entry
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建Tkinter输入框失败: %s", e)
            raise
    
    def create_table_widget(self, parent: Any, rows: int, columns: int) -> Any:
        """创建表格控件"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # Tkinter没有原生表格，使用Treeview模拟
            tree = ttk.Treeview(parent, columns=columns, show='headings')
            
            # 设置列标题
            for i in range(columns):
                tree.heading(f'#{i}', text=f'列{i+1}')
            
            self.logger.info("Tkinter表格创建成功: %sx%s", rows, columns)
            return tree
            
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("创建Tkinter表格失败: %s", e)
            raise
    
    def set_layout(self, parent: Any, layout: Any) -> None:
        """设置布局管理器"""
        try:
            layout.pack(fill='both', expand=True)
            self.logger.info("Tkinter布局设置成功")
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error("设置Tkinter布局失败: %s", e)
            raise
    
    def exec_application(self, app: Any) -> int:
        """运行应用程序"""
        try:
            app.mainloop()
            self.logger.info("Tkinter应用程序运行结束")
            return 0
        except (AttributeError, TypeError, RuntimeError) as e:
            self.logger.error("运行Tkinter应用程序失败: %s", e)
            raise
    
    def _clear_placeholder(self, entry: Any, placeholder: str):
        """清除placeholder"""
        if entry.get() == placeholder:
            entry.delete(0, 'end')
            entry.config(fg='black')
    
    def _set_placeholder(self, entry: Any, placeholder: str):
        """设置placeholder"""
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.config(fg='grey')
