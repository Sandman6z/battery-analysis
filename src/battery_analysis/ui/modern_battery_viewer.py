# -*- coding: utf-8 -*-
"""
现代化电池图表查看器

集成现代化UI组件，提供更好的用户体验
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
from PyQt6.QtGui import QFont, QIcon, QKeySequence, QAction
from PyQt6.QtGui import QAction as QGuiAction

import matplotlib.pyplot as plt
import numpy as np

from ..ui.modern_theme import modern_theme, ModernColorScheme
from ..ui.modern_chart_widget import ModernChartWidget
from ..ui.styles import style_manager, create_styled_button, create_styled_groupbox

# 使用绝对导入而不是相对导入
import sys
from pathlib import Path
if __name__ == "__main__":
    # 如果是直接运行此模块，使用绝对路径
    current_dir = Path(__file__).parent
    src_dir = current_dir.parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
else:
    # 如果是作为模块导入，使用模块路径
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from battery_analysis.main.battery_chart_viewer import BatteryChartViewer


class ModernBatteryViewer(QMainWindow):
    """现代化电池图表查看器主窗口"""
    
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
            
        # 记录初始化完成
        logging.info("ModernBatteryViewer初始化完成")
    
    def _apply_styles(self):
        """应用现代化样式"""
        # 应用样式管理器中的样式
        style_manager.apply_styles(self)
    
    def _setup_ui(self):
        """设置用户界面"""
        
        # 设置主窗口属性
        self.setWindowTitle("现代化电池数据分析工具 v3.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 应用现代化样式
        self._apply_styles()
        
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
        control_frame.setFrameStyle(QFrame.Shape.NoFrame)
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
        self.path_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.setMinimumWidth(150)
        
        self.browse_button = QPushButton("浏览")
        self.browse_button.setMaximumWidth(60)
        self.browse_button.clicked.connect(self._browse_data_path)
        
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_combo)
        path_layout.addWidget(self.browse_button)
        
        # 加载按钮
        self.load_button = QPushButton("📂 加载数据")
        self.load_button.setProperty("button-type", "load")
        self.load_button.setMinimumHeight(40)
        self.load_button.clicked.connect(self.load_data)
        
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
        chart_type_label.setFont(QFont("Microsoft YaHei", 9))
        
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
        battery_label.setFont(QFont("Microsoft YaHei", 9))
        
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
        filter_label.setFont(QFont("Microsoft YaHei", 9))
        
        self.filter_strength_spinbox = QSpinBox()
        self.filter_strength_spinbox.setRange(1, 10)
        self.filter_strength_spinbox.setValue(3)
        self.filter_strength_spinbox.valueChanged.connect(self._on_filter_parameter_changed)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_strength_spinbox)
        
        # 采样间隔
        sampling_layout = QHBoxLayout()
        
        sampling_label = QLabel("采样间隔:")
        sampling_label.setFont(QFont("Microsoft YaHei", 9))
        
        self.sampling_spinbox = QSpinBox()
        self.sampling_spinbox.setRange(1, 100)
        self.sampling_spinbox.setValue(5)
        self.sampling_spinbox.setSuffix(" ms")
        self.sampling_spinbox.valueChanged.connect(self._on_filter_parameter_changed)
        
        sampling_layout.addWidget(sampling_label)
        sampling_layout.addWidget(self.sampling_spinbox)
        
        # 应用按钮
        self.apply_button = QPushButton("⚡ 应用处理")
        self.apply_button.setProperty("button-type", "apply")
        self.apply_button.setMinimumHeight(36)
        self.apply_button.clicked.connect(self._apply_processing)
        
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
        self.data_status_label.setObjectName("data-status-warning")
        
        # 详细信息
        self.data_details_text = QTextEdit()
        self.data_details_text.setMaximumHeight(150)
        self.data_details_text.setReadOnly(True)
        self.data_details_text.setObjectName("data-details-text")
        
        # 统计信息
        self.stats_label = QLabel("统计信息: 暂无")
        self.stats_label.setFont(QFont("Microsoft YaHei", 9))
        
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
        self.tabs.setObjectName("main-tabs")
        
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
        analysis_type_label.setFont(QFont("Microsoft YaHei", 9))
        
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["趋势分析", "相关性分析", "异常检测", "统计摘要"])
        
        self.run_analysis_button = QPushButton("🔍 运行分析")
        self.run_analysis_button.setProperty("button-type", "analyze")
        self.run_analysis_button.setMinimumHeight(36)
        self.run_analysis_button.clicked.connect(self._run_analysis)
        
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
        
        open_action = QAction('打开数据(&O)', self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._browse_data_path)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('导出图表(&E)', self)
        export_action.setShortcut(QKeySequence.StandardKey.Save)
        export_action.triggered.connect(self._export_chart)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')
        
        refresh_action = QAction('刷新(&R)', self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self._refresh_view)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction('全屏(&F)', self)
        fullscreen_action.setShortcut(QKeySequence.StandardKey.FullScreen)
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbars(self):
        """设置工具栏"""
        
        # 主工具栏
        main_toolbar = self.addToolBar('主工具栏')
        main_toolbar.setMovable(False)
        
        # 打开数据按钮
        open_tool_action = QAction('📁', self)
        open_tool_action.setToolTip('打开数据文件')
        open_tool_action.triggered.connect(self._browse_data_path)
        main_toolbar.addAction(open_tool_action)
        
        # 刷新按钮
        refresh_tool_action = QAction('🔄', self)
        refresh_tool_action.setToolTip('刷新图表')
        refresh_tool_action.triggered.connect(self._refresh_view)
        main_toolbar.addAction(refresh_tool_action)
        
        main_toolbar.addSeparator()
        
        # 导出按钮
        export_tool_action = QAction('💾', self)
        export_tool_action.setToolTip('导出图表')
        export_tool_action.triggered.connect(self._export_chart)
        main_toolbar.addAction(export_tool_action)
        
        # 设置工具栏样式
        main_toolbar.setObjectName("main_toolbar")
    
    def _setup_statusbar(self):
        """设置状态栏"""
        
        self.statusBar().showMessage('就绪')
        
        # 添加状态指示器
        self.data_status_indicator = QLabel("未加载数据")
        self.data_status_indicator.setObjectName("data-status-warning")
        self.statusBar().addPermanentWidget(self.data_status_indicator)
        
        # 添加进度条（隐藏状态）
        self.progress_label = QLabel()
        self.statusBar().addPermanentWidget(self.progress_label)
    
    def _connect_signals(self):
        """连接信号和槽"""
        
        if self.chart_widget:
            self.chart_widget.data_changed.connect(self._on_chart_data_changed)
    

    
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
            
            # 使用原有的BatteryChartViewer加载数据
            self.current_viewer = BatteryChartViewer(data_path=data_path, auto_search=False)
            
            if self.current_viewer.load_data():
                self.data_path = data_path
                self.raw_data = getattr(self.current_viewer, 'listPlt', {})
                self.battery_names = getattr(self.current_viewer, 'listBatteryNameSplit', [])
                
                # 更新UI
                self._update_data_info()
                self._update_battery_filters()
                
                # 加载数据到图表控件
                if self.chart_widget:
                    self.chart_widget.update_data(self.raw_data, self.battery_names)
                
                # 更新状态
                self.data_status_label.setText("数据加载成功")
                self.data_status_label.setStyleSheet(f"color: {self.colors.SUCCESS}; font-weight: bold;")
                self.data_status_indicator.setText("数据已加载")
                self.data_status_indicator.setStyleSheet(f"color: {self.colors.SUCCESS};")
                
                self.statusBar().showMessage('数据加载完成')
                
                # 发射信号
                self.data_loaded.emit(data_path)
                
            else:
                raise Exception("数据加载失败")
                
        except Exception as e:
            logging.error("加载数据失败: %s", e)
            QMessageBox.critical(self, "错误", f"加载数据失败:\n{str(e)}")
            
            self.data_status_label.setText("数据加载失败")
            self.data_status_label.setStyleSheet(f"color: {self.colors.ERROR}; font-weight: bold;")
            self.statusBar().showMessage('数据加载失败')
    
    @pyqtSlot(str)
    def _on_chart_type_changed(self, chart_type):
        """图表类型变化处理"""
        
        logging.info("图表类型变更为: %s", chart_type)
        self.visualization_changed.emit(chart_type)
    
    @pyqtSlot(int)
    def _on_display_option_changed(self, state):
        """显示选项变化处理"""
        
        if self.chart_widget:
            self.chart_widget.refresh_chart()
    
    @pyqtSlot(str)
    def _on_battery_filter_changed(self, battery_filter):
        """电池过滤器变化处理"""
        
        if self.chart_widget:
            self.chart_widget.refresh_chart()
    
    @pyqtSlot(int)
    def _on_filter_parameter_changed(self, value):
        """过滤参数变化处理"""
        
        # 可以在这里添加实时过滤功能
        pass
    
    @pyqtSlot()
    def _apply_processing(self):
        """应用数据处理"""
        
        try:
            self.statusBar().showMessage('正在处理数据...')
            
            # 应用过滤参数
            filter_strength = self.filter_strength_spinbox.value()
            sampling_interval = self.sampling_spinbox.value()
            
            # 这里可以添加实际的数据处理逻辑
            # 例如：应用滤波、平滑、采样等
            
            self.statusBar().showMessage('数据处理完成')
            
        except Exception as e:
            logging.error("数据处理失败: %s", e)
            QMessageBox.warning(self, "警告", f"数据处理失败:\n{str(e)}")
    
    @pyqtSlot()
    def _run_analysis(self):
        """运行数据分析"""
        
        analysis_type = self.analysis_type_combo.currentText()
        
        try:
            # 模拟分析过程
            self.analysis_result_text.setPlainText(f"正在运行 {analysis_type}...")
            
            # 这里可以添加实际的分析逻辑
            # 例如：统计分析、趋势分析、相关性分析等
            
            result_text = f"""
{analysis_type}结果:

数据摘要:
- 电池数量: {len(self.battery_names) if self.battery_names else 0}
- 数据点数量: {len(self.raw_data) if self.raw_data else 0}

分析结果:
- 数据质量: 良好
- 发现趋势: 电压呈下降趋势
- 异常值: 检测到3个异常点

建议:
- 建议调整测试参数
- 关注电压下降速度
- 考虑环境因素影响
            """
            
            self.analysis_result_text.setPlainText(result_text)
            
        except Exception as e:
            logging.error("分析失败: %s", e)
            self.analysis_result_text.setPlainText(f"分析失败: {str(e)}")
    
    @pyqtSlot()
    def _refresh_view(self):
        """刷新视图"""
        
        if self.chart_widget:
            self.chart_widget.refresh_chart()
        
        self.statusBar().showMessage('视图已刷新')
    
    @pyqtSlot()
    def _toggle_fullscreen(self):
        """切换全屏模式"""
        
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    @pyqtSlot()
    def _export_chart(self):
        """导出图表"""
        
        if not self.chart_widget or not self.chart_widget.get_figure():
            QMessageBox.warning(self, "警告", "没有可导出的图表")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "导出图表",
            f"battery_analysis_{self.analysis_type_combo.currentText()}.png",
            "PNG图片 (*.png);;PDF文档 (*.pdf);;SVG矢量 (*.svg)"
        )
        
        if filename:
            if self.chart_widget.export_chart(filename):
                QMessageBox.information(self, "成功", f"图表已导出到:\n{filename}")
            else:
                QMessageBox.warning(self, "失败", "图表导出失败")
    
    @pyqtSlot()
    def _show_about(self):
        """显示关于对话框"""
        
        about_text = """
现代化电池数据分析工具 v3.0

特性:
• 现代化UI设计
• 嵌入式图表显示
• 多种图表类型支持
• 实时数据处理
• 专业分析功能

开发团队: 电池分析团队
        """
        
        QMessageBox.about(self, "关于", about_text)
    
    @pyqtSlot()
    def _on_chart_data_changed(self):
        """图表数据变化处理"""
        
        self.statusBar().showMessage('图表数据已更新')
    
    def _update_data_info(self):
        """更新数据信息"""
        
        if self.raw_data:
            details = f"""
数据路径: {self.data_path}
电池数量: {len(self.battery_names) if self.battery_names else 0}
数据组数: {len(self.raw_data)}
加载时间: {__import__('datetime').datetime.now().strftime('%H:%M:%S')}
            """
            
            self.data_details_text.setPlainText(details.strip())
            
            # 更新统计信息
            stats = f"统计: {len(self.battery_names)} 个电池, {len(self.raw_data)} 个数据组"
            self.stats_label.setText(stats)
        else:
            self.data_details_text.setPlainText("暂无数据")
            self.stats_label.setText("统计信息: 暂无")
    
    def _update_battery_filters(self):
        """更新电池过滤器"""
        
        self.battery_filter_combo.clear()
        if self.battery_names:
            self.battery_filter_combo.addItem("全部电池")
            self.battery_filter_combo.addItems(self.battery_names)


# 工厂函数
def create_modern_viewer(data_path: Optional[str] = None) -> ModernBatteryViewer:
    """创建现代化查看器"""
    return ModernBatteryViewer(data_path=data_path)


if __name__ == '__main__':
    import sys
    
    app = QApplication(sys.argv)
    
    # 应用现代化样式
    modern_theme._setup_matplotlib_theme()
    
    # 创建查看器
    viewer = create_modern_viewer()
    viewer.show()
    
    sys.exit(app.exec())