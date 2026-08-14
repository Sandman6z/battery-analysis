"""
电池分析主窗口模块

这个模块实现了电池分析应用的主窗口界面和核心功能，包括：
- 窗口初始化和布局设置
- 配置文件管理
- 控制器连接和信号处理
- 用户交互界面
"""

# 标准库导入
import logging
import multiprocessing
import os
import sys
import time
from pathlib import Path
from typing import Any

# 第三方库导入
import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.ui import ui_main_window


class Main(QW.QMainWindow, ui_main_window.Ui_MainWindow):
    sigSetVersion = QC.pyqtSignal()

    def __init__(self, splash=None) -> None:
        super().__init__()

        # 初始化属性
        self._services = {}
        self._controllers = {}
        self._lazy_init_done = False

        # 仅构建 UI 骨架（Qt 控件树 + 布局），不填充数据
        self.setupUi(self)

        # 将绝对定位转换为响应式布局（适配不同屏幕尺寸）
        self._apply_responsive_layout()

        # 使用 Designer 默认尺寸显示窗口，不强制最大化
        self.show()

        # 关闭闪屏
        if splash:
            splash.finish(self)

        # 所有业务初始化延后到窗口显示后执行
        QC.QTimer.singleShot(0, self._deferred_init)

    def _apply_responsive_layout(self) -> None:
        """
        将 setupUi 设置的绝对定位替换为响应式布局。
        窗口大小改变时，各面板按比例自适应，支持不同屏幕尺寸和 DPI。

        做法：保留 existing centralwidget（setupUi 已通过 setCentralWidget 注册），
        直接在上面设布局 + 加子控件，避免 setCentralWidget 的 C++ 对象删除问题。
        """
        # 1) 左侧内容（4 个 group box）放到可滚动区域
        left_content = QW.QWidget()
        left_layout = QW.QVBoxLayout(left_content)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)

        for w in (self.groupBox_TestConfig, self.groupBox_Path,
                  self.groupBox_BatteryConfig, self.groupBox_TestInformation):
            w.setParent(left_content)
            left_layout.addWidget(w)

        # 2) 最小高度（压缩到刚好能看清的程度）
        self.groupBox_TestConfig.setMinimumHeight(110)
        self.groupBox_Path.setMinimumHeight(110)
        self.groupBox_BatteryConfig.setMinimumHeight(341)
        self.groupBox_TestInformation.setMinimumHeight(131)

        # 3) 大小策略
        self.groupBox_TestConfig.setSizePolicy(
            QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        self.groupBox_Path.setSizePolicy(
            QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        self.groupBox_BatteryConfig.setSizePolicy(
            QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Expanding)
        self.groupBox_TestInformation.setSizePolicy(
            QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Expanding)
        # 给 TestInformation 设布局替换 setGeometry，让内部 scrollArea/table 随宽度自适应
        info_lo = QW.QVBoxLayout(self.groupBox_TestInformation)
        info_lo.setContentsMargins(5, 15, 5, 5)
        info_lo.setSpacing(0)
        info_lo.addWidget(self.scrollArea)

        left_content.setMinimumSize(left_layout.minimumSize())

        # 4) 可滚动区域（只包左边内容，右侧 Run 按钮固定不滚动）
        left_scroll = QW.QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QW.QFrame.Shape.NoFrame)
        left_scroll.setWidget(left_content)

        # 5) 直接用 existing centralwidget（setupUi 已注册好），在其上设水平布局
        # 注意：group box 已被 reparent 到 left_content，frame_RunButton 还在 old centralwidget 下
        old_layout = self.centralwidget.layout()
        if old_layout:
            # 清除旧 layout（如果有），避免干扰
            dummy = QW.QWidget()
            dummy.setLayout(old_layout)
            dummy.deleteLater()

        layout = QW.QHBoxLayout(self.centralwidget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        layout.addWidget(left_scroll)
        layout.addWidget(self.frame_RunButton)
        layout.setStretch(0, 661)
        layout.setStretch(1, 231)

        # 6) 右侧面板不垂直拉伸，固定最小尺寸（原始 setGeometry 的尺寸）
        self.frame_RunButton.setSizePolicy(
            QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Preferred)
        self.frame_RunButton.setMinimumSize(231, 301)

        # 7) 窗口显示后调整大小并居中
        QC.QTimer.singleShot(0, self._adjust_window_size)

    def _adjust_window_size(self) -> None:
        """调整窗口：最小完整显示，不超出屏幕，自动居中

        参考尺寸足够展示所有内容，不最大化/全屏。
        小屏幕自动缩放到可用空间，QScrollArea 自动出现滚动条。
        """
        screen = QW.QApplication.primaryScreen().availableGeometry()

        ref_w = 920
        ref_h = 750

        w = max(min(ref_w, screen.width()), 800)
        h = max(min(ref_h, screen.height()), 600)

        self.resize(w, h)

        # 居中，确保窗口不超出屏幕顶部/左侧
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        if frame.top() < screen.top():
            frame.moveTop(screen.top())
        if frame.left() < screen.left():
            frame.moveLeft(screen.left())
        self.move(frame.topLeft())

    def _deferred_init(self):
        """窗口显示后执行的全部初始化 — 不再阻塞启动

        4 阶段流程：
          环境准备 → 核心服务 → UI 构建 → 启动完成
        """
        t0 = time.time()
        try:
            # ── 前置准备（日志、异常钩子）────────────────────
            from battery_analysis.utils.log_manager import get_logger
            self.logger = get_logger('main_window')

            from battery_analysis.main.application_initializer import ApplicationInitializer
            initializer = ApplicationInitializer()
            if not initializer.initialize():
                self.logger.error("Application initialization failed; some features may be unavailable")
                return

            # ── 阶段 1-3: 初始化管线 ───────────────────────
            # 环境准备 → 核心服务 → UI 构建
            from battery_analysis.main.managers.initialization_manager import (
                InitializationManager,
                PHASE_ENV_PREP,
                PHASE_CORE_SVC,
                PHASE_UI_BUILD,
                PHASE_LAUNCH,
            )
            self.logger.info("─" * 40)
            self.logger.info("Initialization pipeline: %s → %s → %s",
                           PHASE_ENV_PREP, PHASE_CORE_SVC, PHASE_UI_BUILD)
            init_manager = InitializationManager(self)
            init_manager.initialize()

            # ── 阶段 4: 启动完成 ────────────────────────────
            self.logger.info("")
            self.logger.info("▶ Phase [%s]", PHASE_LAUNCH)

            # 4a) UI 后处理（窗口属性、控件填充）
            self.init_window()
            self.init_widget()
            if hasattr(self, 'tableWidget_TestInformation'):
                self.tableWidget_TestInformation.resizeColumnsToContents()

            # 4b) 版本号
            self.get_version()

            # 4c) 非关键 UI 辅助功能／工具提示
            self._lazy_init()

            # 4d) 环境日志（包含 psutil/platform 调用，UI 已可见）
            try:
                from battery_analysis.utils.log_manager import get_log_manager
                lm = get_log_manager()
                if lm:
                    lm.log_environment_info()
            except Exception:
                pass

            self.logger.info("  Phase [%s] completed ✓", PHASE_LAUNCH)

            elapsed = (time.time() - t0) * 1000
            self.logger.info("Background initialization completed in %dms", elapsed)
        except Exception as e:
            logging.getLogger(__name__).error("Background initialization error: %s", e)

    # ------------------------------
    # 服务和控制器获取方法
    # ------------------------------
    def _get_component(self, component_name, component_type="service"):
        cache_dict = self._services if component_type == "service" else self._controllers
        if component_name not in cache_dict:
            try:
                cache_dict[component_name] = self._service_container.get(component_name)
            except Exception as e:
                self.logger.warning("Failed to get %s %s: %s", component_type, component_name, e)
                cache_dict[component_name] = None
        return cache_dict[component_name]

    def _get_service(self, service_name):
        return self._get_component(service_name, "service")

    def _get_controller(self, controller_name):
        return self._get_component(controller_name, "controller")

    # ------------------------------
    # 配置相关方法
    # ------------------------------
    def get_config(self, config_key):
        return self.config_manager.get_config(config_key)

    def init_window(self) -> None:
        self.ui_manager.init_window()

    # ------------------------------
    # 窗口和UI管理方法
    # ------------------------------
    def _load_application_icon(self) -> QG.QIcon:
        logger = getattr(self, 'logger', logging.getLogger(__name__))
        try:
            from battery_analysis.main.utils import FileUtils
            from battery_analysis.i18n.language_manager import _
            env_detector = getattr(self, 'env_detector', None)
            icon_paths = FileUtils.get_icon_paths(env_detector, getattr(self, 'current_directory', None))
            for icon_path in icon_paths:
                if icon_path.exists():
                    return QG.QIcon(str(icon_path))
            logger.warning(_("App icon not found; using default icon."))
            return QG.QIcon()
        except (OSError, TypeError, ValueError, RuntimeError, ImportError) as e:
            logger.error("Failed to load application icon: %s", e)
            return QG.QIcon()

    # ------------------------------
    # 语言相关方法
    # ------------------------------
    def _on_language_changed(self, language_code):
        from battery_analysis.i18n.language_manager import _
        self.setWindowTitle(f"Battery Analyzer v{self.version}")
        self._update_ui_texts()
        self._update_statusbar_messages()
        self._refresh_dialogs()
        logging.info("Interface language switched to: %s", language_code)

    def _update_ui_texts(self):
        from battery_analysis.i18n.language_manager import _
        if hasattr(self, 'signal_connector') and self.signal_connector.progress_dialog:
            self.signal_connector.progress_dialog.setWindowTitle(
                _("Battery Analysis Progress"))
            self.signal_connector.progress_dialog.status_label.setText(
                _("Ready to start analysis..."))

    def _update_statusbar_messages(self):
        self.menu_manager.update_statusbar_messages()

    def _refresh_dialogs(self):
        pass

    def init_widget(self) -> None:
        self.ui_manager.init_widget()
        self.pushButton_Run.setFocus()

    def connect_widget(self) -> None:
        self.ui_manager.connect_widget()
        self.pushButton_Run.clicked.connect(self.run)
        self.sigSetVersion.connect(self.get_version)
        self.menu_manager.connect_menu_actions()
        self.setup_menu_shortcuts()

    # ------------------------------
    # 用户交互方法
    # ------------------------------
    def handle_exit(self) -> None:
        self.dialog_manager.handle_exit()

    def handle_about(self) -> None:
        self.dialog_manager.handle_about()

    def show_preferences(self) -> None:
        self.dialog_manager.show_preferences()

    def on_preferences_applied(self) -> None:
        try:
            # 配置路径/重载统一经 ConfigService；仅需丢弃 config_utils 的路径缓存，
            # 让 ConfigService 重新解析（含 QSettings 里的自定义路径）
            from battery_analysis.utils.config_utils import clear_config_cache
            clear_config_cache()
            svc = self._get_service("config")
            if svc is not None:
                svc.reload_config()
            if hasattr(self, 'config_manager'):
                self.config_manager.reload_config()
            if hasattr(self, 'ui_manager'):
                self.ui_manager.init_combobox()
            self.refresh_ui()
        except Exception as e:
            self.logger.error("Preferences apply post-processing failed: %s", e)

    def reload_configuration(self) -> None:
        try:
            from battery_analysis.utils.config_utils import clear_config_cache
            clear_config_cache()
            svc = self._get_service("config")
            if svc is not None:
                svc.reload_config()
            if hasattr(self, 'config_manager'):
                self.config_manager.reload_config()
            if hasattr(self, 'ui_manager'):
                self.ui_manager.init_combobox()
            self.refresh_ui()
        except Exception as e:
            self.logger.error("Failed to reload configuration: %s", e)
            if hasattr(self, 'statusBar_BatteryAnalysis'):
                self.statusBar_BatteryAnalysis.showMessage(f"Configuration reload failed: {str(e)}")

    def refresh_ui(self) -> None:
        try:
            if hasattr(self, 'statusBar_BatteryAnalysis'):
                self.statusBar_BatteryAnalysis.showMessage("Configuration reloaded successfully")
            if hasattr(self, 'comboBox_Specification_Type'):
                current_text = self.comboBox_Specification_Type.currentText()
                if current_text:
                    index = self.comboBox_Specification_Type.findText(current_text)
                    if index >= 0:
                        self.comboBox_Specification_Type.setCurrentIndex(index)
        except Exception as e:
            self.logger.error("Error refreshing UI: %s", e)

    def toggle_toolbar_safe(self) -> None:
        self.menu_manager.toggle_toolbar_safe()

    def toggle_statusbar_safe(self) -> None:
        self.menu_manager.toggle_statusbar_safe()

    def setup_menu_shortcuts(self) -> None:
        self.menu_manager.setup_menu_shortcuts()

    def show_user_manual(self) -> None:
        self.help_manager.show_user_manual()

    def show_online_help(self) -> None:
        self.dialog_manager.show_online_help()

    def copy_selected_text(self) -> None:
        w = self.focusWidget()
        if isinstance(w, (QW.QLineEdit, QW.QTextEdit)):
            w.copy()

    def paste_text(self) -> None:
        w = self.focusWidget()
        if isinstance(w, (QW.QLineEdit, QW.QTextEdit)):
            w.paste()

    def cut_selected_text(self) -> None:
        w = self.focusWidget()
        if isinstance(w, (QW.QLineEdit, QW.QTextEdit)):
            w.cut()

    # ------------------------------
    # 电池分析功能方法
    # ------------------------------
    def calculate_battery(self) -> None:
        self.calculate_battery_command.execute()

    def analyze_data(self) -> None:
        self.analyze_data_command.execute()

    def generate_report(self) -> None:
        self.generate_report_command.execute()

    # ------------------------------
    # 环境和信息管理方法
    # ------------------------------
    def _initialize_environment_info(self):
        self.environment_manager.initialize_environment_info()

    def _ensure_env_info_keys(self):
        self.environment_manager.ensure_env_info_keys()

    # ------------------------------
    # 可视化相关方法
    # ------------------------------
    def run_visualizer(self, xml_path=None) -> None:
        self.visualization_manager.run_visualizer(xml_path)

    def show_visualizer_error(self, error_msg: str):
        self.visualization_manager.show_visualizer_error(error_msg)

    def batch_processing(self) -> None:
        self.batch_processing_command.execute()

    def show_config_dialog(self):
        saved = {
            "BatteryType": self.comboBox_BatteryType.currentText(),
            "Manufacturer": self.comboBox_Manufacturer.currentText(),
            "TesterLocation": self.comboBox_TesterLocation.currentText(),
            "TestedBy": self.comboBox_TestedBy.currentText(),
            "ReportedBy": self.comboBox_ReportedBy.currentText(),
        }
        from battery_analysis.main.ui_components.config_dialog import ConfigDialog
        dialog = ConfigDialog(self)
        if dialog.exec() == QW.QDialog.DialogCode.Accepted:
            self.statusBar_BatteryAnalysis.showMessage("Configuration saved")
            self.config_manager.reload_config()
            self.ui_manager.init_combobox()
            for name, text in saved.items():
                combo = getattr(self, f"comboBox_{name}")
                if text:
                    combo.setCurrentText(text)

    def save_settings(self) -> None:
        self.statusBar_BatteryAnalysis.showMessage("Settings saved")

    # ------------------------------
    # 报告相关方法
    # ------------------------------
    def export_report(self) -> None:
        self.export_report_command.execute()

    def set_theme(self, theme_name) -> None:
        self.theme_manager.set_theme(theme_name)

    def toggle_statusbar(self) -> None:
        self.menu_manager.toggle_statusbar()

    # ------------------------------
    # 验证相关方法
    # ------------------------------
    def validate_version(self) -> None:
        self.validation_manager.validate_version()

    def validate_input_path(self) -> None:
        self.validation_manager.validate_input_path()

    def validate_required_fields(self) -> None:
        self.validation_manager.validate_required_fields()

    def check_batterytype(self) -> None:
        self.validation_manager.check_batterytype()

    def check_specification(self) -> None:
        self.validation_manager.check_specification()

    # ------------------------------
    # 表格相关方法
    # ------------------------------
    def set_table(self) -> None:
        self.table_manager.set_table()

    # ------------------------------
    # 温度相关方法
    # ------------------------------
    def on_temperature_type_changed(self, index):
        self.temperature_handler.on_temperature_type_changed()

    def get_xlsxinfo(self) -> None:
        self.data_processor.get_xlsxinfo()

    def get_version(self) -> None:
        self.version_manager.get_version()

    def set_version(self) -> None:
        self.version_manager.set_version()

    # ------------------------------
    # 路径选择方法
    # ------------------------------
    def select_testprofile(self) -> None:
        self.test_profile_manager.select_testprofile()

    def select_inputpath(self) -> None:
        self.path_manager.select_inputpath()

    def select_outputpath(self) -> None:
        self.path_manager.select_outputpath()

    def run(self) -> None:
        self.run_analysis_command.execute()

    def save_table(self) -> None:
        self.table_manager.save_table()

    def init_widgetcolor(self) -> None:
        self.ui_manager.init_widgetcolor()

    def checkinput(self) -> bool:
        return self.validation_manager.checkinput()

    def _open_report(self, dialog=None):
        self.report_manager.open_report(dialog)

    def _open_report_path(self, dialog=None):
        self.report_manager.open_report_path(dialog)

    def _show_analysis_complete_dialog(self):
        self.report_manager.show_analysis_complete_dialog()

    def rename_pltPath(self, strTestDate):
        self.config_manager.rename_pltPath(strTestDate)

    def update_config(self, test_info) -> None:
        self.config_manager.update_config(test_info)

    def resizeEvent(self, event):
        """窗口大小改变时的事件处理函数"""
        super().resizeEvent(event)
        if hasattr(self, 'tableWidget_TestInformation'):
            if self.tableWidget_TestInformation.rowCount() > 0:
                self.tableWidget_TestInformation.resizeColumnsToContents()

    def _lazy_init(self):
        """延迟初始化非关键UI组件（窗口显示后执行）"""
        if self._lazy_init_done:
            return
        self._lazy_init_done = True
        try:
            t0 = time.time()
            # 可访问性设置和工具提示 — 不影响功能
            if hasattr(self, 'ui_manager'):
                self.ui_manager.setup_accessibility()
                self.ui_manager.setup_tooltips()
            self.logger.debug("Deferred initialization completed in %dms", (time.time() - t0) * 1000)
        except Exception as e:
            self.logger.warning("Deferred initialization failed: %s", e)


def _create_splash_screen(app):
    """创建启动闪屏"""
    try:
        splash_pixmap = QG.QPixmap(480, 300)
        splash_pixmap.fill(QG.QColor("#2c3e50"))
        splash = QW.QSplashScreen(splash_pixmap)
        splash.setWindowFlags(QC.Qt.WindowType.WindowStaysOnTopHint)
        splash.show()

        # 绘制标题文字
        from battery_analysis import __version__
        splash.showMessage(
            f"Battery Analyzer v{__version__}",
            QC.Qt.AlignmentFlag.AlignTop | QC.Qt.AlignmentFlag.AlignCenter,
            QG.QColor("#ecf0f1"))
        app.processEvents()

        return splash
    except Exception as e:
        logging.getLogger(__name__).warning("Failed to create splash screen: %s", e)
        return None


def main(app=None, splash=None) -> None:
    # 解决PyInstaller打包后multiprocessing导致的递归启动问题
    multiprocessing.freeze_support()
    # 如果未传入 app（从 launcher 调用时已有），创建 QApplication
    if app is None:
        app = QW.QApplication(sys.argv)
        app.setStyle(QW.QStyleFactory.create("Fusion"))
        font = QG.QFont()
        font.setFamilies(["Segoe UI", "Segoe UI Emoji", "SimHei", "Microsoft YaHei"])
        app.setFont(font)

    # 如果未传入闪屏，创建闪屏
    if splash is None:
        splash = _create_splash_screen(app)

    # 创建主窗口（内部根据屏幕尺寸自动居中或最大化）
    window = Main(splash=splash)
    window.setMinimumSize(800, 600)

    # 运行应用程序事件循环
    try:
        result = app.exec()
    except Exception as e:
        logging.getLogger(__name__).critical("Event loop error: %s", e)
        result = 1

    sys.exit(result)


if __name__ == '__main__':
    # 这确保在multiprocessing子进程中不会执行UI初始化代码
    # 防止在Windows和PyInstaller环境下的递归启动问题
    main()
