def filter_data(
    plt_charge_list: list, 
    plt_voltage_list: list, 
    times=5, 
    slope_max=0.2, 
    difference_max=0.05
):
    plt_charge_filtered = []
    plt_voltage_filtered = []
    for p in range(len(plt_charge_list)):
        plt_charge_single = plt_charge_list[p]
        plt_voltage_single = plt_voltage_list[p]
        current_times = times
        while current_times:
            plt_charge_single_temp = [plt_charge_single[0]]
            plt_voltage_single_temp = [plt_voltage_single[0]]
            for c in range(1, len(plt_charge_single)):
                if (plt_charge_single[c] - plt_charge_single[c - 1]) == 0:
                    slope = slope_max
                else:
                    slope = abs((plt_voltage_single[c] - plt_voltage_single[c - 1]) / (
                        plt_charge_single[c] - plt_charge_single[c - 1]))
                if slope >= slope_max:
                    pass
                else:
                    if abs(plt_voltage_single[c] - 
                           plt_voltage_single[c - 1]) >= difference_max:
                        pass
                    else:
                        plt_charge_single_temp.append(
                            plt_charge_single[c])
                        plt_voltage_single_temp.append(
                            plt_voltage_single[c])
            plt_charge_single = plt_charge_single_temp
            plt_voltage_single = plt_voltage_single_temp
            current_times -= 1
        plt_charge_filtered.append(plt_charge_single)
        plt_voltage_filtered.append(plt_voltage_single)
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


def detect_outliers(data: list, data_name: str, result_index: int, test_results: list) -> list:
    """
    检测数据中的异常值，使用3σ原则
    
    Args:
        data: 数据列表
        data_name: 数据名称
        result_index: 当前结果索引
        test_results: 测试结果列表
        
    Returns:
        异常值列表
    """
    anomalies = []
    if not data:
        return anomalies
    
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
