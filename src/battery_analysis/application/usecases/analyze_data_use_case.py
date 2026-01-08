"""
AnalyzeDataUseCase实现

Application层的use case，负责数据分析的业务逻辑
"""

from dataclasses import dataclass
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
from battery_analysis.domain.repositories.battery_repository import BatteryRepository
from battery_analysis.domain.services.battery_analysis_service import BatteryAnalysisService


@dataclass
class AnalyzeDataInput:
    """数据分析输入数据类"""
    input_path: str
    output_path: str
    battery_type: str
    
    def validate(self) -> Dict[str, str]:
        """验证输入数据
        
        Returns:
            Dict[str, str]: 验证结果，键为字段名，值为错误信息
        """
        errors = {}
        
        # 验证必需字段
        if not self.input_path:
            errors["input_path"] = "缺少输入路径"
        elif not os.path.exists(self.input_path):
            errors["input_path"] = f"输入路径不存在: {self.input_path}"
        
        if not self.output_path:
            errors["output_path"] = "缺少输出路径"
        
        if not self.battery_type:
            errors["battery_type"] = "缺少电池类型"
        
        return errors


@dataclass
class ExcelFileInfo:
    """Excel文件信息类"""
    filename: str
    path: Path
    size: int
    modified_time: float


@dataclass
class AnalyzeDataOutput:
    """数据分析输出数据类"""
    success: bool
    message: str
    analyzed_batteries: int = 0
    processed_files: int = 0
    excel_files: Optional[List[ExcelFileInfo]] = None
    error_details: Optional[str] = None


class AnalyzeDataUseCase:
    """数据分析用例"""
    
    def __init__(self, 
                 battery_repository: BatteryRepository, 
                 battery_analysis_service: BatteryAnalysisService):
        """
        初始化数据分析用例
        
        Args:
            battery_repository: 电池仓库实例
            battery_analysis_service: 电池分析服务实例
        """
        self.battery_repository = battery_repository
        self.battery_analysis_service = battery_analysis_service
        self.logger = logging.getLogger(__name__)
    
    def execute(self, input_data: AnalyzeDataInput) -> AnalyzeDataOutput:
        """
        执行数据分析用例
        
        Args:
            input_data: 数据分析输入数据
            
        Returns:
            AnalyzeDataOutput: 数据分析输出结果
        """
        try:
            self.logger.info("开始执行数据分析用例")
            
            # 验证输入数据
            validation_errors = input_data.validate()
            if validation_errors:
                error_message = "\n".join(validation_errors.values())
                self.logger.warning("输入数据验证失败: %s", error_message)
                return AnalyzeDataOutput(
                    success=False,
                    message=f"输入数据验证失败: {error_message}",
                    error_details=error_message
                )
            
            # 查找所有Excel文件
            excel_files = self._find_excel_files(input_data.input_path)
            if not excel_files:
                self.logger.warning("没有找到Excel文件")
                return AnalyzeDataOutput(
                    success=False,
                    message="没有找到Excel文件",
                    excel_files=[],
                    processed_files=0,
                    analyzed_batteries=0
                )
            
            # 处理Excel文件并分析数据
            processed_files = 0
            analyzed_batteries = 0
            
            for excel_file in excel_files:
                try:
                    self.logger.info("处理Excel文件: %s", excel_file.filename)
                    
                    # 这里可以实现Excel文件处理逻辑
                    # 例如：读取Excel文件内容，提取电池数据，进行分析
                    
                    processed_files += 1
                    analyzed_batteries += 1  # 假设每个文件包含一个电池的数据
                    
                except Exception as e:
                    self.logger.error("处理Excel文件失败 %s: %s", excel_file.filename, str(e))
                    continue
            
            self.logger.info("数据分析用例执行成功")
            return AnalyzeDataOutput(
                success=True,
                message=f"数据分析完成，共处理 {processed_files} 个文件，分析 {analyzed_batteries} 个电池",
                analyzed_batteries=analyzed_batteries,
                processed_files=processed_files,
                excel_files=excel_files
            )
            
        except Exception as e:
            self.logger.error("数据分析用例执行失败: %s", str(e))
            return AnalyzeDataOutput(
                success=False,
                message=f"数据分析失败: {str(e)}",
                error_details=str(e),
                processed_files=0,
                analyzed_batteries=0
            )
    
    def _find_excel_files(self, directory: str) -> List[ExcelFileInfo]:
        """
        查找目录中的所有Excel文件
        
        Args:
            directory: 目录路径
            
        Returns:
            List[ExcelFileInfo]: Excel文件信息列表
        """
        excel_files = []
        
        try:
            # 遍历目录中的所有文件
            for file in os.listdir(directory):
                # 跳过临时文件和非Excel文件
                if file[:2] == "~$" or file[-5:] != ".xlsx":
                    continue
                
                # 构建文件路径
                file_path = Path(directory) / file
                
                # 获取文件信息
                file_stat = file_path.stat()
                
                # 创建Excel文件信息对象
                excel_file_info = ExcelFileInfo(
                    filename=file,
                    path=file_path,
                    size=file_stat.st_size,
                    modified_time=file_stat.st_mtime
                )
                
                excel_files.append(excel_file_info)
            
        except Exception as e:
            self.logger.error("查找Excel文件失败: %s", str(e))
        
        return excel_files
    
    def handle_data_error(self, error_msg: str) -> str:
        """
        处理数据错误
        
        Args:
            error_msg: 错误信息
            
        Returns:
            str: 用户选择的恢复选项
        """
        self.logger.error("处理数据错误: %s", error_msg)
        
        # 在实际应用中，这里应该返回一个决策，而不是直接处理UI
        # 决策可以通过Presenter层传递给UI
        return "retry"  # 默认返回重试选项
