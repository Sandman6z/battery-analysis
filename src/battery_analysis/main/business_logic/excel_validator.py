"""
Excel文件验证模块
"""

import logging

from battery_analysis.utils.file_validator import FileValidator
from battery_analysis.utils.processors.excel_processor import is_metadata_header, read_excel_smart

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

    # ── 检查是否含有标准列名（子串匹配，兼容"放电容量(mAh)"等带单位的列名）──
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
    col_strs = [str(c) for c in df.columns]
    has_common_column = any(
        keyword in col for col in col_strs for keyword in common_columns
    )

    # ── 综合判断：列名不对 + 数据也无法识别 → 致命错误 ──────
    if not has_common_column and not has_numeric and not has_potential_numeric:
        return False, (
            f"File content cannot be recognized: {filename}\n"
            f"No standard column names (e.g., Capacity/Voltage/Current) found, "
            f"and the data columns cannot be recognized as numeric types."
        )

    # ── 非致命警告 ────────────────────────────────────────────
    # 检测已知的表头格式问题：全部 Unnamed、或元数据独占首行（长描述 + Unnamed）
    header_issue = is_metadata_header(df.columns) or all(
        str(col).startswith("Unnamed") for col in df.columns
    )

    if header_issue and (has_numeric or has_potential_numeric):
        # 表头格式问题但数据可读——单一简洁提示
        logger.info("Sheet has non-standard headers but contains numeric data: %s", filename)
    else:
        if not has_numeric and has_potential_numeric:
            logger.warning("Sheet may contain numeric data but was not recognized: %s", filename)

        if not has_common_column:
            logger.warning(
                "Sheet may be missing required columns: %s, found columns: %s",
                filename,
                list(df.columns),
            )

    return True, ""


def validate_excel_file(file_path, filename, cache):
    """
    验证Excel文件的有效性

    Returns:
        tuple: (是否有效, 错误消息, 数据框)
    """
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
        df = read_excel_smart(file_path)

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
