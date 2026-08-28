"""可视化管理器模块"""

import logging

from PyQt6 import QtWidgets as QW


class VisualizationManager:
    """可视化工具管理器"""

    def __init__(self, main_window=None):
        """
        初始化可视化管理器

        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

    def _get_test_profile(self) -> str:
        if self.main_window and hasattr(self.main_window, "lineEdit_TestProfile"):
            return self.main_window.lineEdit_TestProfile.text()
        return ""

    def _status(self, msg: str):
        if self.main_window and hasattr(self.main_window, "statusBar_BatteryAnalysis"):
            self.main_window.statusBar_BatteryAnalysis.showMessage(msg)

    def _get_visualizer_factory(self):
        if self.main_window and hasattr(self.main_window, "visualizer_factory"):
            return self.main_window.visualizer_factory
        return None

    def run_visualizer(self, xml_path=None) -> None:
        """运行可视化工具"""
        self.logger.info("Entering visualizer run method")

        # 检查xml_path是否为布尔值，如果是，则忽略（可能来自QAction的triggered信号）
        if isinstance(xml_path, bool):
            self.logger.info("Detected boolean xml_path parameter, ignoring it")
            xml_path = None

        # 如果未提供xml_path，尝试从主窗口获取
        if xml_path is None:
            xml_path = self._get_test_profile()
            if xml_path:
                self.logger.info("Retrieved XML path: %s", xml_path)
            else:
                self.logger.info("XML path not set")

        self._status("Starting visualizer...")

        try:
            # 清理matplotlib资源
            self._cleanup_matplotlib_resources()

            # 使用工厂模式创建可视化器
            factory = self._get_visualizer_factory()
            visualizer = factory.create_visualizer("battery_chart") if factory else None

            if visualizer is None:
                raise RuntimeError("Failed to create visualizer instance")

            # 显示可视化（传递XML路径，让viewer处理数据搜索和加载）
            show_success = visualizer.show_figure(xml_path=xml_path)

            if show_success:
                self.logger.info("Visualizer started")
                self._status("Visualizer started")
            else:
                raise RuntimeError("Failed to display visualization")

        except (OSError, ValueError, RuntimeError, ImportError) as e:
            self.logger.error("Error starting visualizer: %s", e)
            self._handle_visualization_error(str(e))

    def _cleanup_matplotlib_resources(self):
        """清理matplotlib资源"""
        import matplotlib.pyplot as plt

        try:
            plt.close("all")
        except (ImportError, RuntimeError) as e:
            self.logger.warning("Error cleaning up matplotlib resources: %s", e)

    def _handle_visualization_error(self, error_msg: str):
        """处理可视化错误"""
        data_error_keywords = ["data", "csv", "load", "file", "path", "config", "info_image"]
        is_data_error = any(keyword in error_msg.lower() for keyword in data_error_keywords)

        if is_data_error:
            from battery_analysis.main.dialogs.data_error_dialog import DataErrorRecoveryDialog

            dialog = DataErrorRecoveryDialog(self.main_window)
            dialog.show(error_msg)
        else:
            self._critical(
                "Error",
                f"Error starting visualizer:\n\n{error_msg}\n\nPlease check the configuration file or contact technical support.",
            )

        self._status("Status: Ready")

    def show_visualizer_error(self, error_msg: str):
        """显示可视化错误消息"""
        self._critical("Error", f"Error starting visualizer: {error_msg}")
        self._status("Status: Ready")

    # ── UI 助手 ──────────────────────────────────────────────────

    def _critical(self, title, msg):
        if self.main_window:
            QW.QMessageBox.critical(self.main_window, title, msg)
