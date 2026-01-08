"""
BatteryRepository接口定义

Domain层的仓库接口，定义电池数据的访问契约
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from battery_analysis.domain.entities.battery import Battery


class BatteryRepository(ABC):
    """电池仓库接口"""
    
    @abstractmethod
    def save(self, battery: Battery) -> Battery:
        """保存电池数据
        
        Args:
            battery: 电池实体对象
            
        Returns:
            保存后的电池实体对象
        """
        pass
    
    @abstractmethod
    def get_by_serial_number(self, serial_number: str) -> Optional[Battery]:
        """根据序列号获取电池数据
        
        Args:
            serial_number: 电池序列号
            
        Returns:
            电池实体对象，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[Battery]:
        """获取所有电池数据
        
        Returns:
            电池实体对象列表
        """
        pass
    
    @abstractmethod
    def delete(self, serial_number: str) -> bool:
        """删除电池数据
        
        Args:
            serial_number: 电池序列号
            
        Returns:
            删除成功返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池数据
        
        Args:
            battery: 电池实体对象
            
        Returns:
            更新后的电池实体对象
        """
        pass
