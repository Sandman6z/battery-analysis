"""
BatteryAnalysisService实现类

基础设施层，实现Domain层的BatteryAnalysisService接口
"""

import logging
from typing import Dict, List, Optional, Any
from battery_analysis.domain.entities.test_result import TestResult
from battery_analysis.domain.entities.battery import Battery
from battery_analysis.domain.entities.test_profile import TestProfile
from battery_analysis.domain.services.battery_analysis_service import BatteryAnalysisService


class BatteryAnalysisServiceImpl(BatteryAnalysisService):
    """电池分析服务实现类"""
    
    def __init__(self):
        """初始化电池分析服务"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化BatteryAnalysisServiceImpl")
    
    def calculate_state_of_health(self, test_result: TestResult, battery: Battery) -> float:
        """
        计算电池健康状态(SOH)
        
        Args:
            test_result: 测试结果实体
            battery: 电池实体
            
        Returns:
            健康状态百分比 (0-100)
        """
        self.logger.info("计算电池健康状态(SOH): %s", battery.serial_number)
        
        # SOH = (实际容量 / 标称容量) * 100
        soh = (test_result.capacity / battery.nominal_capacity) * 100
        return max(0.0, min(100.0, soh))
    
    def calculate_state_of_charge(self, voltage: float, battery: Battery) -> float:
        """
        计算电池充电状态(SOC)
        
        Args:
            voltage: 当前电压 (V)
            battery: 电池实体
            
        Returns:
            充电状态百分比 (0-100)
        """
        self.logger.info("计算电池充电状态(SOC): %s, 电压: %.2fV", battery.serial_number, voltage)
        
        # 电压范围映射到SOC (0-100%)
        voltage_range = battery.max_voltage - battery.min_voltage
        soc = ((voltage - battery.min_voltage) / voltage_range) * 100
        return max(0.0, min(100.0, soc))
    
    def analyze_cycle_life(self, test_results: List[TestResult], battery: Battery) -> Dict[str, Any]:
        """
        分析电池循环寿命
        
        Args:
            test_results: 测试结果列表
            battery: 电池实体
            
        Returns:
            循环寿命分析结果
        """
        self.logger.info("分析电池循环寿命: %s, 测试结果数量: %d", battery.serial_number, len(test_results))
        
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
        """
        验证测试结果是否符合测试配置要求
        
        Args:
            test_result: 测试结果实体
            test_profile: 测试配置实体
            battery: 电池实体
            
        Returns:
            验证结果，包含是否通过和详细信息
        """
        self.logger.info("验证测试结果: %s, 测试ID: %s", battery.serial_number, test_result.test_id)
        
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
        """
        计算电池性能指标
        
        Args:
            test_result: 测试结果实体
            battery: 电池实体
            
        Returns:
            性能指标字典
        """
        self.logger.info("计算电池性能指标: %s, 测试ID: %s", battery.serial_number, test_result.test_id)
        
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
        """
        检测测试结果中的异常
        
        Args:
            test_results: 测试结果列表
            
        Returns:
            异常列表
        """
        self.logger.info("检测测试结果中的异常, 测试结果数量: %d", len(test_results))
        
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
        """
        比较两个测试结果
        
        Args:
            test_result1: 第一个测试结果
            test_result2: 第二个测试结果
            
        Returns:
            比较结果
        """
        self.logger.info("比较两个测试结果: %s 和 %s", test_result1.test_id, test_result2.test_id)
        
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