"""
Excel报告写入器

处理电池分析结果的Excel（xlsx）文件写入，包括主结果表和样本表。
"""

import os
import math
import logging
from pathlib import Path

import xlsxwriter as xwt

from battery_analysis.utils import excel_utils
from battery_analysis.utils import numeric_utils
from battery_analysis.utils.exception_type import BatteryAnalysisException
from battery_analysis import __version__


logger = logging.getLogger(__name__)


def _compute_list_cpt(listBatteryCharge, intBatteryNum, intCurrentLevelNum, intVoltageLevelNum):
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


def _compute_statistics(listCpt, intCurrentLevelNum, intVoltageLevelNum):
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


class ExcelReportWriter:
    """Excel报告写入器，处理所有xlsx格式的输出"""

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
        self.strFileCurrentType = ""
        for c in range(self.intCurrentLevelNum):
            self.strFileCurrentType += f"{self.listCurrentLevel[c]}-"
        self.strFileCurrentType = self.strFileCurrentType[:-1]

        # 电池信息
        self.listBatteryCharge = self.listBatteryInfo[0]
        self.listBatteryName = self.listBatteryInfo[1]
        self.intBatteryNum = len(self.listBatteryName)

        # 图像路径列表（用于插入到Excel）
        self.listPngPath = []
        for b in range(self.intCurrentLevelNum):
            self.listPngPath.append(
                (f"{self.strResultPath}/Image_UseableCapacityOver"
                 f"CutoffVoltage{self.listCurrentLevel[b]}mALoad.png"))

        # Excel文件路径
        safe_temperature = self.listTestInfo[7].replace(':', '_')
        self.strResultXlsxPath = (
            f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.xlsx"
        )
        self.strSampleXlsxPath = (
            f"{self.strResultPath}/Sample_{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.xlsx"
        )

        # 计算Word报告路径（用于样本表中的相对路径链接）
        # 从strResultPath提取td（日期部分）
        basename = os.path.basename(strResultPath)
        if "_v" in basename:
            td = basename.split("_v")[0]
        else:
            td = "00000000"
        report_name = (
            f"{self.listTestInfo[4]}_{self.listTestInfo[2]}_DC{self.listTestInfo[5]}"
            f"_TD{td}_v{self.listTestInfo[16]}.docx"
        )
        result_dir = Path(self.strResultPath).parent
        self.strReportWordPath = str(result_dir / report_name)

        # init variables for plt (部分，仅boxplot titles用于excel)
        self.listPltColorType = ['#DF7040', '#0675BE', '#EDB120',
                                 '#7E2F8E', '#32CD32', '#FF4500', '#000000', '#000000']
        self.listColorName = ["red = ", "blue = ", "yellow = ",
                              "violet = ", "green = ", "orange = ", "black1 = ", "black2 = "]

    def write(self) -> None:
        """执行Excel报告写入"""
        # ── 创建工作簿和工作表 ──
        wbResult = xwt.Workbook(self.strResultXlsxPath)
        wsOverview = wbResult.add_worksheet("overview")
        wsOverviewStatisticalStartLine = 13
        wsResult = wbResult.add_worksheet("result")
        wbSample = xwt.Workbook(self.strSampleXlsxPath)
        wsWord = wbSample.add_worksheet("word")
        wsExcel = wbSample.add_worksheet("excel")

        # ── 格式定义 ──
        wsResultData = wbResult.add_format({
            'font_name': 'Microsoft YaHei',
            'font_size': 9,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter'
        })
        wsResultData_italic = wbResult.add_format({
            'font_name': 'Microsoft YaHei',
            'font_size': 9,
            'font_color': 'black',
            'italic': True,
            'bold': False,
            'align': 'center',
            'valign': 'vcenter'
        })
        wsOverviewStatistics = wbResult.add_format({
            'font_name': 'Arial Narrow',
            'font_size': 9,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': '#BFBFBF'
        })
        wsOverviewStatistics_bgdarkgray = wbResult.add_format({
            'font_name': 'Arial Narrow',
            'font_size': 12,
            'font_color': 'black',
            'bg_color': '#BFBFBF',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#BFBFBF'
        })
        wsOverviewStatistics_bglightgray = wbResult.add_format({
            'font_name': 'Arial Narrow',
            'font_size': 12,
            'font_color': 'black',
            'bg_color': '#F2F2F2',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#BFBFBF'
        })
        wsOverviewStatistics_bglightgray_blod = wbResult.add_format({
            'font_name': 'Arial Narrow',
            'font_size': 12,
            'font_color': 'black',
            'bg_color': '#F2F2F2',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#BFBFBF'
        })
        wsExcelLine = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': 'black'
        })
        wsExcelData = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })
        wsExcelData_bold = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })
        wsExcelData_percentage = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'num_format': '0%',
            'border': 1,
            'border_color': 'black'
        })
        wsExcelData_percentage_bold = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'num_format': '0%',
            'border': 1,
            'border_color': 'black',
        })
        wsExcelData_bgyellow = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black',
            'bg_color': '#FFFF00'
        })
        wsWordLine = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': 'black'
        })
        wsWordData = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })
        wsWordData_bold = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })
        wsWordData_percentage = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black',
            'num_format': '0%'
        })
        wsWordData_percentage_bold = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black',
            'num_format': '0%'
        })
        wsWordData_bgyellow = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black',
            'bg_color': '#FFFF00'
        })
        wbSampleHyperlink = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': '#0000FF',
            'underline': True,
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })

        # ── 写入Overview表头和结果表列名 ──
        if wsOverview is None:
            raise BatteryAnalysisException(
                f"{self.strResultXlsxPath} sheet[overview] creation failed")
        # Write header information
        header_info = [
            f"#BEGIN HEADER",
            f"#PULSE DISCHARGE",
            f"#BATTERY CHARACTERISTICS",
            f"#Start Time: {self.listBatteryInfo[2][0]}",
            f"#Start Time: {self.listBatteryInfo[2][1]}",
            f"#Battery Type: {self.listTestInfo[2]} {self.listTestInfo[3]}",
            f"#Battery Manufacturer: {self.listTestInfo[4]}",
            f"#Battery Date Code: {self.listTestInfo[5]}",
            f"#Temperature: {self.listTestInfo[6]}",
            f"#Test Profile: {self.listTestInfo[13]}",
            f"#Version: v{__version__}",
            f"#END HEADER"
        ]
        for i, info in enumerate(header_info):
            wsOverview.write(i, 0, info)

        if wsResult is None:
            raise BatteryAnalysisException(
                f"{self.strResultXlsxPath} sheet[result] creation failed")
        excel_utils.ws_set_col(
            wsResult, 0, self.intCurrentLevelNum * (2 + self.intVoltageLevelNum) + 1, 10)
        excel_utils.ws_set_col(wsResult, 0, 1, 20)
        wsResult.write(2, 0, "Battery", wsResultData)
        wsResult.write(4 + self.intBatteryNum, 0,
                       "Mean(μ)", wsResultData_italic)
        wsResult.write(5 + self.intBatteryNum, 0,
                       "Median", wsResultData_italic)
        wsResult.write(6 + self.intBatteryNum, 0,
                       "Std. Var.(σ)", wsResultData_italic)
        wsResult.write(7 + self.intBatteryNum, 0,
                       "μ-3σ", wsResultData_italic)
        wsResult.write(8 + self.intBatteryNum, 0,
                       "μ-2σ", wsResultData_italic)
        wsResult.write(9 + self.intBatteryNum, 0,
                       "μ+2σ", wsResultData_italic)
        wsResult.write(10 + self.intBatteryNum, 0,
                       "μ+3σ", wsResultData_italic)
        wsResult.write(11 + self.intBatteryNum, 0,
                       "Minimum", wsResultData_italic)
        wsResult.write(12 + self.intBatteryNum, 0,
                       "Maximum", wsResultData_italic)
        for c in range(self.intCurrentLevelNum):
            wsResult.write(1, 1 + c * (2 + self.intVoltageLevelNum),
                           f"{self.listCurrentLevel[c]}mA", wsResultData)
            wsResult.merge_range(1, 2 + c * (2 + self.intVoltageLevelNum), 1, (c + 1) * (
                2 + self.intVoltageLevelNum) - 1, "Voltage", wsResultData)
            for v in range(self.intVoltageLevelNum):
                wsResult.write(2, 2 + c * (2 + self.intVoltageLevelNum) + v,
                               f"{self.listVoltageLevel[v]}V", wsResultData)

        # ── 写入电池数据 ──
        for b in range(self.intBatteryNum):
            excel_utils.ws_result_write_data(
                3 + b, 0, self.listBatteryName[b], wsResultData, wsResult)
            i = 0
            for c in range(self.intCurrentLevelNum):
                for v in range(self.intVoltageLevelNum):
                    excel_utils.ws_result_write_data(
                        3 + b,
                        2 + c * (2 + self.intVoltageLevelNum) + v,
                        self.listBatteryCharge[b][i],
                        wsResultData,
                        wsResult)
                    i += 1

        # ── 计算统计值 ──
        listCpt = _compute_list_cpt(
            self.listBatteryCharge,
            self.intBatteryNum,
            self.intCurrentLevelNum,
            self.intVoltageLevelNum,
        )
        stats = _compute_statistics(
            listCpt,
            self.intCurrentLevelNum,
            self.intVoltageLevelNum,
        )
        listMean = stats['mean']
        listMed = stats['med']
        listStd = stats['std']
        listMM3S = stats['mm3s']
        listMM2S = stats['mm2s']
        listMP2S = stats['mp2s']
        listMP3S = stats['mp3s']
        listMin = stats['min']
        listMax = stats['max']

        # ── 写入统计值到结果表 ──
        for c in range(self.intCurrentLevelNum):
            for v in range(self.intVoltageLevelNum):
                excel_utils.ws_result_write_data(
                    4 + self.intBatteryNum,
                    2 + c * (2 + self.intVoltageLevelNum) + v,
                    round(listMean[c][v], 5),
                    wsResultData,
                    wsResult)
                excel_utils.ws_result_write_data(
                    5 + self.intBatteryNum,
                    2 + c * (2 + self.intVoltageLevelNum) + v,
                    round(listMed[c][v], 5),
                    wsResultData,
                    wsResult)
                excel_utils.ws_result_write_data(
                    6 + self.intBatteryNum,
                    2 + c * (2 + self.intVoltageLevelNum) + v,
                    round(listStd[c][v], 5),
                    wsResultData,
                    wsResult)
                excel_utils.ws_result_write_data(
                    7 + self.intBatteryNum,
                    2 + c * (2 + self.intVoltageLevelNum) + v,
                    round(listMM3S[c][v], 5),
                    wsResultData,
                    wsResult)
                excel_utils.ws_result_write_data(
                    8 + self.intBatteryNum,
                    2 + c * (2 + self.intVoltageLevelNum) + v,
                    round(listMM2S[c][v], 5),
                    wsResultData,
                    wsResult)
                excel_utils.ws_result_write_data(
                    9 + self.intBatteryNum,
                    2 + c * (2 + self.intVoltageLevelNum) + v,
                    round(listMP2S[c][v], 5),
                    wsResultData,
                    wsResult)
                excel_utils.ws_result_write_data(
                    10 + self.intBatteryNum,
                    2 + c * (2 + self.intVoltageLevelNum) + v,
                    round(listMP3S[c][v], 5),
                    wsResultData,
                    wsResult)
                excel_utils.ws_result_write_data(
                    11 + self.intBatteryNum,
                    2 + c * (2 + self.intVoltageLevelNum) + v,
                    round(listMin[c][v], 5),
                    wsResultData,
                    wsResult)
                excel_utils.ws_result_write_data(
                    12 + self.intBatteryNum,
                    2 + c * (2 + self.intVoltageLevelNum) + v,
                    round(listMax[c][v], 5),
                    wsResultData,
                    wsResult)

        # ── 插入图像 ──
        for c in range(self.intCurrentLevelNum):
            wsResult.insert_image(
                14 + self.intBatteryNum,
                1 + c * (2 + self.intVoltageLevelNum),
                self.listPngPath[c],
                {
                    'x_scale': ((2 + self.intVoltageLevelNum) * 2 - 1) / 16,
                    'y_scale': ((2 + self.intVoltageLevelNum) * 2 - 1) / 16
                }
            )

        # ── 写入wsOverview统计表 ──
        wsOverview.write(wsOverviewStatisticalStartLine, 0,
                         "Statisticals Results", wsOverviewStatistics_bgdarkgray)
        wsOverview.set_row(wsOverviewStatisticalStartLine, 20)
        wsOverview.set_column(0, 0, 18)
        for v in range(1, self.intVoltageLevelNum + 1):
            wsOverview.set_column(v, v, 18)
            wsOverview.write_rich_string(
                wsOverviewStatisticalStartLine, v,
                wsOverviewStatistics_bglightgray, "Cut-off Voltage ",
                wsOverviewStatistics_bglightgray_blod,
                f"{self.listVoltageLevel[v - 1]}V",
                wsOverviewStatistics_bglightgray
            )
        for c in range(1, self.intCurrentLevelNum + 1):
            wsOverview.set_row(wsOverviewStatisticalStartLine + c, 120)
            wsOverview.write_rich_string(
                wsOverviewStatisticalStartLine + c, 0,
                wsOverviewStatistics_bglightgray, "Pulse Current ",
                wsOverviewStatistics_bglightgray_blod,
                f"{self.listCurrentLevel[c - 1]}mA",
                wsOverviewStatistics_bglightgray
            )
            for v in range(1, self.intVoltageLevelNum + 1):
                wsOverview.write(
                    wsOverviewStatisticalStartLine + c, v,
                    (f"μ: {round(listMean[c - 1][v - 1])}mAh\n"
                     f"Median: {round(listMed[c - 1][v - 1])}mAh\n"
                     f"σ: {round(listStd[c - 1][v - 1])}mAh\n"
                     f"μ - 3σ: {round(listMM3S[c - 1][v - 1])}mAh\n"
                     f"μ - 2σ: {round(listMM2S[c - 1][v - 1])}mAh\n"
                     f"μ + 2σ: {round(listMP2S[c - 1][v - 1])}mAh\n"
                     f"μ + 3σ: {round(listMP3S[c - 1][v - 1])}mAh\n"
                     f"Minimum: {round(listMin[c - 1][v - 1])}mAh\n"
                     f"Maximum: {round(listMax[c - 1][v - 1])}mAh"),
                    wsOverviewStatistics
                )

        # ── 计算intPosiMaxmA、intPosi2V25、intTestProfileStartLine ──
        intPosiMaxmA = 0
        intPosi2V25 = 0
        intPresentmA = 0
        for c in range(self.intCurrentLevelNum):
            intPresentmA = self.listCurrentLevel[c]
            if self.listCurrentLevel[c] > intPresentmA:
                intPosiMaxmA = c
                break
        for v in range(self.intVoltageLevelNum):
            if self.listVoltageLevel[v] == 2.25:
                intPosi2V25 = v
                break

        if self.listTestInfo[0] == "Coin Cell":
            intTestProfileStartLine = 3
        elif self.listTestInfo[0] == "Pouch Cell":
            intTestProfileStartLine = 4
        else:
            raise BatteryAnalysisException(
                "[Test Info Error]: listTestInfo[0] is a unknown battery type")

        # ── 写入样本表（wsExcel） ──
        excel_utils.ws_set_col(wsExcel, 0, 3, 12)
        excel_utils.ws_set_col(wsExcel, 3, 1, 20)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine, 1, 12)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 1, 1, 15)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 2, 1, 10)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 3, 1, 18)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 4, 1, 25)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 5, 2, 30)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 7, 2, 15)
        intActualMeasuredCapacityLength = self.intVoltageLevelNum * 2
        excel_utils.ws_set_col(
            wsExcel, intTestProfileStartLine + 9, intActualMeasuredCapacityLength, 6)
        intTestDateStartCol = intTestProfileStartLine + \
            9 + intActualMeasuredCapacityLength
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol, 1, 10)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 1, 1, 12)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 2, 1, 18)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 3, 1, 8)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 4, 2, 40)

        listStrItems = [
            "Battery Type",  # 0
            "Specification",  # 1
            "Manufacturer",  # 2
            "Construction Method",  # 3
            "Test Profile",  # 4
            "Tester location",  # 5
            "Tested By",  # 6
            "Batch/Date Code",  # 7
            "Accelerated Aging[Years]",  # 8
            "Datasheet Nominal Capacity[mAh]",  # 9
            "Calculation Nominal Capacity[mAh]",  # 10
            "Required Useable Capacity[mAh]",  # 11
            None,  # 12
            # 13
            f"Actual Measured Capacity[mAh]\n(at {self.listCurrentLevel[intPosiMaxmA]}mA/2.25V)",
            "Test Date",  # 14
            "Samples Qty",  # 15
            "Temperature[℃]",  # 16
            "Result",  # 17
            "Test Results File",  # 18
            "Remarks"  # 19
        ]

        try:
            strRelProfilePath = os.path.relpath(
                self.listTestInfo[13], os.path.dirname(self.strSampleXlsxPath))
        except ValueError:
            strRelProfilePath = self.listTestInfo[13]

        if not self.listTestInfo[5]:
            strBatchDateCode = "n.a."
        else:
            strBatchDateCode = self.listTestInfo[5]

        intPassRate = float(
            int(self.listTestInfo[17]) / int(self.listTestInfo[9]))
        strRequiredUseableCapacityPercentage = f"{int(100 * int(self.listTestInfo[17]) / int(self.listTestInfo[9]))}%"

        [sy, sm, sd] = self.listBatteryInfo[2][0].split(" ")[0].split("-")
        [ey, em, ed] = self.listBatteryInfo[2][1].split(" ")[0].split("-")

        strRelResultPath = os.path.relpath(
            self.strResultXlsxPath, os.path.dirname(self.strReportWordPath))
        if listMM2S[intPosiMaxmA][intPosi2V25] / int(self.listTestInfo[9]) >= intPassRate:
            strResult = "Pass"
            strRemarks = "OK"
        else:
            strResult = "Fail"
            strRemarks = f"The expected usable Q(stat) should be more than {strRequiredUseableCapacityPercentage}, " \
                         f"while the actual measured minimum capacity to 2.25V is " \
                         f"{math.floor(100 * listMM2S[intPosiMaxmA][intPosi2V25] / int(self.listTestInfo[9]))}%."

        listStrContent = [
            self.listTestInfo[0],  # 0
            f"{self.listTestInfo[2]}-{self.listTestInfo[3]}",  # 1
            self.listTestInfo[4],  # 2
            self.listTestInfo[1],  # 3
            strRelProfilePath,  # 4
            self.listTestInfo[11],  # 5
            self.listTestInfo[12],  # 6
            strBatchDateCode,  # 7
            self.listTestInfo[10],  # 8
            self.listTestInfo[8],  # 9
            self.listTestInfo[9],  # 10
            self.listTestInfo[17],  # 11
            strRequiredUseableCapacityPercentage,  # 12
            None,  # 13
            f"{sd}.{sm}.{sy} - {ed}.{em}.{ey}",  # 14
            self.listTestInfo[6],  # 15
            self.listTestInfo[7],  # 16
            strResult,  # 17
            strRelResultPath,  # 18
            strRemarks  # 19
        ]

        # First 4 items
        for i in range(4):
            wsExcel.merge_range(0, i, 1, i, listStrItems[i], wsExcelLine)
        if intTestProfileStartLine == 4:
            wsExcel.merge_range(0, intTestProfileStartLine,
                                1, intTestProfileStartLine, "", wsExcelLine)
        wsExcel.write(0, intTestProfileStartLine, listStrItems[4], wsExcelLine)
        # Items 5-10
        for i in range(5, 11):
            wsExcel.merge_range(0, intTestProfileStartLine + (i - 4), 1,
                                intTestProfileStartLine + (i - 4), listStrItems[i], wsExcelLine)
        wsExcel.merge_range(0, intTestProfileStartLine + 7, 1,
                            intTestProfileStartLine + 8, listStrItems[11], wsExcelLine)
        wsExcel.merge_range(0, intTestProfileStartLine + 9, 0,
                            intTestDateStartCol - 1, listStrItems[13], wsExcelLine)
        for v in range(self.intVoltageLevelNum):
            wsExcel.merge_range(1, intTestProfileStartLine + 9 + v * 2, 1, intTestProfileStartLine +
                                9 + v * 2 + 1, f"{self.listVoltageLevel[v]}V", wsExcelLine)
        # Date columns (items 14-19)
        for i in range(14, 20):
            wsExcel.merge_range(0, intTestDateStartCol + (i - 14), 1,
                                intTestDateStartCol + (i - 14), listStrItems[i], wsExcelLine)

        wsExcel.write(2, 0, listStrContent[0], wsExcelData)
        wsExcel.write(2, 1, listStrContent[1], wsExcelData)
        wsExcel.write(2, 2, listStrContent[2], wsExcelData)
        wsExcel.write(2, 3, listStrContent[3], wsExcelData)
        if len(listStrContent[4].split("\\")) == 1:
            wsExcel.write(2, intTestProfileStartLine,
                          listStrContent[4], wsExcelData)
        else:
            url_path = listStrContent[4]
            url_path = url_path.replace('\\', '/')
            file_url = f'file:///{url_path}'
            wsExcel.write_url(2, intTestProfileStartLine, file_url,
                              wbSampleHyperlink, string=listStrContent[4].split("\\")[-1])
        for i in range(5, 13):
            wsExcel.write(2, intTestProfileStartLine + (i - 4),
                          listStrContent[i], wsExcelData)

        for v in range(self.intVoltageLevelNum):
            if v == intPosi2V25:
                wsExcel.write(2, intTestProfileStartLine + 9 + v * 2,
                              f"{round(listMM2S[intPosiMaxmA][v], 2)}", wsExcelData_bold)
                wsExcel.write_formula(f"{excel_utils.num2letter(intTestProfileStartLine + 9 + v * 2 + 1)}3",
                                      f"=TRUNC({excel_utils.num2letter(intTestProfileStartLine + 9 + v * 2)}3/{excel_utils.num2letter(intTestProfileStartLine + 6)}3, 2)",
                                      wsExcelData_percentage_bold)
            else:
                wsExcel.write(2, intTestProfileStartLine + 9 + v * 2,
                              f"{round(listMM2S[intPosiMaxmA][v], 2)}", wsExcelData)
                wsExcel.write_formula(f"{excel_utils.num2letter(intTestProfileStartLine + 9 + v * 2 + 1)}3",
                                      f"=TRUNC({excel_utils.num2letter(intTestProfileStartLine + 9 + v * 2)}3/{excel_utils.num2letter(intTestProfileStartLine + 6)}3, 2)",
                                      wsExcelData_percentage)

        # 写入常规数据列（Test Date, Samples Qty, Temperature, Result）
        for i in range(4):
            wsExcel.write(2, intTestDateStartCol + i,
                          listStrContent[14 + i],
                          wsExcelData_bgyellow if i == 3 else wsExcelData)

        # Remarks (col offset 5)
        wsExcel.write(2, intTestDateStartCol + 5,
                      listStrContent[19], wsExcelData)

        # Test Results File 作为超链接 (col offset 4)
        url_path = listStrContent[18]
        url_path = url_path.replace('\\', '/')
        file_url = f'file:///{url_path}'
        wsExcel.write_url(2, intTestDateStartCol + 4, file_url,
                          wbSampleHyperlink, string=listStrContent[18].split("\\")[-1])

        # ── 写入样本表（wsWord） ──
        excel_utils.ws_set_col(wsWord, 0, 1, 30)
        excel_utils.ws_set_col(wsWord, 1, intActualMeasuredCapacityLength, 3)
        for i in range(4):
            wsWord.write(i, 0, listStrItems[i], wsWordLine)
        for i in range(4, 12):
            wsWord.write(intTestProfileStartLine + (i - 4),
                         0, listStrItems[i], wsWordLine)
        wsWord.merge_range(intTestProfileStartLine + 8, 0,
                           intTestProfileStartLine + 10, 0, listStrItems[13], wsWordLine)
        intTestDateStartRow = intTestProfileStartLine + 11
        for i in range(6):
            wsWord.write(intTestDateStartRow + i, 0,
                         listStrItems[14 + i], wsWordLine)

        for i in range(4):
            wsWord.merge_range(
                i, 1, i, intActualMeasuredCapacityLength, listStrContent[i], wsWordData)
        if intTestProfileStartLine == 4:
            wsWord.merge_range(intTestProfileStartLine, 1, intTestProfileStartLine,
                               intActualMeasuredCapacityLength, "", wsWordData)
        if len(listStrContent[4].split("\\")) == 1:
            wsWord.write(intTestProfileStartLine, 1,
                         listStrContent[4], wsWordData)
        else:
            url_path = listStrContent[4]
            url_path = url_path.replace('\\', '/')
            file_url = f'file:///{url_path}'
            wsWord.write_url(intTestProfileStartLine, 1, file_url,
                             wbSampleHyperlink, string=listStrContent[4].split("\\")[-1])
        for i in range(5, 11):
            wsWord.merge_range(intTestProfileStartLine + (i - 4), 1, intTestProfileStartLine + (
                i - 4), intActualMeasuredCapacityLength, listStrContent[i], wsWordData)
        wsWord.merge_range(intTestProfileStartLine + 7, 1, intTestProfileStartLine + 7,
                           int(intActualMeasuredCapacityLength / 2), listStrContent[11], wsWordData)
        wsWord.merge_range(intTestProfileStartLine + 7, int(intActualMeasuredCapacityLength / 2) + 1,
                           intTestProfileStartLine + 7, intActualMeasuredCapacityLength, listStrContent[12], wsWordData)
        for v in range(self.intVoltageLevelNum):
            if v == intPosi2V25:
                wsWord.merge_range(intTestProfileStartLine + 8, 1 + v * 2, intTestProfileStartLine +
                                   8, 2 + v * 2, f"{self.listVoltageLevel[v]}V", wsWordData_bold)
                wsWord.merge_range(intTestProfileStartLine + 9, 1 + v * 2, intTestProfileStartLine + 9,
                                   2 + v * 2, f"{round(listMM2S[intPosiMaxmA][v], 2)}", wsWordData_bold)
                wsWord.merge_range(intTestProfileStartLine + 10, 1 + v * 2,
                                   intTestProfileStartLine + 10, 2 + v * 2, "", wsWordData_bold)
                wsWord.write_formula(f"{excel_utils.num2letter(1 + v * 2)}{intTestProfileStartLine + 11}",
                                     f"=TRUNC({excel_utils.num2letter(1 + v * 2)}{intTestProfileStartLine + 10}/B{intTestProfileStartLine + 7}, 2)",
                                     wsWordData_percentage_bold)
            else:
                wsWord.merge_range(intTestProfileStartLine + 8, 1 + v * 2, intTestProfileStartLine +
                                   8, 2 + v * 2, f"{self.listVoltageLevel[v]}V", wsWordData)
                wsWord.merge_range(intTestProfileStartLine + 9, 1 + v * 2, intTestProfileStartLine +
                                   9, 2 + v * 2, f"{round(listMM2S[intPosiMaxmA][v], 2)}", wsWordData)
                wsWord.merge_range(intTestProfileStartLine + 10, 1 + v * 2,
                                   intTestProfileStartLine + 10, 2 + v * 2, "", wsWordData)
                wsWord.write_formula(f"{excel_utils.num2letter(1 + v * 2)}{intTestProfileStartLine + 11}",
                                     f"=TRUNC({excel_utils.num2letter(1 + v * 2)}{intTestProfileStartLine + 10}/B{intTestProfileStartLine + 7}, 2)",
                                     wsWordData_percentage)

        wsWord.merge_range(intTestDateStartRow, 1, intTestDateStartRow,
                           intActualMeasuredCapacityLength, listStrContent[14], wsWordData)
        wsWord.merge_range(intTestDateStartRow + 1, 1, intTestDateStartRow + 1,
                           intActualMeasuredCapacityLength, listStrContent[15], wsWordData)
        wsWord.merge_range(intTestDateStartRow + 2, 1, intTestDateStartRow + 2,
                           intActualMeasuredCapacityLength, listStrContent[16], wsWordData)
        wsWord.merge_range(intTestDateStartRow + 3, 1, intTestDateStartRow + 3,
                           intActualMeasuredCapacityLength, listStrContent[17], wsWordData_bgyellow)
        wsWord.merge_range(intTestDateStartRow + 4, 1, intTestDateStartRow +
                           4, intActualMeasuredCapacityLength, "", wsWordData)
        url_path = strRelResultPath
        url_path = url_path.replace('\\', '/')
        file_url = f'file:///{url_path}'
        wsWord.write_url(intTestDateStartRow + 4, 1, file_url,
                         wbSampleHyperlink, string=listStrContent[18].split("\\")[-1])
        wsWord.merge_range(intTestDateStartRow + 5, 1, intTestDateStartRow + 5,
                           intActualMeasuredCapacityLength, listStrContent[19], wsWordData)

        # ── 关闭工作簿 ──
        wbResult.close()
        wbSample.close()
