"""Xlsx/Word/Csv 写入器（旧版适配器）

主要功能是协调绘图和委托给专用的 ExcelReportWriter / WordReportWriter / CsvWriter。
与新版 writer 的差异：生成插件标题、管理图片/ SVG 路径、处理旧式日期回退逻辑。
"""

import importlib.resources
import logging
import math
import os
import re
from pathlib import Path

import matplotlib

from battery_analysis.utils.constants import (
    BATTERY_TYPE_BASE,
    CN_FONT_LIST,
    COLOR_NAME,
    PLT_COLOR_TYPE,
)
from battery_analysis.utils.processors.data_utils import (
    build_plot_title,
    generate_current_type_string,
)
from battery_analysis.utils.readers.date_parser import parse_test_date
from battery_analysis.utils.writers import plot_writer

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = CN_FONT_LIST
plt.rcParams["axes.unicode_minus"] = False


logger = logging.getLogger(__name__)

# ── 共享常量 ──────────────────────────────────────────────────


def match_battery_type(test_info_type: str) -> str:
    """从测试信息中匹配电池类型，返回标准类型名称"""
    try:
        stripped_types = [bt.strip() for bt in BATTERY_TYPE_BASE]
        result = next((bt for bt in stripped_types if bt in test_info_type), None)
        return result or stripped_types[0]
    except (IndexError, TypeError, ValueError):
        return test_info_type


# ── 共享报告内容计算 ──────────────────────────────────────────
# ExcelReportWriter._prepare_sample_content 与
# WordReportWriter._prepare_overview_content 约 90% 相同，
# 本函数提取公共部分，差异由各调用方自行处理。


def compute_report_content_base(
    listCurrentLevel,
    intCurrentLevelNum,
    listVoltageLevel,
    intVoltageLevelNum,
    listTestInfo,
    listBatteryInfo,
    strSampleXlsxPath,
    strResultXlsxPath,
    strReportWordPath,
    stats,
):
    """计算报告内容的位置参数和列表项（Excel/Word 共享部分）

    Returns:
        dict: 包含 intPosiMaxmA, intPosi2V25, intTestProfileStartLine,
              intActualMeasuredCapacityLength, listStrItems, listStrContent,
              strResult, strRemarks, strRequiredUseableCapacityPercentage
    """
    # 最大电流位置
    intPosiMaxmA = 0
    for c in range(1, intCurrentLevelNum):
        if listCurrentLevel[c] > listCurrentLevel[intPosiMaxmA]:
            intPosiMaxmA = c

    # 2.25V 电压位置
    intPosi2V25 = 0
    for v in range(intVoltageLevelNum):
        if listVoltageLevel[v] == 2.25:
            intPosi2V25 = v
            break

    # 测试配置起始行：基础 3 行（Battery Type / Specification / Manufacturer）
    # 如果构造方法（listTestInfo[1]）有值，则增加一行
    intTestProfileStartLine = 3
    if listTestInfo[1]:
        intTestProfileStartLine += 1

    intActualMeasuredCapacityLength = intVoltageLevelNum * 2

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
        f"Actual Measured Capacity[mAh]\n(at {listCurrentLevel[intPosiMaxmA]}mA/2.25V)",  # 13
        "Test Date",  # 14
        "Samples Qty",  # 15
        "Temperature[℃]",  # 16
        "Result",  # 17
        "Test Results File",  # 18
        "Remarks",  # 19
    ]

    try:
        strRelProfilePath = os.path.relpath(listTestInfo[13], os.path.dirname(strSampleXlsxPath))
    except ValueError:
        strRelProfilePath = listTestInfo[13]

    strBatchDateCode = listTestInfo[5] if listTestInfo[5] else "n.a."
    intPassRate = float(int(listTestInfo[17]) / int(listTestInfo[9]))
    strRequiredUseableCapacityPercentage = f"{int(100 * intPassRate)}%"

    [sy, sm, sd] = listBatteryInfo[2][0].split(" ")[0].split("-")
    [ey, em, ed] = listBatteryInfo[2][1].split(" ")[0].split("-")

    strRelResultPath = os.path.relpath(strResultXlsxPath, os.path.dirname(strReportWordPath))

    listMM2S = stats["mm2s"]
    if listMM2S[intPosiMaxmA][intPosi2V25] / int(listTestInfo[9]) >= intPassRate:
        strResult = "Pass"
        strRemarks = "OK"
    else:
        strResult = "Fail"
        strRemarks = (
            f"The expected usable Q(stat) should be more than "
            f"{strRequiredUseableCapacityPercentage}, "
            f"while the actual measured minimum capacity to 2.25V is "
            f"{math.floor(100 * listMM2S[intPosiMaxmA][intPosi2V25] / int(listTestInfo[9]))}%."
        )

    listStrContent = [
        listTestInfo[0],  # 0
        f"{listTestInfo[2]}-{listTestInfo[3]}",  # 1
        listTestInfo[4],  # 2
        listTestInfo[1],  # 3
        strRelProfilePath,  # 4
        listTestInfo[11],  # 5
        listTestInfo[12],  # 6
        strBatchDateCode,  # 7
        listTestInfo[10],  # 8
        listTestInfo[8],  # 9
        listTestInfo[9],  # 10
        listTestInfo[17],  # 11
        strRequiredUseableCapacityPercentage,  # 12
        None,  # 13
        f"{sd}.{sm}.{sy} - {ed}.{em}.{ey}",  # 14
        listTestInfo[6],  # 15
        listTestInfo[7],  # 16
        strResult,  # 17
        strRelResultPath,  # 18
        strRemarks,  # 19
    ]

    return {
        "intPosiMaxmA": intPosiMaxmA,
        "intPosi2V25": intPosi2V25,
        "intTestProfileStartLine": intTestProfileStartLine,
        "intActualMeasuredCapacityLength": intActualMeasuredCapacityLength,
        "listStrItems": listStrItems,
        "listStrContent": listStrContent,
        "strResult": strResult,
        "strRemarks": strRemarks,
        "strRequiredUseableCapacityPercentage": strRequiredUseableCapacityPercentage,
        "strBatchDateCode": strBatchDateCode,
        "strRelResultPath": strRelResultPath,
    }


class ReportCoordinator:
    """报告协调器 — 协调 Excel / Word / CSV / 图表的全流程写入。

    旧名 XlsxWordWriter（保留为别名以保持向后兼容）。
    """

    def __init__(
        self,
        strResultPath: str,
        listTestInfo: list,
        listBatteryInfo: list,
        equipment_info: dict | None = None,
    ) -> None:
        # ── 后向兼容：接受 TestInfo 实例 ──────────────────────────
        from battery_analysis.domain.entities.test_info import TestInfo

        if isinstance(listTestInfo, TestInfo):
            listTestInfo = listTestInfo.to_list()

        self.listTestInfo = listTestInfo
        self.listBatteryInfo = listBatteryInfo
        self._equipment_info = equipment_info or {}

        # 提取测试日期（YYYYMMDD）
        td = self._extract_test_date()

        # 构建输出路径
        self.strResultPath = os.path.join(strResultPath, f"{td}_v{listTestInfo[16]}")
        os.makedirs(self.strResultPath, exist_ok=True)

        # 电流/电压等级信息
        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        self.intCurrentLevelNum = len(self.listCurrentLevel)
        self.intVoltageLevelNum = len(self.listVoltageLevel)
        self.strFileCurrentType = generate_current_type_string(self.listCurrentLevel)

        # 电池信息
        self.listBatteryCharge = self.listBatteryInfo[0]
        self.listBatteryName = self.listBatteryInfo[1]
        self.intBatteryNum = len(self.listBatteryName)

        # 图像标题与路径
        self._build_image_paths_and_titles(td)
        # 文档路径（excel / word / csv）
        self._build_document_paths(td)
        # 文本替换列表
        self._build_replacements()

    def _extract_test_date(self) -> str:
        """从 BatteryInfo 提取测试日期，返回 YYYYMMDD 字符串"""
        # 优先使用 listBatteryInfo[3] (标准路径)
        test_date = self.listBatteryInfo[3] if len(self.listBatteryInfo) > 3 else ""
        original_cycle = self.listBatteryInfo[4] if len(self.listBatteryInfo) > 4 else ""
        td = parse_test_date(
            str(test_date) if test_date else "", str(original_cycle) if original_cycle else ""
        )

        if td and td != "00000000":
            logger.info("Successfully parsed date: %s", td)
            return td

        # 回退：从电池名称中提取
        return self._extract_date_from_battery_name()

    def _extract_date_from_battery_name(self) -> str:
        """从电池名称的最后一组连续数字提取日期"""
        logger.warning("Standard date parsing failed, trying to extract from battery name")
        if len(self.listBatteryInfo) > 1 and self.listBatteryInfo[1]:
            first_name = self.listBatteryInfo[1][0] if self.listBatteryInfo[1] else ""
            if first_name:
                digit_groups = re.findall(r"(\d+)", first_name)
                if digit_groups:
                    last_group = digit_groups[-1]
                    if len(last_group) >= 8:
                        td = last_group[:8]
                        logger.info("Extracted first 8 digits as date from battery name: %s", td)
                        return td
                    match = re.search(r"(\d{8})", first_name)
                    if match:
                        td = match.group(1)
                        logger.info("Extracted 8-digit date from battery name: %s", td)
                        return td
        logger.warning("Could not extract date from battery name, using default value")
        return "00000000"

    def _build_image_paths_and_titles(self, td: str) -> None:
        """构建图像路径与框线图标题"""
        # 生成动态标题
        try:
            strImageTitle = build_plot_title(
                manufacturer=self.listTestInfo[4],
                spec_type=self.listTestInfo[2],
                spec_method=self.listTestInfo[3],
                batch_code=self.listTestInfo[5],
                capacity=self.listTestInfo[8] if len(self.listTestInfo) > 8 else "",
                temperature=self.listTestInfo[7] if len(self.listTestInfo) > 7 else "",
            )
        except (IndexError, TypeError, ValueError) as e:
            logging.error("An error occurred while getting the title: %s", e)
            strImageTitle = "Default battery analysis plot title"

        # 框线图标题
        self.listBoxplotTitle = []
        if len(strImageTitle) <= 70:
            strBoxplotTitle = strImageTitle
        else:
            strSplit = "A, "
            strBoxplotTitle = (
                strImageTitle.split(strSplit)[0]
                + strSplit
                + "\n"
                + strImageTitle.split(strSplit)[1]
                + strSplit
                + strImageTitle.split(strSplit)[2]
            )

        # 图像路径
        self.listPngPath = []
        self.listSvgPath = []
        for b in range(self.intCurrentLevelNum):
            self.listBoxplotTitle.append(
                f"Useable Capacity over Cutoff Voltage, {self.listCurrentLevel[b]}mA Load\n{strBoxplotTitle}"
            )
            self.listPngPath.append(
                f"{self.strResultPath}/Image_UseableCapacityOverCutoffVoltage{self.listCurrentLevel[b]}mALoad.png"
            )
            self.listSvgPath.append(
                f"{self.strResultPath}/Image_UseableCapacityOverCutoffVoltage{self.listCurrentLevel[b]}mALoad.svg"
            )

        self.strUnfilteredPngPath = (
            f"{self.strResultPath}/Image_UnfilteredLoadVoltageOverCharge.png"
        )
        self.strUnfilteredSvgPath = (
            f"{self.strResultPath}/Image_UnfilteredLoadVoltageOverCharge.svg"
        )
        self.strFilteredPngPath = f"{self.strResultPath}/Image_FilteredLoadVoltageOverCharge.png"
        self.strFilteredSvgPath = f"{self.strResultPath}/Image_FilteredLoadVoltageOverCharge.svg"
        self.strPltName = f"Load Voltage over Charge\n{strImageTitle}"
        self.strInfoImageCsvPath = f"{self.strResultPath}/Info_Image.csv"

        # 颜色
        self.listPltColorType = PLT_COLOR_TYPE
        self.listColorName = COLOR_NAME

    def _build_document_paths(self, td: str) -> None:
        """构建 Excel / Word / CSV 输出路径"""
        safe_temperature = self.listTestInfo[7].replace(":", "_")

        self.strResultXlsxPath = (
            f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.xlsx"
        )
        self.strSampleXlsxPath = (
            f"{self.strResultPath}/Sample_{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.xlsx"
        )

        # Word 模板
        if self.intCurrentLevelNum <= 4:
            template_filename = "Battery Measurement Report of TypeC TypeA_TypeD.docx"
        else:
            template_filename = "Battery Measurement Report of TypeC TypeA_TypeD_MP.docx"

        try:
            pkg_template = (
                importlib.resources.files("battery_analysis") / "templates" / template_filename
            )
            if pkg_template.is_file():
                self.strSampleReportWordPath = str(pkg_template)
                logger.info(
                    "Loading Word template from in-package template directory: %s",
                    self.strSampleReportWordPath,
                )
            else:
                raise FileNotFoundError
        except (TypeError, ModuleNotFoundError, FileNotFoundError):
            self.strSampleReportWordPath = str(
                Path(self.strResultPath) / f"../../0_doc/{template_filename}"
            )
            logger.info(
                "Loading Word template from external 0_doc directory: %s",
                self.strSampleReportWordPath,
            )

        report_name = (
            f"{self.listTestInfo[4]}_{self.listTestInfo[2]}_DC{self.listTestInfo[5]}"
            f"_TD{td}_v{self.listTestInfo[16]}.docx"
        )
        result_dir = Path(self.strResultPath).parent
        self.strReportWordPath = str(result_dir / report_name)

        self.strResultCsvPath = (
            f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.csv"
        )

    def _build_replacements(self) -> None:
        """构建 Word 模板文本替换列表"""
        self.listTextToReplace = [
            "TypeA",
            "TypeB",
            "TypeC",
            "TypeD",
            "TypeE",
            "TypeF",
            "TypeG",
            "StrA",
            "StrB",
            "StrC",
            "StrD",
            "StrF",
        ]
        self.listImageToReplace = ["<<Image_FilteredLoadVoltageOverCharge>>"]
        for i in range(10):
            self.listImageToReplace.append(f"<<Image_UseableCapacityOverCutoffVoltage{i}>>")
            self.listImageToReplace.append(f"<<Title_UseableCapacityOverCutoffVoltage{i}>>")

        # 电池类型匹配
        strBatteryType = match_battery_type(self.listTestInfo[2])

        # 颜色/电流等级字符串
        strStrF = ""
        for c in range(self.intCurrentLevelNum):
            strStrF += f"{self.listColorName[c]}{self.listCurrentLevel[c]}mA, "
        strStrF = strStrF[:-2]

        self.listTestInfoForReplace = [
            self.listTestInfo[2],
            self.listTestInfo[3],
            self.listTestInfo[4],
            self.listTestInfo[5],
            self.listTestInfo[7],
            self.listTestInfo[11],
            strBatteryType,
            None,
            None,
            None,
            None,
            strStrF,
        ]

    # ── 公共方法 ──

    def write(self) -> None:
        """执行完整的写入流程：绘图 → Excel → Word → CSV"""
        from battery_analysis.utils.writers.statistics_utils import (
            compute_list_cpt,
            compute_statistics,
        )

        listCpt = compute_list_cpt(
            self.listBatteryCharge,
            self.intBatteryNum,
            self.intCurrentLevelNum,
            self.intVoltageLevelNum,
        )
        stats = compute_statistics(listCpt, self.intCurrentLevelNum, self.intVoltageLevelNum)

        # 绘制箱线图
        plot_writer.draw_boxplot_and_curves(
            self.intCurrentLevelNum,
            self.intVoltageLevelNum,
            self.listVoltageLevel,
            self.listBoxplotTitle,
            self.listPngPath,
            self.listSvgPath,
            self.strInfoImageCsvPath,
            self.strPltName,
            self.strUnfilteredPngPath,
            self.strUnfilteredSvgPath,
            self.strFilteredPngPath,
            self.strFilteredSvgPath,
            self.listTestInfo,
            self.listPltColorType,
            self.intBatteryNum,
            listCpt,
            int(self.listTestInfo[8]),
        )

        # 委托给专用写入器
        from battery_analysis.utils.writers.csv_writer import CsvWriter
        from battery_analysis.utils.writers.excel_report_writer import ExcelReportWriter
        from battery_analysis.utils.writers.word_report_writer import WordReportWriter

        ExcelReportWriter(self.strResultPath, self.listTestInfo, self.listBatteryInfo).write(
            listCpt, stats
        )
        WordReportWriter(
            self.strResultPath,
            self.listTestInfo,
            self.listBatteryInfo,
            equipment_info=self._equipment_info,
        ).write(listCpt, stats)
        CsvWriter(self.strResultPath, self.listTestInfo, self.listBatteryInfo).write(listCpt, stats)

    # ── 静态工具 ──

    def _get_equip_value(self, dotted_key: str, fallback: str = "") -> str:
        """从 _equipment_info 读取带点号的键"""
        parts = dotted_key.split(".")
        value = self._equipment_info
        try:
            for p in parts:
                value = value[p]
            if isinstance(value, str):
                return value
            if isinstance(value, (list, tuple)):
                return ", ".join(str(v) for v in value)
        except (KeyError, TypeError, IndexError):
            pass
        return fallback


# ── 向后兼容别名 ──────────────────────────────────────────────

XlsxWordWriter = ReportCoordinator
