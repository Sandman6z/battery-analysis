def filter_data(
    plt_charge_list: list, 
    plt_voltage_list: list, 
    times=5, 
    slope_max=0.2, 
    difference_max=0.05
):
    """
    优化后的数据过滤函数，使用numpy进行向量运算，降低时间复杂度
    """
    plt_charge_filtered = []
    plt_voltage_filtered = []
    
    # 尝试导入numpy，若不可用则使用原算法
    try:
        import numpy as np
        
        for charge_data, voltage_data in zip(plt_charge_list, plt_voltage_list):
            # 直接转换为numpy数组，避免重复转换
            charge_np = np.asarray(charge_data)
            voltage_np = np.asarray(voltage_data)
            
            # 计算差值
            charge_diff = np.diff(charge_np)
            voltage_diff = np.diff(voltage_np)
            
            # 计算斜率，使用更高效的方式
            with np.errstate(divide='ignore', invalid='ignore'):
                # 使用numpy的where函数高效处理除数为0的情况
                slopes = np.abs(np.where(charge_diff != 0, voltage_diff / charge_diff, slope_max))
            
            # 计算电压差值绝对值
            voltage_diff_abs = np.abs(voltage_diff)
            
            # 生成过滤掩码，合并条件
            mask = (slopes < slope_max) & (voltage_diff_abs < difference_max)
            
            # 确保第一个点总是保留，使用更高效的掩码生成方式
            filtered_mask = np.zeros(len(charge_np), dtype=bool)
            filtered_mask[0] = True
            filtered_mask[1:] = mask
            
            # 应用过滤，直接获取结果
            plt_charge_filtered.append(charge_np[filtered_mask].tolist())
            plt_voltage_filtered.append(voltage_np[filtered_mask].tolist())
    except ImportError:
        # 若numpy不可用，使用优化后的原算法
        for charge_data, voltage_data in zip(plt_charge_list, plt_voltage_list):
            # 使用列表推导式和生成器表达式优化
            filtered_charge = [charge_data[0]]
            filtered_voltage = [voltage_data[0]]
            
            # 使用zip和enumerate优化循环
            for i in range(1, len(charge_data)):
                prev_charge, curr_charge = charge_data[i-1], charge_data[i]
                prev_voltage, curr_voltage = voltage_data[i-1], voltage_data[i]
                
                charge_diff = curr_charge - prev_charge
                voltage_diff = curr_voltage - prev_voltage
                
                if charge_diff == 0:
                    slope = slope_max
                else:
                    slope = abs(voltage_diff / charge_diff)
                
                voltage_diff_abs = abs(voltage_diff)
                
                # 只保留符合条件的点
                if slope < slope_max and voltage_diff_abs < difference_max:
                    filtered_charge.append(curr_charge)
                    filtered_voltage.append(curr_voltage)
            
            plt_charge_filtered.append(filtered_charge)
            plt_voltage_filtered.append(filtered_voltage)
    
    return plt_charge_filtered, plt_voltage_filtered


def generate_current_type_string(list_current_level: list) -> str:
    """
    生成电流类型字符串，将电流水平列表用"-"连接
    
    Args:
        list_current_level: 电流水平列表
        
    Returns:
        连接后的电流类型字符串
    """
    if not list_current_level:
        return ""
    return "-".join(str(level) for level in list_current_level)


def detect_outliers(data: list, data_name: str, result_index: int, test_results: list, precomputed_stats=None) -> list:
    """
    检测数据中的异常值，使用3σ原则
    
    Args:
        data: 数据列表
        data_name: 数据名称
        result_index: 当前结果索引
        test_results: 测试结果列表
        precomputed_stats: 预计算的统计量，格式为 (avg, std_dev)
        
    Returns:
        异常值列表
    """
    anomalies = []
    if not data:
        return anomalies
    
    # 使用预计算的统计量或计算新的
    if precomputed_stats:
        avg, std_dev = precomputed_stats
    else:
        avg = sum(data) / len(data)
        std_dev = (sum((x - avg) ** 2 for x in data) / len(data)) ** 0.5
    
    # 检查当前结果是否为异常值
    current_value = data[result_index]
    if abs(current_value - avg) > 3 * std_dev:
        anomalies.append({
            "test_id": test_results[result_index].test_id,
            "cycle_count": test_results[result_index].cycle_count,
            "parameter": data_name,
            "value": current_value,
            "expected_range": [round(avg - 3 * std_dev, 2), round(avg + 3 * std_dev, 2)],
            "type": "outlier"
        })
    
    return anomalies
