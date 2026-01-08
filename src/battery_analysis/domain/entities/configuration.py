"""
Configuration实体定义

Domain层的配置实体，代表应用程序的配置和用户设置
"""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class Configuration:
    """配置实体类"""
    
    # 电池类型设置
    battery_type: str
    
    # 温度设置
    temperature_unit: str  # 'C' 或 'F'
    temperature_limit: float  # 温度限制
    
    # 输出路径设置
    output_path: Path
    report_path: Path
    log_path: Path
    
    # 应用程序设置
    language: str = "zh_CN"
    theme: str = "light"
    auto_save: bool = True
    
    # 分析设置
    analysis_mode: str = "standard"  # 'standard' 或 'advanced'
    calculation_precision: int = 4  # 计算精度
    
    def __post_init__(self):
        """初始化后验证"""
        # 验证温度单位
        if self.temperature_unit not in ['C', 'F']:
            raise ValueError("温度单位必须是'C'或'F'")
        
        # 验证分析模式
        if self.analysis_mode not in ['standard', 'advanced']:
            raise ValueError("分析模式必须是'standard'或'advanced'")
        
        # 验证计算精度
        if self.calculation_precision < 0:
            raise ValueError("计算精度不能为负数")
        
        # 确保路径存在
        for path in [self.output_path, self.report_path, self.log_path]:
            path.mkdir(parents=True, exist_ok=True)
