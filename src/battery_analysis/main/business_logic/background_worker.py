"""
后台工作线程 — 已弃用，请使用 workers.task_runner.TaskRunner。

保留此模块仅用于向后兼容。
"""

import logging
from PyQt6 import QtCore as QC
from battery_analysis.main.workers.task_runner import TaskRunner, TaskSignals


class BackgroundWorker(QC.QObject):
    """已弃用 — 请使用 TaskRunner。"""

    finished = QC.pyqtSignal(object)
    error = QC.pyqtSignal(str)
    progress = QC.pyqtSignal(int, str)

    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self._inner = TaskRunner(task_func, *args, **kwargs)
        self._inner.signals.finished.connect(self.finished.emit)
        self._inner.signals.error.connect(self.error.emit)
        self._inner.signals.progress.connect(self.progress.emit)
        self.logger = logging.getLogger(__name__)

    @QC.pyqtSlot()
    def run(self):
        self._inner.run()
