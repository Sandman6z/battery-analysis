# -*- coding: utf-8 -*-
"""
TestService服务定义

Domain层的服务，封装测试流程和测试结果管理的核心业务逻辑
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from battery_analysis.domain.entities.test_result import TestResult
from battery_analysis.domain.entities.test_profile import TestProfile
from battery_analysis.domain.entities.battery import Battery


class TestService(ABC):
    """测试服务接口"""
    
    @abstractmethod
    def create_test_result(self, battery: Battery, test_profile: TestProfile, 
                         test_data: Dict[str, Any], operator: str, 
                         equipment: str) -> TestResult:
        """创建测试结果
        
        Args:
            battery: 电池实体
            test_profile: 测试配置实体
            test_data: 测试数据
            operator: 测试操作员
            equipment: 测试设备
            
        Returns:
            创建的测试结果实体
        """
        pass
    
    @abstractmethod
    def update_test_result(self, test_result: TestResult, test_data: Dict[str, Any]) -> TestResult:
        """更新测试结果
        
        Args:
            test_result: 测试结果实体
            test_data: 更新的测试数据
            
        Returns:
            更新后的测试结果实体
        """
        pass
    
    @abstractmethod
    def validate_test_profile(self, test_profile: TestProfile) -> Dict[str, Any]:
        """验证测试配置是否有效
        
        Args:
            test_profile: 测试配置实体
            
        Returns:
            验证结果，包含是否有效和详细信息
        """
        pass
    
    @abstractmethod
    def generate_test_id(self, battery: Battery) -> str:
        """生成测试ID
        
        Args:
            battery: 电池实体
            
        Returns:
            生成的测试ID
        """
        pass
    
    @abstractmethod
    def get_test_summary(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """获取测试结果摘要
        
        Args:
            test_results: 测试结果列表
            
        Returns:
            测试结果摘要
        """
        pass
    
    @abstractmethod
    def calculate_test_statistics(self, test_results: List[TestResult]) -> Dict[str, float]:
        """计算测试统计信息
        
        Args:
            test_results: 测试结果列表
            
        Returns:
            测试统计信息
        """
        pass
    
    @abstractmethod
    def group_test_results_by_criteria(self, test_results: List[TestResult], 
                                      criteria: str) -> Dict[str, List[TestResult]]:
        """按指定条件分组测试结果
        
        Args:
            test_results: 测试结果列表
            criteria: 分组条件 (如: 'date', 'battery_type', 'operator')
            
        Returns:
            按条件分组的测试结果
        """
        pass
