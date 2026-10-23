"""
主控制器模块
负责处理核心业务逻辑和协调各个组件
"""

import logging
from copy import deepcopy

from PyQt6 import QtCore as QC
from PyQt6 import QtWidgets as QW

from battery_analysis.main.workers.analysis_worker import AnalysisWorker
from battery_analysis.main.workers.task_runner import TaskSignals

logger = logging.getLogger("battery_analysis.main_controller")


class MainController(QC.QObject):
    """
    主控制器类
    负责应用程序的核心业务逻辑控制
    """

    # 定义信号
    progress_updated = QC.pyqtSignal(int, str)  # 进度更新信号
    status_changed = QC.pyqtSignal(bool, int, str)  # 状态变化信号
    analysis_completed = QC.pyqtSignal()  # 分析结束（含失败/取消），仅用于 UI 复位
    analysis_succeeded = QC.pyqtSignal()  # 报告成功，用于版本计次
    path_renamed = QC.pyqtSignal(str)  # 路径重命名信号
    start_visualizer = QC.pyqtSignal()  # 启动可视化工具信号

    def __init__(self):
        """
        初始化主控制器
        """
        super().__init__()
        self.thread_pool = QC.QThreadPool.globalInstance()
        self.current_worker = None
        self.is_analysis_running = False
        self.project_path = ""
        self.input_path = ""
        self.output_path = ""
        self.test_info = []
        self.completed_context = {}

    def set_project_context(self, project_path=None, input_path=None, output_path=None):
        """
        设置项目上下文信息

        Args:
            project_path: 项目路径 (可选)
            input_path: 输入数据路径 (可选)
            output_path: 输出结果路径 (可选)
        """
        if project_path is not None:
            self.project_path = project_path
        if input_path is not None:
            self.input_path = input_path
        if output_path is not None:
            self.output_path = output_path

    def set_test_info(self, test_info):
        """
        设置测试信息

        Args:
            test_info: TestInfo 实例或 list
        """
        self.test_info = test_info

    def start_analysis(self):
        """
        开始电池分析任务
        """
        if self.is_analysis_running:
            return False

        # 验证必要的参数
        if not all([self.project_path, self.input_path, self.output_path, self.test_info]):
            self.status_changed.emit(False, 1, "Error: missing required analysis parameters")
            return False

        # 创建工作线程 — TaskSignals 以 controller（QObject）为 parent，
        # 确保 C++ 侧生命周期由 Qt 管理，不会被 Python GC 提前销毁。
        signals = TaskSignals(self)
        self.current_worker = AnalysisWorker(signals=signals)
        self.current_worker.set_info(
            self.project_path, self.input_path, self.output_path, self.test_info
        )
        self.current_worker.input_files = deepcopy(getattr(self, "input_files", None))
        self.current_worker.profile_validation = deepcopy(getattr(self, "profile_validation", None) or {})
        self.current_worker.equipment_info = deepcopy(getattr(self, "equipment_info", {}))
        from battery_analysis.domain.test_info import TestInfo

        info = self.current_worker.list_test_info
        self.current_worker.success_context = {
            "project_path": self.project_path,
            "output_path": self.output_path,
            "checksum": getattr(self, "checksum", ""),
            "version": info.version if isinstance(info, TestInfo) else info[16],
        }

        # 连接信号
        self.current_worker.signals.progress.connect(self._on_progress_update)
        self.current_worker.signals.info.connect(self._on_status_changed)
        self.current_worker.signals.thread_end.connect(self._on_analysis_completed)
        self.current_worker.signals.analysis_succeeded.connect(self.analysis_succeeded.emit)
        self.current_worker.signals.anomalies_request.connect(self._on_anomalies_request)
        self.current_worker.signals.rename_path.connect(self._on_path_renamed)
        self.current_worker.signals.start_visualizer.connect(self._on_start_visualizer)

        # 启动工作线程
        self.thread_pool.start(self.current_worker)
        self.is_analysis_running = True
        logger.info("Analysis submitted: input=%s output=%s", self.input_path, self.output_path)
        return True

    def cancel_analysis(self):
        """
        取消正在进行的分析任务
        """
        if not self.is_analysis_running or not self.current_worker:
            return False

        self.current_worker.request_cancel()
        return True

    def is_running(self):
        """
        检查分析是否正在运行

        Returns:
            bool: True表示正在运行，False表示未运行
        """
        return self.is_analysis_running

    @staticmethod
    def _show_anomaly_dialog(title, prompt, lines, confirm_label):
        """Keep anomaly details scrollable and the action buttons on screen."""
        parent = QW.QApplication.activeWindow()
        dialog = QW.QDialog(parent)
        dialog.setWindowTitle(title)
        layout = QW.QVBoxLayout(dialog)
        summary = QW.QLabel(prompt)
        summary.setWordWrap(True)
        layout.addWidget(summary)
        details = QW.QPlainTextEdit(dialog)
        details.setReadOnly(True)
        details.setPlainText("\n".join(lines))
        layout.addWidget(details)
        buttons = QW.QDialogButtonBox(dialog)
        confirm = buttons.addButton(confirm_label, QW.QDialogButtonBox.ButtonRole.AcceptRole)
        stop = buttons.addButton("Stop batch", QW.QDialogButtonBox.ButtonRole.RejectRole)
        stop.setDefault(True)
        confirm.clicked.connect(dialog.accept)
        stop.clicked.connect(dialog.reject)
        layout.addWidget(buttons)
        screen = parent.screen() if parent else QW.QApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()
            dialog.resize(min(700, int(available.width() * 0.8)), min(500, int(available.height() * 2 / 3)))
        return dialog.exec() == QW.QDialog.DialogCode.Accepted

    def _on_anomalies_request(self, anomalies):
        """Both confirmations run on this QObject's GUI thread, never in the worker."""
        worker = self.current_worker
        if worker is None or worker.b_cancel_requested:
            if worker:
                worker.confirm_anomalies(False)
            return
        logger.info("Showing anomaly dialog: count=%d", len(anomalies))
        lines = [
            f"{a['file']}: {a['type']} — {a['current']} mA / {a['voltage']} V (required judgment cell)"
            if a["type"] in ("missing_pulse", "required_slot_missing") else
            f"{a['file']}: {a['type']} - {a.get('reason', a.get('current', ''))}"
            for a in anomalies
        ]
        summary = f"Missing/invalid slots: {len(anomalies)}; affected files: {len({a['file'] for a in anomalies})}. "
        structural = any(a["type"] != "current_deviation" for a in anomalies)
        consequence = (
            "Required judgment data or input files are missing. Continuing leaves slots empty; the report is not proof of a complete qualification test."
            if structural else "Measured pulse currents deviate from the Step.xml recipe; data remain available."
        )
        allowed = False
        if self._show_anomaly_dialog("Analysis anomalies", summary + "Stop the entire batch? Review the anomalies below before continuing.", lines, "Review consequences") and not worker.b_cancel_requested:
            allowed = self._show_anomaly_dialog("Missing data consequences", summary + consequence + " Continue?", lines, "Continue analysis")
        logger.info("Anomaly dialog completed: allowed=%s", allowed)
        worker.confirm_anomalies(allowed)

    def _on_progress_update(self, progress, status_text):
        """
        进度更新回调

        Args:
            progress: 进度值(0-100)
            status_text: 状态文本
        """
        self.progress_updated.emit(progress, status_text)

    def _on_status_changed(self, is_running, status_code, message):
        """
        状态变化回调

        Args:
            is_running: 是否正在运行
            status_code: 状态代码
            message: 状态消息
        """
        if not is_running and status_code == 0 and message.split("\n", 1)[0] == "status:success":
            self.completed_context = dict(self.current_worker.success_context)
            self.completed_report_path = self.current_worker.delivered_report_path
            self.completed_result_dir = self.current_worker.delivered_result_dir
        self.status_changed.emit(is_running, status_code, message)

    def _on_analysis_completed(self):
        """
        分析完成回调
        """
        logger.info("Analysis thread ended")
        self.is_analysis_running = False
        # 释放 worker 引用，允许 Python GC 回收 TaskRunner（setAutoDelete=False）
        self.current_worker = None
        self.analysis_completed.emit()

    def _on_path_renamed(self, test_date):
        """
        路径重命名回调

        Args:
            test_date: 测试日期
        """
        self.path_renamed.emit(test_date)

    def _on_start_visualizer(self):
        """
        启动可视化工具回调
        转发信号给主窗口
        """
        try:
            if hasattr(self, "start_visualizer"):
                self.start_visualizer.emit()
            else:
                logging.error(
                    "main_controller.start_visualizer signal does not exist, cannot forward"
                )
        except (AttributeError, TypeError, RuntimeError) as e:
            logging.error("Failed to forward start visualizer signal: %s", e)
