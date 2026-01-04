# -*- coding: utf-8 -*-
"""
数据处理服务接口模块

定义数据处理相关的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path


class IDataProcessingService(ABC):
    """
    数据处理服务接口
    提供数据过滤、分析和可视化相关功能
    """
    
    @abstractmethod
    def filter_battery_data(self, data: List[Dict[str, Any]], 
                           filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        过滤电池数据
        
        Args:
            data: 原始数据列表
            filters: 过滤条件字典
            
        Returns:
            List[Dict[str, Any]]: 过滤后的数据
        """
        pass
    
    @abstractmethod
    def analyze_battery_performance(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析电池性能
        
        Args:
            data: 电池数据列表
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        pass
    
    @abstractmethod
    def calculate_statistics(self, data: List[Union[float, int]], 
                           statistics: List[str] = None) -> Dict[str, float]:
        """
        计算统计数据
        
        Args:
            data: 数据列表
            statistics: 统计类型列表（如["mean", "std", "min", "max"]）
            
        Returns:
            Dict[str, float]: 统计数据
        """
        pass
    
    @abstractmethod
    def smooth_data(self, data: List[float], method: str = "moving_average", 
                   window_size: int = 5) -> List[float]:
        """
        数据平滑处理
        
        Args:
            data: 原始数据
            method: 平滑方法（"moving_average", "gaussian", "savgol"）
            window_size: 窗口大小
            
        Returns:
            List[float]: 平滑后的数据
        """
        pass
    
    @abstractmethod
    def detect_outliers(self, data: List[Union[float, int]], 
                       method: str = "iqr") -> List[int]:
        """
        检测异常值
        
        Args:
            data: 数据列表
            method: 检测方法（"iqr", "zscore", "isolation_forest"）
            
        Returns:
            List[int]: 异常值的索引列表
        """
        pass
    
    @abstractmethod
    def generate_mock_data(self, battery_count: int = 1, 
                          data_points: int = 100) -> List[Dict[str, Any]]:
        """
        生成模拟电池数据
        
        Args:
            battery_count: 电池数量
            data_points: 数据点数量
            
        Returns:
            List[Dict[str, Any]]: 模拟数据
        """
        pass
    
    @abstractmethod
    def validate_data_integrity(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证数据完整性
        
        Args:
            data: 待验证的数据
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        pass
    
    @abstractmethod
    def process_csv_data(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        处理CSV数据文件
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            List[Dict[str, Any]]: 解析后的数据
        """
        pass
    
    @abstractmethod
    def export_processed_data(self, data: List[Dict[str, Any]], 
                            output_path: str, format: str = "csv") -> bool:
        """
        导出处理后的数据
        
        Args:
            data: 要导出的数据
            output_path: 输出文件路径
            format: 导出格式（"csv", "json", "excel"）
            
        Returns:
            bool: 导出是否成功
        """
        pass
    
    @abstractmethod
    def merge_battery_data(self, data_list: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        合并多个电池数据集
        
        Args:
            data_list: 数据集列表
            
        Returns:
            List[Dict[str, Any]]: 合并后的数据
        """
        pass
    
    @abstractmethod
    def extract_features(self, data: List[Dict[str, Any]], 
                        feature_types: List[str]) -> Dict[str, Any]:
        """
        提取数据特征
        
        Args:
            data: 原始数据
            feature_types: 特征类型列表
            
        Returns:
            Dict[str, Any]: 提取的特征
        """
        pass
