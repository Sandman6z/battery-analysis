import logging

from battery_analysis.utils.json_writer import JsonWriter
from battery_analysis.utils.report_coordinator import ReportCoordinator


def write_all(
    strResultPath: str,
    listTestInfo: list,
    listBatteryInfo: list,
    equipment_info: dict | None = None,
) -> None:
    """写入 Excel/Word/CSV/JSON 报告（FileWriter 的简化替代）"""
    # ── 后向兼容：接受 TestInfo 实例 ──────────────────────────
    from battery_analysis.domain.entities.test_info import TestInfo

    if isinstance(listTestInfo, TestInfo):
        listTestInfo = listTestInfo.to_list()

    ReportCoordinator(strResultPath, listTestInfo, listBatteryInfo, equipment_info).write()
    JsonWriter(strResultPath, listTestInfo, listBatteryInfo)


class FileWriter:
    """已弃用 — 请使用 write_all()"""

    def __init__(
        self,
        strResultPath: str,
        listTestInfo: list,
        listBatteryInfo: list,
        equipment_info: dict | None = None,
    ) -> None:
        self.strErrorLog = ""
        try:
            write_all(strResultPath, listTestInfo, listBatteryInfo, equipment_info)
        except Exception as e:
            self.strErrorLog = str(e)
            logging.exception("Failed to write report")

    def UFW_GetErrorLog(self) -> str:
        return self.strErrorLog
