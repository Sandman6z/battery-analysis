"""Word 报告页眉内容：版本历史 / 测试信息 / 统计结果

从 word_report_writer.py 拆出（大文件拆分重构）。"""

import datetime
import logging

from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_LINE_SPACING
from docx.shared import Cm, Pt

from battery_analysis import __version__
from battery_analysis.utils.writers import word_utils

logger = logging.getLogger(__name__)


class WordFrontMatterMixin:
    """版本历史、测试信息、统计结果三个页眉小节"""

    def _get_equip_value(self, dotted_key: str, fallback: str = "") -> str:
        """从 _equipment_info 字典读取带点号的键"""
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

    # ── 写入Version History表 ──

    def _write_version_history(self, doc):
        """在Word文档中写入版本历史表"""
        table = doc.add_table(9, 4, style="Grid Table 4 Accent 3")
        for r in range(9):
            table.rows[r].height = Cm(0.6)
            for c in range(4):
                if c < 4:
                    table.cell(0, c).width = Cm(2.8)
                cell = table.cell(r, c)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                cell.paragraphs[0].paragraph_format.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell.paragraphs[0].paragraph_format.line_spacing_rules = WD_LINE_SPACING.SINGLE
                cell.paragraphs[0].paragraph_format.space_after = Pt(0)

        headers = ["Date", "Version", "Editor", "Changes"]
        for j, header in enumerate(headers):
            table.cell(0, j).paragraphs[0].add_run(header).font.size = Pt(10)

        version_data = [
            (0, datetime.datetime.now().strftime("%Y.%m.%d"), {"bold": False}),
            (1, "1.0", {}),
            (2, self.listTestInfo[18] if len(self.listTestInfo) > 18 else "", {}),
            (3, "Initial version", {}),
        ]
        for col, content, properties in version_data:
            text = table.cell(1, col).paragraphs[0].add_run(content)
            text.font.size = Pt(10)
            for prop, value in properties.items():
                setattr(text, prop, value)

        return table

    # ── 写入Test Information表 ──

    def _write_test_information(self, doc):
        """在Word文档中写入测试信息表"""
        table = doc.add_table(5, 2, style="Table Grid")
        table.cell(0, 1).width = Cm(10)
        for r in range(5):
            for c in range(2):
                cell = table.cell(r, c)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                cell.paragraphs[0].paragraph_format.alignment = WD_TABLE_ALIGNMENT.LEFT
                cell.paragraphs[0].paragraph_format.line_spacing_rules = WD_LINE_SPACING.SINGLE
                cell.paragraphs[0].paragraph_format.space_after = Pt(0)

        test_info_headers = [
            "Test Equipment",
            "Software Versions",
            "middle Machines",
            "Test Units",
            "Data Processing Platforms",
        ]
        for r, header in enumerate(test_info_headers):
            table.cell(r, 0).paragraphs[0].add_run(header).font.size = Pt(10)

        test_info_data = [
            (0, lambda: self._equipment_info.get("testEquipment", "")),
            (
                1,
                lambda: (
                    f"BTS Server Version: {self._get_equip_value('softwareVersions.btsServer')}\n"
                    f"BTS Client Version: {self._get_equip_value('softwareVersions.btsClient')}\n"
                    f"BTSDA (Data Analysis) Version: {self._get_equip_value('softwareVersions.btsda')}"
                ),
            ),
            (
                2,
                lambda: (
                    f"Model: {self._get_equip_value('middleMachines.model')}\n"
                    f"Hardware Version: {self._get_equip_value('middleMachines.hardwareVersion')}\n"
                    f"Serial Number: {self._get_equip_value('middleMachines.serialNumber')}\n"
                    f"Firmware Version: {self._get_equip_value('middleMachines.firmwareVersion')}\n"
                    f"Device Type: {self._get_equip_value('middleMachines.deviceType')}"
                ),
            ),
            (
                3,
                lambda: (
                    f"Model: {self._get_equip_value('testUnits.model')}\n"
                    f"Hardware Version: {self._get_equip_value('testUnits.hardwareVersion')}\n"
                    f"Firmware Version: {self._get_equip_value('testUnits.firmwareVersion')}"
                ),
            ),
            (4, lambda: f"Battery Analyzer-v{__version__}"),
        ]
        for row, content_func in test_info_data:
            content = content_func()
            table.cell(row, 1).paragraphs[0].add_run(f"{content}").font.size = Pt(10)

        return table

    # ── 写入Statistical Results表 ──

    def _write_statistical_results(self, doc, stats):
        """在Word文档中写入统计结果表"""
        table = doc.add_table(
            self.intCurrentLevelNum + 1, self.intVoltageLevelNum + 1, style="Table Grid"
        )
        for c in range(self.intCurrentLevelNum + 1):
            for v in range(self.intVoltageLevelNum + 1):
                cell = table.cell(c, v)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                cell.paragraphs[0].paragraph_format.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell.paragraphs[0].paragraph_format.line_spacing_rules = WD_LINE_SPACING.SINGLE
                cell.paragraphs[0].paragraph_format.space_after = Pt(0)
                if c == 0 and v == 0:
                    table.rows[c].height = Cm(0.7)
                    table.cell(c, v).width = Cm(3.55)
                    text = cell.paragraphs[0].add_run("Statisticals\nResults")
                    text.font.size = Pt(12)
                    text.bold = True
                    word_utils.table_set_bg_color(cell, "#BFBFBF")
                elif c == 0 and v > 0:
                    table.cell(c, v).width = Cm(3.55)
                    text1 = cell.paragraphs[0].add_run("Cut-off Voltage\n")
                    text1.font.size = Pt(12)
                    text2 = cell.paragraphs[0].add_run(f"{self.listVoltageLevel[v - 1]}V")
                    text2.font.bold = True
                    text2.font.size = Pt(12)
                    word_utils.table_set_bg_color(cell, "#F2F2F2")
                elif c > 0 and v == 0:
                    table.rows[c].height = Cm(2.35)
                    text1 = cell.paragraphs[0].add_run("Pulse Current\n")
                    text1.font.size = Pt(12)
                    text2 = cell.paragraphs[0].add_run(f"{self.listCurrentLevel[c - 1]}mA")
                    text2.font.bold = True
                    text2.font.size = Pt(12)
                    word_utils.table_set_bg_color(cell, "#F2F2F2")
                else:
                    text = cell.paragraphs[0].add_run(
                        f"μ: {round(stats['mean'][c - 1][v - 1])}mAh\n"
                        f"Median: {round(stats['med'][c - 1][v - 1])}mAh\n"
                        f"σ: {round(stats['std'][c - 1][v - 1])}mAh\n"
                        f"μ - 3σ: {round(stats['mm3s'][c - 1][v - 1])}mAh\n"
                        f"μ - 2σ: {round(stats['mm2s'][c - 1][v - 1])}mAh\n"
                        f"μ + 2σ: {round(stats['mp2s'][c - 1][v - 1])}mAh\n"
                        f"μ + 3σ: {round(stats['mp3s'][c - 1][v - 1])}mAh\n"
                        f"Minimum: {round(stats['min'][c - 1][v - 1])}mAh\n"
                        f"Maximum: {round(stats['max'][c - 1][v - 1])}mAh"
                    )
                    if not stats["counts"][c - 1][v - 1]:
                        text.text = "No data (n=0)"
                    else:
                        text.text = f"n={stats['counts'][c - 1][v - 1]}\n{text.text}"
                    text.font.size = Pt(7)
                    cell.paragraphs[0].paragraph_format.line_spacing_rules = WD_LINE_SPACING.EXACTLY
                    cell.paragraphs[0].paragraph_format.line_spacing = Pt(10)

        return table
