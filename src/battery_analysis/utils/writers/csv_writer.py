"""
CSV输出写入器

处理电池分析结果的CSV文件写入
"""

import csv
import os
import logging

from battery_analysis.utils.writers import csv_utils
from battery_analysis.utils import numeric_utils
from battery_analysis.utils.processors.data_utils import generate_current_type_string
from battery_analysis.utils.writers.statistics_utils import (
    compute_list_cpt, compute_statistics,
)
from battery_analysis import __version__


logger = logging.getLogger(__name__)


class CsvWriter:
    """CSV文件写入器"""

    def __init__(self, strResultPath: str, listTestInfo: list, listBatteryInfo: list) -> None:
        self.strResultPath = strResultPath
        self.listTestInfo = listTestInfo
        self.listBatteryInfo = listBatteryInfo

        # 计算电流/电压等级信息
        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        self.intCurrentLevelNum = len(self.listCurrentLevel)
        self.intVoltageLevelNum = len(self.listVoltageLevel)

        # 计算文件电流类型字符串
        self.strFileCurrentType = generate_current_type_string(self.listCurrentLevel)

        # 电池信息
        self.listBatteryCharge = self.listBatteryInfo[0]
        self.listBatteryName = self.listBatteryInfo[1]
        self.intBatteryNum = len(self.listBatteryName)

        # CSV路径
        safe_temperature = self.listTestInfo[7].replace(':', '_')
        self.strResultCsvPath = (
            f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.csv"
        )

    def write(self, list_cpt=None, stats=None) -> None:
        """写入CSV文件"""
        # init csv writer
        f = open(self.strResultCsvPath, mode='w', newline='', encoding='utf-8')
        csvwriterResultCsvFile = csv.writer(f)

        # CSV写入缓冲区，减少I/O操作
        csv_buffer = []
        csv_buffer_size = 0
        max_csv_buffer_size = 100  # 每次写入100行

        # Write CSV header information
        csv_header_info = [
            f"#BEGIN HEADER",
            f"#PULSE DISCHARGE",
            f"#BATTERY CHARACTERISTICS",
            f"#Start Time: {self.listBatteryInfo[2][0]}",
            f"#End Time: {self.listBatteryInfo[2][1]}",
            f"#Battery Type: {self.listTestInfo[2]} {self.listTestInfo[3]}",
            f"#Battery Manufacturer: {self.listTestInfo[4]}",
            f"#Battery Date Code: {self.listTestInfo[5]}",
            f"#Temperature: {self.listTestInfo[6]}",
            f"#Test Profile: {self.listTestInfo[13]}",
            f"#Version: v{__version__}",
            f"#END HEADER"
        ]
        for info in csv_header_info:
            csv_buffer_size = csv_utils.csv_write(
                info, csvwriterResultCsvFile, csv_buffer, csv_buffer_size, max_csv_buffer_size)

        # Write CSV column headers
        csv_buffer_size = csv_utils.csv_write(
            "", csvwriterResultCsvFile, csv_buffer, csv_buffer_size, max_csv_buffer_size)
        listCsvLine = [""]
        for c in range(self.intCurrentLevelNum):
            listCsvLine.append(f"{self.listCurrentLevel[c]}mA")
            listCsvLine.append("Voltage")
            for v in range(self.intVoltageLevelNum):
                listCsvLine.append("")
        csv_buffer_size = csv_utils.csv_write(
            listCsvLine, csvwriterResultCsvFile, csv_buffer, csv_buffer_size, max_csv_buffer_size)
        listCsvLine = []
        for c in range(self.intCurrentLevelNum):
            listCsvLine.append("")
            listCsvLine.append("")
            for v in range(self.intVoltageLevelNum):
                listCsvLine.append(f"{self.listVoltageLevel[v]}V")
        listCsvLine[0] = "Battery"
        csv_buffer_size = csv_utils.csv_write(
            listCsvLine, csvwriterResultCsvFile, csv_buffer, csv_buffer_size, max_csv_buffer_size)

        # Write analytical battery statistic
        for b in range(self.intBatteryNum):
            listCsvLine = []
            i = 0
            for c in range(self.intCurrentLevelNum):
                listCsvLine.append("")
                listCsvLine.append("")
                for v in range(self.intVoltageLevelNum):
                    listCsvLine.append(self.listBatteryCharge[b][i])
                    i += 1
            listCsvLine[0] = f"{self.listBatteryName[b]}"
            csv_buffer_size = csv_utils.csv_write(
                listCsvLine, csvwriterResultCsvFile, csv_buffer, csv_buffer_size, max_csv_buffer_size)

        # Compute statistics (if not pre-computed)
        if list_cpt is None:
            list_cpt = compute_list_cpt(
            self.listBatteryCharge,
            self.intBatteryNum,
            self.intCurrentLevelNum,
            self.intVoltageLevelNum,
        )
        stats = compute_statistics(
            list_cpt,
            self.intCurrentLevelNum,
            self.intVoltageLevelNum,
        )

        # Write calculated statistic
        listCsvName = ["Mean(μ)", "Median", "Std. Var.(σ)", "μ-3σ",
                       "μ-2σ", "μ+2σ", "μ+3σ", "Minimum", "Maximum"]
        listCsvList = [stats['mean'], stats['med'], stats['std'],
                       stats['mm3s'], stats['mm2s'], stats['mp2s'],
                       stats['mp3s'], stats['min'], stats['max']]
        csv_buffer_size = csv_utils.csv_write(
            "", csvwriterResultCsvFile, csv_buffer, csv_buffer_size, max_csv_buffer_size)
        for n in range(len(listCsvName)):
            listCsvLine = []
            for c in range(self.intCurrentLevelNum):
                listCsvLine.append("")
                listCsvLine.append("")
                for v in range(self.intVoltageLevelNum):
                    listCsvLine.append(round(listCsvList[n][c][v], 5))
            listCsvLine[0] = f"{listCsvName[n]}"
            csv_buffer_size = csv_utils.csv_write(
                listCsvLine, csvwriterResultCsvFile, csv_buffer, csv_buffer_size, max_csv_buffer_size)

        # Flush buffer and close
        if csv_buffer:
            csvwriterResultCsvFile.writerows(csv_buffer)
            csv_buffer.clear()
        f.close()
