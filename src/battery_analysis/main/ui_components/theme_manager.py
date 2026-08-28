"""
主题管理模块

此模块负责应用程序的主题切换和管理功能，包括：
- 设置应用程序主题样式
- 管理主题动作映射
- 处理主题切换事件
"""

# 标准库导入
import sys
import logging

# 第三方库导入
import PyQt6.QtWidgets as QW
import PyQt6.QtCore as QC

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _


class ThemeManager:
    """
    主题管理器类，负责应用程序的主题切换和管理
    """
    
    def __init__(self, main_window=None):
        """
        初始化主题管理器

        Args:
            main_window: 主窗口实例（旧接口）
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # 初始化主题动作映射
        self._initialize_theme_actions()
    
    def _initialize_theme_actions(self):
        """
        初始化主题动作映射
        """
        self.theme_actions = {}
        
        # 定义主题名称和对应的动作名称映射
        theme_action_map = {
            "System Default": "actionSystem_Default",
            "Windows 11": "actionWindows_11",
            "Windows Vista": "actionWindows_Vista",
            "Fusion": "actionFusion",
            "Dark Theme": "actionDark_Theme"
        }
        
        # 定义主题工具提示
        theme_tooltips = {
            "System Default": _("Use System Default Theme"),
            "Windows 11": _("Use Windows 11 Style Theme"),
            "Windows Vista": _("Use Windows Vista Style Theme"),
            "Fusion": _("Use Cross-platform Fusion Theme"),
            "Dark Theme": _("Use Dark Theme for Night Use")
        }
        
        # 检查并添加存在的主题动作
        for theme_name, action_name in theme_action_map.items():
            if hasattr(self.main_window, action_name):
                action = getattr(self.main_window, action_name)
                self.theme_actions[theme_name] = action
                action.setCheckable(True)
                # 添加主题工具提示
                if theme_name in theme_tooltips:
                    action.setToolTip(theme_tooltips[theme_name])
    
    def set_theme(self, theme_name) -> None:
        """
        设置应用程序主题
        
        Args:
            theme_name: 主题名称
        """
        app = QW.QApplication.instance()
        
        # 清除现有的样式表
        app.setStyleSheet("")
        
        # 清除所有主题动作的选中状态
        for action in self.theme_actions.values():
            action.setChecked(False)
        
        try:
            if theme_name == "System Default":
                # 使用系统默认样式
                app.setStyle(QW.QStyleFactory.create(
                    "windowsvista" if sys.platform == "win32" else "fusion"))
                self.main_window.statusBar_BatteryAnalysis.showMessage(_("Switched to System Default theme"))
            elif theme_name == "Windows 11":
                # 尝试使用Windows 11样式（如果可用）
                if sys.platform == "win32":
                    app.setStyle(QW.QStyleFactory.create("windowsvista"))
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        "Switched to Windows 11 theme")
                else:
                    # 非Windows平台回退到Fusion
                    app.setStyle(QW.QStyleFactory.create("fusion"))
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        "Switched to Fusion theme (Windows 11 style is unavailable on this platform)")
            elif theme_name == "Windows Vista":
                # 使用Windows Vista样式
                if sys.platform == "win32":
                    app.setStyle(QW.QStyleFactory.create("windowsvista"))
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        "Switched to Windows Vista theme")
                else:
                    # 非Windows平台回退到Fusion
                    app.setStyle(QW.QStyleFactory.create("fusion"))
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        "Switched to Fusion theme (Windows Vista style is unavailable on this platform)")
            elif theme_name == "Fusion":
                # 使用Fusion样式（跨平台）
                app.setStyle(QW.QStyleFactory.create("fusion"))
                self.main_window.statusBar_BatteryAnalysis.showMessage(_("Switched to Fusion theme"))
            elif theme_name == "Dark Theme":
                # 使用深色主题
                try:
                    # 尝试使用我们的QSS主题系统
                    from battery_analysis.ui.styles import style_manager
                    style_manager.apply_global_style(app, "dark")
                    self.main_window.statusBar_BatteryAnalysis.showMessage(_("Switched to Dark theme"))
                except (ImportError, AttributeError, TypeError, RuntimeError) as e:
                    # 如果主题系统加载失败，使用简单的深色主题样式表
                    dark_stylesheet = """QWidget {
    background-color: #2b2b2b;
    color: #cccccc;
}
QMenuBar {
    background-color: #2b2b2b;
    color: #cccccc;
}
QMenu {
    background-color: #3a3a3a;
    color: #cccccc;
}
QMenu::item:selected {
    background-color: #555555;
}
QPushButton {
    background-color: #4a4a4a;
    border: none;
    border-radius: 8px;
    color: #cccccc;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #555555;
}
QLineEdit, QComboBox, QTextEdit, QSpinBox {
    background-color: #3a3a3a;
    border: none;
    border-radius: 8px;
    color: #cccccc;
    padding: 8px 12px;
}
QTableWidget {
    background-color: #3a3a3a;
    color: #cccccc;
    alternate-background-color: #4a4a4a;
    border: none;
}
QHeaderView::section {
    background-color: #4a4a4a;
    color: #cccccc;
}
QGroupBox {
    border: none;
    color: #cccccc;
}
QGroupBox::title {
    color: #cccccc;
}
QFrame {
    border: none;
    background: transparent;
}
"""
                    app.setStyleSheet(dark_stylesheet)
                    self.main_window.statusBar_BatteryAnalysis.showMessage(_("Switched to Simple Dark theme"))
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.error("Failed to switch theme: %s", e)
            self.main_window.statusBar_BatteryAnalysis.showMessage(f"Failed to switch theme: {str(e)}")
        
        # 设置当前主题动作的选中状态
        if theme_name in self.theme_actions:
            self.theme_actions[theme_name].setChecked(True)
        
        # 确保界面立即更新
        # 移除 processEvents()（roadmap #12）：setStyleSheet 走 Qt 样式系统
        # 自动重绘，显式 processEvents 只会重入事件循环。
    
    def toggle_statusbar(self):
        """
        切换状态栏的显示/隐藏状态
        """
        self.main_window.statusBar_BatteryAnalysis.setVisible(
            self.main_window.actionShow_Statusbar.isChecked())
