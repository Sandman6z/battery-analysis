"""
BatteryRepository实现类

基础设施层，实现Domain层的BatteryRepository接口
"""

import logging
from typing import List, Optional
from datetime import datetime
from battery_analysis.domain.entities.battery import Battery
from battery_analysis.domain.repositories.battery_repository import BatteryRepository


class BatteryRepositoryImpl(BatteryRepository):
    """电池仓库实现类（基于内存存储）"""
    
    def __init__(self):
        """初始化电池仓库"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化BatteryRepositoryImpl")
        # 使用内存字典存储电池数据，键为序列号
        self._batteries = {}
    
    def save(self, battery: Battery) -> Battery:
        """
        保存电池数据
        
        Args:
            battery: 电池实体对象
            
        Returns:
            保存后的电池实体对象
        """
        self.logger.info("保存电池数据: %s", battery.serial_number)
        # 保存到内存字典
        self._batteries[battery.serial_number] = battery
        return battery
    
    def find_by_serial_number(self, serial_number: str) -> Optional[Battery]:
        """
        根据序列号查找电池
        
        Args:
            serial_number: 电池序列号
            
        Returns:
            电池实体对象，或None
        """
        self.logger.info("根据序列号查找电池: %s", serial_number)
        # 从内存字典中获取
        return self._batteries.get(serial_number)
    
    def find_by_model_number(self, model_number: str) -> List[Battery]:
        """
        根据型号查找电池
        
        Args:
            model_number: 电池型号
            
        Returns:
            电池实体对象列表
        """
        self.logger.info("根据型号查找电池: %s", model_number)
        # 从内存字典中过滤
        return [battery for battery in self._batteries.values() if battery.model_number == model_number]
    
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """
        根据制造商查找电池
        
        Args:
            manufacturer: 制造商
            
        Returns:
            电池实体对象列表
        """
        self.logger.info("根据制造商查找电池: %s", manufacturer)
        # 从内存字典中过滤
        return [battery for battery in self._batteries.values() if battery.manufacturer == manufacturer]
    
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """
        根据电池类型查找电池
        
        Args:
            battery_type: 电池类型
            
        Returns:
            电池实体对象列表
        """
        self.logger.info("根据电池类型查找电池: %s", battery_type)
        # 从内存字典中过滤
        return [battery for battery in self._batteries.values() if battery.battery_type == battery_type]
    
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """
        根据生产日期范围查找电池
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            电池实体对象列表
        """
        self.logger.info("根据生产日期范围查找电池: %s 到 %s", start_date, end_date)
        # 从内存字典中过滤
        return [battery for battery in self._batteries.values() 
                if start_date <= battery.production_date <= end_date]
    
    def find_by_status(self, status: str) -> List[Battery]:
        """
        根据状态查找电池
        
        Args:
            status: 电池状态
            
        Returns:
            电池实体对象列表
        """
        self.logger.info("根据状态查找电池: %s", status)
        # 从内存字典中过滤
        return [battery for battery in self._batteries.values() if battery.status == status]
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """
        查找所有电池
        
        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量
            
        Returns:
            电池实体对象列表
        """
        self.logger.info("查找所有电池，限制: %d, 偏移: %d", limit, offset)
        # 返回所有电池实体列表，并应用限制和偏移
        all_batteries = list(self._batteries.values())
        return all_batteries[offset:offset+limit]
    
    def update(self, battery: Battery) -> Battery:
        """
        更新电池信息
        
        Args:
            battery: 电池实体对象
            
        Returns:
            更新后的电池实体对象
        """
        self.logger.info("更新电池数据: %s", battery.serial_number)
        # 更新内存字典中的电池数据
        self._batteries[battery.serial_number] = battery
        return battery
    
    def delete(self, serial_number: str) -> bool:
        """
        删除电池信息
        
        Args:
            serial_number: 电池序列号
            
        Returns:
            是否删除成功
        """
        self.logger.info("删除电池数据: %s", serial_number)
        # 从内存字典中删除
        if serial_number in self._batteries:
            del self._batteries[serial_number]
            return True
        return False
    
    def count(self) -> int:
        """
        统计电池数量
        
        Returns:
            电池数量
        """
        count = len(self._batteries)
        self.logger.info("统计电池数量: %d", count)
        # 返回内存字典中的电池数量
        return count