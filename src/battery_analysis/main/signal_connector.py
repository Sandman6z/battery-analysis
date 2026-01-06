"""
信号连接器模块

这个模块实现了电池分析应用的信号连接功能，包括：
- 连接各种控制器的信号和槽函数
- 事件总线事件订阅
- 进度更新处理
- 配置变更处理
"""

import logging
import time
from typing import Any

import PyQt6.QtWidgets as QW

from battery_analysis.i18n.language_manager import _


class SignalConnector:
    """
    信号连接器类

    负责连接各种控制器的信号和槽函数，处理事件总线事件，
    管理进度更新和配置变更等。
    """

    def __init__(self, main_window):
        """
        初始化信号连接器

        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

        self.progress_dialog = None
        self.progress_start_time = None
        self.show_popup_progress = False
        self._task_duration_threshold = 30

    @property
    def task_duration_threshold(self):
        """获取任务时长阈值，优先使用主窗口的配置"""
        if hasattr(self.main_window, 'task_duration_threshold'):
            return self.main_window.task_duration_threshold
        return self._task_duration_threshold

    @task_duration_threshold.setter
    def task_duration_threshold(self, value):
        """设置任务时长阈值"""
        self._task_duration_threshold = value

    def _get_controller(self, controller_name):
        """获取控制器"""
        return self.main_window._get_controller(controller_name)

    def _get_service(self, service_name):
        """获取服务"""
        return self.main_window._get_service(service_name)

    def connect_controllers(self):
        """连接控制器信号和槽函数"""
        self._connect_main_controller_signals()
        self._connect_file_controller_signals()
        self._connect_validation_controller_signals()
        self._connect_event_bus_events()

    def _connect_main_controller_signals(self):
        """连接主控制器信号"""
        main_controller = self._get_controller("main_controller")
        if main_controller:
            if hasattr(main_controller, 'progress_updated'):
                main_controller.progress_updated.connect(self._on_progress_updated)
            if hasattr(main_controller, 'status_changed'):
                main_controller.status_changed.connect(self.main_window.get_threadinfo)
            if hasattr(main_controller, 'analysis_completed'):
                main_controller.analysis_completed.connect(self.main_window.set_version)
            if hasattr(main_controller, 'path_renamed'):
                main_controller.path_renamed.connect(self.main_window.rename_pltPath)
            if hasattr(main_controller, 'start_visualizer'):
                main_controller.start_visualizer.connect(self.main_window.run_visualizer)

    def _connect_file_controller_signals(self):
        """连接文件控制器信号"""
        file_controller = self._get_controller("file_controller")
        if file_controller:
            if hasattr(file_controller, 'config_loaded'):
                file_controller.config_loaded.connect(self._on_config_loaded)
            if hasattr(file_controller, 'error_occurred'):
                file_controller.error_occurred.connect(self._on_controller_error)

    def _connect_validation_controller_signals(self):
        """连接验证控制器信号"""
        validation_controller = self._get_controller("validation_controller")
        if validation_controller:
            if hasattr(validation_controller, 'validation_error'):
                validation_controller.validation_error.connect(self._on_controller_error)

    def _connect_event_bus_events(self):
        """连接事件总线事件"""
        event_bus = self._get_service("event_bus")
        if event_bus:
            event_bus.subscribe("progress_updated", self._on_event_progress_updated)
            event_bus.subscribe("status_changed", self._on_event_status_changed)
            event_bus.subscribe("file_selected", self._on_file_selected)
            event_bus.subscribe("config_changed", self._on_config_changed)

    def _on_progress_updated(self, progress, status_text):
        """进度更新处理"""
        if hasattr(self.main_window, 'progressBar'):
            self.main_window.progressBar.setValue(progress)
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage(f"状态: {status_text}")

        if self.progress_start_time is not None:
            elapsed_time = time.time() - self.progress_start_time
            if elapsed_time > self.task_duration_threshold and not self.show_popup_progress:
                self._show_progress_dialog()

        if self.show_popup_progress and self.progress_dialog:
            self.progress_dialog.update_progress(progress, status_text)

        if progress >= 100:
            self._close_progress_dialog()

    def _on_event_progress_updated(self, progress: int, status: str):
        """事件总线进度更新处理"""
        progress_service = self._get_service("progress")
        if progress_service:
            progress_service.update_progress(progress, status)
        self._on_progress_updated(progress, status)

    def _on_event_status_changed(self, status: bool, code: int, message: str):
        """事件总线状态变化处理"""
        self.logger.info("Status changed: %s, Code: %s, Message: %s", status, code, message)

    def _on_file_selected(self, file_path: str):
        """事件总线文件选择处理"""
        self.logger.info("File selected via event bus: %s", file_path)

    def _on_config_changed(self, key: str, value: Any):
        """事件总线配置变更处理"""
        self.logger.debug("Config changed: %s = %s", key, value)
        config_service = self._get_service("config")
        if config_service:
            config_service.set(key, value)

    def _on_config_loaded(self, config_dict):
        """配置加载完成处理"""
        pass

    def _on_controller_error(self, error_msg):
        """控制器错误处理"""
        self._close_progress_dialog()
        QW.QMessageBox.critical(self.main_window, _("error_title", "错误"), error_msg)

    def _show_progress_dialog(self):
        """显示弹出式进度条对话框"""
        from battery_analysis.main.progress_dialog import ProgressDialog
        if not self.progress_dialog:
            self.progress_dialog = ProgressDialog(self.main_window)
        self.progress_dialog.show()
        self.progress_dialog.raise_()
        self.progress_dialog.activateWindow()
        self.show_popup_progress = True

    def _close_progress_dialog(self):
        """关闭弹出式进度条对话框"""
        if self.progress_dialog and self.show_popup_progress:
            self.progress_dialog.close()
            self.progress_dialog = None
            self.show_popup_progress = False
        self.progress_start_time = None

    def start_progress_tracking(self):
        """开始进度跟踪"""
        self.progress_start_time = time.time()

    def stop_progress_tracking(self):
        """停止进度跟踪"""
        self.progress_start_time = None
        self._close_progress_dialog()
