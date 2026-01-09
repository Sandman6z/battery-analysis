# -*- coding: utf-8 -*-
"""
基础服务类
提供统一的错误处理、日志记录等公共功能
"""

import logging
from typing import Any, Optional, Tuple


class BaseService:
    """
    基础服务类
    提供统一的错误处理、日志记录等公共功能
    """
    
    def __init__(self):
        """
        初始化基础服务
        """
        self.logger = logging.getLogger(self.__class__.__name__)
    
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
            self.logger.error(f"操作失败: {str(e)}")
            return None


# 统一的异常类
class BatteryAnalysisException(Exception):
    """
    电池分析通用异常
    """
    
    def __init__(self, message: str, error_code: int = 500):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误码
        """
        super().__init__(message)
        self.error_code = error_code
    
    def __str__(self) -> str:
        """
        返回异常字符串表示
        """
        return f"{self.error_code}: {super().__str__()}"