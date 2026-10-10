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
import sys

# 第三方库导入
import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.main.window_actions import WindowActionsMixin
from battery_analysis.main.window_init import WindowInitMixin
from battery_analysis.main.window_texts import WindowTextsMixin


class Main(WindowInitMixin, WindowTextsMixin, WindowActionsMixin, QW.QMainWindow):
    """电池分析主窗口（骨架类）

    原 599 行大文件按职责拆分，本文件保留类头、__init__、信号声明
    以及模块级入口（_create_splash_screen / main）：
    - window_init    延迟初始化、组件获取、图标、环境信息、resizeEvent
    - window_texts   语言切换与 refresh_texts 文本刷新
    - window_actions 信号连接、偏好/配置动作、剪贴板、主题、状态栏

    注意：sigSetVersion 信号必须声明在 QMainWindow 子类上（Mixin 非 QObject）。
    """

    sigSetVersion = QC.pyqtSignal()

    def __init__(self, splash=None) -> None:
        super().__init__()

        # 初始化属性
        self._services = {}
        self._controllers = {}
        self._lazy_init_done = False
        self._resize_timer = None

        # 主题管理器（延迟初始化，但需要在 on_preferences_applied 前就绪）
        from battery_analysis.main.ui_components.theme_manager import ThemeManager

        self.theme_manager = ThemeManager(self)

        # 日志器在构造时即就绪，避免 on_preferences_applied 等方法的
        # except 分支在 _deferred_init 执行前访问 self.logger 时崩溃。
        # （_deferred_init 会再次赋值同一 logger，幂等无副作用）
        from battery_analysis.utils.log_manager import get_logger

        self.logger = get_logger("main_window")

        # 使用 UIBuilder 构建 UI（替代 Designer 生成的 setupUi）
        from battery_analysis.main.ui_builder import UIBuilder

        ui_builder = UIBuilder(self)
        ui_builder.build_ui()
        ui_builder.create_actions()
        ui_builder.create_menus()

        # 使用 Designer 默认尺寸显示窗口，不强制最大化
        self.show()

        # 关闭闪屏
        if splash:
            splash.finish(self)

        # 所有业务初始化延后到窗口显示后执行
        QC.QTimer.singleShot(0, self._deferred_init)


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
            QG.QColor("#ecf0f1"),
        )
        # 保留 processEvents()：同 launcher，启动期 splash 绘制（进入事件循环前）。
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


if __name__ == "__main__":
    # 这确保在multiprocessing子进程中不会执行UI初始化代码
    # 防止在Windows和PyInstaller环境下的递归启动问题
    import warnings as _warnings

    _warnings.filterwarnings("ignore", message=".*sipPyTypeDict.*")

    # 过滤 Qt 内部无害警告（QTableWidget auto-expand 时的 dataChanged 防护检查）
    _QT_FILTER_MSG = "dataChanged() called with an invalid index range"

    def _qt_msg_handler(mode, ctx, msg):
        if _QT_FILTER_MSG not in msg:
            sys.stderr.write(msg + "\n")

    from PyQt6.QtCore import qInstallMessageHandler

    qInstallMessageHandler(_qt_msg_handler)

    main()
