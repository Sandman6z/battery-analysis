"""
BatteryRepository实现类

基础设施层，实现Domain层的BatteryRepository接口
"""

import logging
from typing import List, Optional
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
    
    def get_by_serial_number(self, serial_number: str) -> Optional[Battery]:
        """
        根据序列号获取电池数据
        
        Args:
            serial_number: 电池序列号
            
        Returns:
            电池实体对象，如果不存在则返回None
        """
        self.logger.info("根据序列号获取电池数据: %s", serial_number)
        # 从内存字典中获取
        return self._batteries.get(serial_number)
    
    def get_all(self) -> List[Battery]:
        """
        获取所有电池数据
        
        Returns:
            电池实体对象列表
        """
        self.logger.info("获取所有电池数据，共 %d 个电池", len(self._batteries))
        # 返回所有电池实体列表
        return list(self._batteries.values())
    
    def delete(self, serial_number: str) -> bool:
        """
        删除电池数据
        
        Args:
            serial_number: 电池序列号
            
        Returns:
            删除成功返回True，否则返回False
        """
        self.logger.info("删除电池数据: %s", serial_number)
        # 从内存字典中删除
        if serial_number in self._batteries:
            del self._batteries[serial_number]
            return True
        return False
    
    def update(self, battery: Battery) -> Battery:
        """
        更新电池数据
        
        Args:
            battery: 电池实体对象
            
        Returns:
            更新后的电池实体对象
        """
        self.logger.info("更新电池数据: %s", battery.serial_number)
        # 更新内存字典中的电池数据
        self._batteries[battery.serial_number] = battery
        return battery