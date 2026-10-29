"""
窗口设置组件

负责主窗口的初始化和设置
"""

import logging

from PyQt6 import QtGui as QG

from battery_analysis.main.ui_components.menu_manager import toggle_statusbar


class WindowSetup:
    """
    窗口设置类，负责主窗口的初始化和设置
    """

    def __init__(self, main_window=None):
        """
        初始化窗口设置

        Args:
            main_window: 主窗口实例（旧接口）
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

    def init_window(self) -> None:
        """
        初始化窗口
        """
        # 调用父类方法设置窗口标题
        window_title = f"Battery Analyzer v{self.main_window.version}"
        self.main_window.setWindowTitle(window_title)

        # 加载应用图标
        self._load_application_icon()

    def _load_application_icon(self) -> QG.QIcon:
        """
        加载应用程序图标

        Returns:
            应用程序图标
        """
        try:
            from battery_analysis.main.utils.file_utils import FileUtils

            icon_paths = FileUtils.get_icon_paths(
                getattr(self.main_window, "env_detector", None),
                getattr(self.main_window, "current_directory", None),
            )

            # 遍历所有可能的路径，找到第一个存在的
            for icon_path in icon_paths:
                if icon_path.exists():
                    self.logger.debug("Application icon found: %s", icon_path)
                    app_icon = QG.QIcon(str(icon_path))
                    self.main_window.setWindowIcon(app_icon)
                    return app_icon

            # 如果都找不到，使用默认图标
            self.logger.warning("Application icon file not found; using default icon")
            return QG.QIcon()
        except (OSError, TypeError, ValueError, RuntimeError, ImportError) as e:
            # 捕获所有可能的异常，确保应用能正常启动
            self.logger.error("Failed to load application icon: %s", e)
            return QG.QIcon()

    def toggle_statusbar_safe(self) -> None:
        """兼容旧窗口入口，与菜单使用相同的切换规则。"""
        toggle_statusbar(self.main_window)
