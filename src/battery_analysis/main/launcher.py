"""
应用启动器 - 最小化入口

仅在启动时才导入的轻量模块，负责在加载任何业务模块前尽早显示闪屏。
"""
import os
import sys
import multiprocessing
import warnings
from pathlib import Path

# 电池测试设备生成的 xlsx 文件通常不包含 openpyxl 默认样式，
# 每次读取都会触发 "Workbook contains no default style" 警告，这里统一静默
warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style",
    module="openpyxl.styles.stylesheet",
    category=UserWarning,
)

from PyQt6.QtWidgets import QApplication, QStyleFactory, QSplashScreen
from PyQt6.QtGui import QPixmap, QFont, QColor, QPainter
from PyQt6.QtCore import Qt, qInstallMessageHandler, QtMsgType


def _create_splash(app):
    """创建并显示启动闪屏（仅用PyQt6基类，不触发任何业务模块import）"""
    try:
        pixmap = QPixmap(480, 300)
        pixmap.fill(QColor("#2c3e50"))
        splash = QSplashScreen(pixmap)
        splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        splash.show()
        splash.showMessage(
            "Battery Analyzer",
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter,
            QColor("#ecf0f1"))
        splash.showMessage(
            "Loading...",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            QColor("white"))
        # 保留 processEvents()：启动时尚未进入事件循环，QSplashScreen 官方模式
        # 要求在此绘制 splash。roadmap #12 移除的是 progress_dialog/theme_manager/
        # battery_chart_viewer 的防重入调用，此处移除会导致启动 splash 空白。
        app.processEvents()
        return splash
    except Exception:
        return None


def main():
    """应用入口点 — 尽早显示闪屏，再加载业务模块"""
    multiprocessing.freeze_support()
    warnings.filterwarnings("ignore", message=".*sipPyTypeDict.*")

    # 禁用 Qt 可访问性桥（解决特定 Windows 机器上下拉框无响应的问题）
    os.environ["QT_ACCESSIBILITY"] = "0"

    # 1) 创建 QApplication 和闪屏（只依赖 PyQt6 基础库）
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))

    # 过滤 Qt 内部无害警告（QTableWidget auto-expand 时的 dataChanged 防护检查）
    _QT_FILTER_MSG = "dataChanged() called with an invalid index range"
    def _qt_msg_handler(mode, ctx, msg):
        if _QT_FILTER_MSG not in msg:
            sys.stderr.write(msg + "\n")
    qInstallMessageHandler(_qt_msg_handler)

    font = QFont()
    font.setFamilies(["Segoe UI", "Segoe UI Emoji", "SimHei", "Microsoft YaHei"])
    app.setFont(font)

    splash = _create_splash(app)

    # 2) 导入主窗口模块（此时闪屏已在屏幕上，用户看到反馈）
    from battery_analysis.main.main_window import main as main_window_main

    # 3) 委托给主窗口的 main()，传递已创建的 app 和闪屏
    main_window_main(app=app, splash=splash)


if __name__ == '__main__':
    main()
