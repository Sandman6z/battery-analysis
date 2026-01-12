# -*- coding: utf-8 -*-
"""
TestResultRepository接口定义

Domain层的仓库接口，定义测试结果的持久化和查询操作
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from battery_analysis.domain.entities.test_result import TestResult


class TestResultRepository(ABC):
    """测试结果仓库接口"""
    
    @abstractmethod
    def save(self, test_result: TestResult) -> TestResult:
        """保存测试结果
        
        Args:
            test_result: 测试结果实体对象
            
        Returns:
            保存后的测试结果实体对象
        """
        pass
    
    @abstractmethod
    def find_by_id(self, test_id: str) -> Optional[TestResult]:
        """根据ID查找测试结果
        
        Args:
            test_id: 测试结果ID
            
        Returns:
            测试结果实体对象，或None
        """
        pass
    
    @abstractmethod
    def find_by_battery_serial(self, serial_number: str) -> List[TestResult]:
        """根据电池序列号查找测试结果
        
        Args:
            serial_number: 电池序列号
            
        Returns:
            测试结果实体对象列表
        """
        pass
    
    @abstractmethod
    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[TestResult]:
        """根据日期范围查找测试结果
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            测试结果实体对象列表
        """
        pass
    
    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[TestResult]:
        """查找所有测试结果
        
        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量
            
        Returns:
            测试结果实体对象列表
        """
        pass
    
    @abstractmethod
    def update(self, test_result: TestResult) -> TestResult:
        """更新测试结果
        
        Args:
            test_result: 测试结果实体对象
            
        Returns:
            更新后的测试结果实体对象
        """
        pass
    
    @abstractmethod
    def delete(self, test_id: str) -> bool:
        """删除测试结果
        
        Args:
            test_id: 测试结果ID
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    def count_by_battery_serial(self, serial_number: str) -> int:
        """统计电池的测试结果数量
        
        Args:
            serial_number: 电池序列号
            
        Returns:
            测试结果数量
        """
        pass
