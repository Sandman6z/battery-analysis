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
        安全地设置所有菜单的快捷键和工具提示
        """
        try:
            # 文件菜单快捷键和工具提示
            if hasattr(self.main_window, 'actionNew'):
                self.main_window.actionNew.setShortcut(QG.QKeySequence.StandardKey.New)
                self.main_window.actionNew.setToolTip(_("tooltip_new", "新建项目"))
            if hasattr(self.main_window, 'actionOpen'):
                self.main_window.actionOpen.setShortcut(QG.QKeySequence.StandardKey.Open)
                self.main_window.actionOpen.setToolTip(_("tooltip_open", "打开项目"))
            if hasattr(self.main_window, 'actionSave'):
                self.main_window.actionSave.setShortcut(QG.QKeySequence.StandardKey.Save)
                self.main_window.actionSave.setToolTip(_("tooltip_save", "保存设置"))
            if hasattr(self.main_window, 'actionSave_As'):
                self.main_window.actionSave_As.setShortcut(
                    QG.QKeySequence.StandardKey.SaveAs)
                self.main_window.actionSave_As.setToolTip(_("tooltip_save_as", "另存为"))
            if hasattr(self.main_window, 'actionExit'):
                self.main_window.actionExit.setShortcut(QG.QKeySequence.StandardKey.Quit)
                self.main_window.actionExit.setToolTip(_("tooltip_exit", "退出应用"))

            # 编辑菜单快捷键和工具提示
            if hasattr(self.main_window, 'actionUndo'):
                self.main_window.actionUndo.setShortcut(QG.QKeySequence.StandardKey.Undo)
                self.main_window.actionUndo.setToolTip(_("tooltip_undo", "撤销操作"))
            if hasattr(self.main_window, 'actionRedo'):
                self.main_window.actionRedo.setShortcut(QG.QKeySequence.StandardKey.Redo)
                self.main_window.actionRedo.setToolTip(_("tooltip_redo", "重做操作"))
            if hasattr(self.main_window, 'actionCut'):
                self.main_window.actionCut.setShortcut(QG.QKeySequence.StandardKey.Cut)
                self.main_window.actionCut.setToolTip(_("tooltip_cut", "剪切选中内容"))
            if hasattr(self.main_window, 'actionCopy'):
                self.main_window.actionCopy.setShortcut(QG.QKeySequence.StandardKey.Copy)
                self.main_window.actionCopy.setToolTip(_("tooltip_copy", "复制选中内容"))
            if hasattr(self.main_window, 'actionPaste'):
                self.main_window.actionPaste.setShortcut(QG.QKeySequence.StandardKey.Paste)
                self.main_window.actionPaste.setToolTip(_("tooltip_paste", "粘贴内容"))

            # 视图菜单快捷键和工具提示
            if hasattr(self.main_window, 'actionZoom_In'):
                self.main_window.actionZoom_In.setShortcut(
                    QG.QKeySequence.StandardKey.ZoomIn)
                self.main_window.actionZoom_In.setToolTip(_("tooltip_zoom_in", "放大界面"))
            if hasattr(self.main_window, 'actionZoom_Out'):
                self.main_window.actionZoom_Out.setShortcut(
                    QG.QKeySequence.StandardKey.ZoomOut)
                self.main_window.actionZoom_Out.setToolTip(_("tooltip_zoom_out", "缩小界面"))
            if hasattr(self.main_window, 'actionReset_Zoom'):
                self.main_window.actionReset_Zoom.setToolTip(_("tooltip_reset_zoom", "重置界面缩放"))
            if hasattr(self.main_window, 'actionShow_Toolbar'):
                self.main_window.actionShow_Toolbar.setCheckable(True)
                self.main_window.actionShow_Toolbar.setChecked(False)
                self.main_window.actionShow_Toolbar.setToolTip(_("tooltip_show_toolbar", "显示/隐藏工具栏"))
                # 确保toolbar的可见性与action状态一致
                if hasattr(self.main_window, 'toolBar'):
                    self.main_window.toolBar.setVisible(False)
            if hasattr(self.main_window, 'actionShow_Statusbar'):
                self.main_window.actionShow_Statusbar.setCheckable(True)
                self.main_window.actionShow_Statusbar.setChecked(True)
                self.main_window.actionShow_Statusbar.setToolTip(_("tooltip_show_statusbar", "显示/隐藏状态栏"))

            # 工具菜单快捷键和工具提示
            if hasattr(self.main_window, 'actionCalculate_Battery'):
                self.main_window.actionCalculate_Battery.setShortcut(
                    QG.QKeySequence("Ctrl+B"))
                self.main_window.actionCalculate_Battery.setToolTip(_("tooltip_calculate_battery", "计算电池参数"))
            if hasattr(self.main_window, 'actionAnalyze_Data'):
                self.main_window.actionAnalyze_Data.setShortcut(QG.QKeySequence("Ctrl+D"))
                self.main_window.actionAnalyze_Data.setToolTip(_("tooltip_analyze_data", "分析数据"))
            if hasattr(self.main_window, 'actionGenerate_Report'):
                self.main_window.actionGenerate_Report.setShortcut(
                    QG.QKeySequence("Ctrl+R"))
                self.main_window.actionGenerate_Report.setToolTip(_("tooltip_generate_report", "生成报告"))
            if hasattr(self.main_window, 'actionBatteryChartViewer'):
                self.main_window.actionBatteryChartViewer.setToolTip(_("tooltip_chart_viewer", "打开电池图表查看器"))
            if hasattr(self.main_window, 'actionBatch_Processing'):
                self.main_window.actionBatch_Processing.setToolTip(_("tooltip_batch_processing", "批量处理数据"))
            if hasattr(self.main_window, 'actionPreferences'):
                self.main_window.actionPreferences.setToolTip(_("tooltip_preferences", "首选项设置"))

            # 帮助菜单快捷键和工具提示
            if hasattr(self.main_window, 'actionUser_Mannual'):
                self.main_window.actionUser_Mannual.setShortcut(
                    QG.QKeySequence.StandardKey.HelpContents)
                self.main_window.actionUser_Mannual.setToolTip(_("tooltip_user_manual", "打开用户手册"))
            if hasattr(self.main_window, 'actionOnline_Help'):
                self.main_window.actionOnline_Help.setShortcut(QG.QKeySequence("F1"))
                self.main_window.actionOnline_Help.setToolTip(_("tooltip_online_help", "打开在线帮助"))
            if hasattr(self.main_window, 'actionAbout'):
                self.main_window.actionAbout.setShortcut(QG.QKeySequence("Ctrl+Alt+A"))
                self.main_window.actionAbout.setToolTip(_("tooltip_about", "关于应用"))
            if hasattr(self.main_window, 'actionExport_Report'):
                self.main_window.actionExport_Report.setToolTip(_("tooltip_export_report", "导出报告"))
        except (AttributeError, TypeError, RuntimeError) as e:
            logging.error("设置菜单快捷键和工具提示失败: %s", e)
    
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
        self.main_window.actionZoom_In.triggered.connect(self.zoom_in)
        self.main_window.actionZoom_Out.triggered.connect(self.zoom_out)
        self.main_window.actionReset_Zoom.triggered.connect(self.reset_zoom)

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
    
    def zoom_in(self):
        """放大界面元素"""
        font = self.main_window.font()
        current_size = font.pointSize()
        if current_size < 20:  # 设置最大字体大小限制
            font.setPointSize(current_size + 1)
            self.main_window.setFont(font)
    
    def zoom_out(self):
        """缩小界面元素"""
        font = self.main_window.font()
        current_size = font.pointSize()
        if current_size > 8:  # 设置最小字体大小限制
            font.setPointSize(current_size - 1)
            self.main_window.setFont(font)
    
    def reset_zoom(self):
        """重置界面缩放"""
        font = self.main_window.font()
        font.setPointSize(9)  # 假设默认字体大小为9
        self.main_window.setFont(font)
    
    def update_menu_texts(self):
        """
        更新菜单文本为当前语言
        """
        # 这里可以添加菜单文本的国际化更新
        # 例如：self.main_window.actionExit.setText(_("menu_exit", "Exit"))
        pass
    
    def update_statusbar_messages(self):
        """
        更新状态栏消息为当前语言
        """
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            # 保存当前消息，以便切换语言后恢复
            current_message = self.main_window.statusBar_BatteryAnalysis.currentMessage()
            
            # 获取翻译后的状态消息
            status_ready = _("status_ready", "状态:就绪")
            
            # 更新状态栏
            if current_message in ("状态:就绪", "Ready"):
                self.main_window.statusBar_BatteryAnalysis.showMessage(status_ready)
