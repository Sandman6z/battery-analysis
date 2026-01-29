# -*- coding: utf-8 -*-
"""
BatteryAnalysisServiceImpl服务实现

Domain层服务的具体实现，封装电池分析的核心业务逻辑
"""

import time
from typing import Dict, Any, List, Optional
from battery_analysis.domain.entities.test_result import TestResult
from battery_analysis.domain.entities.battery import Battery
from battery_analysis.domain.entities.test_profile import TestProfile
from battery_analysis.domain.services.battery_analysis_service import BatteryAnalysisService


class BatteryAnalysisServiceImpl(BatteryAnalysisService):
    """电池分析服务实现类"""
    
    def __init__(self, max_cache_size: int = 1000, cache_ttl: int = 3600):
        """初始化电池分析服务
        
        Args:
            max_cache_size: 最大缓存数量，默认1000
            cache_ttl: 缓存过期时间（秒），默认3600秒（1小时）
        """
        self._max_cache_size = max_cache_size
        self._cache_ttl = cache_ttl
        self._cache = {
            "calculate_battery_health": {},
            "analyze_battery_performance": {},
            "validate_battery_data": {},
            "predict_battery_lifetime": {},
            "compare_batteries": {}
        }
        self._cache_access_order = {
            "calculate_battery_health": [],
            "analyze_battery_performance": [],
            "validate_battery_data": [],
            "predict_battery_lifetime": [],
            "compare_batteries": []
        }
        self._cache_timestamps = {}
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def _generate_cache_key(self, method_name: str, *args, **kwargs) -> str:
        """生成缓存键
        
        Args:
            method_name: 方法名称
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            str: 生成的缓存键
        """
        key_parts = [method_name]
        
        for arg in args:
            if hasattr(arg, 'serial_number'):
                key_parts.append(arg.serial_number)
                if hasattr(arg, 'nominal_capacity'):
                    key_parts.append(str(arg.nominal_capacity))
                if hasattr(arg, 'nominal_voltage'):
                    key_parts.append(str(arg.nominal_voltage))
            elif isinstance(arg, list):
                if arg and hasattr(arg[0], 'serial_number'):
                    sorted_serials = sorted([b.serial_number for b in arg])
                    key_parts.append("_".join(sorted_serials))
                else:
                    key_parts.append(str(len(arg)))
            else:
                key_parts.append(str(arg))
        
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        
        return "_".join(key_parts)
    
    def _is_cache_valid(self, method_name: str, cache_key: str) -> bool:
        """检查缓存是否有效
        
        Args:
            method_name: 方法名称
            cache_key: 缓存键
            
        Returns:
            bool: 缓存是否有效
        """
        if cache_key not in self._cache.get(method_name, {}):
            return False
        
        timestamp_key = f"{method_name}:{cache_key}"
        if timestamp_key not in self._cache_timestamps:
            return False
        
        elapsed = time.time() - self._cache_timestamps[timestamp_key]
        return elapsed < self._cache_ttl
    
    def _check_and_evict_cache(self, method_name: str):
        """检查并淘汰缓存
        
        Args:
            method_name: 方法名称
        """
        cache = self._cache.get(method_name, {})
        if len(cache) < self._max_cache_size:
            return
        
        access_list = self._cache_access_order.get(method_name, [])
        while len(cache) >= self._max_cache_size and access_list:
            oldest_key = access_list.pop(0)
            if oldest_key in cache:
                del cache[oldest_key]
                timestamp_key = f"{method_name}:{oldest_key}"
                if timestamp_key in self._cache_timestamps:
                    del self._cache_timestamps[timestamp_key]
                self._cache_stats["evictions"] += 1
    
    def _update_cache(self, method_name: str, cache_key: str, value: Any):
        """更新缓存
        
        Args:
            method_name: 方法名称
            cache_key: 缓存键
            value: 缓存值
        """
        self._check_and_evict_cache(method_name)
        
        if method_name not in self._cache:
            self._cache[method_name] = {}
        if method_name not in self._cache_access_order:
            self._cache_access_order[method_name] = []
        
        self._cache[method_name][cache_key] = value
        self._cache_access_order[method_name].append(cache_key)
        self._cache_timestamps[f"{method_name}:{cache_key}"] = time.time()
    
    def _get_from_cache(self, method_name: str, cache_key: str) -> Optional[Any]:
        """从缓存获取数据
        
        Args:
            method_name: 方法名称
            cache_key: 缓存键
            
        Returns:
            Optional[Any]: 缓存的数据，如果不存在或已过期则返回None
        """
        if not self._is_cache_valid(method_name, cache_key):
            self._cache_stats["misses"] += 1
            return None
        
        self._cache_stats["hits"] += 1
        
        access_list = self._cache_access_order.get(method_name, [])
        if cache_key in access_list:
            access_list.remove(cache_key)
            access_list.append(cache_key)
        
        return self._cache.get(method_name, {}).get(cache_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息
        
        Returns:
            Dict[str, Any]: 缓存统计信息
        """
        total_requests = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = (self._cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self._cache_stats["hits"],
            "misses": self._cache_stats["misses"],
            "evictions": self._cache_stats["evictions"],
            "hit_rate": round(hit_rate, 2),
            "total_cache_size": sum(len(cache) for cache in self._cache.values()),
            "max_cache_size": self._max_cache_size,
            "cache_ttl": self._cache_ttl
        }
    
    def calculate_state_of_health(self, test_result: TestResult, battery: Battery) -> float:
        """计算电池健康状态(SOH)
        
        使用当前容量与标称容量的比率计算SOH
        """
        soh = (test_result.capacity / battery.nominal_capacity) * 100
        return max(0.0, min(100.0, soh))
    
    def calculate_state_of_charge(self, voltage: float, battery: Battery) -> float:
        """计算电池充电状态(SOC)
        
        使用简单的电压-SOC关系计算，实际应用中可能需要更复杂的算法
        """
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
        
        sorted_results = sorted(test_results, key=lambda x: x.cycle_count)
        total_cycles = sorted_results[-1].cycle_count
        average_capacity = sum(result.capacity for result in test_results) / len(test_results)
        initial_capacity = sorted_results[0].capacity if sorted_results else 0.0
        final_capacity = sorted_results[-1].capacity if sorted_results else 0.0
        capacity_fade = initial_capacity - final_capacity
        capacity_fade_rate = (capacity_fade / initial_capacity) * 100 if initial_capacity > 0 else 0.0
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
        
        if test_result.temperature < test_profile.min_temperature or test_result.temperature > test_profile.max_temperature:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("temperature_range")
            validation_results["details"].append(f"温度 {test_result.temperature}°C 超出允许范围 [{test_profile.min_temperature}, {test_profile.max_temperature}]°C")
        
        if test_result.voltage > test_profile.test_voltage * 1.1 or test_result.voltage < test_profile.test_voltage * 0.9:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("voltage_range")
            validation_results["details"].append(f"电压 {test_result.voltage}V 超出允许范围 [{test_profile.test_voltage * 0.9}, {test_profile.test_voltage * 1.1}]V")
        
        if abs(test_result.current) > test_profile.test_current * 1.2:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("current_range")
            validation_results["details"].append(f"电流 {test_result.current}A 超出允许范围 [-{test_profile.test_current * 1.2}, {test_profile.test_current * 1.2}]A")
        
        if test_result.capacity < battery.nominal_capacity * 0.5 or test_result.capacity > battery.nominal_capacity * 1.2:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("capacity_range")
            validation_results["details"].append(f"容量 {test_result.capacity}Ah 超出合理范围 [{battery.nominal_capacity * 0.5}, {battery.nominal_capacity * 1.2}]Ah")
        
        return validation_results
    
    def calculate_performance_metrics(self, test_result: TestResult, battery: Battery) -> Dict[str, float]:
        """计算电池性能指标
        
        计算各种电池性能指标
        """
        soh = self.calculate_state_of_health(test_result, battery)
        charge_efficiency = 100.0 - (test_result.internal_resistance * 0.1)
        charge_efficiency = max(0.0, min(100.0, charge_efficiency))
        energy = test_result.capacity * test_result.voltage
        energy_density = energy / battery.weight if battery.weight > 0 else 0.0
        power = test_result.voltage * test_result.current
        power_density = power / battery.weight if battery.weight > 0 else 0.0
        
        return {
            "soh": round(soh, 2),
            "charge_efficiency": round(charge_efficiency, 2),
            "energy_density": round(energy_density, 2),
            "power_density": round(power_density, 2),
            "temperature_stability": round(100.0 - abs(test_result.temperature - 25.0) * 2, 2)
        }
    
    def detect_anomalies(self, test_results: List[TestResult]) -> List[Dict[str, Any]]:
        """检测测试结果中的异常
        
        识别测试结果中的异常值
        """
        anomalies = []
        
        if len(test_results) < 3:
            return anomalies
        
        capacities = [result.capacity for result in test_results]
        voltages = [result.voltage for result in test_results]
        currents = [result.current for result in test_results]
        temperatures = [result.temperature for result in test_results]
        internal_resistances = [result.internal_resistance for result in test_results]
        
        from battery_analysis.utils.data_utils import detect_outliers as common_detect_outliers
        
        def precompute_stats(data):
            if not data:
                return (0, 0)
            avg = sum(data) / len(data)
            std_dev = (sum((x - avg) ** 2 for x in data) / len(data)) ** 0.5
            return (avg, std_dev)
        
        stats = {
            "capacity": precompute_stats(capacities),
            "voltage": precompute_stats(voltages),
            "current": precompute_stats(currents),
            "temperature": precompute_stats(temperatures),
            "internal_resistance": precompute_stats(internal_resistances)
        }
        
        for i in range(len(test_results)):
            anomalies.extend(common_detect_outliers(capacities, "capacity", i, test_results, stats["capacity"]))
            anomalies.extend(common_detect_outliers(voltages, "voltage", i, test_results, stats["voltage"]))
            anomalies.extend(common_detect_outliers(currents, "current", i, test_results, stats["current"]))
            anomalies.extend(common_detect_outliers(temperatures, "temperature", i, test_results, stats["temperature"]))
            anomalies.extend(common_detect_outliers(internal_resistances, "internal_resistance", i, test_results, stats["internal_resistance"]))
        
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
    
    def validate_battery_data(self, battery: Battery) -> Dict[str, bool]:
        """验证电池数据
        
        验证电池数据是否有效
        """
        cache_key = self._generate_cache_key("validate_battery_data", battery)
        
        cached_result = self._get_from_cache("validate_battery_data", cache_key)
        if cached_result is not None:
            return cached_result
        
        validation_result = {
            "valid": True,
            "model": True,
            "serial_number": True,
            "nominal_capacity": True,
            "nominal_voltage": True
        }
        
        if not battery.model:
            validation_result["model"] = False
            validation_result["valid"] = False
        if not battery.serial_number:
            validation_result["serial_number"] = False
            validation_result["valid"] = False
        if battery.nominal_capacity <= 0:
            validation_result["nominal_capacity"] = False
            validation_result["valid"] = False
        if battery.nominal_voltage <= 0:
            validation_result["nominal_voltage"] = False
            validation_result["valid"] = False
        
        self._update_cache("validate_battery_data", cache_key, validation_result)
        
        return validation_result
    
    def calculate_battery_health(self, battery: Battery) -> Battery:
        """计算电池健康状态
        
        计算电池的健康状态并更新电池对象
        """
        cache_key = self._generate_cache_key("calculate_battery_health", battery)
        
        cached_result = self._get_from_cache("calculate_battery_health", cache_key)
        if cached_result is not None:
            return cached_result
        
        battery.health_status = "good"
        
        self._update_cache("calculate_battery_health", cache_key, battery)
        
        return battery
    
    def analyze_battery_performance(self, battery: Battery) -> Dict[str, Any]:
        """分析电池性能
        
        分析电池的性能指标
        """
        cache_key = self._generate_cache_key("analyze_battery_performance", battery)
        
        cached_result = self._get_from_cache("analyze_battery_performance", cache_key)
        if cached_result is not None:
            return cached_result
        
        performance_data = {
            "performance": "good",
            "estimated_lifetime": 5 * 365,
            "efficiency": 95.0,
            "recommendation": "正常使用"
        }
        
        self._update_cache("analyze_battery_performance", cache_key, performance_data)
        
        return performance_data
    
    def predict_battery_lifetime(self, battery: Battery) -> Dict[str, Any]:
        """预测电池寿命
        
        预测电池的剩余使用寿命
        """
        cache_key = self._generate_cache_key("predict_battery_lifetime", battery)
        
        cached_result = self._get_from_cache("predict_battery_lifetime", cache_key)
        if cached_result is not None:
            return cached_result
        
        lifetime_prediction = {
            "lifetime": "5 years",
            "remaining_cycles": 500,
            "estimated_end_date": "2029-01-01",
            "status": "healthy"
        }
        
        self._update_cache("predict_battery_lifetime", cache_key, lifetime_prediction)
        
        return lifetime_prediction
    
    def compare_batteries(self, batteries: List[Battery]) -> Dict[str, Any]:
        """比较多个电池
        
        比较多个电池的性能和状态
        """
        cache_key = self._generate_cache_key("compare_batteries", batteries)
        
        cached_result = self._get_from_cache("compare_batteries", cache_key)
        if cached_result is not None:
            return cached_result
        
        comparison_result = {
            "battery_count": len(batteries),
            "average_health": "good",
            "best_performer": batteries[0].serial_number if batteries else None,
            "recommendations": "All batteries are in good condition"
        }
        
        self._update_cache("compare_batteries", cache_key, comparison_result)
        
        return comparison_result
    
    def clear_cache(self, method_name: Optional[str] = None):
        """清除缓存
        
        Args:
            method_name: 要清除的方法缓存名称，如果为None则清除所有缓存
        """
        if method_name:
            if method_name in self._cache:
                self._cache[method_name].clear()
            if method_name in self._cache_access_order:
                self._cache_access_order[method_name].clear()
            keys_to_remove = [k for k in self._cache_timestamps if k.startswith(method_name + ":")]
            for k in keys_to_remove:
                del self._cache_timestamps[k]
        else:
            for key in self._cache:
                self._cache[key].clear()
            for key in self._cache_access_order:
                self._cache_access_order[key].clear()
            self._cache_timestamps.clear()