# -*- coding: utf-8 -*-
"""
可视化器控制器模块

本模块提供了可视化器的控制功能，负责初始化和配置可视化器实例。
"""

import os
import logging

# 导入可视化器模块
from battery_analysis.main import image_show


class VisualizerController:
    """
    可视化器控制器类
    负责初始化和配置可视化器实例
    """
    
    def __init__(self):
        """
        初始化可视化器控制器
        """
        self.visualizer = None
        
    def create_visualizer(self, xml_path=None):
        """
        创建可视化器实例
        
        Args:
            xml_path: 可选，指定XML文件路径
            
        Returns:
            image_show.FIGURE: 可视化器实例
        """
        try:
            if xml_path and xml_path != "" and xml_path != "Not provided":
                # 获取XML文件的目录路径
                test_profile_dir = os.path.dirname(xml_path)
                parent_dir = os.path.dirname(test_profile_dir)
                
                # 创建visualizer实例时传递数据路径
                self.visualizer = image_show.FIGURE(data_path=parent_dir)
            else:
                # 没有选择XML文件，创建空的visualizer实例
                self.visualizer = image_show.FIGURE()
                
            return self.visualizer
        except Exception as e:
            logging.error("创建可视化器时出错: %s", str(e))
            raise
    
    def show_figure(self):
        """
        显示可视化图表
        
        Raises:
            Exception: 如果可视化器未初始化
        """
        if not self.visualizer:
            raise Exception("可视化器未初始化")
            
        self.visualizer.plt_figure()
    
    def run_visualizer(self, xml_path=None):
        """
        运行可视化器的完整流程
        
        Args:
            xml_path: 可选，指定XML文件路径
        """
        self.create_visualizer(xml_path)
        self.show_figure()
