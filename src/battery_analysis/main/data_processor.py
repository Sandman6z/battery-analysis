"""
电池数据分析数据处理模块

本模块提供了用于电池数据分析的数据处理功能。它能够从CSV文件读取电池数据，
进行数据过滤和处理，并提供数据解析功能。

主要功能：
- 从CSV文件加载电池数据
- 解析电池名称
- 实现数据过滤算法
- 处理数据结构初始化
"""

import os
import csv
import logging
import traceback
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DataProcessor:
    """
    数据处理类，负责CSV数据的读取、解析和过滤
    """
    
    def __init__(self, csv_path, current_level_num):
        """
        初始化数据处理类
        
        Args:
            csv_path: CSV文件路径
            current_level_num: 电流级别数量
        """
        self.csv_path = csv_path
        self.current_level_num = current_level_num
        self.intBatteryNum = 0
        self.listBatteryName = []
        self.listBatteryNameSplit = []
        self.listPlt = []
        
    def initialize_data_structures(self):
        """
        初始化数据结构
        
        创建并初始化用于存储电池数据的数据结构。
        生成三维列表用于存储每个电流级别下所有电池的原始和过滤后的数据。
        列表结构: listPlt[电流级别][数据类型][电池索引][数据点]
        其中数据类型: 0-原始充电数据, 1-原始电压数据, 2-过滤后充电数据, 3-过滤后电压数据
        """
        self.listPlt = []
        self.listBatteryName = []
        self.listBatteryNameSplit = []
        
        for c in range(self.current_level_num):
            self.listPlt.append([])
            for _ in range(4):  # 0: 原始充电数据, 1: 原始电压数据, 2: 过滤后充电数据, 3: 过滤后电压数据
                self.listPlt[c].append([])
    
    def process_csv_data(self, csvreader):
        """
        处理CSV数据并填充到数据结构中
        
        从CSV读取器中处理数据并填充到数据结构中。将CSV中的数据按电池和电流级别分类，
        存储原始数据。处理过程中进行异常检测，跳过无效行，并记录警告日志。
        
        Args:
            csvreader: CSV数据读取器
        """
        intPerBatteryRows = 1 + self.current_level_num * 3
        index = 0
        
        for row in csvreader:
            loop = index % intPerBatteryRows
            if loop == 0:
                # 新电池的开始行
                if len(row) > 1:
                    self.listBatteryName.append(row[1].strip())
            else:
                # 数据行，根据格式规则填充数据
                if (loop % 3) != 1:
                    try:
                        current_idx = int((loop - 1) / 3)
                        data_idx = ((loop - 1) % 3) - 1
                        # 确保索引在有效范围内
                        if 0 <= current_idx < self.current_level_num and 0 <= data_idx < 4:
                            # 尝试将所有数据转换为float
                            float_data = [float(row[i]) for i in range(len(row))]
                            self.listPlt[current_idx][data_idx].append(float_data)
                    except (ValueError, IndexError) as e:
                        logging.warning(f"解析CSV行数据时出错: {e}，跳过此行")
            index += 1
    
    def csv_read(self):
        """
        从CSV文件读取数据
        
        数据处理流程：
        1. 检查CSV文件是否存在
        2. 初始化数据结构
        3. 读取并处理CSV数据
        4. 解析电池名称
        5. 过滤数据
        
        Returns:
            bool: 是否成功读取数据
        """
        try:
            logging.info(f"开始读取CSV文件: {self.csv_path}")
            
            # 检查文件是否存在
            csv_path = Path(self.csv_path)
            if not csv_path.exists():
                logging.error(f"错误: 找不到CSV文件 {self.csv_path}")
                self.intBatteryNum = 0
                return False
            
            # 检查文件大小
            file_size = csv_path.stat().st_size
            if file_size == 0:
                logging.error(f"错误: CSV文件 {self.csv_path} 为空")
                self.intBatteryNum = 0
                return False
            
            # 初始化数据结构
            self.initialize_data_structures()
            
            # 使用上下文管理器安全读取文件
            with open(csv_path, mode='r', encoding='utf-8') as f:
                csvreader = csv.reader(f)
                # 读取所有行以验证数据量
                all_rows = list(csvreader)
                if len(all_rows) < 5:  # 至少需要几行数据才可能包含有效电池信息
                    logging.error(f"错误: CSV文件 {self.csv_path} 数据行数不足")
                    self.intBatteryNum = 0
                    return False
                
                # 重置读取器以处理数据
                f.seek(0)
                csvreader = csv.reader(f)
                self.process_csv_data(csvreader)
            
            self.intBatteryNum = len(self.listBatteryName)
            
            # 检查是否读取到有效数据
            if self.intBatteryNum == 0:
                logging.error("错误: CSV文件中没有找到有效的电池信息")
                logging.warning("请确认CSV文件格式正确，包含电池测试数据")
                return False
            
            # 解析电池名称
            self.parse_battery_names()
            
            # 过滤数据
            self.filter_all_data()
            
            # 验证过滤后的数据
            data_valid = False
            for c in range(self.current_level_num):
                if c < len(self.listPlt) and self.listPlt[c][2]:  # 检查过滤后的数据
                    data_valid = True
                    break
            
            if not data_valid:
                logging.error("错误: 过滤后没有有效的电池数据可供显示")
                self.intBatteryNum = 0
                return False
            
            logging.info(f"成功读取并处理CSV数据，包含{self.intBatteryNum}个电池的真实测试数据")
            return True
            
        except FileNotFoundError:
            logging.error(f"错误: 文件未找到: {self.csv_path}")
            self.intBatteryNum = 0
            return False
        except PermissionError:
            logging.error(f"错误: 没有权限访问文件: {self.csv_path}")
            self.intBatteryNum = 0
            return False
        except Exception as e:
            logging.error(f"错误: 读取CSV文件时发生异常: {str(e)}")
            logging.error(f"错误类型: {type(e).__name__}")
            traceback.print_exc()
            self.intBatteryNum = 0
            return False
    
    def parse_battery_names(self):
        """
        解析电池名称，提取有意义的标识符
        
        从电池名称中提取有意义的部分，生成简洁易读的电池标识符。
        优先查找BTS标识后的部分，如果存在则提取其中的关键信息；
        如果不存在BTS标识，则使用名称的后部分或默认名称。
        处理过程中进行异常检测，确保即使解析失败也能返回有效的默认名称。
        """
        for b in range(self.intBatteryNum):
            try:
                # 尝试提取BTS后的标识符部分
                if "BTS" in self.listBatteryName[b]:
                    strBatteryNameSplit = self.listBatteryName[b].split("BTS")[1].split("_")
                    if len(strBatteryNameSplit) >= 4:
                        strBatteryName = f"{strBatteryNameSplit[2]}_{strBatteryNameSplit[3]}"
                    else:
                        # 如果分割后部分不足，使用可用部分
                        strBatteryName = "_".join(strBatteryNameSplit[1:3]) if len(strBatteryNameSplit) >= 3 else f"Battery_{b}"
                else:
                    # 如果没有BTS标识，使用原始名称的后部分或默认名称
                    name_parts = self.listBatteryName[b].split("_")
                    strBatteryName = "_".join(name_parts[-2:]) if len(name_parts) >= 2 else f"Battery_{b}"
                self.listBatteryNameSplit.append(strBatteryName)
            except Exception as e:
                logging.warning(f"解析电池名称时出错: {e}，使用默认名称")
                strBatteryName = f"Battery_{b}"
                self.listBatteryNameSplit.append(strBatteryName)
    
    def filter_data(self, list_plt_charge: list, list_plt_voltage: list, times=5, slope_max=0.2, difference_max=0.05):
        """
        过滤数据以去除异常值和噪声
        
        实现一个基于斜率和电压差异的过滤算法，用于去除电池数据中的异常值和噪声。
        通过多次迭代过滤，逐步平滑数据曲线，同时保留数据的整体趋势。
        
        Args:
            list_plt_charge: 充电数据列表
            list_plt_voltage: 电压数据列表
            times: 过滤迭代次数，默认为5次
            slope_max: 允许的最大斜率，默认为0.2
            difference_max: 允许的最大电压差异，默认为0.05
            
        Returns:
            tuple: 过滤后的充电数据和电压数据
        """
        filtered_charge = []
        filtered_voltage = []
        
        for p in range(len(list_plt_charge)):
            charge_single = list_plt_charge[p]
            voltage_single = list_plt_voltage[p]
            current_times = times
            
            while current_times > 0:
                charge_temp = [charge_single[0]]
                voltage_temp = [voltage_single[0]]
                
                for c in range(1, len(charge_single)):
                    # 计算斜率，避免除以零
                    charge_diff = charge_single[c] - charge_single[c - 1]
                    if charge_diff == 0:
                        slope = slope_max
                    else:
                        slope = abs((voltage_single[c] - voltage_single[c - 1]) / charge_diff)
                    
                    # 根据斜率和电压差异进行过滤
                    if slope < slope_max and abs(voltage_single[c] - voltage_single[c - 1]) < difference_max:
                        charge_temp.append(charge_single[c])
                        voltage_temp.append(voltage_single[c])
                
                charge_single = charge_temp
                voltage_single = voltage_temp
                current_times -= 1
            
            filtered_charge.append(charge_single)
            filtered_voltage.append(voltage_single)
        
        return filtered_charge, filtered_voltage
    
    def filter_all_data(self):
        """
        过滤所有电池的数据
        
        对所有电池数据应用过滤算法。遍历每个电流级别和电池的数据，
        应用filter_data方法进行数据平滑处理，去除异常值和噪声。
        处理过程中进行异常检测，确保单个电池数据处理失败不会影响整体处理流程。
        """
        for c in range(self.current_level_num):
            try:
                # 检查数据是否有效
                if c < len(self.listPlt) and len(self.listPlt[c]) >= 4:
                    if self.listPlt[c][0] and self.listPlt[c][1]:
                        self.listPlt[c][2], self.listPlt[c][3] = self.filter_data(self.listPlt[c][0], self.listPlt[c][1])
            except Exception as e:
                logging.error(f"过滤数据时出错 (电流级别 {c}): {e}")