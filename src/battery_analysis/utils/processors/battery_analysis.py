"""
电池分析核心模块

负责电池分析数据的读取、并行处理和结果输出。
编排以下模块完成完整分析流程：
  - file_finder: 目录扫描与自然排序
  - readers.xlsx_reader: Excel 文件读取
  - processors.pulse_detector: 脉冲行检测
  - processors.pulse_matcher: 电流/电压等级匹配
  - processors.charge_calculator: 电荷量计算
  - writers.info_csv_writer: 绘图用 CSV/JSON 写入
"""

import concurrent.futures
import datetime
import logging
import multiprocessing
import sys
import traceback

from battery_analysis.utils.exceptions import BatteryAnalysisException
from battery_analysis.utils.file_finder import scan_sorted_xlsx
from battery_analysis.utils.processors.charge_calculator import ChargeCalculator
from battery_analysis.utils.processors.data_utils import generate_current_type_string
from battery_analysis.utils.processors.pulse_detector import detect_pulse_rows
from battery_analysis.utils.processors.pulse_matcher import match_pulse_levels
from battery_analysis.utils.readers.xlsx_reader import (
    extract_test_date_from_xls,
    read_xlsx_sheets,
)
from battery_analysis.utils.writers.info_csv_writer import (
    write_info_csv,
    write_info_json,
)

if __name__ == "__main__":
    pass

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")


class BatteryAnalysis:
    """电池分析编排器

    职责：读取指定目录下的所有 xlsx 文件，并行分析脉冲数据，
    计算电荷量，输出 CSV/JSON 结果供图表工具使用。
    """

    def __init__(
        self, strInDataXlsxDir: str, strResultPath: str, listTestInfo: list, progress_callback=None
    ) -> None:
        # ── 后向兼容：接受 TestInfo 实例 ──────────────────────────
        from battery_analysis.domain.entities.test_info import TestInfo

        if isinstance(listTestInfo, TestInfo):
            listTestInfo = listTestInfo.to_list()

        # ── 输入验证 ──────────────────────────────────────────────
        if len(listTestInfo) < 19:
            logging.error(
                "Test info list format error: missing required information. "
                "Need at least 19 elements, but only found %d",
                len(listTestInfo),
            )
            raise BatteryAnalysisException(
                f"Test information list format error: missing required information. "
                f"Expected at least 19 elements, but found {len(listTestInfo)}"
            )

        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]

        if not self.listCurrentLevel:
            logging.error("Current level list is empty")
            raise BatteryAnalysisException("Current level list is empty")

        if not self.listVoltageLevel:
            logging.error("Voltage level list is empty")
            raise BatteryAnalysisException("Voltage level list is empty")

        self.strFileCurrentType = generate_current_type_string(self.listCurrentLevel)

        # ── 路径设置 ──────────────────────────────────────────────
        self.strInDataXlsxDir = f"{strInDataXlsxDir}/"
        self.strResultPath = strResultPath
        safe_temperature = listTestInfo[7].replace(":", "_")
        self.strResultLogTxt = (
            f"{strResultPath}/V{listTestInfo[16]}/"
            f"{listTestInfo[4]}_{listTestInfo[2]}_{listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.txt"
        )

        # ── 结果容器 ──────────────────────────────────────────────
        self.listAllBatteryCharge = []
        self.listBatteryName = []
        self.listTimeStamp = []
        self.listTestInfo = listTestInfo
        self.test_date = "00000000"
        self.original_cycle_date = "00000000"

        self.listAllPosiForInfoImageCsv = []
        self.listAllChargeForInfoImageCsv = []
        self.listAllVoltageForInfoImageCsv = []

        self.strErrorLog = ""

        # 日志缓冲区（减少 I/O）
        self._log_buffer = []
        self._log_buffer_size = 0
        self._max_buffer_size = 1024 * 10

        # 保存进度回调供 run() 使用
        self._progress_callback = progress_callback

        # 初始化后自动执行（保持向后兼容）
        self.run(strResultPath)

    def run(self, strResultPath: str = "") -> None:
        """执行分析流程：扫描文件 → 并行处理 → 合并 → 写入CSV。

        从 __init__ 中提取，支持独立调用和重入。
        """
        if not strResultPath:
            return

        progress_callback = self._progress_callback
        try:
            # ── 扫描文件 ──────────────────────────────────────────
            self.listAllInXlsx = scan_sorted_xlsx(self.strInDataXlsxDir)

            if not self.listAllInXlsx:
                raise BatteryAnalysisException("[Input Path Error]: has no data file")

            # ── 获取测试日期 ──────────────────────────────────────
            first_date = extract_test_date_from_xls(self.listAllInXlsx[0])
            if first_date != "00000000":
                self.test_date = first_date

            # ── 并行处理 ──────────────────────────────────────────
            process_args = [
                (file_path, self.listCurrentLevel, self.listVoltageLevel)
                for file_path in self.listAllInXlsx
            ]

            results = []
            is_frozen = getattr(sys, "frozen", False)

            if progress_callback:
                progress_callback(12, "Reading Excel file...")

            if is_frozen or sys.platform.startswith("win"):
                from battery_analysis.utils.resource_manager import ResourceManager

                max_processes = ResourceManager.get_optimal_process_count()
                ctx = ResourceManager.get_processing_context()

                with concurrent.futures.ProcessPoolExecutor(
                    max_workers=max_processes, mp_context=ctx
                ) as executor:
                    future_to_idx = {
                        executor.submit(self._parallel_process_file, args): idx
                        for idx, args in enumerate(process_args)
                    }

                    if progress_callback:
                        progress_callback(15, "Analyzing battery data in parallel...")

                    results_map = {}
                    completed = 0
                    total = len(future_to_idx)
                    for future in concurrent.futures.as_completed(future_to_idx):
                        idx = future_to_idx[future]
                        try:
                            result = future.result()
                            if result is not None:
                                results_map[idx] = result
                        except (
                            FileNotFoundError,
                            PermissionError,
                            ValueError,
                            KeyError,
                            IndexError,
                            BatteryAnalysisException,
                        ) as e:
                            file_name = (
                                process_args[idx][0] if idx < len(process_args) else "unknown"
                            )
                            logging.error("Error processing file (skipped): %s - %s", file_name, e)
                            # 跳过失败文件，继续处理其余文件

                        completed += 1
                        if progress_callback and total > 1:
                            pct = 15 + int((completed / total) * 35)
                            progress_callback(
                                pct, f"Analyzing battery data... ({completed}/{total})"
                            )

                    results = [results_map.get(i) for i in range(len(process_args))]
                    results = [r for r in results if r is not None]

                    if not results:
                        raise BatteryAnalysisException(
                            "[Analysis Error]: All files failed to process, please check the data format"
                        )

            else:
                cpu_count = min(multiprocessing.cpu_count(), 4)
                if progress_callback:
                    progress_callback(15, "Analyzing battery data in parallel...")
                with multiprocessing.Pool(processes=cpu_count) as pool:
                    try:
                        results = pool.map(self._parallel_process_file, process_args)
                    except (
                        FileNotFoundError,
                        PermissionError,
                        ValueError,
                        KeyError,
                        IndexError,
                        BatteryAnalysisException,
                    ) as e:
                        logging.error("Error while processing files in parallel: %s", e)
                        pool.terminate()
                        raise BatteryAnalysisException(f"Parallel processing failed: {e!s}")
                    finally:
                        pool.close()
                        pool.join()

            # ── 合并结果 ──────────────────────────────────────────
            for (
                battery_name,
                battery_charge,
                posi_data,
                voltage_data,
                charge_data,
                timestamp_info,
            ) in results:
                self.listBatteryName.append(battery_name)
                self.listAllBatteryCharge.append(battery_charge)
                self.listAllPosiForInfoImageCsv.append(posi_data)
                self.listAllVoltageForInfoImageCsv.append(voltage_data)
                self.listAllChargeForInfoImageCsv.append(charge_data)

                if not self.listTimeStamp:
                    self.listTimeStamp = timestamp_info
                else:
                    self.listTimeStamp[0] = self._str_compare_date(
                        timestamp_info[0], self.listTimeStamp[0], True
                    )
                    self.listTimeStamp[1] = self._str_compare_date(
                        timestamp_info[1], self.listTimeStamp[1], False
                    )

            if progress_callback:
                progress_callback(52, "Writing CSV file...")

            # ── 输出结果 ──────────────────────────────────────────
            self.UBA_WriteCsv(f"{strResultPath}/V{self.listTestInfo[16]}")

            if progress_callback:
                progress_callback(55, "Data processing complete")

        except (OSError, ValueError, BatteryAnalysisException, KeyError) as e:
            self.strErrorLog = str(e)
            if not isinstance(e, (BatteryAnalysisException, KeyError)):
                traceback.print_exc()

    # ────────────────────────────────────────────────────────────
    #  文件级处理（pandas 主路径）
    # ────────────────────────────────────────────────────────────
    @staticmethod
    def _parallel_process_file(args):
        """pandas 主路径：读取并分析单个 xlsx 文件"""
        strPath, listCurrentLevel, listVoltageLevel = args

        try:
            cycle_df, step_df, record_df = read_xlsx_sheets(strPath)
        except Exception as e:  # pylint: disable=broad-exception-caught
            # calamine 引擎异常类型随 pandas 版本变化，统一归一化为业务异常，
            # 由 worker 层的异常处理跳过该文件
            raise BatteryAnalysisException(f"Failed to read Excel file: {strPath}: {e}") from e

        if len(cycle_df) < 3 or len(step_df) < 3 or len(record_df) < 3:
            raise BatteryAnalysisException(
                f"Excel file format error: {strPath} has insufficient data rows"
            )

        # ── 列提取 ──────────────────────────────────────────────
        cycle_cycle = cycle_df.iloc[:, 0]
        cycle_begin = cycle_df.iloc[:, 1]
        cycle_end = cycle_df.iloc[:, 2]
        step_cycle = step_df.iloc[:, 0]
        record_cycle = record_df.iloc[:, 0]
        record_current = record_df.iloc[:, 2]
        record_voltage = record_df.iloc[:, 3]
        record_charge = record_df.iloc[:, 4]

        # ── 时间戳 ──────────────────────────────────────────────
        try:
            listTimeStamp = [
                str(cycle_begin.iloc[2]) if pd_notna(cycle_begin.iloc[2]) else "",
                str(cycle_end.iloc[len(cycle_df) - 1])
                if pd_notna(cycle_end.iloc[len(cycle_df) - 1])
                else "",
            ]
        except IndexError:
            listTimeStamp = ["", ""]

        battery_name = (
            str(cycle_cycle.iloc[0])
            if len(cycle_df) > 0 and pd_notna(cycle_cycle.iloc[0])
            else strPath
        )

        # ── 脉冲检测 ────────────────────────────────────────────
        pulse_mask = detect_pulse_rows(record_df)
        if pulse_mask.sum() == 0:
            raise BatteryAnalysisException(f"Pulse data not found: {strPath}")

        # ── 脉冲等级匹配 ────────────────────────────────────────
        # 不在此处 to_numpy(dtype=float)：record 列含头部标题行（行1 '电流(A)' 等
        # 非数值单元格），全数组强转会抛 ValueError；由 match_pulse_levels 按
        # start_row=2 裁剪后再转换，等价旧实现从 start_row 起逐行 float()。
        matched = match_pulse_levels(
            record_current.to_numpy(),
            record_voltage.to_numpy(),
            pulse_mask.to_numpy(dtype=bool),
            listCurrentLevel,
            listVoltageLevel,
            start_row=2,
        )
        if matched is None:
            raise BatteryAnalysisException(f"Pulse data not found: {strPath}")

        listLevelToVoltage, listLevelToRow, listPosiForInfoImageCsv, listVoltageForInfoImageCsv = (
            matched
        )

        # ── 电荷计算 ────────────────────────────────────────────
        calculator = ChargeCalculator(cycle_df, step_df, record_df)

        listOneBatteryCharge = []
        for c in range(len(listCurrentLevel)):
            for v in range(len(listVoltageLevel)):
                charge = calculator.calculate(listLevelToRow[c][v])
                listOneBatteryCharge.append(charge)

        listChargeForInfoImageCsv = []
        for c, posi_list in enumerate(listPosiForInfoImageCsv):
            charges = calculator.calculate(posi_list, is_single=False)
            if len(charges) != len(listVoltageForInfoImageCsv[c]):
                raise BatteryAnalysisException(
                    f"[Plt Data Error]: battery {battery_name} "
                    f"{listCurrentLevel[c]}mA pulse, "
                    f"charge is not equal to voltage"
                )
            listChargeForInfoImageCsv.append(charges)

        return (
            battery_name,
            listOneBatteryCharge,
            listPosiForInfoImageCsv,
            listVoltageForInfoImageCsv,
            listChargeForInfoImageCsv,
            listTimeStamp,
        )

    # ────────────────────────────────────────────────────────────
    #  日期工具
    # ────────────────────────────────────────────────────────────
    @staticmethod
    def _str_compare_date(strDate1, strDate2, bEarlier):
        """比较两个日期字符串，返回较早或较晚的日期"""

        def int_convert_date(strDate):
            try:
                if " " in strDate:
                    date_part, time_part = strDate.split(" ")
                else:
                    date_part = strDate[:10]
                    time_part = strDate[10:]

                cd1 = date_part.split("-")
                if time_part and ":" in time_part:
                    cd2 = time_part.split(":")
                    return int(
                        f"{int(cd1[0])}{int(cd1[1]):02}{int(cd1[2]):02}"
                        f"{int(cd2[0]):02}{int(cd2[1]):02}{int(cd2[2]):02}"
                    )
                return int(f"{int(cd1[0])}{int(cd1[1]):02}{int(cd1[2]):02}000000")
            except (ValueError, IndexError):
                return 20000101000000

        if strDate1 == strDate2:
            return strDate1 if bEarlier else strDate2

        cd1 = int_convert_date(strDate1)
        cd2 = int_convert_date(strDate2)
        min_date, max_date = (strDate1, strDate2) if cd1 < cd2 else (strDate2, strDate1)
        return min_date if bEarlier else max_date

    # ────────────────────────────────────────────────────────────
    #  单文件分析（保留原接口）
    # ────────────────────────────────────────────────────────────
    def UBA_GetTestDateFromExcel(self, strPath: str) -> str:
        return extract_test_date_from_xls(strPath)

    def UBA_AnalysisXlsx(self, strPath: str) -> None:
        """分析单个 xlsx 文件"""
        result = self._parallel_process_file(
            (strPath, self.listCurrentLevel, self.listVoltageLevel)
        )

        battery_name, battery_charge, posi_data, voltage_data, charge_data, timestamp_info = result

        self.listBatteryName.append(battery_name)
        self.listAllBatteryCharge.append(battery_charge)
        self.listAllPosiForInfoImageCsv.append(posi_data)
        self.listAllVoltageForInfoImageCsv.append(voltage_data)
        self.listAllChargeForInfoImageCsv.append(charge_data)

        if not self.listTimeStamp:
            self.listTimeStamp = timestamp_info
            if isinstance(timestamp_info[0], str) and " " in timestamp_info[0]:
                try:
                    date_part = timestamp_info[0].split(" ")[0]
                    if "-" in date_part:
                        parts = date_part.split("-")
                        if len(parts) >= 3:
                            self.original_cycle_date = (
                                f"{parts[0]}{parts[1].zfill(2)}{parts[2].zfill(2)}"
                            )
                except (ValueError, IndexError):
                    pass
        else:
            self.listTimeStamp[0] = self._str_compare_date(
                timestamp_info[0], self.listTimeStamp[0], True
            )
            self.listTimeStamp[1] = self._str_compare_date(
                timestamp_info[1], self.listTimeStamp[1], False
            )

        self.UBA_Log(datetime.datetime.now().strftime("[%y-%m-%d %H:%M:%S]") + "\r")
        self.UBA_Log(f"Battery {battery_name}:\r")

        # 构建日志用的等级信息
        listLevelToVoltage = []
        listLevelToRow = []
        for c, current_level in enumerate(self.listCurrentLevel):
            listLevelToVoltage.append([])
            listLevelToRow.append([])
            for v, voltage_level in enumerate(self.listVoltageLevel):
                listLevelToVoltage[c].append(voltage_level)
                listLevelToRow[c].append(0)
                for posi, voltage in zip(posi_data[c], voltage_data[c]):
                    if voltage <= voltage_level:
                        listLevelToVoltage[c][v] = voltage
                        listLevelToRow[c][v] = posi
                        break

            self.UBA_Log(f"{current_level}mA - ")
            for v in range(len(self.listVoltageLevel)):
                row_value = listLevelToRow[c][v]
                adjusted_row = row_value + 1 if row_value else row_value
                self.UBA_Log(f"{listLevelToVoltage[c][v]}:{adjusted_row}, ")
            self.UBA_Log("\r")

        self.UBA_Log("\r")

    # ────────────────────────────────────────────────────────────
    #  输出写入
    # ────────────────────────────────────────────────────────────
    def UBA_WriteCsv(self, _strResultPath: str) -> None:
        """写入 Info_Image.csv 和 Info_Plot.json"""
        if not self.listAllPosiForInfoImageCsv:
            logging.error("No valid data to write to CSV file")
            return

        write_info_csv(
            _strResultPath,
            self.listBatteryName,
            self.listCurrentLevel,
            self.listAllPosiForInfoImageCsv,
            self.listAllChargeForInfoImageCsv,
            self.listAllVoltageForInfoImageCsv,
        )

        write_info_json(
            _strResultPath,
            self.listTestInfo,
            current_levels=self.listCurrentLevel,
        )

    # ────────────────────────────────────────────────────────────
    #  日志缓冲
    # ────────────────────────────────────────────────────────────
    def UBA_Log(self, _data: str) -> None:
        self._log_buffer.append(_data)
        self._log_buffer_size += len(_data)
        if self._log_buffer_size >= self._max_buffer_size:
            self._flush_log_buffer()

    def _flush_log_buffer(self):
        if not getattr(self, "_log_buffer", None):
            return
        try:
            with open(self.strResultLogTxt, "a", encoding="utf-8") as f:
                f.writelines(self._log_buffer)
            self._log_buffer = []
            self._log_buffer_size = 0
        except OSError as e:
            logging.error("Failed to write log file: %s", e)

    def __del__(self):
        try:
            self._flush_log_buffer()
        except OSError:
            pass

    # ────────────────────────────────────────────────────────────
    #  结果获取
    # ────────────────────────────────────────────────────────────
    def UBA_GetBatteryInfo(self) -> list:
        return [
            self.listAllBatteryCharge,
            self.listBatteryName,
            self.listTimeStamp,
            self.test_date,
            self.original_cycle_date,
        ]

    def UBA_GetErrorLog(self) -> str:
        return self.strErrorLog


def pd_notna(val):
    """pandas na 检查（避免文件级 import pandas）"""
    try:
        import pandas as pd

        return pd.notna(val)
    except ImportError:
        return val is not None
