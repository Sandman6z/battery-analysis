"""Excel 主结果表（overview sheet）写入

从 excel_report_writer.py 拆出（大文件拆分重构）。"""

import logging

from battery_analysis import __version__
from battery_analysis.analysis.data_utils import missing_reason
from battery_analysis.reports import excel_utils
from battery_analysis.utils.quality_requirements import (
    expected_requirement_text,
    verdict_map,
)

logger = logging.getLogger(__name__)


class ExcelOverviewMixin:
    """主结果表写入：表头、结果列、电池数据、统计、插图"""

    def _write_overview_header(self, wsOverview):
        """写入Overview表的文件头信息"""
        header_info = [
            "#BEGIN HEADER",
            "#PULSE DISCHARGE",
            "#BATTERY CHARACTERISTICS",
            f"#Start Time: {self.listBatteryInfo[2][0]}",
            f"#End Time: {self.listBatteryInfo[2][1]}",
            f"#Battery Type: {self.listTestInfo[2]} {self.listTestInfo[3]}",
            f"#Battery Manufacturer: {self.listTestInfo[4]}",
            f"#Battery Date Code: {self.listTestInfo[5]}",
            f"#Temperature: {self.listTestInfo[6]}",
            f"#Test Profile: {self.listTestInfo[13]}",
            f"#Version: v{__version__}",
            "#END HEADER",
        ]
        for i, info in enumerate(header_info):
            wsOverview.write(i, 0, info)

    def _write_result_columns(self, wsResult, fmts):
        """写入result工作表的列标题行"""
        excel_utils.ws_set_col(
            wsResult, 0, self.intCurrentLevelNum * (2 + self.intVoltageLevelNum) + 1, 10
        )
        excel_utils.ws_set_col(wsResult, 0, 1, 20)
        wsResult.write(2, 0, "Battery", fmts["result_data"])
        wsResult.write(4 + self.intBatteryNum, 0, "Mean(μ)", fmts["result_data_italic"])
        wsResult.write(5 + self.intBatteryNum, 0, "Median", fmts["result_data_italic"])
        wsResult.write(6 + self.intBatteryNum, 0, "Std. Var.(σ)", fmts["result_data_italic"])
        wsResult.write(7 + self.intBatteryNum, 0, "μ-3σ", fmts["result_data_italic"])
        wsResult.write(8 + self.intBatteryNum, 0, "μ-2σ", fmts["result_data_italic"])
        wsResult.write(9 + self.intBatteryNum, 0, "μ+2σ", fmts["result_data_italic"])
        wsResult.write(10 + self.intBatteryNum, 0, "μ+3σ", fmts["result_data_italic"])
        wsResult.write(11 + self.intBatteryNum, 0, "Minimum", fmts["result_data_italic"])
        wsResult.write(12 + self.intBatteryNum, 0, "Maximum", fmts["result_data_italic"])
        for c in range(self.intCurrentLevelNum):
            wsResult.write(
                1,
                1 + c * (2 + self.intVoltageLevelNum),
                f"{self.listCurrentLevel[c]}mA",
                fmts["result_data"],
            )
            wsResult.merge_range(
                1,
                2 + c * (2 + self.intVoltageLevelNum),
                1,
                (c + 1) * (2 + self.intVoltageLevelNum) - 1,
                "Voltage",
                fmts["result_data"],
            )
            for v in range(self.intVoltageLevelNum):
                wsResult.write(
                    2,
                    2 + c * (2 + self.intVoltageLevelNum) + v,
                    f"{self.listVoltageLevel[v]}V",
                    fmts["result_data"],
                )

    def _write_battery_data(self, wsResult, fmts):
        """将每块电池的容量数据写入result表"""
        for b in range(self.intBatteryNum):
            excel_utils.ws_result_write_data(
                3 + b, 0, self.listBatteryName[b], fmts["result_data"], wsResult
            )
            i = 0
            for c in range(self.intCurrentLevelNum):
                for v in range(self.intVoltageLevelNum):
                    excel_utils.ws_result_write_data(
                        3 + b,
                        2 + c * (2 + self.intVoltageLevelNum) + v,
                        self.listBatteryCharge[b][i] if self.listBatteryCharge[b][i] is not None else missing_reason(self.listBatteryInfo, b),
                        fmts["result_data"],
                        wsResult,
                    )
                    i += 1

    def _write_result_statistics(self, wsResult, stats, fmts):
        """将统计值（均值、中位数、标准差等）写入result表"""
        counts = stats.get("counts", [[1] * self.intVoltageLevelNum for _ in range(self.intCurrentLevelNum)])
        for c in range(self.intCurrentLevelNum):
            for v in range(self.intVoltageLevelNum):
                stat_rows = [
                    (4, "mean"),
                    (5, "med"),
                    (6, "std"),
                    (7, "mm3s"),
                    (8, "mm2s"),
                    (9, "mp2s"),
                    (10, "mp3s"),
                    (11, "min"),
                    (12, "max"),
                ]
                for row_offset, key in stat_rows:
                    excel_utils.ws_result_write_data(
                        row_offset + self.intBatteryNum,
                        2 + c * (2 + self.intVoltageLevelNum) + v,
                        round(stats[key][c][v], 5) if counts[c][v] else "No data (n=0)",
                        fmts["result_data"],
                        wsResult,
                    )

    def _insert_images(self, wsResult):
        """将容量图插入result表"""
        for c in range(self.intCurrentLevelNum):
            wsResult.insert_image(
                14 + self.intBatteryNum,
                1 + c * (2 + self.intVoltageLevelNum),
                self.listPngPath[c],
                {
                    "x_scale": ((2 + self.intVoltageLevelNum) * 2 - 1) / 16,
                    "y_scale": ((2 + self.intVoltageLevelNum) * 2 - 1) / 16,
                },
            )

    def _write_overview_statistics(
        self,
        wsOverview,
        stats,
        fmts,
        wsOverviewStatisticalStartLine=13,
        verdicts=None,
    ):
        """写入Overview工作表中的统计结果

        Args:
            verdicts: §6.2.11 合格判定结果（可为 None）；命中的
                (脉冲电流, 截止电压) 格在统计文本后追加期望值与 Pass/Fail
                标注，仅文本追加、不改变表格布局。
        """
        vmap = verdict_map(verdicts)
        counts = stats.get("counts", [[1] * self.intVoltageLevelNum for _ in range(self.intCurrentLevelNum)])
        wsOverview.write(
            wsOverviewStatisticalStartLine, 0, "Statisticals Results", fmts["overview_stat_dark"]
        )
        wsOverview.set_row(wsOverviewStatisticalStartLine, 20)
        wsOverview.set_column(0, 0, 18)
        for v in range(1, self.intVoltageLevelNum + 1):
            wsOverview.set_column(v, v, 18)
            wsOverview.write_rich_string(
                wsOverviewStatisticalStartLine,
                v,
                fmts["overview_stat_light"],
                "Cut-off Voltage ",
                fmts["overview_stat_light_bold"],
                f"{self.listVoltageLevel[v - 1]}V",
                fmts["overview_stat_light"],
            )
        for c in range(1, self.intCurrentLevelNum + 1):
            row_has_verdict = any(verdict.current_index == c - 1 for verdict in vmap.values())
            wsOverview.set_row(wsOverviewStatisticalStartLine + c, 140 if row_has_verdict else 120)
            wsOverview.write_rich_string(
                wsOverviewStatisticalStartLine + c,
                0,
                fmts["overview_stat_light"],
                "Pulse Current ",
                fmts["overview_stat_light_bold"],
                f"{self.listCurrentLevel[c - 1]}mA",
                fmts["overview_stat_light"],
            )
            for v in range(1, self.intVoltageLevelNum + 1):
                cell_text = (
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
                if not counts[c - 1][v - 1]:
                    cell_text = "No data"
                cell_verdict = vmap.get((c - 1, v - 1))
                if cell_verdict is not None:
                    # §6.2.11：该格为 PDF 指定的判定格，追加期望与结论
                    cell_text += "\n" + expected_requirement_text(cell_verdict)
                wsOverview.write(
                    wsOverviewStatisticalStartLine + c,
                    v,
                    cell_text,
                    fmts["overview_stat"],
                )
