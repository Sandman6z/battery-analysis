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
            if hasattr(main_controller, 'analysis_completed'):
                main_controller.analysis_completed.connect(self.main_window.get_version)
            if hasattr(main_controller, 'path_renamed'):
                main_controller.path_renamed.connect(self.main_window.rename_pltPath)
            if hasattr(main_controller, 'start_visualizer'):
                main_controller.start_visualizer.connect(self.main_window.run_visualizer)
            if hasattr(main_controller, 'status_changed'):
                main_controller.status_changed.connect(self._on_status_changed)

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
        from battery_analysis.main.services.event_bus import EventType
        
        event_bus = self._get_service("event_bus")
        if event_bus:
            event_bus.subscribe(EventType.PROGRESS_UPDATED, self._on_event_progress_updated)
            event_bus.subscribe(EventType.STATUS_CHANGED, self._on_event_status_changed)
            event_bus.subscribe(EventType.FILE_SELECTED, self._on_file_selected)
            event_bus.subscribe(EventType.CONFIG_CHANGED, self._on_config_changed)

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

    def _on_event_progress_updated(self, event):
        """事件总线进度更新处理"""
        progress = event.data["progress"]
        status = event.data["status"]
        progress_service = self._get_service("progress")
        if progress_service:
            progress_service.update_progress(progress, status)
        self._on_progress_updated(progress, status)

    def _on_event_status_changed(self, event):
        """事件总线状态变化处理"""
        status = event.data["status"]
        code = event.data["code"]
        message = event.data["message"]
        self.logger.info("Status changed: %s, Code: %s, Message: %s", status, code, message)
        
    def _on_status_changed(self, is_running, stateindex, threadinfo):
        """处理主控制器的状态变化信号，更新UI元素"""
        # 正常运行状态处理
        if is_running:
            # 处理取消状态
            if "canceling" in threadinfo:
                self.main_window.statusBar_BatteryAnalysis.showMessage("正在取消任务...")
                self.main_window.pushButton_Run.setText("取消中...")
                self.main_window.pushButton_Run.setEnabled(False)
            else:
                # 正常运行状态显示
                self.main_window.statusBar_BatteryAnalysis.showMessage("正在分析电池数据...")
                self.main_window.pushButton_Run.setText("Running")
        else:
            # 任务完成处理
            if stateindex == 0 and "success" in threadinfo:
                # 关闭进度条
                self._close_progress_dialog()

                self.main_window.pushButton_Run.setText("Run")
                self.main_window.pushButton_Run.setEnabled(True)
                self.main_window.statusBar_BatteryAnalysis.showMessage("电池分析完成！")

                # 显示成功提示，添加打开报告和打开路径按钮
                msg_box = QW.QMessageBox()
                msg_box.setWindowTitle("分析完成")
                msg_box.setText("电池分析已成功完成！\n\n报告已生成到指定输出路径。")
                msg_box.setIcon(QW.QMessageBox.Icon.Information)
                
                # 添加打开报告按钮
                open_report_button = msg_box.addButton("打开报告", QW.QMessageBox.ButtonRole.ActionRole)
                
                # 添加打开路径按钮
                open_path_button = msg_box.addButton("打开路径", QW.QMessageBox.ButtonRole.ActionRole)
                
                # 添加确定按钮
                ok_button = msg_box.addButton(QW.QMessageBox.StandardButton.Ok)
                
                msg_box.exec()
                
                # 处理按钮点击
                clicked_button = msg_box.clickedButton()
                if clicked_button == open_report_button:
                    # 调用主窗口的_open_report方法
                    if hasattr(self.main_window, '_open_report'):
                        self.main_window._open_report()
                elif clicked_button == open_path_button:
                    # 调用主窗口的_open_report_path方法
                    if hasattr(self.main_window, '_open_report_path'):
                        self.main_window._open_report_path()

            # 日期不一致错误处理 (stateindex == 3)
            elif stateindex == 3:
                # 关闭进度条
                self._close_progress_dialog()

                self.main_window.pushButton_Run.setText("Rerun")
                self.main_window.pushButton_Run.setEnabled(True)

                # 日期不一致错误消息处理
                error_title = "日期不一致错误"
                error_details = threadinfo

                # 构建日期不一致错误的具体建议
                suggestions = [
                    "请检查Excel文件中的Test Date字段是否correct",
                    "确保Test Date与实际测试日期一致",
                    "修正日期后重新运行分析"
                ]

                # 构建完整的错误消息
                full_error_msg = f"{error_title}:\n\n{error_details}\n\n建议解决步骤:\n"
                full_error_msg += "\n".join([f"- {s}" for s in suggestions])

                # 显示专门的日期不一致错误对话框
                QW.QMessageBox.critical(
                    self.main_window,
                    error_title,
                    full_error_msg,
                    QW.QMessageBox.StandardButton.Ok
                )

                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    f"[错误]: {error_title}")

            # 电池分析错误处理 (stateindex == 1)
            elif stateindex == 1:
                # 关闭进度条
                self._close_progress_dialog()

                self.main_window.pushButton_Run.setText("Rerun")
                self.main_window.pushButton_Run.setEnabled(True)

                # 增强的电池分析错误处理
                self._handle_error(
                    "电池分析错误",
                    "分析电池数据时出现错误。",
                    threadinfo,
                    True  # 需要关闭进度条
                )

            # 文件写入错误处理 (stateindex == 2)
            elif stateindex == 2:
                # 关闭进度条
                self._close_progress_dialog()

                self.main_window.pushButton_Run.setText("Rerun")
                self.main_window.pushButton_Run.setEnabled(True)

                self._handle_error(
                    "报告生成错误",
                    "生成分析报告时出现错误。",
                    threadinfo,
                    False  # 进度条已关闭
                )

            # 其他错误情况
            else:
                self.main_window.pushButton_Run.setText("Rerun")
                self.main_window.pushButton_Run.setEnabled(True)
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    f"[错误]: {threadinfo}")
    
    def _handle_error(self, error_title, error_msg, error_details, need_close_progress=True):
        """
        通用错误处理方法
        
        Args:
            error_title: 错误标题
            error_msg: 错误消息
            error_details: 错误详情
            need_close_progress: 是否需要关闭进度条
        """
        if need_close_progress:
            self._close_progress_dialog()
            self.main_window.pushButton_Run.setText("Rerun")
            self.main_window.pushButton_Run.setEnabled(True)
        
        # 根据错误内容提供更具体的建议
        suggestions = []
        error_details_lower = error_details.lower() if isinstance(error_details, str) else str(error_details).lower()
        error_details_str = error_details if isinstance(error_details, str) else str(error_details)
        
        if "input path" in error_details_lower or "找不到文件" in error_details_str:
            suggestions.append("请检查输入路径是否正确")
            suggestions.append("确保包含必要的数据文件")
        if "格式" in error_details_str or "format" in error_details_lower:
            suggestions.append("检查数据文件格式是否符合要求")
        if "权限" in error_details_str or "permission" in error_details_lower:
            suggestions.append("确保您有足够的文件操作权限")
        if "output" in error_details_lower or "写入" in error_details_str:
            suggestions.extend([
                "检查输出路径是否存在且可写",
                "确保有足够的磁盘空间",
                "关闭可能正在使用输出文件的其他程序",
                "尝试选择不同的输出目录"
            ])

        # 如果没有具体建议，提供通用建议
        if not suggestions:
            suggestions.extend([
                "检查输入数据的完整性",
                "确保文件路径不包含特殊字符",
                "重新选择有效的输入和输出目录"
            ])

        # 构建完整的错误消息
        full_error_msg = f"{error_msg}:\n\n{error_details_str}\n\n建议解决步骤:\n"
        full_error_msg += "\n".join([f"- {s}" for s in suggestions])

        # 显示详细的错误对话框
        QW.QMessageBox.critical(
            self.main_window,
            error_title,
            full_error_msg,
            QW.QMessageBox.StandardButton.Ok
        )

        self.main_window.statusBar_BatteryAnalysis.showMessage(
            f"[错误]: {error_title}")

    def _on_file_selected(self, event):
        """事件总线文件选择处理"""
        file_path = event.data["file_path"]
        self.logger.info("File selected via event bus: %s", file_path)

    def _on_config_changed(self, event):
        """事件总线配置变更处理"""
        key = event.data["key"]
        value = event.data["value"]
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
        from battery_analysis.main.ui_components.progress_dialog import ProgressDialog
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
