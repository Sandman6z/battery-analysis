# -*- coding: utf-8 -*-
"""
工具函数包
提供各种通用工具函数和装饰器
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional
import time
import hashlib


class Cache:
    """
    通用缓存类，支持内存缓存
    """
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        初始化缓存
        
        Args:
            max_size: 缓存最大容量
            ttl: 缓存过期时间（秒）
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, tuple] = {}
    
    def _generate_key(self, func: Callable, *args, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            func: 函数对象
            args: 函数参数
            kwargs: 函数关键字参数
        
        Returns:
            str: 缓存键
        """
        key = f"{func.__module__}.{func.__name__}"
        key += f"{args}"
        key += f"{sorted(kwargs.items())}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            Any: 缓存值或None
        """
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        # 检查缓存是否过期
        if time.time() - timestamp > self.ttl:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
        """
        # 如果缓存已满，删除最旧的缓存
        if len(self._cache) >= self.max_size:
            # 删除最旧的缓存
            oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        
        self._cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """
        清空缓存
        """
        self._cache.clear()
    
    def delete(self, key: str) -> None:
        """
        删除缓存
        
        Args:
            key: 缓存键
        """
        if key in self._cache:
            del self._cache[key]
    
    def size(self) -> int:
        """
        获取缓存大小
        
        Returns:
            int: 缓存大小
        """
        return len(self._cache)


# 全局缓存实例
_global_cache = Cache()


def cache(max_size: int = 1000, ttl: int = 3600):
    """
    缓存装饰器
    
    Args:
        max_size: 缓存最大容量
        ttl: 缓存过期时间（秒）
    
    Returns:
        Callable: 装饰后的函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = _global_cache._generate_key(func, *args, **kwargs)
            
            # 检查缓存
            cached_value = _global_cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            _global_cache.set(key, result)
            
            return result
        
        # 添加缓存管理方法
        wrapper.clear_cache = _global_cache.clear
        wrapper.delete_cache = lambda k=None: _global_cache.delete(k) if k else _global_cache.clear()
        wrapper.cache_size = _global_cache.size
        
        return wrapper
    
    return decorator


def clear_all_caches() -> None:
    """
    清空所有缓存
    """
    _global_cache.clear()


# 导入日志管理和错误报告功能
from battery_analysis.utils.log_manager import (
    get_logger,
    get_log_directory,
    clear_old_logs
)
from battery_analysis.utils.error_report_generator import (
    generate_error_report,
    get_report_info
)

# 导出公共API
__all__ = [
    'Cache',
    'cache',
    'clear_all_caches',
    'get_logger',
    'get_log_directory',
    'clear_old_logs',
    'generate_error_report',
    'get_report_info'
]