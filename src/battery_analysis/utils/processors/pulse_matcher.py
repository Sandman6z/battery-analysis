"""脉冲电流/电压等级匹配逻辑"""
from typing import List, Optional, Tuple

import numpy as np


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
    """将脉冲行匹配到电流/电压等级（numpy 广播向量化）

    对每个电流等级一次性广播比较整个电流数组，替代逐行三重嵌套循环。
    返回结构与原实现完全一致：(listLevelToVoltage, listLevelToRow,
    listPosiForInfoImageCsv, listVoltageForInfoImageCsv)；无脉冲数据返回 None。

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

    cur_ma = np.asarray(record_current, dtype=float) * 1000.0
    voltage = np.asarray(record_voltage, dtype=float)
    data_len = len(cur_ma)
    if data_len == 0:
        return None

    # pulse_mask 可能与 record 不等长（原代码 row >= len(pulse_mask) 保护尾部）
    mask = np.zeros(data_len, dtype=bool)
    pm = np.asarray(pulse_mask, dtype=bool)
    common = min(data_len, pm.size)
    mask[:common] = pm[:common]

    valid_row = np.zeros(data_len, dtype=bool)
    valid_row[max(start_row, 0):] = True
    valid_row &= mask

    if not valid_row.any():
        return None

    neg_levels = [-float(level) for level in listCurrentLevel]
    voltage_levels = [float(v) for v in listVoltageLevel]

    for c_idx, neg_level in enumerate(neg_levels):
        tolerance = abs(neg_level * 0.05)
        in_range = np.abs(cur_ma - neg_level) <= tolerance
        matched_row = valid_row & in_range

        # ── 脉冲结束点：当前行匹配、下一行不在范围内（末尾行视为端点）──
        next_in_range = np.empty(data_len, dtype=bool)
        next_in_range[:-1] = in_range[1:]
        next_in_range[-1] = False
        is_endpoint = matched_row & ~next_in_range
        endpoint_rows = np.nonzero(is_endpoint)[0]
        if endpoint_rows.size > 0:
            listPosiForInfoImageCsv[c_idx].extend(int(r) for r in endpoint_rows)
            listVoltageForInfoImageCsv[c_idx].extend(float(voltage[r]) for r in endpoint_rows)

        # ── 电压等级匹配：每 (c,v) 首个满足 voltage <= v_level 的匹配行 ──
        for v_idx, v_level in enumerate(voltage_levels):
            satisfies = matched_row & (voltage <= v_level)
            if satisfies.any():
                first_idx = int(np.argmax(satisfies))
                listLevelToVoltage[c_idx][v_idx] = float(voltage[first_idx])
                listLevelToRow[c_idx][v_idx] = first_idx

    return (
        listLevelToVoltage,
        listLevelToRow,
        listPosiForInfoImageCsv,
        listVoltageForInfoImageCsv,
    )
