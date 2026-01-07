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


# 标准库导入
import sys
import logging
from pathlib import Path
import configparser
import traceback
import csv
import os

# 第三方库导入
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import FancyBboxPatch

# 本地库导入
from battery_analysis.utils.config_parser import parse_pulse_current_config
from battery_analysis.utils.config_utils import find_config_file

# 使用QtAgg后端，它会自动检测可用的Qt绑定（包括PyQt6）
# 必须在导入pyplot之前设置后端
matplotlib.use('QtAgg')

# 配置matplotlib支持中文显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei',
                                          'Microsoft YaHei', 'DejaVu Sans', 'Arial', 'Times New Roman']
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 现代化按钮样式配置 - 增强版 v4.1
MODERN_BUTTON_STYLE = {
    # 按钮状态颜色 - 更现代的配色方案
    'active_color': '#4CAF50',       # 现代绿色 - 激活状态
    'inactive_color': '#FAFAFA',     # 极浅灰白 - 未激活状态
    'hover_color': '#66BB6A',        # 中等绿色 - 悬停状态
    'pressed_color': '#2E7D32',      # 深绿色 - 按下状态
    
    # 文字颜色 - 增强对比度
    'active_text_color': '#FFFFFF',   # 激活时白色文字
    'inactive_text_color': '#424242', # 深灰文字 - 未激活状态
    'hover_text_color': '#FFFFFF',    # 悬停时白色文字
    'pressed_text_color': '#FFFFFF',  # 按下时白色文字
    
    # 边框样式 - 现代化边框
    'border_color': '#E0E0E0',        # 浅灰边框
    'border_width': 1.5,              # 稍加粗边框
    'border_radius': 8,               # 更大圆角半径
    
    # 阴影效果 - 更明显的阴影
    'shadow_color': '0.15',
    'shadow_offset': (0, 2),
    'shadow_blur': 3,
    
    # 字体样式 - 现代化字体
    'font_size': 9,                   # 适中字体大小
    'font_weight': '600',             # 更粗字重
    
    # 布局参数 - 优化间距
    'padding': 4,                     # 增加内部边距
    'spacing': 2,                     # 适中间距
    
    # 新增：渐变效果
    'gradient_start': 'rgba(255,255,255,0.9)',   # 渐变开始颜色
    'gradient_end': 'rgba(250,250,250,0.9)',     # 渐变结束颜色
    'active_gradient_start': 'rgba(76,175,80,0.9)', # 激活渐变开始
    'active_gradient_end': 'rgba(102,187,106,0.9)', # 激活渐变结束
    
    # 新增：特殊按钮颜色
    'success_color': '#4CAF50',       # 成功按钮（绿）
    'warning_color': '#FF9800',       # 警告按钮（橙）
    'info_color': '#2196F3',          # 信息按钮（蓝）
    'danger_color': '#F44336',        # 危险按钮（红）
    
    # 新增：状态指示
    'selected_indicator': '#FFD54F',   # 选中指示器颜色
    'focus_outline': '#2196F3',       # 焦点轮廓颜色
}

# 开启Matplotlib的交互模式
plt.ion()

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class BatteryChartViewer:
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
        plot_config: 图表配置对象
    """

    class PlotConfig:
        """
        图表配置类，用于存储可配置的图表参数
        
        属性:
            axis_default: 默认坐标轴范围 [xmin, xmax, ymin, ymax]
            axis_special: 特殊规则下的坐标轴范围 [xmin, xmax, ymin, ymax]
        """
        def __init__(self):
            # 默认坐标轴范围
            self.axis_default = [10, 600, 0, 5]  # [xmin, xmax, ymin, ymax]
            # 特殊规则下的坐标轴范围
            self.axis_special = [10, 600, 1, 3]  # [xmin, xmax, ymin, ymax]

    def __init__(self, data_path=None, auto_search=True):
        """
        初始化BatteryChartViewer类，设置默认配置并加载用户配置

        初始化图表参数，读取配置文件，并设置默认值。如果配置文件不存在，
        将使用硬编码的默认值。

        Args:
            data_path: 可选，指定要加载数据的目录路径
            auto_search: 是否自动搜索数据文件，默认为True
        """
        # 保存auto_search参数
        self.auto_search = auto_search
        
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

        # 初始化图表配置对象
        self.plot_config = self.PlotConfig()
        
        # 设置其他初始化参数
        self.listColor = ['#DF7040', '#0675BE', '#EDB120',
                          '#7E2F8E', '#32CD32', '#FF4500', '#000000', '#000000']
        self.maxXaxis = self.plot_config.axis_default[1]  # 默认最大值
        self.intBatteryNum = 0  # 默认没有电池数据
        self.loaded_data = False  # 数据加载状态标记
        self.current_fig = None  # 当前图表实例引用

        # 初始化坐标轴范围和刻度
        # [xmin, xmax, ymin, ymax]
        self.listAxis = [self.plot_config.axis_default[0], self.maxXaxis, self.plot_config.axis_default[2], self.plot_config.axis_default[3]]  # 使用配置的坐标轴范围
        self.listXTicks = list(range(0, self.maxXaxis + 1, 100))  # X轴刻度值

        # 先初始化默认数据结构
        self.listPlt = []
        self.listBatteryName = []
        self.listBatteryNameSplit = []
        self.strPltPath = None
        self.strInfoImageCsvPath = None

        # 读取配置项
        self._read_configurations()

        # 如果提供了数据路径，覆盖配置文件中的路径
        if data_path is not None:
            logging.info("初始化时接收到数据路径: %s", data_path)
            self.set_data_path(data_path)
            success = self.load_data()
            if success:
                self.loaded_data = True
                logging.info("初始化数据加载成功")
            else:
                logging.warning("初始化数据加载失败")
                # 仅当auto_search为True时才搜索
                if auto_search:
                    self._search_for_data_files()
        else:
            # 默认不加载任何数据，只初始化基本参数
            logging.info("初始化时未提供数据路径，不加载数据")
            # 仅当auto_search为True时才搜索
            if auto_search:
                self._search_for_data_files()

    def set_data_path(self, data_path):
        """
        设置数据路径并更新CSV文件路径

        Args:
            data_path: 要设置的数据目录路径
        """
        logging.info("设置数据路径: %s", data_path)
        self.strPltPath = data_path
        self.strInfoImageCsvPath = os.path.join(
            self.strPltPath, "Info_Image.csv")
        logging.info("更新后的CSV文件路径: %s", self.strInfoImageCsvPath)

    def load_data(self):
        """
        加载数据并处理，为绘制图表做准备

        Returns:
            bool: 是否成功加载数据
        """
        self.listPlt = []
        self.listBatteryName = []
        self.listBatteryNameSplit = []
        self.intBatteryNum = 0

        try:
            self.csv_read()

            # 检查是否有有效的电池数据，只有在有数据时才继续处理
            if self.intBatteryNum <= 0:
                logging.error("没有有效的电池数据，无法生成图表")
                return False

            # 读取并处理规则配置
            self._read_rules_configuration()
            return True
        except (IOError, ValueError, TypeError, OSError) as e:
            self.errorlog = str(e)
            logging.error("加载数据时出错: %s", e)
            traceback.print_exc()
            return False

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
            setting_ini_path = find_config_file()
            if setting_ini_path and os.path.exists(setting_ini_path):
                self.config.read(setting_ini_path, encoding='utf-8')
                logging.info("成功读取setting.ini配置")
                # setting.ini存在时，不检查Config_BatteryAnalysis.ini
                return

            # 如果setting.ini不存在，尝试查找Config_BatteryAnalysis.ini（兼容旧版本）
            config_battery_path = find_config_file(
                "Config_BatteryAnalysis.ini")
            if config_battery_path and os.path.exists(config_battery_path):
                self.config.read(config_battery_path, encoding='utf-8')
                logging.info("成功读取Config_BatteryAnalysis.ini配置")
                return

            logging.warning("未找到配置文件，使用默认配置")
        except (IOError, UnicodeDecodeError, configparser.Error) as e:
            logging.error("配置读取失败: %s，使用默认配置", e)

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
        self.strPltPath = self._get_config_value(
            "PltConfig", "Path", os.getcwd())

        # 读取图表标题配置
        self.strPltTitle = self._get_config_value(
            "PltConfig", "Title", "Battery Test Results")

        # 设置CSV文件路径
        self.strInfoImageCsvPath = os.path.join(
            self.strPltPath, "Info_Image.csv")

        # 读取脉冲电流级别配置
        self.listPulseCurrentLevel = self._get_pulse_current_level()
        self.intCurrentLevelNum = len(self.listPulseCurrentLevel)

        # 读取电池规格类型配置
        self.listCoinCell = self._get_config_list(
            "BatteryConfig", "SpecificationTypeCoinCell")
        self.listPouchCell = self._get_config_list(
            "BatteryConfig", "SpecificationTypePouchCell")

        # 设置图表标题
        self.strPltName = self._set_plot_title()

    def get_axis_default(self):
        """
        获取默认坐标轴范围
        
        Returns:
            list: 默认坐标轴范围 [xmin, xmax, ymin, ymax]
        """
        return self.plot_config.axis_default
    
    def set_axis_default(self, xmin, xmax, ymin, ymax):
        """
        设置默认坐标轴范围
        
        Args:
            xmin: X轴最小值
            xmax: X轴最大值
            ymin: Y轴最小值
            ymax: Y轴最大值
        """
        self.plot_config.axis_default = [xmin, xmax, ymin, ymax]
        # 如果当前使用的是默认范围，同步更新当前listAxis
        if self.listAxis[0] == self.plot_config.axis_default[0] and self.listAxis[2] == self.plot_config.axis_default[2] and self.listAxis[3] == self.plot_config.axis_default[3]:
            self.listAxis = [xmin, self.maxXaxis, ymin, ymax]
    
    def get_axis_special(self):
        """
        获取特殊规则下的坐标轴范围
        
        Returns:
            list: 特殊规则下的坐标轴范围 [xmin, xmax, ymin, ymax]
        """
        return self.plot_config.axis_special
    
    def set_axis_special(self, xmin, xmax, ymin, ymax):
        """
        设置特殊规则下的坐标轴范围
        
        Args:
            xmin: X轴最小值
            xmax: X轴最大值
            ymin: Y轴最小值
            ymax: Y轴最大值
        """
        self.plot_config.axis_special = [xmin, xmax, ymin, ymax]
    
    def get_plot_config(self):
        """
        获取整个图表配置对象
        
        Returns:
            PlotConfig: 图表配置对象
        """
        return self.plot_config
    
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
                logging.debug("获取配置 %s/%s: %s", section, option, value)
                return value
            else:
                logging.warning(
                    "未找到配置 %s/%s，使用默认值: %s", section, option, default_value)
                return default_value
        except (configparser.Error, TypeError, ValueError) as e:
            logging.error(
                "读取配置 %s/%s 出错: %s，使用默认值: %s", section, option, e, default_value)
            return default_value

    def _get_config_list(self, section, option):
        """安全获取配置列表，如果不存在则返回空列表"""
        try:
            if self.config.has_section(section) and self.config.has_option(section, option):
                list_value = self.config.get(section, option).split(",")
                cleaned_list = [item.strip() for item in list_value]
                logging.debug("获取配置列表 %s/%s: %s", section,
                              option, cleaned_list)
                return cleaned_list
            else:
                logging.warning("未找到配置列表 %s/%s，使用空列表", section, option)
                return []
        except (configparser.Error, TypeError, ValueError) as e:
            logging.error("读取配置列表 %s/%s 出错: %s，使用空列表", section, option, e)
            return []

    def _get_pulse_current_level(self):
        """获取脉冲电流级别配置"""
        try:
            if (self.config.has_section("BatteryConfig")
                    and self.config.has_option("BatteryConfig", "PulseCurrent")):
                
                result = parse_pulse_current_config(self.config)
                logging.info("使用配置的脉冲电流级别: %s", result)
                return result
            else:
                default_value = [10, 20, 50]
                logging.warning(
                    "未找到BatteryConfig/PulseCurrent，使用默认值: %s", default_value)
                return default_value
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            default_value = [10, 20, 50]
            logging.error("脉冲电流配置格式错误: %s，使用默认值: %s", e, default_value)
            return default_value

    def _set_plot_title(self):
        """设置图表标题，处理引号情况"""
        try:
            # 尝试移除前后引号（如果存在）
            if (len(self.strPltTitle) >= 2
                and self.strPltTitle[0] == '"'
                    and self.strPltTitle[-1] == '"'):
                title_content = self.strPltTitle[1:-1]
            else:
                title_content = self.strPltTitle
            return f"Load Voltage over Charge\n{title_content}"
        except (TypeError, IndexError, AttributeError, ValueError) as e:
            default_title = "Load Voltage over Charge\nUnknown Battery"
            logging.error("设置图表标题出错: %s，使用默认标题: %s", e, default_title)
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
                logging.warning("未找到BatteryConfig/Rules，使用默认maxXaxis")
        except (configparser.Error, AttributeError, TypeError, ValueError) as e:
            logging.error("读取Rules配置出错: %s，使用默认maxXaxis", e)

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
                                logging.info(
                                    "根据规则设置maxXaxis: %s", self.maxXaxis)
                                # 同步更新坐标轴范围和刻度
                                self.listAxis = [self.plot_config.axis_special[0], self.maxXaxis, self.plot_config.axis_special[2], self.plot_config.axis_special[3]]
                                self.listXTicks = list(
                                    range(0, self.maxXaxis + 1, 100))
                                break
                            except ValueError:
                                logging.warning(
                                    "规则中的maxXaxis值无效: %s", rule_parts[2])
        except (ValueError, IndexError, TypeError) as e:
            logging.error("处理规则时出错: %s，保持默认maxXaxis", e)

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
            logging.info("开始读取CSV文件: %s", self.strInfoImageCsvPath)

            # 检查文件是否存在
            csv_path = Path(self.strInfoImageCsvPath)
            if not csv_path.exists():
                logging.error("错误: 找不到CSV文件 %s", self.strInfoImageCsvPath)
                self.intBatteryNum = 0
                return

            # 检查文件大小
            file_size = csv_path.stat().st_size
            if file_size == 0:
                logging.error("错误: CSV文件 %s 为空", self.strInfoImageCsvPath)
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
                    logging.error(
                        "错误: CSV文件 %s 数据行数不足", self.strInfoImageCsvPath)
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

            logging.info("成功读取并处理CSV数据，包含%d个电池的真实测试数据", self.intBatteryNum)
        except FileNotFoundError:
            logging.error("错误: 文件未找到: %s", self.strInfoImageCsvPath)
            self.intBatteryNum = 0
        except PermissionError:
            logging.error("错误: 没有权限访问文件: %s", self.strInfoImageCsvPath)
            self.intBatteryNum = 0
        except (IOError, ValueError, TypeError, UnicodeDecodeError) as e:
            logging.error("错误: 读取CSV文件时发生异常: %s", str(e))
            logging.error("错误类型: %s", type(e).__name__)
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
                            # 只处理数值列，跳过字符串列（如'Battery_01'）
                            float_data = []
                            for i in range(len(row)):
                                try:
                                    # 尝试转换为float，如果失败则跳过此列
                                    float_data.append(float(row[i]))
                                except ValueError:
                                    # 跳过非数值列
                                    continue
                            # 只有当有有效数值数据时才添加
                            if float_data:
                                self.listPlt[current_idx][data_idx].append(float_data)
                    except (IndexError) as e:
                        logging.warning("解析CSV行数据时出错: %s，跳过此行", e)
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
                    strBatteryNameSplit = self.listBatteryName[b].split("BTS")[
                        1].split("_")
                    if len(strBatteryNameSplit) >= 4:
                        strBatteryName = f"{strBatteryNameSplit[2]}_{strBatteryNameSplit[3]}"
                    else:
                        # 如果分割后部分不足，使用可用部分
                        strBatteryName = "_".join(strBatteryNameSplit[1:3]) if len(
                            strBatteryNameSplit) >= 3 else f"Battery_{b}"
                else:
                    # 如果没有BTS标识，使用原始名称的后部分或默认名称
                    name_parts = self.listBatteryName[b].split("_")
                    strBatteryName = "_".join(
                        name_parts[-2:]) if len(name_parts) >= 2 else f"Battery_{b}"
                self.listBatteryNameSplit.append(strBatteryName)
            except (IndexError, TypeError, AttributeError, ValueError) as e:
                logging.warning(
                    "解析电池名称时出错: %s，使用默认名称", e)
                strBatteryName = f"Battery_{b}"
                self.listBatteryNameSplit.append(strBatteryName)

    def filter_data(self, list_plt_charge: list, list_plt_voltage: list,
                    times=5, slope_max=0.2, difference_max=0.05):
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
                        slope = abs(
                            (voltage_single[c] - voltage_single[c - 1]) / charge_diff)

                    # 根据斜率和电压差异进行过滤
                    if (slope < slope_max
                            and abs(voltage_single[c] - voltage_single[c - 1]) < difference_max):
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
                        self.listPlt[c][2], self.listPlt[c][3] = self.filter_data(
                            self.listPlt[c][0], self.listPlt[c][1])
            except (ValueError, TypeError, IndexError) as e:
                logging.error("过滤数据时出错 (电流级别 %s): %s", c, e)

    def plt_figure(self):
        """创建并显示电池数据图表，包含交互控件以切换数据显示

        重要说明：此方法只使用CSV文件中的真实数据，
        如果没有有效的电池数据或绘图过程中出错，会显示详细的错误信息和故障排除建议。
        """
        try:
            # 开始绘制图表
            logging.info("开始绘制图表")

            # 执行多层次的数据有效性检查
            if self.intBatteryNum <= 0:
                logging.error("错误: 没有有效的电池数据可供显示")
                self._show_error_plot()
                return True

            # 检查必要的数据结构是否有效
            if not hasattr(self, 'listPlt') or not self.listPlt:
                logging.error("错误: 电池数据结构未初始化或为空")
                self._show_error_plot()
                return True

            # 初始化图表和轴
            try:
                fig, ax, title_fontdict, axis_fontdict = self._initialize_figure()
                if fig is None or ax is None:
                    raise ValueError("无法初始化图表或坐标轴")
                
                # 保存当前图表实例引用
                self.current_fig = fig

                # 添加菜单栏
                self._add_menu_bar(fig)
            except (OSError, ValueError, TypeError) as init_error:
                logging.error("图表初始化失败: %s", str(init_error))
                self._show_error_plot()
                return True

            # 绘制电池数据曲线
            try:
                lines_unfiltered, lines_filtered = self._plot_battery_curves(
                    ax)
                valid_data_found = bool(
                    lines_filtered) or bool(lines_unfiltered)

                if valid_data_found:
                    logging.info(
                        "成功绘制了 %d 条过滤曲线和 %d 条原始曲线", len(lines_filtered), len(lines_unfiltered))
            except (OSError, ValueError, TypeError, IndexError) as plot_error:
                logging.error("绘制电池曲线时出错: %s", str(plot_error))
                lines_unfiltered, lines_filtered = [], []
                valid_data_found = False

            # 检查是否成功绘制了曲线
            if not valid_data_found:
                logging.error("严重错误: 无法绘制任何电池数据曲线")
                self._show_error_plot()
                return True

            # 添加交互控件
            try:
                check_filter = self._add_filter_button(
                    fig, ax, lines_unfiltered, lines_filtered, title_fontdict, axis_fontdict)
                self._add_battery_selection_buttons(
                    fig, check_filter, lines_unfiltered, lines_filtered
                )
                self._add_hover_functionality(
                    fig, ax, lines_filtered, lines_unfiltered, check_filter)
                self._add_help_text(fig)
                logging.info("成功添加图表交互控件")
            except (AttributeError, TypeError, ValueError) as ui_error:
                logging.warning("添加交互控件时出错: %s", str(ui_error))
                # 即使交互控件添加失败，仍然尝试显示图表



            logging.info("图表创建完成，显示CSV文件中的真实电池测试数据")
            
            # 在PyQt应用中显示图表，确保与Qt事件循环兼容
            # 设置为交互模式
            plt.ion()
            
            # 确保窗口始终在最前面并正确显示
            plt.show(block=False)
            
            # 确保窗口在最前面显示并获得焦点
            try:
                if hasattr(fig.canvas.manager, 'window'):
                    # 对于Qt后端
                    window = fig.canvas.manager.window
                    
                    # 设置窗口标志
                    window.setWindowFlags(Qt.WindowType.Window | 
                                        Qt.WindowType.WindowMinimizeButtonHint | 
                                        Qt.WindowType.WindowMaximizeButtonHint | 
                                        Qt.WindowType.WindowCloseButtonHint)
                    
                    # 激活并显示窗口
                    window.showNormal()  # 确保窗口不是最小化状态
                    window.show()
                    window.activateWindow()
                    window.raise_()
                    
                    # 确保窗口可见
                    window.setWindowState(Qt.WindowState.WindowActive)
                    
                    # 设置窗口位置在屏幕中央
                    screen = window.screen().availableGeometry()
                    window.move(int((screen.width() - window.width()) / 2), 
                              int((screen.height() - window.height()) / 2))
                    
                    # 强制刷新窗口
                    window.repaint()
                    window.update()
            except (AttributeError, TypeError, RuntimeError) as e:
                logging.warning("无法将窗口置于最前面: %s", str(e))
            
            # 增加暂停时间确保窗口正确渲染
            plt.pause(0.5)
            
            # 显式更新图表
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            # 再次更新以确保窗口稳定显示
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            # 成功完成所有操作
            logging.info("图表显示成功")
            return True

        except (OSError, ValueError, TypeError, AttributeError, RuntimeError) as e:
            logging.error("严重错误: 绘制图表时发生未预期的异常: %s", str(e))
            logging.error("错误类型: %s", type(e).__name__)
            traceback.print_exc()
            self._show_error_plot()
            return True

    def _search_for_data_files(self):
        """
        搜索项目中可能存在的Info_Image.csv文件
        
        这个方法会在项目根目录下搜索所有可能的Info_Image.csv文件，
        如果找到，会自动加载该文件。
        """
        try:
            logging.info("开始搜索项目中的Info_Image.csv文件...")
            
            # 在项目根目录下搜索所有子目录
            for root, dirs, files in os.walk(self.project_root):
                # 跳过隐藏目录和venv目录
                if ".venv" in root or ".git" in root or "__pycache__" in root:
                    continue
                    
                if "Info_Image.csv" in files:
                    info_image_csv = os.path.join(root, "Info_Image.csv")
                    logging.info("在项目中找到Info_Image.csv文件: %s", info_image_csv)
                    
                    # 设置数据路径并尝试加载
                    self.set_data_path(os.path.dirname(info_image_csv))
                    success = self.load_data()
                    if success:
                        self.loaded_data = True
                        logging.info("成功加载找到的数据文件")
                        return
                    else:
                        logging.warning("找到数据文件但加载失败")
            
            # 如果在项目根目录下没有找到，尝试在当前目录下搜索
            logging.info("在项目根目录下未找到，尝试在当前目录下搜索...")
            for root, dirs, files in os.walk(os.getcwd()):
                # 跳过隐藏目录和venv目录
                if ".venv" in root or ".git" in root or "__pycache__" in root:
                    continue
                    
                if "Info_Image.csv" in files:
                    info_image_csv = os.path.join(root, "Info_Image.csv")
                    logging.info("在当前目录下找到Info_Image.csv文件: %s", info_image_csv)
                    
                    # 设置数据路径并尝试加载
                    self.set_data_path(os.path.dirname(info_image_csv))
                    success = self.load_data()
                    if success:
                        self.loaded_data = True
                        logging.info("成功加载找到的数据文件")
                        return
                    else:
                        logging.warning("找到数据文件但加载失败")
            
            logging.warning("在项目中未找到任何有效的Info_Image.csv文件")
        except (OSError, ValueError, TypeError) as e:
            logging.error("搜索数据文件时出错: %s", str(e))
            import traceback
            traceback.print_exc()

    def _show_error_plot(self, title=None, main_message=None, details=None, allow_file_selection=True):
        """
        显示详细的错误信息图表，提供清晰的错误反馈和故障排除建议
        并可选择性地提供数据文件选择功能

        Args:
            title (str, optional): 错误标题，默认为"数据错误"
            main_message (str, optional): 主要错误信息，默认为"无法加载或显示电池数据"
            details (str, optional): 详细错误信息和故障排除建议
            allow_file_selection (bool): 是否允许用户选择数据文件
        """
        try:
            # 设置默认错误信息
            if title is None:
                title = "数据错误"
            if main_message is None:
                main_message = "无法加载或显示电池数据"
            if details is None:
                details = "1. csv文件是否存在且格式正确\n"
                details += "2. 配置文件是否正确选择\n"
                details += "3. 文件路径是否包含中文字符或特殊字符\n"
                details += "4. csv文件是否包含有效的电池测试数据"

            # 创建错误图表 - 应用现代化样式
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 保存当前图表实例引用
            self.current_fig = fig

            # 应用现代化图表样式
            self._apply_modern_plot_style(fig, ax)

            # 设置现代化标题
            title_color = MODERN_BUTTON_STYLE['active_color']  # 使用现代绿色作为标题色
            ax.set_title(title, fontsize=18, fontweight='bold', 
                        color=title_color, pad=20)

            # 隐藏坐标轴
            ax.axis('off')

            # 构建完整的错误信息文本
            full_text = f"{main_message}\n\n"
            full_text += "检查步骤:\n"
            full_text += details
            
            # 添加重新加载提示
            if allow_file_selection:
                full_text += "\n\n解决方案:\n"
                full_text += "1. 点击菜单栏'File' -> 'Open Data'选择数据目录\n"
                full_text += "2. 或按Ctrl+O键打开文件对话框\n"
                full_text += "3. 选择包含Info_Image.csv文件的目录"

            # 显示错误日志信息（如果有）
            if hasattr(self, 'errorlog') and self.errorlog:
                full_text += f"\n\n错误详情: {str(self.errorlog)}"

            # 显示错误信息 - 使用现代化字体和颜色
            text_color = MODERN_BUTTON_STYLE['inactive_text_color']  # 使用现代深灰文字
            main_text_color = MODERN_BUTTON_STYLE['active_color']    # 使用现代绿色强调
            
            # 主标题文字（使用绿色强调）
            main_text = f"{main_message}\n\n"
            ax.text(0.5, 0.75, main_text, fontsize=14, ha='center', va='center',
                    color=main_text_color, weight='bold', linespacing=1.4)
            
            # 检查步骤（使用深灰色）
            check_text = "检查步骤:\n" + details
            ax.text(0.5, 0.55, check_text, fontsize=11, ha='center', va='center',
                    color=text_color, linespacing=1.4)
            
            # 解决方案（如果允许文件选择）
            if allow_file_selection:
                solution_text = "\n\n解决方案:\n" + "1. 点击菜单栏'File' -> 'Open Data'选择数据目录\n" + \
                               "2. 或按Ctrl+O键打开文件对话框\n" + "3. 选择包含Info_Image.csv文件的目录"
                ax.text(0.5, 0.35, solution_text, fontsize=11, ha='center', va='center',
                        color=MODERN_BUTTON_STYLE['hover_color'], weight='bold', linespacing=1.4)

            # 显示错误日志信息（如果有）
            if hasattr(self, 'errorlog') and self.errorlog:
                error_text = f"\n错误详情: {str(self.errorlog)}"
                ax.text(0.5, 0.15, error_text, fontsize=10, ha='center', va='center',
                        color='#d32f2f', style='italic', linespacing=1.3)

            # 添加版本信息和时间戳 - 现代化样式
            import datetime
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fig.text(0.02, 0.01, f"Battery Analysis Tool v1.0 | {current_time}",
                     fontsize=9, color='#6c757d', alpha=0.8)

            # 添加现代化边框和样式
            for spine in ax.spines.values():
                spine.set_color(MODERN_BUTTON_STYLE['border_color'])
                spine.set_linewidth(1.5)
                spine.set_alpha(0.8)

            # 添加菜单栏（包括Open功能）
            menu_added = self._add_menu_bar(fig)
            if not menu_added:
                logging.warning("无法添加菜单栏，将使用默认方式显示错误图表")

            logging.info("显示错误信息图表: %s - %s", title, main_message)
            plt.tight_layout()
            
            # 在PyQt应用中显示错误图表，确保与Qt事件循环兼容
            # 检查是否已经在交互模式
            if not plt.isinteractive():
                plt.ion()
            
            plt.show(block=False)
            plt.pause(0.1)  # 增加暂停时间确保窗口正确渲染
            
            # 显式更新画布
            fig.canvas.draw()
            fig.canvas.flush_events()

        except (OSError, ValueError) as e:
            logging.critical("显示错误图表时发生异常: %s", str(e))
            traceback.print_exc()
            # 如果连错误图表都无法显示，尝试使用简单的文本输出
            logging.error("\n严重错误: 无法显示图形界面的错误信息")
            logging.error(
                "错误详情: %s - %s", title or '未知错误', main_message or '无法加载数据')
            logging.info("\n请检查以下事项:")
            logging.info("1. Python环境是否正确安装")
            logging.info("2. Matplotlib库是否可用")
            logging.info("3. CSV文件是否存在且格式正确")
            logging.info("4. 系统是否有足够的资源显示图形")

    def _cleanup_matplotlib_state(self):
        """
        清理Matplotlib状态，确保新的图表能正常工作
        """
        logging.info("开始清理Matplotlib状态")
        import matplotlib
        import matplotlib.pyplot as plt
        
        # 重置Matplotlib的内部状态（不关闭当前图表，避免事件绑定失效）
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        
        # 重新配置中文字体支持，避免重置后丢失
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial', 'Times New Roman']
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 确保使用正确的后端
        if matplotlib.get_backend() != 'QtAgg':
            logging.info("当前Matplotlib后端: %s, 切换到QtAgg后端", matplotlib.get_backend())
            matplotlib.use('QtAgg')
        
        logging.info("Matplotlib状态清理完成")
        
    def _open_file_dialog(self):
        """
        打开文件对话框，允许用户选择数据文件
        """
        logging.info("=== _open_file_dialog方法开始执行 ===")
        try:
            logging.info("尝试打开文件对话框，选择数据目录")
            
            data_dir = None
            
            # 使用Qt的文件对话框
            logging.info("尝试使用Qt文件对话框")
            try:
                # 打开目录选择对话框
                data_dir = QFileDialog.getExistingDirectory(
                    None,  # 父窗口
                    "选择数据目录",  # 对话框标题
                    self.strPltPath or ".",  # 默认目录
                    QFileDialog.Option.ShowDirsOnly  # 只显示目录
                )
                logging.info("使用Qt文件对话框成功，返回值: %s", data_dir)
            except (ImportError, AttributeError, TypeError, RuntimeError) as qt_error:
                logging.error("Qt文件对话框失败: %s", qt_error)

            if data_dir:
                logging.info("用户选择的数据目录: %s", data_dir)
                # 设置数据路径并重新加载数据
                self.set_data_path(data_dir)
                success = self.load_data()
                if success:
                    logging.info("数据加载成功，重新绘制图表")
                    
                    # 清理Matplotlib状态（确保新图表有正确的事件绑定）
                    self._cleanup_matplotlib_state()
                    
                    # 关闭当前的图表实例（如果存在），确保新创建的图表实例是唯一的
                    if self.current_fig is not None:
                        plt.close(self.current_fig)
                        self.current_fig = None
                    
                    # 重新绘制图表
                    self.plt_figure()
                else:
                    logging.error("数据加载失败，无法显示图表")
        except (AttributeError, TypeError, ValueError, OSError, RuntimeError) as e:
            logging.error("打开文件对话框时出错: %s", str(e))
            traceback.print_exc()

    def _show_about_dialog(self):
        """
        显示About对话框
        """
        try:
            # 获取版本信息
            try:
                import datetime
                current_time = datetime.datetime.now().strftime("%Y")
            except:
                current_time = "2024"
            
            # 使用项目统一的版本管理系统
            try:
                from battery_analysis.utils.version import Version
                version_obj = Version()
                version_info = f"v{version_obj.version}"
            except (ImportError, AttributeError, TypeError) as e:
                logging.warning("无法获取版本信息，使用默认版本: %s", e)
                version_info = "v2.0.0"
            
            # 创建About信息文本
            about_text = f"""Battery Analysis Tool
版本: {version_info}

电池测试数据可视化分析应用
支持多种数据格式导入与图表生成

功能特点:
• 支持CSV文件数据导入
• 交互式图表显示和操作
• 数据过滤和未过滤切换
• 电池选择和通道控制
• 悬停显示详细信息

开发者: Ewin电池分析团队
版权: © {current_time} MIT License

感谢使用Battery Analysis Tool!"""
            
            # 显示About对话框
            msg_box = QMessageBox()
            msg_box.setWindowTitle("About")
            msg_box.setText(about_text)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            
            logging.info("About对话框显示完成")
            
        except (AttributeError, TypeError, ValueError, OSError, RuntimeError) as e:
            logging.error("显示About对话框失败: %s", e)
            # 如果对话框失败，至少打印到日志
            try:
                from battery_analysis.utils.version import Version
                version_obj = Version()
                fallback_version = f"v{version_obj.version}"
            except (ImportError, AttributeError, TypeError):
                fallback_version = "v2.1.2"
            print(f"Battery Analysis Tool {fallback_version}\n开发者: Ewin电池分析团队")

    def _add_menu_bar(self, fig):
        """
        为图表添加菜单栏（统一使用PyQt6）

        Args:
            fig: matplotlib Figure对象
        """
        try:
            logging.info("开始添加PyQt6菜单栏")
            
            # 获取图表窗口的manager
            manager = fig.canvas.manager
            
            # 检查manager和window是否存在
            if not manager or not hasattr(manager, 'window'):
                logging.warning("无法获取matplotlib窗口管理器，跳过菜单栏添加")
                return False
            
            # 添加PyQt6菜单栏
            if hasattr(manager.window, 'menuBar'):
                # 确保窗口有现代样式
                self._apply_window_modern_style(manager.window)
                
                menubar = manager.window.menuBar()
                
                # 重新应用菜单栏样式
                self._apply_menubar_style(menubar)
                
                # 添加File菜单
                file_menu = menubar.addMenu('File')
                
                # 为菜单添加现代化样式
                self._apply_menu_style(file_menu)
                
                # 添加Open菜单项
                open_action = file_menu.addAction('Open')
                
                # 为菜单项添加样式
                open_action.setProperty('menu_action', 'open')
                
                def on_open_clicked():
                    logging.info("Open菜单项被点击")
                    self._open_file_dialog()
                
                open_action.triggered.connect(on_open_clicked)
                
                # 添加分割线
                file_menu.addSeparator()
                
                # 添加Exit菜单项
                exit_action = file_menu.addAction('Exit')
                
                # 为菜单项添加样式
                exit_action.setProperty('menu_action', 'exit')
                
                def on_exit_clicked():
                    logging.info("Exit菜单项被点击，关闭visualizer窗口")
                    # 只关闭当前的visualizer窗口，不退出整个应用
                    if self.current_fig is not None:
                        plt.close(self.current_fig)
                        self.current_fig = None
                        logging.info("已关闭visualizer窗口")
                    else:
                        logging.warning("当前没有打开的visualizer窗口")
                
                exit_action.triggered.connect(on_exit_clicked)
                
                # 添加Help菜单
                help_menu = menubar.addMenu('Help')
                
                # 为菜单添加现代化样式
                self._apply_menu_style(help_menu)
                
                # 添加About菜单项
                about_action = help_menu.addAction('About')
                
                # 为菜单项添加样式
                about_action.setProperty('menu_action', 'about')
                
                def on_about_clicked():
                    logging.info("About菜单项被点击")
                    self._show_about_dialog()
                
                about_action.triggered.connect(on_about_clicked)
                logging.info("成功添加PyQt6菜单栏")
            else:
                raise RuntimeError("窗口不支持菜单栏")
                
        except ImportError as e:
            raise ImportError(f"PyQt6依赖缺失: {e}. 请确保已正确安装PyQt6")
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            logging.error("添加菜单栏失败: %s", e)
            # 不再静默失败，直接抛出错误
            raise RuntimeError(f"菜单栏初始化失败: {e}") from e

    def _initialize_figure(self):
        """初始化图表设置和布局"""
        # 设置字体样式
        title_fontdict = {'fontsize': 15, 'fontweight': 'bold'}
        axis_fontdict = {'fontsize': 15}

        # 创建图表并设置标题
        fig = plt.figure(figsize=(15, 6))
        # 尝试设置窗口标题（添加错误处理以兼容不同后端）
        try:
            if hasattr(fig.canvas.manager, 'window'):
                fig.canvas.manager.window.setWindowTitle(
                    f"Filtered {self.strPltName}")
        except (AttributeError, TypeError, RuntimeError) as e:
            logging.warning("无法设置图表窗口标题: %s", str(e))

        # 设置网格布局
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
        ax.set_ylabel(
            "Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)

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
                        color=self.listColor[c] if c < len(
                            self.listColor) else f'C{c}',
                        label=[f'{self.listBatteryNameSplit[b]}',
                               'Unfiltered'],
                        visible=False,
                        linewidth=0.5
                    )
                    lines_unfiltered.append(ul)

                    # 绘制过滤后的数据曲线（默认显示）
                    fl, = ax.plot(
                        self.listPlt[c][2][b],
                        self.listPlt[c][3][b],
                        color=self.listColor[c] if c < len(
                            self.listColor) else f'C{c}',
                        label=[f'{self.listBatteryNameSplit[b]}', 'Filtered'],
                        visible=True,
                        linewidth=0.5
                    )
                    lines_filtered.append(fl)
                except (IndexError, ValueError, TypeError, AttributeError) as e:
                    logging.error("绘制电池 %s, 电流级别 %s 的曲线时出错: %s", b, c, e)

        return lines_unfiltered, lines_filtered

    def _create_modern_button(self, ax, x, y, width, height, text, callback, 
                             is_toggle=False, initial_state=False):
        """
        创建现代化按钮
        
        Args:
            ax: matplotlib轴对象
            x, y: 按钮位置
            width, height: 按钮尺寸
            text: 按钮文本
            callback: 点击回调函数
            is_toggle: 是否为切换按钮（保存状态）
            initial_state: 初始状态
        """
        try:
            # 创建按钮背景
            button_bg = FancyBboxPatch(
                (x, y), width, height,
                boxstyle=f"round,pad={MODERN_BUTTON_STYLE['padding']/100}",
                facecolor=MODERN_BUTTON_STYLE['inactive_color'],
                edgecolor=MODERN_BUTTON_STYLE['border_color'],
                linewidth=MODERN_BUTTON_STYLE['border_width'],
                alpha=0.95,
                transform=ax.transAxes
            )
            ax.add_patch(button_bg)
            
            # 创建按钮文本
            button_text = ax.text(
                x + width/2, y + height/2, text,
                ha='center', va='center',
                fontsize=MODERN_BUTTON_STYLE['font_size'],
                color=MODERN_BUTTON_STYLE['inactive_text_color'],
                weight=MODERN_BUTTON_STYLE['font_weight'] if is_toggle else 'normal',
                transform=ax.transAxes
            )
            
            # 按钮状态
            state = {'active': initial_state, 'bg': button_bg, 'text': button_text, 'hover': False}
            
            # 初始化按钮样式
            self._update_button_style(state)
            
            def on_button_hover(event):
                """鼠标悬停处理"""
                if event.inaxes != ax:
                    # 鼠标移出按钮区域，重置悬停状态
                    if state['hover']:
                        state['hover'] = False
                        self._update_button_style(state)
                    return
                    
                # 检查鼠标是否在按钮范围内 - 统一检测范围
                is_in_button = (x <= event.xdata <= x + width and 
                              y - 0.01 <= event.ydata <= y + height + 0.01)
                
                if is_in_button and not state['hover']:
                    # 鼠标进入按钮区域
                    state['hover'] = True
                    self._update_button_style(state, hover=True)
                    ax.figure.canvas.draw_idle()
                elif not is_in_button and state['hover']:
                    # 鼠标离开按钮区域
                    state['hover'] = False
                    self._update_button_style(state)
                    ax.figure.canvas.draw_idle()

            def on_button_click(event):
                if event.inaxes != ax:
                    return
                    
                # 检查点击是否在按钮范围内 - 修复点击位置偏移
                if (x <= event.xdata <= x + width and 
                    y - 0.01 <= event.ydata <= y + height + 0.01):
                    
                    if is_toggle:
                        # 切换按钮状态
                        state['active'] = not state['active']
                        self._update_button_style(state)
                    else:
                        # 单次按钮，执行后重置样式
                        self._update_button_style(state, pressed=True)
                        # 延迟重置
                        self._reset_button_after_delay(state, delay=0.1)
                    
                    # 执行回调
                    try:
                        callback()
                    except (TypeError, ValueError, AttributeError) as e:
                        logging.error("按钮回调执行出错: %s", e)
                    
                    # 重绘
                    ax.figure.canvas.draw_idle()
            
            # 连接事件
            ax.figure.canvas.mpl_connect('motion_notify_event', on_button_hover)
            ax.figure.canvas.mpl_connect('button_press_event', on_button_click)
            
            return state
            
        except (ValueError, TypeError, AttributeError) as e:
            logging.error("创建现代化按钮时出错: %s", e)
            return None
    
    def _update_button_style(self, state, pressed=False, hover=False):
        """更新按钮样式 - 增强版 v4.1"""
        try:
            # 更新边框样式 - 现代化边框
            state['bg'].set_linewidth(MODERN_BUTTON_STYLE['border_width'])
            state['bg'].set_edgecolor(MODERN_BUTTON_STYLE['border_color'])
            
            # 更新圆角半径 - 简化处理
            try:
                if hasattr(state['bg'], 'set_boxstyle'):
                    state['bg'].set_boxstyle(f"round,pad={MODERN_BUTTON_STYLE['padding']/100}")
            except (AttributeError, TypeError, ValueError) as box_error:
                # 如果boxstyle更新失败，不影响其他样式更新
                logging.debug("boxstyle更新失败: %s", box_error)
                pass
            
            if pressed:
                # 按下状态 - 深色强调
                state['bg'].set_facecolor(MODERN_BUTTON_STYLE['pressed_color'])
                state['text'].set_color(MODERN_BUTTON_STYLE['pressed_text_color'])
                state['text'].set_weight(MODERN_BUTTON_STYLE['font_weight'])
                # 按下时增强边框
                state['bg'].set_linewidth(MODERN_BUTTON_STYLE['border_width'] + 0.5)
                state['bg'].set_edgecolor(MODERN_BUTTON_STYLE['pressed_color'])
                
            elif hover:
                # 悬停状态 - 亮度提升
                if state['active']:
                    state['bg'].set_facecolor(MODERN_BUTTON_STYLE['hover_color'])
                    state['text'].set_color(MODERN_BUTTON_STYLE['hover_text_color'])
                else:
                    state['bg'].set_facecolor('#F5F5F5')  # 悬停时轻微提亮
                    state['text'].set_color(MODERN_BUTTON_STYLE['inactive_text_color'])
                state['text'].set_weight(MODERN_BUTTON_STYLE['font_weight'])
                # 悬停时边框颜色变亮
                state['bg'].set_edgecolor('#BDBDBD')
                
            elif state['active']:
                # 激活状态 - 绿色主题
                state['bg'].set_facecolor(MODERN_BUTTON_STYLE['active_color'])
                state['text'].set_color(MODERN_BUTTON_STYLE['active_text_color'])
                state['text'].set_weight(MODERN_BUTTON_STYLE['font_weight'])
                # 激活时边框颜色与背景匹配
                state['bg'].set_edgecolor(MODERN_BUTTON_STYLE['active_color'])
                
            else:
                # 未激活状态 - 简洁现代
                state['bg'].set_facecolor(MODERN_BUTTON_STYLE['inactive_color'])
                state['text'].set_color(MODERN_BUTTON_STYLE['inactive_text_color'])
                state['text'].set_weight('normal')
                # 默认边框
                state['bg'].set_edgecolor(MODERN_BUTTON_STYLE['border_color'])
                
            # 增强透明度 - 更现代的半透明效果
            state['bg'].set_alpha(0.95)
            
        except (AttributeError, TypeError, ValueError) as e:
            logging.error("更新按钮样式时出错: %s", e)
    
    def _reset_button_after_delay(self, state, delay=0.1):
        """延迟重置按钮状态"""
        import threading
        timer = threading.Timer(delay, lambda: self._update_button_style(state))
        timer.start()
    
    def _apply_modern_plot_style(self, fig, ax):
        """为图表应用现代化样式"""
        try:
            # 设置现代化背景颜色
            fig.patch.set_facecolor('#f8f9fa')  # 现代浅灰色背景
            ax.set_facecolor('#ffffff')  # 白色图表区域
            
            # 设置现代化标题样式
            if hasattr(ax, 'title'):
                ax.title.set_fontsize(18)
                ax.title.set_fontweight('bold')
                ax.title.set_color(MODERN_BUTTON_STYLE['active_color'])
            
            # 设置现代化坐标轴样式
            ax.tick_params(colors='#6c757d', labelsize=10)
            ax.spines['top'].set_color('#e9ecef')
            ax.spines['right'].set_color('#e9ecef')
            ax.spines['bottom'].set_color('#e9ecef')
            ax.spines['left'].set_color('#e9ecef')
            
            # 设置网格样式（如果需要）
            ax.grid(True, alpha=0.3, color='#e9ecef', linestyle='-', linewidth=0.5)
            
            logging.info("已应用现代化图表样式")
            
        except (AttributeError, TypeError, ValueError) as e:
            logging.warning("应用现代化图表样式失败: %s", e)
    
    def _apply_window_modern_style(self, window):
        """为PyQt6窗口应用现代化样式"""
        try:
            # 确保窗口有现代化样式
            modern_style = """
                QMainWindow {
                    background-color: #f8f9fa;
                    color: #212529;
                    font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                }
            """
            window.setStyleSheet(modern_style)
            logging.info("已应用窗口现代化样式")
            
        except (AttributeError, TypeError, ValueError) as e:
            logging.warning("应用窗口现代化样式失败: %s", e)
    
    def _apply_menubar_style(self, menubar):
        """为菜单栏应用现代化样式"""
        try:
            # 强制应用菜单栏样式
            menubar_style = """
                QMenuBar {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff,
                        stop:1 #f8f9fa);
                    border-bottom: 1px solid #e9ecef;
                    padding: 2px;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 6px 12px;
                    border-radius: 4px;
                    color: #495057;
                    font-weight: 500;
                    font-size: 12px;
                }
                QMenuBar::item:hover {
                    background-color: #e9ecef;
                    color: #495057;
                }
                QMenuBar::item:selected {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db,
                        stop:1 #2980b9);
                    color: white;
                }
            """
            menubar.setStyleSheet(menubar_style)
            logging.info("已应用菜单栏现代化样式")
            
        except (AttributeError, TypeError, ValueError) as e:
            logging.warning("应用菜单栏现代化样式失败: %s", e)
    
    def _apply_menu_style(self, menu):
        """为菜单应用现代化样式"""
        try:
            # 强制应用菜单样式
            menu_style = """
                QMenu {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff,
                        stop:1 #f8f9fa);
                    border: 1px solid #e9ecef;
                    border-radius: 6px;
                    padding: 5px;
                    min-width: 150px;
                }
                QMenu::item {
                    padding: 6px 20px;
                    border-radius: 3px;
                    color: #495057;
                }
                QMenu::item:hover {
                    background-color: #3498db;
                    color: white;
                }
                QMenu::item:selected {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db,
                        stop:1 #2980b9);
                    color: white;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #e9ecef;
                    margin: 4px 8px;
                }
            """
            menu.setStyleSheet(menu_style)
            logging.info("已应用菜单现代化样式")
            
        except (AttributeError, TypeError, ValueError) as e:
            logging.warning("应用菜单现代化样式失败: %s", e)
    
    def _create_modern_toggle_group(self, ax, x, y, width, height, buttons_config):
        """
        创建现代化切换按钮组
        
        Args:
            ax: matplotlib轴对象
            x, y: 按钮组位置
            width, height: 按钮组尺寸
            buttons_config: 按钮配置列表 [{'text': '文本', 'callback': 函数, 'initial': 状态}]
        """
        try:
            button_states = []
            button_width = width / len(buttons_config)
            
            for i, config in enumerate(buttons_config):
                btn_x = x + i * button_width
                btn_state = self._create_modern_button(
                    ax, btn_x, y, button_width - 0.005, height,
                    config['text'], config['callback'],
                    is_toggle=True, initial_state=config.get('initial', False)
                )
                if btn_state:
                    button_states.append(btn_state)
            
            return button_states
            
        except (ValueError, TypeError, AttributeError) as e:
            logging.error("创建现代化切换按钮组时出错: %s", e)
            return []

    def _add_file_operation_buttons(self, fig):
        """添加文件操作按钮区域（打开文件和退出按钮）"""
        try:
            # 创建文件操作按钮区域
            ax_file = fig.add_axes([0.001, 0.90, 0.17, 0.062])
            ax_file.set_xlim(0, 1)
            ax_file.set_ylim(0, 1)
            ax_file.axis('off')
            
            # 按钮配置
            buttons_config = [
                {
                    'text': '📁 Open',
                    'callback': lambda: self._open_file_dialog(),
                    'initial': False
                },
                {
                    'text': '❌ Exit',
                    'callback': lambda: self._close_viewer(),
                    'initial': False
                }
            ]
            
            # 创建现代化按钮组
            self.file_button_states = self._create_modern_toggle_group(
                ax_file, 0.02, 0.15, 0.96, 0.7, buttons_config
            )
            
            logging.info("成功添加现代化文件操作按钮区域")
            
        except (ValueError, TypeError, AttributeError) as e:
            logging.error("创建文件操作按钮时出错: %s", e)
    
    def _close_viewer(self):
        """关闭viewer窗口"""
        try:
            logging.info("文件操作按钮：Exit被点击，关闭visualizer窗口")
            # 只关闭当前的visualizer窗口，不退出整个应用
            if self.current_fig is not None:
                plt.close(self.current_fig)
                self.current_fig = None
                logging.info("已关闭visualizer窗口")
            else:
                logging.warning("当前没有打开的visualizer窗口")
        except (AttributeError, TypeError, RuntimeError) as e:
            logging.error("关闭viewer窗口时出错: %s", e)

    def _add_filter_button(self, fig, ax, lines_unfiltered, lines_filtered,
                           title_fontdict, axis_fontdict):
        """添加过滤/未过滤数据切换按钮"""
        try:
            # 创建按钮区域 - 移至左上角，通道区域上方
            ax_filter = fig.add_axes([0.001, 0.92, 0.12, 0.05])
            ax_filter.set_xlim(0, 1)
            ax_filter.set_ylim(0, 1)
            ax_filter.axis('off')
            
            # 按钮状态变量
            is_filtered = {'value': True}
            button_state_ref = {'button_state': None}
            
            # 切换过滤模式的回调函数
            def toggle_filter_mode():
                try:
                    is_filtered['value'] = not is_filtered['value']
                    
                    # 更新按钮文本
                    if button_state_ref and isinstance(button_state_ref, dict):
                        button_state = button_state_ref.get('button_state')
                        if button_state and isinstance(button_state, dict) and 'text' in button_state:
                            new_text = "🔍 Filtered" if is_filtered['value'] else "📊 All Data"
                            button_state['text'].set_text(new_text)
                    
                    if is_filtered['value']:
                        # 切换到过滤模式
                        fig.canvas.manager.window.setWindowTitle(
                            f"Filtered {self.strPltName}")
                        ax.set_title(
                            f"Filtered {self.strPltName}", fontdict=title_fontdict)
                        ax.set_ylabel(
                            "Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)

                        # 更新线条可见性 - 保持相同电池的可见性一致
                        for i in range(min(len(lines_unfiltered), len(lines_filtered))):
                            # 获取当前电池的可见性状态（基于最后一次设置）
                            # 对于每个电池，所有电流级别的可见性应该保持一致
                            battery_index = i % self.intBatteryNum
                            # 检查该电池是否有任何可见的线条
                            battery_visible = any(lines_unfiltered[battery_index + j * self.intBatteryNum].get_visible() 
                                                for j in range(self.intCurrentLevelNum))
                            
                            # 设置该电池所有电流级别的过滤线条可见性
                            lines_filtered[i].set_visible(battery_visible)
                            lines_unfiltered[i].set_visible(False)
                    else:
                        # 切换到未过滤模式
                        fig.canvas.manager.window.setWindowTitle(
                            f"Unfiltered {self.strPltName}")
                        ax.set_title(
                            f"Unfiltered {self.strPltName}", fontdict=title_fontdict)
                        ax.set_ylabel(
                            "Unfiltered Battery Load Voltage [V]", fontdict=axis_fontdict)

                        # 更新线条可见性 - 保持相同电池的可见性一致
                        for i in range(min(len(lines_filtered), len(lines_unfiltered))):
                            # 获取当前电池的可见性状态（基于最后一次设置）
                            battery_index = i % self.intBatteryNum
                            # 检查该电池是否有任何可见的线条
                            battery_visible = any(lines_filtered[battery_index + j * self.intBatteryNum].get_visible() 
                                                for j in range(self.intCurrentLevelNum))
                            
                            # 设置该电池所有电流级别的原始线条可见性
                            lines_unfiltered[i].set_visible(battery_visible)
                            lines_filtered[i].set_visible(False)
                    
                    fig.canvas.draw_idle()
                except (AttributeError, TypeError, ValueError, IndexError) as e:
                        logging.error("执行过滤切换时出错: %s", e)
            
            # 创建现代化过滤按钮
            button_text = "🔍 Filtered" if is_filtered['value'] else "📊 All Data"
            button_state = self._create_modern_button(
                ax_filter, 0.02, 0.15, 0.96, 0.7,
                button_text, toggle_filter_mode,
                is_toggle=True, initial_state=True
            )
            
            # 保存按钮状态引用
            button_state_ref['button_state'] = button_state
            self.filter_button_state = button_state
            
            logging.info("成功添加现代化过滤按钮")
            
        except (ValueError, TypeError, AttributeError) as e:
            logging.error("创建过滤按钮时出错: %s", e)
        
        # 返回按钮状态，供其他方法使用
        return button_state_ref['button_state']

    def _add_battery_selection_buttons(self, fig, check_filter, lines_unfiltered, lines_filtered):
        """添加电池选择现代化按钮，用于显示/隐藏特定电池的数据曲线"""
        # 初始化默认值
        button_states_line1 = None
        button_states_line2 = None

        # 根据电池数量创建不同的按钮布局
        if self.intBatteryNum > 32:
            # 创建第一个按钮区域（前32个电池）- 宽度减半
            button_states_line1 = self._create_battery_check_buttons(
                fig, [0.001, 0.005, 0.04, 0.029*32], 0, 32,
                check_filter, lines_unfiltered, lines_filtered
            )

            # 创建第二个按钮区域（剩余电池，最多32个）- 宽度减半，位置紧凑
            button_states_line2 = self._create_battery_check_buttons(
                fig, [0.041, 0.005, 0.04, 0.029*32], 32, 64,
                check_filter, lines_unfiltered, lines_filtered
            )
        else:
            # 创建单个按钮区域 - 宽度减半
            button_states_line1 = self._create_battery_check_buttons(
                fig, [0.001, 0.005, 0.04, 0.029*32], 0, 32,
                check_filter, lines_unfiltered, lines_filtered
            )

            # 创建空的第二个按钮区域（占位）- 宽度减半，位置紧凑
            ax_empty = fig.add_axes([0.041, 0.005, 0.04, 0.029*32])
            ax_empty.set_xlim(0, 1)
            ax_empty.set_ylim(0, 1)
            ax_empty.axis('off')
            
            # 添加占位文本
            ax_empty.text(0.5, 0.5, 'Empty', ha='center', va='center', 
                         fontsize=8, alpha=0.5, transform=ax_empty.transAxes)
            
            button_states_line2 = []

        # 存储所有按钮状态引用
        self.battery_button_states = {
            'line1': button_states_line1,
            'line2': button_states_line2
        }

        logging.info("成功添加现代化电池选择按钮")
        return button_states_line1, button_states_line2

    def _create_battery_check_buttons(self, fig, rect, start_idx, end_idx,
                                      check_filter, lines_unfiltered, lines_filtered):
        """创建电池选择现代化按钮"""
        # 创建现代化按钮轴
        ax_buttons = fig.add_axes(rect)
        ax_buttons.set_xlim(0, 1)
        ax_buttons.set_ylim(0, 1)
        ax_buttons.axis('off')

        # 准备电池信息和按钮状态 - 改为正序
        battery_info = []
        for i in range(start_idx, end_idx):
            if i < self.intBatteryNum:
                battery_info.append({
                    'name': self.listBatteryNameSplit[i],
                    'index': i,
                    'initial_state': True,
                    'is_none': False
                })
            else:
                battery_info.append({
                    'name': f"Battery {start_idx + 1}",
                    'index': i,
                    'initial_state': False,
                    'is_none': True
                })
        
        # 按索引正序排列（确保正序显示）
        battery_info.sort(key=lambda x: x['index'])

        # 计算按钮布局参数 - 适配紧凑布局
        num_valid_batteries = min(self.intBatteryNum - start_idx, end_idx - start_idx)
        if num_valid_batteries > 0:
            button_height = 0.92 / num_valid_batteries
            button_spacing = 0.04 / (num_valid_batteries + 1)
        else:
            button_height = 0.1
            button_spacing = 0.45

        # 存储按钮状态引用
        button_states = []

        # 电池切换回调函数
        def toggle_battery_visibility(battery_idx, button_state):
            try:
                logging.debug("切换电池 %s 的可见性", battery_idx)
                
                # 处理空标签
                if battery_info[battery_idx - start_idx].get('is_none', False):
                    return

                # 根据当前模式（过滤/未过滤）更新对应线条的可见性
                is_filtered = self.filter_button_state['active'] if hasattr(self, 'filter_button_state') else True
                logging.debug("当前模式: %s", '过滤' if is_filtered else '未过滤')
                
                # 找到当前点击的电池索引
                battery_index = battery_info[battery_idx - start_idx]['index']
                
                # 检查该电池当前的可见性状态（基于当前模式下的线条）
                current_lines = lines_filtered if is_filtered else lines_unfiltered
                battery_visible = False
                for i in range(len(current_lines)):
                    if i % self.intBatteryNum == battery_index:
                        battery_visible = current_lines[i].get_visible()
                        break
                
                new_visibility = not battery_visible
                
                # 更新当前模式下该电池的所有线条
                updated = False
                for i in range(len(current_lines)):
                    if i % self.intBatteryNum == battery_index:
                        current_lines[i].set_visible(new_visibility)
                        updated = True
                        logging.debug("线条 %s 可见性更新: %s -> %s", i, battery_visible, new_visibility)
                
                # 同时更新另一种模式下该电池的所有线条，保持一致性
                other_lines = lines_unfiltered if is_filtered else lines_filtered
                for i in range(len(other_lines)):
                    if i % self.intBatteryNum == battery_index:
                        other_lines[i].set_visible(new_visibility)
                        logging.debug("另一模式下的线条 %s 可见性也更新为: %s", i, new_visibility)

                # 更新按钮状态
                button_state['active'] = new_visibility
                self._update_button_style(button_state)

                if updated:
                    logging.debug("调用fig.canvas.draw_idle()刷新图表")
                    fig.canvas.draw_idle()
                else:
                    logging.debug("没有找到匹配的线条")
            except (AttributeError, TypeError, ValueError, IndexError) as e:
                        logging.error("执行电池选择时出错: %s", e)

        # 创建现代化按钮
        for i, battery in enumerate(battery_info):
            if battery['is_none']:
                continue
                
            y_pos = button_spacing + i * (button_height + button_spacing)
            
            # 创建现代化按钮 - 适配紧凑布局
            button_state = self._create_modern_button(
                ax_buttons, 0.02, y_pos, 0.96, button_height,
                battery['name'][:12] + '...' if len(battery['name']) > 12 else battery['name'], 
                lambda idx=battery['index']: toggle_battery_visibility(idx, button_state),
                is_toggle=True, 
                initial_state=battery['initial_state']
            )
            
            if button_state:
                button_states.append((battery['index'], button_state))

        logging.info("成功创建现代化电池选择按钮组 (%s-%s)", start_idx, end_idx)
        return button_states

    def _add_help_text(self, fig):
        """添加帮助文本到图表右上角"""
        try:
            fig.text(0.98, 0.85, "提示: 将鼠标悬停在数据点上查看详细信息", fontsize=7, ha='right')
            fig.text(0.98, 0.78, "快捷键: 滚轮缩放, 鼠标拖拽平移, 右键重置视图", fontsize=7, ha='right')
            logging.info("成功添加帮助文本")
        except (AttributeError, TypeError, ValueError) as e:
            logging.warning("添加帮助文本时出错: %s", e)

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
                    # 检查check_filter是否存在，如果不存在则默认使用过滤数据
                    if check_filter is not None:
                        try:
                            current_lines = lines_filtered if check_filter.get_status()[0] else lines_unfiltered
                        except (AttributeError, IndexError):
                            # 如果get_status方法不存在或返回错误，使用默认的过滤数据
                            current_lines = lines_filtered
                    else:
                        # 如果check_filter为None，默认使用过滤数据
                        current_lines = lines_filtered

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
                                    dist = ((x - event.xdata)**2 +
                                            (y - event.ydata) ** 2)**0.5
                                    # 只考虑一定范围内的点
                                    if (dist < min_dist
                                            and dist < 0.05 * (self.maxXaxis - self.listAxis[0])):
                                        min_dist = dist
                                        closest_point = (x, y, i)
                                        closest_line_label = line_label
                            except (AttributeError, TypeError, ValueError, IndexError) as e:
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

                        annot.set_text(
                            f"{label_text}\n点 {idx}:\nCharge: {x:.2f} mAh\nVoltage: {y:.4f} V")
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                    else:
                        if annot.get_visible():
                            annot.set_visible(False)
                            fig.canvas.draw_idle()

            # 连接事件
            fig.canvas.mpl_connect('motion_notify_event', on_hover)

        except (AttributeError, TypeError, ValueError) as e:
            logging.warning("添加悬停功能时出错: %s", e)

    # 注意：_show_error_plot方法已在前面定义，此方法已更新为增强版


if __name__ == '__main__':
    """
    主程序入口

    创建BatteryChartViewer类实例，自动执行初始化、数据读取和图表显示操作。
    
    支持命令行参数：
    - 第一个参数：可选，指定数据目录路径
    """
    import sys
    from PyQt6.QtWidgets import QApplication
    
    # 创建Qt应用程序实例
    app = QApplication(sys.argv)
    
    # 应用样式表 - QSS已启用
    try:
        from battery_analysis.ui.styles.style_manager import StyleManager, apply_modern_theme
        style_manager = StyleManager()
        
        # 统一加载样式文件 - 使用新的battery_analyzer.qss
        unified_style_path = Path(__file__).parent.parent / "ui" / "styles" / "battery_analyzer.qss"
        
        # 输出调试信息
        logging.info("尝试加载统一样式文件: %s", unified_style_path)
        
        if unified_style_path.exists():
            with open(unified_style_path, 'r', encoding='utf-8') as f:
                unified_style = f.read()
                app.setStyleSheet(unified_style)
                # 刷新UI以确保样式生效
                app.processEvents()
                app.style().unpolish(app)
                app.style().polish(app)
                app.update()
                logging.info("已应用统一电池分析器样式")
        else:
            # 如果统一样式文件不存在，尝试使用标准样式
            logging.warning("未找到统一样式文件: %s", unified_style_path)
            try:
                style_manager = StyleManager()
                style_manager.apply_global_style(app, "modern")
                logging.info("已应用备用全局主题样式")
            except (ImportError, AttributeError, TypeError, OSError) as e2:
                logging.error("备用样式应用失败: %s", e2)
    except (ImportError, AttributeError, TypeError, OSError) as e:
        logging.error("应用样式失败: %s", e)
        # 尝试使用标准样式作为最后备用方案
        try:
            style_manager = StyleManager()
            style_manager.apply_global_style(app, "modern")
            logging.info("最终备用样式已应用")
        except (ImportError, AttributeError, TypeError, OSError) as e3:
            logging.error("最终备用样式应用也失败: %s", e3)
    
    data_path = None
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
        logging.info("从命令行接收数据路径: %s", data_path)
    
    # 创建BatteryChartViewer实例
    figure = BatteryChartViewer(data_path=data_path)
    
    # 总是尝试显示图表（无论是正常数据还是错误图表），这样菜单栏样式就会被应用
    logging.info("尝试显示图表（无论是否有数据）")
    figure.plt_figure()
    
    # 启动事件循环
    logging.info("启动Qt事件循环")
    sys.exit(app.exec())
