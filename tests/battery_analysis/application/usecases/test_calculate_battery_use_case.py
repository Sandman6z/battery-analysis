# -*- coding: utf-8 -*-
"""
CalculateBatteryUseCase测试
"""

import pytest
from unittest.mock import Mock
from battery_analysis.application.usecases.calculate_battery_use_case import (
    CalculateBatteryUseCase, CalculateBatteryInput, CalculateBatteryOutput
)
from battery_analysis.domain.entities.battery import Battery


class TestCalculateBatteryUseCase:
    """电池计算用例测试类"""

    def setup_method(self):
        """设置测试环境"""
        # 创建模拟依赖
        self.mock_battery_repository = Mock()
        self.mock_battery_analysis_service = Mock()
        
        # 创建测试用例实例
        self.use_case = CalculateBatteryUseCase(
            battery_repository=self.mock_battery_repository,
            battery_analysis_service=self.mock_battery_analysis_service
        )

    def test_execute_with_invalid_input(self):
        """测试执行电池计算用例（无效输入）"""
        # 创建无效输入（缺少必要字段）
        input_data = CalculateBatteryInput(
            battery_type="",  # 空电池类型
            construction_method="Method A",
            specification_type="Type A",
            specification_method="Method B",
            manufacturer="Manufacturer A",
            tester_location="Location A",
            tested_by="Tester A",
            reported_by="Reporter A",
            temperature="25°C",
            input_path="input/path",
            output_path="output/path",
            barcode="BC-001"
        )
        
        # 执行用例
        result = self.use_case.execute(input_data)
        
        # 验证结果
        assert not result.success
        assert "缺少必要字段" in result.message

    def test_execute_with_valid_input(self):
        """测试执行电池计算用例（有效输入）"""
        # 创建有效输入
        input_data = CalculateBatteryInput(
            battery_type="Li-ion",
            construction_method="Method A",
            specification_type="Type A",
            specification_method="Method B",
            manufacturer="Manufacturer A",
            tester_location="Location A",
            tested_by="Tester A",
            reported_by="Reporter A",
            temperature="25°C",
            input_path="input/path",
            output_path="output/path",
            barcode="BC-001"
        )
        
        # 模拟依赖方法
        mock_battery = Mock(spec=Battery)
        mock_battery.serial_number = "BC-001"
        self.mock_battery_analysis_service.calculate_battery_health.return_value = mock_battery
        self.mock_battery_analysis_service.analyze_battery_performance.return_value = {
            "capacity": 2.0,
            "voltage": 3.7,
            "health": 95.0
        }
        self.mock_battery_repository.save.return_value = mock_battery
        
        # 执行用例
        result = self.use_case.execute(input_data)
        
        # 验证结果
        assert result.success
        assert "电池计算已完成" in result.message
        assert result.battery is not None
        assert result.performance_data is not None
        assert "capacity" in result.performance_data
        assert "voltage" in result.performance_data
        assert "health" in result.performance_data

    def test_execute_with_exception(self):
        """测试执行电池计算用例（异常情况）"""
        # 创建有效输入
        input_data = CalculateBatteryInput(
            battery_type="Li-ion",
            construction_method="Method A",
            specification_type="Type A",
            specification_method="Method B",
            manufacturer="Manufacturer A",
            tester_location="Location A",
            tested_by="Tester A",
            reported_by="Reporter A",
            temperature="25°C",
            input_path="input/path",
            output_path="output/path",
            barcode="BC-001"
        )
        
        # 模拟依赖方法抛出异常
        self.mock_battery_analysis_service.calculate_battery_health.side_effect = Exception("测试异常")
        
        # 执行用例
        result = self.use_case.execute(input_data)
        
        # 验证结果
        assert not result.success
        assert "电池计算失败" in result.message
        assert "测试异常" in result.message

    def test_input_validation(self):
        """测试输入数据验证"""
        # 创建输入数据（所有字段为空）
        input_data = CalculateBatteryInput(
            battery_type="",
            construction_method="",
            specification_type="",
            specification_method="",
            manufacturer="",
            tester_location="",
            tested_by="",
            reported_by="",
            temperature="",
            input_path="",
            output_path="",
            barcode=""
        )
        
        # 验证输入
        errors = input_data.validate()
        
        # 验证结果
        assert len(errors) == 12  # 应该有12个错误
        assert "battery_type" in errors
        assert "construction_method" in errors
        assert "specification_type" in errors
        assert "specification_method" in errors
        assert "manufacturer" in errors
        assert "tester_location" in errors
        assert "tested_by" in errors
        assert "reported_by" in errors
        assert "temperature" in errors
        assert "input_path" in errors
        assert "output_path" in errors
        assert "barcode" in errors

    def test_input_validation_with_all_fields(self):
        """测试输入数据验证（所有字段都有值）"""
        # 创建输入数据（所有字段都有值）
        input_data = CalculateBatteryInput(
            battery_type="Li-ion",
            construction_method="Method A",
            specification_type="Type A",
            specification_method="Method B",
            manufacturer="Manufacturer A",
            tester_location="Location A",
            tested_by="Tester A",
            reported_by="Reporter A",
            temperature="25°C",
            input_path="input/path",
            output_path="output/path",
            barcode="BC-001"
        )
        
        # 验证输入
        errors = input_data.validate()
        
        # 验证结果
        assert len(errors) == 0  # 应该没有错误
