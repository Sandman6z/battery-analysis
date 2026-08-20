import math
from xlsxwriter.utility import xl_col_to_name


def ws_set_col(_WorkSheet, _intCol: int, _intLength: int, _intSize: int):
    _WorkSheet.set_column(_intCol, _intCol + _intLength - 1, _intSize)


def ws_result_write_data(_intRow, _intCol, _strMessage, _format, ws_result):
    if type(_strMessage) == int or type(_strMessage) == float:
        if not math.isnan(_strMessage) and _strMessage != 0:
            ws_result.write(_intRow, _intCol, _strMessage, _format)
    else:
        ws_result.write(_intRow, _intCol, _strMessage, _format)


def num2letter(_intCol: int) -> str:
    """列序号转列字母（0 → A, 25 → Z, 26 → AA）"""
    return xl_col_to_name(_intCol)
