# -*- coding: utf-8 -*-
"""
数据处理抽象接口

定义数据操作的抽象接口，实现数据处理库的解耦
支持多种数据处理库（pandas、numpy、openpyxl等）
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Union
from enum import Enum


class DataFormat(Enum):
    """数据格式枚举"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    HDF5 = "hdf5"
    PARQUET = "parquet"


class DataType(Enum):
    """数据类型枚举"""
    NUMERIC = "numeric"
    STRING = "string"
    DATETIME = "datetime"
    CATEGORICAL = "categorical"


class IDataProcessor(ABC):
    """数据处理抽象接口"""
    
    @abstractmethod
    def load_data(self, file_path: str, format: DataFormat, **kwargs) -> Any:
        """加载数据文件
        
        Args:
            file_path: 文件路径
            format: 数据格式
            **kwargs: 加载参数
            
        Returns:
            Any: 数据对象
        """
        pass
    
    @abstractmethod
    def save_data(self, data: Any, file_path: str, format: DataFormat, **kwargs) -> bool:
        """保存数据文件
        
        Args:
            data: 数据对象
            file_path: 保存路径
            format: 数据格式
            **kwargs: 保存参数
            
        Returns:
            bool: 是否保存成功
        """
        pass
    
    @abstractmethod
    def create_dataframe(self, data: Optional[Union[Dict, List, Any]] = None) -> Any:
        """创建数据框
        
        Args:
            data: 初始数据
            
        Returns:
            Any: 数据框对象
        """
        pass
    
    @abstractmethod
    def filter_data(self, data: Any, conditions: Dict[str, Any]) -> Any:
        """过滤数据
        
        Args:
            data: 数据对象
            conditions: 过滤条件
            
        Returns:
            Any: 过滤后的数据
        """
        pass
    
    @abstractmethod
    def group_data(self, data: Any, by: Union[str, List[str]]) -> Any:
        """分组数据
        
        Args:
            data: 数据对象
            by: 分组字段
            
        Returns:
            Any: 分组后的数据
        """
        pass
    
    @abstractmethod
    def aggregate_data(self, data: Any, aggregations: Dict[str, Dict[str, str]]) -> Any:
        """聚合数据
        
        Args:
            data: 数据对象
            aggregations: 聚合规则
            
        Returns:
            Any: 聚合后的数据
        """
        pass
    
    @abstractmethod
    def sort_data(self, data: Any, by: Union[str, List[str]], ascending: bool = True) -> Any:
        """排序数据
        
        Args:
            data: 数据对象
            by: 排序字段
            ascending: 是否升序
            
        Returns:
            Any: 排序后的数据
        """
        pass
    
    @abstractmethod
    def merge_data(self, left: Any, right: Any, on: Union[str, List[str]], how: str = "inner") -> Any:
        """合并数据
        
        Args:
            left: 左数据
            right: 右数据
            on: 合并字段
            how: 合并方式
            
        Returns:
            Any: 合并后的数据
        """
        pass
    
    @abstractmethod
    def get_column_names(self, data: Any) -> List[str]:
        """获取列名
        
        Args:
            data: 数据对象
            
        Returns:
            List[str]: 列名列表
        """
        pass
    
    @abstractmethod
    def get_column_data(self, data: Any, column: str) -> Any:
        """获取列数据
        
        Args:
            data: 数据对象
            column: 列名
            
        Returns:
            Any: 列数据
        """
        pass
    
    @abstractmethod
    def set_column_data(self, data: Any, column: str, values: Any) -> bool:
        """设置列数据
        
        Args:
            data: 数据对象
            column: 列名
            values: 新数据
            
        Returns:
            bool: 是否设置成功
        """
        pass
    
    @abstractmethod
    def convert_data_type(self, data: Any, column: str, data_type: DataType) -> bool:
        """转换数据类型
        
        Args:
            data: 数据对象
            column: 列名
            data_type: 目标类型
            
        Returns:
            bool: 是否转换成功
        """
        pass
    
    @abstractmethod
    def get_statistics(self, data: Any, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """获取统计信息
        
        Args:
            data: 数据对象
            columns: 指定列（None表示所有列）
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        pass
    
    @abstractmethod
    def handle_missing_values(self, data: Any, strategy: str = "drop") -> Any:
        """处理缺失值
        
        Args:
            data: 数据对象
            strategy: 处理策略（drop、fill、interpolate等）
            
        Returns:
            Any: 处理后的数据
        """
        pass
