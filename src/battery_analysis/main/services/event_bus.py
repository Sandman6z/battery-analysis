# -*- coding: utf-8 -*-
"""
事件总线模块

实现发布-订阅模式的事件总线，用于解耦模块间的通信
"""

import logging
import time
from enum import Enum, auto
from typing import Callable, Dict, List, Any, Optional


class EventType(Enum):
    """
    事件类型枚举
    """
    PROGRESS_UPDATED = auto()
    STATUS_CHANGED = auto()
    ANALYSIS_COMPLETED = auto()
    VISUALIZER_REQUESTED = auto()
    CONFIG_CHANGED = auto()
    FILE_SELECTED = auto()


class Event:
    """
    事件类，封装事件数据
    """

    def __init__(self, event_type: EventType, data: Any = None):
        """
        初始化事件

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        self.event_type = event_type
        self.data = data
        self.timestamp = time.time()
        self.event_id = id(self)

    def __str__(self):
        return f"Event({self.event_type.name}, data={self.data})"


class EventBus:
    """
    事件总线类

    实现发布-订阅模式，用于模块间的解耦通信
    """

    _instance: Optional['EventBus'] = None

    @classmethod
    def get_instance(cls) -> 'EventBus':
        """
        获取事件总线单例实例

        Returns:
            EventBus: 事件总线实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """
        初始化事件总线
        """
        self.logger = logging.getLogger(__name__)

        # 存储事件订阅者，格式：{EventType: [callback, ...]}
        self._subscribers: Dict[EventType, List[Callable]] = {}

        self.logger.info("EventBus initialized")

    def subscribe(self, event_type: EventType, callback: Callable) -> bool:
        """
        订阅事件

        Args:
            event_type: 事件类型
            callback: 回调函数

        Returns:
            bool: 订阅是否成功
        """
        try:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []

            self._subscribers[event_type].append(callback)

            self.logger.debug("Subscribed to event: %s", event_type.name)
            return True

        except (TypeError, MemoryError) as e:
            self.logger.error("Failed to subscribe to event %s: %s", event_type.name, e)
            return False

    def unsubscribe(self, event_type: EventType, callback: Callable) -> bool:
        """
        取消订阅事件

        Args:
            event_type: 事件类型
            callback: 回调函数

        Returns:
            bool: 取消订阅是否成功
        """
        try:
            if event_type in self._subscribers:
                for i, cb in enumerate(self._subscribers[event_type]):
                    if cb == callback:
                        self._subscribers[event_type].pop(i)
                        self.logger.debug("Unsubscribed from event: %s", event_type.name)
                        return True

            self.logger.warning("Callback not found for event: %s", event_type.name)
            return False

        except (TypeError, ValueError) as e:
            self.logger.error("Failed to unsubscribe from event %s: %s", event_type.name, e)
            return False

    def emit(self, event_type: EventType, data: Any = None):
        """
        发布事件

        Args:
            event_type: 事件类型
            data: 事件数据，可选
        """
        try:
            event = Event(event_type, data)
            self._process_event(event)
            self.logger.debug("Event emitted: %s", event)
        except (TypeError, AttributeError) as e:
            self.logger.error("Failed to emit event %s: %s", event_type.name, e)

    def _process_event(self, event: Event):
        """
        处理事件，调用所有匹配的订阅者

        Args:
            event: 事件对象
        """
        try:
            if event.event_type in self._subscribers:
                for callback in self._subscribers[event.event_type]:
                    try:
                        callback(event)
                    except (TypeError, AttributeError, ValueError, OSError) as e:
                        self.logger.error("Error in event callback for %s: %s", event.event_type.name, e)
        except (TypeError, AttributeError) as e:
            self.logger.error("Failed to process event %s: %s", event.event_type.name, e)

