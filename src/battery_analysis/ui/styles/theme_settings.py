"""主题偏好的校验与旧配置迁移，不依赖主题引擎。"""

import logging

from PyQt6.QtCore import QSettings

logger = logging.getLogger(__name__)

THEME_SETTING_KEY = "display/theme"
DEFAULT_THEME = "light"
THEME_PREFERENCES = ("light", "dark", "system")


def normalize_theme(theme: object) -> str:
    """将旧名称和外部配置转换为支持的主题偏好。"""
    if isinstance(theme, str):
        name = theme.strip().lower()
        if name == "modern":
            return DEFAULT_THEME
        if name in THEME_PREFERENCES:
            return name
    logger.warning("Unknown theme: %r, falling back to %s", theme, DEFAULT_THEME)
    return DEFAULT_THEME


def load_theme_preference(settings: QSettings | None = None) -> str:
    """读取并修复旧值，避免每次启动重复回退。"""
    if settings is None:
        settings = QSettings()
    stored = settings.value(THEME_SETTING_KEY, DEFAULT_THEME)
    theme = normalize_theme(stored)
    if stored != theme:
        settings.setValue(THEME_SETTING_KEY, theme)
    return theme
