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
                self.logger.info("接收到XML路径: %s", xml_path)
                import os
                
                # 确保XML路径是绝对路径
                if not os.path.isabs(xml_path):
                    xml_path = os.path.abspath(xml_path)
                    self.logger.info("转换为绝对路径: %s", xml_path)
                
                # 检查XML路径是否存在
                if not os.path.exists(xml_path):
                    self.logger.warning("XML文件不存在: %s", xml_path)
                else:
                    self.logger.info("XML文件存在")
                
                # 获取XML所在目录
                test_profile_dir = os.path.dirname(xml_path)
                self.logger.info("XML所在目录: %s", test_profile_dir)
                
                # 检查XML所在目录是否存在
                if not os.path.exists(test_profile_dir):
                    self.logger.warning("XML所在目录不存在: %s", test_profile_dir)
                else:
                    self.logger.info("XML所在目录存在")
                
                # 获取XML所在目录的上一级目录
                parent_dir = os.path.dirname(test_profile_dir)
                self.logger.info("XML上一级目录: %s", parent_dir)
                
                # 检查XML上一级目录是否存在
                if not os.path.exists(parent_dir):
                    self.logger.warning("XML上一级目录不存在: %s", parent_dir)
                else:
                    self.logger.info("XML上一级目录存在")
                
                # 定义可能的分析结果目录名称
                analysis_dir_names = ["3_analysis results", "analysis results", "Analysis Results", "3_Analysis Results"]
                
                # 尝试在XML上一级目录中寻找分析结果目录
                analysis_results_dir = None
                for dir_name in analysis_dir_names:
                    analysis_dir = os.path.join(parent_dir, dir_name)
                    self.logger.info("尝试分析结果目录: %s", analysis_dir)
                    if os.path.exists(analysis_dir):
                        analysis_results_dir = analysis_dir
                        self.logger.info("找到分析结果目录: %s", analysis_results_dir)
                        break
                
                # 如果在XML上一级目录中没有找到，尝试在XML所在目录中寻找
                if not analysis_results_dir:
                    self.logger.info("在XML上一级目录中未找到分析结果目录，尝试在XML所在目录中寻找")
                    for dir_name in analysis_dir_names:
                        analysis_dir = os.path.join(test_profile_dir, dir_name)
                        self.logger.info("尝试分析结果目录: %s", analysis_dir)
                        if os.path.exists(analysis_dir):
                            analysis_results_dir = analysis_dir
                            self.logger.info("找到分析结果目录: %s", analysis_results_dir)
                            break
                
                # 如果找到分析结果目录，尝试获取最新的子目录
                if analysis_results_dir:
                    # 检查分析结果目录是否存在
                    if not os.path.exists(analysis_results_dir):
                        self.logger.warning("分析结果目录不存在: %s", analysis_results_dir)
                    else:
                        self.logger.info("分析结果目录存在")
                        
                        # 获取子目录列表
                        try:
                            subdirs = [d for d in os.listdir(analysis_results_dir) if os.path.isdir(os.path.join(analysis_results_dir, d))]
                            self.logger.info("分析结果目录中的子目录: %s", subdirs)
                            
                            if subdirs:
                                # 按修改时间排序，获取最新的子目录
                                latest_dir = max(subdirs, key=lambda d: os.path.getmtime(os.path.join(analysis_results_dir, d)))
                                latest_dir_path = os.path.join(analysis_results_dir, latest_dir)
                                self.logger.info("最新版本目录: %s", latest_dir_path)
                                
                                # 检查最新目录中是否有Info_Image.csv文件
                                info_image_csv = os.path.join(latest_dir_path, "Info_Image.csv")
                                self.logger.info("检查Info_Image.csv文件: %s", info_image_csv)
                                if os.path.exists(info_image_csv):
                                    self.logger.info("找到最新的Info_Image.csv文件: %s", info_image_csv)
                                    self._viewer.set_data_path(latest_dir_path)
                                    if self._viewer.load_data():
                                        self._viewer.loaded_data = True
                                        self.logger.info("成功从XML路径加载数据")
                                    else:
                                        self.logger.warning("数据加载失败")
                                else:
                                    self.logger.warning("最新版本目录中没有找到Info_Image.csv文件")
                                    # 尝试在分析结果目录的其他子目录中寻找Info_Image.csv文件
                                    for subdir in subdirs:
                                        subdir_path = os.path.join(analysis_results_dir, subdir)
                                        info_image_csv = os.path.join(subdir_path, "Info_Image.csv")
                                        if os.path.exists(info_image_csv):
                                            self.logger.info("在其他子目录中找到Info_Image.csv文件: %s", info_image_csv)
                                            self._viewer.set_data_path(subdir_path)
                                            if self._viewer.load_data():
                                                self._viewer.loaded_data = True
                                                self.logger.info("成功从其他子目录加载数据")
                                            else:
                                                self.logger.warning("数据加载失败")
                                            break
                            else:
                                self.logger.warning("分析结果目录中没有子目录")
                                # 尝试直接在分析结果目录中寻找Info_Image.csv文件
                                info_image_csv = os.path.join(analysis_results_dir, "Info_Image.csv")
                                if os.path.exists(info_image_csv):
                                    self.logger.info("在分析结果目录中找到Info_Image.csv文件: %s", info_image_csv)
                                    self._viewer.set_data_path(analysis_results_dir)
                                    if self._viewer.load_data():
                                        self._viewer.loaded_data = True
                                        self.logger.info("成功从分析结果目录加载数据")
                                    else:
                                        self.logger.warning("数据加载失败")
                        except Exception as e:
                            self.logger.error("处理分析结果目录时出错: %s", e)
                else:
                    self.logger.warning("未找到分析结果目录")
            
            # 如果提供了数据路径，加载数据
            elif data_path is not None:
                self.logger.info("接收到数据路径: %s", data_path)
                self._viewer.set_data_path(data_path)
                if self._viewer.load_data():
                    self._viewer.loaded_data = True
                    self.logger.info("成功从数据路径加载数据")
                else:
                    self.logger.warning("数据加载失败")
            
            # 其他情况（没有提供XML路径或数据路径），不加载任何数据，直接显示无数据
            else:
                self.logger.info("没有提供XML路径或数据路径，不加载任何数据")
                # 不设置loaded_data，让_viewer在plt_figure时显示无数据

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
