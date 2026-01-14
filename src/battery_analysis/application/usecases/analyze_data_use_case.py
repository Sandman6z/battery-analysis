"""
AnalyzeDataUseCase实现

Application层的use case，负责数据分析的业务逻辑
"""

from dataclasses import dataclass
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from battery_analysis.domain.entities.battery import Battery
from battery_analysis.domain.repositories.battery_repository import BatteryRepository
from battery_analysis.domain.services.battery_analysis_service import BatteryAnalysisService


@dataclass
class AnalyzeDataInput:
    """数据分析输入数据类"""
    input_path: str
    output_path: str
    battery_type: str

    def validate(self) -> Dict[str, str]:
        """
        验证输入数据

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
            self.logger.debug("输入参数: input_path=%s, output_path=%s, battery_type=%s", 
                           input_data.input_path, input_data.output_path, input_data.battery_type)

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
            self.logger.info("找到 %d 个Excel文件", len(excel_files))
            
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
            analysis_results = []

            for excel_file in excel_files:
                try:
                    self.logger.info("开始处理Excel文件: %s", excel_file.filename)
                    self.logger.debug("文件路径: %s, 大小: %d bytes, 修改时间: %s", 
                                   str(excel_file.path), excel_file.size, 
                                   datetime.fromtimestamp(excel_file.modified_time).strftime('%Y-%m-%d %H:%M:%S'))

                    # 处理Excel文件，提取电池数据
                    battery_data_dict = self._process_excel_file(excel_file)

                    if not battery_data_dict:
                        self.logger.warning("无法从Excel文件中提取电池数据: %s", excel_file.filename)
                        continue

                    # 从字典数据创建Battery实体对象
                    battery = self._create_battery_entity(battery_data_dict, excel_file)
                    self.logger.debug("创建电池实体: %s, 序列号: %s", battery.model, battery.serial_number)

                    # 验证电池数据
                    validation_result = self.battery_analysis_service.validate_battery_data(battery)
                    if not all(validation_result.values()):
                        self.logger.warning(
                            "电池数据验证失败: %s, 验证结果: %s",
                            excel_file.filename,
                            validation_result
                        )
                        continue

                    # 计算电池健康状态
                    self.logger.info("开始计算电池健康状态: %s", battery.serial_number)
                    updated_battery = self.battery_analysis_service.calculate_battery_health(
                        battery
                    )
                    self.logger.debug("电池健康状态计算完成: %s, 健康状态: %s", 
                                   updated_battery.serial_number, updated_battery.health_status)

                    # 分析电池性能
                    self.logger.info("开始分析电池性能: %s", updated_battery.serial_number)
                    performance_analysis = (
                        self.battery_analysis_service.analyze_battery_performance(
                            updated_battery
                        )
                    )
                    self.logger.debug("电池性能分析完成: %s, 结果: %s", 
                                   updated_battery.serial_number, performance_analysis)

                    # 预测电池寿命
                    self.logger.info("开始预测电池寿命: %s", updated_battery.serial_number)
                    lifetime_prediction = self.battery_analysis_service.predict_battery_lifetime(
                        updated_battery
                    )
                    self.logger.debug("电池寿命预测完成: %s, 预测结果: %s", 
                                   updated_battery.serial_number, lifetime_prediction)

                    # 整合分析结果
                    analysis_result = {
                        'battery': updated_battery,
                        'performance': performance_analysis,
                        'lifetime_prediction': lifetime_prediction,
                        'file_info': battery_data_dict.get('file_info', {})
                    }

                    # 保存Battery实体对象到仓库
                    self.logger.info("保存电池实体到仓库: %s", updated_battery.serial_number)
                    self.battery_repository.save(updated_battery)

                    # 添加到分析结果列表
                    analysis_results.append(analysis_result)

                    processed_files += 1
                    analyzed_batteries += 1

                    self.logger.info("成功处理电池数据: %s", battery.serial_number)

                except Exception as e:
                    self.logger.error("处理Excel文件失败 %s: %s", excel_file.filename, str(e), exc_info=True)
                    continue

            # 如果有多个电池，进行比较分析
            comparison_result = None
            if len(analysis_results) > 1:
                self.logger.info("开始电池比较分析，共 %d 个电池", len(analysis_results))
                # 提取Battery实体对象列表
                batteries = [result['battery'] for result in analysis_results]
                comparison_result = self.battery_analysis_service.compare_batteries(batteries)
                self.logger.info("电池比较分析完成")
                self.logger.debug("比较结果: %s", comparison_result)

            # 保存比较结果（如果有）
            if comparison_result:
                # 这里可以添加保存比较结果的逻辑
                self.logger.info("保存电池比较结果")
                pass

            self.logger.info("数据分析用例执行成功")
            result_message = f"数据分析完成，共处理 {processed_files} 个文件，分析 {analyzed_batteries} 个电池"
            self.logger.info(result_message)
            
            return AnalyzeDataOutput(
                success=True,
                message=result_message,
                analyzed_batteries=analyzed_batteries,
                processed_files=processed_files,
                excel_files=excel_files
            )

        except Exception as e:
            self.logger.critical("数据分析用例执行失败: %s", str(e), exc_info=True)
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

    def _process_excel_file(self, file_info: ExcelFileInfo) -> Dict[str, Any]:
        """
        使用pandas处理Excel文件，提取完整的电池数据

        Args:
            file_info: Excel文件信息

        Returns:
            Dict[str, Any]: 提取的电池数据
        """
        try:
            self.logger.info("使用pandas处理Excel文件: %s", file_info.filename)

            # 使用pandas读取Excel文件
            df = pd.read_excel(file_info.path, sheet_name=0, engine='openpyxl', header=0)

            # 从文件名提取信息
            filename = file_info.filename

            # 提取批次日期代码
            batch_date_code = ""
            list_batch_date_code = re.findall("DC(.*?),", filename)
            if len(list_batch_date_code) == 1:
                batch_date_code = list_batch_date_code[0].strip()

            # 提取脉冲电流
            list_pulse_current = []
            list_pulse_current_to_split = re.findall(r"\(([\d.]+[-\d.]+)mA", filename)
            if len(list_pulse_current_to_split) == 1:
                list_pulse_current = list_pulse_current_to_split[0].split("-")
                try:
                    list_pulse_current = [float(c.strip()) for c in list_pulse_current]
                except ValueError:
                    list_pulse_current = [int(float(c.strip())) for c in list_pulse_current]

            # 提取恒流电流
            cc_current = ""
            list_cc_current_to_split = re.findall(r"mA,(.*?)\)", filename)
            if len(list_cc_current_to_split) == 1:
                str_cc_current_to_split = list_cc_current_to_split[0].replace("mAh", "")
                list_cc_current_to_split = re.findall(r"([\d.]+)mA", str_cc_current_to_split)
                if len(list_cc_current_to_split) >= 1:
                    cc_current = list_cc_current_to_split[-1]

            # 提取电池序列号
            serial_number = filename.split(".")[0]  # 默认使用文件名作为序列号

            # 从Excel数据中提取电池容量
            nominal_capacity = None
            if 'Capacity' in df.columns or '容量' in df.columns:
                capacity_column = 'Capacity' if 'Capacity' in df.columns else '容量'
                nominal_capacity = df[capacity_column].max() \
                    if not df[capacity_column].empty else None

            # 提取电压数据
            voltage_data = {}
            if 'Voltage' in df.columns or '电压' in df.columns:
                voltage_column = 'Voltage' if 'Voltage' in df.columns else '电压'
                voltage_data = {
                    'min': df[voltage_column].min(),
                    'max': df[voltage_column].max(),
                    'avg': df[voltage_column].mean(),
                    'std': df[voltage_column].std()
                }

            # 提取电流数据
            current_data = {}
            if 'Current' in df.columns or '电流' in df.columns:
                current_column = 'Current' if 'Current' in df.columns else '电流'
                current_data = {
                    'min': df[current_column].min(),
                    'max': df[current_column].max(),
                    'avg': df[current_column].mean(),
                    'std': df[current_column].std()
                }

            # 提取循环数据
            cycle_data = {}
            if 'Cycle' in df.columns or '循环' in df.columns:
                cycle_column = 'Cycle' if 'Cycle' in df.columns else '循环'
                cycle_data = {
                    'total_cycles': df[cycle_column].max(),
                    'cycle_range': [df[cycle_column].min(), df[cycle_column].max()]
                }

            # 提取温度数据
            temperature_data = {}
            if 'Temperature' in df.columns or '温度' in df.columns:
                temperature_column = 'Temperature' if 'Temperature' in df.columns else '温度'
                temperature_data = {
                    'min': df[temperature_column].min(),
                    'max': df[temperature_column].max(),
                    'avg': df[temperature_column].mean(),
                    'std': df[temperature_column].std()
                }

            # 构建完整的电池数据字典
            battery_data = {
                'serial_number': serial_number,
                'filename': filename,
                'batch_date_code': batch_date_code,
                'pulse_current': list_pulse_current,
                'cc_current': cc_current,
                'nominal_capacity': nominal_capacity,
                'voltage_data': voltage_data,
                'current_data': current_data,
                'cycle_data': cycle_data,
                'temperature_data': temperature_data,
                'total_records': len(df),
                'columns': df.columns.tolist(),
                'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
                'non_numeric_columns': df.select_dtypes(exclude=['number']).columns.tolist(),
                'missing_values': df.isnull().sum().to_dict(),
                'basic_stats': df.describe().to_dict(),
                'file_info': {
                    'path': str(file_info.path),
                    'size': file_info.size,
                    'modified_time': file_info.modified_time
                },
                'raw_data': df.to_dict('records')[:100]  # 保留前100条原始数据用于分析
            }

            return battery_data

        except Exception as e:
            self.logger.error("处理Excel文件失败 %s: %s", file_info.filename, str(e))
            return {}

    def _create_battery_entity(self,
                               battery_data_dict: Dict[str, Any],
                               excel_file: ExcelFileInfo) -> Battery:
        """
        从字典数据和Excel文件信息创建Battery实体对象

        Args:
            battery_data_dict: 从Excel文件中提取的电池数据字典
            excel_file: Excel文件信息

        Returns:
            Battery: 创建的Battery实体对象
        """
        # 提取或生成必填字段
        serial_number = battery_data_dict.get('serial_number', excel_file.filename.split('.')[0])

        # 从Excel数据中提取标称容量，如果没有则使用默认值
        nominal_capacity = battery_data_dict.get('nominal_capacity', 1.0)  # 默认值1.0 Ah

        # 从电压数据中提取平均电压，如果没有则使用默认值
        nominal_voltage = battery_data_dict.get('voltage_data', {}).get('avg', 3.7)  # 默认值3.7 V

        # 从文件名或其他字段提取制造商和型号信息
        filename = battery_data_dict.get('filename', '')
        manufacturer = "Unknown"  # 默认值
        model = filename.split('.')[0]  # 默认使用文件名作为型号
        chemistry = "Li-ion"  # 默认值

        # 创建Battery实体对象
        return Battery(
            model=model,
            manufacturer=manufacturer,
            serial_number=serial_number,
            chemistry=chemistry,
            nominal_capacity=nominal_capacity,
            nominal_voltage=nominal_voltage
        )

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
