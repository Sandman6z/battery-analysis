"""可视化管理器模块"""
import logging
import matplotlib.pyplot as plt
from PyQt6 import QtWidgets as QW
from battery_analysis.main.app_context import AppContext, UIBridge


class VisualizationManager:
    """可视化工具管理器"""

    def __init__(self, main_window=None, ctx: AppContext = None):
        """
        初始化可视化管理器

        Args:
            main_window: 主窗口实例（旧接口，过渡用）
            ctx: 应用上下文（新接口）
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._ctx = ctx
        self._ui: UIBridge = ctx.ui if ctx and ctx.ui else \
            (self._make_bridge(main_window) if main_window else None)
        self._parent_widget = main_window

    @staticmethod
    def _make_bridge(mw) -> UIBridge:
        from battery_analysis.main.app_context import UIBridgeImpl
        return UIBridgeImpl(mw)

    def _get_test_profile(self) -> str:
        if self._ui:
            return self._ui.get_lineedit_text("TestProfile")
        if self.main_window and hasattr(self.main_window, 'lineEdit_TestProfile'):
            return self.main_window.lineEdit_TestProfile.text()
        return ""

    def _status(self, msg: str):
        if self._ui:
            self._ui.update_statusbar(msg)
        elif self.main_window and hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage(msg)

    def _get_visualizer_factory(self):
        if self.main_window and hasattr(self.main_window, 'visualizer_factory'):
            return self.main_window.visualizer_factory
        return None

    def run_visualizer(self, xml_path=None) -> None:
        """运行可视化工具"""
        self.logger.info("进入可视化工具运行方法")

        # 检查xml_path是否为布尔值，如果是，则忽略（可能来自QAction的triggered信号）
        if isinstance(xml_path, bool):
            self.logger.info("检测到布尔类型的xml_path参数，忽略它")
            xml_path = None

        # 如果未提供xml_path，尝试从主窗口获取
        if xml_path is None:
            xml_path = self._get_test_profile()
            if xml_path:
                self.logger.info("获取到XML路径: %s", xml_path)
            else:
                self.logger.info("未设置XML路径")

        self._status("启动可视化工具...")

        try:
            # 清理matplotlib资源
            self._cleanup_matplotlib_resources()

            # 使用工厂模式创建可视化器
            factory = self._get_visualizer_factory()
            visualizer = factory.create_visualizer("battery_chart") if factory else None

            if visualizer is None:
                raise RuntimeError("无法创建可视化器实例")

            # 显示可视化（传递XML路径，让viewer处理数据搜索和加载）
            show_success = visualizer.show_figure(xml_path=xml_path)

            if show_success:
                self.logger.info("可视化工具已启动")
                self._status("可视化工具已启动")
            else:
                raise RuntimeError("显示可视化失败")

        except (OSError, ValueError, RuntimeError, ImportError) as e:
            self.logger.error("启动可视化工具时发生错误: %s", e)
            self._handle_visualization_error(str(e))

    def _cleanup_matplotlib_resources(self):
        """清理matplotlib资源"""
        try:
            plt.close('all')
        except (ImportError, RuntimeError) as e:
            self.logger.warning("清理matplotlib资源时出错: %s", e)

    def _handle_visualization_error(self, error_msg: str):
        """处理可视化错误"""
        data_error_keywords = ['data', 'csv', 'load', 'file', 'path', 'config', 'info_image', '数据']
        is_data_error = any(keyword in error_msg.lower() for keyword in data_error_keywords)

        if is_data_error:
            from battery_analysis.main.dialogs.data_error_dialog import DataErrorRecoveryDialog
            dialog = DataErrorRecoveryDialog(self._parent_widget or self.main_window)
            dialog.show(error_msg)
        else:
            self._critical("错误",
                           f"启动可视化工具时出错:\n\n{error_msg}\n\n请检查配置文件或联系技术支持。")

        self._status("状态:就绪")

    def show_visualizer_error(self, error_msg: str):
        """显示可视化错误消息"""
        self._critical("错误",
                       f"启动可视化工具时发生错误: {error_msg}")
        self._status("状态:就绪")

    # ── UI 助手 ──────────────────────────────────────────────────

    def _critical(self, title, msg):
        if self._ui:
            self._ui.show_critical(title, msg)
        elif self.main_window:
            QW.QMessageBox.critical(self.main_window, title, msg)
