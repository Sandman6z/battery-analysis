#!/usr/bin/env python
"""
测试按钮美化功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QToolBar, QMenuBar, QMenu
from PyQt6.QtCore import Qt
from battery_analysis.ui.styles.style_manager import StyleManager, apply_modern_theme

def create_test_window():
    """创建测试窗口"""
    window = QMainWindow()
    window.setWindowTitle("按钮美化测试")
    window.setGeometry(100, 100, 800, 600)
    
    # 创建一个中央部件
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # 创建布局
    layout = QVBoxLayout(central_widget)
    
    # 添加菜单栏
    menubar = window.menuBar()
    file_menu = menubar.addMenu("文件")
    file_menu.addAction("新建")
    file_menu.addAction("打开")
    file_menu.addAction("保存")
    edit_menu = menubar.addMenu("编辑")
    edit_menu.addAction("复制")
    edit_menu.addAction("粘贴")
    view_menu = menubar.addMenu("视图")
    view_menu.addAction("缩放")
    view_menu.addAction("全屏")
    tools_menu = menubar.addMenu("工具")
    tools_menu.addAction("设置")
    tools_menu.addAction("导入")
    
    # 添加工具栏
    toolbar = QToolBar("主工具栏")
    window.addToolBar(toolbar)
    toolbar.addAction("新建")
    toolbar.addAction("打开")
    toolbar.addAction("保存")
    
    # 添加测试按钮
    button1 = QPushButton("普通按钮1")
    button2 = QPushButton("普通按钮2")
    button3 = QPushButton("普通按钮3")
    
    # 添加带动作的按钮
    load_button = QPushButton("加载数据")
    apply_button = QPushButton("应用处理")
    analyze_button = QPushButton("运行分析")
    
    # 设置属性
    load_button.setProperty("data-action", "load")
    apply_button.setProperty("data-action", "apply")
    analyze_button.setProperty("data-action", "analyze")
    
    layout.addWidget(button1)
    layout.addWidget(button2)
    layout.addWidget(button3)
    layout.addWidget(load_button)
    layout.addWidget(apply_button)
    layout.addWidget(analyze_button)
    
    return window

if __name__ == "__main__":
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 应用样式表
    try:
        from battery_analysis.ui.styles.style_manager import StyleManager, apply_modern_theme
        style_manager = StyleManager()
        style_manager.apply_global_style(app, "modern")
        print("已应用全局主题样式")
    except Exception as e:
        print(f"应用样式失败: {e}")
    
    # 创建测试窗口
    window = create_test_window()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())