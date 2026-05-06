"""
Excel文件验证模块
"""

import logging
import pandas as pd


logger = logging.getLogger(__name__)


def validate_excel_filename(filename):
    """验证Excel文件名的有效性"""
    from battery_analysis.utils.file_validator import FileValidator
    validator = FileValidator()
    return validator.validate_excel_filename(filename)


def validate_excel_file_content(df, filename):
    """
    验证Excel文件内容的有效性

    Returns:
        tuple: (是否有效, 错误消息)
    """
    if df.empty:
        return False, f"Sheet页为空: {filename}"

    if len(df.columns) == 0:
        return False, f"Sheet页无列数据: {filename}"

    if len(df) == 0:
        return False, f"Sheet页无行数据: {filename}"

    numeric_columns = df.select_dtypes(include=['number']).columns

    if len(numeric_columns) == 0:
        has_potential_numeric = False
        for col in df.columns:
            try:
                pd.to_numeric(df[col], errors='coerce')
                has_potential_numeric = True
                break
            except (ValueError, TypeError, KeyError):
                continue

        if has_potential_numeric:
            logger.warning(f"Sheet页可能包含数值数据但未被识别: {filename}")
        else:
            logger.warning(f"Sheet页无数值列数据: {filename}")

    common_columns = ['Capacity', '容量', 'Voltage', '电压', 'Current', '电流',
                      'Cycle', '循环', 'Temperature', '温度', 'Time', '时间']
    has_common_column = any(col in df.columns for col in common_columns)
    if not has_common_column:
        logger.warning(f"Sheet页可能缺少必要的列: {filename}, 找到列: {list(df.columns)}")

    return True, ""


def validate_excel_file(file_path, filename, cache, optimize_dataframe_memory):
    """
    验证Excel文件的有效性

    Returns:
        tuple: (是否有效, 错误消息, 数据框)
    """
    cache_key = f"{file_path}:{filename}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.debug("从缓存读取文件验证结果: %s", cache_key)
        return cached_result

    from battery_analysis.utils.file_validator import FileValidator
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
        df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl', header=0)
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
        result = (False, f"Excel文件读取失败: {filename} - {str(e)}", None)
        cache.put(cache_key, result)
        return result
