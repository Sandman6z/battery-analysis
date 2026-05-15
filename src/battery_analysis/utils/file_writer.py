import logging
import traceback

from battery_analysis.utils.xlsx_word_writer import XlsxWordWriter
from battery_analysis.utils.json_writer import JsonWriter


class FileWriter:
    def __init__(self, strResultPath: str, listTestInfo: list, listBatteryInfo: list) -> None:
        self.strErrorLog = ""
        try:
            writer = XlsxWordWriter(strResultPath, listTestInfo, listBatteryInfo)
            writer.write()
            JsonWriter(strResultPath, listTestInfo, listBatteryInfo)
        except (IOError, OSError, ImportError, ValueError, TypeError, UnicodeError) as e:
            self.strErrorLog = str(e)
            traceback.print_exc()

    def UFW_GetErrorLog(self) -> str:
        return self.strErrorLog
