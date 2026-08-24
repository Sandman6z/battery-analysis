# -*- coding: utf-8 -*-
"""
可视化器工厂模块

使用工厂模式创建可视化器实例，实现依赖倒置
"""

import logging
import os
from typing import Optional, Type, Dict, Any
from battery_analysis.main.interfaces.ivisualizer import IVisualizer


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
            raise ValueError(f"Class {visualizer_class.__name__} must implement the IVisualizer interface")
        
        self._visualizers[name] = visualizer_class
        self.logger.debug("Registered visualizer: %s -> %s", name, visualizer_class.__name__)

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
        
        # 延迟导入，避免 import visualizer_factory 时触发 matplotlib 等 heavy 导入
        from battery_analysis.main.battery_chart_viewer import BatteryChartViewer
        self._viewer = BatteryChartViewer(data_path=None, auto_search=False)
        self._config = {}
        
        # 如果提供了有效的数据路径，先设置路径但不自动加载
        if data_path and os.path.exists(data_path):
            self._viewer.set_data_path(data_path)
            # 不自动加载数据，由调用者决定何时加载
    

        
    def show_figure(self, data_path: Optional[str] = None, xml_path: Optional[str] = None) -> bool:
        """
        显示图表
        
        Args:
            data_path: 可选的数据路径
            xml_path: 可选的XML文件路径
            
        Returns:
            bool: 是否成功显示
        """
        try:
            # 重置viewer状态
            self._viewer.loaded_data = False
            
            # 只有当提供了XML路径或数据路径时才加载数据
            if xml_path is not None and xml_path:
                import os

                # 确保XML路径是绝对路径
                if not os.path.isabs(xml_path):
                    xml_path = os.path.abspath(xml_path)

                # 检查XML路径是否存在
                if not os.path.exists(xml_path):
                    self.logger.warning("XML file does not exist: %s", xml_path)

                # 获取XML所在目录
                test_profile_dir = os.path.dirname(xml_path)

                # 检查XML所在目录是否存在
                if not os.path.exists(test_profile_dir):
                    self.logger.warning("XML directory does not exist: %s", test_profile_dir)

                # 获取XML所在目录的上一级目录
                parent_dir = os.path.dirname(test_profile_dir)

                # 检查XML上一级目录是否存在
                if not os.path.exists(parent_dir):
                    self.logger.warning("XML parent directory does not exist: %s", parent_dir)

                # 定义可能的分析结果目录名称
                analysis_dir_names = ["3_analysis results", "analysis results", "Analysis Results", "3_Analysis Results"]

                # 尝试在XML上一级目录中寻找分析结果目录
                analysis_results_dir = None
                for dir_name in analysis_dir_names:
                    analysis_dir = os.path.join(parent_dir, dir_name)
                    if os.path.exists(analysis_dir):
                        analysis_results_dir = analysis_dir
                        break

                # 如果在XML上一级目录中没有找到，尝试在XML所在目录中寻找
                if not analysis_results_dir:
                    for dir_name in analysis_dir_names:
                        analysis_dir = os.path.join(test_profile_dir, dir_name)
                        if os.path.exists(analysis_dir):
                            analysis_results_dir = analysis_dir
                            break
                
                # 如果找到分析结果目录，尝试获取最新的子目录
                if analysis_results_dir:
                    # 检查分析结果目录是否存在
                    if not os.path.exists(analysis_results_dir):
                        self.logger.warning("Analysis results directory does not exist: %s", analysis_results_dir)
                    else:
                        # 获取子目录列表
                        try:
                            subdirs = [d for d in os.listdir(analysis_results_dir) if os.path.isdir(os.path.join(analysis_results_dir, d))]

                            if subdirs:
                                # 按修改时间排序，获取最新的子目录
                                latest_dir = max(subdirs, key=lambda d: os.path.getmtime(os.path.join(analysis_results_dir, d)))
                                latest_dir_path = os.path.join(analysis_results_dir, latest_dir)

                                # 检查最新目录中是否有Info_Image.csv文件
                                info_image_csv = os.path.join(latest_dir_path, "Info_Image.csv")
                                if os.path.exists(info_image_csv):
                                    self._viewer.set_data_path(latest_dir_path)
                                    if self._viewer.load_data():
                                        self._viewer.loaded_data = True
                                        self.logger.info("Successfully loaded data from XML path")
                                    else:
                                        self.logger.warning("Data loading failed")
                                else:
                                    self.logger.warning("Info_Image.csv file not found in the latest version directory")
                                    # 尝试在分析结果目录的其他子目录中寻找Info_Image.csv文件
                                    for subdir in subdirs:
                                        subdir_path = os.path.join(analysis_results_dir, subdir)
                                        info_image_csv = os.path.join(subdir_path, "Info_Image.csv")
                                        if os.path.exists(info_image_csv):
                                            self._viewer.set_data_path(subdir_path)
                                            if self._viewer.load_data():
                                                self._viewer.loaded_data = True
                                                self.logger.info("Successfully loaded data from another subdirectory")
                                            else:
                                                self.logger.warning("Data loading failed")
                                            break
                            else:
                                self.logger.warning("No subdirectories in the analysis results directory")
                                # 尝试直接在分析结果目录中寻找Info_Image.csv文件
                                info_image_csv = os.path.join(analysis_results_dir, "Info_Image.csv")
                                if os.path.exists(info_image_csv):
                                    self._viewer.set_data_path(analysis_results_dir)
                                    if self._viewer.load_data():
                                        self._viewer.loaded_data = True
                                        self.logger.info("Successfully loaded data from analysis results directory")
                                    else:
                                        self.logger.warning("Data loading failed")
                        except Exception as e:
                            self.logger.error("Error processing analysis results directory: %s", e)
                else:
                    self.logger.warning("Analysis results directory not found")

            # 如果提供了数据路径，加载数据
            elif data_path is not None:
                self._viewer.set_data_path(data_path)
                if self._viewer.load_data():
                    self._viewer.loaded_data = True
                    self.logger.info("Successfully loaded data from data path")
                else:
                    self.logger.warning("Data loading failed")

            # 其他情况（没有提供XML路径或数据路径），不加载任何数据，直接显示无数据
            # 不设置loaded_data，让_viewer在plt_figure时显示无数据

            # 创建可视化
            success = self._viewer.plt_figure()
            if not success:
                self.logger.warning("Chart display failed")
            
            return success
        except (ImportError, TypeError, ValueError, OSError) as e:
            self.logger.error("Error displaying chart: %s", e)
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
            if not success:
                self._viewer.loaded_data = False
                self.logger.warning("Data loading failed: %s", data_path)
            else:
                self._viewer.loaded_data = True
            
            return success
        except (IOError, TypeError, ValueError, OSError) as e:
            self.logger.error("Error loading data: %s", e)
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
        except (TypeError, AttributeError, OSError) as e:
            self.logger.error("Error clearing data: %s", e)

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
        self.logger.debug("Configuration updated: %s", config)

    def get_config(self) -> dict:
        """
        获取当前配置
        
        Returns:
            dict: 当前配置字典
        """
        return self._config.copy()

    @property
    def viewer(self) -> "BatteryChartViewer":  # noqa: F821 延迟 import，pyflakes 误报
        """
        获取原始的viewer实例
        
        Returns:
            BatteryChartViewer: 原始viewer实例
        """
        return self._viewer
