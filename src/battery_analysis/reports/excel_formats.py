"""Excel 报告格式构件（单一职责：xlsxwriter 格式字典）

从 excel_report_writer.py 拆出（大文件拆分重构）。"""

import logging

logger = logging.getLogger(__name__)


class ExcelFormatMixin:
    """创建 ExcelReportWriter 用到的全部 xlsxwriter 格式对象"""

    def _create_formats(self, wbResult, wbSample):
        """创建所有XlsxWriter格式对象"""
        fmts = {}

        fmts["result_data"] = wbResult.add_format(
            {
                "font_name": "Microsoft YaHei",
                "font_size": 9,
                "font_color": "black",
                "bold": False,
                "align": "center",
                "valign": "vcenter",
            }
        )
        fmts["result_data_italic"] = wbResult.add_format(
            {
                "font_name": "Microsoft YaHei",
                "font_size": 9,
                "font_color": "black",
                "italic": True,
                "bold": False,
                "align": "center",
                "valign": "vcenter",
            }
        )
        fmts["overview_stat"] = wbResult.add_format(
            {
                "font_name": "Arial Narrow",
                "font_size": 9,
                "font_color": "black",
                "bold": False,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "border": 1,
                "border_color": "#BFBFBF",
            }
        )
        fmts["overview_stat_dark"] = wbResult.add_format(
            {
                "font_name": "Arial Narrow",
                "font_size": 12,
                "font_color": "black",
                "bg_color": "#BFBFBF",
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#BFBFBF",
            }
        )
        fmts["overview_stat_light"] = wbResult.add_format(
            {
                "font_name": "Arial Narrow",
                "font_size": 12,
                "font_color": "black",
                "bg_color": "#F2F2F2",
                "bold": False,
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#BFBFBF",
            }
        )
        fmts["overview_stat_light_bold"] = wbResult.add_format(
            {
                "font_name": "Arial Narrow",
                "font_size": 12,
                "font_color": "black",
                "bg_color": "#F2F2F2",
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#BFBFBF",
            }
        )
        fmts["sample_line"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "black",
            }
        )
        fmts["sample_data"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": False,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "border": 1,
                "border_color": "black",
            }
        )
        fmts["sample_data_bold"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "border": 1,
                "border_color": "black",
            }
        )
        fmts["sample_data_pct"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": False,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "num_format": "0%",
                "border": 1,
                "border_color": "black",
            }
        )
        fmts["sample_data_pct_bold"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "num_format": "0%",
                "border": 1,
                "border_color": "black",
            }
        )
        fmts["sample_data_yellow"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": False,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "border": 1,
                "border_color": "black",
                "bg_color": "#FFFF00",
            }
        )
        fmts["word_line"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": False,
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "black",
            }
        )
        fmts["word_data"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": False,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "border": 1,
                "border_color": "black",
            }
        )
        fmts["word_data_bold"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "border": 1,
                "border_color": "black",
            }
        )
        fmts["word_data_pct"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": False,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "border": 1,
                "border_color": "black",
                "num_format": "0%",
            }
        )
        fmts["word_data_pct_bold"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "border": 1,
                "border_color": "black",
                "num_format": "0%",
            }
        )
        fmts["word_data_yellow"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "black",
                "bold": False,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "border": 1,
                "border_color": "black",
                "bg_color": "#FFFF00",
            }
        )
        fmts["hyperlink"] = wbSample.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "font_color": "#0000FF",
                "underline": True,
                "bold": False,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "border": 1,
                "border_color": "black",
            }
        )
        return fmts
