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
        self._embedded_widget = None
        self._current_canvas = None

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
        """运行可视化工具（独立窗口模式）"""
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

        # 直接使用独立窗口模式
        self._run_visualizer_standalone(xml_path)

    def _try_embedded_mode(self, xml_path=None) -> bool:
        """尝试嵌入模式

        Returns:
            bool: 是否成功嵌入
        """
        try:
            # 检查主窗口是否有图表容器
            if not self.main_window or not hasattr(self.main_window, "chart_container"):
                self.logger.info("Main window does not have chart_container, skipping embedded mode")
                return False

            # 清理matplotlib资源
            self._cleanup_matplotlib_resources()

            # 使用工厂模式创建可视化器
            factory = self._get_visualizer_factory()
            visualizer = factory.create_visualizer("battery_chart") if factory else None

            if visualizer is None:
                self.logger.warning("Failed to create visualizer instance")
                return False

            # 获取嵌入区域
            embed_widget = self.main_window.chart_container

            # 嵌入图表
            result = visualizer.embed_to_widget(embed_widget)

            if result is not None:
                fig, canvas, filter_checkbox, scroll_area, battery_checkboxes = result
                self._current_canvas = canvas

                # 将控制面板添加到主窗口的控制面板区域
                if hasattr(self.main_window, "chart_control_panel"):
                    control_panel = self.main_window.chart_control_panel
                    from PyQt6.QtWidgets import QVBoxLayout

                    layout = QVBoxLayout(control_panel)
                    layout.setContentsMargins(5, 5, 5, 5)
                    layout.setSpacing(5)

                    if filter_checkbox:
                        layout.addWidget(filter_checkbox)

                    if scroll_area:
                        layout.addWidget(scroll_area)

                    layout.addStretch()

                    control_panel.setLayout(layout)

                # 显示图表区域
                if hasattr(self.main_window, "show_chart_area"):
                    self.main_window.show_chart_area()

                self.logger.info("Embedded visualizer started")
                self._status("Visualizer started (embedded)")
                return True
            else:
                self.logger.warning("Failed to create embedded visualization")
                return False

        except Exception as e:
            self.logger.warning("Embedded mode failed: %s", e)
            return False

    def _run_visualizer_standalone(self, xml_path=None) -> None:
        """独立窗口模式（回退方案）"""
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
                self.logger.info("Visualizer started (standalone)")
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

    def run_visualizer_embedded(self, xml_path=None) -> bool:
        """运行可视化工具（嵌入模式）

        将图表嵌入到主窗口的嵌入区域中，而不是弹出独立窗口。

        Args:
            xml_path: 可选，XML 配置文件路径

        Returns:
            bool: 是否成功嵌入
        """
        self.logger.info("Entering embedded visualizer run method")

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

        self._status("Starting embedded visualizer...")

        try:
            # 清理matplotlib资源
            self._cleanup_matplotlib_resources()

            # 使用工厂模式创建可视化器
            factory = self._get_visualizer_factory()
            visualizer = factory.create_visualizer("battery_chart") if factory else None

            if visualizer is None:
                raise RuntimeError("Failed to create visualizer instance")

            # 获取或创建嵌入区域
            embed_widget = self._get_or_create_embed_widget()

            # 嵌入图表
            result = visualizer.embed_to_widget(embed_widget)

            if result is not None:
                fig, canvas, filter_checkbox, scroll_area, battery_checkboxes = result
                self._current_canvas = canvas

                # 将控制面板添加到主窗口的控制面板区域
                if self.main_window and hasattr(self.main_window, "chart_control_panel"):
                    control_panel = self.main_window.chart_control_panel
                    from PyQt6.QtWidgets import QVBoxLayout

                    layout = QVBoxLayout(control_panel)
                    layout.setContentsMargins(5, 5, 5, 5)
                    layout.setSpacing(5)

                    if filter_checkbox:
                        layout.addWidget(filter_checkbox)

                    if scroll_area:
                        layout.addWidget(scroll_area)

                    layout.addStretch()

                    control_panel.setLayout(layout)

                # 显示图表区域
                if self.main_window and hasattr(self.main_window, "show_chart_area"):
                    self.main_window.show_chart_area()

                self.logger.info("Embedded visualizer started")
                self._status("Embedded visualizer started")
                return True
            else:
                raise RuntimeError("Failed to create embedded visualization")

        except (OSError, ValueError, RuntimeError, ImportError) as e:
            self.logger.error("Error starting embedded visualizer: %s", e)
            self._handle_visualization_error(str(e))
            return False

    def _get_or_create_embed_widget(self) -> QW.QWidget:
        """获取或创建嵌入区域

        Returns:
            QWidget: 嵌入区域控件
        """
        if self._embedded_widget is not None:
            return self._embedded_widget

        # 检查主窗口是否有 chart_container 控件
        if self.main_window and hasattr(self.main_window, "chart_container"):
            self._embedded_widget = self.main_window.chart_container
            return self._embedded_widget

        # 如果没有，创建一个新的容器
        if self.main_window:
            container = QW.QWidget(self.main_window)
            container.setObjectName("chart_container")
            container.setMinimumSize(600, 400)

            # 将容器添加到主窗口布局中
            # 这里需要根据主窗口的实际布局来决定放置位置
            # 暂时先返回容器，由调用方决定如何放置
            self._embedded_widget = container
            return container

        # 如果没有主窗口，返回一个独立的容器
        container = QW.QWidget()
        container.setObjectName("chart_container")
        container.setMinimumSize(600, 400)
        self._embedded_widget = container
        return container

    def detach_chart(self):
        """分离图表（从嵌入模式切换到独立窗口模式）"""
        if self._current_canvas is not None:
            # 从父控件中移除 canvas
            parent = self._current_canvas.parent()
            if parent and hasattr(parent, "layout"):
                layout = parent.layout()
                if layout:
                    layout.removeWidget(self._current_canvas)

            self._current_canvas = None
            self.logger.info("Chart detached from embedded mode")

    def _critical(self, title, msg):
        if self.main_window:
            QW.QMessageBox.critical(self.main_window, title, msg)
