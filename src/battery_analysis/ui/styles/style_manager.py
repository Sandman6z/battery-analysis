"""
现代化UI样式管理器

提供统一的样式管理方案，支持QSS文件加载和动态样式应用
"""

import logging
import re
import sys
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QGroupBox, QPushButton, QVBoxLayout, QWidget


def _get_resource_dir() -> Path:
    """获取资源目录：兼容 PyInstaller 打包与开发环境。

    PyInstaller（--onefile 和 --onedir）通过 sys._MEIPASS 指向数据文件
    的实际解压/存放位置。开发环境下回退到源码目录。
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "battery_analysis" / "ui" / "styles"
    return Path(__file__).parent


class StyleManager(QObject):
    """现代化UI样式管理器"""

    # 信号定义
    style_loaded = pyqtSignal(str)  # 样式加载完成信号
    theme_changed = pyqtSignal(str)  # 主题切换信号

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._current_theme = "modern"
        self._style_cache = {}
        # 延迟初始化 QFontDatabase，只有在需要时才创建
        self._font_database = None

        # 样式文件路径（兼容 PyInstaller 打包）
        self._style_dir = _get_resource_dir()
        self._load_available_styles()

    def _load_available_styles(self):
        """加载可用的样式文件"""

        # 主样式文件（所有主题共享）
        main_style_file = "battery_analyzer.qss"
        main_style_path = self._style_dir / main_style_file

        # 加载主样式文件 - QSS已启用
        if main_style_path.exists():
            try:
                with open(main_style_path, encoding="utf-8") as f:
                    main_style = f.read()

                    # 解析 url() 中的相对路径为绝对路径（相对 QSS 文件所在目录）
                    def _resolve_url(match):
                        url_path = match.group(1)
                        if url_path.startswith((":/", "/", "http")):
                            return match.group(0)  # 保持资源路径、绝对路径、http 不变
                        abs_path = (self._style_dir / url_path).resolve()
                        if abs_path.exists():
                            return f"url({abs_path.as_posix()})"
                        return match.group(0)

                    main_style = re.sub(r"url\(([^)]+)\)", _resolve_url, main_style)
                    # 所有主题默认使用主样式文件
                    self._style_cache["battery_analyzer"] = main_style
                    self._style_cache["modern"] = main_style
                    self._style_cache["light"] = main_style
                    logging.info("Main style file loaded: %s", main_style_file)

                    # 尝试加载深色主题（如果存在）
                    dark_style_path = self._style_dir / "dark_theme.qss"
                    if dark_style_path.exists():
                        with open(dark_style_path, encoding="utf-8") as f:
                            dark_style = f.read()
                            self._style_cache["dark"] = dark_style
                            logging.info("Dark theme style file loaded: dark_theme.qss")
                    else:
                        # 如果深色主题文件不存在，基于主样式创建
                        dark_style = main_style
                        # 替换颜色变量为深色主题颜色
                        dark_style = dark_style.replace("#f5f0e8", "#2c3e50")  # main background
                        dark_style = dark_style.replace("#faf7f2", "#34495e")  # card surface
                        dark_style = dark_style.replace("#ede9e3", "#3a4a5e")  # input background
                        dark_style = dark_style.replace("#e5e0d8", "#405060")  # input hover
                        dark_style = dark_style.replace("#3d3229", "#ecf0f1")  # primary text
                        dark_style = dark_style.replace("#8a7a6a", "#bdc3c7")  # secondary text
                        dark_style = dark_style.replace("#e0d8cc", "#4a5f7a")  # border/divider
                        self._style_cache["dark"] = dark_style
                        logging.info("Created dark theme based on main style")

                    # 尝试加载高对比度主题（如果存在）
                    high_contrast_style_path = self._style_dir / "high_contrast.qss"
                    if high_contrast_style_path.exists():
                        with open(high_contrast_style_path, encoding="utf-8") as f:
                            high_contrast_style = f.read()
                            self._style_cache["high_contrast"] = high_contrast_style
                            logging.info("High contrast theme style file loaded: high_contrast.qss")
                    else:
                        # 如果高对比度主题文件不存在，基于主样式创建
                        high_contrast_style = main_style
                        # 替换颜色变量为高对比度颜色
                        high_contrast_style = high_contrast_style.replace("#f5f0e8", "#ffffff")
                        high_contrast_style = high_contrast_style.replace("#faf7f2", "#ffffff")
                        high_contrast_style = high_contrast_style.replace("#ede9e3", "#ffffff")
                        high_contrast_style = high_contrast_style.replace("#3d3229", "#000000")
                        high_contrast_style = high_contrast_style.replace("#e0d8cc", "#000000")
                        high_contrast_style = high_contrast_style.replace("#27ae60", "#0000ff")
                        self._style_cache["high_contrast"] = high_contrast_style
                        logging.info("Created high contrast theme based on main style")

                    # 添加蓝色主题（基于主样式创建）
                    blue_style = main_style
                    blue_style = blue_style.replace("#f5f0e8", "#e3f2fd")
                    blue_style = blue_style.replace("#faf7f2", "#ffffff")
                    blue_style = blue_style.replace("#ede9e3", "#e8eaf6")
                    blue_style = blue_style.replace("#3d3229", "#1565c0")
                    blue_style = blue_style.replace("#8a7a6a", "#2196f3")
                    blue_style = blue_style.replace("#e0d8cc", "#bbdefb")
                    self._style_cache["blue"] = blue_style
                    logging.info("Created blue theme based on main style")

                    # 添加绿色主题（基于主样式创建）
                    green_style = main_style
                    green_style = green_style.replace("#f5f0e8", "#e8f5e8")
                    green_style = green_style.replace("#faf7f2", "#ffffff")
                    green_style = green_style.replace("#ede9e3", "#e0f0e0")
                    green_style = green_style.replace("#3d3229", "#2e7d32")
                    green_style = green_style.replace("#8a7a6a", "#43a047")
                    green_style = green_style.replace("#e0d8cc", "#c8e6c9")
                    self._style_cache["green"] = green_style
                    logging.info("Created green theme based on main style")
            except (OSError, UnicodeDecodeError, TypeError, ValueError) as e:
                logging.error("Failed to load main style file %s: %s", main_style_file, e)
        else:
            logging.error("Main style file not found: %s", main_style_file)

    def apply_style(self, widget: QWidget, theme: str | None = None):
        """应用样式到指定控件"""

        if theme is None:
            theme = self._current_theme

        if theme in self._style_cache:
            widget.setStyleSheet(self._style_cache[theme])
            logging.debug("Applied theme style: %s", theme)
        else:
            logging.warning("Theme style not found: %s", theme)

    def apply_global_style(self, app: QApplication, theme: str | None = None):
        """应用全局样式"""

        if theme is None:
            theme = self._current_theme

        # 跳过已废弃的 battery_analyzer 分支，直接走主题缓存逻辑

        if theme in self._style_cache:
            app.setStyleSheet(self._style_cache[theme])
            self._current_theme = theme
            self.theme_changed.emit(theme)
            logging.info("Applied global theme: %s", theme)
        else:
            logging.error("Theme style not found: %s", theme)

    def load_custom_style(self, file_path: str) -> bool:
        """加载自定义样式文件"""

        try:
            with open(file_path, encoding="utf-8") as f:
                custom_style = f.read()
                self._style_cache["custom"] = custom_style
                logging.info("Custom style loaded: %s", file_path)
                return True
        except (OSError, UnicodeDecodeError, TypeError, ValueError) as e:
            logging.error("Failed to load custom style: %s", e)
            return False

    def get_style_variables(self, theme: str | None = None) -> dict[str, Any]:
        """获取样式变量"""

        if theme is None:
            theme = self._current_theme

        # 定义常用颜色变量
        variables = {
            "modern": {
                "primary_color": "#27ae60",
                "secondary_color": "#27ae60",
                "warning_color": "#f39c12",
                "error_color": "#e74c3c",
                "background_color": "#f5f0e8",
                "surface_color": "#faf7f2",
                "text_color": "#3d3229",
                "border_color": "#e0d8cc",
            },
            "dark": {
                "primary_color": "#5dade2",
                "secondary_color": "#58d68d",
                "warning_color": "#f4d03f",
                "error_color": "#ec7063",
                "background_color": "#2c3e50",
                "surface_color": "#34495e",
                "text_color": "#ecf0f1",
                "border_color": "#4a5f7a",
            },
            "light": {
                "primary_color": "#27ae60",
                "secondary_color": "#27ae60",
                "warning_color": "#f39c12",
                "error_color": "#e74c3c",
                "background_color": "#f5f0e8",
                "surface_color": "#faf7f2",
                "text_color": "#3d3229",
                "border_color": "#e0d8cc",
            },
            "blue": {
                "primary_color": "#1e88e5",
                "secondary_color": "#43a047",
                "warning_color": "#f39c12",
                "error_color": "#e53935",
                "background_color": "#e3f2fd",
                "surface_color": "#ffffff",
                "text_color": "#1565c0",
                "border_color": "#bbdefb",
            },
            "green": {
                "primary_color": "#29b6f6",
                "secondary_color": "#388e3c",
                "warning_color": "#f39c12",
                "error_color": "#e53935",
                "background_color": "#e8f5e8",
                "surface_color": "#ffffff",
                "text_color": "#2e7d32",
                "border_color": "#c8e6c9",
            },
            "high_contrast": {
                "primary_color": "#0000ff",
                "secondary_color": "#008000",
                "warning_color": "#ff0000",
                "error_color": "#ff0000",
                "background_color": "#ffffff",
                "surface_color": "#ffffff",
                "text_color": "#000000",
                "border_color": "#000000",
            },
        }

        return variables.get(theme, variables["modern"])

    def register_font(self, font_path: str, family_name: str | None = None) -> bool:
        """
        注册自定义字体
        """

        try:
            # 延迟初始化 QFontDatabase
            if self._font_database is None:
                from PyQt6.QtGui import QFontDatabase

                self._font_database = QFontDatabase()

            font_id = self._font_database.addApplicationFont(font_path)
            if font_id != -1:
                font_families = self._font_database.applicationFontFamilies(font_id)
                if font_families:
                    family_name = family_name or font_families[0]
                    logging.info("Font registered: %s", family_name)
                    return True
            return False
        except (ImportError, AttributeError, TypeError, OSError, RuntimeError) as e:
            logging.error("Failed to register font: %s", e)
            return False

    def set_application_font(self, app: QApplication, font_family: str, size: int = 11):
        """设置应用程序字体"""

        try:
            font = QFont(font_family, size)
            app.setFont(font)
            logging.info("Application font set: %s %spt", font_family, size)
        except (ImportError, TypeError, RuntimeError, AttributeError) as e:
            logging.error("Failed to set font: %s", e)

    def create_themed_button(
        self, parent, text: str, action_type: str, callback=None, **kwargs
    ) -> "QPushButton":
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

    def create_themed_groupbox(
        self, parent, title: str, theme: str, widget: QWidget | None = None
    ) -> "QGroupBox":
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
