"""
用户配置管理模块

该模块负责管理电池分析应用的用户配置，包括：
- 加载用户配置
- 保存用户配置
- 管理配置项，包括电池类型、温度设置、输出路径等
"""

# 标准库导入
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

# 第三方库导入
import PyQt6.QtCore as QC


class UserSettingsManager:
    """
    用户配置管理器类，负责用户配置的加载和保存
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化用户配置管理器
        
        Args:
            config_path: 主配置文件路径，用于定位用户配置文件
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.user_config_path = None
        self.user_settings = None
        
        # 初始化用户配置文件路径
        self._initialize_user_config_path()
        
        # 初始化用户配置QSettings实例
        self._initialize_user_settings()
    
    def _initialize_user_config_path(self):
        """
        初始化用户配置文件路径
        """
        if self.config_path and Path(self.config_path).exists():
            self.user_config_path = os.path.join(
                os.path.dirname(self.config_path), 
                "user_settings.ini"
            )
        else:
            self.user_config_path = None
    
    def _initialize_user_settings(self):
        """
        初始化用户配置QSettings实例
        """
        if self.user_config_path:
            self.user_settings = QC.QSettings(
                self.user_config_path, 
                QC.QSettings.Format.IniFormat
            )
        else:
            self.user_settings = QC.QSettings()
    
    def load_user_settings(self) -> Dict[str, Any]:
        """
        加载用户配置
        
        Returns:
            用户配置字典，包含所有配置项
        """
        try:
            user_config = {}
            
            # 加载电池类型相关设置
            user_config["BatteryType"] = self.user_settings.value("UserConfig/BatteryType")
            user_config["ConstructionMethod"] = self.user_settings.value("UserConfig/ConstructionMethod")
            user_config["SpecificationType"] = self.user_settings.value("UserConfig/SpecificationType")
            user_config["SpecificationMethod"] = self.user_settings.value("UserConfig/SpecificationMethod")
            user_config["Manufacturer"] = self.user_settings.value("UserConfig/Manufacturer")
            user_config["TesterLocation"] = self.user_settings.value("UserConfig/TesterLocation")
            user_config["TestedBy"] = self.user_settings.value("UserConfig/TestedBy")
            user_config["ReportedBy"] = self.user_settings.value("UserConfig/ReportedBy")
            
            # 加载温度设置
            user_config["TemperatureType"] = self.user_settings.value("UserConfig/TemperatureType")
            user_config["FreezerTemperature"] = self.user_settings.value("UserConfig/FreezerTemperature")
            
            # 加载输出路径设置
            user_config["OutputPath"] = self.user_settings.value("UserConfig/OutputPath")
            
            self.logger.info("用户配置加载成功")
            return user_config
        except (AttributeError, TypeError, KeyError, OSError) as e:
            self.logger.error("加载用户配置失败: %s", e)
            return {}
    
    def save_user_settings(self, settings: Dict[str, Any]):
        """
        保存用户配置
        
        Args:
            settings: 包含所有配置项的字典
        """
        try:
            # 保存电池类型相关设置
            if "BatteryType" in settings:
                self.user_settings.setValue("UserConfig/BatteryType", settings["BatteryType"])
            if "ConstructionMethod" in settings:
                self.user_settings.setValue("UserConfig/ConstructionMethod", settings["ConstructionMethod"])
            if "SpecificationType" in settings:
                self.user_settings.setValue("UserConfig/SpecificationType", settings["SpecificationType"])
            if "SpecificationMethod" in settings:
                self.user_settings.setValue("UserConfig/SpecificationMethod", settings["SpecificationMethod"])
            if "Manufacturer" in settings:
                self.user_settings.setValue("UserConfig/Manufacturer", settings["Manufacturer"])
            if "TesterLocation" in settings:
                self.user_settings.setValue("UserConfig/TesterLocation", settings["TesterLocation"])
            if "TestedBy" in settings:
                self.user_settings.setValue("UserConfig/TestedBy", settings["TestedBy"])
            if "ReportedBy" in settings:
                self.user_settings.setValue("UserConfig/ReportedBy", settings["ReportedBy"])
            
            # 保存温度设置
            if "TemperatureType" in settings:
                self.user_settings.setValue("UserConfig/TemperatureType", settings["TemperatureType"])
            if "FreezerTemperature" in settings:
                self.user_settings.setValue("UserConfig/FreezerTemperature", settings["FreezerTemperature"])
            
            # 保存输出路径设置
            if "OutputPath" in settings:
                self.user_settings.setValue("UserConfig/OutputPath", settings["OutputPath"])
            
            # 同步保存到文件
            self.user_settings.sync()
            self.logger.info("用户配置保存成功")
        except (AttributeError, TypeError, KeyError, OSError) as e:
            self.logger.error("保存用户配置失败: %s", e)
    
    def update_user_settings(self, **kwargs):
        """
        更新用户配置项
        
        Args:
            **kwargs: 要更新的配置项键值对
        """
        # 先加载现有配置
        current_settings = self.load_user_settings()
        
        # 更新配置项
        current_settings.update(kwargs)
        
        # 保存更新后的配置
        self.save_user_settings(current_settings)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        获取单个配置项
        
        Args:
            key: 配置项键
            default: 默认值，当配置项不存在时返回
            
        Returns:
            配置项值或默认值
        """
        try:
            value = self.user_settings.value(f"UserConfig/{key}")
            return value if value is not None else default
        except (AttributeError, TypeError, KeyError, OSError) as e:
            self.logger.error("获取配置项失败: %s, %s", key, e)
            return default
    
    def set_setting(self, key: str, value: Any):
        """
        设置单个配置项
        
        Args:
            key: 配置项键
            value: 配置项值
        """
        try:
            self.user_settings.setValue(f"UserConfig/{key}", value)
            self.user_settings.sync()
        except (AttributeError, TypeError, KeyError, OSError) as e:
            self.logger.error("设置配置项失败: %s, %s", key, e)
    
    def get_user_config_path(self) -> Optional[str]:
        """
        获取用户配置文件路径
        
        Returns:
            用户配置文件路径
        """
        return self.user_config_path
