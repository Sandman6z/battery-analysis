# -*- coding: utf-8 -*-
"""
可视化器控制器模块

本模块提供了可视化器的控制功能，负责初始化和配置可视化器实例。
已优化为支持多种环境（开发、IDE、容器、PyInstaller打包）
"""

import os
import logging

# 导入可视化器模块
from battery_analysis.main import battery_chart_viewer
from battery_analysis.utils.environment_utils import get_environment_detector, EnvironmentType


class VisualizerController:
    """
    可视化器控制器类
    负责初始化和配置可视化器实例
    """
    
    def __init__(self):
        """
        初始化可视化器控制器
        """
        # 初始化环境检测器
        self.env_detector = get_environment_detector()
        self.env_info = self.env_detector.get_environment_info()
        
        self.visualizer = None
        self.logger = logging.getLogger(__name__)
        
        # 环境适配处理
        self._handle_environment_adaptation()

    def _handle_environment_adaptation(self):
        """
        处理环境适配逻辑
        """
        env_type = self.env_info['environment_type']
        
        # 根据环境类型进行适配
        if env_type == EnvironmentType.IDE:
            self.logger.debug("IDE环境：调整可视化行为以适应开发环境")
            self._adapt_for_ide_environment()
        elif env_type == EnvironmentType.CONTAINER:
            self.logger.debug("容器环境：调整可视化行为以适应容器环境")
            self._adapt_for_container_environment()
        elif env_type == EnvironmentType.PRODUCTION:
            self.logger.debug("生产环境：优化可视化性能")
            self._adapt_for_production_environment()
        
        # GUI可用性检查
        if not self.env_info['gui_available']:
            self.logger.warning("GUI环境不可用，可视化功能可能受限")
            self._handle_gui_unavailable()

    def _adapt_for_ide_environment(self):
        """
        IDE环境适配
        """
        # 在IDE中通常没有显示，添加调试信息
        self.logger.debug("在IDE环境中运行，某些可视化功能可能受限")
        
        # 在IDE环境中，可能需要更严格的错误处理
        self.ide_mode = True

    def _adapt_for_container_environment(self):
        """
        容器环境适配
        """
        self.logger.debug("在容器环境中运行，调整路径和资源管理")
        
        # 容器环境中的资源路径可能不同
        self.container_mode = True

    def _adapt_for_production_environment(self):
        """
        生产环境适配
        """
        self.logger.debug("在生产环境中运行，优化可视化性能")
        
        # 生产环境中启用更多优化
        self.production_mode = True

    def _handle_gui_unavailable(self):
        """
        处理GUI不可用的情况
        """
        self.logger.error("GUI环境不可用，可视化功能将受限")
        # 在GUI不可用时，可以考虑生成静态图表或保存图片
        
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
                logging.info("当前Matplotlib后端: %s, 切换到QtAgg后端", matplotlib.get_backend())
                matplotlib.use('QtAgg')
            
            data_path = None
            
            if xml_path and xml_path != "" and xml_path != "Not provided":
                logging.info("接收到的XML路径: %s", xml_path)
                
                # 将相对路径转换为绝对路径
                xml_path = os.path.abspath(xml_path)
                logging.info("转换为绝对路径: %s", xml_path)
                
                # 获取XML所在目录
                test_profile_dir = os.path.dirname(xml_path)
                logging.info("XML所在目录: %s", test_profile_dir)
                
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
                        logging.info("找到分析结果目录: %s", analysis_results_dir)
                        break
                
                if analysis_results_dir:
                    # 获取所有子目录
                    subdirs = [d for d in os.listdir(analysis_results_dir) 
                             if os.path.isdir(os.path.join(analysis_results_dir, d))]
                    
                    if subdirs:
                        # 按修改when间排序，获取最新的子目录
                        latest_dir = max(subdirs, key=lambda d: os.path.getmtime(
                            os.path.join(analysis_results_dir, d)))
                        latest_dir_path = os.path.join(analysis_results_dir, latest_dir)
                        logging.info("最新版本目录: %s", latest_dir_path)
                        
                        # 检查最新目录中是否有Info_Image.csv文件
                        info_image_csv = os.path.join(latest_dir_path, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            logging.info("找到最新的Info_Image.csv文件: %s", info_image_csv)
                            data_path = latest_dir_path
                        else:
                            logging.warning("最新版本目录中没有找到Info_Image.csv文件: %s", latest_dir_path)
                            # 如果最新版本目录中没有文件，尝试找到第一个包含Info_Image.csv的目录
                            for subdir in subdirs:
                                subdir_path = os.path.join(analysis_results_dir, subdir)
                                csv_path = os.path.join(subdir_path, "Info_Image.csv")
                                if os.path.exists(csv_path):
                                    logging.info("找到包含Info_Image.csv的目录: %s", subdir_path)
                                    data_path = subdir_path
                                    break
                    else:
                        logging.error("分析结果目录中没有子目录")
                        # 检查分析结果目录本身是否包含Info_Image.csv
                        info_image_csv = os.path.join(analysis_results_dir, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            logging.info("在分析结果目录中找到Info_Image.csv文件: %s", info_image_csv)
                            data_path = analysis_results_dir
                else:
                    logging.error("未找到分析结果目录，尝试的路径:")
                    for path in possible_paths:
                        logging.error("  - %s", path)
            
            # 直接在当前目录查找Info_Image.csv
            if not data_path:
                current_dir = os.getcwd()
                info_image_csv = os.path.join(current_dir, "Info_Image.csv")
                if os.path.exists(info_image_csv):
                    logging.info("在当前目录找到Info_Image.csv文件: %s", info_image_csv)
                    data_path = current_dir
            
            # 检查传入的路径本身是否包含Info_Image.csv
            if not data_path and xml_path:
                test_path = xml_path if os.path.isdir(xml_path) else os.path.dirname(xml_path)
                info_image_csv = os.path.join(test_path, "Info_Image.csv")
                if os.path.exists(info_image_csv):
                    logging.info("在指定路径找到Info_Image.csv文件: %s", info_image_csv)
                    data_path = test_path
            
            # 查找当前目录下的3_analysis results目录
            if not data_path:
                analysis_results_dir = os.path.join(os.getcwd(), "3_analysis results")
                if os.path.exists(analysis_results_dir):
                    logging.info("找到分析结果目录: %s", analysis_results_dir)
                    # 查找最新的子目录
                    subdirs = [d for d in os.listdir(analysis_results_dir) if os.path.isdir(os.path.join(analysis_results_dir, d))]
                    if subdirs:
                        # 按修改when间排序，获取最新的子目录
                        latest_dir = max(subdirs, key=lambda d: os.path.getmtime(os.path.join(analysis_results_dir, d)))
                        latest_dir_path = os.path.join(analysis_results_dir, latest_dir)
                        logging.info("最新的分析结果子目录: %s", latest_dir_path)
                        # 检查是否包含Info_Image.csv
                        info_image_csv = os.path.join(latest_dir_path, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            logging.info("在最新的分析结果子目录中找到Info_Image.csv文件: %s", info_image_csv)
                            data_path = latest_dir_path
                        else:
                            # 检查所有子目录
                            for subdir in subdirs:
                                subdir_path = os.path.join(analysis_results_dir, subdir)
                                info_image_csv = os.path.join(subdir_path, "Info_Image.csv")
                                if os.path.exists(info_image_csv):
                                    logging.info("在分析结果子目录中找到Info_Image.csv文件: %s", info_image_csv)
                                    data_path = subdir_path
                                    break
                    else:
                        # 检查分析结果目录本身
                        info_image_csv = os.path.join(analysis_results_dir, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            logging.info("在分析结果目录中找到Info_Image.csv文件: %s", info_image_csv)
                            data_path = analysis_results_dir
            
            # 查找项目根目录下的所有Info_Image.csv文件
            if not data_path:
                # 使用环境检测器获取正确的项目根目录
                project_root = self.env_detector.get_project_root()
                logging.info("在项目根目录查找Info_Image.csv: %s", project_root)
                
                # 搜索整个项目目录
                for root, dirs, files in os.walk(project_root):
                    if "Info_Image.csv" in files:
                        info_image_csv = os.path.join(root, "Info_Image.csv")
                        logging.info("在项目中找到Info_Image.csv文件: %s", info_image_csv)
                        data_path = root
                        break
            
            if data_path:
                # 使用找到的数据路径
                self.visualizer = battery_chart_viewer.BatteryChartViewer(data_path=data_path)
                logging.info("成功创建可视化器实例，数据路径: %s", data_path)
            else:
                logging.warning("未找到任何包含Info_Image.csv的目录，将创建空的可视化器实例")
                # 如果找不到有效数据路径，创建空的visualizer实例
                self.visualizer = battery_chart_viewer.BatteryChartViewer()

            return self.visualizer
        except Exception as e:
            logging.error("创建可视化器whenerror occurred: %s", str(e))
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
        # 环境检测和适配
        self._configure_matplotlib_for_environment()
        
        try:
            self.create_visualizer(xml_path)
            
            # 根据环境类型决定是否显示图形
            if self.env_info['gui_available']:
                self.show_figure()
            else:
                self.logger.info("GUI不可用，生成静态图表文件")
                self._generate_static_chart()
                
        except Exception as e:
            self.logger.error("运行可视化器失败: %s", e)
            raise

    def _configure_matplotlib_for_environment(self):
        """
        根据环境配置Matplotlib
        """
        import matplotlib
        import matplotlib.pyplot as plt
        
        # 重置Matplotlib的内部状态（不关闭当前图表，避免事件绑定失效）
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        
        # 重新配置中文字体支持，避免重置后丢失
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial', 'Times New Roman']
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 根据环境选择合适的后端
        env_type = self.env_info['environment_type']
        
        if env_type == EnvironmentType.IDE:
            # IDE环境可能不支持GUI显示
            if not self.env_info['gui_available']:
                self.logger.debug("IDE环境且无GUI，使用Agg后端生成静态图表")
                matplotlib.use('Agg')
            else:
                self.logger.debug("IDE环境且有GUI，尝试使用QtAgg后端")
                if matplotlib.get_backend() != 'QtAgg':
                    matplotlib.use('QtAgg')
        elif env_type == EnvironmentType.CONTAINER:
            # 容器环境通常使用无头模式
            self.logger.debug("容器环境，使用Agg后端")
            matplotlib.use('Agg')
        else:
            # 生产环境和其他环境使用QtAgg后端
            if matplotlib.get_backend() != 'QtAgg':
                self.logger.debug("切换Matplotlib后端到QtAgg (当前: %s)", matplotlib.get_backend())
                matplotlib.use('QtAgg')

    def _generate_static_chart(self):
        """
        生成静态图表文件（用于无GUI环境）
        """
        try:
            if not self.visualizer:
                self.logger.error("可视化器未初始化，无法生成静态图表")
                return
            
            # 生成静态图表文件
            import matplotlib.pyplot as plt
            
            # 保存为PNG文件
            output_path = self.env_detector.get_resource_path("output")
            output_path.mkdir(parents=True, exist_ok=True)
            
            chart_file = output_path / "battery_analysis_chart.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            
            self.logger.info("静态图表已保存到: %s", chart_file)
            
            # 同时保存为PDF文件（矢量格式）
            pdf_file = output_path / "battery_analysis_chart.pdf"
            plt.savefig(pdf_file, bbox_inches='tight')
            
            self.logger.info("PDF图表已保存到: %s", pdf_file)
            
        except Exception as e:
            self.logger.error("生成静态图表失败: %s", e)
