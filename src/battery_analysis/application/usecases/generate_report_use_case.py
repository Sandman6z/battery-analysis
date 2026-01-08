"""
GenerateReportUseCase实现

Application层的use case，负责报告生成的业务逻辑
"""

from dataclasses import dataclass
import logging
import os
from typing import Dict, List, Optional
from battery_analysis.domain.entities.battery import Battery
from battery_analysis.domain.repositories.battery_repository import BatteryRepository


@dataclass
class GenerateReportInput:
    """报告生成输入数据类"""
    battery_ids: List[str]
    output_path: str
    report_type: str = "standard"  # 'standard' 或 'detailed'
    include_charts: bool = True
    include_raw_data: bool = False
    export_format: str = "pdf"  # 'pdf', 'docx', 'html'
    
    def validate(self) -> Dict[str, str]:
        """验证输入数据
        
        Returns:
            Dict[str, str]: 验证结果，键为字段名，值为错误信息
        """
        errors = {}
        
        # 验证必需字段
        if not self.battery_ids:
            errors["battery_ids"] = "缺少电池ID列表"
        
        if not self.output_path:
            errors["output_path"] = "缺少输出路径"
        elif not os.path.exists(self.output_path):
            errors["output_path"] = f"输出路径不存在: {self.output_path}"
        
        # 验证报告类型
        if self.report_type not in ["standard", "detailed"]:
            errors["report_type"] = "报告类型必须是'standard'或'detailed'"
        
        # 验证导出格式
        if self.export_format not in ["pdf", "docx", "html"]:
            errors["export_format"] = "导出格式必须是'pdf'、'docx'或'html'"
        
        return errors


@dataclass
class BatchProcessingInput:
    """批量处理输入数据类"""
    data_directories: List[str]
    output_path: str
    report_type: str = "standard"
    include_charts: bool = True
    export_format: str = "pdf"
    
    def validate(self) -> Dict[str, str]:
        """验证输入数据
        
        Returns:
            Dict[str, str]: 验证结果，键为字段名，值为错误信息
        """
        errors = {}
        
        # 验证必需字段
        if not self.data_directories:
            errors["data_directories"] = "缺少数据目录列表"
        else:
            # 验证每个目录是否存在
            for directory in self.data_directories:
                if not os.path.exists(directory):
                    errors["data_directories"] = f"数据目录不存在: {directory}"
                    break
        
        if not self.output_path:
            errors["output_path"] = "缺少输出路径"
        elif not os.path.exists(self.output_path):
            errors["output_path"] = f"输出路径不存在: {self.output_path}"
        
        return errors


@dataclass
class GenerateReportOutput:
    """报告生成输出数据类"""
    success: bool
    message: str
    report_files: List[str] = None
    generated_reports: int = 0
    error_details: Optional[str] = None


class GenerateReportUseCase:
    """报告生成用例"""
    
    def __init__(self, battery_repository: BatteryRepository):
        """
        初始化报告生成用例
        
        Args:
            battery_repository: 电池仓库实例
        """
        self.battery_repository = battery_repository
        self.logger = logging.getLogger(__name__)
    
    def generate_report(self, input_data: GenerateReportInput) -> GenerateReportOutput:
        """
        生成报告
        
        Args:
            input_data: 报告生成输入数据
            
        Returns:
            GenerateReportOutput: 报告生成输出结果
        """
        try:
            self.logger.info("开始生成报告")
            
            # 验证输入数据
            validation_errors = input_data.validate()
            if validation_errors:
                error_message = "\n".join(validation_errors.values())
                self.logger.warning("输入数据验证失败: %s", error_message)
                return GenerateReportOutput(
                    success=False,
                    message=f"输入数据验证失败: {error_message}",
                    error_details=error_message
                )
            
            # 从仓库获取电池数据
            batteries = []
            for battery_id in input_data.battery_ids:
                battery = self.battery_repository.get_by_serial_number(battery_id)
                if battery:
                    batteries.append(battery)
                else:
                    self.logger.warning("未找到电池: %s", battery_id)
            
            if not batteries:
                self.logger.warning("没有找到任何电池数据")
                return GenerateReportOutput(
                    success=False,
                    message="没有找到任何电池数据",
                    generated_reports=0
                )
            
            # 生成报告文件
            report_files = []
            for battery in batteries:
                report_path = self._generate_single_report(battery, input_data)
                if report_path:
                    report_files.append(report_path)
            
            self.logger.info("报告生成完成，共生成 %d 份报告", len(report_files))
            return GenerateReportOutput(
                success=True,
                message=f"报告生成完成，共生成 {len(report_files)} 份报告",
                report_files=report_files,
                generated_reports=len(report_files)
            )
            
        except Exception as e:
            self.logger.error("报告生成失败: %s", str(e))
            return GenerateReportOutput(
                success=False,
                message=f"报告生成失败: {str(e)}",
                error_details=str(e),
                generated_reports=0
            )
    
    def _generate_single_report(self, battery: Battery, input_data: GenerateReportInput) -> Optional[str]:
        """
        生成单个电池报告
        
        Args:
            battery: 电池实体对象
            input_data: 报告生成输入数据
            
        Returns:
            Optional[str]: 生成的报告文件路径，失败则返回None
        """
        try:
            self.logger.info("为电池 %s 生成报告", battery.serial_number)
            
            # 构建报告文件名
            report_filename = f"Battery_Report_{battery.serial_number}_{battery.model}_{battery.manufacturer}.{input_data.export_format}"
            report_path = os.path.join(input_data.output_path, report_filename)
            
            # 这里可以实现实际的报告生成逻辑
            # 例如：使用模板引擎生成报告，包含电池数据、图表等
            
            # 示例：创建一个空文件表示报告已生成
            with open(report_path, 'w') as f:
                f.write(f"# 电池报告\n\n")
                f.write(f"## 电池信息\n")
                f.write(f"- 型号: {battery.model}\n")
                f.write(f"- 制造商: {battery.manufacturer}\n")
                f.write(f"- 序列号: {battery.serial_number}\n")
                f.write(f"- 化学类型: {battery.chemistry}\n")
                f.write(f"- 标称容量: {battery.nominal_capacity} Ah\n")
                f.write(f"- 标称电压: {battery.nominal_voltage} V\n")
                
                if battery.state_of_health is not None:
                    f.write(f"- 健康状态: {battery.state_of_health:.1f}%\n")
                
                if battery.state_of_charge is not None:
                    f.write(f"- 充电状态: {battery.state_of_charge:.1f}%\n")
            
            return report_path
            
        except Exception as e:
            self.logger.error("为电池 %s 生成报告失败: %s", battery.serial_number, str(e))
            return None
    
    def export_report(self, report_path: str, export_format: str = "pdf") -> GenerateReportOutput:
        """
        导出报告
        
        Args:
            report_path: 报告文件路径
            export_format: 导出格式
            
        Returns:
            GenerateReportOutput: 报告导出输出结果
        """
        try:
            self.logger.info("导出报告: %s 到格式: %s", report_path, export_format)
            
            # 验证输入
            if not os.path.exists(report_path):
                return GenerateReportOutput(
                    success=False,
                    message=f"报告文件不存在: {report_path}",
                    generated_reports=0
                )
            
            # 验证导出格式
            if export_format not in ["pdf", "docx", "html"]:
                return GenerateReportOutput(
                    success=False,
                    message=f"不支持的导出格式: {export_format}",
                    generated_reports=0
                )
            
            # 这里可以实现实际的报告导出逻辑
            # 例如：将报告转换为指定格式
            
            self.logger.info("报告导出成功")
            return GenerateReportOutput(
                success=True,
                message="报告导出成功",
                report_files=[report_path],
                generated_reports=1
            )
            
        except Exception as e:
            self.logger.error("报告导出失败: %s", str(e))
            return GenerateReportOutput(
                success=False,
                message=f"报告导出失败: {str(e)}",
                error_details=str(e),
                generated_reports=0
            )
    
    def batch_processing(self, input_data: BatchProcessingInput) -> GenerateReportOutput:
        """
        批量处理报告生成
        
        Args:
            input_data: 批量处理输入数据
            
        Returns:
            GenerateReportOutput: 批量处理输出结果
        """
        try:
            self.logger.info("开始批量处理报告生成")
            
            # 验证输入数据
            validation_errors = input_data.validate()
            if validation_errors:
                error_message = "\n".join(validation_errors.values())
                self.logger.warning("批量处理输入数据验证失败: %s", error_message)
                return GenerateReportOutput(
                    success=False,
                    message=f"批量处理输入数据验证失败: {error_message}",
                    error_details=error_message,
                    generated_reports=0
                )
            
            # 这里可以实现实际的批量处理逻辑
            # 例如：遍历每个数据目录，处理其中的电池数据，生成报告
            
            # 示例：假设每个目录生成一份报告
            report_files = []
            for directory in input_data.data_directories:
                # 构建报告文件名
                dir_name = os.path.basename(directory)
                report_filename = f"Batch_Report_{dir_name}.{input_data.export_format}"
                report_path = os.path.join(input_data.output_path, report_filename)
                
                # 创建一个空文件表示报告已生成
                with open(report_path, 'w') as f:
                    f.write(f"# 批量报告\n\n")
                    f.write(f"## 数据目录: {directory}\n")
                    f.write(f"## 报告类型: {input_data.report_type}\n")
                    f.write(f"## 包含图表: {input_data.include_charts}\n")
                    f.write(f"## 导出格式: {input_data.export_format}\n")
                
                report_files.append(report_path)
            
            self.logger.info("批量处理报告生成完成，共生成 %d 份报告", len(report_files))
            return GenerateReportOutput(
                success=True,
                message=f"批量处理报告生成完成，共生成 {len(report_files)} 份报告",
                report_files=report_files,
                generated_reports=len(report_files)
            )
            
        except Exception as e:
            self.logger.error("批量处理报告生成失败: %s", str(e))
            return GenerateReportOutput(
                success=False,
                message=f"批量处理报告生成失败: {str(e)}",
                error_details=str(e),
                generated_reports=0
            )
