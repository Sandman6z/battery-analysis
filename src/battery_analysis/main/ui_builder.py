"""
主窗口 UI 构建器（重构版）

职责精简为：
  - 创建电池分析主页面作为 centralWidget
  - 构建菜单栏、状态栏
  - 窗口居中

主页面的具体布局由 tabs/ 下的独立 QWidget 子类管理。
"""

from typing import TYPE_CHECKING

import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

from battery_analysis.i18n import _

if TYPE_CHECKING:
    from battery_analysis.main.main_window import Main


class UIBuilder:
    """主窗口 UI 构建器"""

    def __init__(self, main_window: Main):
        self.main_window = main_window

    def build_ui(self) -> None:
        """构建主窗口 UI"""
        mw = self.main_window
        mw.setWindowTitle(_("Battery Analyzer"))
        mw.setMinimumSize(720, 600)
        mw.resize(720, 750)
        mw.setCursor(QG.QCursor(QC.Qt.CursorShape.ArrowCursor))

        # ── 电池分析主页面 ──
        self._build_analysis_page()

        # ── 状态栏 ──
        self._build_status_bar()

        # ── 窗口居中 ──
        self._adjust_window_size()

    def _build_analysis_page(self) -> None:
        """直接显示电池分析页面，转换工具由菜单独立打开。"""
        from battery_analysis.main.tabs.battery_tab import BatteryAnalysisTab

        mw = self.main_window
        battery_tab = BatteryAnalysisTab(main_window=mw)
        mw.setCentralWidget(battery_tab)
        mw.centralwidget = battery_tab  # 兼容初始化管理器的 can_execute 检查

    def _build_status_bar(self) -> None:
        """构建状态栏"""
        mw = self.main_window
        mw.statusBar_BatteryAnalysis = QW.QStatusBar()
        mw.statusBar_BatteryAnalysis.setObjectName("statusBar_BatteryAnalysis")
        mw.setStatusBar(mw.statusBar_BatteryAnalysis)

    def _adjust_window_size(self) -> None:
        """调整窗口：最小完整显示，不超出屏幕，自动居中"""
        primary_screen = QW.QApplication.primaryScreen()
        if primary_screen is None:
            return
        screen = primary_screen.availableGeometry()
        ref_w, ref_h = 720, 750
        w = max(min(ref_w, screen.width()), 720)
        h = max(min(ref_h, screen.height()), 600)
        self.main_window.resize(w, h)

        frame = self.main_window.frameGeometry()
        frame.moveCenter(screen.center())
        if frame.top() < screen.top():
            frame.moveTop(screen.top())
        if frame.left() < screen.left():
            frame.moveLeft(screen.left())
        self.main_window.move(frame.topLeft())

    # ─────────────────────────────────────────────────────
    #  Actions（供菜单栏使用）
    # ─────────────────────────────────────────────────────
    def create_actions(self) -> None:
        mw = self.main_window

        # 文件菜单动作
        mw.actionExit = QG.QAction(_("Exit"), mw)
        mw.actionExit.setObjectName("actionExit")
        mw.actionExit.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Quit))

        # 编辑菜单动作
        mw.actionCut = QG.QAction(_("Cut"), mw)
        mw.actionCut.setObjectName("actionCut")
        mw.actionCut.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Cut))

        mw.actionCopy = QG.QAction(_("Copy"), mw)
        mw.actionCopy.setObjectName("actionCopy")
        mw.actionCopy.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Copy))

        mw.actionPaste = QG.QAction(_("Paste"), mw)
        mw.actionPaste.setObjectName("actionPaste")
        mw.actionPaste.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Paste))

        mw.actionPreferences = QG.QAction(_("Preferences"), mw)
        mw.actionPreferences.setObjectName("actionPreferences")

        # 视图菜单动作
        mw.actionShow_Statusbar = QG.QAction(_("Show Statusbar"), mw)
        mw.actionShow_Statusbar.setObjectName("actionShow_Statusbar")
        mw.actionShow_Statusbar.setCheckable(True)
        mw.actionShow_Statusbar.setChecked(True)

        mw.actionZoom_In = QG.QAction(_("Zoom In"), mw)
        mw.actionZoom_In.setObjectName("actionZoom_In")
        mw.actionZoom_In.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.ZoomIn))

        mw.actionZoom_Out = QG.QAction(_("Zoom Out"), mw)
        mw.actionZoom_Out.setObjectName("actionZoom_Out")
        mw.actionZoom_Out.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.ZoomOut))

        mw.actionReset_Zoom = QG.QAction(_("Reset Zoom"), mw)
        mw.actionReset_Zoom.setObjectName("actionReset_Zoom")

        # 工具菜单动作
        mw.actionBatteryChartViewer = QG.QAction(_("BatteryChartViewer"), mw)
        mw.actionBatteryChartViewer.setObjectName("actionBatteryChartViewer")

        mw.actionNdaxConverter = QG.QAction(_("NDAX Converter"), mw)
        mw.actionNdaxConverter.setObjectName("actionNdaxConverter")

        mw.actionAnalyze_Data = QG.QAction(_("Analyze Data"), mw)
        mw.actionAnalyze_Data.setObjectName("actionAnalyze_Data")

        mw.actionConfiguration = QG.QAction(_("Configuration"), mw)
        mw.actionConfiguration.setObjectName("actionConfiguration")

        # 帮助菜单动作
        mw.actionUser_Mannual = QG.QAction(_("User Manual"), mw)
        mw.actionUser_Mannual.setObjectName("actionUser_Mannual")

        mw.actionOnline_Help = QG.QAction(_("Online Help"), mw)
        mw.actionOnline_Help.setObjectName("actionOnline_Help")

        mw.actionAbout = QG.QAction(_("About"), mw)
        mw.actionAbout.setObjectName("actionAbout")

        # 主题菜单动作
        mw.actionLight_Theme = QG.QAction(_("Light Theme"), mw)
        mw.actionLight_Theme.setObjectName("actionLight_Theme")

        mw.actionDark_Theme = QG.QAction(_("Dark Theme"), mw)
        mw.actionDark_Theme.setObjectName("actionDark_Theme")

    def create_menus(self) -> None:
        mw = self.main_window
        menubar = QW.QMenuBar(mw)
        mw.setMenuBar(menubar)

        # 文件菜单
        file_menu = QW.QMenu(_("File"), menubar)
        menubar.addMenu(file_menu)
        file_menu.addAction(mw.actionExit)

        # 编辑菜单
        edit_menu = QW.QMenu(_("Edit"), menubar)
        menubar.addMenu(edit_menu)
        edit_menu.addAction(mw.actionCut)
        edit_menu.addAction(mw.actionCopy)
        edit_menu.addAction(mw.actionPaste)
        edit_menu.addSeparator()
        edit_menu.addAction(mw.actionPreferences)

        # 视图菜单
        view_menu = QW.QMenu(_("View"), menubar)
        menubar.addMenu(view_menu)
        view_menu.addAction(mw.actionShow_Statusbar)
        view_menu.addSeparator()
        view_menu.addAction(mw.actionZoom_In)
        view_menu.addAction(mw.actionZoom_Out)
        view_menu.addAction(mw.actionReset_Zoom)
        view_menu.addSeparator()
        view_menu.addAction(mw.actionLight_Theme)
        view_menu.addAction(mw.actionDark_Theme)

        # 工具菜单
        tools_menu = QW.QMenu(_("Tools"), menubar)
        menubar.addMenu(tools_menu)
        tools_menu.addAction(mw.actionBatteryChartViewer)
        tools_menu.addAction(mw.actionNdaxConverter)
        tools_menu.addSeparator()
        tools_menu.addAction(mw.actionAnalyze_Data)
        tools_menu.addSeparator()
        tools_menu.addAction(mw.actionConfiguration)

        # 帮助菜单
        help_menu = QW.QMenu(_("Help"), menubar)
        menubar.addMenu(help_menu)
        help_menu.addAction(mw.actionUser_Mannual)
        help_menu.addAction(mw.actionOnline_Help)
        help_menu.addSeparator()
        help_menu.addAction(mw.actionAbout)
