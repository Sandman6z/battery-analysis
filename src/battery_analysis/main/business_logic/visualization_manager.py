"""
可视化工具管理器模块

负责处理可视化工具的调用和管理
"""

import logging
from PyQt6 import QtWidgets as QW
from battery_analysis.i18n.language_manager import _


class VisualizationManager:
    """
    可视化工具管理器类，负责处理可视化工具的调用和管理
    """
    
    def __init__(self, main_window):
        """
        初始化可视化工具管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def run_visualizer(self, xml_path=None) -> None:
        """
        运行可视化工具，使用工厂模式解耦依赖
        
        Args:
            xml_path: 可选，XML文件路径
        """
        self.logger.info("进入visualization_manager.run_visualizer方法")
        
        # 检查xml_path是否为布尔值，如果是，则忽略（可能来自QAction的triggered信号）
        if isinstance(xml_path, bool):
            self.logger.info("检测到布尔类型的xml_path参数，忽略它")
            xml_path = None
        
        # 更新状态栏
        self.main_window.statusBar_BatteryAnalysis.showMessage(
            _("starting_visualizer", "启动可视化工具...")
        )
        
        try:
            # 确保所有matplotlib资源都被释放（只清理全局资源，不涉及实例）
            try:
                import matplotlib.pyplot as plt
                plt.close('all')  # 关闭所有打开的matplotlib窗口
            except (ImportError, RuntimeError) as e:
                self.logger.warning("清理matplotlib全局资源时出错: %s", e)
            
            # 检查必要的路径设置
            input_path = self.main_window.lineEdit_InputPath.text()
            output_path = self.main_window.lineEdit_OutputPath.text()
            
            if not input_path:
                QW.QMessageBox.warning(
                    self.main_window,
                    _("warning_title", "警告"),
                    _("input_path_not_set", "请先设置输入路径。")
                )
                return
            
            if not output_path:
                QW.QMessageBox.warning(
                    self.main_window,
                    _("warning_title", "警告"),
                    _("output_path_not_set", "请先设置输出路径。")
                )
                return
            
            # 这里可以实现可视化工具调用的逻辑
            # 例如：使用工厂模式创建和运行可视化工具
            
            # 目前暂时使用消息框提示
            QW.QMessageBox.information(
                self.main_window,
                _("visualizer_started", "可视化工具已启动"),
                _("visualizer_started_message", "可视化工具已启动。\n\n目前此功能处于开发阶段。")
            )
            
        except (ImportError, AttributeError, TypeError, OSError, ValueError, RuntimeError) as e:
            self.logger.error("运行可视化工具失败: %s", e)
            QW.QMessageBox.critical(
                self.main_window,
                _("visualizer_error_title", "可视化工具错误"),
                _("visualizer_error_message", "运行可视化工具失败:\n\n{}").format(e)
            )
        finally:
            # 无论成功与否，都更新状态栏为就绪状态
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                _("status_ready", "状态:就绪")
            )
