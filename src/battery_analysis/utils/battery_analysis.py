from battery_analysis.utils.exception_type import BatteryAnalysisException
from battery_analysis.utils.data_utils import generate_current_type_string
import xlrd as rd
import os
import csv
import datetime
import traceback
import logging
import re
import multiprocessing
import sys
import concurrent.futures

# 添加进程保护，避免在multiprocessing子进程中执行不必要的代码
if __name__ == '__main__':
    # 这确保在子进程中不会执行主程序逻辑
    pass

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class BatteryAnalysis:
    def __init__(self, strInDataXlsxDir: str, strResultPath: str, listTestInfo: list) -> None:
        # list for current level and voltage level, next get them in main_window.py
        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        self.strFileCurrentType = generate_current_type_string(self.listCurrentLevel)

        # input .xlsx directory and result txt path
        self.strInDataXlsxDir = f"{strInDataXlsxDir}/"
        self.strResultLogTxt = (
            f"{strResultPath}/V{listTestInfo[16]}/"
            f"{listTestInfo[4]}_{listTestInfo[2]}_{listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{listTestInfo[7]}.txt"
        )

        # list to store all battery charge
        self.listAllBatteryCharge = []
        # list for all battery name
        self.listBatteryName = []
        # list for time stamp
        self.listTimeStamp = []
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
            # get all input .xlsx path
            self.listAllInXlsx = [self.strInDataXlsxDir + f for f in os.listdir(
                self.strInDataXlsxDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]

            if len(self.listAllInXlsx) == 0:
                raise BatteryAnalysisException(
                    "[Input Path Error]: has no data file")

            # 并行处理Excel文件
            # 首先获取测试日期（如果有需要统一处理的）
            if self.listAllInXlsx:
                # 从第一个文件获取测试日期
                first_date = self.UBA_GetTestDateFromExcel(
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

                if is_frozen or sys.platform.startswith('win'):
                    # 在Windows或PyInstaller环境下，使用进程池但避免递归启动问题
                    logging.info("使用进程池并行处理")

                    # 使用资源管理器获取最优进程数
                    from battery_analysis.utils.resource_manager import ResourceManager
                    max_processes = ResourceManager.get_optimal_process_count()

                    # 获取适合当前平台的进程上下文
                    ctx = ResourceManager.get_processing_context()

                    with concurrent.futures.ProcessPoolExecutor(
                        max_workers=max_processes, 
                        mp_context=ctx
                    ) as executor:
                        # 提交所有任务
                        future_to_args = {
                            executor.submit(self._parallel_process_file, args): args 
                            for args in process_args
                        }

                        # 获取结果
                        for future in concurrent.futures.as_completed(future_to_args):
                            try:
                                result = future.result()
                                results.append(result)
                            except (
                                FileNotFoundError, PermissionError, ValueError, 
                                KeyError, IndexError
                            ) as e:
                                logging.error("处理文件时出错: %s", e)
                                raise BatteryAnalysisException(
                                    f"处理失败: {str(e)}")
                else:
                    # 在非Windows环境下，使用进程池并行处理以获得更好的CPU利用率
                    logging.info("在非Windows环境中，使用进程池并行处理以获得最佳性能")
                    cpu_count = min(multiprocessing.cpu_count(), 4)
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

                    # 处理时间戳
                    if not self.listTimeStamp:
                        self.listTimeStamp = timestamp_info
                    else:
                        # 更新最早和最晚时间
                        self.listTimeStamp[0] = self._str_compare_date(
                            timestamp_info[0], self.listTimeStamp[0], True)
                        self.listTimeStamp[1] = self._str_compare_date(
                            timestamp_info[1], self.listTimeStamp[1], False)

            # write .csv for draw line chart
            self.UBA_WriteCsv(f"{strResultPath}/V{listTestInfo[16]}")

        except (IOError, OSError, ValueError, rd.XLRDError) as e:
            self.strErrorLog = str(e)
            traceback.print_exc()

    def UBA_GetTestDateFromExcel(self, strPath: str) -> str:
        """
        从Excel文件中提取Test Date字段

        Args:
            strPath: Excel文件路径

        Returns:
            str: 格式化的日期字符串 (YYYYMMDD)，如果无法提取则返回默认值
        """
        try:
            rb = rd.open_workbook(strPath)

            # 搜索所有工作表中的"Test Date"字段
            for sheet_idx in range(len(rb.sheets())):
                sheet = rb.sheets()[sheet_idx]
                for row in range(min(20, sheet.nrows)):  # 只搜索前20行以提高效率
                    for col in range(sheet.ncols):
                        cell_value = sheet.cell_value(row, col)
                        if isinstance(cell_value, str):
                            # 搜索包含Test Date的单元格
                            if "Test Date" in cell_value or "测试日期" in cell_value:
                                # 尝试从相邻单元格获取日期值
                                if col + 1 < sheet.ncols:
                                    date_value = sheet.cell_value(row, col + 1)
                                    if isinstance(date_value, str) and date_value.strip():
                                        # 处理多种日期格式
                                        date_str = date_value.strip()
                                        # 格式1: 10.06.2025 - 08.07.2025
                                        if "-" in date_str and "." in date_str:
                                            start_date_part = date_str.split(
                                                "-")[0].strip()
                                            if "." in start_date_part:
                                                parts = start_date_part.split(
                                                    ".")
                                                if len(parts) == 3:
                                                    try:
                                                        day, month, year = parts
                                                        # 确保值可以转换为整数并直接使用
                                                        return f"{year.zfill(4)}" \
                                                                f"{month.zfill(2)}" \
                                                                f"{day.zfill(2)}"
                                                    except ValueError:
                                                        logging.warning(
                                                            "日期部分无法转换为整数: %s", parts)
                                        # 格式2: 2025-06-10
                                        elif "-" in date_str:
                                            parts = date_str.split("-")
                                            if len(parts) >= 3:
                                                try:
                                                    year, month, day = parts[:3]
                                                    # 确保值可以转换为整数并直接使用
                                                    return f"{year.zfill(4)}" \
                                                            f"{month.zfill(2)}" \
                                                            f"{day.zfill(2)}"
                                                except ValueError:
                                                    logging.warning(
                                                        "日期部分无法转换为整数: %s", parts[:3])

                                # 尝试从下方单元格获取日期值
                                if row + 1 < sheet.nrows:
                                    date_value = sheet.cell_value(row + 1, col)
                                    if isinstance(date_value, str) and date_value.strip():
                                        # 处理多种日期格式
                                        date_str = date_value.strip()
                                        if "-" in date_str and "." in date_str:
                                            start_date_part = date_str.split(
                                                "-")[0].strip()
                                            if "." in start_date_part:
                                                parts = start_date_part.split(
                                                    ".")
                                                if len(parts) == 3:
                                                    try:
                                                        day, month, year = parts
                                                        # 确保值可以转换为整数并直接使用
                                                        return f"{year.zfill(4)}" \
                                                                f"{month.zfill(2)}" \
                                                                f"{day.zfill(2)}"
                                                    except ValueError:
                                                        logging.warning(
                                                            "日期部分无法转换为整数: %s", parts)
                                        elif "-" in date_str:
                                            parts = date_str.split("-")
                                            if len(parts) >= 3:
                                                try:
                                                    year, month, day = parts[:3]
                                                    # 确保值可以转换为整数并直接使用
                                                    return f"{year.zfill(4)}" \
                                                            f"{month.zfill(2)}" \
                                                            f"{day.zfill(2)}"
                                                except ValueError:
                                                    logging.warning(
                                                        "日期部分无法转换为整数: %s", parts[:3])

            # 如果找不到Test Date字段，尝试从文件名提取
            file_name = os.path.basename(strPath)
            logging.info("从文件名解析日期: %s", file_name)

            # 尝试从文件名中提取日期
            # 匹配文件名中所有连续的数字组
            digit_groups = re.findall(r'(\d+)', file_name)
            if digit_groups:
                # 取最后一组连续数字
                last_digit_group = digit_groups[-1]
                # 提取前8位作为日期（如果长度足够）
                if len(last_digit_group) >= 8:
                    date_str = last_digit_group[:8]
                    logging.info("提取日期: %s", date_str)
                    # 验证提取的日期是否有效（简单验证：年份在合理范围）
                    try:
                        year = int(date_str[:4])
                        if 2000 <= year <= 2100:
                            return date_str
                        logging.warning("提取的年份 %s 不在有效范围内", year)
                    except ValueError:
                        logging.error("无法解析年份")
            # 然后尝试其他常见的日期格式
            date_patterns = [
                r'(\d{4})-(\d{2})-(\d{2})',  # 2025-06-10
                r'(\d{2})\.(\d{2})\.(\d{4})'  # 10.06.2025
            ]

            for pattern in date_patterns:
                match = re.search(pattern, file_name)
                if match:
                    try:
                        if pattern == r'(\d{2})\.(\d{2})\.(\d{4})':
                            day, month, year = match.groups()
                            result = f"{year}{month.zfill(2)}{day.zfill(2)}"
                            logging.info("从文件名提取到日期: %s", result)
                            return result
                        year, month, day = match.groups()
                        result = f"{year}{month.zfill(2)}{day.zfill(2)}"
                        logging.info("从文件名提取到日期: %s", result)
                        return result
                    except (ValueError, AttributeError) as e:
                        logging.warning("从文件名解析日期失败: %s", e)

        except (rd.XLRDError, FileNotFoundError, PermissionError, ValueError) as e:
            logging.error("从Excel提取Test Date失败: %s, 错误: %s", strPath, e)

        # 确保总是有返回值
        return "00000000"

    @staticmethod
    def _parallel_process_file(args):
        """并行处理单个Excel文件的静态方法"""
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
        # cycle sheet
        cycleTable = rb.sheets()[0]
        cycleRows = cycleTable.nrows
        cycleCycle = cycleTable.col_values(0)
        cycleBegin = cycleTable.col_values(1)
        cycleEnd = cycleTable.col_values(2)
        cycleCharge = cycleTable.col_values(3)
        # step sheet
        stepTable = rb.sheets()[1]
        stepRows = stepTable.nrows
        stepCycle = stepTable.col_values(0)
        stepStep = stepTable.col_values(1)
        stepCharge = stepTable.col_values(2)
        # record sheet
        recordTable = rb.sheets()[2]
        recordRows = recordTable.nrows
        recordCycle = recordTable.col_values(0)
        recordStep = recordTable.col_values(1)
        recordCurrent = recordTable.col_values(2)
        recordVoltage = recordTable.col_values(3)
        recordCharge = recordTable.col_values(4)

        # 处理时间戳
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
            total_charge += abs(cycleCharge[c1])
            cycle_cumulative_charge[c1] = total_charge

        # 2. 创建step数据的字典索引，加速查找
        step_dict = {}
        for c2 in range(2, stepRows):
            cycle_key = stepCycle[c2]
            if cycle_key not in step_dict:
                step_dict[cycle_key] = []
            if stepStep[c2] not in ("脉冲", "Pulse"):
                step_dict[cycle_key].append(abs(stepCharge[c2]))

        # 3. 合并posi2_charge和list_posi2_charge功能，减少代码重复
        def calculate_charge(positions, is_single=True):
            """统一计算单个或多个位置的充电量"""
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
                intCharge += abs(recordCharge[intPosi])

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
            # 日期时间转换函数
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

        # 处理时间戳
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
            # 更新最早和最晚时间
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

    def UBA_Log(self, _data: str) -> None:
        """优化的日志写入方法，使用缓冲区减少I/O操作"""
        logging.debug(_data, end='')
        # 添加到缓冲区
        self._log_buffer.append(_data)
        self._log_buffer_size += len(_data)

        # 当缓冲区达到一定大小时写入文件
        if self._log_buffer_size >= self._max_buffer_size:
            self._flush_log_buffer()

    def _flush_log_buffer(self):
        """将日志缓冲区写入文件"""
        if not self._log_buffer:
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
        [2]: 时间戳列表
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
