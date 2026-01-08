"""
Battery实体定义

Domain层的核心实体，代表电池及其相关属性
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Battery:
    """电池实体类"""
    
    # 电池基本信息
    model: str
    manufacturer: str
    serial_number: str
    chemistry: str
    
    # 电池规格参数
    nominal_capacity: float  # 标称容量 (Ah)
    nominal_voltage: float  # 标称电压 (V)
    
    # 电池状态参数
    current_capacity: Optional[float] = None  # 当前容量 (Ah)
    internal_resistance: Optional[float] = None  # 内阻 (mΩ)
    temperature: Optional[float] = None  # 温度 (°C)
    
    # 电池健康状态
    state_of_health: Optional[float] = None  # 健康状态 (0-100%)
    state_of_charge: Optional[float] = None  # 充电状态 (0-100%)
    
    def __post_init__(self):
        """初始化后验证"""
        if self.nominal_capacity <= 0:
            raise ValueError("标称容量必须大于0")
        if self.nominal_voltage <= 0:
            raise ValueError("标称电压必须大于0")
        if self.current_capacity is not None and self.current_capacity < 0:
            raise ValueError("当前容量不能为负数")
        if self.state_of_health is not None and not (0 <= self.state_of_health <= 100):
            raise ValueError("健康状态必须在0-100%之间")
        if self.state_of_charge is not None and not (0 <= self.state_of_charge <= 100):
            raise ValueError("充电状态必须在0-100%之间")
