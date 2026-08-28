"""
Excel文件验证模块
"""

import logging

from battery_analysis.utils.file_validator import FileValidator

logger = logging.getLogger(__name__)


def validate_excel_filename(filename):
    """验证Excel文件名的有效性"""
    validator = FileValidator()
    return validator.validate_excel_filename(filename)


def validate_excel_file_content(df, filename):
    """
    验证Excel文件内容的有效性

    Returns:
        tuple: (是否有效, 错误消息)
    """
    import pandas as pd

    if df.empty:
        return False, f"Sheet is empty: {filename}"

    if len(df.columns) == 0:
        return False, f"Sheet has no column data: {filename}"

    if len(df) == 0:
        return False, f"Sheet has no row data: {filename}"

    # ── 检查是否含有数值数据 ──────────────────────────────────
    numeric_columns = df.select_dtypes(include=["number"]).columns
    has_numeric = len(numeric_columns) > 0
    has_potential_numeric = False

    if not has_numeric:
        for col in df.columns:
            try:
                pd.to_numeric(df[col], errors="coerce")
                has_potential_numeric = True
                break
            except (ValueError, TypeError, KeyError):
                continue

    # ── 检查是否含有标准列名 ──────────────────────────────────
    common_columns = [
        "Capacity",
        "容量",
        "Voltage",
        "电压",
        "Current",
        "电流",
        "Cycle",
        "循环",
        "Temperature",
        "温度",
        "Time",
        "时间",
    ]
    has_common_column = any(col in df.columns for col in common_columns)

    # ── 综合判断：列名不对 + 数据也无法识别 → 致命错误 ──────
    if not has_common_column and not has_numeric and not has_potential_numeric:
        return False, (
            f"File content cannot be recognized: {filename}\n"
            f"No standard column names (e.g., Capacity/Voltage/Current) found, "
            f"and the data columns cannot be recognized as numeric types."
        )

    # ── 非致命警告 ────────────────────────────────────────────
    if not has_numeric and has_potential_numeric:
        logger.warning(f"Sheet may contain numeric data but was not recognized: {filename}")

    if not has_common_column:
        logger.warning(
            f"Sheet may be missing required columns: {filename}, found columns: {list(df.columns)}"
        )

    return True, ""


def validate_excel_file(file_path, filename, cache, optimize_dataframe_memory):
    """
    验证Excel文件的有效性

    Returns:
        tuple: (是否有效, 错误消息, 数据框)
    """
    import pandas as pd

    cache_key = f"{file_path}:{filename}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.debug("Reading file validation result from cache: %s", cache_key)
        return cached_result

    validator = FileValidator()

    is_valid, error_msg = validate_excel_filename(filename)
    if not is_valid:
        result = (False, error_msg, None)
        cache.put(cache_key, result)
        return result

    is_valid, error_msg = validator.validate_file_not_empty(file_path)
    if not is_valid:
        result = (False, error_msg, None)
        cache.put(cache_key, result)
        return result

    try:
        df = pd.read_excel(file_path, sheet_name=0, engine="calamine", header=0)
        df = optimize_dataframe_memory(df)

        is_valid, error_msg = validate_excel_file_content(df, filename)
        if not is_valid:
            result = (False, error_msg, None)
            cache.put(cache_key, result)
            return result

        result = (True, "", df)
        cache.put(cache_key, result)
        return result

    except Exception as e:
        result = (False, f"Failed to read Excel file: {filename} - {e!s}", None)
        cache.put(cache_key, result)
        return result
