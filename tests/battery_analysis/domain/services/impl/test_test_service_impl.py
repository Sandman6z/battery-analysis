import pytest
from unittest.mock import Mock, patch
from battery_analysis.domain.services.impl.test_service_impl import TestServiceImpl


class TestTestServiceImpl:
    def setup_method(self):
        self.service = TestServiceImpl()

    def test_create_test_result(self):
        # 创建电池实体的模拟对象
        battery = Mock()
        battery.serial_number = "BAT001"
        battery.nominal_voltage = 3.7
        battery.nominal_capacity = 2.0
        battery.weight = 0.1
        battery.max_voltage = 4.2
        battery.min_voltage = 2.5
        battery.max_current = 5.0
        battery.battery_type = "Li-ion"
        battery.status = "active"
        
        # 创建测试配置实体的模拟对象
        test_profile = Mock()
        test_profile.test_voltage = 4.2
        test_profile.test_current = 0.5
        test_profile.min_temperature = 0
        test_profile.max_temperature = 40
        test_profile.max_cycles = 1000
        test_profile.charge_voltage = 4.2
        test_profile.discharge_voltage = 2.5
        test_profile.cut_off_voltage = 2.5
        test_profile.sampling_interval = 1.0
        
        # 创建测试数据
        test_data = {
            "temperature": 25.0,
            "humidity": 50.0,
            "voltage": 4.2,
            "current": 0.5,
            "capacity": 2.0,
            "internal_resistance": 0.1,
            "cycle_count": 0
        }
        
        # 调用方法
        result = self.service.create_test_result(battery, test_profile, test_data, "Operator", "Equipment")
        
        # 验证结果
        assert hasattr(result, "test_id")
        assert hasattr(result, "test_date")
        assert hasattr(result, "battery_serial_number")

    def test_update_test_result(self):
        # 创建测试结果实体的模拟对象
        test_result = Mock()
        test_result.temperature = 25.0
        test_result.humidity = 50.0
        test_result.voltage = 4.2
        test_result.current = 0.5
        test_result.capacity = 2.0
        test_result.internal_resistance = 0.1
        test_result.cycle_count = 0
        test_result.max_temperature = 25.0
        test_result.min_temperature = 25.0
        test_result.raw_data = None
        test_result.is_passed = True
        test_result.test_status = "completed"
        
        # 创建更新的测试数据
        test_data = {
            "temperature": 26.0,
            "humidity": 55.0,
            "voltage": 4.1,
            "current": 0.6,
            "capacity": 1.9,
            "internal_resistance": 0.11,
            "cycle_count": 1,
            "max_temperature": 26.0,
            "min_temperature": 24.0,
            "raw_data": {"data": [1, 2, 3]},
            "is_passed": True,
            "test_status": "completed"
        }
        
        # 调用方法
        result = self.service.update_test_result(test_result, test_data)
        
        # 验证结果
        assert result.temperature == 26.0
        assert result.humidity == 55.0
        assert result.voltage == 4.1
        assert result.current == 0.6
        assert result.capacity == 1.9
        assert result.internal_resistance == 0.11
        assert result.cycle_count == 1
        assert result.max_temperature == 26.0
        assert result.min_temperature == 24.0
        assert result.raw_data == {"data": [1, 2, 3]}
        assert result.is_passed == True
        assert result.test_status == "completed"

    def test_validate_test_profile(self):
        # 创建测试配置实体的模拟对象
        test_profile = Mock()
        test_profile.test_voltage = 4.2
        test_profile.test_current = 0.5
        test_profile.min_temperature = 0
        test_profile.max_temperature = 40
        test_profile.max_cycles = 1000
        test_profile.charge_voltage = 4.2
        test_profile.discharge_voltage = 2.5
        test_profile.cut_off_voltage = 2.5
        test_profile.sampling_interval = 1.0
        
        # 调用方法
        result = self.service.validate_test_profile(test_profile)
        
        # 验证结果
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "details" in result
        assert "failed_checks" in result

    def test_generate_test_id(self):
        # 创建电池实体的模拟对象
        battery = Mock()
        battery.serial_number = "BAT001"
        
        # 调用方法
        result = self.service.generate_test_id(battery)
        
        # 验证结果
        assert isinstance(result, str)
        assert "BAT001" in result

    def test_get_test_summary(self):
        # 导入 datetime 模块
        from datetime import datetime, timedelta
        
        # 创建实际的日期对象
        date1 = datetime(2024, 1, 1, 10, 0, 0)
        date2 = datetime(2024, 1, 2, 10, 0, 0)
        
        # 创建测试结果实体的模拟对象
        test_result1 = Mock()
        test_result1.is_passed = True
        test_result1.test_date = date1
        test_result1.capacity = 2.0
        test_result1.internal_resistance = 0.1
        
        test_result2 = Mock()
        test_result2.is_passed = False
        test_result2.test_date = date2
        test_result2.capacity = 1.9
        test_result2.internal_resistance = 0.11
        
        # 调用方法
        result = self.service.get_test_summary([test_result1, test_result2])
        
        # 验证结果
        assert isinstance(result, dict)
        assert "total_tests" in result
        assert "passed_tests" in result
        assert "failed_tests" in result
        assert "average_capacity" in result
        assert "average_internal_resistance" in result
        assert "test_dates" in result

    def test_calculate_test_statistics(self):
        # 创建测试结果实体的模拟对象
        test_result1 = Mock()
        test_result1.temperature = 25.0
        test_result1.humidity = 50.0
        test_result1.voltage = 4.2
        test_result1.current = 0.5
        test_result1.capacity = 2.0
        test_result1.internal_resistance = 0.1
        test_result1.cycle_count = 0
        
        test_result2 = Mock()
        test_result2.temperature = 26.0
        test_result2.humidity = 55.0
        test_result2.voltage = 4.1
        test_result2.current = 0.6
        test_result2.capacity = 1.9
        test_result2.internal_resistance = 0.11
        test_result2.cycle_count = 1
        
        # 调用方法
        result = self.service.calculate_test_statistics([test_result1, test_result2])
        
        # 验证结果
        assert isinstance(result, dict)
        assert "avg_temperature" in result
        assert "avg_humidity" in result
        assert "avg_voltage" in result
        assert "avg_current" in result
        assert "avg_capacity" in result
        assert "avg_internal_resistance" in result
        assert "avg_cycle_count" in result

    def test_group_test_results_by_criteria(self):
        # 创建测试结果实体的模拟对象
        test_result1 = Mock()
        test_result1.test_date = Mock()
        test_result1.test_date.strftime.return_value = "2024-01-01"
        test_result1.test_operator = "Operator1"
        test_result1.test_equipment = "Equipment1"
        test_result1.temperature = 25.0
        
        test_result2 = Mock()
        test_result2.test_date = Mock()
        test_result2.test_date.strftime.return_value = "2024-01-01"
        test_result2.test_operator = "Operator1"
        test_result2.test_equipment = "Equipment2"
        test_result2.temperature = 26.0
        
        # 调用方法
        result = self.service.group_test_results_by_criteria([test_result1, test_result2], "date")
        
        # 验证结果
        assert isinstance(result, dict)
        assert "2024-01-01" in result
        assert len(result["2024-01-01"]) == 2