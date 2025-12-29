# -*- coding: utf-8 -*-
"""
UI框架抽象接口

定义UI操作的抽象接口，实现UI框架的解耦
支持多种UI框架（PyQt6、PySide6、Tkinter等）
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from enum import Enum


class UIFrameworkType(Enum):
    """UI框架类型枚举"""
    PYQT6 = "pyqt6"
    PYSIDE6 = "pyside6"
    TKINTER = "tkinter"


class MessageBoxType(Enum):
    """消息框类型枚举"""
    INFORMATION = "information"
    WARNING = "warning"
    CRITICAL = "critical"
    QUESTION = "question"


class IUIFramework(ABC):
    """UI框架抽象接口"""
    
    @abstractmethod
    def create_application(self, args: Optional[List[str]] = None) -> Any:
        """创建应用程序实例
        
        Returns:
            Any: 应用程序实例
        """
        pass
    
    @abstractmethod
    def create_main_window(self) -> Any:
        """创建主窗口
        
        Returns:
            Any: 主窗口实例
        """
        pass
    
    @abstractmethod
    def create_progress_dialog(self, parent: Optional[Any] = None) -> Any:
        """创建进度对话框
        
        Args:
            parent: 父窗口
            
        Returns:
            Any: 进度对话框实例
        """
        pass
    
    @abstractmethod
    def show_message_box(self, 
                        parent: Optional[Any],
                        title: str, 
                        message: str, 
                        msg_type: MessageBoxType) -> Any:
        """显示消息框
        
        Args:
            parent: 父窗口
            title: 窗口标题
            message: 消息内容
            msg_type: 消息类型
            
        Returns:
            Any: 消息框实例
        """
        pass
    
    @abstractmethod
    def create_file_dialog(self, 
                          parent: Optional[Any],
                          caption: str,
                          directory: str = "",
                          filter_pattern: str = "") -> Any:
        """创建文件选择对话框
        
        Args:
            parent: 父窗口
            caption: 对话框标题
            directory: 默认目录
            filter_pattern: 文件过滤器
            
        Returns:
            Any: 文件对话框实例
        """
        pass
    
    @abstractmethod
    def create_label(self, parent: Any, text: str) -> Any:
        """创建标签控件
        
        Args:
            parent: 父控件
            text: 标签文本
            
        Returns:
            Any: 标签控件实例
        """
        pass
    
    @abstractmethod
    def create_button(self, parent: Any, text: str) -> Any:
        """创建按钮控件
        
        Args:
            parent: 父控件
            text: 按钮文本
            
        Returns:
            Any: 按钮控件实例
        """
        pass
    
    @abstractmethod
    def create_input_field(self, parent: Any, placeholder: str = "") -> Any:
        """创建输入框控件
        
        Args:
            parent: 父控件
            placeholder: 占位符文本
            
        Returns:
            Any: 输入框控件实例
        """
        pass
    
    @abstractmethod
    def create_table_widget(self, parent: Any, rows: int, columns: int) -> Any:
        """创建表格控件
        
        Args:
            parent: 父控件
            rows: 行数
            columns: 列数
            
        Returns:
            Any: 表格控件实例
        """
        pass
    
    @abstractmethod
    def set_layout(self, parent: Any, layout: Any) -> None:
        """设置布局管理器
        
        Args:
            parent: 父控件
            layout: 布局管理器
        """
        pass
    
    @abstractmethod
    def exec_application(self, app: Any) -> int:
        """运行应用程序
        
        Args:
            app: 应用程序实例
            
        Returns:
            int: 退出代码
        """
        pass