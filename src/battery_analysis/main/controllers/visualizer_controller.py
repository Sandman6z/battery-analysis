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
from battery_analysis.utils.constants import CN_FONT_LIST


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
        
        # 初始化环境适配属性
        self.ide_mode = False
        self.container_mode = False
        self.production_mode = False
        
        # 环境适配处理
        self._handle_environment_adaptation()

    def _handle_environment_adaptation(self):
        """
        处理环境适配逻辑
        """
        env_type = self.env_info['environment_type']
        
        # 根据环境类型进行适配
        if env_type == EnvironmentType.IDE:
            self.logger.debug("IDE environment: adjusting visualization behavior for development environment")
            self._adapt_for_ide_environment()
        elif env_type == EnvironmentType.CONTAINER:
            self.logger.debug("Container environment: adjusting visualization behavior for container environment")
            self._adapt_for_container_environment()
        elif env_type == EnvironmentType.PRODUCTION:
            self.logger.debug("Production environment: optimizing visualization performance")
            self._adapt_for_production_environment()
        
        # GUI可用性检查
        if not self.env_info['gui_available']:
            self.logger.warning("GUI environment is unavailable; visualization features may be limited")
            self._handle_gui_unavailable()

    def _adapt_for_ide_environment(self):
        """
        IDE环境适配
        """
        # 在IDE中通常没有显示，添加调试信息
        self.logger.debug("Running in IDE environment; some visualization features may be limited")
        
        # 在IDE环境中，可能需要更严格的错误处理
        self.ide_mode = True

    def _adapt_for_container_environment(self):
        """
        容器环境适配
        """
        self.logger.debug("Running in container environment; adjusting path and resource management")
        
        # 容器环境中的资源路径可能不同
        self.container_mode = True

    def _adapt_for_production_environment(self):
        """
        生产环境适配
        """
        self.logger.debug("Running in production environment; optimizing visualization performance")
        
        # 生产环境中启用更多优化
        self.production_mode = True

    def _handle_gui_unavailable(self):
        """
        处理GUI不可用的情况
        """
        self.logger.error("GUI environment is unavailable; visualization features will be limited")
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
            # 释放旧的可视化器实例
            if hasattr(self, 'visualizer') and self.visualizer is not None:
                logging.info("Releasing the previous visualizer instance")
                try:
                    # 关闭图表窗口
                    if hasattr(self.visualizer, 'current_fig') and self.visualizer.current_fig is not None:
                        import matplotlib.pyplot as plt
                        plt.close(self.visualizer.current_fig)
                        self.visualizer.current_fig = None
                    
                    # 清理Matplotlib状态
                    if hasattr(self.visualizer, '_cleanup_matplotlib_state'):
                        self.visualizer._cleanup_matplotlib_state()
                    
                    # 释放数据资源
                    if hasattr(self.visualizer, 'listPlt'):
                        try:
                            for c in range(len(self.visualizer.listPlt)):
                                if len(self.visualizer.listPlt[c]) >= 4:
                                    self.visualizer.listPlt[c][0].clear()  # 充电数据
                                    self.visualizer.listPlt[c][1].clear()  # 电压数据
                                    self.visualizer.listPlt[c][2].clear()  # 过滤后充电数据
                                    self.visualizer.listPlt[c][3].clear()  # 过滤后电压数据
                        except Exception as e:
                            logging.error("Error releasing data resources: %s", e)
                    
                    # 清理引用
                    self.visualizer = None
                    logging.info("Previous visualizer instance released successfully")
                except Exception as e:
                    logging.error("Error releasing the previous visualizer instance: %s", e)
            
            # 强制设置Matplotlib使用QtAgg后端
            import matplotlib
            if matplotlib.get_backend() != 'QtAgg':
                logging.info("Current Matplotlib backend: %s, switching to QtAgg backend", matplotlib.get_backend())
                matplotlib.use('QtAgg')
            
            data_path = None
            
            if xml_path and xml_path != "" and xml_path != "Not provided":
                xml_path = os.path.abspath(xml_path)
                test_profile_dir = os.path.dirname(xml_path)
                analysis_dir_names = ["3_analysis results", "analysis results", "Analysis Results", "3_Analysis Results"]
                possible_paths = []
                parent_dir = os.path.dirname(test_profile_dir)
                possible_paths.extend([os.path.join(parent_dir, dir_name) for dir_name in analysis_dir_names])
                possible_paths.extend([os.path.join(test_profile_dir, dir_name) for dir_name in analysis_dir_names])
                possible_paths.extend([os.path.join(os.getcwd(), dir_name) for dir_name in analysis_dir_names])
                current_file_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))
                possible_paths.extend([os.path.join(project_root, dir_name) for dir_name in analysis_dir_names])
                analysis_results_dir = None
                for path in possible_paths:
                    if os.path.exists(path):
                        analysis_results_dir = path
                        break
                if analysis_results_dir:
                    subdirs = [d for d in os.listdir(analysis_results_dir)
                             if os.path.isdir(os.path.join(analysis_results_dir, d))]
                    if subdirs:
                        latest_dir = max(subdirs, key=lambda d: os.path.getmtime(
                            os.path.join(analysis_results_dir, d)))
                        latest_dir_path = os.path.join(analysis_results_dir, latest_dir)
                        info_image_csv = os.path.join(latest_dir_path, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            data_path = latest_dir_path
                        else:
                            for subdir in subdirs:
                                subdir_path = os.path.join(analysis_results_dir, subdir)
                                csv_path = os.path.join(subdir_path, "Info_Image.csv")
                                if os.path.exists(csv_path):
                                    data_path = subdir_path
                                    break
                    else:
                        info_image_csv = os.path.join(analysis_results_dir, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            data_path = analysis_results_dir

            if not data_path:
                info_image_csv = os.path.join(os.getcwd(), "Info_Image.csv")
                if os.path.exists(info_image_csv):
                    data_path = os.getcwd()

            if not data_path and xml_path:
                test_path = xml_path if os.path.isdir(xml_path) else os.path.dirname(xml_path)
                info_image_csv = os.path.join(test_path, "Info_Image.csv")
                if os.path.exists(info_image_csv):
                    data_path = test_path

            if not data_path:
                analysis_results_dir = os.path.join(os.getcwd(), "3_analysis results")
                if os.path.exists(analysis_results_dir):
                    subdirs = [d for d in os.listdir(analysis_results_dir) if os.path.isdir(os.path.join(analysis_results_dir, d))]
                    if subdirs:
                        latest_dir = max(subdirs, key=lambda d: os.path.getmtime(os.path.join(analysis_results_dir, d)))
                        latest_dir_path = os.path.join(analysis_results_dir, latest_dir)
                        info_image_csv = os.path.join(latest_dir_path, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            data_path = latest_dir_path
                        else:
                            for subdir in subdirs:
                                subdir_path = os.path.join(analysis_results_dir, subdir)
                                info_image_csv = os.path.join(subdir_path, "Info_Image.csv")
                                if os.path.exists(info_image_csv):
                                    data_path = subdir_path
                                    break
                    else:
                        info_image_csv = os.path.join(analysis_results_dir, "Info_Image.csv")
                        if os.path.exists(info_image_csv):
                            data_path = analysis_results_dir

            if not data_path:
                project_root = self.env_detector.get_project_root()
                for root, dirs, files in os.walk(project_root):
                    if "Info_Image.csv" in files:
                        data_path = root
                        break

            if data_path:
                self.visualizer = battery_chart_viewer.BatteryChartViewer(data_path=data_path)
                logging.info("Visualizer instance created, data path: %s", data_path)
            else:
                logging.warning("No directory containing Info_Image.csv found; creating an empty visualizer instance")
                self.visualizer = battery_chart_viewer.BatteryChartViewer()

            return self.visualizer
        except (ImportError, AttributeError, TypeError, OSError, ValueError, RuntimeError) as e:
            logging.error("Error creating visualizer: %s", str(e))
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
                self.logger.info("GUI unavailable; generating static chart file")
                self._generate_static_chart()
                
        except (ImportError, AttributeError, TypeError, OSError, ValueError, RuntimeError) as e:
            self.logger.error("Failed to run visualizer: %s", e)
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
        matplotlib.rcParams['font.sans-serif'] = CN_FONT_LIST
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 根据环境选择合适的后端
        env_type = self.env_info['environment_type']
        
        if env_type == EnvironmentType.IDE:
            # IDE环境可能不支持GUI显示
            if not self.env_info['gui_available']:
                self.logger.debug("IDE environment without GUI; using Agg backend to generate static charts")
                matplotlib.use('Agg')
            else:
                self.logger.debug("IDE environment with GUI; attempting to use QtAgg backend")
                if matplotlib.get_backend() != 'QtAgg':
                    matplotlib.use('QtAgg')
        elif env_type == EnvironmentType.CONTAINER:
            # 容器环境通常使用无头模式
            self.logger.debug("Container environment; using Agg backend")
            matplotlib.use('Agg')
        else:
            # 生产环境和其他环境使用QtAgg后端
            if matplotlib.get_backend() != 'QtAgg':
                self.logger.debug("Switching Matplotlib backend to QtAgg (current: %s)", matplotlib.get_backend())
                matplotlib.use('QtAgg')

    def _generate_static_chart(self):
        """
        生成静态图表文件（用于无GUI环境）
        """
        try:
            if not self.visualizer:
                self.logger.error("Visualizer not initialized; cannot generate static chart")
                return
            
            # 生成静态图表文件
            import matplotlib.pyplot as plt
            
            # 保存为PNG文件
            output_path = self.env_detector.get_resource_path("output")
            output_path.mkdir(parents=True, exist_ok=True)
            
            chart_file = output_path / "battery_analysis_chart.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            
            self.logger.info("Static chart saved to: %s", chart_file)
            
            # 同时保存为PDF文件（矢量格式）
            pdf_file = output_path / "battery_analysis_chart.pdf"
            plt.savefig(pdf_file, bbox_inches='tight')
            
            self.logger.info("PDF chart saved to: %s", pdf_file)
            
        except (ValueError, RuntimeError, OSError, IOError, TypeError) as e:
            self.logger.error("Failed to generate static chart: %s", e)
