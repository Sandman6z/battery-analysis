"""
主窗口 UI 构建器（重构版）

职责精简为：
  - 创建 QTabWidget 作为 centralWidget
  - 注册各 Tab 页面
  - 构建菜单栏、状态栏
  - 窗口居中

各 Tab 的具体布局由 tabs/ 下的独立 QWidget 子类管理。
"""

import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW
from pathlib import Path

from battery_analysis.i18n import _


class UIBuilder:
    """主窗口 UI 构建器"""

    def __init__(self, main_window: QW.QMainWindow):
        self.main_window = main_window

    def build_ui(self) -> None:
        """构建主窗口 UI"""
        mw = self.main_window
        mw.setWindowTitle(_("Battery Analyzer"))
        mw.setMinimumSize(800, 600)
        mw.resize(920, 750)
        mw.setCursor(QG.QCursor(QC.Qt.CursorShape.ArrowCursor))

        # ── TabWidget 作为 centralWidget ──
        self._build_tab_widget()

        # ── 状态栏 ──
        self._build_status_bar()

        # ── 窗口居中 ──
        self._adjust_window_size()

    def _build_tab_widget(self) -> None:
        """创建 QTabWidget 并注册各 Tab 页面"""
        mw = self.main_window

        tab_widget = QW.QTabWidget()
        tab_widget.setTabPosition(QW.QTabWidget.TabPosition.North)
        tab_widget.setDocumentMode(True)
        tab_widget.setTabShape(QW.QTabWidget.TabShape.Rounded)

        # Tab 0: NDAX 转换（分析前的准备工作，排在前面）
        from battery_analysis.main.tabs.ndax_tab import NdaxConverterTab
        ndax_tab = NdaxConverterTab()
        tab_widget.addTab(ndax_tab, _("📊 NDAX转换"))

        # Tab 1: 电池分析
        from battery_analysis.main.tabs.battery_tab import BatteryAnalysisTab
        battery_tab = BatteryAnalysisTab(main_window=mw)
        tab_widget.addTab(battery_tab, _("🔋 电池分析"))

        # 连接跨 Tab 信号：找到 test profile XML → 自动填入电池分析
        ndax_tab.test_profile_found.connect(
            lambda xml_path: self._on_test_profile_found(xml_path)
        )

        mw.setCentralWidget(tab_widget)
        mw.centralwidget = tab_widget  # 兼容初始化管理器的 can_execute 检查
        mw._tab_widget = tab_widget
        mw._ndax_tab = ndax_tab

    def _on_test_profile_found(self, xml_path: str) -> None:
        """找到 test profile XML 后，统一走 path_manager 填入所有相关字段

        填入顺序：
          1. Test Profile (lineEdit_TestProfile)
          2. Input Path  -> path_manager.set_input_path -> 触发 sigSetVersion -> 自动获取 Report Ver.
          3. Output Path -> path_manager.set_output_path
        """
        mw = self.main_window
        if not hasattr(mw, "path_manager"):
            return

        # 1. 填入 Test Profile
        if hasattr(mw, "lineEdit_TestProfile"):
            mw.lineEdit_TestProfile.setText(xml_path)

        # 2 & 3. 走 path_manager 统一逻辑（含版本号自动获取）
        profile_dir = Path(xml_path).parent
        parent_dir = str(profile_dir.parent)
        mw.path_manager.set_input_path(parent_dir)
        mw.path_manager.set_output_path(parent_dir)

    def _build_status_bar(self) -> None:
        """构建状态栏"""
        mw = self.main_window
        mw.statusBar_BatteryAnalysis = QW.QStatusBar()
        mw.statusBar_BatteryAnalysis.setObjectName("statusBar_BatteryAnalysis")
        mw.setStatusBar(mw.statusBar_BatteryAnalysis)

    def _adjust_window_size(self) -> None:
        """调整窗口：最小完整显示，不超出屏幕，自动居中"""
        screen = QW.QApplication.primaryScreen().availableGeometry()
        ref_w, ref_h = 920, 750
        w = max(min(ref_w, screen.width()), 800)
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
        mw.actionNew = QG.QAction(_("New"), mw)
        mw.actionNew.setObjectName("actionNew")
        mw.actionNew.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.New))

        mw.actionOpen = QG.QAction(_("Open"), mw)
        mw.actionOpen.setObjectName("actionOpen")
        mw.actionOpen.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Open))

        mw.actionSave = QG.QAction(_("Save"), mw)
        mw.actionSave.setObjectName("actionSave")
        mw.actionSave.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Save))

        mw.actionSave_As = QG.QAction(_("Save As"), mw)
        mw.actionSave_As.setObjectName("actionSave_As")
        mw.actionSave_As.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.SaveAs))

        mw.actionExport_Report = QG.QAction(_("Export Report"), mw)
        mw.actionExport_Report.setObjectName("actionExport_Report")

        mw.actionExit = QG.QAction(_("Exit"), mw)
        mw.actionExit.setObjectName("actionExit")
        mw.actionExit.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Quit))

        # 编辑菜单动作
        mw.actionUndo = QG.QAction(_("Undo"), mw)
        mw.actionUndo.setObjectName("actionUndo")
        mw.actionUndo.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Undo))

        mw.actionRedo = QG.QAction(_("Redo"), mw)
        mw.actionRedo.setObjectName("actionRedo")
        mw.actionRedo.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Redo))

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

        mw.actionCalculate_Battery = QG.QAction(_("Calculate Battery"), mw)
        mw.actionCalculate_Battery.setObjectName("actionCalculate_Battery")

        mw.actionAnalyze_Data = QG.QAction(_("Analyze Data"), mw)
        mw.actionAnalyze_Data.setObjectName("actionAnalyze_Data")

        mw.actionGenerate_Report = QG.QAction(_("Generate Report"), mw)
        mw.actionGenerate_Report.setObjectName("actionGenerate_Report")

        mw.actionBatch_Processing = QG.QAction(_("Batch Processing"), mw)
        mw.actionBatch_Processing.setObjectName("actionBatch_Processing")

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
        menubar = mw.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu(_("File"))
        file_menu.addAction(mw.actionNew)
        file_menu.addAction(mw.actionOpen)
        file_menu.addAction(mw.actionSave)
        file_menu.addAction(mw.actionSave_As)
        file_menu.addSeparator()
        file_menu.addAction(mw.actionExport_Report)
        file_menu.addSeparator()
        file_menu.addAction(mw.actionExit)

        # 编辑菜单
        edit_menu = menubar.addMenu(_("Edit"))
        edit_menu.addAction(mw.actionUndo)
        edit_menu.addAction(mw.actionRedo)
        edit_menu.addSeparator()
        edit_menu.addAction(mw.actionCut)
        edit_menu.addAction(mw.actionCopy)
        edit_menu.addAction(mw.actionPaste)
        edit_menu.addSeparator()
        edit_menu.addAction(mw.actionPreferences)

        # 视图菜单
        view_menu = menubar.addMenu(_("View"))
        view_menu.addAction(mw.actionShow_Statusbar)
        view_menu.addSeparator()
        view_menu.addAction(mw.actionZoom_In)
        view_menu.addAction(mw.actionZoom_Out)
        view_menu.addAction(mw.actionReset_Zoom)
        view_menu.addSeparator()
        view_menu.addAction(mw.actionLight_Theme)
        view_menu.addAction(mw.actionDark_Theme)

        # 工具菜单
        tools_menu = menubar.addMenu(_("Tools"))
        tools_menu.addAction(mw.actionBatteryChartViewer)
        tools_menu.addSeparator()
        tools_menu.addAction(mw.actionCalculate_Battery)
        tools_menu.addAction(mw.actionAnalyze_Data)
        tools_menu.addAction(mw.actionGenerate_Report)
        tools_menu.addAction(mw.actionBatch_Processing)
        tools_menu.addSeparator()
        tools_menu.addAction(mw.actionConfiguration)

        # 帮助菜单
        help_menu = menubar.addMenu(_("Help"))
        help_menu.addAction(mw.actionUser_Mannual)
        help_menu.addAction(mw.actionOnline_Help)
        help_menu.addSeparator()
        help_menu.addAction(mw.actionAbout)
