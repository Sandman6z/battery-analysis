# -*- coding: utf-8 -*-
"""
事件总线模块

实现发布-订阅模式的事件总线，用于解耦模块间的通信
"""

import logging
from typing import Callable, Dict, List, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class EventBus(QObject):
    """
    事件总线类
    
    实现发布-订阅模式，用于模块间的解耦通信
    """
    
    # 定义事件信号
    progress_updated = pyqtSignal(int, str)  # 进度更新信号
    status_changed = pyqtSignal(bool, int, str)  # 状态变化信号
    analysis_completed = pyqtSignal()  # 分析完成信号
    visualizer_requested = pyqtSignal()  # 可视化器请求信号
    config_changed = pyqtSignal(str, Any)  # 配置变更信号
    file_selected = pyqtSignal(str)  # 文件选择信号
    language_changed = pyqtSignal(str)  # 语言变更信号
    
    def __init__(self):
        """
        初始化事件总线
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 存储事件订阅者
        self._subscribers: Dict[str, List[Callable]] = {}
        
        # 连接内部信号到事件处理
        self._connect_internal_signals()
        
        self.logger.info("EventBus initialized")
    
    def _connect_internal_signals(self):
        """
        连接内部信号到事件处理
        """
        # 连接进度更新信号
        self.progress_updated.connect(self._on_progress_updated)
        
        # 连接状态变化信号
        self.status_changed.connect(self._on_status_changed)
        
        # 连接分析完成信号
        self.analysis_completed.connect(self._on_analysis_completed)
        
        # 连接可视化器请求信号
        self.visualizer_requested.connect(self._on_visualizer_requested)
        
        # 连接配置变更信号
        self.config_changed.connect(self._on_config_changed)
        
        # 连接文件选择信号
        self.file_selected.connect(self._on_file_selected)
        
        # 连接语言变更信号
        self.language_changed.connect(self._on_language_changed)
    
    @pyqtSlot(int, str)
    def _on_progress_updated(self, progress: int, status: str):
        """
        处理进度更新事件

        Args:
            progress: 进度值
            status: 状态文本
        """
        self._emit_event("progress_updated", progress, status)
    
    @pyqtSlot(bool, int, str)
    def _on_status_changed(self, status: bool, code: int, message: str):
        """
        处理状态变化事件

        Args:
            status: 状态布尔值
            code: 状态码
            message: 状态消息
        """
        self._emit_event("status_changed", status, code, message)
    
    @pyqtSlot()
    def _on_analysis_completed(self):
        """
        处理分析完成事件
        """
        self._emit_event("analysis_completed")
    
    @pyqtSlot()
    def _on_visualizer_requested(self):
        """
        处理可视化器请求事件
        """
        self._emit_event("visualizer_requested")
    
    @pyqtSlot(str, Any)
    def _on_config_changed(self, key: str, value: Any):
        """
        处理配置变更事件

        Args:
            key: 配置键
            value: 配置值
        """
        self._emit_event("config_changed", key, value)
    
    @pyqtSlot(str)
    def _on_file_selected(self, file_path: str):
        """
        处理文件选择事件

        Args:
            file_path: 文件路径
        """
        self._emit_event("file_selected", file_path)
    
    @pyqtSlot(str)
    def _on_language_changed(self, language_code: str):
        """
        处理语言变更事件

        Args:
            language_code: 语言代码
        """
        self._emit_event("language_changed", language_code)
    
    def subscribe(self, event_name: str, callback: Callable) -> bool:
        """
        订阅事件

        Args:
            event_name: 事件名称
            callback: 回调函数

        Returns:
            bool: 订阅是否成功
        """
        try:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            
            self._subscribers[event_name].append(callback)
            self.logger.debug("Subscribed to event: %s", event_name)
            return True
            
        except Exception as e:
            self.logger.error("Failed to subscribe to event %s: %s", event_name, e)
            return False
    
    def unsubscribe(self, event_name: str, callback: Callable) -> bool:
        """
        取消订阅事件

        Args:
            event_name: 事件名称
            callback: 回调函数

        Returns:
            bool: 取消订阅是否成功
        """
        try:
            if event_name in self._subscribers and callback in self._subscribers[event_name]:
                self._subscribers[event_name].remove(callback)
                self.logger.debug("Unsubscribed from event: %s", event_name)
                return True
            else:
                self.logger.warning("Callback not found for event: %s", event_name)
                return False
                
        except Exception as e:
            self.logger.error("Failed to unsubscribe from event %s: %s", event_name, e)
            return False
    
    def emit(self, event_name: str, *args, **kwargs):
        """
        发布事件

        Args:
            event_name: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数
        """
        try:
            if event_name in self._subscribers:
                for callback in self._subscribers[event_name]:
                    try:
                        callback(*args, **kwargs)
                    except Exception as e:
                        self.logger.error("Error in event callback for %s: %s", event_name, e)
            
            self.logger.debug("Event emitted: %s", event_name)
            
        except Exception as e:
            self.logger.error("Failed to emit event %s: %s", event_name, e)
    
    def _emit_event(self, event_name: str, *args, **kwargs):
        """
        内部事件发布方法

        Args:
            event_name: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self.emit(event_name, *args, **kwargs)
    
    def get_subscribers(self, event_name: str) -> List[Callable]:
        """
        获取事件订阅者列表

        Args:
            event_name: 事件名称

        Returns:
            List[Callable]: 订阅者列表
        """
        return self._subscribers.get(event_name, [])
    
    def get_all_subscribers(self) -> Dict[str, List[Callable]]:
        """
        获取所有事件订阅者

        Returns:
            Dict[str, List[Callable]]: 所有事件订阅者
        """
        return self._subscribers.copy()
    
    def clear_subscribers(self, event_name: str = None):
        """
        清除事件订阅者

        Args:
            event_name: 事件名称，如果为None则清除所有订阅者
        """
        if event_name:
            if event_name in self._subscribers:
                self._subscribers[event_name].clear()
                self.logger.debug("Cleared subscribers for event: %s", event_name)
        else:
            self._subscribers.clear()
            self.logger.debug("Cleared all subscribers")
    
    def has_subscribers(self, event_name: str) -> bool:
        """
        检查事件是否有订阅者

        Args:
            event_name: 事件名称

        Returns:
            bool: 是否有订阅者
        """
        return event_name in self._subscribers and len(self._subscribers[event_name]) > 0
    
    def get_event_names(self) -> List[str]:
        """
        获取所有事件名称

        Returns:
            List[str]: 事件名称列表
        """
        return list(self._subscribers.keys())