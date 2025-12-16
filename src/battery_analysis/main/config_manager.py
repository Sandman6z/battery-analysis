"""
电池数据分析配置管理模块

本模块提供了用于电池数据分析的配置管理功能。它能够从配置文件读取配置，
并提供配置值的安全获取方法。

主要功能：
- 加载配置文件（setting.ini 和 Config_BatteryAnalysis.ini）
- 安全获取配置值
- 处理特殊配置项（如脉冲电流级别、规则配置等）
"""

import os
import logging
import configparser
from pathlib import Path
from battery_analysis.utils.config_utils import find_config_file

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ConfigManager:
    """
    配置管理类，负责配置文件的读取和管理
    """
    
    def __init__(self, project_root):
        """
        初始化配置管理类
        
        Args:
            project_root: 项目根目录路径
        """
        self.config = configparser.ConfigParser()
        self.project_root = project_root
        self.strPltPath = None
        self.strPltTitle = None
        self.strInfoImageCsvPath = None
        self.listPulseCurrentLevel = None
        self.intCurrentLevelNum = 0
        self.listCoinCell = []
        self.listPouchCell = []
        self.strPltName = None
        self.maxXaxis = 1000  # 默认最大值
        
        # 初始化默认配置
        if not self.config.has_section("PltConfig"):
            self.config.add_section("PltConfig")
    
    def load_config_file(self):
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
            else:
                logging.warning("未找到setting.ini配置文件")
                return
            
            # 回退到Config_BatteryAnalysis.ini（兼容旧版本）
            config_battery_path = find_config_file("Config_BatteryAnalysis.ini")
            if config_battery_path and os.path.exists(config_battery_path):
                self.config.read(config_battery_path, encoding='utf-8')
                logging.info("成功读取Config_BatteryAnalysis.ini配置")
                return
            
            logging.warning("未找到配置文件，使用默认配置")
        except Exception as e:
            logging.error(f"配置读取失败: {e}，使用默认配置")
    
    def read_configurations(self):
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
        self.strPltPath = self.get_config_value("PltConfig", "Path", os.getcwd())
        
        # 读取图表标题配置
        self.strPltTitle = self.get_config_value("PltConfig", "Title", "Battery Test Results")
        
        # 设置CSV文件路径
        self.strInfoImageCsvPath = os.path.join(self.strPltPath, "Info_Image.csv")
        
        # 读取脉冲电流级别配置
        self.listPulseCurrentLevel = self.get_pulse_current_level()
        self.intCurrentLevelNum = len(self.listPulseCurrentLevel)
        
        # 读取电池规格类型配置
        self.listCoinCell = self.get_config_list("BatteryConfig", "SpecificationTypeCoinCell")
        self.listPouchCell = self.get_config_list("BatteryConfig", "SpecificationTypePouchCell")
        
        # 设置图表标题
        self.strPltName = self.set_plot_title()
    
    def get_config_value(self, section, option, default_value):
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
    
    def get_config_list(self, section, option):
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
    
    def get_pulse_current_level(self):
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
    
    def set_plot_title(self):
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
    
    def read_rules_configuration(self):
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