"""
测试缓存机制是否正常工作

验证缓存的命中情况和性能提升
"""

import time
from datetime import datetime
from battery_analysis.domain.entities.battery import Battery
from battery_analysis.domain.services.impl.battery_analysis_service_impl import BatteryAnalysisServiceImpl


def test_cache_mechanism():
    """测试缓存机制"""
    print("=== 测试缓存机制 ===")
    
    # 创建电池分析服务实例
    service = BatteryAnalysisServiceImpl()
    
    # 创建测试电池
    battery1 = Battery(
        serial_number="TEST001",
        model_number="ModelA",
        manufacturer="Test Manufacturer",
        production_date=datetime.now(),
        battery_type="Li-ion",
        nominal_voltage=3.7,
        nominal_capacity=2.0,
        max_voltage=4.2,
        min_voltage=2.5,
        max_current=5.0,
        weight=0.1
    )
    
    battery2 = Battery(
        serial_number="TEST002",
        model_number="ModelB",
        manufacturer="Test Manufacturer",
        production_date=datetime.now(),
        battery_type="Li-ion",
        nominal_voltage=3.7,
        nominal_capacity=3.0,
        max_voltage=4.2,
        min_voltage=2.5,
        max_current=5.0,
        weight=0.15
    )
    
    # 测试1: 测试calculate_battery_health方法的缓存
    print("\n1. 测试 calculate_battery_health 方法的缓存")
    
    # 第一次调用（应该计算并缓存）
    start_time = time.time()
    result1_first = service.calculate_battery_health(battery1)
    first_time = time.time() - start_time
    print(f"第一次调用时间: {first_time:.6f}秒")
    print(f"结果: health_status={result1_first.health_status}")
    
    # 第二次调用（应该从缓存获取）
    start_time = time.time()
    result1_second = service.calculate_battery_health(battery1)
    second_time = time.time() - start_time
    print(f"第二次调用时间: {second_time:.6f}秒")
    print(f"结果: health_status={result1_second.health_status}")
    
    # 验证是否是同一个对象
    print(f"是否是同一个对象: {result1_first is result1_second}")
    
    # 测试2: 测试analyze_battery_performance方法的缓存
    print("\n2. 测试 analyze_battery_performance 方法的缓存")
    
    # 第一次调用（应该计算并缓存）
    start_time = time.time()
    perf1_first = service.analyze_battery_performance(battery1)
    first_time = time.time() - start_time
    print(f"第一次调用时间: {first_time:.6f}秒")
    print(f"结果: {perf1_first}")
    
    # 第二次调用（应该从缓存获取）
    start_time = time.time()
    perf1_second = service.analyze_battery_performance(battery1)
    second_time = time.time() - start_time
    print(f"第二次调用时间: {second_time:.6f}秒")
    print(f"结果: {perf1_second}")
    
    # 验证结果是否相同
    print(f"结果是否相同: {perf1_first == perf1_second}")
    
    # 测试3: 测试不同电池的缓存
    print("\n3. 测试不同电池的缓存")
    
    # 调用第一个电池
    start_time = time.time()
    perf1 = service.analyze_battery_performance(battery1)
    time1 = time.time() - start_time
    print(f"电池1调用时间: {time1:.6f}秒")
    
    # 调用第二个电池
    start_time = time.time()
    perf2 = service.analyze_battery_performance(battery2)
    time2 = time.time() - start_time
    print(f"电池2调用时间: {time2:.6f}秒")
    
    # 再次调用第一个电池（应该从缓存获取）
    start_time = time.time()
    perf1_again = service.analyze_battery_performance(battery1)
    time1_again = time.time() - start_time
    print(f"电池1再次调用时间: {time1_again:.6f}秒")
    
    # 测试4: 测试缓存清除功能
    print("\n4. 测试缓存清除功能")
    
    # 清除特定方法的缓存
    print("清除 analyze_battery_performance 方法的缓存")
    service.clear_cache("analyze_battery_performance")
    
    # 再次调用（应该重新计算）
    start_time = time.time()
    perf1_after_clear = service.analyze_battery_performance(battery1)
    time_after_clear = time.time() - start_time
    print(f"清除缓存后调用时间: {time_after_clear:.6f}秒")
    
    # 测试5: 测试compare_batteries方法的缓存
    print("\n5. 测试 compare_batteries 方法的缓存")
    
    # 第一次调用（应该计算并缓存）
    start_time = time.time()
    compare_result_first = service.compare_batteries([battery1, battery2])
    first_time = time.time() - start_time
    print(f"第一次调用时间: {first_time:.6f}秒")
    print(f"结果: {compare_result_first}")
    
    # 第二次调用（应该从缓存获取）
    start_time = time.time()
    compare_result_second = service.compare_batteries([battery1, battery2])
    second_time = time.time() - start_time
    print(f"第二次调用时间: {second_time:.6f}秒")
    print(f"结果: {compare_result_second}")
    
    # 验证结果是否相同
    print(f"结果是否相同: {compare_result_first == compare_result_second}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_cache_mechanism()
