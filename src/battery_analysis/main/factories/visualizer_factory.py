# -*- coding: utf-8 -*-
"""
可视化器工厂模块

使用工厂模式创建可视化器实例，实现依赖倒置
"""

import logging
import os
from typing import Optional, Type, Dict, Any
from battery_analysis.main.interfaces.ivisualizer import IVisualizer
from battery_analysis.main.battery_chart_viewer import BatteryChartViewer


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
        self.logger.debug("注册可视化器: %s -> %s", name, visualizer_class.__name__)

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
            self.logger.error("未找到可视化器: %s", name)
            return None

        try:
            visualizer_class = self._visualizers[name]
            instance = visualizer_class(**kwargs)
            self.logger.debug("创建可视化器实例: %s", name)
            return instance
        except (ImportError, TypeError, ValueError, OSError) as e:
            self.logger.error("创建可视化器 %s 失败: %s", name, e)
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
        self._viewer = BatteryChartViewer(data_path=None, auto_search=False)
        self._config = {}
        
        # 如果提供了有效的数据路径，先设置路径但不自动加载
        if data_path and os.path.exists(data_path):
            self._viewer.set_data_path(data_path)
            self.logger.info("设置数据路径: %s", data_path)
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
            # 重置viewer状态，确保每次显示都能重新搜索数据
            self._viewer.loaded_data = False
            
            # 如果提供了新的数据路径，先加载数据
            if data_path is not None:
                self._viewer.set_data_path(data_path)
                if not self._viewer.load_data():
                    self.logger.warning("数据加载失败，尝试搜索其他数据文件")
                    self._viewer.loaded_data = False
                    # 即使提供了数据路径，也尝试搜索其他可能的数据文件
                    self._viewer._search_for_data_files()
            # 始终尝试搜索数据文件，确保能找到最新的数据
            else:
                self.logger.info("没有提供数据路径，尝试搜索数据文件")
                self._viewer._search_for_data_files()
                
            # 如果搜索后仍没有数据，尝试从配置中获取数据路径
            if not self._viewer.loaded_data:
                self.logger.info("搜索后仍没有数据，尝试从配置中获取数据路径")
                # 尝试从主控制器获取输出路径作为数据路径
                try:
                    from battery_analysis.main.controllers.main_controller import MainController
                    from battery_analysis.main.services.service_container import get_service_container
                    
                    service_container = get_service_container()
                    main_controller = service_container.get("main_controller")
                    if main_controller and hasattr(main_controller, 'output_path') and main_controller.output_path:
                        self.logger.info("从主控制器获取到输出路径: %s", main_controller.output_path)
                        self._viewer.set_data_path(main_controller.output_path)
                        if self._viewer.load_data():
                            self.logger.info("成功从主控制器输出路径加载数据")
                            self._viewer.loaded_data = True
                except (ImportError, AttributeError, TypeError, ValueError) as e:
                    self.logger.warning("从主控制器获取数据路径失败: %s", e)

            # 创建可视化
            success = self._viewer.plt_figure()
            if success:
                self.logger.info("图表显示成功")
            else:
                self.logger.warning("图表显示失败")
            
            return success
        except (ImportError, TypeError, ValueError, OSError) as e:
            self.logger.error("显示图表时出错: %s", e)
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
                self.logger.info("数据加载成功: %s", data_path)
            else:
                self._viewer.loaded_data = False
                self.logger.warning("数据加载失败: %s", data_path)
            
            return success
        except (IOError, TypeError, ValueError, OSError) as e:
            self.logger.error("加载数据时出错: %s", e)
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
        except (TypeError, AttributeError, OSError) as e:
            self.logger.error("清除数据时出错: %s", e)

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
        self.logger.debug("配置已更新: %s", config)

    def get_config(self) -> dict:
        """
        获取当前配置
        
        Returns:
            dict: 当前配置字典
        """
        return self._config.copy()

    @property
    def viewer(self) -> BatteryChartViewer:
        """
        获取原始的viewer实例
        
        Returns:
            BatteryChartViewer: 原始viewer实例
        """
        return self._viewer
