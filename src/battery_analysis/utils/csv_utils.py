import csv
from battery_analysis.utils.exception_type import BatteryAnalysisException


def csv_write(_strMessage, csv_writer, buffer, buffer_size, max_buffer_size):
    if type(_strMessage) == str:
        _listTemp = [_strMessage]
        buffer.append(_listTemp)
    elif type(_strMessage) == list:
        _listTemp = []
        for _i in range(len(_strMessage)):
            if _strMessage[_i] != 0:
                _listTemp.append(_strMessage[_i])
            else:
                _listTemp.append("")
        buffer.append(_listTemp)
    else:
        raise BatteryAnalysisException(
            "File: csv_utils.py, Function:csv_write(_message), Error: Unknown _message type")

    buffer_size += 1

    # 当缓冲区达到一定大小或写入特定标记时，批量写入文件
    if buffer_size >= max_buffer_size or (_strMessage and isinstance(_strMessage, str) and "#END HEADER" in _strMessage):
        csv_writer.writerows(buffer)
        buffer.clear()
        buffer_size = 0

    return buffer_size
