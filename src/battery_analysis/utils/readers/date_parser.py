"""测试日期解析工具"""

from typing import Optional


def _parse_date_string(date_str: str) -> Optional[str]:
    """尝试将单个日期字符串解析为 YYYYMMDD 格式

    支持格式: YYYYMMDD, YYYY-MM-DD, YYYY/MM/DD
    返回 YYYYMMDD 字符串，或 None（解析失败）
    """
    if not date_str:
        return None

    # 已经是 YYYYMMDD 格式
    if len(date_str) == 8 and date_str.isdigit():
        return date_str

    # 取空格前部分（去掉时间）
    date_part = date_str.split(" ")[0] if " " in date_str else date_str

    try:
        if "-" in date_part:
            parts = date_part.split("-")
        elif "/" in date_part:
            parts = date_part.split("/")
        else:
            return None

        if len(parts) == 3:
            return f"{parts[0]}{parts[1]}{parts[2]}"
    except (ValueError, TypeError, IndexError):
        pass

    return None


def parse_test_date(
    test_date: str,
    original_cycle_date: str = "",
    fallback_date_str: str = "",
) -> str:
    """解析测试日期，返回 YYYYMMDD 格式的日期字符串

    按优先级尝试多个日期来源：
    1. test_date（首选，来自 Excel 或文件名提取）
    2. original_cycle_date（备选，原始周期日期）
    3. fallback_date_str（最终回退，如 "YYYY-MM-DD HH:MM:SS" 格式）
    4. "00000000"（全部失败）

    Args:
        test_date: 首选日期字符串
        original_cycle_date: 备选日期字符串
        fallback_date_str: 最终回退日期字符串

    Returns:
        YYYYMMDD 格式的日期字符串，或 "00000000"
    """
    # 优先级 1: test_date
    result = _parse_date_string(test_date)
    if result:
        return result

    # test_date 有内容但未被识别为标准格式时，保持原样（向后兼容）
    if test_date:
        return test_date

    # 优先级 2: original_cycle_date
    result = _parse_date_string(original_cycle_date)
    if result:
        return result

    # original_cycle_date 有内容但未被识别为标准格式时，保持原样（向后兼容）
    if original_cycle_date:
        return original_cycle_date

    # 优先级 3: fallback_date_str
    result = _parse_date_string(fallback_date_str)
    if result:
        return result

    # fallback_date_str 有内容但未被识别为标准格式时，保持原样（向后兼容）
    if fallback_date_str:
        return fallback_date_str

    return "00000000"
