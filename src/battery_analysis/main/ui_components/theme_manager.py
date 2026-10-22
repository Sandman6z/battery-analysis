"""主题管理模块。

负责应用程序的主题切换，内部委托给 ThemeEngine（Token 驱动）。
"""

import logging

from PyQt6.QtCore import QSettings

from battery_analysis.ui.styles.style_manager import ThemeEngine, get_theme_engine
from battery_analysis.ui.styles.theme_settings import THEME_SETTING_KEY, normalize_theme

logger = logging.getLogger(__name__)


class ThemeManager:
    """主题管理器，提供 Light/Dark 主题切换。"""

    def __init__(self, main_window=None) -> None:
        self.main_window = main_window
        self._engine: ThemeEngine = get_theme_engine()

    def set_theme(self, theme_name: str) -> None:
        """设置应用程序主题。

        Args:
            theme_name: "light"、"dark" 或 "system"
        """
        preference = normalize_theme(theme_name)
        self._engine.set_theme(preference)
        QSettings().setValue(THEME_SETTING_KEY, preference)
        if self.main_window is not None:
            status_bar = getattr(self.main_window, "statusBar_BatteryAnalysis", None)
            if status_bar is not None:
                status_bar.showMessage(f"Switched to {self.get_current_theme()} theme")

    def get_current_theme(self) -> str:
        return self._engine.get_current_theme()

    def get_available_themes(self) -> list[str]:
        return self._engine.get_available_themes()
