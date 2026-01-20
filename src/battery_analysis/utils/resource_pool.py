"""
资源池管理模块

提供资源池的创建、获取、释放和管理功能，避免频繁创建和销毁资源，
提高系统性能和资源利用率。
"""
import logging
import threading
from typing import Dict, Optional, Any, Callable


class ResourcePool:
    """
    资源池类，用于管理和复用资源
    """
    
    # 全局资源池注册表
    _pools: Dict[str, 'ResourcePool'] = {}
    _pool_lock = threading.Lock()
    
    def __init__(self, name: str, create_func: Callable[[], Any], max_size: int = 10):
        """
        初始化资源池
        
        Args:
            name: 资源池名称
            create_func: 创建资源的函数
            max_size: 资源池最大大小
        """
        self.name = name
        self.create_func = create_func
        self.max_size = max_size
        self.resources = []
        self.in_use = set()
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # 注册资源池
        with ResourcePool._pool_lock:
            ResourcePool._pools[name] = self
        
        self.logger.info(f"创建资源池: {name}, 最大大小: {max_size}")
    
    def acquire(self) -> Optional[Any]:
        """
        从资源池获取资源
        
        Returns:
            Optional[Any]: 获取的资源，如果获取失败返回None
        """
        with self.lock:
            # 尝试从资源池中获取可用资源
            for i, resource in enumerate(self.resources):
                if i not in self.in_use:
                    self.in_use.add(i)
                    self.logger.debug(f"从资源池{self.name}获取资源: {i}")
                    return resource
            
            # 如果没有可用资源且未达到最大大小，创建新资源
            if len(self.resources) < self.max_size:
                try:
                    new_resource = self.create_func()
                    self.resources.append(new_resource)
                    resource_index = len(self.resources) - 1
                    self.in_use.add(resource_index)
                    self.logger.debug(f"在资源池{self.name}创建新资源: {resource_index}")
                    return new_resource
                except Exception as e:
                    self.logger.error(f"创建资源失败: {str(e)}")
                    return None
            
            self.logger.warning(f"资源池{self.name}已满，无法获取资源")
            return None
    
    def release(self, resource: Any) -> bool:
        """
        释放资源回资源池
        
        Args:
            resource: 要释放的资源
            
        Returns:
            bool: 释放是否成功
        """
        with self.lock:
            # 查找资源索引
            for i, res in enumerate(self.resources):
                if res is resource:
                    if i in self.in_use:
                        self.in_use.remove(i)
                        self.logger.debug(f"释放资源回资源池{self.name}: {i}")
                        return True
                    break
            
            self.logger.warning(f"资源不在使用中: {resource}")
            return False
    
    def size(self) -> int:
        """
        获取资源池大小
        
        Returns:
            int: 资源池大小
        """
        with self.lock:
            return len(self.resources)
    
    def in_use_count(self) -> int:
        """
        获取正在使用的资源数量
        
        Returns:
            int: 正在使用的资源数量
        """
        with self.lock:
            return len(self.in_use)
    
    def clear(self) -> None:
        """
        清空资源池
        """
        with self.lock:
            self.resources.clear()
            self.in_use.clear()
            self.logger.info(f"清空资源池: {self.name}")
    
    @classmethod
    def get_pool(cls, name: str) -> Optional['ResourcePool']:
        """
        获取资源池
        
        Args:
            name: 资源池名称
            
        Returns:
            Optional[ResourcePool]: 资源池对象
        """
        with cls._pool_lock:
            return cls._pools.get(name)
    
    @classmethod
    def create_pool(cls, name: str, create_func: Callable[[], Any], max_size: int = 10) -> 'ResourcePool':
        """
        创建资源池
        
        Args:
            name: 资源池名称
            create_func: 创建资源的函数
            max_size: 资源池最大大小
            
        Returns:
            ResourcePool: 资源池对象
        """
        with cls._pool_lock:
            if name not in cls._pools:
                cls._pools[name] = ResourcePool(name, create_func, max_size)
            return cls._pools[name]
    
    @classmethod
    def remove_pool(cls, name: str) -> bool:
        """
        移除资源池
        
        Args:
            name: 资源池名称
            
        Returns:
            bool: 是否成功移除
        """
        with cls._pool_lock:
            if name in cls._pools:
                pool = cls._pools.pop(name)
                pool.clear()
                logging.getLogger(__name__).info(f"移除资源池: {name}")
                return True
            return False
