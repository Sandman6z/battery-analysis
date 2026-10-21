"""Word报告写入器

处理电池分析结果的 Word（docx）文件写入。

原 651 行大文件按职责拆分为：

- word_front_matter   版本历史 / 测试信息 / 统计结果
- word_overview       总览内容计算、总览表、段落与表格替换

本文件保留 WordReportWriter 类骨架（__init__ / write）。"""

import importlib
import logging
import os
from pathlib import Path

from docx import Document

from battery_analysis.utils.constants import COLOR_NAME
from battery_analysis.utils.processors.data_utils import generate_current_type_string
from battery_analysis.utils.report_coordinator import match_battery_type, report_filename
from battery_analysis.utils.writers.statistics_utils import (
    compute_list_cpt,
    compute_statistics,
)
from battery_analysis.utils.writers.word_front_matter import WordFrontMatterMixin
from battery_analysis.utils.writers.word_overview import WordOverviewMixin

logger = logging.getLogger(__name__)


class WordReportWriter(WordFrontMatterMixin, WordOverviewMixin):
    """Word报告写入器（骨架类，方法分布在 2 个 Mixin 中）"""

    def __init__(
        self,
        strResultPath: str,
        listTestInfo: list,
        listBatteryInfo: list,
        equipment_info: dict | None = None,
        *,
        test_date: str | None = None,
    ) -> None:
        self._equipment_info = equipment_info or {}
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

        # 路径推导（图像 / Excel / Word 模板 / Word 输出）
        self._init_report_paths(strResultPath, test_date)

        # 替换占位符与电池类型匹配
        self._init_replace_placeholders()

    def _init_report_paths(self, strResultPath: str, test_date: str | None = None) -> None:
        """由结果目录推导图像、Excel、Word 模板与输出路径"""
        # 从strResultPath提取td（日期部分）
        basename = os.path.basename(strResultPath)
        if test_date:
            td = test_date
        elif "_v" in basename:
            td = basename.split("_v")[0]
        else:
            td = "00000000"

        # 图像路径
        self.listPngPath = []
        for b in range(self.intCurrentLevelNum):
            self.listPngPath.append(
                f"{self.strResultPath}/Image_UseableCapacityOver"
                f"CutoffVoltage{self.listCurrentLevel[b]}mALoad.png"
            )
        self.strFilteredPngPath = f"{self.strResultPath}/Image_FilteredLoadVoltageOverCharge.png"

        # Excel路径（用于相对链接）
        safe_temperature = self.listTestInfo[7].replace(":", "_")
        self.strResultXlsxPath = (
            f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.xlsx"
        )
        self.strSampleXlsxPath = (
            f"{self.strResultPath}/Sample_{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.xlsx"
        )

        # Word模板路径
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
                    "Loading Word template from package template directory: %s",
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

        # Word输出路径
        report_name = report_filename(self.listTestInfo, td)
        result_dir = Path(self.strResultPath).parent
        self.strReportWordPath = str(result_dir / report_name)

    def _init_replace_placeholders(self) -> None:
        """构建文本/图片替换占位符与 listTestInfoForReplace"""
        # 文本替换占位符
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

        # strStrF（颜色/电流等级字符串）
        strStrF = ""
        for c in range(self.intCurrentLevelNum):
            strStrF += f"{COLOR_NAME[c]}{self.listCurrentLevel[c]}mA, "
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

    # ── 主入口 ──

    def write(self, list_cpt=None, stats=None) -> None:
        """执行Word报告写入"""
        # 初始化Word文档
        wdReport = Document(self.strSampleReportWordPath)

        # 计算统计值
        if list_cpt is None:
            list_cpt = compute_list_cpt(
                self.listBatteryCharge,
                self.intBatteryNum,
                self.intCurrentLevelNum,
                self.intVoltageLevelNum,
            )
        if stats is None:
            stats = compute_statistics(list_cpt, self.intCurrentLevelNum, self.intVoltageLevelNum)

        # 逐个写入各章节的表格
        tables = {
            "version_history": self._write_version_history(wdReport),
            "test_information": self._write_test_information(wdReport),
            "statistical_results": self._write_statistical_results(wdReport, stats),
        }

        # 准备Overview表内容（会修改 listTestInfoForReplace）
        overview_content = self._prepare_overview_content(wdReport, stats)
        tables["overview"] = self._write_overview_table(wdReport, overview_content, stats)

        # 文本替换、图片插入、表格插入
        self._replace_and_insert(wdReport, tables)

        # 清理并保存文档
        body = wdReport.element.body
        while len(body) > 0:
            last_child = body[-1]
            if last_child.tag.endswith("}p"):
                from docx.text.paragraph import Paragraph

                p = Paragraph(last_child, wdReport.element.body)
                if not p.text.strip():
                    body.remove(last_child)
                else:
                    break
            else:
                break
        wdReport.save(self.strReportWordPath)
        logger.info(
            "Data analysis complete, generated docx report path: %s", self.strReportWordPath
        )
