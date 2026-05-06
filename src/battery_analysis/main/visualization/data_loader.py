"""
数据加载模块

提供CSV文件读取、配置加载、数据解析和过滤方法
"""

import logging
import os
import csv
import configparser
import traceback
from pathlib import Path

from battery_analysis.utils.config_parser import parse_pulse_current_config
from battery_analysis.utils.config_utils import find_config_file

logger = logging.getLogger(__name__)


class DataLoaderMixin:
    """数据加载混入类，提供数据加载、解析和过滤方法"""

    def set_data_path(self, data_path):
        """设置数据路径并更新CSV文件路径"""
        logger.info("设置数据路径: %s", data_path)
        self.strPltPath = data_path
        self.strInfoImageCsvPath = os.path.join(
            self.strPltPath, "Info_Image.csv")
        logger.info("更新后的CSV文件路径: %s", self.strInfoImageCsvPath)

    def load_data(self):
        """加载数据并处理，为绘制图表做准备"""
        self.listPlt = []
        self.listBatteryName = []
        self.listBatteryNameSplit = []
        self.intBatteryNum = 0

        try:
            self.csv_read()

            if self.intBatteryNum <= 0:
                logger.error("没有有效的电池数据，无法生成图表")
                return False

            self._read_rules_configuration()
            return True
        except (IOError, ValueError, TypeError, OSError) as e:
            self.errorlog = str(e)
            logger.error("加载数据时出错: %s", e)
            traceback.print_exc()
            return False

    def _load_config_file(self):
        """加载配置文件，优先使用setting.ini，其次是Config_BatteryAnalysis.ini"""
        try:
            setting_ini_path = find_config_file()
            if setting_ini_path and os.path.exists(setting_ini_path):
                self.config.read(setting_ini_path, encoding='utf-8')
                logger.info("成功读取setting.ini配置")
                return

            config_battery_path = find_config_file(
                "Config_BatteryAnalysis.ini")
            if config_battery_path and os.path.exists(config_battery_path):
                self.config.read(config_battery_path, encoding='utf-8')
                logger.info("成功读取Config_BatteryAnalysis.ini配置")
                return

            logger.warning("未找到配置文件，使用默认配置")
        except (IOError, UnicodeDecodeError, configparser.Error) as e:
            logger.error("配置读取失败: %s，使用默认配置", e)

    def _read_configurations(self):
        """读取所有配置项并设置默认值"""
        self.strPltPath = self._get_config_value(
            "PltConfig", "Path", os.getcwd())

        self.strPltTitle = self._get_config_value(
            "PltConfig", "Title", "Battery Test Results")

        self.strInfoImageCsvPath = os.path.join(
            self.strPltPath, "Info_Image.csv")

        self.listPulseCurrentLevel = self._get_pulse_current_level()
        self.intCurrentLevelNum = len(self.listPulseCurrentLevel)

        self.listCoinCell = self._get_config_list(
            "BatteryConfig", "SpecificationTypeCoinCell")
        self.listPouchCell = self._get_config_list(
            "BatteryConfig", "SpecificationTypePouchCell")

        self.strPltName = self._set_plot_title()

    def _get_config_value(self, section, option, default_value):
        """安全获取配置值，如果不存在则返回默认值"""
        try:
            if self.config.has_section(section) and self.config.has_option(section, option):
                value = self.config.get(section, option)
                logger.debug("获取配置 %s/%s: %s", section, option, value)
                return value
            else:
                logger.warning(
                    "未找到配置 %s/%s，使用默认值: %s", section, option, default_value)
                return default_value
        except (configparser.Error, TypeError, ValueError) as e:
            logger.error(
                "读取配置 %s/%s 出错: %s，使用默认值: %s", section, option, e, default_value)
            return default_value

    def _get_config_list(self, section, option):
        """安全获取配置列表，如果不存在则返回空列表"""
        try:
            if self.config.has_section(section) and self.config.has_option(section, option):
                list_value = self.config.get(section, option).split(",")
                cleaned_list = [item.strip() for item in list_value]
                logger.debug("获取配置列表 %s/%s: %s", section,
                              option, cleaned_list)
                return cleaned_list
            else:
                logger.warning("未找到配置列表 %s/%s，使用空列表", section, option)
                return []
        except (configparser.Error, TypeError, ValueError) as e:
            logger.error("读取配置列表 %s/%s 出错: %s，使用空列表", section, option, e)
            return []

    def _get_pulse_current_level(self):
        """获取脉冲电流级别配置"""
        try:
            if (self.config.has_section("BatteryConfig")
                    and self.config.has_option("BatteryConfig", "PulseCurrent")):
                result = parse_pulse_current_config(self.config)
                logger.info("使用配置的脉冲电流级别: %s", result)
                return result
            else:
                default_value = [10, 20, 50]
                logger.warning(
                    "未找到BatteryConfig/PulseCurrent，使用默认值: %s", default_value)
                return default_value
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            default_value = [10, 20, 50]
            logger.error("脉冲电流配置格式错误: %s，使用默认值: %s", e, default_value)
            return default_value

    def _set_plot_title(self):
        """设置图表标题，处理引号情况"""
        try:
            if (len(self.strPltTitle) >= 2
                and self.strPltTitle[0] == '"'
                    and self.strPltTitle[-1] == '"'):
                title_content = self.strPltTitle[1:-1]
            else:
                title_content = self.strPltTitle
            return f"Load Voltage over Charge\n{title_content}"
        except (TypeError, IndexError, AttributeError, ValueError) as e:
            default_title = "Load Voltage over Charge\nUnknown Battery"
            logger.error("设置图表标题出错: %s，使用默认标题: %s", e, default_title)
            return default_title

    def _read_rules_configuration(self):
        """读取并处理规则配置"""
        try:
            if (self.config.has_section("BatteryConfig")
                    and self.config.has_option("BatteryConfig", "Rules")):
                listRules = self.config.get(
                    "BatteryConfig", "Rules").split(",")
                self._process_rules(listRules)
            else:
                logger.warning("未找到BatteryConfig/Rules，使用默认maxXaxis")
        except (configparser.Error, AttributeError, TypeError, ValueError) as e:
            logger.error("读取Rules配置出错: %s，使用默认maxXaxis", e)

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
                                logger.info(
                                    "根据规则设置maxXaxis: %s", self.maxXaxis)
                                self.listAxis = [self.plot_config.axis_special[0], self.maxXaxis, self.plot_config.axis_special[2], 5.0]
                                self.listXTicks = list(
                                    range(0, self.maxXaxis + 1, 100))
                                break
                            except ValueError:
                                logger.warning(
                                    "规则中的maxXaxis值无效: %s", rule_parts[2])
        except (ValueError, IndexError, TypeError) as e:
            logger.error("处理规则时出错: %s，保持默认maxXaxis", e)

    def csv_read(self):
        """从CSV文件读取数据"""
        try:
            logger.info("开始读取CSV文件: %s", self.strInfoImageCsvPath)

            csv_path = Path(self.strInfoImageCsvPath)
            if not csv_path.exists():
                logger.error("错误: 找不到CSV文件 %s", self.strInfoImageCsvPath)
                self.intBatteryNum = 0
                return

            file_size = csv_path.stat().st_size
            if file_size == 0:
                logger.error("错误: CSV文件 %s 为空", self.strInfoImageCsvPath)
                self.intBatteryNum = 0
                return

            self._initialize_data_structures()

            with open(csv_path, mode='r', encoding='utf-8') as f:
                csvreader = csv.reader(f)
                all_rows = list(csvreader)
                if len(all_rows) < 5:
                    logger.error(
                        "错误: CSV文件 %s 数据行数不足", self.strInfoImageCsvPath)
                    self.intBatteryNum = 0
                    return

                f.seek(0)
                csvreader = csv.reader(f)
                self._process_csv_data(csvreader)

            self.intBatteryNum = len(self.listBatteryName)

            if self.intBatteryNum == 0:
                logger.error("错误: CSV文件中没有找到有效的电池信息")
                return

            self._parse_battery_names()
            self._filter_all_data()

            data_valid = False
            for c in range(self.intCurrentLevelNum):
                if c < len(self.listPlt) and self.listPlt[c][2]:
                    data_valid = True
                    break

            if not data_valid:
                logger.error("错误: 过滤后没有有效的电池数据可供显示")
                self.intBatteryNum = 0
                return

            self.last_data_path = self.strPltPath
            if self.strInfoImageCsvPath:
                import datetime
                try:
                    if os.path.exists(self.strInfoImageCsvPath):
                        timestamp = os.path.getmtime(self.strInfoImageCsvPath)
                        self.last_data_timestamp = timestamp
                        logger.info("更新数据时间戳: %s", datetime.datetime.fromtimestamp(timestamp))
                except Exception as e:
                    logger.warning("更新数据时间戳时出错: %s", e)

            logger.info("成功读取并处理CSV数据，包含%d个电池的真实测试数据", self.intBatteryNum)
        except FileNotFoundError:
            logger.error("错误: 文件未找到: %s", self.strInfoImageCsvPath)
            self.intBatteryNum = 0
        except PermissionError:
            logger.error("错误: 没有权限访问文件: %s", self.strInfoImageCsvPath)
            self.intBatteryNum = 0
        except (IOError, ValueError, TypeError, UnicodeDecodeError) as e:
            logger.error("错误: 读取CSV文件时发生异常: %s", str(e))
            traceback.print_exc()
            self.intBatteryNum = 0

    def _initialize_data_structures(self):
        """初始化数据结构"""
        self.listPlt = []
        self.listBatteryName = []
        self.listBatteryNameSplit = []

        for c in range(self.intCurrentLevelNum):
            self.listPlt.append([])
            for _ in range(4):
                self.listPlt[c].append([])

    def _process_csv_data(self, csvreader):
        """处理CSV数据并填充到数据结构中"""
        intPerBatteryRows = 1 + self.intCurrentLevelNum * 3
        index = 0

        for row in csvreader:
            loop = index % intPerBatteryRows
            if loop == 0:
                if len(row) > 1:
                    self.listBatteryName.append(row[1].strip())
            else:
                if (loop % 3) != 1:
                    try:
                        current_idx = int((loop - 1) / 3)
                        data_idx = ((loop - 1) % 3) - 1
                        if 0 <= current_idx < self.intCurrentLevelNum and 0 <= data_idx < 4:
                            float_data = []
                            for i in range(len(row)):
                                try:
                                    float_data.append(float(row[i]))
                                except ValueError:
                                    continue
                            if float_data:
                                self.listPlt[current_idx][data_idx].append(float_data)
                    except IndexError as e:
                        logger.warning("解析CSV行数据时出错: %s，跳过此行", e)
            index += 1

    def _parse_battery_names(self):
        """解析电池名称，提取有意义的标识符"""
        for b in range(self.intBatteryNum):
            try:
                if "BTS" in self.listBatteryName[b]:
                    strBatteryNameSplit = self.listBatteryName[b].split("BTS")[
                        1].split("_")
                    if len(strBatteryNameSplit) >= 4:
                        strBatteryName = f"{strBatteryNameSplit[2]}_{strBatteryNameSplit[3]}"
                    else:
                        strBatteryName = "_".join(strBatteryNameSplit[1:3]) if len(
                            strBatteryNameSplit) >= 3 else f"Battery_{b}"
                else:
                    name_parts = self.listBatteryName[b].split("_")
                    strBatteryName = "_".join(
                        name_parts[-2:]) if len(name_parts) >= 2 else f"Battery_{b}"
                self.listBatteryNameSplit.append(strBatteryName)
            except (IndexError, TypeError, AttributeError, ValueError) as e:
                logger.warning("解析电池名称时出错: %s，使用默认名称", e)
                self.listBatteryNameSplit.append(f"Battery_{b}")

    def filter_data(self, list_plt_charge, list_plt_voltage,
                    times=5, slope_max=0.2, difference_max=0.05):
        """过滤数据以去除异常值和噪声"""
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
                    try:
                        charge_curr = float(charge_single[c])
                        charge_prev = float(charge_single[c - 1])
                        voltage_curr = float(voltage_single[c])
                        voltage_prev = float(voltage_single[c - 1])

                        charge_diff = charge_curr - charge_prev
                        if charge_diff == 0:
                            slope = slope_max
                        else:
                            voltage_diff = voltage_curr - voltage_prev
                            slope = abs(voltage_diff / charge_diff)

                        voltage_diff_abs = abs(voltage_diff)
                        if slope < slope_max and voltage_diff_abs < difference_max:
                            charge_temp.append(charge_curr)
                            voltage_temp.append(voltage_curr)
                    except (ValueError, TypeError):
                        continue

                charge_single = charge_temp
                voltage_single = voltage_temp
                current_times -= 1

            filtered_charge.append(charge_single)
            filtered_voltage.append(voltage_single)

        return filtered_charge, filtered_voltage

    def _filter_all_data(self):
        """过滤所有电池的数据"""
        for c in range(self.intCurrentLevelNum):
            try:
                if c < len(self.listPlt) and len(self.listPlt[c]) >= 4:
                    if self.listPlt[c][0] and self.listPlt[c][1]:
                        self.listPlt[c][2], self.listPlt[c][3] = self.filter_data(
                            self.listPlt[c][0], self.listPlt[c][1])
            except (ValueError, TypeError, IndexError) as e:
                logger.error("过滤数据时出错 (电流级别 %s): %s", c, e)

    def _search_for_data_files(self):
        """搜索项目中可能存在的Info_Image.csv文件"""
        try:
            logger.info("开始搜索项目中的Info_Image.csv文件...")

            for root, dirs, files in os.walk(self.project_root):
                if ".venv" in root or ".git" in root or "__pycache__" in root:
                    continue
                if "Info_Image.csv" in files:
                    info_image_csv = os.path.join(root, "Info_Image.csv")
                    logger.info("在项目中找到Info_Image.csv文件: %s", info_image_csv)
                    self.set_data_path(os.path.dirname(info_image_csv))
                    success = self.load_data()
                    if success:
                        self.loaded_data = True
                        logger.info("成功加载找到的数据文件")
                        return
                    else:
                        logger.warning("找到数据文件但加载失败")

            logger.info("在项目根目录下未找到，尝试在当前目录下搜索...")
            for root, dirs, files in os.walk(os.getcwd()):
                if ".venv" in root or ".git" in root or "__pycache__" in root:
                    continue
                if "Info_Image.csv" in files:
                    info_image_csv = os.path.join(root, "Info_Image.csv")
                    logger.info("在当前目录下找到Info_Image.csv文件: %s", info_image_csv)
                    self.set_data_path(os.path.dirname(info_image_csv))
                    success = self.load_data()
                    if success:
                        self.loaded_data = True
                        logger.info("成功加载找到的数据文件")
                        return
                    else:
                        logger.warning("找到数据文件但加载失败")

            logger.warning("在项目中未找到任何有效的Info_Image.csv文件")
        except (OSError, ValueError, TypeError) as e:
            logger.error("搜索数据文件时出错: %s", str(e))
            traceback.print_exc()
