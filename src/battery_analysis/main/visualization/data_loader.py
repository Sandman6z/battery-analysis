"""
数据加载模块

提供CSV文件读取、配置加载、数据解析和过滤方法
"""

import logging
import os
import csv
import json
import traceback
from pathlib import Path

from battery_analysis.utils.processors.data_utils import build_plot_title

logger = logging.getLogger(__name__)


class DataLoaderMixin:
    """数据加载混入类，提供数据加载、解析和过滤方法"""

    def set_data_path(self, data_path):
        """设置数据路径并更新CSV文件路径"""
        logger.info("Setting data path: %s", data_path)
        self.strPltPath = data_path
        self.strInfoImageCsvPath = os.path.join(
            self.strPltPath, "Info_Image.csv")
        logger.info("Updated CSV file path: %s", self.strInfoImageCsvPath)
        # 当数据路径改变时，尝试加载元数据以更新动态标题
        self._try_load_metadata_title()
        self.strPltName = self._set_plot_title()

    def load_data(self):
        """加载数据并处理，为绘制图表做准备"""
        self.listPlt = []
        self.listBatteryName = []
        self.listBatteryNameSplit = []
        self.intBatteryNum = 0

        try:
            self.csv_read()

            if self.intBatteryNum <= 0:
                logger.error("No valid battery data, cannot generate chart")
                return False

            self._read_rules_configuration()
            return True
        except (IOError, ValueError, TypeError, OSError) as e:
            self.errorlog = str(e)
            logger.error("Error loading data: %s", e)
            traceback.print_exc()
            return False

    def _load_config_file(self):
        """通过 ConfigService 加载配置，存储服务引用供后续使用"""
        try:
            from battery_analysis.main.services.service_container import get_service_container
            container = get_service_container()
            config_service = container.get("config")

            if config_service is not None:
                config_service.load_config(use_cache=True)
                self._config_service = config_service
                logger.info("Successfully read configuration via ConfigService")
            else:
                logger.warning("ConfigService unavailable, using empty configuration")
                self._config_service = None
        except (ImportError, AttributeError, TypeError) as e:
            logger.error("Failed to read configuration: %s, using default configuration", e)
            self._config_service = None

    def _read_configurations(self):
        """读取所有配置项并设置默认值"""
        # PltConfig 已不再持久化，使用当前工作目录
        self.strPltPath = os.getcwd()

        self.strPltTitle = "Battery Test Results"

        self.strInfoImageCsvPath = os.path.join(
            self.strPltPath, "Info_Image.csv")

        # 尝试从元数据文件读取动态标题（优先于配置中的静态标题）
        self._try_load_metadata_title()

        self.listPulseCurrentLevel = self._get_pulse_current_level()
        self.intCurrentLevelNum = len(self.listPulseCurrentLevel)

        svc = getattr(self, '_config_service', None)
        if svc is not None:
            specs = svc.get_config_value("battery.specifications", {})
            self.listCoinCell = specs.get("Coin Cell", [])
            self.listPouchCell = specs.get("Pouch Cell", [])
        else:
            self.listCoinCell = []
            self.listPouchCell = []

        self.strPltName = self._set_plot_title()

    def _try_load_metadata_title(self):
        """尝试从 Info_Plot.json 读取测试元数据以构建动态标题"""
        try:
            meta_path = os.path.join(self.strPltPath, "Info_Plot.json")
            if not os.path.exists(meta_path):
                return

            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            manufacturer = meta.get("manufacturer", "")
            spec_type = meta.get("spec_type", "")
            spec_method = meta.get("spec_method", "")
            batch_code = meta.get("batch_code", "")
            capacity = meta.get("capacity", "")
            temperature = meta.get("temperature", "")

            title_base = build_plot_title(
                manufacturer=manufacturer,
                spec_type=spec_type,
                spec_method=spec_method,
                batch_code=batch_code,
                capacity=capacity,
                temperature=temperature,
            )

            if title_base.strip():
                self.strPltTitle = title_base
                logger.info("Loaded dynamic title from metadata file: %s", self.strPltTitle)
        except (IOError, json.JSONDecodeError, TypeError, ValueError) as e:
            logger.warning("Failed to read metadata file, using default title: %s", e)

    def _get_pulse_current_level(self):
        """获取脉冲电流级别配置"""
        svc = getattr(self, '_config_service', None)
        if svc is not None:
            try:
                levels = svc.get_config_value("battery.pulseCurrents", [10, 20, 50])
                if levels:
                    logger.info("Using configured pulse current levels: %s", levels)
                    return levels
            except (ValueError, TypeError, AttributeError) as e:
                logger.error("Invalid pulse current configuration format: %s, using default value", e)
        default_value = [10, 20, 50]
        logger.warning("Using default pulse current levels: %s", default_value)
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
            logger.error("Error setting chart title: %s, using default title: %s", e, default_title)
            return default_title

    def _read_rules_configuration(self):
        """读取并处理规则配置"""
        svc = getattr(self, '_config_service', None)
        if svc is not None:
            try:
                rules = svc.get_config_value("battery.rules", [])
                if rules:
                    self._process_rules(rules)
                    return
            except (ValueError, TypeError, AttributeError) as e:
                logger.error("Error reading Rules configuration: %s, using default maxXaxis", e)
        logger.warning("battery.rules not found, using default maxXaxis")

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
                                    "Setting maxXaxis based on rule: %s", self.maxXaxis)
                                self.listAxis = [self.plot_config.axis_special[0], self.maxXaxis, self.plot_config.axis_special[2], 5.0]
                                self.listXTicks = list(
                                    range(0, self.maxXaxis + 1, 100))
                                break
                            except ValueError:
                                logger.warning(
                                    "Invalid maxXaxis value in rule: %s", rule_parts[2])
        except (ValueError, IndexError, TypeError) as e:
            logger.error("Error processing rules: %s, keeping default maxXaxis", e)

    def csv_read(self):
        """从CSV文件读取数据"""
        try:
            logger.info("Starting to read CSV file: %s", self.strInfoImageCsvPath)

            csv_path = Path(self.strInfoImageCsvPath)
            if not csv_path.exists():
                logger.error("Error: CSV file not found %s", self.strInfoImageCsvPath)
                self.intBatteryNum = 0
                return

            file_size = csv_path.stat().st_size
            if file_size == 0:
                logger.error("Error: CSV file %s is empty", self.strInfoImageCsvPath)
                self.intBatteryNum = 0
                return

            self._initialize_data_structures()

            with open(csv_path, mode='r', encoding='utf-8') as f:
                csvreader = csv.reader(f)
                all_rows = list(csvreader)
                if len(all_rows) < 5:
                    logger.error(
                        "Error: CSV file %s has insufficient data rows", self.strInfoImageCsvPath)
                    self.intBatteryNum = 0
                    return

                f.seek(0)
                csvreader = csv.reader(f)
                self._process_csv_data(csvreader)

            self.intBatteryNum = len(self.listBatteryName)

            if self.intBatteryNum == 0:
                logger.error("Error: no valid battery info found in CSV file")
                return

            self._parse_battery_names()
            self._filter_all_data()

            data_valid = False
            for c in range(self.intCurrentLevelNum):
                if c < len(self.listPlt) and self.listPlt[c][2]:
                    data_valid = True
                    break

            if not data_valid:
                logger.error("Error: no valid battery data available for display after filtering")
                self.intBatteryNum = 0
                return

            self.last_data_path = self.strPltPath
            if self.strInfoImageCsvPath:
                import datetime
                try:
                    if os.path.exists(self.strInfoImageCsvPath):
                        timestamp = os.path.getmtime(self.strInfoImageCsvPath)
                        self.last_data_timestamp = timestamp
                        logger.info("Updating data timestamp: %s", datetime.datetime.fromtimestamp(timestamp))
                except Exception as e:
                    logger.warning("Error updating data timestamp: %s", e)

            logger.info("Successfully read and processed CSV data with %d batteries of real test data", self.intBatteryNum)
        except FileNotFoundError:
            logger.error("Error: file not found: %s", self.strInfoImageCsvPath)
            self.intBatteryNum = 0
        except PermissionError:
            logger.error("Error: no permission to access file: %s", self.strInfoImageCsvPath)
            self.intBatteryNum = 0
        except (IOError, ValueError, TypeError, UnicodeDecodeError) as e:
            logger.error("Error: exception occurred while reading CSV file: %s", str(e))
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
                        logger.warning("Error parsing CSV row data: %s, skipping this row", e)
            index += 1

    def _parse_battery_names(self):
        """解析电池名称，提取有意义的标识符"""
        for b in range(self.intBatteryNum):
            try:
                if "BTS" in self.listBatteryName[b]:
                    strBatteryNameSplit = self.listBatteryName[b].split("BTS")[
                        1].split("_")
                    if len(strBatteryNameSplit) >= 4:
                        strBatteryName = f"{strBatteryNameSplit[2]}-{strBatteryNameSplit[3]}"
                    else:
                        strBatteryName = "-".join(strBatteryNameSplit[1:3]) if len(
                            strBatteryNameSplit) >= 3 else f"Battery-{b}"
                else:
                    name_parts = self.listBatteryName[b].split("_")
                    strBatteryName = "-".join(
                        name_parts[-2:]) if len(name_parts) >= 2 else f"Battery-{b}"
                self.listBatteryNameSplit.append(strBatteryName)
            except (IndexError, TypeError, AttributeError, ValueError) as e:
                logger.warning("Error parsing battery name: %s, using default name", e)
                self.listBatteryNameSplit.append(f"Battery-{b}")

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
                logger.error("Error filtering data (current level %s): %s", c, e)

    def _search_for_data_files(self):
        """搜索项目中可能存在的Info_Image.csv文件"""
        try:
            logger.info("Starting to search for Info_Image.csv files in the project...")

            for root, dirs, files in os.walk(self.project_root):
                if ".venv" in root or ".git" in root or "__pycache__" in root:
                    continue
                if "Info_Image.csv" in files:
                    info_image_csv = os.path.join(root, "Info_Image.csv")
                    logger.info("Found Info_Image.csv file in project: %s", info_image_csv)
                    self.set_data_path(os.path.dirname(info_image_csv))
                    success = self.load_data()
                    if success:
                        self.loaded_data = True
                        logger.info("Successfully loaded found data file")
                        return
                    else:
                        logger.warning("Found data file but failed to load it")

            logger.info("Not found in project root, trying to search in current directory...")
            for root, dirs, files in os.walk(os.getcwd()):
                if ".venv" in root or ".git" in root or "__pycache__" in root:
                    continue
                if "Info_Image.csv" in files:
                    info_image_csv = os.path.join(root, "Info_Image.csv")
                    logger.info("Found Info_Image.csv file in current directory: %s", info_image_csv)
                    self.set_data_path(os.path.dirname(info_image_csv))
                    success = self.load_data()
                    if success:
                        self.loaded_data = True
                        logger.info("Successfully loaded found data file")
                        return
                    else:
                        logger.warning("Found data file but failed to load it")

            logger.warning("No valid Info_Image.csv file found in project")
        except (OSError, ValueError, TypeError) as e:
            logger.error("Error searching for data files: %s", str(e))
            traceback.print_exc()
