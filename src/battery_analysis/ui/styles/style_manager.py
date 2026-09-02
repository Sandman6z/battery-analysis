"""现代化 UI 样式管理器。

提供统一的样式管理方案，支持设计令牌（Token）驱动的 QSS 主题切换。
"""

import logging
import re
import sys
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QGroupBox, QPushButton, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


def _get_resource_dir() -> Path:
    """获取资源目录：兼容 PyInstaller 打包与开发环境。"""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "battery_analysis" / "ui" / "styles"
    return Path(__file__).parent


# ──────────────────────────────────────────────────────────────
# 设计令牌（Design Tokens）
#
# QSS 中出现的每个语义颜色都在此定义。主题切换时只替换令牌值，
# QSS 结构不变。新增颜色只需在 LIGHT/DARK 各加一行。
# ──────────────────────────────────────────────────────────────

_LIGHT_TOKENS: dict[str, str] = {
    # 背景
    "bg_primary":       "#f5f0e8",
    "bg_card":          "#faf7f2",
    "bg_input":         "#ede9e3",
    "bg_input_hover":   "#e5e0d8",
    "bg_input_focus":   "#ffffff",
    "bg_tooltip":       "#3d3229",
    # 文字
    "text_primary":     "#3d3229",
    "text_secondary":   "#8a7a6a",
    "text_inverse":     "#ffffff",
    "text_placeholder": "#adb5bd",
    # 强调色
    "accent_green":     "#27ae60",
    "accent_green_lt":  "#2ecc71",
    "accent_green_dk":  "#1e8449",
    "accent_blue":      "#3498db",
    "accent_blue_lt":   "#5dade2",
    "accent_blue_dk":   "#2980b9",
    "accent_red":       "#e74c3c",
    "accent_red_lt":    "#ec7063",
    "accent_red_dk":    "#c0392b",
    "accent_orange":    "#f39c12",
    "accent_orange_lt": "#f1c40f",
    "accent_teal":      "#1abc9c",
    # 边框 / 分隔线
    "border_default":   "#e0d8cc",
    "border_focus":     "#27ae60",
    "border_input":     "#d5cdc0",
    "border_card":      "#f0ebe3",
    # 进度条
    "progress_bar":     "#27ae60",
    "progress_bg":      "#e0d8cc",
    # 滚动条
    "scrollbar_bg":     "#e0d8cc",
    "scrollbar_handle": "#c0b8a8",
    # 按钮
    "btn_run_bg":       "#27ae60",
    "btn_run_hover":    "#2ecc71",
    "btn_run_pressed":  "#1e8449",
    "btn_cancel_bg":    "#e74c3c",
    "btn_cancel_hover": "#ec7063",
}

_DARK_TOKENS: dict[str, str] = {
    # 背景
    "bg_primary":       "#1e1e1e",
    "bg_card":          "#2a2a2a",
    "bg_input":         "#333333",
    "bg_input_hover":   "#3d3d3d",
    "bg_input_focus":   "#404040",
    "bg_tooltip":       "#3d3d3d",
    # 文字
    "text_primary":     "#e0e0e0",
    "text_secondary":   "#a0a0a0",
    "text_inverse":     "#1e1e1e",
    "text_placeholder": "#666666",
    # 强调色
    "accent_green":     "#2ecc71",
    "accent_green_lt":  "#58d68d",
    "accent_green_dk":  "#27ae60",
    "accent_blue":      "#5dade2",
    "accent_blue_lt":   "#85c1e9",
    "accent_blue_dk":   "#2980b9",
    "accent_red":       "#ec7063",
    "accent_red_lt":    "#f1948a",
    "accent_red_dk":    "#e74c3c",
    "accent_orange":    "#f4d03f",
    "accent_orange_lt": "#f7dc6f",
    "accent_teal":      "#48c9b0",
    # 边框 / 分隔线
    "border_default":   "#3a3a3a",
    "border_focus":     "#2ecc71",
    "border_input":     "#4a4a4a",
    "border_card":      "#333333",
    # 进度条
    "progress_bar":     "#2ecc71",
    "progress_bg":      "#3a3a3a",
    # 滚动条
    "scrollbar_bg":     "#2a2a2a",
    "scrollbar_handle": "#4a4a4a",
    # 按钮
    "btn_run_bg":       "#2ecc71",
    "btn_run_hover":    "#58d68d",
    "btn_run_pressed":  "#27ae60",
    "btn_cancel_bg":    "#ec7063",
    "btn_cancel_hover": "#f1948a",
}

THEMES: dict[str, dict[str, str]] = {
    "light": _LIGHT_TOKENS,
    "dark": _DARK_TOKENS,
}

# QSS 中出现的所有硬编码颜色 → 令牌名的映射表。
# 按长度降序排列，避免短色值误匹配长色值（如 #abc 匹配到 #abcdef）。
_COLOR_TO_TOKEN: list[tuple[str, str]] = []


def _build_color_map() -> list[tuple[str, str]]:
    """从 LIGHT 令牌集构建颜色→令牌映射，按颜色长度降序排列。"""
    mapping: list[tuple[str, str]] = []
    for token, color in _LIGHT_TOKENS.items():
        mapping.append((color.lower(), token))
    # 暗色主题中与亮色不同的颜色也要映射（如 #2c3e50 不在 LIGHT 中但 DARK 中有）
    # 这些颜色在 QSS 原文中不会出现，不需要映射
    mapping.sort(key=lambda x: -len(x[0]))
    return mapping


_COLOR_TO_TOKEN = _build_color_map()


def _resolve_qss_urls(qss: str, style_dir: Path) -> str:
    """将 QSS 中 url() 的相对路径解析为绝对路径。"""

    def _replace(match: re.Match) -> str:
        url_path = match.group(1)
        if url_path.startswith((":/", "/", "http")):
            return match.group(0)
        abs_path = (style_dir / url_path).resolve()
        if abs_path.exists():
            return f"url({abs_path.as_posix()})"
        return match.group(0)

    return re.sub(r"url\(([^)]+)\)", _replace, qss)


class ThemeEngine(QObject):
    """Token 驱动的主题引擎。

    工作流程：
    1. 加载原始 QSS（亮色主题的硬编码颜色）
    2. 用正则将硬编码颜色替换为 `{token}` 占位符，得到 QSS 模板
    3. 切换主题时，用对应令牌集渲染模板 → 应用到 app
    """

    theme_changed = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._style_dir = _get_resource_dir()
        self._qss_template: str = ""
        self._current_theme: str = "light"
        self._tokens: dict[str, str] = dict(_LIGHT_TOKENS)

        self._load_and_tokenize_qss()

    def _load_and_tokenize_qss(self) -> None:
        """加载 QSS 文件，将硬编码颜色替换为令牌占位符。"""
        qss_path = self._style_dir / "battery_analyzer.qss"
        if not qss_path.exists():
            logger.error("QSS file not found: %s", qss_path)
            return

        try:
            with open(qss_path, encoding="utf-8") as f:
                qss = f.read()
        except (OSError, UnicodeDecodeError) as e:
            logger.error("Failed to load QSS: %s", e)
            return

        # 解析 url() 路径
        qss = _resolve_qss_urls(qss, self._style_dir)

        # 将硬编码颜色替换为令牌占位符
        # 按颜色长度降序处理，避免短色值误匹配
        for color, token in _COLOR_TO_TOKEN:
            # 只匹配完整色值（前面不是字母数字，后面也不是）
            pattern = re.compile(r"(?<![0-9a-fA-F])" + re.escape(color) + r"(?![0-9a-fA-F])", re.IGNORECASE)
            qss = pattern.sub(f"{{{token}}}", qss)

        self._qss_template = qss
        logger.info("QSS template created with %d tokens", len(_COLOR_TO_TOKEN))

    def set_theme(self, theme_name: str) -> None:
        """切换主题并应用到 QApplication。"""
        if theme_name not in THEMES:
            logger.warning("Unknown theme: %s, falling back to light", theme_name)
            theme_name = "light"

        self._tokens = THEMES[theme_name]
        self._current_theme = theme_name

        app = QApplication.instance()
        if app is not None:
            qss = self._render()
            app.setStyleSheet(qss)
            self.theme_changed.emit(theme_name)
            logger.info("Theme applied: %s", theme_name)

    def _render(self) -> str:
        """用当前令牌集渲染 QSS 模板。"""
        qss = self._qss_template
        for token, value in self._tokens.items():
            qss = qss.replace(f"{{{token}}}", value)
        return qss

    def get_current_theme(self) -> str:
        return self._current_theme

    def get_token(self, name: str) -> str:
        """获取当前主题的令牌值。"""
        return self._tokens.get(name, "")

    def get_available_themes(self) -> list[str]:
        return list(THEMES.keys())


# ──────────────────────────────────────────────────────────────
# 全局实例（兼容旧 API）
# ──────────────────────────────────────────────────────────────

_theme_engine: ThemeEngine | None = None


def get_theme_engine() -> ThemeEngine:
    """获取全局 ThemeEngine 实例（延迟初始化）。"""
    global _theme_engine
    if _theme_engine is None:
        _theme_engine = ThemeEngine()
    return _theme_engine


# ──────────────────────────────────────────────────────────────
# 旧 StyleManager API 兼容层
# ──────────────────────────────────────────────────────────────

class StyleManager(QObject):
    """兼容旧 API 的样式管理器，内部委托给 ThemeEngine。"""

    style_loaded = pyqtSignal(str)
    theme_changed = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._engine = get_theme_engine()
        self._engine.theme_changed.connect(self.theme_changed.emit)

    def apply_style(self, widget: QWidget, theme: str | None = None):
        if theme:
            self._engine.set_theme(theme)
        qss = self._engine._render()
        widget.setStyleSheet(qss)

    def apply_global_style(self, app: QApplication, theme: str | None = None):
        if theme:
            self._engine.set_theme(theme)
        else:
            self._engine.set_theme(self._engine.get_current_theme())

    def get_current_theme(self) -> str:
        return self._engine.get_current_theme()

    def get_available_themes(self) -> list[str]:
        return self._engine.get_available_themes()

    def get_style_variables(self, theme: str | None = None) -> dict[str, Any]:
        tokens = THEMES.get(theme or self._engine.get_current_theme(), _LIGHT_TOKENS)
        return {
            "primary_color": tokens.get("accent_green", "#27ae60"),
            "secondary_color": tokens.get("accent_blue", "#3498db"),
            "warning_color": tokens.get("accent_orange", "#f39c12"),
            "error_color": tokens.get("accent_red", "#e74c3c"),
            "background_color": tokens.get("bg_primary", "#f5f0e8"),
            "surface_color": tokens.get("bg_card", "#faf7f2"),
            "text_color": tokens.get("text_primary", "#3d3229"),
            "border_color": tokens.get("border_default", "#e0d8cc"),
        }

    def register_font(self, font_path: str, family_name: str | None = None) -> bool:
        try:
            from PyQt6.QtGui import QFontDatabase

            db = QFontDatabase()
            font_id = db.addApplicationFont(font_path)
            if font_id != -1:
                families = db.applicationFontFamilies(font_id)
                if families:
                    logger.info("Font registered: %s", family_name or families[0])
                    return True
            return False
        except (ImportError, AttributeError, TypeError, OSError, RuntimeError) as e:
            logger.error("Failed to register font: %s", e)
            return False

    def set_application_font(self, app: QApplication, font_family: str, size: int = 11):
        try:
            app.setFont(QFont(font_family, size))
        except (ImportError, TypeError, RuntimeError, AttributeError) as e:
            logger.error("Failed to set font: %s", e)

    def create_themed_button(
        self, parent, text: str, action_type: str, callback=None, **kwargs
    ) -> QPushButton:
        button = QPushButton(text, parent)
        button.setProperty("data-action", action_type)
        button.setMinimumHeight(kwargs.get("min_height", 36))
        if callback:
            button.clicked.connect(callback)
        return button

    def create_themed_groupbox(
        self, parent, title: str, theme: str, widget: QWidget | None = None
    ) -> QGroupBox:
        groupbox = QGroupBox(title, parent)
        groupbox.setProperty("data-theme", theme)
        if widget:
            layout = QVBoxLayout(groupbox)
            layout.addWidget(widget)
        return groupbox


# 全局实例
style_manager = StyleManager()


def apply_modern_theme(app: QApplication, theme: str = "light"):
    style_manager.apply_global_style(app, theme)


def create_styled_button(parent, text: str, action_type: str, callback=None):
    return style_manager.create_themed_button(parent, text, action_type, callback)


def create_styled_groupbox(parent, title: str, theme: str, widget=None):
    return style_manager.create_themed_groupbox(parent, title, theme, widget)
