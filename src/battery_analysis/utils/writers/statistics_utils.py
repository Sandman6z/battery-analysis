"""
统计计算工具

提供电池容量数据的统计计算函数
"""

from battery_analysis.utils import numeric_utils


def compute_list_cpt(listBatteryCharge, intBatteryNum, intCurrentLevelNum, intVoltageLevelNum):
    """从电池充电数据计算容量列表，用于后续统计计算"""
    listCpt = []
    for c in range(intCurrentLevelNum):
        listCpt.append([])
        for _ in range(intVoltageLevelNum):
            listCpt[c].append([])
    for b in range(intBatteryNum):
        i = 0
        for c in range(intCurrentLevelNum):
            for v in range(intVoltageLevelNum):
                if listBatteryCharge[b][i] != 0:
                    listCpt[c][v].append(listBatteryCharge[b][i])
                i += 1
    return listCpt


def compute_statistics(listCpt, intCurrentLevelNum, intVoltageLevelNum):
    """从容量数据计算统计值（均值、中位数、标准差等）"""
    listMean = []
    listStd = []
    listMax = []
    listMin = []
    listMed = []
    listMM3S = []
    listMM2S = []
    listMP2S = []
    listMP3S = []

    for c in range(intCurrentLevelNum):
        listMean.append([])
        listMed.append([])
        listStd.append([])
        listMM3S.append([])
        listMM2S.append([])
        listMP2S.append([])
        listMP3S.append([])
        listMin.append([])
        listMax.append([])

    for c in range(intCurrentLevelNum):
        for v in range(intVoltageLevelNum):
            listMean[c].append(numeric_utils.np_mean(listCpt[c][v]))
            listMed[c].append(numeric_utils.np_med(listCpt[c][v]))
            listStd[c].append(numeric_utils.np_std(listCpt[c][v]))
            listMM3S[c].append(listMean[c][v] - 3 * listStd[c][v])
            listMM2S[c].append(listMean[c][v] - 2 * listStd[c][v])
            listMP2S[c].append(listMean[c][v] + 2 * listStd[c][v])
            listMP3S[c].append(listMean[c][v] + 3 * listStd[c][v])
            listMin[c].append(numeric_utils.np_min(listCpt[c][v]))
            listMax[c].append(numeric_utils.np_max(listCpt[c][v]))

    return {
        'mean': listMean,
        'med': listMed,
        'std': listStd,
        'mm3s': listMM3S,
        'mm2s': listMM2S,
        'mp2s': listMP2S,
        'mp3s': listMP3S,
        'min': listMin,
        'max': listMax,
    }
