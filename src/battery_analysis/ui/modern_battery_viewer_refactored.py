# -*- coding: utf-8 -*-
"""
现代化电池图表查看器 - 重构版本

使用外部样式文件，遵循更好的UI架构设计
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QMenuBar, QStatusBar, QToolBar, QTabWidget,
                           QSplitter, QFrame, QLabel, QPushButton, QComboBox,
                           QCheckBox, QSpinBox, QGroupBox, QTextEdit, QFileDialog,
                           QMessageBox, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QKeySequence, QAction as QGuiAction

import matplotlib.pyplot as plt
import numpy as np

from ..ui.modern_theme import modern_theme, ModernColorScheme
from ..ui.modern_chart_widget import ModernChartWidget
from ..ui.styles import style_manager, create_styled_button, create_styled_groupbox
from .battery_chart_viewer import BatteryChartViewer


class ModernBatteryViewerRefactored(QMainWindow):
    """现代化电池图表查看器主窗口 - 重构版本"""
    
    # 信号定义
    data_loaded = pyqtSignal(str)  # 数据加载完成信号
    visualization_changed = pyqtSignal(str)  # 可视化变化信号
    
    def __init__(self, data_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.colors = ModernColorScheme()
        self.data_path = data_path
        self.current_viewer = None
        self.chart_widget = None
        
        # 数据存储
        self.raw_data = {}
        self.processed_data = {}
        self.battery_names = []
        
        # UI组件
        self.tabs = None
        self.chart_area = None
        self.control_panel = None
        self.data_info_panel = None
        
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbars()
        self._setup_statusbar()
        self._connect_signals()
        
        # 应用现代化样式
        self._apply_styles()
        
        # 如果提供了数据路径，自动加载
        if self.data_path and os.path.exists(self.data_path):
            QTimer.singleShot(100, lambda: self.load_data(self.data_path))
    
    def _setup_ui(self):
        """设置用户界面"""
        
        # 设置主窗口属性
        self.setWindowTitle("现代化电池数据分析工具 v3.0 - 重构版")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧控制面板
        self._create_control_panel(splitter)
        
        # 右侧图表区域
        self._create_chart_area(splitter)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)  # 控制面板
        splitter.setStretchFactor(1, 3)  # 图表区域
    
    def _create_control_panel(self, parent):
        """创建左侧控制面板"""
        
        control_frame = QFrame()
        control_frame.setObjectName("control_frame")
        control_frame.setMaximumWidth(350)
        control_frame.setMinimumWidth(300)
        
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(12)
        
        # 数据加载控制
        self._create_data_control_group(control_layout)
        
        # 图表显示控制
        self._create_display_control_group(control_layout)
        
        # 数据处理控制
        self._create_processing_control_group(control_layout)
        
        # 数据信息面板
        self._create_data_info_panel(control_layout)
        
        # 添加弹簧
        control_layout.addStretch()
        
        parent.addWidget(control_frame)
    
    def _create_data_control_group(self, parent):
        """创建数据控制组"""
        
        # 使用样式管理器创建主题化分组框
        group = create_styled_groupbox(self, "📁 数据管理", "data")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        # 数据路径选择
        path_layout = QHBoxLayout()
        
        self.path_label = QLabel("数据路径:")
        self.path_label.setProperty("data-type", "title")
        
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.setMinimumWidth(150)
        
        self.browse_button = QPushButton("浏览")
        self.browse_button.setMaximumWidth(60)
        self.browse_button.clicked.connect(self._browse_data_path)
        
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_combo)
        path_layout.addWidget(self.browse_button)
        
        # 加载按钮 - 使用样式管理器创建
        self.load_button = create_styled_button(
            self, 
            "📂 加载数据", 
            "load", 
            self.load_data,
            min_height=40
        )
        
        # 添加到布局
        layout.addLayout(path_layout)
        layout.addWidget(self.load_button)
        
        parent.addWidget(group)
    
    def _create_display_control_group(self, parent):
        """创建显示控制组"""
        
        # 使用样式管理器创建主题化分组框
        group = create_styled_groupbox(self, "🎨 显示控制", "display")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # 图表类型
        chart_type_layout = QHBoxLayout()
        
        chart_type_label = QLabel("图表类型:")
        chart_type_label.setProperty("data-type", "normal")
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["折线图", "散点图", "面积图", "对比图"])
        self.chart_type_combo.currentTextChanged.connect(self._on_chart_type_changed)
        
        chart_type_layout.addWidget(chart_type_label)
        chart_type_layout.addWidget(self.chart_type_combo)
        
        # 显示选项
        self.show_filtered_checkbox = QCheckBox("显示过滤数据")
        self.show_filtered_checkbox.setChecked(True)
        self.show_filtered_checkbox.stateChanged.connect(self._on_display_option_changed)
        
        self.show_raw_checkbox = QCheckBox("显示原始数据")
        self.show_raw_checkbox.setChecked(False)
        self.show_raw_checkbox.stateChanged.connect(self._on_display_option_changed)
        
        self.show_grid_checkbox = QCheckBox("显示网格")
        self.show_grid_checkbox.setChecked(True)
        self.show_grid_checkbox.stateChanged.connect(self._on_display_option_changed)
        
        self.show_legend_checkbox = QCheckBox("显示图例")
        self.show_legend_checkbox.setChecked(True)
        self.show_legend_checkbox.stateChanged.connect(self._on_display_option_changed)
        
        # 电池选择
        battery_layout = QHBoxLayout()
        
        battery_label = QLabel("电池选择:")
        battery_label.setProperty("data-type", "normal")
        
        self.battery_filter_combo = QComboBox()
        self.battery_filter_combo.setEditable(True)
        self.battery_filter_combo.currentTextChanged.connect(self._on_battery_filter_changed)
        
        battery_layout.addWidget(battery_label)
        battery_layout.addWidget(self.battery_filter_combo)
        
        # 添加到布局
        layout.addLayout(chart_type_layout)
        layout.addWidget(self.show_filtered_checkbox)
        layout.addWidget(self.show_raw_checkbox)
        layout.addWidget(self.show_grid_checkbox)
        layout.addWidget(self.show_legend_checkbox)
        layout.addLayout(battery_layout)
        
        parent.addWidget(group)
    
    def _create_processing_control_group(self, parent):
        """创建数据处理控制组"""
        
        # 使用样式管理器创建主题化分组框
        group = create_styled_groupbox(self, "⚙️ 数据处理", "processing")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # 过滤参数
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel("过滤强度:")
        filter_label.setProperty("data-type", "normal")
        
        self.filter_strength_spinbox = QSpinBox()
        self.filter_strength_spinbox.setRange(1, 10)
        self.filter_strength_spinbox.setValue(3)
        self.filter_strength_spinbox.valueChanged.connect(self._on_filter_parameter_changed)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_strength_spinbox)
        
        # 采样间隔
        sampling_layout = QHBoxLayout()
        
        sampling_label = QLabel("采样间隔:")
        sampling_label.setProperty("data-type", "normal")
        
        self.sampling_spinbox = QSpinBox()
        self.sampling_spinbox.setRange(1, 100)
        self.sampling_spinbox.setValue(5)
        self.sampling_spinbox.setSuffix(" ms")
        self.sampling_spinbox.valueChanged.connect(self._on_filter_parameter_changed)
        
        sampling_layout.addWidget(sampling_label)
        sampling_layout.addWidget(self.sampling_spinbox)
        
        # 应用按钮 - 使用样式管理器创建
        self.apply_button = create_styled_button(
            self,
            "⚡ 应用处理",
            "apply",
            self._apply_processing,
            min_height=36
        )
        
        # 添加到布局
        layout.addLayout(filter_layout)
        layout.addLayout(sampling_layout)
        layout.addWidget(self.apply_button)
        
        parent.addWidget(group)
    
    def _create_data_info_panel(self, parent):
        """创建数据信息面板"""
        
        # 使用样式管理器创建主题化分组框
        group = create_styled_groupbox(self, "📊 数据信息", "info")
        layout = QVBoxLayout(group)
        
        # 数据状态
        self.data_status_label = QLabel("未加载数据")
        self.data_status_label.setProperty("data-type", "status")
        
        # 详细信息
        self.data_details_text = QTextEdit()
        self.data_details_text.setMaximumHeight(150)
        self.data_details_text.setReadOnly(True)
        self.data_details_text.setProperty("data-style", "info")
        
        # 统计信息
        self.stats_label = QLabel("统计信息: 暂无")
        self.stats_label.setProperty("data-type", "normal")
        
        # 添加到布局
        layout.addWidget(self.data_status_label)
        layout.addWidget(self.data_details_text)
        layout.addWidget(self.stats_label)
        
        parent.addWidget(group)
    
    def _create_chart_area(self, parent):
        """创建右侧图表区域"""
        
        chart_frame = QFrame()
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(5, 5, 5, 5)
        
        # 标签页控件
        self.tabs = QTabWidget()
        
        # 图表标签页
        self.chart_widget = ModernChartWidget()
        self.chart_widget.data_changed.connect(self._on_chart_data_changed)
        self.tabs.addTab(self.chart_widget, "📊 数据图表")
        
        # 分析标签页
        analysis_widget = self._create_analysis_widget()
        self.tabs.addTab(analysis_widget, "📈 数据分析")
        
        chart_layout.addWidget(self.tabs)
        
        parent.addWidget(chart_frame)
    
    def _create_analysis_widget(self):
        """创建分析面板"""
        
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)
        
        # 分析控制
        analysis_control_layout = QHBoxLayout()
        
        analysis_type_label = QLabel("分析类型:")
        analysis_type_label.setProperty("data-type", "normal")
        
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["趋势分析", "相关性分析", "异常检测", "统计摘要"])
        
        # 分析按钮 - 使用样式管理器创建
        self.run_analysis_button = create_styled_button(
            self,
            "🔍 运行分析",
            "analyze",
            self._run_analysis,
            min_height=36
        )
        
        analysis_control_layout.addWidget(analysis_type_label)
        analysis_control_layout.addWidget(self.analysis_type_combo)
        analysis_control_layout.addWidget(self.run_analysis_button)
        
        # 分析结果
        self.analysis_result_text = QTextEdit()
        self.analysis_result_text.setReadOnly(True)
        
        layout.addLayout(analysis_control_layout)
        layout.addWidget(self.analysis_result_text)
        
        return analysis_widget
    
    def _setup_menus(self):
        """设置菜单栏"""
        
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        open_action = QGuiAction('打开数据(&O)', self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._browse_data_path)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        export_action = QGuiAction('导出图表(&E)', self)
        export_action.setShortcut(QKeySequence.StandardKey.Save)
        export_action.triggered.connect(self._export_chart)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QGuiAction('退出(&X)', self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')
        
        refresh_action = QGuiAction('刷新(&R)', self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self._refresh_view)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QGuiAction('全屏(&F)', self)
        fullscreen_action.setShortcut(QKeySequence.StandardKey.FullScreen)
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        about_action = QGuiAction('关于(&A)', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbars(self):
        """设置工具栏"""
        
        # 主工具栏
        main_toolbar = self.addToolBar('主工具栏')
        main_toolbar.setMovable(False)
        
        # 打开数据按钮
        open_tool_action = QGuiAction('📁', self)
        open_tool_action.setToolTip('打开数据文件')
        open_tool_action.triggered.connect(self._browse_data_path)
        main_toolbar.addAction(open_tool_action)
        
        # 刷新按钮
        refresh_tool_action = QGuiAction('🔄', self)
        refresh_tool_action.setToolTip('刷新图表')
        refresh_tool_action.triggered.connect(self._refresh_view)
        main_toolbar.addAction(refresh_tool_action)
        
        main_toolbar.addSeparator()
        
        # 导出按钮
        export_tool_action = QGuiAction('💾', self)
        export_tool_action.setToolTip('导出图表')
        export_tool_action.triggered.connect(self._export_chart)
        main_toolbar.addAction(export_tool_action)
    
    def _setup_statusbar(self):
        """设置状态栏"""
        
        self.statusBar().showMessage('就绪')
        
        # 添加状态指示器
        self.data_status_indicator = QLabel("未加载数据")
        self.statusBar().addPermanentWidget(self.data_status_indicator)
        
        # 添加进度条（隐藏状态）
        self.progress_label = QLabel()
        self.statusBar().addPermanentWidget(self.progress_label)
    
    def _connect_signals(self):
        """连接信号和槽"""
        
        if self.chart_widget:
            self.chart_widget.data_changed.connect(self._on_chart_data_changed)
    
    def _apply_styles(self):
        """应用现代化样式"""
        
        # 使用样式管理器应用全局样式
        app = QApplication.instance()
        if app:
            style_manager.apply_global_style(app, "modern")
    
    # 槽函数实现
    
    @pyqtSlot()
    def _browse_data_path(self):
        """浏览数据路径"""
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择数据目录",
            self.path_combo.currentText() or ".",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.path_combo.setCurrentText(directory)
    
    @pyqtSlot()
    def load_data(self, data_path: Optional[str] = None):
        """加载数据"""
        
        if data_path is None:
            data_path = self.path_combo.currentText()
        
        if not data_path or not os.path.exists(data_path):
            QMessageBox.warning(self, "警告", "请选择有效的数据路径")
            return
        
        try:
            self.statusBar().showMessage('正在加载数据...')
            
            # 这里实现数据加载逻辑
            # 目前作为示例，只更新状态
            self.data_status_label.setText("数据已加载")
            self.data_status_indicator.setText("已加载")
            
            # 更新详细信息
            info_text = f"数据路径: {data_path}\n加载状态: 成功\n电池数量: 0"
            self.data_details_text.setPlainText(info_text)
            
            self.statusBar().showMessage('数据加载完成')
            
            # 发射信号
            self.data_loaded.emit(data_path)
            
        except Exception as e:
            logging.error("加载数据失败: %s", e)
            QMessageBox.critical(self, "错误", f"加载数据失败: {str(e)}")
            self.statusBar().showMessage('数据加载失败')
    
    @pyqtSlot(str)
    def _on_chart_type_changed(self, chart_type: str):
        """图表类型改变处理"""
        self.visualization_changed.emit(chart_type)
    
    @pyqtSlot(int)
    def _on_display_option_changed(self, state):
        """显示选项改变处理"""
        self.visualization_changed.emit("display_options_changed")
    
    @pyqtSlot(str)
    def _on_battery_filter_changed(self, battery_name: str):
        """电池过滤改变处理"""
        self.visualization_changed.emit("battery_filter_changed")
    
    @pyqtSlot(int)
    def _on_filter_parameter_changed(self, value):
        """过滤参数改变处理"""
        self.visualization_changed.emit("filter_parameters_changed")
    
    @pyqtSlot()
    def _apply_processing(self):
        """应用数据处理"""
        # 这里实现数据处理逻辑
        self.statusBar().showMessage('正在处理数据...')
        QTimer.singleShot(1000, lambda: self.statusBar().showMessage('处理完成'))
    
    @pyqtSlot()
    def _run_analysis(self):
        """运行数据分析"""
        analysis_type = self.analysis_type_combo.currentText()
        result_text = f"分析类型: {analysis_type}\n分析结果: 数据处理完成\n建议: 继续监控电池状态"
        self.analysis_result_text.setPlainText(result_text)
    
    @pyqtSlot()
    def _export_chart(self):
        """导出图表"""
        QMessageBox.information(self, "提示", "图表导出功能开发中...")
    
    @pyqtSlot()
    def _refresh_view(self):
        """刷新视图"""
        if self.chart_widget:
            self.chart_widget.refresh()
        self.statusBar().showMessage('视图已刷新')
    
    @pyqtSlot()
    def _toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    @pyqtSlot()
    def _show_about(self):
        """显示关于信息"""
        QMessageBox.about(self, "关于", 
                         "现代化电池数据分析工具 v3.0\n\n"
                         "使用PyQt6 + Matplotlib构建\n"
                         "提供现代化的用户界面和数据分析功能")
    
    @pyqtSlot(object)
    def _on_chart_data_changed(self, data):
        """图表数据改变处理"""
        self.visualization_changed.emit("chart_data_changed")


# 便捷创建函数
def create_modern_viewer_refactored(data_path: Optional[str] = None) -> ModernBatteryViewerRefactored:
    """创建现代化查看器实例"""
    return ModernBatteryViewerRefactored(data_path)


def demo_refactored_ui():
    """演示重构版现代化UI"""
    
    print("=== 重构版现代化电池数据分析工具 UI演示 ===")
    print()
    
    # 创建应用程序
    print("1. 创建Qt应用程序...")
    app = QApplication(sys.argv)
    print("   ✓ Qt应用程序已创建")
    
    # 创建现代化查看器
    print("2. 创建重构版现代化查看器...")
    try:
        viewer = create_modern_viewer_refactored()
        print("   ✓ 重构版现代化查看器已创建")
        
        # 显示窗口
        print("3. 显示现代化界面...")
        viewer.show()
        print("   ✓ 界面已显示")
        
        # 运行应用程序
        print("4. 运行应用程序...")
        print("   📱 界面特点:")
        print("      • 使用外部QSS样式文件")
        print("      • 样式与业务逻辑分离")
        print("      • 支持主题切换")
        print("      • 更易维护和扩展")
        print()
        
        return app.exec()
        
    except Exception as e:
        print(f"   ❌ 创建查看器失败: {e}")
        return 1


if __name__ == "__main__":
    demo_refactored_ui()
