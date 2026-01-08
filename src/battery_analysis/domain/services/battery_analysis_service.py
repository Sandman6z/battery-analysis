"""
BatteryAnalysisService接口定义

Domain层的服务接口，定义电池分析的核心业务逻辑
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from battery_analysis.domain.entities.battery import Battery


class BatteryAnalysisService(ABC):
    """电池分析服务接口"""
    
    @abstractmethod
    def calculate_battery_health(self, battery: Battery) -> Battery:
        """计算电池健康状态
        
        Args:
            battery: 电池实体对象
            
        Returns:
            更新了健康状态的电池实体对象
        """
        pass
    
    @abstractmethod
    def analyze_battery_performance(self, battery: Battery) -> Dict[str, float]:
        """分析电池性能
        
        Args:
            battery: 电池实体对象
            
        Returns:
            包含各种性能指标的字典
        """
        pass
    
    @abstractmethod
    def compare_batteries(self, batteries: List[Battery]) -> Dict[str, List[float]]:
        """比较多个电池
        
        Args:
            batteries: 电池实体对象列表
            
        Returns:
            包含比较结果的字典
        """
        pass
    
    @abstractmethod
    def predict_battery_lifetime(self, battery: Battery) -> float:
        """预测电池寿命
        
        Args:
            battery: 电池实体对象
            
        Returns:
            预测的剩余寿命（以月为单位）
        """
        pass
    
    @abstractmethod
    def validate_battery_data(self, battery: Battery) -> Dict[str, bool]:
        """验证电池数据
        
        Args:
            battery: 电池实体对象
            
        Returns:
            包含验证结果的字典
        """
        pass
