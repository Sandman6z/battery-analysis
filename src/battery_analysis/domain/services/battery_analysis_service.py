# -*- coding: utf-8 -*-
"""
BatteryAnalysisService服务定义

Domain层的服务，封装电池分析的核心业务逻辑
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from battery_analysis.domain.entities.test_result import TestResult
from battery_analysis.domain.entities.battery import Battery
from battery_analysis.domain.entities.test_profile import TestProfile


class BatteryAnalysisService(ABC):
    """电池分析服务接口"""
    
    @abstractmethod
    def calculate_state_of_health(self, test_result: TestResult, battery: Battery) -> float:
        """计算电池健康状态(SOH)
        
        Args:
            test_result: 测试结果实体
            battery: 电池实体
            
        Returns:
            健康状态百分比 (0-100)
        """
        pass
    
    @abstractmethod
    def calculate_state_of_charge(self, voltage: float, battery: Battery) -> float:
        """计算电池充电状态(SOC)
        
        Args:
            voltage: 当前电压 (V)
            battery: 电池实体
            
        Returns:
            充电状态百分比 (0-100)
        """
        pass
    
    @abstractmethod
    def analyze_cycle_life(self, test_results: List[TestResult], battery: Battery) -> Dict[str, Any]:
        """分析电池循环寿命
        
        Args:
            test_results: 测试结果列表
            battery: 电池实体
            
        Returns:
            循环寿命分析结果
        """
        pass
    
    @abstractmethod
    def validate_test_result(self, test_result: TestResult, test_profile: TestProfile, battery: Battery) -> Dict[str, Any]:
        """验证测试结果是否符合测试配置要求
        
        Args:
            test_result: 测试结果实体
            test_profile: 测试配置实体
            battery: 电池实体
            
        Returns:
            验证结果，包含是否通过和详细信息
        """
        pass
    
    @abstractmethod
    def calculate_performance_metrics(self, test_result: TestResult, battery: Battery) -> Dict[str, float]:
        """计算电池性能指标
        
        Args:
            test_result: 测试结果实体
            battery: 电池实体
            
        Returns:
            性能指标字典
        """
        pass
    
    @abstractmethod
    def detect_anomalies(self, test_results: List[TestResult]) -> List[Dict[str, Any]]:
        """检测测试结果中的异常
        
        Args:
            test_results: 测试结果列表
            
        Returns:
            异常列表
        """
        pass
    
    @abstractmethod
    def compare_test_results(self, test_result1: TestResult, test_result2: TestResult) -> Dict[str, Any]:
        """比较两个测试结果
        
        Args:
            test_result1: 第一个测试结果
            test_result2: 第二个测试结果
            
        Returns:
            比较结果
        """
        pass
