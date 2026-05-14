"""Info_Image.csv 和 Info_Plot.json 写入器"""

import csv
import json
import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)


def write_info_csv(
    result_path: str,
    list_battery_name: List[str],
    list_current_level: list,
    list_all_posi: List[List[List[int]]],
    list_all_charge: List[List[list]],
    list_all_voltage: List[List[list]],
) -> None:
    """写入 Info_Image.csv（供 BatteryChartViewer 绘制图表）

    格式：
        BATTERY, battery_name
        posi_row_1, posi_row_2, ...
        charge_1, charge_2, ...
        voltage_1, voltage_2, ...
        BATTERY, battery_name
        ...

    Args:
        result_path: 输出目录路径
        list_battery_name: 电池名称列表
        list_current_level: 电流等级列表
        list_all_posi: [b][c] = 位置列表
        list_all_charge: [b][c] = 电荷列表
        list_all_voltage: [b][c] = 电压列表
    """
    file_path = os.path.join(result_path, "Info_Image.csv")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    csv_data = []
    for b, battery_name in enumerate(list_battery_name):
        csv_data.append(["BATTERY", battery_name])
        for c in range(len(list_current_level)):
            csv_data.append(list_all_posi[b][c])
            csv_data.append(list_all_charge[b][c])
            csv_data.append(list_all_voltage[b][c])

    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)


def write_info_json(
    result_path: str,
    list_test_info: list,
    manufacturer: str = "",
    spec_type: str = "",
    spec_method: str = "",
    batch_code: str = "",
    capacity: str = "",
    temperature: str = "",
    current_levels: Optional[list] = None,
) -> None:
    """写入 Info_Plot.json（供 BatteryChartViewer 读取动态标题）

    Args:
        result_path: 输出目录路径
        list_test_info: 完整测试信息列表（备用数据源）
        manufacturer: 制造商（优先使用，为空时从 list_test_info 提取）
        spec_type: 规格类型
        spec_method: 规格方法
        batch_code: 批次编号
        capacity: 容量
        temperature: 温度
        current_levels: 电流等级列表
    """
    file_path = os.path.join(result_path, "Info_Plot.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    meta_data = {
        "manufacturer": manufacturer or (list_test_info[4] if len(list_test_info) > 4 else ""),
        "spec_type": spec_type or (list_test_info[2] if len(list_test_info) > 2 else ""),
        "spec_method": spec_method or (list_test_info[3] if len(list_test_info) > 3 else ""),
        "batch_code": batch_code or (list_test_info[5] if len(list_test_info) > 5 else ""),
        "capacity": capacity or (list_test_info[8] if len(list_test_info) > 8 else ""),
        "temperature": temperature or (list_test_info[7] if len(list_test_info) > 7 else ""),
        "current_levels": current_levels or (list_test_info[14] if len(list_test_info) > 14 else []),
    }

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=2)
