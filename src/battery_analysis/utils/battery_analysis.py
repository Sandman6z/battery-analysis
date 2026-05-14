from battery_analysis.utils.exception_type import BatteryAnalysisException
from battery_analysis.utils.data_utils import generate_current_type_string
import xlrd as rd
import pandas as pd
import os
import csv
import datetime
import traceback
import logging
import json
import re
from battery_analysis.utils.readers.xlsx_reader import read_xlsx_sheets, extract_test_date_from_xls
from battery_analysis.utils.processors.pulse_detector import b_is_in_range, is_pulse_step, detect_pulse_rows
from battery_analysis.utils.processors.charge_calculator import ChargeCalculator
import multiprocessing
import sys
import concurrent.futures

# 添加进程保护，避免在multiprocessing子进程中执行不必要的代码
if __name__ == '__main__':
    # 这确保在子进程中不会执行主程序逻辑
    pass

# 配置日志
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class BatteryAnalysis:
    def __init__(self, strInDataXlsxDir: str, strResultPath: str, listTestInfo: list,
                 progress_callback=None) -> None:
        # Check if listTestInfo has enough elements
        if len(listTestInfo) < 19:
            logging.error("测试信息列表格式错误: 缺少必要的信息。需要至少19个元素，但只找到%d个", len(listTestInfo))
            raise BatteryAnalysisException(f"测试信息列表格式错误: 缺少必要的信息。需要至少19个元素，但只找到{len(listTestInfo)}个")
        
        # list for current level and voltage level, next get them in main_window.py
        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        
        # Check if current and voltage level lists are valid
        if not self.listCurrentLevel:
            logging.error("当前等级列表为空")
            raise BatteryAnalysisException("当前等级列表为空")
        
        if not self.listVoltageLevel:
            logging.error("电压等级列表为空")
            raise BatteryAnalysisException("电压等级列表为空")
        
        self.strFileCurrentType = generate_current_type_string(self.listCurrentLevel)

        # input .xlsx directory and result txt path
        self.strInDataXlsxDir = f"{strInDataXlsxDir}/"
        # 替换文件名中的无效字符，特别是冒号
        safe_temperature = listTestInfo[7].replace(':', '_')
        self.strResultLogTxt = (
            f"{strResultPath}/V{listTestInfo[16]}/"
            f"{listTestInfo[4]}_{listTestInfo[2]}_{listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.txt"
        )

        # list to store all battery charge
        self.listAllBatteryCharge = []
        # list for all battery name
        self.listBatteryName = []
        # list for time stamp
        self.listTimeStamp = []
        # 保存完整测试信息，供后续写入元数据文件使用
        self.listTestInfo = listTestInfo
        # 存储从Excel提取的测试日期
        self.test_date = "00000000"
        # 存储从cycleBegin提取的原始日期
        self.original_cycle_date = "00000000"

        # list for Info_Iamge.csv, use the .csv to draw line chart
        self.listAllPosiForInfoImageCsv = []
        self.listAllChargeForInfoImageCsv = []
        self.listAllVoltageForInfoImageCsv = []

        # str for error log
        self.strErrorLog = ""

        # 日志缓冲区，减少I/O操作
        self._log_buffer = []
        self._log_buffer_size = 0
        self._max_buffer_size = 1024 * 10  # 10KB缓冲区

        try:
            # get all input .xlsx path with natural sorting
            def natural_sort_key(filename):
                """
                提取文件名中的数字部分用于自然排序
                针对格式: BTS83_40_5_4_2818580619_...
                将所有数字段转换为整数进行比较，确保 5_4, 5_5, 5_6... 正确排序
                """
                # 将文件名分割成文本和数字部分
                # re.split(r'(\d+)', ...) 会保留分隔符（数字部分）
                parts = re.split(r'(\d+)', filename)
                # 将数字部分转换为整数，文本部分转为小写
                # 这样比较时: ['BTS', 83, '_', 40, '_', 5, '_', 4, ...]
                # 数字按数值大小比较，而不是字符串字典序
                return [int(part) if part.isdigit() else part.lower() for part in parts]

            # 获取所有xlsx文件并按自然顺序排序
            xlsx_files = [f for f in os.listdir(
                self.strInDataXlsxDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            xlsx_files.sort(key=natural_sort_key)
            self.listAllInXlsx = [self.strInDataXlsxDir + f for f in xlsx_files]

            if not self.listAllInXlsx:
                raise BatteryAnalysisException(
                    "[Input Path Error]: has no data file")

            # 并行处理Excel文件
            # 首先获取测试日期（如果有需要统一处理的）
            if self.listAllInXlsx:
                # 从第一个文件获取测试日期
                first_date = extract_test_date_from_xls(
                    self.listAllInXlsx[0])
                if first_date != "00000000":
                    self.test_date = first_date

                # 准备并行处理的参数
                process_args = [(file_path, self.listCurrentLevel, self.listVoltageLevel)
                                for file_path in self.listAllInXlsx]

                # 在Windows环境下使用更安全的并行处理方式
                # 避免multiprocessing在PyInstaller环境中导致的递归启动问题
                results = []

                # 检查是否在PyInstaller环境中运行
                is_frozen = getattr(sys, 'frozen', False)

                if progress_callback:
                    progress_callback(12, "正在读取Excel文件...")

                if is_frozen or sys.platform.startswith('win'):
                    # 在WindowsorPyInstaller环境下，使用进程池但避免递归启动问题

                    # 使用资源管理器获取最优进程数
                    from battery_analysis.utils.resource_manager import ResourceManager
                    max_processes = ResourceManager.get_optimal_process_count()

                    # 获取适合当前平台的进程上下文
                    ctx = ResourceManager.get_processing_context()

                    with concurrent.futures.ProcessPoolExecutor(
                        max_workers=max_processes,
                        mp_context=ctx
                    ) as executor:
                        # 提交所有任务，保持索引映射
                        future_to_idx = {
                            executor.submit(self._parallel_process_file, args): idx
                            for idx, args in enumerate(process_args)
                        }

                        if progress_callback:
                            progress_callback(15, "正在并行分析电池数据...")

                        # 使用as_completed按完成顺序收集，实现每文件进度反馈
                        results_map = {}
                        completed = 0
                        total = len(future_to_idx)
                        for future in concurrent.futures.as_completed(future_to_idx):
                            idx = future_to_idx[future]
                            try:
                                result = future.result()
                                results_map[idx] = result
                            except (
                                FileNotFoundError, PermissionError, ValueError,
                                KeyError, IndexError
                            ) as e:
                                logging.error("处理文件时出错: %s", e)
                                raise BatteryAnalysisException(
                                    f"处理失败: {str(e)}")

                            completed += 1
                            if progress_callback and total > 1:
                                pct = 15 + int((completed / total) * 35)
                                progress_callback(
                                    pct,
                                    f"正在分析电池数据... ({completed}/{total})"
                                )

                        # 按提交顺序还原结果
                        results = [results_map[i] for i in range(len(process_args))]
                else:
                    # 在非Windows环境下，使用进程池并行处理以获得更好的CPU利用率
                    cpu_count = min(multiprocessing.cpu_count(), 4)
                    if progress_callback:
                        progress_callback(15, "正在并行分析电池数据...")
                    with multiprocessing.Pool(processes=cpu_count) as pool:
                        try:
                            results = pool.map(
                                self._parallel_process_file, process_args)
                        except (
                            FileNotFoundError, PermissionError, ValueError,
                            KeyError, IndexError
                        ) as e:
                            logging.error("并行处理文件时出错: %s", e)
                            pool.terminate()
                            raise BatteryAnalysisException(f"并行处理失败: {str(e)}")
                        finally:
                            pool.close()
                            pool.join()

                # 合并结果
                for battery_name, battery_charge, posi_data, \
                           voltage_data, charge_data, timestamp_info in results:
                    self.listBatteryName.append(battery_name)
                    self.listAllBatteryCharge.append(battery_charge)
                    self.listAllPosiForInfoImageCsv.append(posi_data)
                    self.listAllVoltageForInfoImageCsv.append(voltage_data)
                    self.listAllChargeForInfoImageCsv.append(charge_data)

                    # 处理when间戳
                    if not self.listTimeStamp:
                        self.listTimeStamp = timestamp_info
                    else:
                        # 更新最早和最晚when间
                        self.listTimeStamp[0] = self._str_compare_date(
                            timestamp_info[0], self.listTimeStamp[0], True)
                        self.listTimeStamp[1] = self._str_compare_date(
                            timestamp_info[1], self.listTimeStamp[1], False)

            if progress_callback:
                progress_callback(52, "正在写入CSV文件...")

            # write .csv for draw line chart
            self.UBA_WriteCsv(f"{strResultPath}/V{listTestInfo[16]}")

            if progress_callback:
                progress_callback(55, "数据处理完成")

        except (IOError, OSError, ValueError, rd.XLRDError) as e:
            self.strErrorLog = str(e)
            traceback.print_exc()

    def UBA_GetTestDateFromExcel(self, strPath: str) -> str:
        """委托给 readers.xlsx_reader.extract_test_date_from_xls"""
        return extract_test_date_from_xls(strPath)

    @staticmethod
    def _parallel_process_file(args):
        """并行处理单个Excel文件的静态方法（pandas 优化版本）"""
        strPath, listCurrentLevel, listVoltageLevel = args

        listLevelToVoltage = []
        listLevelToRow = []
        listLevelToCharge = []
        listPosiForInfoImageCsv = []
        listVoltageForInfoImageCsv = []
        listChargeForInfoImageCsv = []

        for c, _ in enumerate(listCurrentLevel):
            listLevelToVoltage.append([])
            listLevelToRow.append([])
            listLevelToCharge.append([])
            listPosiForInfoImageCsv.append([])
            listVoltageForInfoImageCsv.append([])
            listChargeForInfoImageCsv.append([])
            for v, _ in enumerate(listVoltageLevel):
                listLevelToVoltage[c].append(listVoltageLevel[v])
                listLevelToRow[c].append(0)
                listLevelToCharge[c].append(0)

        try:
            cycle_df, step_df, record_df = read_xlsx_sheets(strPath)
        except Exception as e:
            logging.error("pandas 读取失败 %s, 回退到 xlrd. 原始错误: %s", strPath, e)
            return BatteryAnalysis._parallel_process_file_xlrd_fallback(args)

        if len(cycle_df) < 3 or len(step_df) < 3 or len(record_df) < 3:
            raise BatteryAnalysisException(f"Excel文件格式错误: {strPath} 数据行不足")

        # 列提取（xlrd 兼容：索引与 xlrd col_values 完全一致）
        cycle_cycle = cycle_df.iloc[:, 0]
        cycle_begin = cycle_df.iloc[:, 1]
        cycle_end = cycle_df.iloc[:, 2]
        cycle_charge = cycle_df.iloc[:, 3]

        step_cycle = step_df.iloc[:, 0]
        step_step = step_df.iloc[:, 1]
        step_charge = step_df.iloc[:, 2]

        record_cycle = record_df.iloc[:, 0]
        record_step = record_df.iloc[:, 1]
        record_current = record_df.iloc[:, 2]
        record_voltage = record_df.iloc[:, 3]
        record_charge = record_df.iloc[:, 4]

        # 兼容原始 xlrd 的索引：row 0 = 表头/电池名，row 1 = 元数据，row 2+ = 数据行
        try:
            listTimeStamp = [
                str(cycle_begin.iloc[2]) if pd.notna(cycle_begin.iloc[2]) else "",
                str(cycle_end.iloc[len(cycle_df)-1]) if pd.notna(cycle_end.iloc[len(cycle_df)-1]) else ""
            ]
        except IndexError:
            listTimeStamp = ["", ""]

        battery_name = str(cycle_cycle.iloc[0]) if len(cycle_df) > 0 and pd.notna(cycle_cycle.iloc[0]) else strPath

        neg_current_levels = [-float(level) for level in listCurrentLevel]

        # 脉冲检测
        pulse_mask = detect_pulse_rows(record_df)
        if pulse_mask.sum() == 0:
            raise BatteryAnalysisException(f"未找到脉冲数据: {strPath}")

        # 遍历每个脉冲行，从索引 2 开始（跳过 header + metadata，与 xlrd 原代码一致）
        for row in range(2, len(record_df)):
            if not pulse_mask.iloc[row]:
                continue

            try:
                current_ma = float(record_current.iloc[row]) * 1000
                voltage = float(record_voltage.iloc[row])
            except (ValueError, TypeError):
                continue

            for c_idx, neg_level in enumerate(neg_current_levels):
                if b_is_in_range(current_ma, neg_level):
                    # 检查是否是脉冲结束点
                    is_endpoint = True
                    if row < len(record_df) - 1:
                        try:
                            next_current = float(record_current.iloc[row + 1]) * 1000
                            if b_is_in_range(next_current, neg_level):
                                is_endpoint = False
                        except (ValueError, TypeError):
                            pass

                    if is_endpoint:
                        listPosiForInfoImageCsv[c_idx].append(row)
                        listVoltageForInfoImageCsv[c_idx].append(voltage)

                    # 检查电压等级
                    for v_idx, v_level in enumerate(listVoltageLevel):
                        if voltage <= v_level and listLevelToRow[c_idx][v_idx] == 0:
                            listLevelToVoltage[c_idx][v_idx] = voltage
                            listLevelToRow[c_idx][v_idx] = row

        # 累积电荷计算（xlrd 兼容索引）
        calculator = ChargeCalculator(cycle_df, step_df, record_df)

        # 计算各电流/电压档位的充电量
        listOneBatteryCharge = []
        for c in range(len(listCurrentLevel)):
            for v in range(len(listVoltageLevel)):
                charge = calculator.calculate(listLevelToRow[c][v])
                listOneBatteryCharge.append(charge)

        # 计算绘图用数据
        for c, posi_list in enumerate(listPosiForInfoImageCsv):
            listChargeForInfoImageCsv[c] = calculator.calculate(posi_list, is_single=False)
            if len(listChargeForInfoImageCsv[c]) != len(listVoltageForInfoImageCsv[c]):
                raise BatteryAnalysisException(
                    f"[Plt Data Error]: battery {battery_name} {listCurrentLevel[c]}mA pulse, "
                    f"charge is not equal to voltage")

        return (
            battery_name,
            listOneBatteryCharge,
            listPosiForInfoImageCsv,
            listVoltageForInfoImageCsv,
            listChargeForInfoImageCsv,
            listTimeStamp
        )

    @staticmethod
    def _parallel_process_file_xlrd_fallback(args):
        """xlrd 回退：原始 xlrd 行扫描实现"""
        strPath, listCurrentLevel, listVoltageLevel = args

        # temp list to store voltage and row refer to different current level and voltage level
        listLevelToVoltage = []
        listLevelToRow = []
        listLevelToCharge = []
        # temp list to store every battery info for .csv
        listPosiForInfoImageCsv = []
        listVoltageForInfoImageCsv = []
        listChargeForInfoImageCsv = []

        # init list
        for c, _ in enumerate(listCurrentLevel):
            listLevelToVoltage.append([])
            listLevelToRow.append([])
            listLevelToCharge.append([])
            listPosiForInfoImageCsv.append([])
            listVoltageForInfoImageCsv.append([])
            listChargeForInfoImageCsv.append([])
            for v, voltage_level in enumerate(listVoltageLevel):
                listLevelToVoltage[c].append(voltage_level)
                listLevelToRow[c].append(0)
                listLevelToCharge[c].append(0)

        # read workbook with error handling
        try:
            rb = rd.open_workbook(strPath)
        except (FileNotFoundError, PermissionError, rd.XLRDError) as e:
            logging.error("读取Excel文件失败: %s, 错误: %s", strPath, e)
            raise BatteryAnalysisException(f"无法打开Excel文件: {strPath}") from e
        
        # Check if we have enough sheets
        sheets = rb.sheets()
        if len(sheets) < 3:
            logging.error("Excel文件格式错误: %s, 缺少必要的工作表。需要至少3个工作表，但只找到%d个", strPath, len(sheets))
            raise BatteryAnalysisException(f"Excel文件格式错误: {strPath} 缺少必要的工作表。需要至少3个工作表，但只找到{len(sheets)}个")
        
        # cycle sheet
        cycleTable = sheets[0]
        cycleRows = cycleTable.nrows
        
        # 安全读取列，确保不会越界
        cycleCycle = cycleTable.col_values(0) if cycleTable.ncols > 0 else []
        cycleBegin = cycleTable.col_values(1) if cycleTable.ncols > 1 else []
        cycleEnd = cycleTable.col_values(2) if cycleTable.ncols > 2 else []
        cycleCharge = cycleTable.col_values(3) if cycleTable.ncols > 3 else []
        
        # 检查必要的列是否存在
        if len(cycleCycle) < 3 or len(cycleBegin) < 3 or len(cycleEnd) < 3 or len(cycleCharge) < 3:
            logging.error("Excel文件格式错误: %s, 第一个工作表缺少必要的列数据", strPath)
            raise BatteryAnalysisException(f"Excel文件格式错误: {strPath} 第一个工作表缺少必要的列数据")
        
        # step sheet
        stepTable = sheets[1]
        stepRows = stepTable.nrows
        stepCycle = stepTable.col_values(0) if stepTable.ncols > 0 else []
        stepStep = stepTable.col_values(1) if stepTable.ncols > 1 else []
        stepCharge = stepTable.col_values(2) if stepTable.ncols > 2 else []
        
        # 检查必要的列是否存在
        if len(stepCycle) < 3 or len(stepStep) < 3 or len(stepCharge) < 3:
            logging.error("Excel文件格式错误: %s, 第二个工作表缺少必要的列数据", strPath)
            raise BatteryAnalysisException(f"Excel文件格式错误: {strPath} 第二个工作表缺少必要的列数据")
        
        # record sheet
        recordTable = sheets[2]
        recordRows = recordTable.nrows
        recordCycle = recordTable.col_values(0) if recordTable.ncols > 0 else []
        recordStep = recordTable.col_values(1) if recordTable.ncols > 1 else []
        recordCurrent = recordTable.col_values(2) if recordTable.ncols > 2 else []
        recordVoltage = recordTable.col_values(3) if recordTable.ncols > 3 else []
        recordCharge = recordTable.col_values(4) if recordTable.ncols > 4 else []
        
        # 检查必要的列是否存在
        if len(recordCycle) < 3 or len(recordStep) < 3 or len(recordCurrent) < 3 or len(recordVoltage) < 3 or len(recordCharge) < 3:
            logging.error("Excel文件格式错误: %s, 第三个工作表缺少必要的列数据", strPath)
            raise BatteryAnalysisException(f"Excel文件格式错误: {strPath} 第三个工作表缺少必要的列数据")

        # 处理when间戳
        listTimeStamp = [cycleBegin[2], cycleEnd[-1]]

        def b_is_in_range_milli_ampere(_floatInput, _floatStandard):
            _floatMin = _floatStandard*1.05
            _floatMax = _floatStandard*0.95
            return _floatMin <= _floatInput <= _floatMax

        # analysis battery data
        battery_name = cycleCycle[0]

        # 优化：预计算负值的电流等级，避免重复计算
        neg_current_levels = [-float(level) for level in listCurrentLevel]

        # 优化：使用更高效的数据结构和算法
        for row in range(2, recordRows):
            step = recordStep[row]
            # 快速跳过非脉冲步骤
            if step not in ("脉冲", "Pulse"):
                continue

            current = float(recordCurrent[row]) * 1000
            voltage = float(recordVoltage[row])

            # 遍历电流等级，使用预计算的负值
            for c_idx, neg_current_level in enumerate(neg_current_levels):
                if b_is_in_range_milli_ampere(current, neg_current_level):
                    # 检查是否是脉冲结束点
                    if row < recordRows - 1:
                        next_current = float(recordCurrent[row + 1]) * 1000
                        if not b_is_in_range_milli_ampere(next_current, neg_current_level):
                            listPosiForInfoImageCsv[c_idx].append(row)
                            listVoltageForInfoImageCsv[c_idx].append(voltage)

                    # 检查电压等级
                    for v_idx, voltage_level in enumerate(listVoltageLevel):
                        if voltage <= voltage_level and listLevelToRow[c_idx][v_idx] == 0:
                            listLevelToVoltage[c_idx][v_idx] = voltage
                            listLevelToRow[c_idx][v_idx] = row

        # 算法优化：预计算累积充电量和索引表，加速后续计算
        # 1. 预计算cycle的累积充电量
        cycle_cumulative_charge = [0.0] * cycleRows
        total_charge = 0.0
        for c1 in range(2, cycleRows):
            try:
                charge_value = float(cycleCharge[c1])
                total_charge += abs(charge_value)
                cycle_cumulative_charge[c1] = total_charge
            except (ValueError, TypeError) as e:
                logging.warning(f"处理cycleCharge数据时遇到非数字值，跳过此点: {e}")
                continue

        # 2. 创建step数据的字典索引，加速查找
        step_dict = {}
        for c2 in range(2, stepRows):
            cycle_key = stepCycle[c2]
            if cycle_key not in step_dict:
                step_dict[cycle_key] = []
            if stepStep[c2] not in ("脉冲", "Pulse"):
                try:
                    charge_value = float(stepCharge[c2])
                    step_dict[cycle_key].append(abs(charge_value))
                except (ValueError, TypeError) as e:
                    logging.warning(f"处理stepCharge数据时遇到非数字值，跳过此点: {e}")
                    continue

        # 3. 合并posi2_charge和list_posi2_charge功能，减少代码重复
        def calculate_charge(positions, is_single=True):
            """统一计算单个or多个位置的充电量"""
            if is_single:
                positions = [positions]
                results = []
            else:
                results = [0.0] * len(positions)

            for idx, intPosi in enumerate(positions):
                if not intPosi:
                    if is_single:
                        results.append(0)
                    continue

                _cycle = recordCycle[intPosi]

                # 使用预计算的累积充电量，避免重复遍历
                # 找到第一个大于等于当前cycle的索引
                cycle_idx = 2
                while cycle_idx < cycleRows and cycleCycle[cycle_idx] < _cycle:
                    cycle_idx += 1

                # 获取累积充电量
                intCharge = cycle_cumulative_charge[cycle_idx -
                                                    1] if cycle_idx > 2 else 0

                # 使用字典快速查找step数据
                if _cycle in step_dict:
                    intCharge += sum(step_dict[_cycle])

                # 添加当前记录的充电量
                try:
                    charge_value = float(recordCharge[intPosi])
                    intCharge += abs(charge_value)
                except (ValueError, TypeError) as e:
                    logging.warning(f"处理recordCharge数据时遇到非数字值，跳过此点: {e}")
                    continue

                if is_single:
                    results.append(round(intCharge))
                else:
                    results[idx] = intCharge

            return results[0] if is_single else results

        # for Utility_XlsxWriter.py to write .xlsx
        listOneBatteryCharge = []

        for c in range(len(listCurrentLevel)):
            for v in range(len(listVoltageLevel)):
                charge = calculate_charge(listLevelToRow[c][v])
                listOneBatteryCharge.append(charge)

        # for BatteryChartViewer to draw line chart
        for c, posi_list in enumerate(listPosiForInfoImageCsv):
            listChargeForInfoImageCsv[c] = calculate_charge(
                posi_list, is_single=False)
            if len(listChargeForInfoImageCsv[c]) != len(listVoltageForInfoImageCsv[c]):

                raise BatteryAnalysisException(
                    f"[Plt Data Error]: battery {battery_name} {listCurrentLevel[c]}mA pulse, "
                    f"charge is not equal to voltage")

        # 返回处理结果
        return (
            battery_name,
            listOneBatteryCharge,
            listPosiForInfoImageCsv,
            listVoltageForInfoImageCsv,
            listChargeForInfoImageCsv,
            listTimeStamp
        )

    def _str_compare_date(self, strDate1, strDate2, bEarlier):
        """日期比较辅助方法"""
        def int_convert_date(strDate):
            # 日期when间转换函数
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

        convert_date1 = int_convert_date(strDate1)
        convert_date2 = int_convert_date(strDate2)

        if convert_date1 < convert_date2:
            min_date = strDate1
            max_date = strDate2
        else:
            min_date = strDate2
            max_date = strDate1

        return min_date if bEarlier else max_date

        # 移除重复定义的方法，使用内部实现

    def UBA_AnalysisXlsx(self, strPath: str) -> None:
        """保留原方法接口，使用并行处理方法实现"""
        # 使用并行处理方法处理单个文件
        result = self._parallel_process_file(
            (strPath, self.listCurrentLevel, self.listVoltageLevel))

        # 处理结果，与原方法保持一致
        battery_name, battery_charge, posi_data, voltage_data, charge_data, timestamp_info = result

        # 更新类属性
        self.listBatteryName.append(battery_name)
        self.listAllBatteryCharge.append(battery_charge)
        self.listAllPosiForInfoImageCsv.append(posi_data)
        self.listAllVoltageForInfoImageCsv.append(voltage_data)
        self.listAllChargeForInfoImageCsv.append(charge_data)

        # 处理when间戳
        if not self.listTimeStamp:
            self.listTimeStamp = timestamp_info
            # 尝试提取原始cycle日期
            if isinstance(timestamp_info[0], str) and " " in timestamp_info[0]:
                try:
                    date_part = timestamp_info[0].split(" ")[0]
                    if "-" in date_part:
                        parts = date_part.split("-")
                        if len(parts) >= 3:
                            year, month, day = parts[:3]
                            self.original_cycle_date = f"{year}{month.zfill(2)}{day.zfill(2)}"
                except (ValueError, IndexError) as e:
                    logging.error("解析原始cycle日期失败: %s", e)
        else:
            # 更新最早和最晚when间
            self.listTimeStamp[0] = self._str_compare_date(
                timestamp_info[0], self.listTimeStamp[0], True)
            self.listTimeStamp[1] = self._str_compare_date(
                timestamp_info[1], self.listTimeStamp[1], False)

        # 记录日志
        self.UBA_Log(datetime.datetime.now().strftime(
            "[%y-%m-%d %H:%M:%S]") + '\r')
        self.UBA_Log(f"Battery {battery_name}:\r")

        # 重建listLevelToVoltage和listLevelToRow用于日志输出
        listLevelToVoltage = []
        listLevelToRow = []
        for c, current_level in enumerate(self.listCurrentLevel):
            listLevelToVoltage.append([])
            listLevelToRow.append([])
            for v, voltage_level in enumerate(self.listVoltageLevel):
                # 从结果数据中提取电压和行信息
                listLevelToVoltage[c].append(voltage_level)
                listLevelToRow[c].append(0)

                # 查找匹配的电压等级
                for posi, voltage in zip(posi_data[c], voltage_data[c]):
                    if voltage <= voltage_level:
                        listLevelToVoltage[c][v] = voltage
                        listLevelToRow[c][v] = posi
                        break

            self.UBA_Log(f"{current_level}mA - ")
            for v, voltage in enumerate(self.listVoltageLevel):
                row_value = listLevelToRow[c][v]
                adjusted_row = row_value + 1 if row_value else row_value
                self.UBA_Log(
                    f"{listLevelToVoltage[c][v]}:{adjusted_row}, ")
            self.UBA_Log("\r")

        self.UBA_Log("\r")

    def UBA_WriteCsv(self, _strResultPath: str) -> None:
        """将结果写入CSV文件（优化版）"""
        # 检查是否存在有效数据
        if not self.listAllPosiForInfoImageCsv:
            logging.error("没有有效数据可写入CSV文件")
            return

        # 创建CSV文件路径
        strCsvFilePath = f"{_strResultPath}/Info_Image.csv"

        # 优化：批量准备CSV数据，减少I/O操作次数
        csv_data = []

        # 遍历电池数据
        for b, battery_name in enumerate(self.listBatteryName):
            csv_data.append(["BATTERY", battery_name])
            for c in range(len(self.listCurrentLevel)):
                # 一次性添加所有相关行
                csv_data.append(self.listAllPosiForInfoImageCsv[b][c])
                csv_data.append(self.listAllChargeForInfoImageCsv[b][c])
                csv_data.append(self.listAllVoltageForInfoImageCsv[b][c])

        # 一次性写入所有数据
        with open(strCsvFilePath, 'w', newline='', encoding='utf-8') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(csv_data)

        # 写入元数据JSON文件，供BatteryChartViewer读取以获取动态标题
        try:
            strMetaFilePath = f"{_strResultPath}/Info_Plot.json"
            meta_data = {
                "manufacturer": self.listTestInfo[4] if len(self.listTestInfo) > 4 else "",
                "spec_type": self.listTestInfo[2] if len(self.listTestInfo) > 2 else "",
                "spec_method": self.listTestInfo[3] if len(self.listTestInfo) > 3 else "",
                "batch_code": self.listTestInfo[5] if len(self.listTestInfo) > 5 else "",
                "capacity": self.listTestInfo[8] if len(self.listTestInfo) > 8 else "",
                "temperature": self.listTestInfo[7] if len(self.listTestInfo) > 7 else "",
                "current_levels": self.listTestInfo[14] if len(self.listTestInfo) > 14 else [],
            }
            with open(strMetaFilePath, 'w', encoding='utf-8') as metaFile:
                json.dump(meta_data, metaFile, ensure_ascii=False, indent=2)
            logging.info("写入元数据文件: %s", strMetaFilePath)
        except (IndexError, TypeError, OSError, ValueError) as e:
            logging.warning("写入元数据文件失败: %s", e)

    def UBA_Log(self, _data: str) -> None:
        """优化的日志写入方法，使用缓冲区减少I/O操作"""
        # 添加到缓冲区
        self._log_buffer.append(_data)
        self._log_buffer_size += len(_data)

        # 当缓冲区达到一定大小when写入文件
        if self._log_buffer_size >= self._max_buffer_size:
            self._flush_log_buffer()

    def _flush_log_buffer(self):
        """将日志缓冲区写入文件"""
        if not getattr(self, '_log_buffer', None):
            return

        try:
            with open(self.strResultLogTxt, "a", encoding='utf-8') as f:
                f.writelines(self._log_buffer)
            # 清空缓冲区
            self._log_buffer = []
            self._log_buffer_size = 0
        except (IOError, OSError) as e:
            logging.error("写入日志文件失败: %s", e)

    def __del__(self):
        """析构函数，确保日志缓冲区被刷新"""
        try:
            self._flush_log_buffer()
        except (IOError, OSError):
            pass

    def UBA_GetBatteryInfo(self) -> list:
        """
        返回电池信息列表，包含以下内容：
        [0]: 所有电池电荷数据
        [1]: 电池名称列表
        [2]: when间戳列表
        [3]: 从Test Date提取的日期
        [4]: 从cycleBegin提取的原始日期
        """
        return [
            self.listAllBatteryCharge, 
            self.listBatteryName, 
            self.listTimeStamp, 
            self.test_date, 
            self.original_cycle_date
        ]

    def UBA_GetErrorLog(self) -> str:
        return self.strErrorLog
