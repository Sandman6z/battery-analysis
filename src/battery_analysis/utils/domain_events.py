# -*- coding: utf-8 -*-
"""
领域事件系统

为业务层提供类型安全的事件发布/订阅机制。
事件通过 Qt 信号传递，确保 UI 线程安全。
与旧版 EventBus 的区别：事件有类型、有结构化数据、可追踪。
"""

from __future__ import annotations

import logging
import time
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum, auto

logger = logging.getLogger(__name__)


# ── 事件类型 ──────────────────────────────────────────────────


class DomainEventType(Enum):
    """所有领域事件的类型枚举。"""
    # 分析流程
    ANALYSIS_STARTED = auto()
    ANALYSIS_PROGRESS = auto()
    ANALYSIS_COMPLETED = auto()
    ANALYSIS_FAILED = auto()
    ANALYSIS_CANCELLED = auto()
    # 报告
    REPORT_GENERATED = auto()
    REPORT_EXPORTED = auto()
    # 配置
    CONFIG_CHANGED = auto()
    CONFIG_RELOADED = auto()
    # 可视化
    VISUALIZER_STARTED = auto()
    VISUALIZER_FAILED = auto()


# ── 事件数据 ──────────────────────────────────────────────────


@dataclass
class DomainEvent:
    """领域事件基类。"""
    type: DomainEventType
    timestamp: float = field(default_factory=time.time)
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.type.name}] from={self.source} data={self.data}"


# ── 具体事件工厂 ──────────────────────────────────────────────


def analysis_started(source: str = "") -> DomainEvent:
    return DomainEvent(DomainEventType.ANALYSIS_STARTED, source=source)


def analysis_completed(test_date: str = "", version: str = "", source: str = "") -> DomainEvent:
    return DomainEvent(
        DomainEventType.ANALYSIS_COMPLETED,
        source=source,
        data={"test_date": test_date, "version": version},
    )


def analysis_failed(error: str = "", source: str = "") -> DomainEvent:
    return DomainEvent(
        DomainEventType.ANALYSIS_FAILED,
        source=source,
        data={"error": error},
    )


# ── 事件总线 ──────────────────────────────────────────────────


class DomainEventBus:
    """轻量级领域事件总线（非 Qt，用于业务层内部）。"""

    _instance: Optional["DomainEventBus"] = None

    @classmethod
    def instance(cls) -> "DomainEventBus":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._subscribers: Dict[DomainEventType, List[Callable[[DomainEvent], None]]] = {}
        self._history: List[DomainEvent] = []
        self._max_history = 100

    def subscribe(self, event_type: DomainEventType, callback: Callable[[DomainEvent], None]) -> None:
        """订阅指定类型的事件。"""
        self._subscribers.setdefault(event_type, []).append(callback)

    def unsubscribe(self, event_type: DomainEventType, callback: Callable[[DomainEvent], None]) -> None:
        """取消订阅。"""
        subs = self._subscribers.get(event_type, [])
        if callback in subs:
            subs.remove(callback)

    def publish(self, event: DomainEvent) -> None:
        """发布事件（同步调用所有订阅者）。"""
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        logger.debug("Publishing domain event: %s", event)
        for callback in self._subscribers.get(event.type, []):
            try:
                callback(event)
            except Exception as e:
                logger.error("Domain event callback error [%s]: %s", event.type.name, e)

    def get_history(self, limit: int = 10) -> List[DomainEvent]:
        """获取最近 N 个事件（用于诊断/调试）。"""
        return self._history[-limit:]

    def clear_history(self) -> None:
        self._history.clear()

    def reset(self) -> None:
        """重置（测试用）。"""
        self._subscribers.clear()
        self._history.clear()
