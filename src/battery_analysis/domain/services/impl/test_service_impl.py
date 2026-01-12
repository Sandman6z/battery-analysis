# -*- coding: utf-8 -*-
"""
TestServiceImpl服务实现

Domain层服务的具体实现，封装测试流程和测试结果管理的核心业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from battery_analysis.domain.entities.test_result import TestResult
from battery_analysis.domain.entities.test_profile import TestProfile
from battery_analysis.domain.entities.battery import Battery
from battery_analysis.domain.services.test_service import TestService


class TestServiceImpl(TestService):
    """测试服务实现类"""
    
    def create_test_result(self, battery: Battery, test_profile: TestProfile, 
                         test_data: Dict[str, Any], operator: str, 
                         equipment: str) -> TestResult:
        """创建测试结果
        
        Args:
            battery: 电池实体
            test_profile: 测试配置实体
            test_data: 测试数据
            operator: 测试操作员
            equipment: 测试设备
            
        Returns:
            创建的测试结果实体
        """
        # 生成测试ID
        test_id = self.generate_test_id(battery)
        
        # 创建测试结果实体
        test_result = TestResult(
            test_id=test_id,
            test_date=datetime.now(),
            battery_serial_number=battery.serial_number,
            test_equipment=equipment,
            test_operator=operator,
            temperature=test_data.get("temperature", 25.0),
            humidity=test_data.get("humidity", 50.0),
            voltage=test_data.get("voltage", battery.nominal_voltage),
            current=test_data.get("current", 0.0),
            capacity=test_data.get("capacity", battery.nominal_capacity),
            internal_resistance=test_data.get("internal_resistance", 0.0),
            cycle_count=test_data.get("cycle_count", 0),
            max_temperature=test_data.get("max_temperature", test_data.get("temperature", 25.0)),
            min_temperature=test_data.get("min_temperature", test_data.get("temperature", 25.0)),
            raw_data=test_data.get("raw_data"),
            is_passed=test_data.get("is_passed", True),
            test_status=test_data.get("test_status", "completed")
        )
        
        return test_result
    
    def update_test_result(self, test_result: TestResult, test_data: Dict[str, Any]) -> TestResult:
        """更新测试结果
        
        Args:
            test_result: 测试结果实体
            test_data: 更新的测试数据
            
        Returns:
            更新后的测试结果实体
        """
        # 更新测试结果的属性
        if "temperature" in test_data:
            test_result.temperature = test_data["temperature"]
        if "humidity" in test_data:
            test_result.humidity = test_data["humidity"]
        if "voltage" in test_data:
            test_result.voltage = test_data["voltage"]
        if "current" in test_data:
            test_result.current = test_data["current"]
        if "capacity" in test_data:
            test_result.capacity = test_data["capacity"]
        if "internal_resistance" in test_data:
            test_result.internal_resistance = test_data["internal_resistance"]
        if "cycle_count" in test_data:
            test_result.cycle_count = test_data["cycle_count"]
        if "max_temperature" in test_data:
            test_result.max_temperature = test_data["max_temperature"]
        if "min_temperature" in test_data:
            test_result.min_temperature = test_data["min_temperature"]
        if "raw_data" in test_data:
            test_result.raw_data = test_data["raw_data"]
        if "is_passed" in test_data:
            test_result.is_passed = test_data["is_passed"]
        if "test_status" in test_data:
            test_result.test_status = test_data["test_status"]
        
        return test_result
    
    def validate_test_profile(self, test_profile: TestProfile) -> Dict[str, Any]:
        """验证测试配置是否有效
        
        Args:
            test_profile: 测试配置实体
            
        Returns:
            验证结果，包含是否有效和详细信息
        """
        validation_results = {
            "is_valid": True,
            "details": [],
            "failed_checks": []
        }
        
        # 验证测试电压
        if test_profile.test_voltage <= 0:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("test_voltage")
            validation_results["details"].append("测试电压必须大于0")
        
        # 验证测试电流
        if test_profile.test_current <= 0:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("test_current")
            validation_results["details"].append("测试电流必须大于0")
        
        # 验证最大循环次数
        if test_profile.max_cycles <= 0:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("max_cycles")
            validation_results["details"].append("最大循环次数必须大于0")
        
        # 验证温度范围
        if test_profile.min_temperature > test_profile.max_temperature:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("temperature_range")
            validation_results["details"].append("最低温度不能大于最高温度")
        
        # 验证充电电压
        if test_profile.charge_voltage <= 0:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("charge_voltage")
            validation_results["details"].append("充电电压必须大于0")
        
        # 验证放电电压
        if test_profile.discharge_voltage <= 0:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("discharge_voltage")
            validation_results["details"].append("放电电压必须大于0")
        
        # 验证截止电压
        if test_profile.cut_off_voltage <= 0:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("cut_off_voltage")
            validation_results["details"].append("截止电压必须大于0")
        
        # 验证采样间隔
        if test_profile.sampling_interval <= 0:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("sampling_interval")
            validation_results["details"].append("采样间隔必须大于0")
        
        return validation_results
    
    def generate_test_id(self, battery: Battery) -> str:
        """生成测试ID
        
        Args:
            battery: 电池实体
            
        Returns:
            生成的测试ID
        """
        # 生成格式: BAT-{电池序列号}-{年份}{月份}{日期}-{UUID前8位}
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        uuid_str = str(uuid4())[:8]
        
        return f"BAT-{battery.serial_number}-{date_str}-{uuid_str}"
    
    def get_test_summary(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """获取测试结果摘要
        
        Args:
            test_results: 测试结果列表
            
        Returns:
            测试结果摘要
        """
        if not test_results:
            return {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "average_capacity": 0.0,
                "average_internal_resistance": 0.0,
                "test_dates": {
                    "first_test": None,
                    "last_test": None
                }
            }
        
        # 计算测试数量
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result.is_passed)
        failed_tests = total_tests - passed_tests
        
        # 计算平均容量
        average_capacity = sum(result.capacity for result in test_results) / total_tests
        
        # 计算平均内阻
        average_internal_resistance = sum(result.internal_resistance for result in test_results) / total_tests
        
        # 获取测试日期范围
        test_dates = [result.test_date for result in test_results]
        first_test = min(test_dates)
        last_test = max(test_dates)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": round((passed_tests / total_tests) * 100, 2),
            "average_capacity": round(average_capacity, 2),
            "average_internal_resistance": round(average_internal_resistance, 2),
            "test_dates": {
                "first_test": first_test.strftime("%Y-%m-%d %H:%M:%S"),
                "last_test": last_test.strftime("%Y-%m-%d %H:%M:%S"),
                "test_period_days": (last_test - first_test).days
            }
        }
    
    def calculate_test_statistics(self, test_results: List[TestResult]) -> Dict[str, float]:
        """计算测试统计信息
        
        Args:
            test_results: 测试结果列表
            
        Returns:
            测试统计信息
        """
        if not test_results:
            return {
                "avg_temperature": 0.0,
                "avg_humidity": 0.0,
                "avg_voltage": 0.0,
                "avg_current": 0.0,
                "avg_capacity": 0.0,
                "avg_internal_resistance": 0.0,
                "avg_cycle_count": 0.0
            }
        
        # 计算各项统计指标
        avg_temperature = sum(result.temperature for result in test_results) / len(test_results)
        avg_humidity = sum(result.humidity for result in test_results) / len(test_results)
        avg_voltage = sum(result.voltage for result in test_results) / len(test_results)
        avg_current = sum(result.current for result in test_results) / len(test_results)
        avg_capacity = sum(result.capacity for result in test_results) / len(test_results)
        avg_internal_resistance = sum(result.internal_resistance for result in test_results) / len(test_results)
        avg_cycle_count = sum(result.cycle_count for result in test_results) / len(test_results)
        
        return {
            "avg_temperature": round(avg_temperature, 2),
            "avg_humidity": round(avg_humidity, 2),
            "avg_voltage": round(avg_voltage, 2),
            "avg_current": round(avg_current, 2),
            "avg_capacity": round(avg_capacity, 2),
            "avg_internal_resistance": round(avg_internal_resistance, 2),
            "avg_cycle_count": round(avg_cycle_count, 2)
        }
    
    def group_test_results_by_criteria(self, test_results: List[TestResult], 
                                      criteria: str) -> Dict[str, List[TestResult]]:
        """按指定条件分组测试结果
        
        Args:
            test_results: 测试结果列表
            criteria: 分组条件 (如: 'date', 'battery_type', 'operator')
            
        Returns:
            按条件分组的测试结果
        """
        grouped_results = {}
        
        for result in test_results:
            # 根据不同条件获取分组键
            if criteria == "date":
                # 按日期分组 (YYYY-MM-DD)
                group_key = result.test_date.strftime("%Y-%m-%d")
            elif criteria == "operator":
                # 按操作员分组
                group_key = result.test_operator
            elif criteria == "equipment":
                # 按测试设备分组
                group_key = result.test_equipment
            elif criteria == "temperature_range":
                # 按温度范围分组
                if result.temperature < 20:
                    group_key = "< 20°C"
                elif result.temperature < 30:
                    group_key = "20-30°C"
                else:
                    group_key = ">= 30°C"
            else:
                # 默认按测试ID分组
                group_key = result.test_id
            
            # 添加到对应的分组
            if group_key not in grouped_results:
                grouped_results[group_key] = []
            grouped_results[group_key].append(result)
        
        return grouped_results
