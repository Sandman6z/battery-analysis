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
                logging.info(f"接收到的XML路径: {xml_path}")
                
                # 将相对路径转换为绝对路径
                xml_path = os.path.abspath(xml_path)
                logging.info(f"转换为绝对路径: {xml_path}")
                
                # 获取XML所在目录
                test_profile_dir = os.path.dirname(xml_path)
                logging.info(f"XML所在目录: {test_profile_dir}")
                
                # 获取XML所在目录的上级目录
                parent_dir = os.path.dirname(test_profile_dir)
                logging.info(f"XML所在目录的上级目录: {parent_dir}")
                
                # 在上级目录中寻找3_analysis results目录
                analysis_results_dir = os.path.join(parent_dir, "3_analysis results")
                logging.info(f"分析结果目录: {analysis_results_dir}")
                
                # 找到最新版本的子目录
                if os.path.exists(analysis_results_dir):
                    # 获取所有子目录
                    subdirs = [d for d in os.listdir(analysis_results_dir) 
                             if os.path.isdir(os.path.join(analysis_results_dir, d))]
                    
                    if subdirs:
                        # 按修改时间排序，获取最新的子目录
                        latest_dir = max(subdirs, key=lambda d: os.path.getmtime(
                            os.path.join(analysis_results_dir, d)))
                        latest_dir_path = os.path.join(analysis_results_dir, latest_dir)
                        logging.info(f"最新版本目录: {latest_dir_path}")
                        
                        # 检查最新目录中是否有Info_Image.csv文件
                        info_image_csv = os.path.join(latest_dir_path, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            logging.info(f"找到最新的Info_Image.csv文件: {info_image_csv}")
                            data_path = latest_dir_path
                        else:
                            logging.warning(f"最新版本目录中没有找到Info_Image.csv文件: {latest_dir_path}")
                            # 如果最新版本目录中没有文件，尝试找到第一个包含Info_Image.csv的目录
                            data_path = None
                            for subdir in subdirs:
                                subdir_path = os.path.join(analysis_results_dir, subdir)
                                csv_path = os.path.join(subdir_path, "Info_Image.csv")
                                if os.path.exists(csv_path):
                                    logging.info(f"找到包含Info_Image.csv的目录: {subdir_path}")
                                    data_path = subdir_path
                                    break
                        
                        if data_path:
                            # 使用找到的最新分析结果目录作为数据路径
                            self.visualizer = image_show.FIGURE(data_path=data_path)
                            logging.info(f"成功创建可视化器实例，数据路径: {data_path}")
                        else:
                            logging.error("在分析结果目录中没有找到任何包含Info_Image.csv的子目录")
                            # 如果找不到有效数据路径，创建空的visualizer实例
                            self.visualizer = image_show.FIGURE()
                    else:
                        logging.error("分析结果目录中没有子目录")
                        # 如果没有子目录，创建空的visualizer实例
                        self.visualizer = image_show.FIGURE()
                else:
                    logging.error("分析结果目录不存在: %s", analysis_results_dir)
                    # 如果分析结果目录不存在，创建空的visualizer实例
                    self.visualizer = image_show.FIGURE()
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
