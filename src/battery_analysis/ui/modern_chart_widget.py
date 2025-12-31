# -*- coding: utf-8 -*-
"""
嵌入式图表控件

提供将matplotlib图表嵌入到Qt界面中的自定义控件
"""

import sys
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QComboBox, QCheckBox,
                           QGroupBox, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np

from battery_analysis.ui.modern_theme import modern_theme, ModernColorScheme


class ModernChartWidget(QWidget):
    """现代化图表控件"""
    
    # 信号定义
    data_changed = pyqtSignal()  # 数据变化信号
    chart_type_changed = pyqtSignal(str)  # 图表类型变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = ModernColorScheme()
        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.axes = None
        
        # 图表状态
        self.current_data = None
        self.chart_type = 'line'
        self.is_filtered = True
        
        self._setup_ui()
        self._setup_chart()
    
    def _setup_ui(self):
        """设置用户界面"""
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 工具栏
        self._create_toolbar(main_layout)
        
        # 图表区域
        self._create_chart_area(main_layout)
        
        # 控制面板
        self._create_control_panel(main_layout)
        
        # 设置样式
        self._apply_styles()
    
    def _create_toolbar(self, parent_layout):
        """创建工具栏"""
        
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.Shape.Box)
        toolbar_frame.setMaximumHeight(50)
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        # 图表类型选择
        type_label = QLabel("图表类型:")
        type_label.setFont(QFont("Microsoft YaHei", 9))
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["折线图", "散点图", "面积图", "柱状图"])
        self.chart_type_combo.currentTextChanged.connect(self._on_chart_type_changed)
        
        # 过滤开关
        self.filter_checkbox = QCheckBox("显示过滤数据")
        self.filter_checkbox.setChecked(True)
        self.filter_checkbox.stateChanged.connect(self._on_filter_changed)
        
        # 刷新按钮
        self.refresh_button = QPushButton("刷新图表")
        self.refresh_button.clicked.connect(self.refresh_chart)
        
        # 添加到工具栏
        toolbar_layout.addWidget(type_label)
        toolbar_layout.addWidget(self.chart_type_combo)
        toolbar_layout.addWidget(self.filter_checkbox)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.refresh_button)
        
        parent_layout.addWidget(toolbar_frame)
    
    def _create_chart_area(self, parent_layout):
        """创建图表区域"""
        
        # 图表容器
        chart_container = QFrame()
        chart_container.setFrameStyle(QFrame.Shape.Box)
        chart_container.setSizePolicy(QSizePolicy.Policy.Expanding, 
                                    QSizePolicy.Policy.Expanding)
        
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.setContentsMargins(5, 5, 5, 5)
        
        # 图表标题
        self.chart_title = QLabel("电池数据分析图表")
        self.chart_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        
        chart_layout.addWidget(self.chart_title)
        
        parent_layout.addWidget(chart_container)
        
        # 这里将设置matplotlib图表
        self._setup_matplotlib_chart(chart_layout)
    
    def _setup_matplotlib_chart(self, parent_layout):
        """设置matplotlib图表"""
        
        try:
            # 创建图表
            self.figure = Figure(figsize=(10, 6), dpi=100,
                               facecolor=self.colors.SURFACE)
            
            # 创建画布
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, 
                                    QSizePolicy.Policy.Expanding)
            
            # 创建工具栏
            self.toolbar = NavigationToolbar(self.canvas, self)
            self.toolbar.setStyleSheet(f"""
                QToolBar {{
                    background-color: {self.colors.SURFACE};
                    border: 1px solid {self.colors.SURFACE_VARIANT};
                    spacing: 5px;
                }}
                QToolBar QToolButton {{
                    background-color: {self.colors.SURFACE};
                    border: 1px solid {self.colors.SURFACE_VARIANT};
                    border-radius: 4px;
                    padding: 5px;
                    margin: 2px;
                }}
                QToolBar QToolButton:hover {{
                    background-color: {self.colors.PRIMARY_LIGHT};
                }}
            """)
            
            # 添加到布局
            parent_layout.addWidget(self.toolbar)
            parent_layout.addWidget(self.canvas)
            
            # 创建默认的坐标轴
            self.axes = self.figure.add_subplot(111)
            self._apply_modern_style()
            
            logging.info("Matplotlib图表控件初始化成功")
            
        except Exception as e:
            logging.error(f"初始化Matplotlib图表失败: {e}")
            # 创建错误显示
            error_label = QLabel("图表初始化失败")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet(f"color: {self.colors.ERROR}; font-size: 14px;")
            parent_layout.addWidget(error_label)
    
    def _create_control_panel(self, parent_layout):
        """创建控制面板"""
        
        control_group = QGroupBox("图表控制")
        control_group.setMaximumHeight(120)
        
        control_layout = QHBoxLayout(control_group)
        control_layout.setContentsMargins(10, 5, 10, 5)
        
        # 数据信息
        info_label = QLabel("数据信息:")
        info_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        
        self.data_info_label = QLabel("暂无数据")
        self.data_info_label.setFont(QFont("Microsoft YaHei", 9))
        self.data_info_label.setStyleSheet(f"color: {self.colors.ON_SURFACE_LIGHT};")
        
        # 缩放控制
        zoom_label = QLabel("缩放:")
        
        self.zoom_in_button = QPushButton("放大")
        self.zoom_out_button = QPushButton("缩小")
        self.reset_zoom_button = QPushButton("重置")
        
        self.zoom_in_button.clicked.connect(lambda: self._zoom(1.2))
        self.zoom_out_button.clicked.connect(lambda: self._zoom(0.8))
        self.reset_zoom_button.clicked.connect(self.reset_zoom)
        
        # 添加到控制面板
        control_layout.addWidget(info_label)
        control_layout.addWidget(self.data_info_label)
        control_layout.addStretch()
        control_layout.addWidget(zoom_label)
        control_layout.addWidget(self.zoom_in_button)
        control_layout.addWidget(self.zoom_out_button)
        control_layout.addWidget(self.reset_zoom_button)
        
        parent_layout.addWidget(control_group)
    
    def _apply_styles(self):
        """应用现代化样式"""
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors.BACKGROUND};
                color: {self.colors.ON_SURFACE};
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {self.colors.SURFACE_VARIANT};
                border-radius: 8px;
                margin: 5px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {self.colors.PRIMARY};
                background-color: {self.colors.BACKGROUND};
            }}
            
            QPushButton {{
                background-color: {self.colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: medium;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: {self.colors.PRIMARY_LIGHT};
            }}
            
            QPushButton:pressed {{
                background-color: {self.colors.PRIMARY_DARK};
            }}
            
            QComboBox {{
                background-color: {self.colors.SURFACE};
                border: 1px solid {self.colors.SURFACE_VARIANT};
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }}
            
            QComboBox:hover {{
                border-color: {self.colors.PRIMARY};
            }}
            
            QCheckBox {{
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid {self.colors.SURFACE_VARIANT};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {self.colors.PRIMARY};
                border-color: {self.colors.PRIMARY};
            }}
        """)
    
    def _setup_chart(self):
        """设置图表基本配置"""
        
        if self.figure and self.axes:
            # 应用现代化主题
            modern_theme._style_axes(self.axes)
            
            # 设置初始数据
            self._show_placeholder()
    
    def _apply_modern_style(self):
        """应用现代化样式到图表"""
        
        if not self.axes:
            return
        
        # 应用现代化主题
        modern_theme._style_axes(self.axes)
        
        # 额外的现代化样式
        self.axes.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.axes.set_facecolor(self.colors.SURFACE)
        
        # 标题样式
        self.axes.set_title("电池数据分析", 
                          fontsize=14, 
                          fontweight='bold',
                          color=self.colors.ON_SURFACE,
                          pad=20)
    
    def _show_placeholder(self):
        """显示占位符图表"""
        
        if not self.axes:
            return
        
        self.axes.clear()
        self._apply_modern_style()
        
        # 创建示例数据
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        
        # 绘制示例曲线
        self.axes.plot(x, y1, label='电池1', 
                      color=self.colors.CHART_COLORS[0], linewidth=2)
        self.axes.plot(x, y2, label='电池2',
                      color=self.colors.CHART_COLORS[1], linewidth=2)
        
        self.axes.legend(loc='upper right')
        self.axes.set_xlabel('时间 (s)')
        self.axes.set_ylabel('电压 (V)')
        
        self.canvas.draw()
    
    def update_data(self, data, battery_names=None):
        """更新图表数据"""
        
        try:
            self.current_data = data
            
            if battery_names:
                self.battery_names = battery_names
            
            # 更新数据信息显示
            if data and len(data) > 0:
                info_text = f"数据点: {len(data[0]) if isinstance(data[0], list) else 'N/A'}"
                if battery_names:
                    info_text += f" | 电池数量: {len(battery_names)}"
                self.data_info_label.setText(info_text)
            
            # 刷新图表
            self.refresh_chart()
            
            # 发射信号
            self.data_changed.emit()
            
        except Exception as e:
            logging.error(f"更新图表数据失败: {e}")
    
    def refresh_chart(self):
        """刷新图表显示"""
        
        if not self.axes or not self.current_data:
            self._show_placeholder()
            return
        
        try:
            # 清空当前图表
            self.axes.clear()
            self._apply_modern_style()
            
            # 根据当前设置绘制数据
            self._plot_current_data()
            
            # 更新画布
            self.canvas.draw()
            
        except Exception as e:
            logging.error(f"刷新图表失败: {e}")
    
    def _plot_current_data(self):
        """根据当前设置绘制数据"""
        
        if not self.current_data:
            return
        
        chart_styles = modern_theme.get_chart_style(self.chart_type)
        
        # 这里需要根据实际的数据结构来调整
        # 示例：假设数据是 [x_data, y_data, battery_name] 的列表
        for i, data_series in enumerate(self.current_data):
            if len(data_series) >= 2:
                x_data = data_series[0]
                y_data = data_series[1]
                battery_name = data_series[2] if len(data_series) > 2 else f"电池{i+1}"
                
                color = self.colors.CHART_COLORS[i % len(self.colors.CHART_COLORS)]
                
                if self.chart_type == 'line':
                    self.axes.plot(x_data, y_data, 
                                 label=battery_name,
                                 color=color,
                                 linewidth=2,
                                 alpha=0.8)
                
                elif self.chart_type == 'scatter':
                    self.axes.scatter(x_data, y_data,
                                    label=battery_name,
                                    color=color,
                                    alpha=0.7,
                                    s=30)
                
                elif self.chart_type == 'area':
                    self.axes.fill_between(x_data, y_data,
                                         alpha=0.3,
                                         color=color,
                                         label=battery_name)
            
            # 设置图例
            if i == 0:  # 只在第一次添加图例
                self.axes.legend(loc='upper right')
    
    def _on_chart_type_changed(self, chart_type):
        """图表类型变化处理"""
        
        type_mapping = {
            "折线图": "line",
            "散点图": "scatter", 
            "面积图": "area",
            "柱状图": "bar"
        }
        
        self.chart_type = type_mapping.get(chart_type, "line")
        self.refresh_chart()
        
        # 发射信号
        self.chart_type_changed.emit(self.chart_type)
    
    def _on_filter_changed(self, state):
        """过滤状态变化处理"""
        
        self.is_filtered = state == Qt.CheckState.Checked.value
        self.refresh_chart()
    
    def _zoom(self, factor):
        """缩放图表"""
        
        if self.axes:
            self.axes.set_xlim([x * factor for x in self.axes.get_xlim()])
            self.axes.set_ylim([y * factor for y in self.axes.get_ylim()])
            self.canvas.draw()
    
    def reset_zoom(self):
        """重置缩放"""
        
        if self.axes:
            self.axes.relim()
            self.axes.autoscale_view()
            self.canvas.draw()
    
    def export_chart(self, filename, format='png'):
        """导出图表"""
        
        if self.figure:
            try:
                self.figure.savefig(filename, format=format, 
                                  dpi=300, bbox_inches='tight')
                logging.info(f"图表已导出到: {filename}")
                return True
            except Exception as e:
                logging.error(f"导出图表失败: {e}")
                return False
        return False
    
    def get_figure(self):
        """获取matplotlib图形对象"""
        return self.figure
    
    def get_canvas(self):
        """获取画布对象"""
        return self.canvas
    
    def sizeHint(self):
        """返回建议大小"""
        return QSize(800, 600)
    
    def minimumSizeHint(self):
        """返回最小大小"""
        return QSize(600, 400)