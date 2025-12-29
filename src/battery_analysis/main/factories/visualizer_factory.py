# -*- coding: utf-8 -*-
"""
可视化器工厂模块

使用工厂模式创建可视化器实例，实现依赖倒置
"""

import logging
from typing import Optional, Type, Dict, Any
from battery_analysis.main.interfaces.ivisualizer import IVisualizer
from battery_analysis.main import battery_chart_viewer


class VisualizerFactory:
    """
    可视化器工厂类
    
    负责创建不同类型的可视化器实例
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 存储已注册的可视化器类
        self._visualizers: Dict[str, Type[IVisualizer]] = {}
        self._register_default_visualizers()

    def _register_default_visualizers(self):
        """注册默认的可视化器"""
        self.register_visualizer("battery_chart", BatteryChartViewerWrapper)

    def register_visualizer(self, name: str, visualizer_class: Type[IVisualizer]):
        """
        注册可视化器类
        
        Args:
            name: 可视化器名称
            visualizer_class: 可视化器类
        """
        if not issubclass(visualizer_class, IVisualizer):
            raise ValueError(f"类 {visualizer_class.__name__} 必须实现 IVisualizer 接口")
        
        self._visualizers[name] = visualizer_class
        self.logger.debug(f"注册可视化器: {name} -> {visualizer_class.__name__}")

    def create_visualizer(self, name: str, **kwargs) -> Optional[IVisualizer]:
        """
        创建可视化器实例
        
        Args:
            name: 可视化器名称
            **kwargs: 传递给可视化器构造函数的参数
            
        Returns:
            可视化器实例或None（如果不存在）
        """
        if name not in self._visualizers:
            self.logger.error(f"未找到可视化器: {name}")
            return None

        try:
            visualizer_class = self._visualizers[name]
            instance = visualizer_class(**kwargs)
            self.logger.debug(f"创建可视化器实例: {name}")
            return instance
        except Exception as e:
            self.logger.error(f"创建可视化器 {name} 失败: {e}")
            return None

    def get_available_visualizers(self) -> list:
        """
        获取可用的可视化器列表
        
        Returns:
            list: 可用可视化器名称列表
        """
        return list(self._visualizers.keys())


class BatteryChartViewerWrapper(IVisualizer):
    """
    BatteryChartViewer的适配器类
    
    将现有的BatteryChartViewer包装为实现IVisualizer接口的类
    """

    def __init__(self, data_path: Optional[str] = None):
        """
        初始化适配器
        
        Args:
            data_path: 可选的数据路径
        """
        self.logger = logging.getLogger(__name__)
        
        # 创建viewer实例时传递data_path=None和auto_search=False以避免自动搜索
        self._viewer = battery_chart_viewer.BatteryChartViewer(data_path=None, auto_search=False)
        self._config = {}
        
        # 如果提供了有效的数据路径，先设置路径但不自动加载
        if data_path and os.path.exists(data_path):
            self._viewer.set_data_path(data_path)
            self.logger.info(f"设置数据路径: {data_path}")
            # 不自动加载数据，由调用者决定何时加载
    

        
    def show_figure(self, data_path: Optional[str] = None) -> bool:
        """
        显示图表
        
        Args:
            data_path: 可选的数据路径
            
        Returns:
            bool: 是否成功显示
        """
        try:
            # 如果提供了新的数据路径，先加载数据
            if data_path is not None:
                self._viewer.set_data_path(data_path)
                if not self._viewer.load_data():
                    self.logger.warning("数据加载失败，显示空图表")
                    self._viewer.loaded_data = False

            # 创建可视化
            success = self._viewer.plt_figure()
            if success:
                self.logger.info("图表显示成功")
            else:
                self.logger.warning("图表显示失败")
            
            return success
        except Exception as e:
            self.logger.error(f"显示图表时出错: {e}")
            return False

    def load_data(self, data_path: str) -> bool:
        """
        加载数据
        
        Args:
            data_path: 数据路径
            
        Returns:
            bool: 是否成功加载数据
        """
        try:
            self._viewer.set_data_path(data_path)
            success = self._viewer.load_data()
            if success:
                self._viewer.loaded_data = True
                self.logger.info(f"数据加载成功: {data_path}")
            else:
                self._viewer.loaded_data = False
                self.logger.warning(f"数据加载失败: {data_path}")
            
            return success
        except Exception as e:
            self.logger.error(f"加载数据时出错: {e}")
            self._viewer.loaded_data = False
            return False

    def clear_data(self) -> None:
        """
        清除所有数据，回到初始状态
        """
        try:
            self._viewer.loaded_data = False
            self._viewer.listPlt = []
            self._viewer.listBatteryName = []
            self._viewer.listBatteryNameSplit = []
            self._viewer.intBatteryNum = 0
            
            # 清除数据路径
            self._viewer.strPltPath = None
            self._viewer.strInfoImageCsvPath = None
            
            self.logger.info("数据已清除")
        except Exception as e:
            self.logger.error(f"清除数据时出错: {e}")

    def is_data_loaded(self) -> bool:
        """
        检查是否有数据已加载
        
        Returns:
            bool: 是否已加载数据
        """
        return getattr(self._viewer, 'loaded_data', False)

    def get_status_info(self) -> dict:
        """
        获取状态信息
        
        Returns:
            dict: 状态信息字典
        """
        return {
            'data_loaded': self.is_data_loaded(),
            'battery_count': getattr(self._viewer, 'intBatteryNum', 0),
            'data_path': getattr(self._viewer, 'strPltPath', None),
            'config': self._config.copy()
        }

    def set_config(self, config: dict) -> None:
        """
        设置配置
        
        Args:
            config: 配置字典
        """
        self._config.update(config)
        self.logger.debug(f"配置已更新: {config}")

    def get_config(self) -> dict:
        """
        获取当前配置
        
        Returns:
            dict: 当前配置字典
        """
        return self._config.copy()

    @property
    def viewer(self) -> battery_chart_viewer.BatteryChartViewer:
        """
        获取原始的viewer实例
        
        Returns:
            BatteryChartViewer: 原始viewer实例
        """
        return self._viewer