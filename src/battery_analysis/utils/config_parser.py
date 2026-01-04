#!/usr/bin/env python3
"""
配置解析工具模块

提供安全的配置值解析功能，支持各种数据类型的兼容性转换
"""

import logging
from typing import Any, List, Union, Optional, Callable
from configparser import ConfigParser


class ConfigParseError(Exception):
    """配置解析错误异常"""
    pass


def safe_int_convert(value: str, default: int = 0) -> int:
    """
    安全地将字符串转换为整数
    
    支持格式：
    - 纯整数字符串："30" -> 30
    - 浮点数字符串："30.5" -> 30 (截断小数部分)
    - 科学计数法："1e2" -> 100
    
    Args:
        value: 要转换的字符串
        default: 转换失败时的默认值
        
    Returns:
        转换后的整数
        
    Raises:
        ConfigParseError: 当转换失败且没有提供默认值时
    """
    if not isinstance(value, str):
        value = str(value)
    
    try:
        return int(float(value.strip()))
    except (ValueError, TypeError) as e:
        logging.warning("无法将值 '%s' 转换为整数: %s", value, e)
        return default


def safe_float_convert(value: str, default: float = 0.0) -> float:
    """
    安全地将字符串转换为浮点数
    
    支持格式：
    - 整数字符串："30" -> 30.0
    - 浮点数字符串："30.5" -> 30.5
    - 科学计数法："1e2" -> 100.0
    
    Args:
        value: 要转换的字符串
        default: 转换失败时的默认值
        
    Returns:
        转换后的浮点数
    """
    if not isinstance(value, str):
        value = str(value)
    
    try:
        return float(value.strip())
    except (ValueError, TypeError) as e:
        logging.warning("无法将值 '%s' 转换为浮点数: %s", value, e)
        return default


def safe_bool_convert(value: str, default: bool = False) -> bool:
    """
    安全地将字符串转换为布尔值
    
    支持格式：
    - "true", "True", "1", "yes" -> True
    - "false", "False", "0", "no" -> False
    
    Args:
        value: 要转换的字符串
        default: 转换失败时的默认值
        
    Returns:
        转换后的布尔值
    """
    if not isinstance(value, str):
        value = str(value)
    
    value = value.strip().lower()
    if value in ("true", "1", "yes", "on"):
        return True
    elif value in ("false", "0", "no", "off"):
        return False
    else:
        logging.warning("无法将值 '%s' 转换为布尔值，使用默认值: %s", value, default)
        return default


def parse_config_list(config: ConfigParser, section: str, option: str, 
                     converter: Callable = str, default: Any = None, 
                     delimiter: str = ",") -> List[Any]:
    """
    安全解析配置列表
    
    从配置文件中读取逗号分隔的列表，并使用指定的转换器转换每个元素
    
    Args:
        config: ConfigParser实例
        section: 配置段名
        option: 配置项名
        converter: 元素转换函数（如int, float, safe_int_convert等）
        default: 转换失败时的默认值列表
        delimiter: 分隔符，默认为逗号
        
    Returns:
        转换后的列表
        
    Raises:
        ConfigParseError: 当配置项不存在且没有提供默认值时
    """
    if not config.has_section(section):
        if default is not None:
            logging.warning("配置段 '%s' 不存在，使用默认值: %s", section, default)
            return default
        raise ConfigParseError(f"配置段 '{section}' 不存在")
    
    if not config.has_option(section, option):
        if default is not None:
            logging.warning("配置项 '%s/%s' 不存在，使用默认值: %s", section, option, default)
            return default
        raise ConfigParseError(f"配置项 '{section}/{option}' 不存在")
    
    try:
        raw_value = config.get(section, option)
        items = [item.strip() for item in raw_value.split(delimiter) if item.strip()]
        
        # 转换每个元素
        result = []
        for item in items:
            try:
                converted_item = converter(item)
                result.append(converted_item)
            except (ValueError, TypeError) as e:
                logging.warning("无法转换元素 '%s': %s", item, e)
                if default is not None:
                    result.extend(default if isinstance(default, list) else [default])
                else:
                    result.append(converter.__defaults__[0] if hasattr(converter, '__defaults__') and converter.__defaults__ else None)
        
        logging.debug("成功解析配置 %s/%s: %s", section, option, result)
        return result
        
    except Exception as e:
        if default is not None:
            logging.error("解析配置 %s/%s 失败: %s，使用默认值: %s", section, option, e, default)
            return default
        raise ConfigParseError(f"解析配置 {section}/{option} 失败: {e}")


def parse_pulse_current_config(config: ConfigParser, section: str = "BatteryConfig", 
                             option: str = "PulseCurrent", 
                             default: List[int] = None) -> List[int]:
    """
    专门解析脉冲电流配置的便捷函数
    
    Args:
        config: ConfigParser实例
        section: 配置段名，默认为"BatteryConfig"
        option: 配置项名，默认为"PulseCurrent"
        default: 默认值，默认为[10, 20, 50]
        
    Returns:
        脉冲电流级别列表
    """
    if default is None:
        default = [10, 20, 50]
    
    return parse_config_list(config, section, option, safe_int_convert, default)


def parse_voltage_config(config: ConfigParser, section: str = "BatteryConfig", 
                       option: str = "CutOffVoltage", 
                       default: List[float] = None) -> List[float]:
    """
    专门解析电压配置的便捷函数
    
    Args:
        config: ConfigParser实例
        section: 配置段名，默认为"BatteryConfig"
        option: 配置项名，默认为"CutOffVoltage"
        default: 默认值，默认为[2.0, 1.8]
        
    Returns:
        电压级别列表
    """
    if default is None:
        default = [2.0, 1.8]
    
    return parse_config_list(config, section, option, safe_float_convert, default)


# 使用示例
if __name__ == "__main__":
    # 示例用法
    from configparser import ConfigParser
    
    # 创建示例配置
    config = ConfigParser()
    config.add_section("BatteryConfig")
    config.set("BatteryConfig", "PulseCurrent", "30, 26.5, 15, 7.5")
    config.set("BatteryConfig", "CutOffVoltage", "2.6, 2.5, 2.4")
    config.set("BatteryConfig", "EnableFeature", "true")
    
    # 测试解析
    try:
        pulse_currents = parse_pulse_current_config(config)
        print(f"脉冲电流: {pulse_currents}")
        
        voltages = parse_voltage_config(config)
        print(f"截止电压: {voltages}")
        
        # 手动解析布尔值
        enable_feature = config.get("BatteryConfig", "EnableFeature")
        is_enabled = safe_bool_convert(enable_feature)
        print(f"功能启用: {is_enabled}")
        
    except ConfigParseError as e:
        print(f"配置解析错误: {e}")