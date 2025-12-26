# -*- coding: utf-8 -*-
"""
可视化器控制器模块

本模块提供了可视化器的控制功能，负责初始化和配置可视化器实例。
"""

import os
import logging

# 导入可视化器模块
from battery_analysis.main import battery_chart_viewer


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
            battery_chart_viewer.BatteryChartViewer: 可视化器实例
        """
        try:
            # 强制设置Matplotlib使用QtAgg后端
            import matplotlib
            if matplotlib.get_backend() != 'QtAgg':
                logging.info(f"当前Matplotlib后端: {matplotlib.get_backend()}, 切换到QtAgg后端")
                matplotlib.use('QtAgg')
            
            data_path = None
            
            if xml_path and xml_path != "" and xml_path != "Not provided":
                logging.info(f"接收到的XML路径: {xml_path}")
                
                # 将相对路径转换为绝对路径
                xml_path = os.path.abspath(xml_path)
                logging.info(f"转换为绝对路径: {xml_path}")
                
                # 获取XML所在目录
                test_profile_dir = os.path.dirname(xml_path)
                logging.info(f"XML所在目录: {test_profile_dir}")
                
                # 定义可能的分析结果目录名称
                analysis_dir_names = ["3_analysis results", "analysis results", "Analysis Results", "3_Analysis Results"]
                
                # 尝试在不同位置寻找分析结果目录
                possible_paths = []
                
                # 1. XML所在目录的父目录
                parent_dir = os.path.dirname(test_profile_dir)
                possible_paths.extend([os.path.join(parent_dir, dir_name) for dir_name in analysis_dir_names])
                
                # 2. XML所在目录
                possible_paths.extend([os.path.join(test_profile_dir, dir_name) for dir_name in analysis_dir_names])
                
                # 3. 当前工作目录
                possible_paths.extend([os.path.join(os.getcwd(), dir_name) for dir_name in analysis_dir_names])
                
                # 4. 项目根目录
                current_file_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))
                possible_paths.extend([os.path.join(project_root, dir_name) for dir_name in analysis_dir_names])
                
                # 尝试找到存在的分析结果目录
                analysis_results_dir = None
                for path in possible_paths:
                    if os.path.exists(path):
                        analysis_results_dir = path
                        logging.info(f"找到分析结果目录: {analysis_results_dir}")
                        break
                
                if analysis_results_dir:
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
                            for subdir in subdirs:
                                subdir_path = os.path.join(analysis_results_dir, subdir)
                                csv_path = os.path.join(subdir_path, "Info_Image.csv")
                                if os.path.exists(csv_path):
                                    logging.info(f"找到包含Info_Image.csv的目录: {subdir_path}")
                                    data_path = subdir_path
                                    break
                    else:
                        logging.error("分析结果目录中没有子目录")
                        # 检查分析结果目录本身是否包含Info_Image.csv
                        info_image_csv = os.path.join(analysis_results_dir, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            logging.info(f"在分析结果目录中找到Info_Image.csv文件: {info_image_csv}")
                            data_path = analysis_results_dir
                else:
                    logging.error("未找到分析结果目录，尝试的路径:")
                    for path in possible_paths:
                        logging.error(f"  - {path}")
            
            # 直接在当前目录查找Info_Image.csv
            if not data_path:
                current_dir = os.getcwd()
                info_image_csv = os.path.join(current_dir, "Info_Image.csv")
                if os.path.exists(info_image_csv):
                    logging.info(f"在当前目录找到Info_Image.csv文件: {info_image_csv}")
                    data_path = current_dir
            
            # 查找当前目录下的3_analysis results目录
            if not data_path:
                analysis_results_dir = os.path.join(os.getcwd(), "3_analysis results")
                if os.path.exists(analysis_results_dir):
                    logging.info(f"找到分析结果目录: {analysis_results_dir}")
                    # 查找最新的子目录
                    subdirs = [d for d in os.listdir(analysis_results_dir) if os.path.isdir(os.path.join(analysis_results_dir, d))]
                    if subdirs:
                        # 按修改时间排序，获取最新的子目录
                        latest_dir = max(subdirs, key=lambda d: os.path.getmtime(os.path.join(analysis_results_dir, d)))
                        latest_dir_path = os.path.join(analysis_results_dir, latest_dir)
                        logging.info(f"最新的分析结果子目录: {latest_dir_path}")
                        # 检查是否包含Info_Image.csv
                        info_image_csv = os.path.join(latest_dir_path, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            logging.info(f"在最新的分析结果子目录中找到Info_Image.csv文件: {info_image_csv}")
                            data_path = latest_dir_path
                        else:
                            # 检查所有子目录
                            for subdir in subdirs:
                                subdir_path = os.path.join(analysis_results_dir, subdir)
                                info_image_csv = os.path.join(subdir_path, "Info_Image.csv")
                                if os.path.exists(info_image_csv):
                                    logging.info(f"在分析结果子目录中找到Info_Image.csv文件: {info_image_csv}")
                                    data_path = subdir_path
                                    break
                    else:
                        # 检查分析结果目录本身
                        info_image_csv = os.path.join(analysis_results_dir, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            logging.info(f"在分析结果目录中找到Info_Image.csv文件: {info_image_csv}")
                            data_path = analysis_results_dir
            
            # 查找项目根目录下的所有Info_Image.csv文件
            if not data_path:
                current_file_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))
                logging.info(f"在项目根目录查找Info_Image.csv: {project_root}")
                
                # 搜索整个项目目录
                for root, dirs, files in os.walk(project_root):
                    if "Info_Image.csv" in files:
                        info_image_csv = os.path.join(root, "Info_Image.csv")
                        logging.info(f"在项目中找到Info_Image.csv文件: {info_image_csv}")
                        data_path = root
                        break
            
            if data_path:
                # 使用找到的数据路径
                self.visualizer = battery_chart_viewer.BatteryChartViewer(data_path=data_path)
                logging.info(f"成功创建可视化器实例，数据路径: {data_path}")
            else:
                logging.warning("未找到任何包含Info_Image.csv的目录，将创建空的可视化器实例")
                # 如果找不到有效数据路径，创建空的visualizer实例
                self.visualizer = battery_chart_viewer.BatteryChartViewer()

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
        # 更彻底地清理Matplotlib状态，确保新的可视化器能正常工作
        import matplotlib
        import matplotlib.pyplot as plt
        
        # 重置Matplotlib的内部状态（不关闭当前图表，避免事件绑定失效）
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        
        # 重新配置中文字体支持，避免重置后丢失
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial', 'Times New Roman']
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 确保使用正确的后端
        if matplotlib.get_backend() != 'QtAgg':
            logging.info(f"当前Matplotlib后端: {matplotlib.get_backend()}, 切换到QtAgg后端")
            matplotlib.use('QtAgg')
        
        self.create_visualizer(xml_path)
        self.show_figure()
