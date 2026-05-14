"""脉冲电流/电压等级匹配逻辑"""

from typing import List, Tuple, Optional


def b_is_in_range(current: float, standard: float) -> bool:
    """检查电流是否在标准值的 ±5% 范围内"""
    return abs(current - standard) <= abs(standard * 0.05)


def _init_level_structures(
    listCurrentLevel: list,
    listVoltageLevel: list,
) -> Tuple[list, list, list, list, list]:
    """初始化等级匹配所需的嵌套列表结构"""
    listLevelToVoltage = []
    listLevelToRow = []
    listLevelToCharge = []
    listPosiForInfoImageCsv = []
    listVoltageForInfoImageCsv = []

    for c_idx in range(len(listCurrentLevel)):
        listLevelToVoltage.append([])
        listLevelToRow.append([])
        listLevelToCharge.append([])
        listPosiForInfoImageCsv.append([])
        listVoltageForInfoImageCsv.append([])
        for v_idx in range(len(listVoltageLevel)):
            listLevelToVoltage[c_idx].append(listVoltageLevel[v_idx])
            listLevelToRow[c_idx].append(0)
            listLevelToCharge[c_idx].append(0)

    return (
        listLevelToVoltage,
        listLevelToRow,
        listLevelToCharge,
        listPosiForInfoImageCsv,
        listVoltageForInfoImageCsv,
    )


def match_pulse_levels(
    record_current: List[float],
    record_voltage: List[float],
    pulse_mask: List[bool],
    listCurrentLevel: list,
    listVoltageLevel: list,
    start_row: int = 2,
) -> Optional[Tuple[list, list, list, list]]:
    """将脉冲行匹配到电流/电压等级

    遍历脉冲数据行，对每个脉冲行匹配对应的电流等级和电压等级，
    返回用于后续电荷计算和绘图的四组数据结构。

    Args:
        record_current: 电流数据列表（单位 A，函数内部转为 mA 比较）
        record_voltage: 电压数据列表（单位 V）
        pulse_mask: 布尔列表，标记哪些行是脉冲行
        listCurrentLevel: 电流等级列表（单位 mA）
        listVoltageLevel: 电压等级列表（单位 V）
        start_row: 有效数据起始行索引

    Returns:
        (listLevelToVoltage, listLevelToRow, listPosiForInfoImageCsv, listVoltageForInfoImageCsv)
        如果无脉冲数据返回 None
    """
    structures = _init_level_structures(listCurrentLevel, listVoltageLevel)
    listLevelToVoltage, listLevelToRow, _, listPosiForInfoImageCsv, listVoltageForInfoImageCsv = structures

    neg_current_levels = [-float(level) for level in listCurrentLevel]
    data_len = len(record_current)
    has_pulse = False

    for row in range(start_row, data_len):
        if row >= len(pulse_mask) or not pulse_mask[row]:
            continue
        has_pulse = True

        current_ma = float(record_current[row]) * 1000
        voltage = float(record_voltage[row])

        for c_idx, neg_level in enumerate(neg_current_levels):
            if not b_is_in_range(current_ma, neg_level):
                continue

            # 检查是否是脉冲结束点
            is_endpoint = True
            if row + 1 < data_len:
                next_current = float(record_current[row + 1]) * 1000
                if b_is_in_range(next_current, neg_level):
                    is_endpoint = False

            if is_endpoint:
                listPosiForInfoImageCsv[c_idx].append(row)
                listVoltageForInfoImageCsv[c_idx].append(voltage)

            # 匹配电压等级
            for v_idx, v_level in enumerate(listVoltageLevel):
                if voltage <= v_level and listLevelToRow[c_idx][v_idx] == 0:
                    listLevelToVoltage[c_idx][v_idx] = voltage
                    listLevelToRow[c_idx][v_idx] = row

    if not has_pulse:
        return None

    return (
        listLevelToVoltage,
        listLevelToRow,
        listPosiForInfoImageCsv,
        listVoltageForInfoImageCsv,
    )
