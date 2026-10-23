"""Excel报告写入器

处理电池分析结果的Excel（xlsx）文件写入，包括主结果表和样本表。

原 906 行大文件按职责拆分为：

- excel_formats    各类 xlsxwriter 格式对象
- excel_overview   主结果表写入
- excel_sample     样本 Excel / Word 写入

本文件保留 ExcelReportWriter 类骨架（__init__ / write）与向后兼容别名。"""

import logging
import os
from pathlib import Path

import xlsxwriter as xwt

from battery_analysis.analysis.data_utils import generate_current_type_string
from battery_analysis.reports.excel_formats import ExcelFormatMixin
from battery_analysis.reports.excel_overview import ExcelOverviewMixin
from battery_analysis.reports.excel_sample import ExcelSampleMixin
from battery_analysis.reports.statistics_utils import (
    compute_list_cpt,
    compute_statistics,
)
from battery_analysis.utils.quality_requirements import (
    build_expectations,
    evaluate_expectations,
)
from battery_analysis.utils.report_coordinator import report_filename

logger = logging.getLogger(__name__)

# 向后兼容别名
_compute_list_cpt = compute_list_cpt
_compute_statistics = compute_statistics


class ExcelReportWriter(ExcelFormatMixin, ExcelOverviewMixin, ExcelSampleMixin):
    """Excel 报告写入器（骨架类，方法分布在 3 个 Mixin 中）"""

    def __init__(self, strResultPath: str, listTestInfo: list, listBatteryInfo: list, *, test_date: str | None = None) -> None:
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

        # 图像路径列表（用于插入到Excel）
        self.listPngPath = []
        for b in range(self.intCurrentLevelNum):
            self.listPngPath.append(
                f"{self.strResultPath}/Image_UseableCapacityOver"
                f"CutoffVoltage{self.listCurrentLevel[b]}mALoad.png"
            )

        # Excel文件路径
        safe_temperature = self.listTestInfo[7].replace(":", "_")
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
        if test_date:
            td = test_date
        elif "_v" in basename:
            td = basename.split("_v")[0]
        else:
            td = "00000000"
        report_name = report_filename(self.listTestInfo, td)
        result_dir = Path(self.strResultPath).parent
        self.strReportWordPath = str(result_dir / report_name)

    def write(self, list_cpt=None, stats=None) -> None:
        """执行Excel报告写入"""
        # 创建工作簿和工作表
        wbResult = xwt.Workbook(self.strResultXlsxPath)
        wsOverview = wbResult.add_worksheet("overview")
        wsResult = wbResult.add_worksheet("result")
        wbSample = xwt.Workbook(self.strSampleXlsxPath)
        wsWord = wbSample.add_worksheet("word")
        wsExcel = wbSample.add_worksheet("excel")
        try:
            # 创建格式
            fmts = self._create_formats(wbResult, wbSample)

            # 写入Overview表头
            # 注：xlsxwriter.add_worksheet 失败时抛异常而非返回 None，
            # 故不再做 `wsOverview is None` / `wsResult is None` 判断（不可达）
            self._write_overview_header(wsOverview)

            # 写入result表列名
            self._write_result_columns(wsResult, fmts)

            # 写入电池数据
            self._write_battery_data(wsResult, fmts)

            # 计算统计值
            if list_cpt is None:
                list_cpt = _compute_list_cpt(
                    self.listBatteryCharge,
                    self.intBatteryNum,
                    self.intCurrentLevelNum,
                    self.intVoltageLevelNum,
                )
            if stats is None:
                stats = _compute_statistics(
                    list_cpt, self.intCurrentLevelNum, self.intVoltageLevelNum
                )

            # 写入统计值、图像、Overview统计表
            self._write_result_statistics(wsResult, stats, fmts)
            self._insert_images(wsResult)
            # §6.2.11 合格判定：仅对 PDF 指定的 (脉冲电流, 截止电压) 格标注
            expectations = build_expectations(self.listTestInfo)
            verdicts = evaluate_expectations(
                stats,
                self.listCurrentLevel,
                self.listVoltageLevel,
                expectations,
            )
            self._write_overview_statistics(wsOverview, stats, fmts, verdicts=verdicts)

            # 准备样本表内容并写入
            sample = self._prepare_sample_content(stats)
            self._write_sample_excel(wsExcel, sample, stats, fmts)
            self._write_sample_word(wsWord, sample, stats, fmts)
        finally:
            # 关闭工作簿：无论写入是否失败都必须关闭，避免留下损坏/未写出的 xlsx
            wbResult.close()
            wbSample.close()
