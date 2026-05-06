"""
后台工作线程，用于执行I/O密集型操作，避免阻塞UI
"""

import logging
from PyQt6 import QtCore as QC


class BackgroundWorker(QC.QObject):
    """后台工作线程，在QThread中执行任务函数"""

    finished = QC.pyqtSignal(object)
    error = QC.pyqtSignal(str)
    progress = QC.pyqtSignal(int, str)

    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.logger = logging.getLogger(__name__)

    @QC.pyqtSlot()
    def run(self):
        try:
            self.logger.debug("后台任务开始执行: %s", self.task_func.__name__)
            result = self.task_func(*self.args, **self.kwargs)
            self.logger.debug("后台任务执行完成: %s", self.task_func.__name__)
            self.finished.emit(result)
        except Exception as e:
            self.logger.error("后台任务执行失败: %s - %s", self.task_func.__name__, str(e))
            self.error.emit(str(e))
