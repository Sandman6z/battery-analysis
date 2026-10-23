"""样本报告（sample sheet / Word 样本）写入

从 excel_report_writer.py 拆出（大文件拆分重构）。"""

import logging

from battery_analysis.reports import excel_utils
from battery_analysis.utils.report_coordinator import compute_report_content_base

logger = logging.getLogger(__name__)


class ExcelSampleMixin:
    """样本内容准备与样本 Excel / Word 写入"""

    def _prepare_sample_content(self, stats):
        """计算样本表所需的位置参数和内容列表"""
        base = compute_report_content_base(
            self.listCurrentLevel,
            self.intCurrentLevelNum,
            self.listVoltageLevel,
            self.intVoltageLevelNum,
            self.listTestInfo,
            self.listBatteryInfo,
            self.strSampleXlsxPath,
            self.strResultXlsxPath,
            self.strReportWordPath,
            stats,
        )

        intTestDateStartCol = (
            base["intTestProfileStartLine"] + 9 + base["intActualMeasuredCapacityLength"]
        )

        return {
            **base,
            "intTestDateStartCol": intTestDateStartCol,
        }

    def _write_sample_excel(self, wsExcel, sample, stats, fmts):
        """写入Sample文件的Excel工作表"""
        intPosiMaxmA = sample["intPosiMaxmA"]
        intPosi2V25 = sample["intPosi2V25"]
        intTestProfileStartLine = sample["intTestProfileStartLine"]
        intActualMeasuredCapacityLength = sample["intActualMeasuredCapacityLength"]
        intTestDateStartCol = sample["intTestDateStartCol"]
        listStrItems = sample["listStrItems"]
        listStrContent = sample["listStrContent"]

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
            wsExcel, intTestProfileStartLine + 9, intActualMeasuredCapacityLength, 6
        )
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol, 1, 10)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 1, 1, 12)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 2, 1, 18)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 3, 1, 8)
        excel_utils.ws_set_col(wsExcel, intTestDateStartCol + 4, 2, 40)

        # 写入表头行
        for i in range(4):
            wsExcel.merge_range(0, i, 1, i, listStrItems[i], fmts["sample_line"])
        if intTestProfileStartLine == 4:
            wsExcel.merge_range(
                0, intTestProfileStartLine, 1, intTestProfileStartLine, "", fmts["sample_line"]
            )
        wsExcel.write(0, intTestProfileStartLine, listStrItems[4], fmts["sample_line"])
        for i in range(5, 11):
            wsExcel.merge_range(
                0,
                intTestProfileStartLine + (i - 4),
                1,
                intTestProfileStartLine + (i - 4),
                listStrItems[i],
                fmts["sample_line"],
            )
        wsExcel.merge_range(
            0,
            intTestProfileStartLine + 7,
            1,
            intTestProfileStartLine + 8,
            listStrItems[11],
            fmts["sample_line"],
        )
        wsExcel.merge_range(
            0,
            intTestProfileStartLine + 9,
            0,
            intTestDateStartCol - 1,
            listStrItems[13],
            fmts["sample_line"],
        )
        for v in range(self.intVoltageLevelNum):
            wsExcel.merge_range(
                1,
                intTestProfileStartLine + 9 + v * 2,
                1,
                intTestProfileStartLine + 9 + v * 2 + 1,
                f"{self.listVoltageLevel[v]}V",
                fmts["sample_line"],
            )
        for i in range(14, 20):
            wsExcel.merge_range(
                0,
                intTestDateStartCol + (i - 14),
                1,
                intTestDateStartCol + (i - 14),
                listStrItems[i],
                fmts["sample_line"],
            )

        # 写入内容行
        wsExcel.write(2, 0, listStrContent[0], fmts["sample_data"])
        wsExcel.write(2, 1, listStrContent[1], fmts["sample_data"])
        wsExcel.write(2, 2, listStrContent[2], fmts["sample_data"])
        wsExcel.write(2, 3, listStrContent[3], fmts["sample_data"])
        if len(listStrContent[4].split("\\")) == 1:
            wsExcel.write(2, intTestProfileStartLine, listStrContent[4], fmts["sample_data"])
        else:
            url_path = listStrContent[4].replace("\\", "/")
            wsExcel.write_url(
                2,
                intTestProfileStartLine,
                f"file:///{url_path}",
                fmts["hyperlink"],
                string=listStrContent[4].split("\\")[-1],
            )
        for i in range(5, 13):
            wsExcel.write(
                2, intTestProfileStartLine + (i - 4), listStrContent[i], fmts["sample_data"]
            )

        # 电压等级容量列
        for v in range(self.intVoltageLevelNum):
            fmt_val = fmts["sample_data_bold"] if v == intPosi2V25 else fmts["sample_data"]
            fmt_pct = fmts["sample_data_pct_bold"] if v == intPosi2V25 else fmts["sample_data_pct"]
            col = intTestProfileStartLine + 9 + v * 2
            if stats.get("counts", [[1] * self.intVoltageLevelNum] * self.intCurrentLevelNum)[intPosiMaxmA][v]:
                wsExcel.write(2, col, f"{round(stats['mm2s'][intPosiMaxmA][v], 2)}", fmt_val)
                wsExcel.write_formula(
                    f"{excel_utils.num2letter(col + 1)}3",
                    f"=TRUNC({excel_utils.num2letter(col)}3/"
                    f"{excel_utils.num2letter(intTestProfileStartLine + 6)}3, 2)",
                    fmt_pct,
                )
            else:
                # 缺数据格写原因，不写 0，也不留下会报 #VALUE! 的公式
                wsExcel.write(2, col, "No data (n=0)", fmt_val)
                wsExcel.write(f"{excel_utils.num2letter(col + 1)}3", "", fmt_pct)

        # 日期/结果列
        for i in range(4):
            fmt = fmts["sample_data_yellow"] if i == 3 else fmts["sample_data"]
            wsExcel.write(2, intTestDateStartCol + i, listStrContent[14 + i], fmt)

        wsExcel.write(2, intTestDateStartCol + 5, listStrContent[19], fmts["sample_data"])

        # 测试结果超链接
        url_path = listStrContent[18].replace("\\", "/")
        wsExcel.write_url(
            2,
            intTestDateStartCol + 4,
            f"file:///{url_path}",
            fmts["hyperlink"],
            string=listStrContent[18].split("\\")[-1],
        )

    def _write_sample_word(self, wsWord, sample, stats, fmts):
        """写入Sample文件的Word工作表"""
        intPosiMaxmA = sample["intPosiMaxmA"]
        intPosi2V25 = sample["intPosi2V25"]
        intTestProfileStartLine = sample["intTestProfileStartLine"]
        intActualMeasuredCapacityLength = sample["intActualMeasuredCapacityLength"]
        listStrItems = sample["listStrItems"]
        listStrContent = sample["listStrContent"]
        intTestDateStartRow = intTestProfileStartLine + 11

        # 设置列宽
        excel_utils.ws_set_col(wsWord, 0, 1, 30)
        excel_utils.ws_set_col(wsWord, 1, intActualMeasuredCapacityLength, 3)

        # 写入表头
        for i in range(4):
            wsWord.write(i, 0, listStrItems[i], fmts["word_line"])
        for i in range(4, 12):
            wsWord.write(intTestProfileStartLine + (i - 4), 0, listStrItems[i], fmts["word_line"])
        wsWord.merge_range(
            intTestProfileStartLine + 8,
            0,
            intTestProfileStartLine + 10,
            0,
            listStrItems[13],
            fmts["word_line"],
        )
        for i in range(6):
            wsWord.write(intTestDateStartRow + i, 0, listStrItems[14 + i], fmts["word_line"])

        # 写入内容
        for i in range(4):
            wsWord.merge_range(
                i, 1, i, intActualMeasuredCapacityLength, listStrContent[i], fmts["word_data"]
            )
        if intTestProfileStartLine == 4:
            wsWord.merge_range(
                intTestProfileStartLine,
                1,
                intTestProfileStartLine,
                intActualMeasuredCapacityLength,
                "",
                fmts["word_data"],
            )
        if len(listStrContent[4].split("\\")) == 1:
            wsWord.write(intTestProfileStartLine, 1, listStrContent[4], fmts["word_data"])
        else:
            url_path = listStrContent[4].replace("\\", "/")
            wsWord.write_url(
                intTestProfileStartLine,
                1,
                f"file:///{url_path}",
                fmts["hyperlink"],
                string=listStrContent[4].split("\\")[-1],
            )
        for i in range(5, 11):
            wsWord.merge_range(
                intTestProfileStartLine + (i - 4),
                1,
                intTestProfileStartLine + (i - 4),
                intActualMeasuredCapacityLength,
                listStrContent[i],
                fmts["word_data"],
            )
        wsWord.merge_range(
            intTestProfileStartLine + 7,
            1,
            intTestProfileStartLine + 7,
            int(intActualMeasuredCapacityLength / 2),
            listStrContent[11],
            fmts["word_data"],
        )
        wsWord.merge_range(
            intTestProfileStartLine + 7,
            int(intActualMeasuredCapacityLength / 2) + 1,
            intTestProfileStartLine + 7,
            intActualMeasuredCapacityLength,
            listStrContent[12],
            fmts["word_data"],
        )

        for v in range(self.intVoltageLevelNum):
            is_25v = v == intPosi2V25
            fmt_val = fmts["word_data_bold"] if is_25v else fmts["word_data"]
            fmt_pct = fmts["word_data_pct_bold"] if is_25v else fmts["word_data_pct"]
            col = 1 + v * 2
            wsWord.merge_range(
                intTestProfileStartLine + 8,
                col,
                intTestProfileStartLine + 8,
                col + 1,
                f"{self.listVoltageLevel[v]}V",
                fmt_val,
            )
            wsWord.merge_range(
                intTestProfileStartLine + 9,
                col,
                intTestProfileStartLine + 9,
                col + 1,
                "No data (n=0)"
                if not stats.get("counts", [[1] * self.intVoltageLevelNum] * self.intCurrentLevelNum)[intPosiMaxmA][v]
                else f"{round(stats['mm2s'][intPosiMaxmA][v], 2)}",
                fmt_val,
            )
            wsWord.merge_range(
                intTestProfileStartLine + 10,
                col,
                intTestProfileStartLine + 10,
                col + 1,
                "",
                fmt_val,
            )
            wsWord.write_formula(
                f"{excel_utils.num2letter(col)}{intTestProfileStartLine + 11}",
                f"=TRUNC({excel_utils.num2letter(col)}{intTestProfileStartLine + 10}/"
                f"B{intTestProfileStartLine + 7}, 2)",
                fmt_pct,
            )

        # 日期/结果行
        wsWord.merge_range(
            intTestDateStartRow,
            1,
            intTestDateStartRow,
            intActualMeasuredCapacityLength,
            listStrContent[14],
            fmts["word_data"],
        )
        wsWord.merge_range(
            intTestDateStartRow + 1,
            1,
            intTestDateStartRow + 1,
            intActualMeasuredCapacityLength,
            listStrContent[15],
            fmts["word_data"],
        )
        wsWord.merge_range(
            intTestDateStartRow + 2,
            1,
            intTestDateStartRow + 2,
            intActualMeasuredCapacityLength,
            listStrContent[16],
            fmts["word_data"],
        )
        wsWord.merge_range(
            intTestDateStartRow + 3,
            1,
            intTestDateStartRow + 3,
            intActualMeasuredCapacityLength,
            listStrContent[17],
            fmts["word_data_yellow"],
        )
        url_path = listStrContent[18].replace("\\", "/")
        display_text = listStrContent[18].split("\\")[-1]
        wsWord.merge_range(
            intTestDateStartRow + 4,
            1,
            intTestDateStartRow + 4,
            intActualMeasuredCapacityLength,
            display_text,
            fmts["word_data"],
        )
        wsWord.write_url(
            intTestDateStartRow + 4,
            1,
            f"file:///{url_path}",
            fmts["hyperlink"],
            string=display_text,
        )
        wsWord.merge_range(
            intTestDateStartRow + 5,
            1,
            intTestDateStartRow + 5,
            intActualMeasuredCapacityLength,
            listStrContent[19],
            fmts["word_data"],
        )
