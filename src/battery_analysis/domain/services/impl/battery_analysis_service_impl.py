# -*- coding: utf-8 -*-
"""
BatteryAnalysisServiceImpl服务实现

Domain层服务的具体实现，封装电池分析的核心业务逻辑
"""

from typing import Dict, Any, List, Optional
from battery_analysis.domain.entities.test_result import TestResult
from battery_analysis.domain.entities.battery import Battery
from battery_analysis.domain.entities.test_profile import TestProfile
from battery_analysis.domain.services.battery_analysis_service import BatteryAnalysisService


class BatteryAnalysisServiceImpl(BatteryAnalysisService):
    """电池分析服务实现类"""
    
    def calculate_state_of_health(self, test_result: TestResult, battery: Battery) -> float:
        """计算电池健康状态(SOH)
        
        使用当前容量与标称容量的比率计算SOH
        """
        # SOH = (实际容量 / 标称容量) * 100
        soh = (test_result.capacity / battery.nominal_capacity) * 100
        return max(0.0, min(100.0, soh))
    
    def calculate_state_of_charge(self, voltage: float, battery: Battery) -> float:
        """计算电池充电状态(SOC)
        
        使用简单的电压-SOC关系计算，实际应用中可能需要更复杂的算法
        """
        # 电压范围映射到SOC (0-100%)
        voltage_range = battery.max_voltage - battery.min_voltage
        soc = ((voltage - battery.min_voltage) / voltage_range) * 100
        return max(0.0, min(100.0, soc))
    
    def analyze_cycle_life(self, test_results: List[TestResult], battery: Battery) -> Dict[str, Any]:
        """分析电池循环寿命
        
        根据测试结果分析电池的循环寿命特性
        """
        if not test_results:
            return {
                "total_cycles": 0,
                "average_capacity": 0.0,
                "capacity_fade_rate": 0.0,
                "estimated_remaining_cycles": 0
            }
        
        # 按循环次数排序
        sorted_results = sorted(test_results, key=lambda x: x.cycle_count)
        
        # 计算总循环次数
        total_cycles = sorted_results[-1].cycle_count
        
        # 计算平均容量
        average_capacity = sum(result.capacity for result in test_results) / len(test_results)
        
        # 计算容量衰减率
        initial_capacity = sorted_results[0].capacity if sorted_results else 0.0
        final_capacity = sorted_results[-1].capacity if sorted_results else 0.0
        capacity_fade = initial_capacity - final_capacity
        capacity_fade_rate = (capacity_fade / initial_capacity) * 100 if initial_capacity > 0 else 0.0
        
        # 估算剩余循环次数（简单模型）
        # 假设当容量衰减到80%时，电池寿命结束
        remaining_capacity_percent = (final_capacity / battery.nominal_capacity) * 100
        estimated_remaining_cycles = 0
        
        if remaining_capacity_percent > 80 and capacity_fade_rate > 0:
            remaining_capacity_needed = remaining_capacity_percent - 80
            estimated_remaining_cycles = int((remaining_capacity_needed / capacity_fade_rate) * total_cycles)
        
        return {
            "total_cycles": total_cycles,
            "average_capacity": round(average_capacity, 2),
            "capacity_fade_rate": round(capacity_fade_rate, 2),
            "estimated_remaining_cycles": estimated_remaining_cycles
        }
    
    def validate_test_result(self, test_result: TestResult, test_profile: TestProfile, battery: Battery) -> Dict[str, Any]:
        """验证测试结果是否符合测试配置要求
        
        检查测试结果是否在测试配置的允许范围内
        """
        validation_results = {
            "is_valid": True,
            "details": [],
            "failed_checks": []
        }
        
        # 检查温度范围
        if test_result.temperature < test_profile.min_temperature or test_result.temperature > test_profile.max_temperature:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("temperature_range")
            validation_results["details"].append(f"温度 {test_result.temperature}°C 超出允许范围 [{test_profile.min_temperature}, {test_profile.max_temperature}]°C")
        
        # 检查电压范围
        if test_result.voltage > test_profile.test_voltage * 1.1 or test_result.voltage < test_profile.test_voltage * 0.9:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("voltage_range")
            validation_results["details"].append(f"电压 {test_result.voltage}V 超出允许范围 [{test_profile.test_voltage * 0.9}, {test_profile.test_voltage * 1.1}]V")
        
        # 检查电流范围
        if abs(test_result.current) > test_profile.test_current * 1.2:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("current_range")
            validation_results["details"].append(f"电流 {test_result.current}A 超出允许范围 [-{test_profile.test_current * 1.2}, {test_profile.test_current * 1.2}]A")
        
        # 检查容量是否在合理范围内
        if test_result.capacity < battery.nominal_capacity * 0.5 or test_result.capacity > battery.nominal_capacity * 1.2:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("capacity_range")
            validation_results["details"].append(f"容量 {test_result.capacity}Ah 超出合理范围 [{battery.nominal_capacity * 0.5}, {battery.nominal_capacity * 1.2}]Ah")
        
        return validation_results
    
    def calculate_performance_metrics(self, test_result: TestResult, battery: Battery) -> Dict[str, float]:
        """计算电池性能指标
        
        计算各种电池性能指标
        """
        # 计算健康状态
        soh = self.calculate_state_of_health(test_result, battery)
        
        # 计算充电效率（简单模型）
        charge_efficiency = 100.0 - (test_result.internal_resistance * 0.1)  # 内阻越大，效率越低
        charge_efficiency = max(0.0, min(100.0, charge_efficiency))
        
        # 计算能量密度 (Wh/kg)
        energy = test_result.capacity * test_result.voltage  # Wh
        energy_density = energy / battery.weight if battery.weight > 0 else 0.0
        
        # 计算功率密度 (W/kg)
        power = test_result.voltage * test_result.current  # W
        power_density = power / battery.weight if battery.weight > 0 else 0.0
        
        return {
            "soh": round(soh, 2),
            "charge_efficiency": round(charge_efficiency, 2),
            "energy_density": round(energy_density, 2),
            "power_density": round(power_density, 2),
            "temperature_stability": round(100.0 - abs(test_result.temperature - 25.0) * 2, 2)  # 越接近25°C，稳定性越高
        }
    
    def detect_anomalies(self, test_results: List[TestResult]) -> List[Dict[str, Any]]:
        """检测测试结果中的异常
        
        识别测试结果中的异常值
        """
        anomalies = []
        
        if len(test_results) < 3:  # 数据不足，无法检测异常
            return anomalies
        
        # 计算各项指标的平均值和标准差
        capacities = [result.capacity for result in test_results]
        voltages = [result.voltage for result in test_results]
        currents = [result.current for result in test_results]
        temperatures = [result.temperature for result in test_results]
        internal_resistances = [result.internal_resistance for result in test_results]
        
        # 使用公共工具函数进行异常检测
        from battery_analysis.utils.data_utils import detect_outliers as common_detect_outliers
        
        # 检测每个结果的异常
        for i in range(len(test_results)):
            anomalies.extend(common_detect_outliers(capacities, "capacity", i, test_results))
            anomalies.extend(common_detect_outliers(voltages, "voltage", i, test_results))
            anomalies.extend(common_detect_outliers(currents, "current", i, test_results))
            anomalies.extend(common_detect_outliers(temperatures, "temperature", i, test_results))
            anomalies.extend(common_detect_outliers(internal_resistances, "internal_resistance", i, test_results))
        
        return anomalies
    
    def compare_test_results(self, test_result1: TestResult, test_result2: TestResult) -> Dict[str, Any]:
        """比较两个测试结果
        
        比较两个测试结果的差异
        """
        return {
            "test_id_1": test_result1.test_id,
            "test_id_2": test_result2.test_id,
            "cycle_count_difference": test_result2.cycle_count - test_result1.cycle_count,
            "capacity_difference": round(test_result2.capacity - test_result1.capacity, 3),
            "capacity_difference_percent": round(((test_result2.capacity - test_result1.capacity) / test_result1.capacity * 100) if test_result1.capacity > 0 else 0, 2),
            "internal_resistance_difference": round(test_result2.internal_resistance - test_result1.internal_resistance, 3),
            "temperature_difference": round(test_result2.temperature - test_result1.temperature, 2),
            "voltage_difference": round(test_result2.voltage - test_result1.voltage, 3),
            "current_difference": round(test_result2.current - test_result1.current, 3)
        }
