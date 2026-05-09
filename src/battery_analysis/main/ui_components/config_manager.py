"""
配置管理器模块

这个模块实现了电池分析应用的配置管理功能，包括：
- 配置文件的查找和加载
- 配置值的读取和解析
- 用户设置的加载和保存
- 配置变更的处理

对 setting.ini 的读写统一委托给 ConfigService（单一路径，无降级无兼容）。
"""

# 标准库导入
import logging
from pathlib import Path
from typing import Any, List, Optional

# 本地应用/库导入


class ConfigManager:
    """
    配置管理器类，负责配置文件的读取和写入
    对 setting.ini 的读写统一通过 ConfigService（单一路径）。
    """

    # INI 键到 JSON 点路径的映射
    _INI_TO_JSON_KEY = {
        "BatteryConfig/BatteryType": "battery.types",
        "BatteryConfig/ConstructionMethod": "battery.constructionMethods",
        "BatteryConfig/SpecificationTypeCoinCell": "battery.specifications.Coin Cell",
        "BatteryConfig/SpecificationTypePouchCell": "battery.specifications.Pouch Cell",
        "BatteryConfig/SpecificationMethod": "battery.specificationMethods",
        "BatteryConfig/Manufacturer": "battery.manufacturers",
        "BatteryConfig/Rules": "battery.rules",
        "BatteryConfig/PulseCurrent": "battery.pulseCurrents",
        "BatteryConfig/CutOffVoltage": "battery.cutOffVoltages",
        "TestConfig/TesterLocation": "test.locations",
        "TestConfig/TestedBy": "test.testedBy",
    }

    def __init__(self, main_window):
        """
        初始化配置管理器

        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._config_service = None
        self.config_path = None
        self.b_has_config = True

        # 缓存 ConfigService 引用
        self._init_config_service()

        # 初始化配置
        self._initialize_config()

    def _init_config_service(self):
        """获取并缓存 ConfigService 引用"""
        try:
            self._config_service = self.main_window._get_service("config")
        except (AttributeError, TypeError) as e:
            self.logger.warning("无法获取 ConfigService: %s", e)
            self._config_service = None

    def _initialize_config(self):
        """
        初始化配置文件路径
        """
        self.logger.info("[_initialize_config] 开始初始化配置文件...")

        if self._config_service:
            self._config_service.clear_cache()
            try:
                config_path_result = self._config_service.find_config_file(use_cache=False)
                self.config_path = str(config_path_result) if config_path_result else None
            except (OSError, TypeError, ValueError) as e:
                self.logger.warning("从 ConfigService 查找配置失败: %s", e)
                self.config_path = None

        self.logger.info(f"[_initialize_config] config_path: {self.config_path}")
        config_path_obj = Path(self.config_path) if self.config_path else None
        path_exists = config_path_obj.exists() if config_path_obj else False
        self.b_has_config = bool(self.config_path and path_exists)

        if not self.b_has_config:
            self.logger.info("[_initialize_config] 配置文件不存在")

    def get_config(self, config_key: str) -> List[str]:
        """
        获取配置值并处理为列表格式，通过 ConfigService 读取

        Args:
            config_key: 配置键，格式为 "Section/Key"

        Returns:
            配置值列表
        """
        if not self.b_has_config or not self._config_service:
            return []

        try:
            json_key = self._INI_TO_JSON_KEY.get(config_key, config_key)
            value = self._config_service.get_config_value(json_key)
            if value is None:
                return []
            if isinstance(value, list):
                return [str(v) for v in value]
            if isinstance(value, str):
                return [v.strip().strip('"') for v in value.split(",") if v.strip()]
            return [str(value)]
        except Exception as e:
            logging.error("读取配置 %s 失败: %s", config_key, e)
            return []

    def save_user_settings(self):
        """
        保存用户配置（已弃用，保留空方法避免调用方报错）
        """
        pass
    
    def get_current_config_path(self) -> Optional[str]:
        """
        获取当前配置文件路径

        Returns:
            配置文件路径
        """
        return self.config_path

    def has_config(self) -> bool:
        """
        检查是否有配置文件

        Returns:
            是否有配置文件
        """
        return self.b_has_config

    def reload_config(self):
        """
        重新加载配置文件（委托 ConfigService 清除缓存后强制重读）
        """
        if self._config_service:
            self._config_service.reload_config()
        # 更新路径信息但不 clear_cache（避免强制下游重新读取文件）
        if self._config_service:
            try:
                config_path_result = self._config_service.find_config_file(use_cache=False)
                self.config_path = str(config_path_result) if config_path_result else None
            except (OSError, TypeError, ValueError) as e:
                self.logger.warning("从 ConfigService 查找配置失败: %s", e)
                self.config_path = None
        config_path_obj = Path(self.config_path) if self.config_path else None
        path_exists = config_path_obj.exists() if config_path_obj else False
        self.b_has_config = bool(self.config_path and path_exists)
    
    def update_config(self, test_info) -> None:
        """
        更新内存中的图表相关设置，不再修改配置文件
        
        Args:
            test_info: 测试信息列表
        """
        try:
            # 初始化checker_update_config如果不存在
            if not hasattr(self.main_window, 'checker_update_config'):
                from battery_analysis.main.utils import Checker
                self.main_window.checker_update_config = Checker()
            
            self.main_window.checker_update_config.clear()
            
            # 不再更新配置文件，只在内存中处理
            # 图表路径和标题将在需要时动态计算
            
            bSetTitle = False
            rules = self.main_window.get_config("BatteryConfig/Rules")
            specification_type = self.main_window.comboBox_Specification_Type.currentText()
            strPulseCurrent = "".join(
                [f"{current_level}mA/" for current_level in self.main_window.listCurrentLevel])
            
            for rule in rules:
                rule_parts = rule.split("/")
                if not self.main_window.cc_current:
                    self.main_window.cc_current = rule_parts[5]
                if rule_parts[0] == specification_type or rule_parts[0] in specification_type:
                    # 标题信息将在需要时动态生成
                    bSetTitle = True
                    break
            
            if not bSetTitle:
                self.main_window.checker_update_config.set_error("PltTitle")
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    f"[Error]: No rules for {specification_type}")
        except (AttributeError, TypeError, ValueError, OSError) as e:
            self.logger.error("更新配置失败: %s", e)
    
    def rename_pltPath(self, strTestDate):
        """
        根据测试日期重命名图表保存路径，不再修改配置文件
        
        Args:
            strTestDate: 测试日期字符串
        """
        try:
            # 不再更新配置文件，只在内存中处理
            # 图表路径将在需要时动态计算
            pass
        except (AttributeError, TypeError, ValueError, OSError) as e:
            self.logger.error("重命名图表路径失败: %s", e)
