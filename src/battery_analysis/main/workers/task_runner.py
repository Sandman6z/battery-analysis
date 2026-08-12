# -*- coding: utf-8 -*-
"""
统一后台任务执行器

替代原有的 AnalysisWorker（QRunnable）和 BackgroundWorker（QObject）两套模式。
通过 TaskRunner（QRunnable）执行一次性任务，通过 TaskManager 管理生命周期。
"""

from __future__ import annotations

import logging
from typing import Callable, Optional, Any
from PyQt6 import QtCore as QC


class TaskSignals(QC.QObject):
    """任务信号 — 所有 TaskRunner 共享的信号集合。"""
    started = QC.pyqtSignal()
    progress = QC.pyqtSignal(int, str)  # (百分比, 状态文本)
    finished = QC.pyqtSignal(object)    # 返回结果
    error = QC.pyqtSignal(str)          # 错误消息
    cancelled = QC.pyqtSignal()


class TaskRunner(QC.QRunnable):
    """通用后台任务执行器。

    用法:
        runner = TaskRunner(fn, arg1, arg2, progress_callback=on_progress)
        runner.signals.finished.connect(on_done)
        QThreadPool.globalInstance().start(runner)
    """

    def __init__(self, task_func: Callable, *args, progress_callback=None, **kwargs):
        super().__init__()
        self._task_func = task_func
        self._args = args
        self._kwargs = kwargs
        self._cancelled = False
        self.signals = TaskSignals()
        self._progress_cb = progress_callback
        self.logger = logging.getLogger(__name__)

    def run(self):
        """执行任务（QRunnable 入口）。"""
        if self._cancelled:
            self.signals.cancelled.emit()
            return

        try:
            self.signals.started.emit()

            # 包装 progress_callback
            if self._progress_cb is None:
                def default_progress(pct, msg):
                    self.signals.progress.emit(pct, msg)
                wrapped_cb = default_progress
            else:
                wrapped_cb = self._progress_cb

            result = self._task_func(
                *self._args,
                progress_callback=wrapped_cb,
                **self._kwargs
            )
            if not self._cancelled:
                self.signals.finished.emit(result)
        except Exception as e:
            self.logger.error("Task execution failed: %s", e)
            self.signals.error.emit(str(e))

    def cancel(self):
        """请求取消任务。"""
        self._cancelled = True
        self.signals.cancelled.emit()


class TaskManager(QC.QObject):
    """任务管理器 — 管理多个 TaskRunner 的生命周期。

    可替代原有的 MainController（部分职责），统一线程池和任务队列管理。
    """
    all_completed = QC.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pool = QC.QThreadPool.globalInstance()
        self._active: list[TaskRunner] = []
        self.logger = logging.getLogger(__name__)

    def submit(self, runner: TaskRunner) -> TaskRunner:
        """提交任务到线程池。"""
        self._active.append(runner)
        runner.signals.finished.connect(lambda: self._on_done(runner))
        runner.signals.error.connect(lambda _: self._on_done(runner))
        self._pool.start(runner)
        return runner

    def cancel_all(self):
        """取消所有活跃任务。"""
        for r in self._active:
            r.cancel()
        self._active.clear()

    def _on_done(self, runner: TaskRunner):
        if runner in self._active:
            self._active.remove(runner)
        if not self._active:
            self.all_completed.emit()

    @property
    def active_count(self) -> int:
        return len(self._active)
