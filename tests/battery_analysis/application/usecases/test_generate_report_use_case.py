# -*- coding: utf-8 -*-
"""
GenerateReportUseCase测试
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock
from battery_analysis.application.usecases.generate_report_use_case import (
    GenerateReportUseCase, GenerateReportInput, GenerateReportOutput, BatchProcessingInput
)
from battery_analysis.domain.entities.battery import Battery


class TestGenerateReportUseCase:
    """报告生成用例测试类"""

    def setup_method(self):
        """设置测试环境"""
        # 创建模拟依赖
        self.mock_battery_repository = Mock()
        
        # 创建测试用例实例
        self.use_case = GenerateReportUseCase(
            battery_repository=self.mock_battery_repository
        )
        
        # 创建临时目录用于测试
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name) / "output"
        self.data_dir = Path(self.temp_dir.name) / "data"
        self.output_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """清理测试环境"""
        self.temp_dir.cleanup()

    def test_generate_report_with_invalid_input(self):
        """测试生成报告（无效输入）"""
        # 创建无效输入（缺少电池ID列表）
        input_data = GenerateReportInput(
            battery_ids=[],  # 空电池ID列表
            output_path=str(self.output_dir),
            report_type="standard",
            include_charts=True,
            include_raw_data=False,
            export_format="pdf"
        )
        
        # 执行用例
        result = self.use_case.generate_report(input_data)
        
        # 验证结果
        assert not result.success
        assert "缺少电池ID列表" in result.message

    def test_generate_report_with_nonexistent_output_path(self):
        """测试生成报告（不存在的输出路径）"""
        # 创建输入
        input_data = GenerateReportInput(
            battery_ids=["BAT-001"],
            output_path="nonexistent/path",
            report_type="standard",
            include_charts=True,
            include_raw_data=False,
            export_format="pdf"
        )
        
        # 执行用例
        result = self.use_case.generate_report(input_data)
        
        # 验证结果
        assert not result.success
        assert "输出路径不存在" in result.message

    def test_generate_report_with_invalid_report_type(self):
        """测试生成报告（无效的报告类型）"""
        # 创建输入
        input_data = GenerateReportInput(
            battery_ids=["BAT-001"],
            output_path=str(self.output_dir),
            report_type="invalid",  # 无效的报告类型
            include_charts=True,
            include_raw_data=False,
            export_format="pdf"
        )
        
        # 执行用例
        result = self.use_case.generate_report(input_data)
        
        # 验证结果
        assert not result.success
        assert "报告类型必须是'standard'或'detailed'" in result.message

    def test_generate_report_with_invalid_export_format(self):
        """测试生成报告（无效的导出格式）"""
        # 创建输入
        input_data = GenerateReportInput(
            battery_ids=["BAT-001"],
            output_path=str(self.output_dir),
            report_type="standard",
            include_charts=True,
            include_raw_data=False,
            export_format="invalid"  # 无效的导出格式
        )
        
        # 执行用例
        result = self.use_case.generate_report(input_data)
        
        # 验证结果
        assert not result.success
        assert "导出格式必须是'pdf'、'docx'或'html'" in result.message

    def test_generate_report_with_no_battery_data(self):
        """测试生成报告（没有电池数据）"""
        # 创建输入
        input_data = GenerateReportInput(
            battery_ids=["BAT-001"],
            output_path=str(self.output_dir),
            report_type="standard",
            include_charts=True,
            include_raw_data=False,
            export_format="pdf"
        )
        
        # 模拟依赖方法（返回None，表示未找到电池）
        self.mock_battery_repository.get_by_serial_number.return_value = None
        
        # 执行用例
        result = self.use_case.generate_report(input_data)
        
        # 验证结果
        assert not result.success
        assert "没有找到任何电池数据" in result.message

    def test_generate_report_with_valid_input(self):
        """测试生成报告（有效输入）"""
        # 创建输入
        input_data = GenerateReportInput(
            battery_ids=["BAT-001"],
            output_path=str(self.output_dir),
            report_type="standard",
            include_charts=True,
            include_raw_data=False,
            export_format="pdf"
        )
        
        # 创建模拟电池对象
        mock_battery = Mock()
        mock_battery.serial_number = "BAT-001"
        mock_battery.model = "Li-ion"
        mock_battery.manufacturer = "Manufacturer A"
        mock_battery.chemistry = "Lithium-ion"
        mock_battery.nominal_capacity = 2.0
        mock_battery.nominal_voltage = 3.7
        mock_battery.state_of_health = 95.0
        mock_battery.state_of_charge = 80.0
        
        # 模拟依赖方法
        self.mock_battery_repository.get_by_serial_number.return_value = mock_battery
        
        # 执行用例
        result = self.use_case.generate_report(input_data)
        
        # 验证结果
        assert result.success
        assert "报告生成完成" in result.message
        assert len(result.report_files) == 1
        assert result.generated_reports == 1
        
        # 验证报告文件是否存在
        report_file = result.report_files[0]
        assert os.path.exists(report_file)

    def test_export_report_with_nonexistent_file(self):
        """测试导出报告（不存在的文件）"""
        # 执行导出
        result = self.use_case.export_report("nonexistent/file.pdf", "pdf")
        
        # 验证结果
        assert not result.success
        assert "报告文件不存在" in result.message

    def test_export_report_with_invalid_format(self):
        """测试导出报告（无效的格式）"""
        # 创建测试报告文件
        test_report = self.output_dir / "test_report.pdf"
        test_report.write_text("")
        
        # 执行导出
        result = self.use_case.export_report(str(test_report), "invalid")
        
        # 验证结果
        assert not result.success
        assert "不支持的导出格式" in result.message

    def test_export_report_with_valid_input(self):
        """测试导出报告（有效输入）"""
        # 创建测试报告文件
        test_report = self.output_dir / "test_report.pdf"
        test_report.write_text("")
        
        # 执行导出
        result = self.use_case.export_report(str(test_report), "pdf")
        
        # 验证结果
        assert result.success
        assert "报告导出成功" in result.message
        assert len(result.report_files) == 1
        assert result.generated_reports == 1

    def test_batch_processing_with_invalid_input(self):
        """测试批量处理报告生成（无效输入）"""
        # 创建无效输入（缺少数据目录列表）
        input_data = BatchProcessingInput(
            data_directories=[],  # 空数据目录列表
            output_path=str(self.output_dir),
            report_type="standard",
            include_charts=True,
            export_format="pdf"
        )
        
        # 执行批量处理
        result = self.use_case.batch_processing(input_data)
        
        # 验证结果
        assert not result.success
        assert "缺少数据目录列表" in result.message

    def test_batch_processing_with_valid_input(self):
        """测试批量处理报告生成（有效输入）"""
        # 创建输入
        input_data = BatchProcessingInput(
            data_directories=[str(self.data_dir)],
            output_path=str(self.output_dir),
            report_type="standard",
            include_charts=True,
            export_format="pdf"
        )
        
        # 执行批量处理
        result = self.use_case.batch_processing(input_data)
        
        # 验证结果
        assert result.success
        assert "批量处理报告生成完成" in result.message
        assert len(result.report_files) == 1
        assert result.generated_reports == 1
        
        # 验证报告文件是否存在
        report_file = result.report_files[0]
        assert os.path.exists(report_file)
