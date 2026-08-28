#!/usr/bin/env python3
"""
配置解析工具模块

提供安全的配置值解析功能，支持各种数据类型的兼容性转换
"""

import logging


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
        logging.warning("Unable to convert value '%s' to integer: %s", value, e)
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
        logging.warning("Unable to convert value '%s' to float: %s", value, e)
        return default
