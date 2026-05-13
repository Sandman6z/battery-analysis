import logging
import traceback

from battery_analysis.utils.writers.excel_report_writer import ExcelReportWriter
from battery_analysis.utils.writers.word_report_writer import WordReportWriter
from battery_analysis.utils.writers.csv_writer import CsvWriter
from battery_analysis.utils.json_writer import JsonWriter


class FileWriter:
    def __init__(self, strResultPath: str, listTestInfo: list, listBatteryInfo: list) -> None:
        self.strErrorLog = ""
        try:
            ExcelReportWriter(strResultPath, listTestInfo, listBatteryInfo).write()
            WordReportWriter(strResultPath, listTestInfo, listBatteryInfo).write()
            CsvWriter(strResultPath, listTestInfo, listBatteryInfo).write()
            JsonWriter(strResultPath, listTestInfo, listBatteryInfo)
        except (IOError, OSError, ImportError, ValueError, TypeError, UnicodeError) as e:
            self.strErrorLog = str(e)
            traceback.print_exc()

    def UFW_GetErrorLog(self) -> str:
        return self.strErrorLog
