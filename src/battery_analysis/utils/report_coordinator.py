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

from battery_analysis.analysis.data_utils import (
    build_plot_title,
    generate_current_type_string,
)
from battery_analysis.reports import plot_writer
from battery_analysis.utils.battery_classifier import battery_type_code
from battery_analysis.utils.constants import (
    CN_FONT_LIST,
    COLOR_NAME,
    PLT_COLOR_TYPE,
)
from battery_analysis.utils.quality_requirements import (
    _EXPECTATION_CUTOFF_V,
    _MIN_EPSILON,
    Expectation,
    build_expectations,
    evaluate_expectations,
    format_failure_remarks,
)
from battery_analysis.utils.readers.date_parser import parse_test_date

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = CN_FONT_LIST
plt.rcParams["axes.unicode_minus"] = False


logger = logging.getLogger(__name__)

# ── 共享常量 ──────────────────────────────────────────────────


def report_filename(test_info: list, test_date: str) -> str:
    """既有 Word 命名契约：DC 为批次码，TD 为本次确定的测试日期。"""
    return (
        f"{test_info[4]}_{test_info[2]}_DC{test_info[5]}"
        f"_TD{test_date}_v{test_info[16]}.docx"
    )


def match_battery_type(test_info_type: str) -> str:
    """从测试信息中匹配电池类型，返回标准类型名称"""
    return battery_type_code(test_info_type)


# ── 共享报告内容计算 ──────────────────────────────────────────
# ExcelReportWriter._prepare_sample_content 与
# WordReportWriter._prepare_overview_content 约 90% 相同，
# 本函数提取公共部分，差异由各调用方自行处理。


def _require_positive_int(value, label: str) -> int:
    """解析正整数报告字段；空值/非法值时抛带字段名的 ValueError。

    错误信息由 analysis_worker 捕获，经 "Report Generation Error" 弹窗展示，
    字段名帮助用户定位到对应输入框（如 Required Useable Capacity）。
    """
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a positive integer, got {value!r}") from None
    if parsed <= 0:
        raise ValueError(f"{label} must be a positive integer, got {value!r}")
    return parsed


def _capacity_failure_remarks(threshold, minimum, statistic, qnom, cutoff, sample_ok, stat_ok):
    """Keep the historical report wording; detailed criteria belong in the audit log."""
    remarks = []
    if not stat_ok:
        remarks.append(
            f"The expected usable Q(stat) should be more than {int(100 * threshold / qnom)}%, "
            f"while the actual measured minimum capacity to {cutoff:g}V is "
            f"{math.floor(100 * statistic / qnom)}%."
        )
    if not sample_ok:
        remarks.append(
            f"The minimum sample capacity should be at least {round(threshold)}mAh, "
            f"while the actual measured minimum capacity to {cutoff:g}V is {round(minimum)}mAh."
        )
    return " ".join(remarks)


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

    # 2.25V 电压位置（P1：容差匹配，避免 float == 2.25 精确比较静默失配；
    # 未命中时回退 index 0，技术细节记日志，Remarks 只说明缺失的测量）
    intPosi2V25 = 0
    found_225v = False
    for v in range(intVoltageLevelNum):
        try:
            if abs(float(listVoltageLevel[v]) - _EXPECTATION_CUTOFF_V) < 1e-6:
                intPosi2V25 = v
                found_225v = True
                break
        except (TypeError, ValueError):
            continue
    if not found_225v:
        logger.warning(
            "2.25V cutoff level not found in voltage levels %s; "
            "falling back to index %d (%s V) for legacy positioning",
            listVoltageLevel,
            intPosi2V25,
            listVoltageLevel[intPosi2V25] if intVoltageLevelNum else "n/a",
        )

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
    # 空值/非正整数 → 抛带字段名的 ValueError，由 Report Generation Error 弹窗定位
    intRequiredCapacity = _require_positive_int(listTestInfo[17], "Required Useable Capacity")
    intQnomCapacity = _require_positive_int(listTestInfo[9], "Calculated Capacity")
    intPassRate = float(intRequiredCapacity / intQnomCapacity)
    strRequiredUseableCapacityPercentage = f"{int(100 * intPassRate)}%"

    [sy, sm, sd] = listBatteryInfo[2][0].split(" ")[0].split("-")
    [ey, em, ed] = listBatteryInfo[2][1].split(" ")[0].split("-")

    strRelResultPath = os.path.relpath(strResultXlsxPath, os.path.dirname(strReportWordPath))

    listMM2S = stats["mm2s"]

    # ── §6.2.11 合格判定（BatteryQualityRequirements_v2.3）──────
    # 仅对 PDF 指定的 (脉冲电流, 截止电压) 格判定：
    #   ① 所有单样本 ≥ 期望可用容量；② µ-2σ > 期望（严格）。
    # 配置的 9 档超集（2.6V/2.1V 等非 PDF 列）不参与判定。
    # 期望格派生失败时回退到历史判定位置（最高脉冲电流 × 2.25V）。
    expectations = build_expectations(listTestInfo)
    if not expectations:
        expectations = [
            Expectation(
                current_ma=float(listCurrentLevel[intPosiMaxmA]),
                # P1：固定 2.25V，不用 intPosi2V25 对应的实际电压——
                # 若 2.25V 不在档位中，这里会取到 2.6V 并在错误格上执行双条件
                cutoff_v=_EXPECTATION_CUTOFF_V,
                threshold_mah=float(intRequiredCapacity),
                source="legacy",
            )
        ]
    verdicts = evaluate_expectations(stats, listCurrentLevel, listVoltageLevel, expectations)

    if verdicts:
        # P3 三态聚合：failed → Fail；仅 no_data → Incomplete（绝不聚合 Pass）；否则 Pass
        no_data = [v for v in verdicts if v.no_data]
        failed = [v for v in verdicts if not v.passed and not v.no_data]
        if failed:
            strResult = "Fail"
        elif no_data:
            strResult = "Incomplete"
        else:
            strResult = "Pass"
        remarks = []
        for verdict in verdicts:
            if verdict.no_data:
                remarks.extend(verdict.failure_texts())
            elif not verdict.passed:
                text = _capacity_failure_remarks(
                    verdict.expectation.threshold_mah, verdict.minimum, verdict.mu2sigma,
                    intQnomCapacity, verdict.expectation.cutoff_v,
                    verdict.sample_ok, verdict.stat_ok,
                )
                if len(expectations) > 1:
                    text = f"{verdict.expectation.label}: {text}"
                remarks.append(text)
        strRemarks = " ".join(remarks) or "OK"
        logger.info("Report judgment audit: %s", format_failure_remarks(verdicts))
        single_samples = [v for v in verdicts if v.sample_count == 1]
        if single_samples:
            labels = ", ".join(v.expectation.label for v in single_samples)
            logger.info("Report judgment audit: single sample at %s: σ=0, µ-2σ equals mean", labels)
    else:
        # 期望格不在实测档位中：保留原有单点判定（安全网，行为与历史一致）。
        # P2：保留最小值判据，回退路径只在日志中记录。
        legacy_min = float(stats["min"][intPosiMaxmA][intPosi2V25])
        legacy_stat_ok = (
            listMM2S[intPosiMaxmA][intPosi2V25] / intQnomCapacity >= intPassRate
        )
        legacy_sample_ok = legacy_min >= intRequiredCapacity - _MIN_EPSILON
        logger.warning(
            "PDF expectation cell(s) %s not present in measured levels "
            "(currents=%s, voltages=%s); using legacy single-point verdict "
            "at %s mA / %s V",
            [e.label for e in expectations],
            listCurrentLevel,
            listVoltageLevel,
            listCurrentLevel[intPosiMaxmA],
            listVoltageLevel[intPosi2V25],
        )
        if legacy_stat_ok and legacy_sample_ok:
            strResult = "Pass"
            strRemarks = "OK"
        else:
            strResult = "Fail"
            strRemarks = _capacity_failure_remarks(
                intRequiredCapacity, legacy_min, listMM2S[intPosiMaxmA][intPosi2V25],
                intQnomCapacity, float(listVoltageLevel[intPosi2V25]),
                legacy_sample_ok, legacy_stat_ok,
            )

    measured_expectations = {v.expectation for v in verdicts}
    missing_expectations = [e for e in expectations if e not in measured_expectations]
    if missing_expectations:
        missing_text = "; ".join(
            f"no measured samples at {e.label}: data incomplete, retest required"
            for e in missing_expectations
        )
        strRemarks = missing_text if strRemarks == "OK" else f"{strRemarks} {missing_text}"

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
        result_dir: str | None = None,
        test_date: str | None = None,
    ) -> None:
        # ── 后向兼容：接受 TestInfo 实例 ──────────────────────────
        from battery_analysis.domain.test_info import TestInfo

        if isinstance(listTestInfo, TestInfo):
            listTestInfo = listTestInfo.to_list()

        self.listTestInfo = listTestInfo
        self.listBatteryInfo = listBatteryInfo
        self._equipment_info = equipment_info or {}

        # 提取测试日期（YYYYMMDD）
        td = test_date or self._extract_test_date()
        self.test_date = td

        # 构建输出路径
        self.strResultPath = result_dir or os.path.join(strResultPath, f"{td}_v{listTestInfo[16]}")
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
                digit_groups: list[str] = re.findall(r"(\d+)", first_name)
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

        report_name = report_filename(self.listTestInfo, td)
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
        strBatteryType = match_battery_type(self.listTestInfo[0])

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
        from battery_analysis.reports.statistics_utils import (
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
        from battery_analysis.reports.csv_writer import CsvWriter
        from battery_analysis.reports.excel_report_writer import ExcelReportWriter
        from battery_analysis.reports.word_report_writer import WordReportWriter

        ExcelReportWriter(self.strResultPath, self.listTestInfo, self.listBatteryInfo, test_date=self.test_date).write(
            listCpt, stats
        )
        WordReportWriter(
            self.strResultPath,
            self.listTestInfo,
            self.listBatteryInfo,
            equipment_info=self._equipment_info,
            test_date=self.test_date,
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
