"""
电池数据分析图像显示模块

本模块提供了用于电池数据分析和可视化的主要功能。它能够从CSV文件读取电池数据，
进行数据过滤和处理，生成模拟数据，并创建交互式图表进行数据可视化。

主要功能：
- 从CSV文件加载电池数据
- 支持配置文件读取和自定义配置
- 实现数据过滤算法
- 生成模拟电池数据
- 创建交互式图表，支持数据点悬停、曲线切换等功能

依赖：
- matplotlib: 用于图表绘制
- csv: 用于CSV文件读取
- pathlib: 用于文件路径处理
- logging: 用于日志记录
- traceback: 用于错误跟踪
- configparser: 用于配置文件解析
- math: 用于数学计算
"""

import os
import csv
import sys
import math
import traceback
import configparser
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import CheckButtons

# 尝试导入异常类，如果失败则定义一个简单的异常类
try:
    # 尝试相对导入
    from ..utils.exception_type import BatteryAnalysisException
except ImportError:
    try:
        # 尝试绝对导入
        from src.battery_analysis.utils.exception_type import BatteryAnalysisException
    except ImportError:
        # 如果都失败，定义一个简单的异常类
        class BatteryAnalysisException(Exception):
            """电池分析异常类"""
            pass


class FIGURE:
    """
    图表生成和数据可视化类
    
    这个类负责电池数据的可视化处理，包括配置文件读取、数据加载、过滤和图表生成。
    支持从CSV文件读取实际数据或生成模拟数据，并提供交互式图表界面进行数据分析。
    
    属性:
        strPltName: 图表标题名称
        listColor: 图表颜色列表
        maxXaxis: X轴最大值
        listPlt: 图表数据列表
        listBatteryNameSplit: 电池名称列表
        intBatteryNum: 电池数量
        intCurrentLevelNum: 电流级别数量
        listAxis: 坐标轴范围
        listXTicks: X轴刻度值
    """
    
    def __init__(self):
        """
        初始化FIGURE类，设置默认配置并加载用户配置
        
        初始化图表参数，读取配置文件，并设置默认值。如果配置文件不存在，
        将使用硬编码的默认值。
        """
        self.config = configparser.ConfigParser()
        
        # 初始化默认配置
        if not self.config.has_section("PltConfig"):
            self.config.add_section("PltConfig")
        
        # 获取项目根目录的config文件夹路径
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.project_root = current_dir.parent.parent
        self.path = self.project_root
        
        # 加载配置文件
        self._load_config_file()
        
        # 读取配置项
        self._read_configurations()
        
        # 设置其他初始化参数
        self.listColor = ['#DF7040', '#0675BE', '#EDB120', '#7E2F8E', '#32CD32', '#FF4500', '#000000', '#000000']
        self.maxXaxis = 1000  # 默认最大值
        self._read_rules_configuration()
    
    def _load_config_file(self):
        """
        加载配置文件，优先使用setting.ini，其次是Config_BatteryAnalysis.ini
        
        尝试从项目根目录的config文件夹读取配置文件，首先查找setting.ini，
        如果不存在则尝试查找Config_BatteryAnalysis.ini。如果两个文件都不存在，
        则使用默认配置并记录警告日志。
        
        异常处理：捕获配置文件读取过程中可能出现的所有异常，并记录错误日志。
        """
        try:
            # 优先读取setting.ini（发布模式）
            setting_ini_path = self.project_root / "config" / "setting.ini"
            if setting_ini_path.exists():
                self.config.read(setting_ini_path, encoding='utf-8')
                logging.info("成功读取setting.ini配置")
            else:
                # 如果找不到，尝试使用绝对路径（确保在任何位置都能找到）
                abs_setting_ini_path = Path(__file__).resolve().parent.parent.parent / "config" / "setting.ini"
                if abs_setting_ini_path.exists():
                    self.config.read(abs_setting_ini_path, encoding='utf-8')
                    logging.info("成功读取绝对路径下的setting.ini配置")
                return
            
            # 回退到Config_BatteryAnalysis.ini（兼容旧版本）
            config_path = self.project_root / "config" / "Config_BatteryAnalysis.ini"
            if config_path.exists():
                self.config.read(config_path, encoding='utf-8')
                logging.info("成功读取Config_BatteryAnalysis.ini配置")
                return
            
            logging.warning("未找到配置文件，使用默认配置")
        except Exception as e:
            logging.error(f"配置读取失败: {e}，使用默认配置")
    
    def _read_configurations(self):
        """
        读取所有配置项并设置默认值
        
        从加载的配置文件中读取图表路径、标题、脉冲电流级别、电池规格类型等配置项，
        并为每个配置项设置合理的默认值。
        
        配置项包括：
        - 图表路径和标题
        - CSV文件路径
        - 脉冲电流级别配置
        - 电池规格类型配置（纽扣电池和软包电池）
        """
        # 读取图表路径配置
        self.strPltPath = self._get_config_value("PltConfig", "Path", os.getcwd())
        
        # 读取图表标题配置
        self.strPltTitle = self._get_config_value("PltConfig", "Title", "Battery Test Results")
        
        # 设置CSV文件路径
        self.strInfoImageCsvPath = os.path.join(self.strPltPath, "Info_Image.csv")
        
        # 读取脉冲电流级别配置
        self.listPulseCurrentLevel = self._get_pulse_current_level()
        self.intCurrentLevelNum = len(self.listPulseCurrentLevel)
        
        # 读取电池规格类型配置
        self.listCoinCell = self._get_config_list("BatteryConfig", "SpecificationTypeCoinCell")
        self.listPouchCell = self._get_config_list("BatteryConfig", "SpecificationTypePouchCell")
        
        # 设置图表标题
        self.strPltName = self._set_plot_title()
    
    def _get_config_value(self, section, option, default_value):
        """
        安全获取配置值，如果不存在则返回默认值
        
        从配置文件中读取指定section和option的值。如果section或option不存在，
        或者读取过程中出现异常，则返回提供的默认值并记录相应的日志信息。
        
        Args:
            section (str): 配置文件中的section名称
            option (str): 配置项名称
            default_value: 默认值，当配置项不存在时返回
            
        Returns:
            配置值或默认值
        """
        try:
            if self.config.has_section(section) and self.config.has_option(section, option):
                value = self.config.get(section, option)
                logging.debug(f"获取配置 {section}/{option}: {value}")
                return value
            else:
                logging.warning(f"未找到配置 {section}/{option}，使用默认值: {default_value}")
                return default_value
        except Exception as e:
            logging.error(f"读取配置 {section}/{option} 出错: {e}，使用默认值: {default_value}")
            return default_value
    
    def _get_config_list(self, section, option):
        """安全获取配置列表，如果不存在则返回空列表"""
        try:
            if self.config.has_section(section) and self.config.has_option(section, option):
                list_value = self.config.get(section, option).split(",")
                cleaned_list = [item.strip() for item in list_value]
                logging.debug(f"获取配置列表 {section}/{option}: {cleaned_list}")
                return cleaned_list
            else:
                logging.warning(f"未找到配置列表 {section}/{option}，使用空列表")
                return []
        except Exception as e:
            logging.error(f"读取配置列表 {section}/{option} 出错: {e}，使用空列表")
            return []
    
    def _get_pulse_current_level(self):
        """获取脉冲电流级别配置"""
        try:
            if self.config.has_section("BatteryConfig") and self.config.has_option("BatteryConfig", "PulseCurrent"):
                listPulseCurrentLevel = self.config.get("BatteryConfig", "PulseCurrent").split(",")
                result = [int(item.strip()) for item in listPulseCurrentLevel]
                logging.info(f"使用配置的脉冲电流级别: {result}")
                return result
            else:
                default_value = [10, 20, 50]
                logging.warning(f"未找到BatteryConfig/PulseCurrent，使用默认值: {default_value}")
                return default_value
        except Exception as e:
            default_value = [10, 20, 50]
            logging.error(f"脉冲电流配置格式错误: {e}，使用默认值: {default_value}")
            return default_value
    
    def _set_plot_title(self):
        """设置图表标题，处理引号情况"""
        try:
            # 尝试移除前后引号（如果存在）
            if len(self.strPltTitle) >= 2 and self.strPltTitle[0] == '"' and self.strPltTitle[-1] == '"':
                title_content = self.strPltTitle[1:-1]
            else:
                title_content = self.strPltTitle
            return f"Load Voltage over Charge\n{title_content}"
        except Exception as e:
            default_title = "Load Voltage over Charge\nUnknown Battery"
            logging.error(f"设置图表标题出错: {e}，使用默认标题: {default_title}")
            return default_title
    
    def _read_rules_configuration(self):
        """读取并处理规则配置"""
        try:
            if self.config.has_section("BatteryConfig") and self.config.has_option("BatteryConfig", "Rules"):
                listRules = self.config.get("BatteryConfig", "Rules").split(",")
                self._process_rules(listRules)
            else:
                logging.warning("未找到BatteryConfig/Rules，使用默认maxXaxis")
        except Exception as e:
            logging.error(f"读取Rules配置出错: {e}，使用默认maxXaxis")
    
    def _process_rules(self, listRules):
        """根据规则配置处理maxXaxis"""
        try:
            if len(self.strPltName.split(" ")) > 4:
                spec_type = self.strPltName.split(" ")[4]
                for rule in listRules:
                    if spec_type in rule and "/" in rule:
                        rule_parts = rule.split("/")
                        if len(rule_parts) > 2:
                            try:
                                self.maxXaxis = int(rule_parts[2])
                                logging.info(f"根据规则设置maxXaxis: {self.maxXaxis}")
                                break
                            except ValueError:
                                logging.warning(f"规则中的maxXaxis值无效: {rule_parts[2]}")
        except Exception as e:
            logging.error(f"处理规则时出错: {e}，保持默认maxXaxis")

        self.listPlt = []
        self.listBatteryName = []
        self.listBatteryNameSplit = []
        self.intBatteryNum = 0

        try:
            self.csv_read()
            
            # 检查是否有有效的电池数据，只有在有数据时才继续处理
            if self.intBatteryNum <= 0:
                logging.error("没有有效的电池数据，无法生成图表")
                return
            
            bMatchSpecificationType = False
            strSpecificationType = self.strPltName.split(" ")[4]
            for c in range(len(self.listCoinCell)):
                if self.listCoinCell[c] == strSpecificationType:
                    self.listAxis = [10, 600, 1, 3]
                    self.listXTicks = [10, 100, 200, 300, 400, 500, 600]
                    bMatchSpecificationType = True
                    break
            if not bMatchSpecificationType:
                for p in range(len(self.listPouchCell)):
                    if self.listPouchCell[p] == strSpecificationType:
                        maxTicks = math.ceil(self.maxXaxis/100)*100
                        self.listAxis = [20, maxTicks, 1, 3]
                        self.listXTicks = [20]
                        if maxTicks <= 1000:
                            for i in range(1, 11):
                                self.listXTicks.append(i*100)
                                if i*100 >= maxTicks:
                                    break
                        elif maxTicks <= 2000:
                            for i in range(1, 11):
                                self.listXTicks.append(i*200)
                                if i*200 >= maxTicks:
                                    break
                        elif maxTicks <= 3000:
                            for i in range(1, 11):
                                self.listXTicks.append(i*300)
                                if i*300 >= maxTicks:
                                    break
                        elif maxTicks <= 4000:
                            for i in range(1, 11):
                                self.listXTicks.append(i*400)
                                if i*400 >= maxTicks:
                                    break
                        else:
                            for i in range(1, 11):
                                self.listXTicks.append(i*500)
                                if i*500 >= maxTicks:
                                    break
                        bMatchSpecificationType = True
                        break
            if bMatchSpecificationType:
                self.plt_figure()
            else:
                logging.warning("未找到匹配的规格类型，使用默认配置继续展示")
                # 设置默认的规格参数
                self.intCurrentLevelNum = 3
                self.intMaxXaxis = 5000
                self.listXTicks = list(range(0, 5001, 500))
                self.listAxis = [0, self.intMaxXaxis, 2.5, 4.5]  # 设置默认坐标轴范围
                self.plt_figure()
            
        except BaseException as e:
            self.errorlog = str(e)
            logging.error(f"处理数据时出错: {e}")
            traceback.print_exc()

    def csv_read(self):
        """
        从CSV文件读取数据
        
        数据处理流程：
        1. 检查CSV文件是否存在
        2. 初始化数据结构
        3. 读取并处理CSV数据
        4. 解析电池名称
        5. 过滤数据
        
        重要说明：此方法仅使用CSV文件中的真实数据，不会生成或使用任何模拟数据。
        如果CSV文件不存在或读取失败，会记录错误并返回，不会自动生成替代数据。
        异常处理：捕获读取和处理过程中可能出现的所有异常，并记录详细日志。
        """
        try:
            logging.info(f"开始读取CSV文件: {self.strInfoImageCsvPath}")
            
            # 检查文件是否存在
            csv_path = Path(self.strInfoImageCsvPath)
            if not csv_path.exists():
                logging.error(f"错误: 找不到CSV文件 {self.strInfoImageCsvPath}")
                self.intBatteryNum = 0
                return
            
            # 检查文件大小
            file_size = csv_path.stat().st_size
            if file_size == 0:
                logging.error(f"错误: CSV文件 {self.strInfoImageCsvPath} 为空")
                self.intBatteryNum = 0
                return
            
            # 初始化数据结构
            self._initialize_data_structures()
            
            # 使用上下文管理器安全读取文件
            with open(csv_path, mode='r', encoding='utf-8') as f:
                csvreader = csv.reader(f)
                # 读取所有行以验证数据量
                all_rows = list(csvreader)
                if len(all_rows) < 5:  # 至少需要几行数据才可能包含有效电池信息
                    logging.error(f"错误: CSV文件 {self.strInfoImageCsvPath} 数据行数不足")
                    self.intBatteryNum = 0
                    return
                
                # 重置读取器以处理数据
                f.seek(0)
                csvreader = csv.reader(f)
                self._process_csv_data(csvreader)
            
            self.intBatteryNum = len(self.listBatteryName)
            
            # 检查是否读取到有效数据
            if self.intBatteryNum == 0:
                logging.error("错误: CSV文件中没有找到有效的电池信息")
                logging.warning("请确认CSV文件格式正确，包含电池测试数据")
                return
            
            # 解析电池名称
            self._parse_battery_names()
            
            # 过滤数据
            self._filter_all_data()
            
            # 验证过滤后的数据
            data_valid = False
            for c in range(self.intCurrentLevelNum):
                if c < len(self.listPlt) and self.listPlt[c][2]:  # 检查过滤后的数据
                    data_valid = True
                    break
            
            if not data_valid:
                logging.error("错误: 过滤后没有有效的电池数据可供显示")
                self.intBatteryNum = 0
                return
            
            logging.info(f"成功读取并处理CSV数据，包含{self.intBatteryNum}个电池的真实测试数据")
        except FileNotFoundError:
            logging.error(f"错误: 文件未找到: {self.strInfoImageCsvPath}")
            self.intBatteryNum = 0
        except PermissionError:
            logging.error(f"错误: 没有权限访问文件: {self.strInfoImageCsvPath}")
            self.intBatteryNum = 0
        except Exception as e:
            logging.error(f"错误: 读取CSV文件时发生异常: {str(e)}")
            logging.error(f"错误类型: {type(e).__name__}")
            traceback.print_exc()
            self.intBatteryNum = 0
    
    def _initialize_data_structures(self):
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
        
        for c in range(self.intCurrentLevelNum):
            self.listPlt.append([])
            for _ in range(4):  # 0: 原始充电数据, 1: 原始电压数据, 2: 过滤后充电数据, 3: 过滤后电压数据
                self.listPlt[c].append([])
    
    def _process_csv_data(self, csvreader):
        """
        处理CSV数据并填充到数据结构中
        
        从CSV读取器中处理数据并填充到数据结构中。将CSV中的数据按电池和电流级别分类，
        存储原始数据。处理过程中进行异常检测，跳过无效行，并记录警告日志。
        
        Args:
            csvreader: CSV数据读取器
        """
        intPerBatteryRows = 1 + self.intCurrentLevelNum * 3
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
                        if 0 <= current_idx < self.intCurrentLevelNum and 0 <= data_idx < 4:
                            # 尝试将所有数据转换为float
                            float_data = [float(row[i]) for i in range(len(row))]
                            self.listPlt[current_idx][data_idx].append(float_data)
                    except (ValueError, IndexError) as e:
                        logging.warning(f"解析CSV行数据时出错: {e}，跳过此行")
            index += 1
    
    def _parse_battery_names(self):
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
    
    def _filter_all_data(self):
        """
        过滤所有电池的数据
        
        对所有电池数据应用过滤算法。遍历每个电流级别和电池的数据，
        应用filter_data方法进行数据平滑处理，去除异常值和噪声。
        处理过程中进行异常检测，确保单个电池数据处理失败不会影响整体处理流程。
        """
        for c in range(self.intCurrentLevelNum):
            try:
                # 检查数据是否有效
                if c < len(self.listPlt) and len(self.listPlt[c]) >= 4:
                    if self.listPlt[c][0] and self.listPlt[c][1]:
                        self.listPlt[c][2], self.listPlt[c][3] = self.filter_data(self.listPlt[c][0], self.listPlt[c][1])
            except Exception as e:
                logging.error(f"过滤数据时出错 (电流级别 {c}): {e}")
    



    def plt_figure(self):
        """创建并显示电池数据图表，包含交互控件以切换数据显示
        
        重要说明：此方法只使用CSV文件中的真实数据，不会生成或显示任何模拟数据。
        如果没有有效的电池数据或绘图过程中出错，会显示详细的错误信息和故障排除建议。
        """
        try:
            logging.info("开始绘制图表，仅使用CSV文件中的真实数据")
            
            # 执行多层次的数据有效性检查
            if self.intBatteryNum <= 0:
                logging.error("严重错误: 没有有效的电池数据可供显示")
                logging.warning("请注意: 此程序仅使用CSV文件中的真实数据，不会生成模拟数据")
                self._show_error_plot()
                return
            
            # 检查必要的数据结构是否有效
            if not hasattr(self, 'listPlt') or not self.listPlt:
                logging.error("严重错误: 电池数据结构未初始化或为空")
                self._show_error_plot()
                return
            
            # 初始化图表和轴
            try:
                fig, ax, title_fontdict, axis_fontdict = self._initialize_figure()
                if fig is None or ax is None:
                    raise ValueError("无法初始化图表或坐标轴")
            except Exception as init_error:
                logging.error(f"图表初始化失败: {str(init_error)}")
                self._show_error_plot()
                return
            
            # 绘制电池数据曲线
            try:
                lines_unfiltered, lines_filtered = self._plot_battery_curves(ax)
                valid_data_found = bool(lines_filtered) or bool(lines_unfiltered)
                
                if valid_data_found:
                    logging.info(f"成功绘制了 {len(lines_filtered)} 条过滤曲线和 {len(lines_unfiltered)} 条原始曲线")
            except Exception as plot_error:
                logging.error(f"绘制电池曲线时出错: {str(plot_error)}")
                lines_unfiltered, lines_filtered = [], []
                valid_data_found = False
            
            # 检查是否成功绘制了曲线
            if not valid_data_found:
                logging.error("严重错误: 无法绘制任何电池数据曲线")
                self._show_error_plot()
                return
            
            # 添加交互控件
            try:
                check_filter = self._add_filter_button(fig, ax, lines_unfiltered, lines_filtered, title_fontdict, axis_fontdict)
                check_line1, check_line2 = self._add_battery_selection_buttons(
                    fig, check_filter, lines_unfiltered, lines_filtered
                )
                self._add_hover_functionality(fig, ax, lines_filtered, lines_unfiltered, check_filter)
                logging.info("成功添加图表交互控件")
            except Exception as ui_error:
                logging.warning(f"添加交互控件时出错: {str(ui_error)}")
                # 即使交互控件添加失败，仍然尝试显示图表
            
            # 添加快捷键提示
            fig.text(0.01, 0.98, "快捷键: 滚轮缩放, 鼠标拖拽平移, 右键重置视图", fontsize=8)
            
            logging.info("图表创建完成，显示CSV文件中的真实电池测试数据")
            plt.show()
        
        except Exception as e:
            logging.error(f"严重错误: 绘制图表时发生未预期的异常: {str(e)}")
            logging.error(f"错误类型: {type(e).__name__}")
            traceback.print_exc()
            self._show_error_plot()
            
    def _show_error_plot(self, title=None, main_message=None, details=None):
        """
        显示详细的错误信息图表，提供清晰的错误反馈和故障排除建议
        
        Args:
            title (str, optional): 错误标题，默认为"数据错误"
            main_message (str, optional): 主要错误信息，默认为"无法加载或显示电池数据"
            details (str, optional): 详细错误信息和故障排除建议
        """
        try:
            # 设置默认错误信息
            if title is None:
                title = "数据错误"
            if main_message is None:
                main_message = "无法加载或显示电池数据"
            if details is None:
                details = "1. CSV文件是否存在且格式正确\n"
                details += "2. 配置文件是否正确配置\n"
                details += "3. 文件路径是否包含中文字符或特殊字符\n"
                details += "4. CSV文件是否包含有效的电池测试数据"
            
            # 创建错误图表
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 设置图表标题
            ax.set_title(title, fontsize=16, fontweight='bold', color='#d32f2f')
            
            # 隐藏坐标轴
            ax.axis('off')
            
            # 构建完整的错误信息文本
            full_text = f"{main_message}\n\n"
            full_text += "故障排除步骤:\n"
            full_text += details
            
            # 添加重要提示
            full_text += "\n\n"
            full_text += "重要提示: 此程序仅使用CSV文件中的真实数据，"
            full_text += "不会生成或使用任何模拟数据。"
            
            # 显示错误日志信息（如果有）
            if hasattr(self, 'errorlog') and self.errorlog:
                full_text += f"\n\n错误详情: {str(self.errorlog)}"
            
            # 显示错误信息
            ax.text(0.5, 0.5, full_text, fontsize=12, ha='center', va='center', 
                   wrap=True, linespacing=1.4)
            
            # 添加版本信息和时间戳
            import datetime
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fig.text(0.01, 0.01, f"Battery Analysis Tool v1.0 | {current_time}", 
                    fontsize=8, color='gray')
            
            # 添加边框和样式
            for spine in ax.spines.values():
                spine.set_color('#ff5722')
                spine.set_linewidth(1)
            
            logging.info(f"显示错误信息图表: {title} - {main_message}")
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            logging.critical(f"显示错误图表时发生异常: {str(e)}")
            traceback.print_exc()
            # 如果连错误图表都无法显示，尝试使用简单的文本输出
            logging.error("\n严重错误: 无法显示图形界面的错误信息")
            logging.error(f"错误详情: {title or '未知错误'} - {main_message or '无法加载数据'}")
            logging.info("\n请检查以下事项:")
            logging.info("1. Python环境是否正确安装")
            logging.info("2. Matplotlib库是否可用")
            logging.info("3. CSV文件是否存在且格式正确")
            logging.info("4. 系统是否有足够的资源显示图形")
    
    def _initialize_figure(self):
        """初始化图表设置和布局"""
        # 设置字体样式
        title_fontdict = {'fontsize': 15, 'fontweight': 'bold'}
        axis_fontdict = {'fontsize': 15}
        
        # 创建图表并设置标题
        fig = plt.figure(figsize=(15, 6))
        fig.canvas.manager.window.setWindowTitle("Filtered Load Voltage over Charge")
        
        # 清理并设置网格布局
        plt.clf()
        gs = fig.add_gridspec(1, 40)
        ax = fig.add_subplot(gs[:, 5:])  # 留出左侧空间给按钮
        
        # 设置坐标轴范围和刻度
        ax.axis(self.listAxis)
        x_ticks = self.listXTicks
        ax.set_xticks(x_ticks)
        
        # 设置Y轴主刻度
        y_major_locator = MultipleLocator(0.2)
        ax.yaxis.set_major_locator(y_major_locator)
        
        # 设置标题和标签
        ax.set_title(f"Filtered {self.strPltName}", fontdict=title_fontdict)
        ax.set_xlabel("Charge [mAh]", fontdict=axis_fontdict)
        ax.set_ylabel("Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)
        
        # 添加网格线
        ax.grid(linestyle="--", alpha=0.3)
        
        return fig, ax, title_fontdict, axis_fontdict
    
    def _plot_battery_curves(self, ax):
        """绘制所有电池的原始和过滤后的曲线"""
        lines_unfiltered = []
        lines_filtered = []
        
        for b in range(self.intBatteryNum):
            for c in range(self.intCurrentLevelNum):
                try:
                    # 绘制原始数据曲线（默认隐藏）
                    ul, = ax.plot(
                        self.listPlt[c][0][b], 
                        self.listPlt[c][1][b], 
                        color=self.listColor[c] if c < len(self.listColor) else f'C{c}',
                        label=[f'{self.listBatteryNameSplit[b]}', 'Unfiltered'], 
                        visible=False, 
                        linewidth=0.5
                    )
                    lines_unfiltered.append(ul)
                    
                    # 绘制过滤后的数据曲线（默认显示）
                    fl, = ax.plot(
                        self.listPlt[c][2][b], 
                        self.listPlt[c][3][b], 
                        color=self.listColor[c] if c < len(self.listColor) else f'C{c}',
                        label=[f'{self.listBatteryNameSplit[b]}', 'Filtered'], 
                        visible=True, 
                        linewidth=0.5
                    )
                    lines_filtered.append(fl)
                except Exception as e:
                    logging.error(f"绘制电池 {b}, 电流级别 {c} 的曲线时出错: {e}")
        
        return lines_unfiltered, lines_filtered
    
    def _add_filter_button(self, fig, ax, lines_unfiltered, lines_filtered, title_fontdict, axis_fontdict):
        """添加过滤/未过滤数据切换按钮"""
        labels_filter = ["       Filtered"]
        visibility_filter = [True]
        
        # 创建按钮区域
        rax_filter = plt.axes([0.001, 0.933, 0.16, 0.062])
        check_filter = CheckButtons(rax_filter, labels_filter, visibility_filter)
        
        # 回调函数：处理过滤/未过滤切换
        def func_filter(label):
            try:
                if check_filter.get_status()[0]:
                    # 切换到过滤模式
                    fig.canvas.manager.window.setWindowTitle("Filtered Load Voltage over Charge")
                    ax.set_title(f"Filtered {self.strPltName}", fontdict=title_fontdict)
                    ax.set_ylabel("Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)
                    
                    # 更新线条可见性
                    for i in range(min(len(lines_unfiltered), len(lines_filtered))):
                        lines_filtered[i].set_visible(lines_unfiltered[i].get_visible())
                        lines_unfiltered[i].set_visible(False)
                else:
                    # 切换到未过滤模式
                    fig.canvas.manager.window.setWindowTitle("Unfiltered Load Voltage over Charge")
                    ax.set_title(f"Unfiltered {self.strPltName}", fontdict=title_fontdict)
                    ax.set_ylabel("Unfiltered Battery Load Voltage [V]", fontdict=axis_fontdict)
                    
                    # 更新线条可见性
                    for i in range(min(len(lines_filtered), len(lines_unfiltered))):
                        lines_unfiltered[i].set_visible(lines_filtered[i].get_visible())
                        lines_filtered[i].set_visible(False)
                
                fig.canvas.draw_idle()
            except Exception as e:
                logging.error(f"执行过滤切换时出错: {e}")
        
        check_filter.on_clicked(func_filter)
        return check_filter
    
    def _add_battery_selection_buttons(self, fig, check_filter, lines_unfiltered, lines_filtered):
        """添加电池选择按钮，用于显示/隐藏特定电池的数据曲线"""
        # 初始化默认值
        check_line1 = None
        check_line2 = None
        
        # 根据电池数量创建不同的按钮布局
        if self.intBatteryNum > 32:
            # 创建第一个按钮区域（前32个电池）
            check_line1 = self._create_battery_check_buttons(
                fig, [0.001, 0.005, 0.08, 0.029*32], 0, 32, 
                check_filter, lines_unfiltered, lines_filtered
            )
            
            # 创建第二个按钮区域（剩余电池，最多32个）
            check_line2 = self._create_battery_check_buttons(
                fig, [0.081, 0.005, 0.08, 0.029*32], 32, 64, 
                check_filter, lines_unfiltered, lines_filtered
            )
        else:
            # 创建单个按钮区域
            check_line1 = self._create_battery_check_buttons(
                fig, [0.001, 0.005, 0.08, 0.029*32], 0, 32, 
                check_filter, lines_unfiltered, lines_filtered
            )
            
            # 创建空的第二个按钮区域
            rax_line2 = plt.axes([0.081, 0.005, 0.08, 0.029*32])
            labels_line2 = ["None"] * 32
            visibility_line2 = [False] * 32
            check_line2 = CheckButtons(rax_line2, labels_line2, visibility_line2)
            
            # 空按钮区域的回调函数
            def func_line2_empty(label):
                for i in range(0, 32):
                    if check_line2.get_status()[i]:
                        check_line2.set_active(i)
            
            check_line2.on_clicked(func_line2_empty)
        
        return check_line1, check_line2
    
    def _create_battery_check_buttons(self, fig, rect, start_idx, end_idx, 
                                    check_filter, lines_unfiltered, lines_filtered):
        """创建电池选择检查按钮"""
        labels_line = []
        visibility_line = []
        
        # 准备按钮标签和初始可见性
        for i in range(start_idx, end_idx):
            if i < self.intBatteryNum:
                labels_line.append(self.listBatteryNameSplit[i])
                visibility_line.append(True)
            else:
                labels_line.append("None")
                visibility_line.append(False)
        
        # 创建按钮区域
        rax = plt.axes(rect)
        check_buttons = CheckButtons(rax, labels_line, visibility_line)
        
        # 回调函数
        def func_line(label):
            try:
                # 处理空标签
                if label == "None":
                    # 确保所有"None"项都处于未选中状态
                    for i in range(min(self.intBatteryNum, end_idx) - start_idx, end_idx - start_idx):
                        if check_buttons.get_status()[i]:
                            check_buttons.set_active(i)
                    return
                
                # 根据当前模式（过滤/未过滤）更新对应线条的可见性
                current_lines = lines_filtered if check_filter.get_status()[0] else lines_unfiltered
                
                for i in range(len(current_lines)):
                    try:
                        # 安全地获取和比较标签
                        line_label = current_lines[i].get_label()
                        if isinstance(line_label, list) and len(line_label) > 0:
                            # 处理标签为列表的情况
                            if label == line_label[0]:
                                current_lines[i].set_visible(not current_lines[i].get_visible())
                        elif isinstance(line_label, str):
                            # 处理标签为字符串的情况
                            if label in line_label:
                                current_lines[i].set_visible(not current_lines[i].get_visible())
                    except Exception as inner_e:
                        # 忽略单个线条处理错误，继续处理其他线条
                        logging.debug(f"处理线条标签时出错: {inner_e}")
                
                fig.canvas.draw_idle()
            except Exception as e:
                logging.error(f"执行电池选择时出错: {e}")
        
        check_buttons.on_clicked(func_line)
        return check_buttons
    
    def _add_hover_functionality(self, fig, ax, lines_filtered, lines_unfiltered, check_filter):
        """添加鼠标悬停功能，显示数据点信息"""
        try:
            # 创建注释对象
            annot = ax.annotate(
                '', xy=(0, 0), xytext=(10, 10),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->')
            )
            annot.set_visible(False)
            
            # 悬停回调函数
            def on_hover(event):
                if event.inaxes == ax:
                    # 获取当前可见的线条
                    current_lines = lines_filtered if check_filter.get_status()[0] else lines_unfiltered
                    
                    # 查找最近的数据点
                    min_dist = float('inf')
                    closest_point = None
                    closest_line_label = None
                    
                    for line in current_lines:
                        if line.get_visible():
                            try:
                                x_data = line.get_xdata()
                                y_data = line.get_ydata()
                                line_label = line.get_label()
                                
                                # 查找距离鼠标最近的点
                                for i, (x, y) in enumerate(zip(x_data, y_data)):
                                    dist = ((x - event.xdata)**2 + (y - event.ydata)** 2)**0.5
                                    # 只考虑一定范围内的点
                                    if dist < min_dist and dist < 0.05 * (self.maxXaxis - self.listAxis[0]):
                                        min_dist = dist
                                        closest_point = (x, y, i)
                                        closest_line_label = line_label
                            except Exception:
                                continue  # 忽略处理单个线条时的错误
                    
                    # 更新注释
                    if closest_point:
                        x, y, idx = closest_point
                        annot.xy = (x, y)
                        
                        # 格式化标签显示
                        label_text = ""
                        if isinstance(closest_line_label, list) and len(closest_line_label) > 0:
                            label_text = f"{closest_line_label[0]}"
                            if len(closest_line_label) > 1:
                                label_text += f" ({closest_line_label[1]})"
                        else:
                            label_text = str(closest_line_label)
                        
                        annot.set_text(f"{label_text}\n点 {idx}:\nCharge: {x:.2f} mAh\nVoltage: {y:.4f} V")
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                    else:
                        if annot.get_visible():
                            annot.set_visible(False)
                            fig.canvas.draw_idle()
            
            # 连接事件
            fig.canvas.mpl_connect('motion_notify_event', on_hover)
            
            # 添加提示文本
            fig.text(0.01, 0.96, "提示: 将鼠标悬停在数据点上查看详细信息", fontsize=7)
            
        except Exception as e:
            logging.warning(f"添加悬停功能时出错: {e}")
    
    # 注意：_show_error_plot方法已在前面定义，此方法已更新为增强版


if __name__ == '__main__':
    """
    主程序入口
    
    创建FIGURE类实例，自动执行初始化、数据读取和图表显示操作。
    """
    FIGURE()
