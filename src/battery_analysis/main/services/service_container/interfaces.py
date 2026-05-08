# -*- coding: utf-8 -*-
"""
服务容器接口定义
"""

from typing import Optional, TypeVar, Type, Generic
from abc import ABC, abstractmethod


T = TypeVar('T')


class IServiceContainer(Generic[T], ABC):
    """
    服务容器接口
    """

    @abstractmethod
    def register(self, name: str, implementation: Type[T], singleton: bool = True) -> bool:
        """
        注册服务

        Args:
            name: 服务名称
            implementation: 实现类
            singleton: 是否单例

        Returns:
            bool: 注册是否成功
        """
        pass

    @abstractmethod
    def register_instance(self, name: str, instance: T) -> bool:
        """
        注册实例

        Args:
            name: 服务名称
            instance: 服务实例

        Returns:
            bool: 注册是否成功
        """
        pass

    @abstractmethod
    def get(self, name: str) -> Optional[T]:
        """
        获取服务

        Args:
            name: 服务名称

        Returns:
            T: 服务实例，如果不存在则返回None
        """
        pass

    @abstractmethod
    def has(self, name: str) -> bool:
        """
        检查服务是否存在

        Args:
            name: 服务名称

        Returns:
            bool: 服务是否存在
        """
        pass

    @abstractmethod
    def unregister(self, name: str) -> bool:
        """
        注销服务

        Args:
            name: 服务名称

        Returns:
            bool: 注销是否成功
        """
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """
        关闭容器

        Returns:
            bool: 关闭是否成功
        """
        pass
