"""
可视化器工厂模块

使用工厂模式创建可视化器实例，实现依赖倒置
"""

import logging
import os

from battery_analysis.main.factories.battery_chart_viewer_wrapper import (
    BatteryChartViewerWrapper,
)
from battery_analysis.main.interfaces.ivisualizer import IVisualizer

__all__ = ["BatteryChartViewerWrapper", "VisualizerFactory"]


class VisualizerFactory:
    """
    可视化器工厂类

    负责创建不同类型的可视化器实例
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 存储已注册的可视化器类
        self._visualizers: dict[str, type[IVisualizer]] = {}
        self._register_default_visualizers()

    def _register_default_visualizers(self):
        """注册默认的可视化器"""
        self.register_visualizer("battery_chart", BatteryChartViewerWrapper)

    def register_visualizer(self, name: str, visualizer_class: type[IVisualizer]):
        """
        注册可视化器类

        Args:
            name: 可视化器名称
            visualizer_class: 可视化器类
        """
        if not issubclass(visualizer_class, IVisualizer):
            raise ValueError(
                f"Class {visualizer_class.__name__} must implement the IVisualizer interface"
            )

        self._visualizers[name] = visualizer_class
        self.logger.debug("Registered visualizer: %s -> %s", name, visualizer_class.__name__)

    def create_visualizer(self, name: str, **kwargs) -> IVisualizer | None:
        """
        创建可视化器实例

        Args:
            name: 可视化器名称
            **kwargs: 传递给可视化器构造函数的参数

        Returns:
            可视化器实例或None（如果不存在）
        """
        if name not in self._visualizers:
            self.logger.error("Visualizer not found: %s", name)
            return None

        try:
            visualizer_class = self._visualizers[name]
            instance = visualizer_class(**kwargs)
            self.logger.debug("Creating visualizer instance: %s", name)
            return instance
        except (ImportError, TypeError, ValueError, OSError) as e:
            self.logger.error("Failed to create visualizer %s: %s", name, e)
            return None

    def get_available_visualizers(self) -> list:
        """
        获取可用的可视化器列表

        Returns:
            list: 可用可视化器名称列表
        """
        return list(self._visualizers.keys())
