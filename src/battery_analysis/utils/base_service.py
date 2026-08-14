# -*- coding: utf-8 -*-
"""
基础服务类
提供统一的错误处理、日志记录等公共功能
"""

import logging
from typing import Any, Tuple
from abc import ABC


class BaseService(ABC):
    """
    基础服务类
    提供统一的错误处理、日志记录等公共功能
    """

    def __init__(self):
        """
        初始化基础服务
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._running = False

    # ── 生命周期 ──────────────────────────────────────────────

    def start(self) -> None:
        """启动服务（子类可覆盖）。"""
        self._running = True

    def stop(self) -> None:
        """停止服务，释放资源（子类可覆盖）。"""
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    # ── 错误处理 ──────────────────────────────────────────────

    def _handle_error(self, e: Exception, message: str) -> Tuple[bool, str]:
        """
        统一错误处理

        Args:
            e: 异常对象
            message: 错误消息

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        error_msg = f"{message}: {str(e)}"
        self.logger.error(error_msg)
        return False, error_msg

    def _log_success(self, message: str) -> None:
        """
        记录成功日志

        Args:
            message: 成功消息
        """
        self.logger.info(message)

    def _safe_operation(self, func, *args, **kwargs) -> Any:
        """
        安全操作装饰器

        Args:
            func: 要执行的函数
            args: 函数参数
            kwargs: 函数关键字参数

        Returns:
            Any: 函数返回值或默认值
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Operation failed: {str(e)}")
            return None


