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
