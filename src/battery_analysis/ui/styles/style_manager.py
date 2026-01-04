# -*- coding: utf-8 -*-
"""
现代化UI样式管理器

提供统一的样式管理方案，支持QSS文件加载和动态样式应用
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase


class StyleManager(QObject):
    """现代化UI样式管理器"""
    
    # 信号定义
    style_loaded = pyqtSignal(str)  # 样式加载完成信号
    theme_changed = pyqtSignal(str)  # 主题切换信号
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._current_theme = "modern"
        self._style_cache = {}
        # 注意：在某些情况下，QFontDatabase 可能不可用
        # 这不会影响样式管理功能
        try:
            from PyQt6.QtGui import QFontDatabase
            self._font_database = QFontDatabase()
        except Exception as e:
            logging.warning("无法初始化QFontDatabase: %s", e)
            self._font_database = None
        
        # 样式文件路径
        self._style_dir = Path(__file__).parent
        self._load_available_styles()
    
    def _load_available_styles(self):
        """加载可用的样式文件"""
        
        style_files = {
            "battery_analyzer": "battery_analyzer.qss",  # 统一电池分析器样式
            "modern": "battery_analyzer.qss",  # 使用统一样式
            "dark": "dark_theme.qss",
            "light": "light_theme.qss",
            "high_contrast": "high_contrast.qss"
        }
        
        for theme_name, filename in style_files.items():
            style_path = self._style_dir / filename
            if style_path.exists():
                try:
                    with open(style_path, 'r', encoding='utf-8') as f:
                        self._style_cache[theme_name] = f.read()
                        logging.info("样式文件已加载: %s", filename)
                except Exception as e:
                    logging.error("加载样式文件失败 %s: %s", filename, e)
    
    def apply_style(self, widget: QWidget, theme: Optional[str] = None):
        """应用样式到指定控件"""
        
        if theme is None:
            theme = self._current_theme
        
        if theme in self._style_cache:
            widget.setStyleSheet(self._style_cache[theme])
            logging.debug("已应用主题样式: %s", theme)
        else:
            logging.warning("未找到主题样式: %s", theme)
    
    def apply_global_style(self, app: QApplication, theme: Optional[str] = None):
        """应用全局样式"""
        
        if theme is None:
            theme = self._current_theme
        
        # 特殊处理battery_analyzer主题 - 优先使用新的统一样式文件
        if theme == "battery_analyzer":
            unified_style_path = self._style_dir / "battery_analyzer.qss"
            if unified_style_path.exists():
                try:
                    with open(unified_style_path, 'r', encoding='utf-8') as f:
                        unified_style = f.read()
                        app.setStyleSheet(unified_style)
                        self._current_theme = theme
                        self.theme_changed.emit(theme)
                        logging.info("已应用统一电池分析器样式 (通过StyleManager)")
                        return
                except Exception as e:
                    logging.error("加载统一样式文件失败: %s", e)
            else:
                logging.warning("未找到统一样式文件: %s", unified_style_path)
        
        if theme in self._style_cache:
            app.setStyleSheet(self._style_cache[theme])
            self._current_theme = theme
            self.theme_changed.emit(theme)
            logging.info("已应用全局主题: %s", theme)
        else:
            logging.error("未找到主题样式: %s", theme)
    
    def load_custom_style(self, file_path: str) -> bool:
        """加载自定义样式文件"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                custom_style = f.read()
                self._style_cache["custom"] = custom_style
                logging.info("已加载自定义样式: %s", file_path)
                return True
        except Exception as e:
            logging.error("加载自定义样式失败: %s", e)
            return False
    
    def get_style_variables(self, theme: Optional[str] = None) -> Dict[str, Any]:
        """获取样式变量"""
        
        if theme is None:
            theme = self._current_theme
        
        # 定义常用颜色变量
        variables = {
            "modern": {
                "primary_color": "#3498db",
                "secondary_color": "#27ae60",
                "warning_color": "#f39c12",
                "error_color": "#e74c3c",
                "background_color": "#f8f9fa",
                "surface_color": "#ffffff",
                "text_color": "#212529",
                "border_color": "#e9ecef"
            },
            "dark": {
                "primary_color": "#5dade2",
                "secondary_color": "#58d68d",
                "warning_color": "#f4d03f",
                "error_color": "#ec7063",
                "background_color": "#2c3e50",
                "surface_color": "#34495e",
                "text_color": "#ecf0f1",
                "border_color": "#4a5f7a"
            },
            "light": {
                "primary_color": "#3498db",
                "secondary_color": "#27ae60",
                "warning_color": "#f39c12",
                "error_color": "#e74c3c",
                "background_color": "#ffffff",
                "surface_color": "#f8f9fa",
                "text_color": "#212529",
                "border_color": "#dee2e6"
            }
        }
        
        return variables.get(theme, variables["modern"])
    
    def register_font(self, font_path: str, family_name: Optional[str] = None) -> bool:
        """注册自定义字体"""
        
        try:
            font_id = self._font_database.addApplicationFont(font_path)
            if font_id != -1:
                font_families = self._font_database.applicationFontFamilies(font_id)
                if font_families:
                    family_name = family_name or font_families[0]
                    logging.info("字体已注册: %s", family_name)
                    return True
            return False
        except Exception as e:
            logging.error("注册字体失败: %s", e)
            return False
    
    def set_application_font(self, app: QApplication, font_family: str, size: int = 11):
        """设置应用程序字体"""
        
        try:
            font = QFont(font_family, size)
            app.setFont(font)
            logging.info("应用程序字体已设置: %s %spt", font_family, size)
        except Exception as e:
            logging.error("设置字体失败: %s", e)
    
    def create_themed_button(self, parent, text: str, action_type: str, 
                           callback=None, **kwargs) -> 'QPushButton':
        """创建主题化按钮"""
        
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton(text, parent)
        
        # 根据动作类型设置数据属性
        button.setProperty("data-action", action_type)
        
        # 设置最小高度
        if "min_height" in kwargs:
            button.setMinimumHeight(kwargs["min_height"])
        else:
            button.setMinimumHeight(36)
        
        # 连接回调
        if callback:
            button.clicked.connect(callback)
        
        return button
    
    def create_themed_groupbox(self, parent, title: str, theme: str, 
                             widget: Optional[QWidget] = None) -> 'QGroupBox':
        """创建主题化分组框"""
        
        from PyQt6.QtWidgets import QGroupBox
        
        groupbox = QGroupBox(title, parent)
        
        # 设置主题属性
        groupbox.setProperty("data-theme", theme)
        
        # 如果提供了控件，添加到分组框中
        if widget:
            layout = QVBoxLayout(groupbox)
            layout.addWidget(widget)
        
        return groupbox
    
    def get_current_theme(self) -> str:
        """获取当前主题"""
        return self._current_theme
    
    def get_available_themes(self) -> list:
        """获取可用的主题列表"""
        return list(self._style_cache.keys())


# 全局样式管理器实例
style_manager = StyleManager()


def apply_modern_theme(app: QApplication, theme: str = "modern"):
    """应用现代化主题的便捷函数"""
    style_manager.apply_global_style(app, theme)


def create_styled_button(parent, text: str, action_type: str, callback=None):
    """创建样式化按钮的便捷函数"""
    return style_manager.create_themed_button(parent, text, action_type, callback)


def create_styled_groupbox(parent, title: str, theme: str, widget=None):
    """创建样式化分组框的便捷函数"""
    return style_manager.create_themed_groupbox(parent, title, theme, widget)