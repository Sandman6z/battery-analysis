# -*- coding: utf-8 -*-
"""
初始化步骤抽象基类

定义初始化步骤的统一接口，实现初始化流程的模块化
"""

from abc import ABC, abstractmethod
import logging
from typing import Optional, Dict, Any


class InitializationStep(ABC):
    """初始化步骤抽象基类"""
    
    def __init__(self, name: str, priority: int = 50):
        """
        初始化步骤
        
        Args:
            name: 步骤名称
            priority: 执行优先级，数字越小优先级越高
        """
        self.name = name
        self.priority = priority
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._dependencies: Dict[str, Any] = {}
    
    @abstractmethod
    def execute(self, main_window) -> bool:
        """
        执行初始化步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        pass
    
    def get_name(self) -> str:
        """
        获取步骤名称
        
        Returns:
            步骤名称
        """
        return self.name
    
    def get_priority(self) -> int:
        """
        获取执行优先级
        
        Returns:
            执行优先级
        """
        return self.priority
    
    def add_dependency(self, dependency_name: str, dependency: Any) -> None:
        """
        添加依赖项
        
        Args:
            dependency_name: 依赖名称
            dependency: 依赖对象
        """
        self._dependencies[dependency_name] = dependency
    
    def get_dependency(self, dependency_name: str) -> Optional[Any]:
        """
        获取依赖项
        
        Args:
            dependency_name: 依赖名称
            
        Returns:
            依赖对象，或None
        """
        return self._dependencies.get(dependency_name)
    
    def can_execute(self, main_window) -> bool:
        """
        检查是否可以执行此步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否可以执行
        """
        return True
    
    def __lt__(self, other):
        """
        用于排序，优先级低的步骤排在后面
        """
        return self.priority < other.priority
