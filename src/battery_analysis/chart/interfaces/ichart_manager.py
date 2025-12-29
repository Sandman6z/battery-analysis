# -*- coding: utf-8 -*-
"""
图表管理抽象接口

定义图表操作的抽象接口，实现图表库的解耦
支持多种图表库（matplotlib、plotly、bokeh等）
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Union
from enum import Enum


class ChartType(Enum):
    """图表类型枚举"""
    LINE = "line"
    SCATTER = "scatter"
    BAR = "bar"
    HISTOGRAM = "histogram"
    PIE = "pie"
    HEATMAP = "heatmap"
    BOX = "box"


class ChartFormat(Enum):
    """图表格式枚举"""
    PNG = "png"
    PDF = "pdf"
    SVG = "svg"
    HTML = "html"


class IChartManager(ABC):
    """图表管理抽象接口"""
    
    @abstractmethod
    def create_chart(self, chart_type: ChartType, **kwargs) -> Any:
        """创建图表
        
        Args:
            chart_type: 图表类型
            **kwargs: 图表参数
            
        Returns:
            Any: 图表实例
        """
        pass
    
    @abstractmethod
    def set_chart_data(self, chart: Any, data: Dict[str, Any]) -> bool:
        """设置图表数据
        
        Args:
            chart: 图表实例
            data: 数据字典
            
        Returns:
            bool: 是否设置成功
        """
        pass
    
    @abstractmethod
    def set_chart_title(self, chart: Any, title: str) -> None:
        """设置图表标题
        
        Args:
            chart: 图表实例
            title: 标题文本
        """
        pass
    
    @abstractmethod
    def set_axis_labels(self, chart: Any, x_label: str, y_label: str) -> None:
        """设置坐标轴标签
        
        Args:
            chart: 图表实例
            x_label: X轴标签
            y_label: Y轴标签
        """
        pass
    
    @abstractmethod
    def add_legend(self, chart: Any) -> None:
        """添加图例
        
        Args:
            chart: 图表实例
        """
        pass
    
    @abstractmethod
    def save_chart(self, chart: Any, file_path: str, format: ChartFormat = ChartFormat.PNG, **kwargs) -> bool:
        """保存图表
        
        Args:
            chart: 图表实例
            file_path: 保存路径
            format: 保存格式
            **kwargs: 保存参数
            
        Returns:
            bool: 是否保存成功
        """
        pass
    
    @abstractmethod
    def show_chart(self, chart: Any) -> bool:
        """显示图表
        
        Args:
            chart: 图表实例
            
        Returns:
            bool: 是否显示成功
        """
        pass
    
    @abstractmethod
    def close_chart(self, chart: Any) -> None:
        """关闭图表
        
        Args:
            chart: 图表实例
        """
        pass
    
    @abstractmethod
    def create_subplot(self, rows: int, columns: int, index: int = 1) -> Any:
        """创建子图
        
        Args:
            rows: 行数
            columns: 列数
            index: 子图索引
            
        Returns:
            Any: 子图实例
        """
        pass
    
    @abstractmethod
    def set_grid(self, chart: Any, show: bool = True) -> None:
        """设置网格
        
        Args:
            chart: 图表实例
            show: 是否显示网格
        """
        pass
    
    @abstractmethod
    def set_colors(self, chart: Any, colors: List[str]) -> None:
        """设置颜色
        
        Args:
            chart: 图表实例
            colors: 颜色列表
        """
        pass