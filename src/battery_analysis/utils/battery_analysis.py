import os
import csv
import datetime
import traceback
import logging
import re
from concurrent.futures import ProcessPoolExecutor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import xlrd as rd

from src.battery_analysis.utils.exception_type import BatteryAnalysisException


class BatteryAnalysis:
    def __init__(self, strInDataXlsxDir: str, strResultPath: str, listTestInfo: list) -> None:
        # list for current level and voltage level, next get them in main_window.py
        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        self.strFileCurrentType = ""
        for c in range(len(self.listCurrentLevel)):
            self.strFileCurrentType = self.strFileCurrentType + f"{self.listCurrentLevel[c]}-"
        self.strFileCurrentType = self.strFileCurrentType[:-1]

        # input .xlsx directory and result txt path
        self.strInDataXlsxDir = f"{strInDataXlsxDir}/"
        self.strResultLogTxt = f"{strResultPath}/V{listTestInfo[16]}/{listTestInfo[4]}_{listTestInfo[2]}_{listTestInfo[3]}_{self.strFileCurrentType}_{listTestInfo[7]}.txt"

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
            self.listAllInXlsx = [self.strInDataXlsxDir + f for f in os.listdir(self.strInDataXlsxDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]

            if len(self.listAllInXlsx) == 0:
                raise BatteryAnalysisException("[Input Path Error]: has no data file")

            # 并行处理Excel文件
            # 首先获取测试日期（如果有需要统一处理的）
            if self.listAllInXlsx:
                # 从第一个文件获取测试日期
                first_date = self.UBA_GetTestDateFromExcel(self.listAllInXlsx[0])
                if first_date != "00000000":
                    self.test_date = first_date
                
                # 准备并行处理的参数
                process_args = [(file_path, self.listCurrentLevel, self.listVoltageLevel) for file_path in self.listAllInXlsx]
                
                # 使用进程池并行处理，添加错误处理和超时控制
                results = []
                with ProcessPoolExecutor(max_workers=None) as executor:  # None表示使用CPU核心数
                    # 使用as_completed获取完成的任务结果
                    future_to_file = {executor.submit(self._parallel_process_file, args): args[0] for args in process_args}
                    
                    from concurrent.futures import as_completed
                    for future in as_completed(future_to_file):
                        file_path = future_to_file[future]
                        try:
                            result = future.result(timeout=300)  # 设置5分钟超时
                            results.append(result)
                        except Exception as e:
                            logging.error(f"处理文件失败: {file_path}, 错误: {e}")
                            from src.battery_analysis.utils.exception_type import BatteryAnalysisException
                            raise BatteryAnalysisException(f"处理文件时出错: {file_path}, 错误: {str(e)}")
                
                # 合并结果
                for battery_name, battery_charge, posi_data, voltage_data, charge_data, timestamp_info in results:
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
                        self.listTimeStamp[0] = self._str_compare_date(timestamp_info[0], self.listTimeStamp[0], True)
                        self.listTimeStamp[1] = self._str_compare_date(timestamp_info[1], self.listTimeStamp[1], False)

            # write .csv for draw line chart
            self.UBA_WriteCsv(f"{strResultPath}/V{listTestInfo[16]}")

        except BaseException as e:
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
                                            start_date_part = date_str.split("-")[0].strip()
                                            if "." in start_date_part:
                                                parts = start_date_part.split(".")
                                                if len(parts) == 3:
                                                    try:
                                                        day, month, year = parts
                                                        # 确保值可以转换为整数
                                                        int(day), int(month), int(year)
                                                        return f"{year.zfill(4)}{month.zfill(2)}{day.zfill(2)}"
                                                    except ValueError:
                                                        logging.warning(f"日期部分无法转换为整数: {parts}")
                                        # 格式2: 2025-06-10
                                        elif "-" in date_str:
                                            parts = date_str.split("-")
                                            if len(parts) >= 3:
                                                try:
                                                    year, month, day = parts[:3]
                                                    # 确保值可以转换为整数
                                                    int(year), int(month), int(day)
                                                    return f"{year.zfill(4)}{month.zfill(2)}{day.zfill(2)}"
                                                except ValueError:
                                                    logging.warning(f"日期部分无法转换为整数: {parts[:3]}")
                                
                                # 尝试从下方单元格获取日期值
                                if row + 1 < sheet.nrows:
                                    date_value = sheet.cell_value(row + 1, col)
                                    if isinstance(date_value, str) and date_value.strip():
                                        # 处理多种日期格式
                                        date_str = date_value.strip()
                                        if "-" in date_str and "." in date_str:
                                            start_date_part = date_str.split("-")[0].strip()
                                            if "." in start_date_part:
                                                parts = start_date_part.split(".")
                                                if len(parts) == 3:
                                                    try:
                                                        day, month, year = parts
                                                        # 确保值可以转换为整数
                                                        int(day), int(month), int(year)
                                                        return f"{year.zfill(4)}{month.zfill(2)}{day.zfill(2)}"
                                                    except ValueError:
                                                        logging.warning(f"日期部分无法转换为整数: {parts}")
                                        elif "-" in date_str:
                                            parts = date_str.split("-")
                                            if len(parts) >= 3:
                                                try:
                                                    year, month, day = parts[:3]
                                                    # 确保值可以转换为整数
                                                    int(year), int(month), int(day)
                                                    return f"{year.zfill(4)}{month.zfill(2)}{day.zfill(2)}"
                                                except ValueError:
                                                    logging.warning(f"日期部分无法转换为整数: {parts[:3]}")
            
            # 如果找不到Test Date字段，尝试从文件名提取
            file_name = os.path.basename(strPath)
            logging.info(f"正在从文件名解析日期: {file_name}")
            
            # 尝试从文件名中提取日期
            # 匹配文件名中所有连续的数字组
            digit_groups = re.findall(r'(\d+)', file_name)
            if digit_groups:
                # 取最后一组连续数字
                last_digit_group = digit_groups[-1]
                # 提取前8位作为日期（如果长度足够）
                if len(last_digit_group) >= 8:
                    date_str = last_digit_group[:8]
                    logging.info(f"从文件名最后一组连续数字提取前8位作为日期: {date_str}")
                    # 验证提取的日期是否有效（简单验证：年份在合理范围）
                    try:
                        year = int(date_str[:4])
                        if 2000 <= year <= 2100:
                            return date_str
                        else:
                            logging.warning(f"提取的日期年份 {year} 不在有效范围内")
                    except ValueError:
                        logging.error("无法解析日期年份")
            # 如果最后一组数字不足8位或验证失败，尝试匹配任意8位数字
            date_match = re.search(r'(\d{8})', file_name)
            if date_match:
                date_str = date_match.group(1)
                logging.info(f"从文件名提取任意8位日期: {date_str}")
                try:
                    year = int(date_str[:4])
                    if 2000 <= year <= 2100:
                        return date_str
                except ValueError:
                    logging.error("无法解析日期年份")
            
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
                            logging.info(f"从文件名提取到日期: {result}")
                            return result
                        else:
                            year, month, day = match.groups()
                            result = f"{year}{month.zfill(2)}{day.zfill(2)}"
                            logging.info(f"从文件名提取到日期: {result}")
                            return result
                    except Exception as e:
                        logging.warning(f"从文件名解析日期失败: {e}")
            
        except Exception as e:
            logging.error(f"从Excel提取Test Date失败: {strPath}, 错误: {e}")
        
        # 确保总是有返回值
        return "00000000"
    
    @staticmethod
    def _parallel_process_file(args):
        """并行处理单个Excel文件的静态方法"""
        strPath, listCurrentLevel, listVoltageLevel = args
        
        # 导入需要的模块
        import xlrd as rd
        import logging
        
        # temp list to store voltage and row refer to different current level and voltage level
        listLevelToVoltage = []
        listLevelToRow = []
        listLevelToCharge = []
        # temp list to store every battery info for .csv
        listPosiForInfoImageCsv = []
        listVoltageForInfoImageCsv = []
        listChargeForInfoImageCsv = []

        # init list
        for c in range(len(listCurrentLevel)):
            listLevelToVoltage.append([])
            listLevelToRow.append([])
            listLevelToCharge.append([])
            listPosiForInfoImageCsv.append([])
            listVoltageForInfoImageCsv.append([])
            listChargeForInfoImageCsv.append([])
            for v in range(len(listVoltageLevel)):
                listLevelToVoltage[c].append(listVoltageLevel[v])
                listLevelToRow[c].append(0)
                listLevelToCharge[c].append(0)

        # read workbook with error handling
        try:
            rb = rd.open_workbook(strPath)
        except Exception as e:
            logging.error(f"读取Excel文件失败: {strPath}, 错误: {e}")
            from src.battery_analysis.utils.exception_type import BatteryAnalysisException
            raise BatteryAnalysisException(f"无法打开Excel文件: {strPath}")
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

        def int_convert_date(strDate: str) -> int:
            """将日期字符串转换为整数"""
            if '-' in strDate:
                return int(strDate.replace('-', ''))
            else:
                return int(strDate)
        
        def str_compare_date(_strDate1, _strDate2, _bEarlier):
            # 首先尝试简单格式的日期比较
            try:
                # 尝试直接比较日期部分（如果是YYYY-MM-DD格式）
                if '-' in _strDate1 and '-' in _strDate2:
                    date1_val = int_convert_date(_strDate1.split(' ')[0])
                    date2_val = int_convert_date(_strDate2.split(' ')[0])
                    if date1_val < date2_val:
                        return _strDate1 if _bEarlier else _strDate2
                    elif date1_val > date2_val:
                        return _strDate2 if _bEarlier else _strDate1
            except:
                pass
                
            # 如果简单比较失败，使用完整的日期时间转换
            def full_int_convert_date(_strDate):
                # 改进的日期时间转换函数，处理可能没有空格分隔的日期字符串
                try:
                    # 尝试按空格分割日期和时间
                    if " " in _strDate:
                        _date_part, _time_part = _strDate.split(" ")
                    else:
                        # 如果没有空格，尝试找到日期部分和时间部分的分割位置
                        _date_part = _strDate[:10]  # 提取YYYY-MM-DD部分
                        _time_part = _strDate[10:]  # 提取剩余的时间部分
                    
                    _cd1 = _date_part.split("-")
                    
                    # 清理时间部分，确保可以正确分割
                    if _time_part and ":" in _time_part:
                        _cd2 = _time_part.split(":")
                        return int("{}{:02}{:02}{:02}{:02}{:02}".format(
                            int(_cd1[0]), int(_cd1[1]), int(_cd1[2]),
                            int(_cd2[0]), int(_cd2[1]), int(_cd2[2])
                        ))
                    else:
                        # 如果时间部分格式不正确，使用默认值
                        return int("{}{:02}{:02}000000".format(
                            int(_cd1[0]), int(_cd1[1]), int(_cd1[2])
                        ))
                except (IndexError, ValueError) as e:
                    # 如果解析失败，记录错误并返回默认值
                    logging.error(f"日期解析错误: {_strDate}, 错误: {e}")
                    # 返回一个默认的日期时间值
                    return 20000101000000  # 2000-01-01 00:00:00
            
            if _strDate1 == _strDate2:
                _min_date = _strDate1
                _max_date = _strDate2
            else:
                _convert_date1 = full_int_convert_date(_strDate1)
                _convert_date2 = full_int_convert_date(_strDate2)
                if _convert_date1 < _convert_date2:
                    _min_date = _strDate1
                    _max_date = _strDate2
                else:
                    _min_date = _strDate2
                    _max_date = _strDate1
            if _bEarlier:
                return _min_date
            else:
                return _max_date

        # 处理时间戳
        listTimeStamp = [cycleBegin[2], cycleEnd[-1]]

        def b_is_in_range_milli_ampere(_floatInput, _floatStandard):
            _floatMin = _floatStandard*1.05
            _floatMax = _floatStandard*0.95
            if _floatMin <= _floatInput <= _floatMax:
                return True
            else:
                return False

        # analysis battery data
        battery_name = cycleCycle[0]
        
        # 优化：预计算负值的电流等级，避免重复计算
        neg_current_levels = [-float(level) for level in listCurrentLevel]
        
        # 优化：使用更高效的数据结构和算法
        for row in range(2, recordRows):
            step = recordStep[row]
            # 快速跳过非脉冲步骤
            if step != "脉冲" and step != "Pulse":
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

        # for Utility_XlsxWriter.py to write .xlsx
        listOneBatteryCharge = []

        def posi2_charge(intPosi, intCharge):
            if intPosi:
                _cycle = recordCycle[intPosi]
                for _c1 in range(2, cycleRows):
                    if cycleCycle[_c1] < _cycle:
                        intCharge += abs(cycleCharge[_c1])
                    if cycleCycle[_c1] >= _cycle:
                        break
                for _c2 in range(2, stepRows):
                    if stepCycle[_c2] == _cycle:
                        if stepStep[_c2] != "脉冲" and stepStep[_c2] != "Pulse":
                            intCharge += abs(stepCharge[_c2])
                    if stepCycle[_c2] > _cycle:
                        break
                intCharge += abs(recordCharge[intPosi])
                listOneBatteryCharge.append(round(intCharge))
            else:
                listOneBatteryCharge.append(0)

        for c in range(len(listCurrentLevel)):
            for v in range(len(listVoltageLevel)):
                posi2_charge(listLevelToRow[c][v], listLevelToCharge[c][v])

        # for Main_ImageShow.py to draw line chart
        def list_posi2_charge(listPosi):
            _listCharge = []
            for _i in range(len(listPosi)):
                _intTempCharge = 0
                _cycle = recordCycle[listPosi[_i]]
                for _c1 in range(2, cycleRows):
                    if cycleCycle[_c1] < _cycle:
                        _intTempCharge += abs(cycleCharge[_c1])
                    if cycleCycle[_c1] >= _cycle:
                        break
                for _c2 in range(2, stepRows):
                    if stepCycle[_c2] == _cycle:
                        if stepStep[_c2] != "脉冲" and stepStep[_c2] != "Pulse":
                            _intTempCharge += abs(stepCharge[_c2])
                    if stepCycle[_c2] > _cycle:
                        break
                _intTempCharge += abs(recordCharge[listPosi[_i]])
                _listCharge.append(_intTempCharge)
            return _listCharge

        for c in range(len(listCurrentLevel)):
            listChargeForInfoImageCsv[c] = list_posi2_charge(listPosiForInfoImageCsv[c])
            if len(listChargeForInfoImageCsv[c]) != len(listVoltageForInfoImageCsv[c]):
                from src.battery_analysis.utils.exception_type import BatteryAnalysisException
                raise BatteryAnalysisException(f"[Plt Data Error]: battery {battery_name} {listCurrentLevel[c]}mA pulse, charge is not equal to voltage")
        
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
                    return int("{}{:02}{:02}{:02}{:02}{:02}".format(
                        int(cd1[0]), int(cd1[1]), int(cd1[2]),
                        int(cd2[0]), int(cd2[1]), int(cd2[2])
                    ))
                else:
                    return int("{}{:02}{:02}000000".format(
                        int(cd1[0]), int(cd1[1]), int(cd1[2])
                    ))
            except Exception:
                return 20000101000000
        
        if strDate1 == strDate2:
            min_date = strDate1
            max_date = strDate2
        else:
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
        result = self._parallel_process_file((strPath, self.listCurrentLevel, self.listVoltageLevel))
        
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
                except Exception as e:
                    logging.error(f"解析原始cycle日期失败: {e}")
        else:
            # 更新最早和最晚时间
            self.listTimeStamp[0] = self._str_compare_date(timestamp_info[0], self.listTimeStamp[0], True)
            self.listTimeStamp[1] = self._str_compare_date(timestamp_info[1], self.listTimeStamp[1], False)
        
        # 记录日志
        self.UBA_Log(datetime.datetime.now().strftime("[%y-%m-%d %H:%M:%S]") + '\r')
        self.UBA_Log(f"Battery {battery_name}:\r")
        
        # 重建listLevelToVoltage和listLevelToRow用于日志输出
        listLevelToVoltage = []
        listLevelToRow = []
        for c in range(len(self.listCurrentLevel)):
            listLevelToVoltage.append([])
            listLevelToRow.append([])
            for v in range(len(self.listVoltageLevel)):
                # 从结果数据中提取电压和行信息
                listLevelToVoltage[c].append(self.listVoltageLevel[v])
                listLevelToRow[c].append(0)
                
                # 查找匹配的电压等级
                for posi, voltage in zip(posi_data[c], voltage_data[c]):
                    if voltage <= self.listVoltageLevel[v]:
                        listLevelToVoltage[c][v] = voltage
                        listLevelToRow[c][v] = posi
                        break
            
            self.UBA_Log(f"{self.listCurrentLevel[c]}mA - ")
            for v in range(len(self.listVoltageLevel)):
                self.UBA_Log(f"{listLevelToVoltage[c][v]}:{listLevelToRow[c][v] and listLevelToRow[c][v] + 1 or listLevelToRow[c][v]}, ")
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
        for b in range(len(self.listBatteryName)):
            csv_data.append(["BATTERY", self.listBatteryName[b]])
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
            with open(self.strResultLogTxt, "a") as f:
                f.writelines(self._log_buffer)
            # 清空缓冲区
            self._log_buffer = []
            self._log_buffer_size = 0
        except Exception as e:
            logging.error(f"写入日志文件失败: {e}")

    def __del__(self):
        """析构函数，确保日志缓冲区被刷新"""
        try:
            self._flush_log_buffer()
        except Exception:
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
        return [self.listAllBatteryCharge, self.listBatteryName, self.listTimeStamp, self.test_date, self.original_cycle_date]

    def UBA_GetErrorLog(self) -> str:
        return self.strErrorLog
