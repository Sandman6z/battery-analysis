"""
菜单管理器模块

这个模块实现了电池分析应用的菜单管理功能，包括：
- 菜单初始化和配置
- 快捷键设置
- 菜单动作连接
- 工具栏管理
- 主题切换功能
- 缩放功能管理
"""

# 标准库导入
import logging

# 第三方库导入
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _


class MenuManager:
    """
    菜单管理器类，负责菜单和工具栏的管理
    """
    
    def __init__(self, main_window):
        """
        初始化菜单管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def setup_menu_shortcuts(self):
        """
        安全地设置所有菜单的快捷键
        """
        try:
            # 文件菜单快捷键
            if hasattr(self.main_window, 'actionNew'):
                self.main_window.actionNew.setShortcut(QG.QKeySequence.StandardKey.New)
            if hasattr(self.main_window, 'actionOpen'):
                self.main_window.actionOpen.setShortcut(QG.QKeySequence.StandardKey.Open)
            if hasattr(self.main_window, 'actionSave'):
                self.main_window.actionSave.setShortcut(QG.QKeySequence.StandardKey.Save)
            if hasattr(self.main_window, 'actionSave_As'):
                self.main_window.actionSave_As.setShortcut(
                    QG.QKeySequence.StandardKey.SaveAs)
            if hasattr(self.main_window, 'actionExit'):
                self.main_window.actionExit.setShortcut(QG.QKeySequence.StandardKey.Quit)

            # 编辑菜单快捷键
            if hasattr(self.main_window, 'actionUndo'):
                self.main_window.actionUndo.setShortcut(QG.QKeySequence.StandardKey.Undo)
            if hasattr(self.main_window, 'actionRedo'):
                self.main_window.actionRedo.setShortcut(QG.QKeySequence.StandardKey.Redo)
            if hasattr(self.main_window, 'actionCut'):
                self.main_window.actionCut.setShortcut(QG.QKeySequence.StandardKey.Cut)
            if hasattr(self.main_window, 'actionCopy'):
                self.main_window.actionCopy.setShortcut(QG.QKeySequence.StandardKey.Copy)
            if hasattr(self.main_window, 'actionPaste'):
                self.main_window.actionPaste.setShortcut(QG.QKeySequence.StandardKey.Paste)

            # 视图菜单快捷键
            if hasattr(self.main_window, 'actionZoom_In'):
                self.main_window.actionZoom_In.setShortcut(
                    QG.QKeySequence.StandardKey.ZoomIn)
            if hasattr(self.main_window, 'actionZoom_Out'):
                self.main_window.actionZoom_Out.setShortcut(
                    QG.QKeySequence.StandardKey.ZoomOut)

            # 工具菜单快捷键
            if hasattr(self.main_window, 'actionCalculate_Battery'):
                self.main_window.actionCalculate_Battery.setShortcut(
                    QG.QKeySequence("Ctrl+B"))
            if hasattr(self.main_window, 'actionAnalyze_Data'):
                self.main_window.actionAnalyze_Data.setShortcut(QG.QKeySequence("Ctrl+D"))
            if hasattr(self.main_window, 'actionGenerate_Report'):
                self.main_window.actionGenerate_Report.setShortcut(
                    QG.QKeySequence("Ctrl+R"))

            # 帮助菜单快捷键
            if hasattr(self.main_window, 'actionUser_Mannual'):
                self.main_window.actionUser_Mannual.setShortcut(
                    QG.QKeySequence.StandardKey.HelpContents)
            if hasattr(self.main_window, 'actionOnline_Help'):
                self.main_window.actionOnline_Help.setShortcut(QG.QKeySequence("F1"))
            if hasattr(self.main_window, 'actionAbout'):
                self.main_window.actionAbout.setShortcut(QG.QKeySequence("Ctrl+Alt+A"))

            # 为菜单项添加视觉提示
            if hasattr(self.main_window, 'actionShow_Toolbar'):
                self.main_window.actionShow_Toolbar.setCheckable(True)
                self.main_window.actionShow_Toolbar.setChecked(False)
                # 确保toolbar的可见性与action状态一致
                if hasattr(self.main_window, 'toolBar'):
                    self.main_window.toolBar.setVisible(False)
            if hasattr(self.main_window, 'actionShow_Statusbar'):
                self.main_window.actionShow_Statusbar.setCheckable(True)
                self.main_window.actionShow_Statusbar.setChecked(True)
        except (AttributeError, TypeError, RuntimeError) as e:
            logging.error("设置菜单快捷键失败: %s", e)
    
    def connect_menu_actions(self):
        """
        连接菜单动作
        """
        # 菜单动作连接
        self.main_window.actionExit.triggered.connect(self.main_window.handle_exit)
        self.main_window.actionAbout.triggered.connect(self.main_window.handle_about)
        self.main_window.actionUser_Mannual.triggered.connect(self.main_window.show_user_manual)
        self.main_window.actionOnline_Help.triggered.connect(self.main_window.show_online_help)

        # 常用编辑功能连接
        self.main_window.actionCopy.triggered.connect(self.main_window.copy_selected_text)
        self.main_window.actionPaste.triggered.connect(self.main_window.paste_text)
        self.main_window.actionCut.triggered.connect(self.main_window.cut_selected_text)

        # 首选项对话框连接
        self.main_window.actionPreferences.triggered.connect(self.main_window.show_preferences)

        # 工具栏和状态栏显示/隐藏功能连接
        if hasattr(self.main_window, 'actionShow_Toolbar'):
            self.main_window.actionShow_Toolbar.triggered.connect(self.main_window.toggle_toolbar_safe)
        if hasattr(self.main_window, 'actionShow_Statusbar'):
            self.main_window.actionShow_Statusbar.triggered.connect(
                self.main_window.toggle_statusbar_safe)

        # 工具菜单功能连接
        self.main_window.actionCalculate_Battery.triggered.connect(self.main_window.calculate_battery)
        self.main_window.actionAnalyze_Data.triggered.connect(self.main_window.analyze_data)
        self.main_window.actionBatteryChartViewer.triggered.connect(self.main_window.run_visualizer)
        self.main_window.actionGenerate_Report.triggered.connect(self.main_window.generate_report)
        self.main_window.actionBatch_Processing.triggered.connect(self.main_window.batch_processing)

        # 缩放功能连接
        self.main_window.actionZoom_In.triggered.connect(self.main_window.zoom_in)
        self.main_window.actionZoom_Out.triggered.connect(self.main_window.zoom_out)
        self.main_window.actionReset_Zoom.triggered.connect(self.main_window.reset_zoom)

        # 主题菜单功能连接
        self._connect_theme_actions()

        # 文件操作连接
        self.main_window.actionSave.triggered.connect(self.main_window.save_settings)
        self.main_window.actionExport_Report.triggered.connect(self.main_window.export_report)
    
    def _connect_theme_actions(self):
        """
        连接主题相关的菜单动作
        """
        # 主题菜单功能连接
        if hasattr(self.main_window, 'actionSystem_Default'):
            self.main_window.actionSystem_Default.triggered.connect(
                lambda: self.main_window.set_theme("System Default"))
        if hasattr(self.main_window, 'actionWindows_11'):
            self.main_window.actionWindows_11.triggered.connect(
                lambda: self.main_window.set_theme("Windows 11"))
        if hasattr(self.main_window, 'actionWindows_Vista'):
            self.main_window.actionWindows_Vista.triggered.connect(
                lambda: self.main_window.set_theme("Windows Vista"))
        if hasattr(self.main_window, 'actionFusion'):
            self.main_window.actionFusion.triggered.connect(
                lambda: self.main_window.set_theme("Fusion"))
        if hasattr(self.main_window, 'actionDark_Theme'):
            self.main_window.actionDark_Theme.triggered.connect(
                lambda: self.main_window.set_theme("Dark Theme"))
    
    def toggle_toolbar_safe(self):
        """
        安全地切换工具栏的显示/隐藏状态
        """
        if hasattr(self.main_window, 'actionShow_Toolbar') and hasattr(self.main_window, 'toolBar'):
            self.main_window.toolBar.setVisible(self.main_window.actionShow_Toolbar.isChecked())
        elif hasattr(self.main_window, 'toolBar'):
            # 如果没有actionShow_Toolbar，只是切换显示状态
            self.main_window.toolBar.setVisible(not self.main_window.toolBar.isVisible())
    
    def toggle_statusbar_safe(self):
        """
        安全地切换状态栏的显示/隐藏状态
        """
        if hasattr(self.main_window, 'actionShow_Statusbar') and hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.setVisible(
                self.main_window.actionShow_Statusbar.isChecked())
        elif hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            # 如果没有actionShow_Statusbar，只是切换显示状态
            self.main_window.statusBar_BatteryAnalysis.setVisible(
                not self.main_window.statusBar_BatteryAnalysis.isVisible())
    
    def update_menu_texts(self):
        """
        更新菜单文本为当前语言
        """
        # 这里可以添加菜单文本的国际化更新
        # 例如：self.main_window.actionExit.setText(_("menu_exit", "Exit"))
        pass
