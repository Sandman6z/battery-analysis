# -*- coding: utf-8 -*-
"""
统一后台任务执行器

替代原有的 AnalysisWorker（QRunnable）和 BackgroundWorker（QObject）两套模式。
通过 TaskRunner（QRunnable）执行一次性任务，通过 TaskManager 管理生命周期。
"""

from __future__ import annotations

import logging
from typing import Callable
from PyQt6 import QtCore as QC


class TaskCancelled(Exception):
    """协作式取消信号——progress_callback 检测到取消请求时抛出，run() 捕获后中断任务。"""


class TaskSignals(QC.QObject):
    """任务信号 — 所有 TaskRunner 共享的信号集合。"""
    started = QC.pyqtSignal()
    progress = QC.pyqtSignal(int, str)  # (百分比, 状态文本)
    finished = QC.pyqtSignal(object)    # 返回结果
    error = QC.pyqtSignal(str)          # 错误消息
    cancelled = QC.pyqtSignal()

    # P5-B：AnalysisWorker 并入的信号
    info = QC.pyqtSignal(bool, int, str)     # (is_running, 状态码, 消息)
    thread_end = QC.pyqtSignal()             # 分析线程结束
    rename_path = QC.pyqtSignal(str)         # 输出目录重命名后的日期
    start_visualizer = QC.pyqtSignal()       # 通知主线程启动可视化


class TaskRunner(QC.QRunnable):
    """通用后台任务执行器。

    用法:
        runner = TaskRunner(fn, arg1, arg2, progress_callback=on_progress)
        runner.signals.finished.connect(on_done)
        QThreadPool.globalInstance().start(runner)

    协作式取消：cancel() 是 cancelled 信号的唯一发射者；取消只在 task_func 调用
    progress_callback 时生效（每次调用检查标志，取消抛 TaskCancelled 中断）。
    不调用 progress_callback 的 task_func 无法被中断，会在取消后跑完但其结果被丢弃
    （finished 被抑制）。
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
            return

        # 包装 progress_callback：每次调用检查取消标志，取消则抛 TaskCancelled
        def wrapped_cb(pct, msg):
            if self._cancelled:
                raise TaskCancelled
            self.signals.progress.emit(pct, msg)
            if self._progress_cb is not None:
                self._progress_cb(pct, msg)

        try:
            self.signals.started.emit()
            result = self._task_func(
                *self._args,
                progress_callback=wrapped_cb,
                **self._kwargs,
            )
            if not self._cancelled:
                self.signals.finished.emit(result)
        except TaskCancelled:
            return
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
        runner.signals.cancelled.connect(lambda: self._on_done(runner))
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
