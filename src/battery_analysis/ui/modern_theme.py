# -*- coding: utf-8 -*-
"""
现代化UI主题配置模块

提供统一的现代化UI主题配置，包括颜色方案、字体、样式等
"""

import logging
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
import numpy as np


# 现代化色彩方案
class ModernColorScheme:
    """现代化色彩方案"""
    
    # 主色调 - 深蓝色系
    PRIMARY = "#1565C0"           # 主蓝色
    PRIMARY_LIGHT = "#42A5F5"     # 浅蓝色
    PRIMARY_DARK = "#0D47A1"      # 深蓝色
    
    # 辅助色
    SECONDARY = "#FF9800"         # 橙色
    SECONDARY_LIGHT = "#FFB74D"   # 浅橙色
    SECONDARY_DARK = "#E65100"    # 深橙色
    
    # 中性色
    BACKGROUND = "#FAFAFA"        # 浅灰背景
    SURFACE = "#FFFFFF"           # 白色表面
    SURFACE_VARIANT = "#F5F5F5"   # 变体表面
    ON_SURFACE = "#212121"        # 表面文字
    ON_SURFACE_LIGHT = "#757575"  # 浅色文字
    
    # 状态色
    SUCCESS = "#4CAF50"           # 成功绿色
    WARNING = "#FF9800"           # 警告橙色
    ERROR = "#F44336"             # 错误红色
    INFO = "#2196F3"              # 信息蓝色
    
    # 图表专用色彩
    CHART_COLORS = [
        "#1565C0",  # 深蓝
        "#FF9800",  # 橙色
        "#4CAF50",  # 绿色
        "#9C27B0",  # 紫色
        "#F44336",  # 红色
        "#00BCD4",  # 青色
        "#795548",  # 棕色
        "#607D8B"   # 蓝灰
    ]


class ModernTheme:
    """现代化主题配置"""
    
    def __init__(self):
        self.colors = ModernColorScheme()
        self._setup_matplotlib_theme()
    
    def _setup_matplotlib_theme(self):
        """设置matplotlib现代化主题"""
        
        # 1. 整体样式配置
        plt.style.use('default')
        
        # 2. 简化版matplotlib参数配置
        try:
            mpl.rcParams.update({
                # 字体配置
                'font.size': 11,
                'font.family': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans', 'Arial'],
                'axes.titlesize': 14,
                'axes.labelsize': 12,
                'xtick.labelsize': 10,
                'ytick.labelsize': 10,
                'legend.fontsize': 10,
                'figure.titlesize': 16,
                
                # 颜色配置
                'axes.facecolor': self.colors.SURFACE,
                'figure.facecolor': self.colors.SURFACE,
                
                # 网格配置
                'axes.grid': True,
                'grid.color': '#E0E0E0',
                'grid.alpha': 0.3,
                'grid.linewidth': 0.8,
                
                # 刻度配置
                'xtick.direction': 'out',
                'ytick.direction': 'out',
                'xtick.major.size': 6,
                'ytick.major.size': 6,
                'xtick.major.width': 1.2,
                'ytick.major.width': 1.2,
                
                # 图例配置
                'legend.frameon': True,
                'legend.framealpha': 0.9,
                'legend.facecolor': self.colors.SURFACE,
                'legend.edgecolor': self.colors.SURFACE_VARIANT,
                
                # 线条配置
                'lines.linewidth': 1.5,
                'lines.markersize': 6,
                
                # 图像配置
                'savefig.dpi': 300,
                'savefig.bbox': 'tight',
                'savefig.pad_inches': 0.1,
                
                # 交互配置
                'interactive': True
            })
        except Exception as e:
            logging.warning("部分matplotlib参数设置失败，使用默认值: %s", e)
            # 使用基本配置
            mpl.rcParams.update({
                'font.size': 11,
                'font.family': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans', 'Arial'],
                'axes.grid': True,
                'interactive': True
            })
        
        # 3. 创建自定义颜色映射
        self._create_custom_colormaps()
    
    def _create_custom_colormaps(self):
        """创建自定义颜色映射"""
        
        # 渐变色彩映射
        gradient_colors = [
            self.colors.PRIMARY_DARK,
            self.colors.PRIMARY,
            self.colors.PRIMARY_LIGHT,
            self.colors.SECONDARY_LIGHT,
            self.colors.SECONDARY
        ]
        
        self.gradient_cmap = LinearSegmentedColormap.from_list(
            'modern_gradient', gradient_colors, N=256)
        
        # 热度图色彩映射
        heat_colors = [
            '#FFFFFF',  # 白色
            '#E3F2FD',  # 浅蓝
            '#90CAF9',  # 中蓝
            '#42A5F5',  # 蓝色
            '#1E88E5',  # 深蓝
            '#1565C0'   # 最深蓝
        ]
        
        self.heat_cmap = LinearSegmentedColormap.from_list(
            'modern_heat', heat_colors, N=256)
    
    def get_chart_style(self, chart_type='line'):
        """获取图表专用样式"""
        
        if chart_type == 'line':
            return {
                'color': self.colors.CHART_COLORS[0],
                'linewidth': 2.0,
                'alpha': 0.8,
                'marker': 'o',
                'markersize': 4,
                'markerfacecolor': 'white',
                'markeredgewidth': 1.5,
                'markeredgecolor': self.colors.CHART_COLORS[0]
            }
        elif chart_type == 'area':
            return {
                'color': self.colors.CHART_COLORS[0],
                'alpha': 0.3,
                'linewidth': 2.0
            }
        elif chart_type == 'scatter':
            return {
                'color': self.colors.CHART_COLORS[0],
                's': 50,
                'alpha': 0.7,
                'edgecolors': 'white',
                'linewidth': 1.0
            }
        else:
            return {'color': self.colors.CHART_COLORS[0]}
    
    def create_modern_figure(self, figsize=(12, 8), dpi=100):
        """创建现代化样式的图表"""
        
        fig = plt.figure(figsize=figsize, dpi=dpi, 
                        facecolor=self.colors.SURFACE,
                        edgecolor='none')
        
        # 创建现代化的子图
        ax = fig.add_subplot(111, facecolor=self.colors.SURFACE)
        
        # 应用现代化样式
        self._style_axes(ax)
        
        return fig, ax
    
    def _style_axes(self, ax):
        """应用现代化样式到坐标轴"""
        
        # 标题和标签的现代化样式
        ax.title.set_fontsize(14)
        ax.title.set_fontweight('bold')
        ax.title.set_color(self.colors.ON_SURFACE)
        
        ax.xaxis.label.set_fontsize(12)
        ax.xaxis.label.set_fontweight('medium')
        ax.xaxis.label.set_color(self.colors.ON_SURFACE)
        
        ax.yaxis.label.set_fontsize(12)
        ax.yaxis.label.set_fontweight('medium')
        ax.yaxis.label.set_color(self.colors.ON_SURFACE)
        
        # 设置刻度样式
        ax.tick_params(
            axis='both',
            which='major',
            colors=self.colors.ON_SURFACE_LIGHT,
            labelsize=10,
            length=6,
            width=1.2
        )
        
        # 设置网格样式
        ax.grid(True, alpha=0.3, color='#E0E0E0', linewidth=0.8)
        
        # 设置边框样式
        for spine in ax.spines.values():
            spine.set_color('#BDBDBD')
            spine.set_linewidth(1.2)
    
    def get_modern_button_style(self, is_active=True):
        """获取现代化按钮样式"""
        
        if is_active:
            return {
                'facecolor': self.colors.PRIMARY,
                'edgecolor': self.colors.PRIMARY_DARK,
                'linewidth': 1.5,
                'alpha': 0.9,
                'labelcolor': 'white'
            }
        else:
            return {
                'facecolor': self.colors.SURFACE,
                'edgecolor': self.colors.SURFACE_VARIANT,
                'linewidth': 1.0,
                'alpha': 0.8,
                'labelcolor': self.colors.ON_SURFACE
            }


# 全局主题实例
modern_theme = ModernTheme()

# 导出常用函数
def apply_modern_theme():
    """应用现代化主题"""
    modern_theme._setup_matplotlib_theme()

def get_modern_colors():
    """获取现代化色彩方案"""
    return modern_theme.colors

def create_modern_figure(figsize=(12, 8), dpi=100):
    """创建现代化图表"""
    return modern_theme.create_modern_figure(figsize, dpi)
