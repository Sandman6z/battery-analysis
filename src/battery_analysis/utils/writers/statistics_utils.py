"""
统计计算工具

提供电池容量数据的统计计算函数
"""

import numpy as np

from battery_analysis.utils import numeric_utils


def compute_list_cpt(listBatteryCharge, intBatteryNum, intCurrentLevelNum, intVoltageLevelNum):
    """从电池充电数据计算容量列表，用于后续统计计算"""
    listCpt = [[[] for _ in range(intVoltageLevelNum)] for _ in range(intCurrentLevelNum)]
    arr = np.asarray(listBatteryCharge, dtype=object)

    if arr.ndim == 2:
        # 批量非零收集（object 数组保持 None/str 的 Python 比较语义）
        i = 0
        for c in range(intCurrentLevelNum):
            for v in range(intVoltageLevelNum):
                col = arr[:, i]
                listCpt[c][v] = col[col != 0].tolist()
                i += 1
    else:
        # 行不等长：回退逐元素收集（与原始实现语义一致）
        for b in range(intBatteryNum):
            i = 0
            for c in range(intCurrentLevelNum):
                for v in range(intVoltageLevelNum):
                    if listBatteryCharge[b][i] != 0:
                        listCpt[c][v].append(listBatteryCharge[b][i])
                    i += 1
    return listCpt


def compute_statistics(listCpt, intCurrentLevelNum, intVoltageLevelNum):
    """从容量数据批量计算统计值（pad + np.nan* 2D 归约）"""
    flat_cells = []
    for c in range(intCurrentLevelNum):
        for v in range(intVoltageLevelNum):
            flat_cells.append(listCpt[c][v])

    n_cells = len(flat_cells)
    max_len = max((len(cell) for cell in flat_cells), default=0)

    if max_len == 0:
        zero = [[0.0 for _ in range(intVoltageLevelNum)] for _ in range(intCurrentLevelNum)]
        return {
            'mean': zero, 'med': zero, 'std': zero,
            'mm3s': zero, 'mm2s': zero, 'mp2s': zero, 'mp3s': zero,
            'min': zero, 'max': zero,
        }

    padded = np.full((n_cells, max_len), np.nan, dtype=float)
    counts = np.zeros(n_cells, dtype=np.int64)
    for i, cell in enumerate(flat_cells):
        vals = np.asarray(cell, dtype=float)
        k = vals.size
        if k > 0:
            padded[i, :k] = vals
            counts[i] = k

    with np.errstate(invalid='ignore', divide='ignore'):
        means = np.nanmean(padded, axis=1)
        meds = np.nanmedian(padded, axis=1)
        stds = np.nanstd(padded, axis=1, ddof=1)
        mins = np.nanmin(padded, axis=1)
        maxs = np.nanmax(padded, axis=1)

    # 对齐 numeric_utils 语义：空 cell → 0.0；样本<=1 的 std → 0.0
    means = np.where(counts > 0, means, 0.0)
    meds = np.where(counts > 0, meds, 0.0)
    stds = np.where(counts > 1, stds, 0.0)
    mins = np.where(counts > 0, mins, 0.0)
    maxs = np.where(counts > 0, maxs, 0.0)

    mm3s = means - 3 * stds
    mm2s = means - 2 * stds
    mp2s = means + 2 * stds
    mp3s = means + 3 * stds

    def to_nested(arr1d):
        return arr1d.reshape(intCurrentLevelNum, intVoltageLevelNum).tolist()

    return {
        'mean': to_nested(means),
        'med': to_nested(meds),
        'std': to_nested(stds),
        'mm3s': to_nested(mm3s),
        'mm2s': to_nested(mm2s),
        'mp2s': to_nested(mp2s),
        'mp3s': to_nested(mp3s),
        'min': to_nested(mins),
        'max': to_nested(maxs),
    }
