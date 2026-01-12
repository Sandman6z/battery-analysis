# -*- coding: utf-8 -*-
"""
TestProfileRepository接口定义

Domain层的仓库接口，定义测试配置文件的持久化和查询操作
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from battery_analysis.domain.entities.test_profile import TestProfile


class TestProfileRepository(ABC):
    """测试配置文件仓库接口"""
    
    @abstractmethod
    def save(self, test_profile: TestProfile) -> TestProfile:
        """保存测试配置文件
        
        Args:
            test_profile: 测试配置文件实体对象
            
        Returns:
            保存后的测试配置文件实体对象
        """
        pass
    
    @abstractmethod
    def find_by_id(self, profile_id: str) -> Optional[TestProfile]:
        """根据ID查找测试配置文件
        
        Args:
            profile_id: 测试配置文件ID
            
        Returns:
            测试配置文件实体对象，或None
        """
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> List[TestProfile]:
        """根据名称查找测试配置文件
        
        Args:
            name: 测试配置文件名称
            
        Returns:
            测试配置文件实体对象列表
        """
        pass
    
    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[TestProfile]:
        """根据电池类型查找测试配置文件
        
        Args:
            battery_type: 电池类型
            
        Returns:
            测试配置文件实体对象列表
        """
        pass
    
    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[TestProfile]:
        """根据制造商查找测试配置文件
        
        Args:
            manufacturer: 制造商
            
        Returns:
            测试配置文件实体对象列表
        """
        pass
    
    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[TestProfile]:
        """查找所有测试配置文件
        
        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量
            
        Returns:
            测试配置文件实体对象列表
        """
        pass
    
    @abstractmethod
    def update(self, test_profile: TestProfile) -> TestProfile:
        """更新测试配置文件
        
        Args:
            test_profile: 测试配置文件实体对象
            
        Returns:
            更新后的测试配置文件实体对象
        """
        pass
    
    @abstractmethod
    def delete(self, profile_id: str) -> bool:
        """删除测试配置文件
        
        Args:
            profile_id: 测试配置文件ID
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """统计测试配置文件数量
        
        Returns:
            测试配置文件数量
        """
        pass
