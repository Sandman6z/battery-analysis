"""可视化管理器模块"""
import logging
import matplotlib.pyplot as plt
from PyQt6 import QtWidgets as QW


class VisualizationManager:
    """可视化工具管理器"""
    
    def __init__(self, main_window):
        """
        初始化可视化管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def run_visualizer(self, xml_path=None) -> None:
        """运行可视化工具"""
        self.logger.info("进入可视化工具运行方法")
        
        # 检查xml_path是否为布尔值，如果是，则忽略（可能来自QAction的triggered信号）
        if isinstance(xml_path, bool):
            self.logger.info("检测到布尔类型的xml_path参数，忽略它")
            xml_path = None
        
        # 如果未提供xml_path，尝试从主窗口获取
        if xml_path is None and hasattr(self.main_window, 'lineEdit_TestProfile'):
            xml_path = self.main_window.lineEdit_TestProfile.text()
            if xml_path:
                self.logger.info("从主窗口获取到XML路径: %s", xml_path)
            else:
                self.logger.info("主窗口未设置XML路径")
        
        self.main_window.statusBar_BatteryAnalysis.showMessage("启动可视化工具...")

        try:
            # 清理matplotlib资源
            self._cleanup_matplotlib_resources()
            
            # 使用工厂模式创建可视化器
            visualizer = self.main_window.visualizer_factory.create_visualizer("battery_chart")
            
            if visualizer is None:
                raise RuntimeError("无法创建可视化器实例")

            # 显示可视化（传递XML路径，让viewer处理数据搜索和加载）
            show_success = visualizer.show_figure(xml_path=xml_path)
            
            if show_success:
                self.logger.info("可视化工具已启动")
                self.main_window.statusBar_BatteryAnalysis.showMessage("可视化工具已启动")
            else:
                raise RuntimeError("显示可视化失败")

        except (OSError, ValueError, RuntimeError, ImportError) as e:
            self.logger.error("启动可视化工具时发生错误: %s", e)
            self._handle_visualization_error(str(e))
    
    def _cleanup_matplotlib_resources(self):
        """清理matplotlib资源"""
        try:
            # 关闭所有打开的matplotlib窗口
            plt.close('all')
        except (ImportError, RuntimeError) as e:
            self.logger.warning("清理matplotlib资源时出错: %s", e)
    
    def _handle_visualization_error(self, error_msg: str):
        """处理可视化错误"""
        # 判断是否为数据相关错误
        data_error_keywords = ['data', 'csv', 'load', 'file', 'path', 'config', 'info_image', '数据']
        is_data_error = any(keyword in error_msg.lower() for keyword in data_error_keywords)
        
        if is_data_error:
            # 数据相关错误，显示恢复对话框
            from battery_analysis.main.dialogs.data_error_dialog import DataErrorRecoveryDialog
            dialog = DataErrorRecoveryDialog(self.main_window)
            dialog.show(error_msg)
        else:
            # 其他错误，显示标准错误对话框
            QW.QMessageBox.critical(
                self.main_window,
                "错误",
                f"启动可视化工具时出错:\n\n{error_msg}\n\n请检查配置文件或联系技术支持。",
                QW.QMessageBox.StandardButton.Ok
            )
        
        self.main_window.statusBar_BatteryAnalysis.showMessage("状态:就绪")
    
    def show_visualizer_error(self, error_msg: str):
        """显示可视化错误消息"""
        QW.QMessageBox.critical(
            self.main_window,
            "错误",
            f"启动可视化工具时发生错误: {error_msg}",
            QW.QMessageBox.StandardButton.Ok
        )
        self.main_window.statusBar_BatteryAnalysis.showMessage("状态:就绪")
