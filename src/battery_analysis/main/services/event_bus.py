# -*- coding: utf-8 -*-
"""
事件总线模块

实现发布-订阅模式的事件总线，用于解耦模块间的通信
"""

import logging
import asyncio
from enum import Enum, auto
from typing import Callable, Dict, List, Any, Optional, Tuple, Set
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread


class EventPriority(Enum):
    """
    事件优先级枚举
    """
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


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
    LANGUAGE_CHANGED = auto()
    BATTERY_DATA_LOADED = auto()
    CHART_UPDATED = auto()
    USER_SETTING_CHANGED = auto()
    ERROR_OCCURRED = auto()


class Event:
    """
    事件类，封装事件数据
    """
    
    def __init__(self, event_type: EventType, data: Any = None, priority: EventPriority = EventPriority.NORMAL):
        """
        初始化事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            priority: 事件优先级
        """
        self.event_type = event_type
        self.data = data
        self.priority = priority
        self.timestamp = asyncio.get_event_loop().time()
        self.event_id = id(self)
    
    def __str__(self):
        return f"Event({self.event_type.name}, priority={self.priority.name}, data={self.data})"


class EventFilter:
    """
    事件过滤器基类
    """
    
    def __call__(self, event: Event) -> bool:
        """
        判断事件是否应该被处理
        
        Args:
            event: 事件对象
            
        Returns:
            bool: 是否处理事件
        """
        return True


class EventBus(QObject):
    """
    事件总线类
    
    实现发布-订阅模式，用于模块间的解耦通信
    """
    
    # 定义事件信号
    event_emitted = pyqtSignal(Event)  # 统一事件信号
    
    # 单例实例
    _instance: Optional['EventBus'] = None
    _lock = asyncio.Lock()
    
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
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 存储事件订阅者，格式：{EventType: [(callback, filter, priority)]}
        self._subscribers: Dict[EventType, List[Tuple[Callable, EventFilter, EventPriority]]] = {}
        
        # 存储事件历史记录
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        
        # 连接统一事件信号
        self.event_emitted.connect(self._on_event_emitted)
        
        self.logger.info("EventBus initialized")
    
    @pyqtSlot(Event)
    def _on_event_emitted(self, event: Event):
        """
        处理统一事件信号
        
        Args:
            event: 事件对象
        """
        self._process_event(event)
    
    def subscribe(self, event_type: EventType, callback: Callable, 
                  event_filter: EventFilter = None, 
                  priority: EventPriority = EventPriority.NORMAL) -> bool:
        """
        订阅事件

        Args:
            event_type: 事件类型
            callback: 回调函数
            event_filter: 事件过滤器，可选
            priority: 订阅优先级，可选

        Returns:
            bool: 订阅是否成功
        """
        try:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            # 使用默认过滤器如果没有提供
            if event_filter is None:
                event_filter = EventFilter()
            
            # 添加订阅者，按优先级排序
            self._subscribers[event_type].append((callback, event_filter, priority))
            # 按优先级降序排序
            self._subscribers[event_type].sort(key=lambda x: x[2].value, reverse=True)
            
            self.logger.debug("Subscribed to event: %s with priority: %s", event_type.name, priority.name)
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
                # 查找并移除订阅者
                for i, (cb, _, _) in enumerate(self._subscribers[event_type]):
                    if cb == callback:
                        self._subscribers[event_type].pop(i)
                        self.logger.debug("Unsubscribed from event: %s", event_type.name)
                        return True
            
            self.logger.warning("Callback not found for event: %s", event_type.name)
            return False
            
        except (TypeError, ValueError) as e:
            self.logger.error("Failed to unsubscribe from event %s: %s", event_type.name, e)
            return False
    
    def emit(self, event_type: EventType, data: Any = None, priority: EventPriority = EventPriority.NORMAL):
        """
        发布事件

        Args:
            event_type: 事件类型
            data: 事件数据，可选
            priority: 事件优先级，可选
        """
        try:
            # 创建事件对象
            event = Event(event_type, data, priority)
            
            # 记录事件历史
            self._add_to_history(event)
            
            # 发送信号
            self.event_emitted.emit(event)
            
            self.logger.debug("Event emitted: %s", event)
            return event
            
        except (TypeError, AttributeError) as e:
            self.logger.error("Failed to emit event %s: %s", event_type.name, e)
            return None
    
    def emit_async(self, event_type: EventType, data: Any = None, priority: EventPriority = EventPriority.NORMAL):
        """
        异步发布事件

        Args:
            event_type: 事件类型
            data: 事件数据，可选
            priority: 事件优先级，可选
        """
        asyncio.create_task(self._emit_async(event_type, data, priority))
    
    async def _emit_async(self, event_type: EventType, data: Any = None, priority: EventPriority = EventPriority.NORMAL):
        """
        异步发布事件的内部方法
        
        Args:
            event_type: 事件类型
            data: 事件数据，可选
            priority: 事件优先级，可选
        """
        self.emit(event_type, data, priority)
    
    def _process_event(self, event: Event):
        """
        处理事件，调用所有匹配的订阅者
        
        Args:
            event: 事件对象
        """
        try:
            if event.event_type in self._subscribers:
                for callback, event_filter, _ in self._subscribers[event.event_type]:
                    try:
                        # 检查过滤器
                        if event_filter(event):
                            # 调用回调函数
                            callback(event)
                    except (TypeError, AttributeError, ValueError, OSError) as e:
                        # 回调函数中的异常应该被记录但不影响其他回调
                        self.logger.error("Error in event callback for %s: %s", event.event_type.name, e)
        except (TypeError, AttributeError) as e:
            self.logger.error("Failed to process event %s: %s", event.event_type.name, e)
    
    def _add_to_history(self, event: Event):
        """
        添加事件到历史记录
        
        Args:
            event: 事件对象
        """
        self._event_history.append(event)
        # 限制历史记录大小
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
    
    def get_subscribers(self, event_type: EventType) -> List[Tuple[Callable, EventFilter, EventPriority]]:
        """
        获取事件订阅者列表

        Args:
            event_type: 事件类型

        Returns:
            List[Tuple[Callable, EventFilter, EventPriority]]: 订阅者列表
        """
        return self._subscribers.get(event_type, [])
    
    def get_all_subscribers(self) -> Dict[EventType, List[Tuple[Callable, EventFilter, EventPriority]]]:
        """
        获取所有事件订阅者

        Returns:
            Dict[EventType, List[Tuple[Callable, EventFilter, EventPriority]]]: 所有事件订阅者
        """
        return self._subscribers.copy()
    
    def clear_subscribers(self, event_type: EventType = None):
        """
        清除事件订阅者

        Args:
            event_type: 事件类型，如果为None则清除所有订阅者
        """
        if event_type:
            if event_type in self._subscribers:
                self._subscribers[event_type].clear()
                self.logger.debug("Cleared subscribers for event: %s", event_type.name)
        else:
            self._subscribers.clear()
            self.logger.debug("Cleared all subscribers")
    
    def has_subscribers(self, event_type: EventType) -> bool:
        """
        检查事件是否有订阅者

        Args:
            event_type: 事件类型

        Returns:
            bool: 是否有订阅者
        """
        return event_type in self._subscribers and len(self._subscribers[event_type]) > 0
    
    def get_event_types(self) -> List[EventType]:
        """
        获取所有事件类型

        Returns:
            List[EventType]: 事件类型列表
        """
        return list(self._subscribers.keys())
    
    def get_event_history(self, event_type: EventType = None, limit: int = None) -> List[Event]:
        """
        获取事件历史记录

        Args:
            event_type: 事件类型，可选，指定则只返回该类型的事件
            limit: 返回的最大事件数，可选

        Returns:
            List[Event]: 事件历史记录
        """
        # 过滤事件类型
        if event_type:
            history = [event for event in self._event_history if event.event_type == event_type]
        else:
            history = self._event_history.copy()
        
        # 限制返回数量
        if limit:
            history = history[-limit:]
        
        return history
    
    def clear_event_history(self):
        """
        清除事件历史记录
        """
        self._event_history.clear()
        self.logger.debug("Cleared event history")
    
    def set_max_history_size(self, size: int):
        """
        设置事件历史记录的最大大小
        
        Args:
            size: 最大大小
        """
        self._max_history_size = size
        # 裁剪历史记录
        if len(self._event_history) > size:
            self._event_history = self._event_history[-size:]
        self.logger.debug("Set max history size to: %d", size)
    
    # 兼容旧版本的方法
    def legacy_emit_progress_updated(self, progress: int, status: str):
        """
        兼容旧版本的进度更新事件
        
        Args:
            progress: 进度值
            status: 状态文本
        """
        self.emit(EventType.PROGRESS_UPDATED, {"progress": progress, "status": status})
    
    def legacy_emit_status_changed(self, status: bool, code: int, message: str):
        """
        兼容旧版本的状态变化事件
        
        Args:
            status: 状态布尔值
            code: 状态码
            message: 状态消息
        """
        self.emit(EventType.STATUS_CHANGED, {"status": status, "code": code, "message": message})
    
    def legacy_emit_analysis_completed(self):
        """
        兼容旧版本的分析完成事件
        """
        self.emit(EventType.ANALYSIS_COMPLETED)
    
    def legacy_emit_visualizer_requested(self):
        """
        兼容旧版本的可视化器请求事件
        """
        self.emit(EventType.VISUALIZER_REQUESTED)
    
    def legacy_emit_config_changed(self, key: str, value: Any):
        """
        兼容旧版本的配置变更事件
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.emit(EventType.CONFIG_CHANGED, {"key": key, "value": value})
    
    def legacy_emit_file_selected(self, file_path: str):
        """
        兼容旧版本的文件选择事件
        
        Args:
            file_path: 文件路径
        """
        self.emit(EventType.FILE_SELECTED, {"file_path": file_path})
    
    def legacy_emit_language_changed(self, language_code: str):
        """
        兼容旧版本的语言变更事件
        
        Args:
            language_code: 语言代码
        """
        self.emit(EventType.LANGUAGE_CHANGED, {"language_code": language_code})
