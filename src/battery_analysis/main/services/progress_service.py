# -*- coding: utf-8 -*-
"""
进度服务模块

提供进度管理的抽象接口和实现
"""

import logging
from typing import Optional, Callable, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class IProgressService:
    """
    进度服务接口
    """
    
    def update_progress(self, progress: int, status: str = "") -> bool:
        """
        更新进度

        Args:
            progress: 进度值 (0-100)
            status: 状态文本

        Returns:
            bool: 更新是否成功
        """
        raise NotImplementedError
    
    def get_progress(self) -> int:
        """
        获取当前进度

        Returns:
            int: 当前进度值
        """
        raise NotImplementedError
    
    def get_status(self) -> str:
        """
        获取当前状态

        Returns:
            str: 当前状态文本
        """
        raise NotImplementedError
    
    def reset_progress(self) -> bool:
        """
        重置进度

        Returns:
            bool: 重置是否成功
        """
        raise NotImplementedError
    
    def is_completed(self) -> bool:
        """
        检查是否完成

        Returns:
            bool: 是否完成
        """
        raise NotImplementedError


class ProgressService(QObject, IProgressService):
    """
    进度服务实现
    """
    
    # 定义信号
    progress_changed = pyqtSignal(int, str)  # 进度变化信号
    progress_completed = pyqtSignal()  # 进度完成信号
    progress_started = pyqtSignal()  # 进度开始信号
    
    def __init__(self):
        """
        初始化进度服务
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 进度状态
        self._progress = 0
        self._status = ""
        self._is_completed = False
        self._is_active = False
        
        # 进度回调
        self._progress_callbacks: Dict[str, Callable] = {}
        
        # 连接内部信号
        self._connect_signals()
        
    def _connect_signals(self):
        """
        连接信号
        """
        self.progress_changed.connect(self._on_progress_changed)
        self.progress_completed.connect(self._on_progress_completed)
        self.progress_started.connect(self._on_progress_started)
        
    @pyqtSlot(int, str)
    def _on_progress_changed(self, progress: int, status: str):
        """
        处理进度变化事件

        Args:
            progress: 进度值
            status: 状态文本
        """
        self.logger.debug("Progress changed: %s%% - %s", progress, status)
        
        # 调用注册的回调函数
        for callback in self._progress_callbacks.values():
            try:
                callback(progress, status)
            except Exception as e:
                self.logger.error("Error in progress callback: %s", e)
    
    @pyqtSlot()
    def _on_progress_completed(self):
        """
        处理进度完成事件
        """
        self.logger.info("Progress completed")
        self._is_completed = True
        self._is_active = False
    
    @pyqtSlot()
    def _on_progress_started(self):
        """
        处理进度开始事件
        """
        self.logger.info("Progress started")
        self._is_completed = False
        self._is_active = True
    
    def initialize(self) -> bool:
        """
        初始化进度服务

        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("Initializing ProgressService...")
            
            # 重置进度状态
            self.reset_progress()
            
            self.logger.info("ProgressService initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error("Failed to initialize ProgressService: %s", e)
            return False
    
    def update_progress(self, progress: int, status: str = "") -> bool:
        """
        更新进度

        Args:
            progress: 进度值 (0-100)
            status: 状态文本

        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证进度值
            progress = max(0, min(100, progress))
            
            # 更新内部状态
            self._progress = progress
            self._status = status
            
            # 发射信号
            self.progress_changed.emit(progress, status)
            
            # 检查是否完成
            if progress >= 100 and not self._is_completed:
                self.progress_completed.emit()
            elif progress > 0 and not self._is_active:
                self.progress_started.emit()
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to update progress: %s", e)
            return False
    
    def get_progress(self) -> int:
        """
        获取当前进度

        Returns:
            int: 当前进度值
        """
        return self._progress
    
    def get_status(self) -> str:
        """
        获取当前状态

        Returns:
            str: 当前状态文本
        """
        return self._status
    
    def reset_progress(self) -> bool:
        """
        重置进度

        Returns:
            bool: 重置是否成功
        """
        try:
            self._progress = 0
            self._status = ""
            self._is_completed = False
            self._is_active = False
            
            self.logger.info("Progress reset")
            return True
            
        except Exception as e:
            self.logger.error("Failed to reset progress: %s", e)
            return False
    
    def is_completed(self) -> bool:
        """
        检查是否完成

        Returns:
            bool: 是否完成
        """
        return self._is_completed
    
    def is_active(self) -> bool:
        """
        检查是否正在运行

        Returns:
            bool: 是否正在运行
        """
        return self._is_active
    
    def register_callback(self, callback_id: str, callback: Callable[[int, str], None]) -> bool:
        """
        注册进度回调

        Args:
            callback_id: 回调ID
            callback: 回调函数

        Returns:
            bool: 注册是否成功
        """
        try:
            self._progress_callbacks[callback_id] = callback
            self.logger.debug("Progress callback registered: %s", callback_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to register progress callback %s: %s", callback_id, e)
            return False
    
    def unregister_callback(self, callback_id: str) -> bool:
        """
        取消注册进度回调

        Args:
            callback_id: 回调ID

        Returns:
            bool: 取消注册是否成功
        """
        try:
            if callback_id in self._progress_callbacks:
                del self._progress_callbacks[callback_id]
                self.logger.debug("Progress callback unregistered: %s", callback_id)
                return True
            else:
                self.logger.warning("Callback not found: %s", callback_id)
                return False
                
        except Exception as e:
            self.logger.error("Failed to unregister progress callback %s: %s", callback_id, e)
            return False
    
    def set_indeterminate(self, status: str = "Processing...") -> bool:
        """
        设置不确定进度（无限进度条）

        Args:
            status: 状态文本

        Returns:
            bool: 设置是否成功
        """
        try:
            self._is_active = True
            self._is_completed = False
            self._status = status
            self._progress = -1  # 使用-1表示不确定进度
            
            # 发射信号但不包含进度值
            self.progress_changed.emit(-1, status)
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to set indeterminate progress: %s", e)
            return False
    
    def is_indeterminate(self) -> bool:
        """
        检查是否为不确定进度

        Returns:
            bool: 是否为不确定进度
        """
        return self._progress == -1
    
    def shutdown(self):
        """
        关闭进度服务
        """
        self.logger.info("Shutting down ProgressService...")
        self.reset_progress()
        self._progress_callbacks.clear()
