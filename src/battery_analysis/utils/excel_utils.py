import math
from openpyxl.utils import get_column_letter

def ws_set_col(_WorkSheet, _intCol: int, _intLength: int, _intSize: int):
    _WorkSheet.set_column(_intCol, _intCol + _intLength - 1, _intSize)

def ws_result_write_data(_intRow, _intCol, _strMessage, _format, ws_result):
    if type(_strMessage) == int or type(_strMessage) == float:
        if not math.isnan(_strMessage) and _strMessage != 0:
            ws_result.write(_intRow, _intCol, _strMessage, _format)
    else:
        ws_result.write(_intRow, _intCol, _strMessage, _format)

def num2letter(_intCol: int) -> str:
    return get_column_letter(_intCol + 1)
