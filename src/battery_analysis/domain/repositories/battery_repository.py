# -*- coding: utf-8 -*-
"""
BatteryRepository接口定义

Domain层的仓库接口，定义电池的持久化和查询操作
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from battery_analysis.domain.entities.battery import Battery


class BatteryRepository(ABC):
    """电池仓库接口"""
    
    @abstractmethod
    def save(self, battery: Battery) -> Battery:
        """保存电池信息
        
        Args:
            battery: 电池实体对象
            
        Returns:
            保存后的电池实体对象
        """
        pass
    
    @abstractmethod
    def find_by_serial_number(self, serial_number: str) -> Optional[Battery]:
        """根据序列号查找电池
        
        Args:
            serial_number: 电池序列号
            
        Returns:
            电池实体对象，或None
        """
        pass
    
    @abstractmethod
    def find_by_model_number(self, model_number: str) -> List[Battery]:
        """根据型号查找电池
        
        Args:
            model_number: 电池型号
            
        Returns:
            电池实体对象列表
        """
        pass
    
    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """根据制造商查找电池
        
        Args:
            manufacturer: 制造商
            
        Returns:
            电池实体对象列表
        """
        pass
    
    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池
        
        Args:
            battery_type: 电池类型
            
        Returns:
            电池实体对象列表
        """
        pass
    
    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            电池实体对象列表
        """
        pass
    
    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池
        
        Args:
            status: 电池状态
            
        Returns:
            电池实体对象列表
        """
        pass
    
    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池
        
        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量
            
        Returns:
            电池实体对象列表
        """
        pass
    
    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池信息
        
        Args:
            battery: 电池实体对象
            
        Returns:
            更新后的电池实体对象
        """
        pass
    
    @abstractmethod
    def delete(self, serial_number: str) -> bool:
        """删除电池信息
        
        Args:
            serial_number: 电池序列号
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """统计电池数量
        
        Returns:
            电池数量
        """
        pass
