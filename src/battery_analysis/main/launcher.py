"""
应用启动器 - 最小化入口

仅在启动时才导入的轻量模块，负责在加载任何业务模块前尽早显示闪屏。
"""
import sys
import multiprocessing
import warnings
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QStyleFactory, QSplashScreen
from PyQt6.QtGui import QPixmap, QFont, QColor, QPainter
from PyQt6.QtCore import Qt


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
        app.processEvents()
        return splash
    except Exception:
        return None


def main():
    """应用入口点 — 尽早显示闪屏，再加载业务模块"""
    multiprocessing.freeze_support()
    warnings.filterwarnings("ignore", message=".*sipPyTypeDict.*")

    # 1) 创建 QApplication 和闪屏（只依赖 PyQt6 基础库）
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
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
