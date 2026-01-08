"""
CalculateBatteryUseCase实现

Application层的use case，负责电池计算的业务逻辑
"""

from dataclasses import dataclass
import logging
from typing import Dict, List, Optional
from battery_analysis.domain.entities.battery import Battery
from battery_analysis.domain.repositories.battery_repository import BatteryRepository
from battery_analysis.domain.services.battery_analysis_service import BatteryAnalysisService


@dataclass
class CalculateBatteryInput:
    """电池计算输入数据类"""
    battery_type: str
    construction_method: str
    specification_type: str
    specification_method: str
    manufacturer: str
    tester_location: str
    tested_by: str
    reported_by: str
    temperature: str
    input_path: str
    output_path: str
    barcode: str
    
    def validate(self) -> Dict[str, str]:
        """验证输入数据
        
        Returns:
            Dict[str, str]: 验证结果，键为字段名，值为错误信息
        """
        errors = {}
        
        # 验证必需字段
        required_fields = [
            ("battery_type", self.battery_type, "电池类型"),
            ("construction_method", self.construction_method, "构造方法"),
            ("specification_type", self.specification_type, "规格类型"),
            ("specification_method", self.specification_method, "规格方法"),
            ("manufacturer", self.manufacturer, "制造商"),
            ("tester_location", self.tester_location, "测试者位置"),
            ("tested_by", self.tested_by, "测试者"),
            ("reported_by", self.reported_by, "报告者"),
            ("temperature", self.temperature, "温度"),
            ("input_path", self.input_path, "输入路径"),
            ("output_path", self.output_path, "输出路径"),
            ("barcode", self.barcode, "条形码")
        ]
        
        for field_name, field_value, field_desc in required_fields:
            if not field_value:
                errors[field_name] = f"缺少必要字段: {field_desc}"
        
        return errors


@dataclass
class CalculateBatteryOutput:
    """电池计算输出数据类"""
    success: bool
    message: str
    battery: Optional[Battery] = None
    performance_data: Optional[Dict[str, float]] = None


class CalculateBatteryUseCase:
    """电池计算用例"""
    
    def __init__(self, 
                 battery_repository: BatteryRepository, 
                 battery_analysis_service: BatteryAnalysisService):
        """
        初始化电池计算用例
        
        Args:
            battery_repository: 电池仓库实例
            battery_analysis_service: 电池分析服务实例
        """
        self.battery_repository = battery_repository
        self.battery_analysis_service = battery_analysis_service
        self.logger = logging.getLogger(__name__)
    
    def execute(self, input_data: CalculateBatteryInput) -> CalculateBatteryOutput:
        """
        执行电池计算用例
        
        Args:
            input_data: 电池计算输入数据
            
        Returns:
            CalculateBatteryOutput: 电池计算输出结果
        """
        try:
            self.logger.info("开始执行电池计算用例")
            
            # 验证输入数据
            validation_errors = input_data.validate()
            if validation_errors:
                error_message = "\n".join(validation_errors.values())
                self.logger.warning("输入数据验证失败: %s", error_message)
                return CalculateBatteryOutput(
                    success=False,
                    message=f"输入数据验证失败: {error_message}"
                )
            
            # 创建电池实体
            battery = Battery(
                model=input_data.battery_type,
                manufacturer=input_data.manufacturer,
                serial_number=input_data.barcode,
                chemistry="Lithium-ion",  # 这里可以根据实际情况从输入中获取
                nominal_capacity=2.0,  # 示例值，实际应从输入或配置中获取
                nominal_voltage=3.7  # 示例值，实际应从输入或配置中获取
            )
            
            # 计算电池健康状态
            battery = self.battery_analysis_service.calculate_battery_health(battery)
            
            # 分析电池性能
            performance_data = self.battery_analysis_service.analyze_battery_performance(battery)
            
            # 保存电池数据
            saved_battery = self.battery_repository.save(battery)
            
            self.logger.info("电池计算用例执行成功")
            return CalculateBatteryOutput(
                success=True,
                message="电池计算已完成",
                battery=saved_battery,
                performance_data=performance_data
            )
            
        except Exception as e:
            self.logger.error("电池计算用例执行失败: %s", str(e))
            return CalculateBatteryOutput(
                success=False,
                message=f"电池计算失败: {str(e)}"
            )
