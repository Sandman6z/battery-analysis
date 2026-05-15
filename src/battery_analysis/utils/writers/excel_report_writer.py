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

    # ── 格式定义 ──

    def _create_formats(self, wbResult, wbSample):
        """创建所有XlsxWriter格式对象"""
        fmts = {}

        fmts['result_data'] = wbResult.add_format({
            'font_name': 'Microsoft YaHei', 'font_size': 9, 'font_color': 'black',
            'bold': False, 'align': 'center', 'valign': 'vcenter',
        })
        fmts['result_data_italic'] = wbResult.add_format({
            'font_name': 'Microsoft YaHei', 'font_size': 9, 'font_color': 'black',
            'italic': True, 'bold': False, 'align': 'center', 'valign': 'vcenter',
        })
        fmts['overview_stat'] = wbResult.add_format({
            'font_name': 'Arial Narrow', 'font_size': 9, 'font_color': 'black',
            'bold': False, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'border': 1, 'border_color': '#BFBFBF',
        })
        fmts['overview_stat_dark'] = wbResult.add_format({
            'font_name': 'Arial Narrow', 'font_size': 12, 'font_color': 'black',
            'bg_color': '#BFBFBF', 'bold': True, 'align': 'center', 'valign': 'vcenter',
            'border': 1, 'border_color': '#BFBFBF',
        })
        fmts['overview_stat_light'] = wbResult.add_format({
            'font_name': 'Arial Narrow', 'font_size': 12, 'font_color': 'black',
            'bg_color': '#F2F2F2', 'bold': False, 'align': 'center', 'valign': 'vcenter',
            'border': 1, 'border_color': '#BFBFBF',
        })
        fmts['overview_stat_light_bold'] = wbResult.add_format({
            'font_name': 'Arial Narrow', 'font_size': 12, 'font_color': 'black',
            'bg_color': '#F2F2F2', 'bold': True, 'align': 'center', 'valign': 'vcenter',
            'border': 1, 'border_color': '#BFBFBF',
        })
        fmts['sample_line'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'border': 1, 'border_color': 'black',
        })
        fmts['sample_data'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': False, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'border': 1, 'border_color': 'black',
        })
        fmts['sample_data_bold'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'border': 1, 'border_color': 'black',
        })
        fmts['sample_data_pct'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': False, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'num_format': '0%', 'border': 1, 'border_color': 'black',
        })
        fmts['sample_data_pct_bold'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'num_format': '0%', 'border': 1, 'border_color': 'black',
        })
        fmts['sample_data_yellow'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': False, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'border': 1, 'border_color': 'black',
            'bg_color': '#FFFF00',
        })
        fmts['word_line'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': False, 'align': 'center', 'valign': 'vcenter',
            'border': 1, 'border_color': 'black',
        })
        fmts['word_data'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': False, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'border': 1, 'border_color': 'black',
        })
        fmts['word_data_bold'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'border': 1, 'border_color': 'black',
        })
        fmts['word_data_pct'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': False, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'border': 1, 'border_color': 'black',
            'num_format': '0%',
        })
        fmts['word_data_pct_bold'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'border': 1, 'border_color': 'black',
            'num_format': '0%',
        })
        fmts['word_data_yellow'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': 'black',
            'bold': False, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'border': 1, 'border_color': 'black',
            'bg_color': '#FFFF00',
        })
        fmts['hyperlink'] = wbSample.add_format({
            'font_name': 'Arial', 'font_size': 10, 'font_color': '#0000FF',
            'underline': True, 'bold': False, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'border': 1, 'border_color': 'black',
        })
        return fmts

    # ── 写入Overview表头 ──

    def _write_overview_header(self, wsOverview):
        """写入Overview表的文件头信息"""
        header_info = [
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
        for i, info in enumerate(header_info):
            wsOverview.write(i, 0, info)

    # ── 写入结果表列名 ──

    def _write_result_columns(self, wsResult, fmts):
        """写入result工作表的列标题行"""
        excel_utils.ws_set_col(
            wsResult, 0, self.intCurrentLevelNum * (2 + self.intVoltageLevelNum) + 1, 10)
        excel_utils.ws_set_col(wsResult, 0, 1, 20)
        wsResult.write(2, 0, "Battery", fmts['result_data'])
        wsResult.write(4 + self.intBatteryNum, 0, "Mean(μ)", fmts['result_data_italic'])
        wsResult.write(5 + self.intBatteryNum, 0, "Median", fmts['result_data_italic'])
        wsResult.write(6 + self.intBatteryNum, 0, "Std. Var.(σ)", fmts['result_data_italic'])
        wsResult.write(7 + self.intBatteryNum, 0, "μ-3σ", fmts['result_data_italic'])
        wsResult.write(8 + self.intBatteryNum, 0, "μ-2σ", fmts['result_data_italic'])
        wsResult.write(9 + self.intBatteryNum, 0, "μ+2σ", fmts['result_data_italic'])
        wsResult.write(10 + self.intBatteryNum, 0, "μ+3σ", fmts['result_data_italic'])
        wsResult.write(11 + self.intBatteryNum, 0, "Minimum", fmts['result_data_italic'])
        wsResult.write(12 + self.intBatteryNum, 0, "Maximum", fmts['result_data_italic'])
        for c in range(self.intCurrentLevelNum):
            wsResult.write(1, 1 + c * (2 + self.intVoltageLevelNum),
                           f"{self.listCurrentLevel[c]}mA", fmts['result_data'])
            wsResult.merge_range(1, 2 + c * (2 + self.intVoltageLevelNum), 1, (c + 1) * (
                2 + self.intVoltageLevelNum) - 1, "Voltage", fmts['result_data'])
            for v in range(self.intVoltageLevelNum):
                wsResult.write(2, 2 + c * (2 + self.intVoltageLevelNum) + v,
                               f"{self.listVoltageLevel[v]}V", fmts['result_data'])

    # ── 写入电池数据 ──

    def _write_battery_data(self, wsResult, fmts):
        """将每块电池的容量数据写入result表"""
        for b in range(self.intBatteryNum):
            excel_utils.ws_result_write_data(
                3 + b, 0, self.listBatteryName[b], fmts['result_data'], wsResult)
            i = 0
            for c in range(self.intCurrentLevelNum):
                for v in range(self.intVoltageLevelNum):
                    excel_utils.ws_result_write_data(
                        3 + b,
                        2 + c * (2 + self.intVoltageLevelNum) + v,
                        self.listBatteryCharge[b][i],
                        fmts['result_data'],
                        wsResult)
                    i += 1

    # ── 写入统计值到结果表 ──

    def _write_result_statistics(self, wsResult, stats, fmts):
        """将统计值（均值、中位数、标准差等）写入result表"""
        for c in range(self.intCurrentLevelNum):
            for v in range(self.intVoltageLevelNum):
                stat_rows = [
                    (4, 'mean'), (5, 'med'), (6, 'std'),
                    (7, 'mm3s'), (8, 'mm2s'), (9, 'mp2s'), (10, 'mp3s'),
                    (11, 'min'), (12, 'max'),
                ]
                for row_offset, key in stat_rows:
                    excel_utils.ws_result_write_data(
                        row_offset + self.intBatteryNum,
                        2 + c * (2 + self.intVoltageLevelNum) + v,
                        round(stats[key][c][v], 5),
                        fmts['result_data'],
                        wsResult)

    # ── 插入图像 ──

    def _insert_images(self, wsResult):
        """将容量图插入result表"""
        for c in range(self.intCurrentLevelNum):
            wsResult.insert_image(
                14 + self.intBatteryNum,
                1 + c * (2 + self.intVoltageLevelNum),
                self.listPngPath[c],
                {
                    'x_scale': ((2 + self.intVoltageLevelNum) * 2 - 1) / 16,
                    'y_scale': ((2 + self.intVoltageLevelNum) * 2 - 1) / 16,
                }
            )

    # ── 写入Overview统计表 ──

    def _write_overview_statistics(self, wsOverview, stats, fmts,
                                   wsOverviewStatisticalStartLine=13):
        """写入Overview工作表中的统计结果"""
        wsOverview.write(wsOverviewStatisticalStartLine, 0,
                         "Statisticals Results", fmts['overview_stat_dark'])
        wsOverview.set_row(wsOverviewStatisticalStartLine, 20)
        wsOverview.set_column(0, 0, 18)
        for v in range(1, self.intVoltageLevelNum + 1):
            wsOverview.set_column(v, v, 18)
            wsOverview.write_rich_string(
                wsOverviewStatisticalStartLine, v,
                fmts['overview_stat_light'], "Cut-off Voltage ",
                fmts['overview_stat_light_bold'],
                f"{self.listVoltageLevel[v - 1]}V",
                fmts['overview_stat_light']
            )
        for c in range(1, self.intCurrentLevelNum + 1):
            wsOverview.set_row(wsOverviewStatisticalStartLine + c, 120)
            wsOverview.write_rich_string(
                wsOverviewStatisticalStartLine + c, 0,
                fmts['overview_stat_light'], "Pulse Current ",
                fmts['overview_stat_light_bold'],
                f"{self.listCurrentLevel[c - 1]}mA",
                fmts['overview_stat_light']
            )
            for v in range(1, self.intVoltageLevelNum + 1):
                wsOverview.write(
                    wsOverviewStatisticalStartLine + c, v,
                    (f"μ: {round(stats['mean'][c - 1][v - 1])}mAh\n"
                     f"Median: {round(stats['med'][c - 1][v - 1])}mAh\n"
                     f"σ: {round(stats['std'][c - 1][v - 1])}mAh\n"
                     f"μ - 3σ: {round(stats['mm3s'][c - 1][v - 1])}mAh\n"
                     f"μ - 2σ: {round(stats['mm2s'][c - 1][v - 1])}mAh\n"
                     f"μ + 2σ: {round(stats['mp2s'][c - 1][v - 1])}mAh\n"
                     f"μ + 3σ: {round(stats['mp3s'][c - 1][v - 1])}mAh\n"
                     f"Minimum: {round(stats['min'][c - 1][v - 1])}mAh\n"
                     f"Maximum: {round(stats['max'][c - 1][v - 1])}mAh"),
                    fmts['overview_stat']
                )

    # ── 计算样本表所需的位置和内容 ──

    def _prepare_sample_content(self, stats):
        """计算样本表所需的位置参数和内容列表"""
        # 最大电流位置
        intPosiMaxmA = 0
        for c in range(1, self.intCurrentLevelNum):
            if self.listCurrentLevel[c] > self.listCurrentLevel[intPosiMaxmA]:
                intPosiMaxmA = c

        # 2.25V 电压位置
        intPosi2V25 = 0
        for v in range(self.intVoltageLevelNum):
            if self.listVoltageLevel[v] == 2.25:
                intPosi2V25 = v
                break

        # 测试配置起始行
        if self.listTestInfo[0] == "Coin Cell":
            intTestProfileStartLine = 3
        elif self.listTestInfo[0] == "Pouch Cell":
            intTestProfileStartLine = 4
        else:
            raise BatteryAnalysisException(
                "[Test Info Error]: listTestInfo[0] is a unknown battery type")

        intActualMeasuredCapacityLength = self.intVoltageLevelNum * 2
        intTestDateStartCol = intTestProfileStartLine + 9 + intActualMeasuredCapacityLength

        # 构建列表项
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
            f"Actual Measured Capacity[mAh]\n(at {self.listCurrentLevel[intPosiMaxmA]}mA/2.25V)",  # 13
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

        strBatchDateCode = self.listTestInfo[5] if self.listTestInfo[5] else "n.a."
        intPassRate = float(int(self.listTestInfo[17]) / int(self.listTestInfo[9]))
        strRequiredUseableCapacityPercentage = f"{int(100 * intPassRate)}%"

        [sy, sm, sd] = self.listBatteryInfo[2][0].split(" ")[0].split("-")
        [ey, em, ed] = self.listBatteryInfo[2][1].split(" ")[0].split("-")

        strRelResultPath = os.path.relpath(
            self.strResultXlsxPath, os.path.dirname(self.strReportWordPath))

        listMM2S = stats['mm2s']
        if listMM2S[intPosiMaxmA][intPosi2V25] / int(self.listTestInfo[9]) >= intPassRate:
            strResult = "Pass"
            strRemarks = "OK"
        else:
            strResult = "Fail"
            strRemarks = (f"The expected usable Q(stat) should be more than "
                          f"{strRequiredUseableCapacityPercentage}, "
                          f"while the actual measured minimum capacity to 2.25V is "
                          f"{math.floor(100 * listMM2S[intPosiMaxmA][intPosi2V25] / int(self.listTestInfo[9]))}%.")

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

        return {
            'intPosiMaxmA': intPosiMaxmA,
            'intPosi2V25': intPosi2V25,
            'intTestProfileStartLine': intTestProfileStartLine,
            'intActualMeasuredCapacityLength': intActualMeasuredCapacityLength,
            'intTestDateStartCol': intTestDateStartCol,
            'listStrItems': listStrItems,
            'listStrContent': listStrContent,
        }

    # ── 写入样本表（wsExcel） ──

    def _write_sample_excel(self, wsExcel, sample, stats, fmts):
        """写入Sample文件的Excel工作表"""
        intPosiMaxmA = sample['intPosiMaxmA']
        intPosi2V25 = sample['intPosi2V25']
        intTestProfileStartLine = sample['intTestProfileStartLine']
        intActualMeasuredCapacityLength = sample['intActualMeasuredCapacityLength']
        intTestDateStartCol = sample['intTestDateStartCol']
        listStrItems = sample['listStrItems']
        listStrContent = sample['listStrContent']

        # 设置列宽
        excel_utils.ws_set_col(wsExcel, 0, 3, 12)
        excel_utils.ws_set_col(wsExcel, 3, 1, 20)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine, 1, 12)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 1, 1, 15)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 2, 1, 10)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 3, 1, 18)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 4, 1, 25)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 5, 2, 30)
        excel_utils.ws_set_col(wsExcel, intTestProfileStartLine + 7, 2, 15)
        excel_utils.ws_set_col(
            wsExcel, intTestProfileStartLine + 9, intActualMeasuredCapacityLength, 6)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol, 1, 10)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 1, 1, 12)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 2, 1, 18)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 3, 1, 8)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 4, 2, 40)

        # 写入表头行
        for i in range(4):
            wsExcel.merge_range(0, i, 1, i, listStrItems[i], fmts['sample_line'])
        if intTestProfileStartLine == 4:
            wsExcel.merge_range(0, intTestProfileStartLine,
                                1, intTestProfileStartLine, "", fmts['sample_line'])
        wsExcel.write(0, intTestProfileStartLine, listStrItems[4], fmts['sample_line'])
        for i in range(5, 11):
            wsExcel.merge_range(0, intTestProfileStartLine + (i - 4), 1,
                                intTestProfileStartLine + (i - 4), listStrItems[i], fmts['sample_line'])
        wsExcel.merge_range(0, intTestProfileStartLine + 7, 1,
                            intTestProfileStartLine + 8, listStrItems[11], fmts['sample_line'])
        wsExcel.merge_range(0, intTestProfileStartLine + 9, 0,
                            intTestDateStartCol - 1, listStrItems[13], fmts['sample_line'])
        for v in range(self.intVoltageLevelNum):
            wsExcel.merge_range(1, intTestProfileStartLine + 9 + v * 2, 1, intTestProfileStartLine +
                                9 + v * 2 + 1, f"{self.listVoltageLevel[v]}V", fmts['sample_line'])
        for i in range(14, 20):
            wsExcel.merge_range(0, intTestDateStartCol + (i - 14), 1,
                                intTestDateStartCol + (i - 14), listStrItems[i], fmts['sample_line'])

        # 写入内容行
        wsExcel.write(2, 0, listStrContent[0], fmts['sample_data'])
        wsExcel.write(2, 1, listStrContent[1], fmts['sample_data'])
        wsExcel.write(2, 2, listStrContent[2], fmts['sample_data'])
        wsExcel.write(2, 3, listStrContent[3], fmts['sample_data'])
        if len(listStrContent[4].split("\\")) == 1:
            wsExcel.write(2, intTestProfileStartLine,
                          listStrContent[4], fmts['sample_data'])
        else:
            url_path = listStrContent[4].replace('\\', '/')
            wsExcel.write_url(2, intTestProfileStartLine, f'file:///{url_path}',
                              fmts['hyperlink'], string=listStrContent[4].split("\\")[-1])
        for i in range(5, 13):
            wsExcel.write(2, intTestProfileStartLine + (i - 4),
                          listStrContent[i], fmts['sample_data'])

        # 电压等级容量列
        for v in range(self.intVoltageLevelNum):
            fmt_val = fmts['sample_data_bold'] if v == intPosi2V25 else fmts['sample_data']
            fmt_pct = fmts['sample_data_pct_bold'] if v == intPosi2V25 else fmts['sample_data_pct']
            col = intTestProfileStartLine + 9 + v * 2
            wsExcel.write(2, col, f"{round(stats['mm2s'][intPosiMaxmA][v], 2)}", fmt_val)
            wsExcel.write_formula(
                f"{excel_utils.num2letter(col + 1)}3",
                f"=TRUNC({excel_utils.num2letter(col + 1)}3/"
                f"{excel_utils.num2letter(intTestProfileStartLine + 6)}3, 2)",
                fmt_pct)

        # 日期/结果列
        for i in range(4):
            fmt = fmts['sample_data_yellow'] if i == 3 else fmts['sample_data']
            wsExcel.write(2, intTestDateStartCol + i,
                          listStrContent[14 + i], fmt)

        wsExcel.write(2, intTestDateStartCol + 5,
                      listStrContent[19], fmts['sample_data'])

        # 测试结果超链接
        url_path = listStrContent[18].replace('\\', '/')
        wsExcel.write_url(2, intTestDateStartCol + 4, f'file:///{url_path}',
                          fmts['hyperlink'], string=listStrContent[18].split("\\")[-1])

    # ── 写入样本表（wsWord） ──

    def _write_sample_word(self, wsWord, sample, stats, fmts):
        """写入Sample文件的Word工作表"""
        intPosiMaxmA = sample['intPosiMaxmA']
        intPosi2V25 = sample['intPosi2V25']
        intTestProfileStartLine = sample['intTestProfileStartLine']
        intActualMeasuredCapacityLength = sample['intActualMeasuredCapacityLength']
        listStrItems = sample['listStrItems']
        listStrContent = sample['listStrContent']
        intTestDateStartRow = intTestProfileStartLine + 11

        # 设置列宽
        excel_utils.ws_set_col(wsWord, 0, 1, 30)
        excel_utils.ws_set_col(wsWord, 1, intActualMeasuredCapacityLength, 3)

        # 写入表头
        for i in range(4):
            wsWord.write(i, 0, listStrItems[i], fmts['word_line'])
        for i in range(4, 12):
            wsWord.write(intTestProfileStartLine + (i - 4),
                         0, listStrItems[i], fmts['word_line'])
        wsWord.merge_range(intTestProfileStartLine + 8, 0,
                           intTestProfileStartLine + 10, 0, listStrItems[13], fmts['word_line'])
        for i in range(6):
            wsWord.write(intTestDateStartRow + i, 0,
                         listStrItems[14 + i], fmts['word_line'])

        # 写入内容
        for i in range(4):
            wsWord.merge_range(
                i, 1, i, intActualMeasuredCapacityLength, listStrContent[i], fmts['word_data'])
        if intTestProfileStartLine == 4:
            wsWord.merge_range(intTestProfileStartLine, 1, intTestProfileStartLine,
                               intActualMeasuredCapacityLength, "", fmts['word_data'])
        if len(listStrContent[4].split("\\")) == 1:
            wsWord.write(intTestProfileStartLine, 1,
                         listStrContent[4], fmts['word_data'])
        else:
            url_path = listStrContent[4].replace('\\', '/')
            wsWord.write_url(intTestProfileStartLine, 1, f'file:///{url_path}',
                             fmts['hyperlink'], string=listStrContent[4].split("\\")[-1])
        for i in range(5, 11):
            wsWord.merge_range(intTestProfileStartLine + (i - 4), 1, intTestProfileStartLine + (
                i - 4), intActualMeasuredCapacityLength, listStrContent[i], fmts['word_data'])
        wsWord.merge_range(intTestProfileStartLine + 7, 1, intTestProfileStartLine + 7,
                           int(intActualMeasuredCapacityLength / 2), listStrContent[11], fmts['word_data'])
        wsWord.merge_range(intTestProfileStartLine + 7, int(intActualMeasuredCapacityLength / 2) + 1,
                           intTestProfileStartLine + 7, intActualMeasuredCapacityLength, listStrContent[12], fmts['word_data'])

        for v in range(self.intVoltageLevelNum):
            is_25v = v == intPosi2V25
            fmt_val = fmts['word_data_bold'] if is_25v else fmts['word_data']
            fmt_pct = fmts['word_data_pct_bold'] if is_25v else fmts['word_data_pct']
            col = 1 + v * 2
            wsWord.merge_range(intTestProfileStartLine + 8, col,
                               intTestProfileStartLine + 8, col + 1,
                               f"{self.listVoltageLevel[v]}V", fmt_val)
            wsWord.merge_range(intTestProfileStartLine + 9, col,
                               intTestProfileStartLine + 9, col + 1,
                               f"{round(stats['mm2s'][intPosiMaxmA][v], 2)}", fmt_val)
            wsWord.merge_range(intTestProfileStartLine + 10, col,
                               intTestProfileStartLine + 10, col + 1, "", fmt_val)
            wsWord.write_formula(
                f"{excel_utils.num2letter(col)}{intTestProfileStartLine + 11}",
                f"=TRUNC({excel_utils.num2letter(col)}{intTestProfileStartLine + 10}/"
                f"B{intTestProfileStartLine + 7}, 2)",
                fmt_pct)

        # 日期/结果行
        wsWord.merge_range(intTestDateStartRow, 1, intTestDateStartRow,
                           intActualMeasuredCapacityLength, listStrContent[14], fmts['word_data'])
        wsWord.merge_range(intTestDateStartRow + 1, 1, intTestDateStartRow + 1,
                           intActualMeasuredCapacityLength, listStrContent[15], fmts['word_data'])
        wsWord.merge_range(intTestDateStartRow + 2, 1, intTestDateStartRow + 2,
                           intActualMeasuredCapacityLength, listStrContent[16], fmts['word_data'])
        wsWord.merge_range(intTestDateStartRow + 3, 1, intTestDateStartRow + 3,
                           intActualMeasuredCapacityLength, listStrContent[17], fmts['word_data_yellow'])
        url_path = listStrContent[18].replace('\\', '/')
        wsWord.write_url(intTestDateStartRow + 4, 1, f'file:///{url_path}',
                         fmts['hyperlink'], string=listStrContent[18].split("\\")[-1])
        wsWord.merge_range(intTestDateStartRow + 5, 1, intTestDateStartRow + 5,
                           intActualMeasuredCapacityLength, listStrContent[19], fmts['word_data'])

    # ── 主入口 ──

    def write(self, list_cpt=None, stats=None) -> None:
        """执行Excel报告写入"""
        # 创建工作簿和工作表
        wbResult = xwt.Workbook(self.strResultXlsxPath)
        wsOverview = wbResult.add_worksheet("overview")
        wsResult = wbResult.add_worksheet("result")
        wbSample = xwt.Workbook(self.strSampleXlsxPath)
        wsWord = wbSample.add_worksheet("word")
        wsExcel = wbSample.add_worksheet("excel")

        # 创建格式
        fmts = self._create_formats(wbResult, wbSample)

        # 写入Overview表头
        if wsOverview is None:
            raise BatteryAnalysisException(
                f"{self.strResultXlsxPath} sheet[overview] creation failed")
        self._write_overview_header(wsOverview)

        # 写入result表列名
        if wsResult is None:
            raise BatteryAnalysisException(
                f"{self.strResultXlsxPath} sheet[result] creation failed")
        self._write_result_columns(wsResult, fmts)

        # 写入电池数据
        self._write_battery_data(wsResult, fmts)

        # 计算统计值
        if list_cpt is None:
            list_cpt = _compute_list_cpt(
                self.listBatteryCharge, self.intBatteryNum,
                self.intCurrentLevelNum, self.intVoltageLevelNum)
        if stats is None:
            stats = _compute_statistics(
                list_cpt, self.intCurrentLevelNum, self.intVoltageLevelNum)

        # 写入统计值、图像、Overview统计表
        self._write_result_statistics(wsResult, stats, fmts)
        self._insert_images(wsResult)
        self._write_overview_statistics(wsOverview, stats, fmts)

        # 准备样本表内容并写入
        sample = self._prepare_sample_content(stats)
        self._write_sample_excel(wsExcel, sample, stats, fmts)
        self._write_sample_word(wsWord, sample, stats, fmts)

        # 关闭工作簿
        wbResult.close()
        wbSample.close()
