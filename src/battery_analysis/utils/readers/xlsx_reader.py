"""xlsx 文件读取器，封装 pandas/calamine 读取逻辑"""
import os
import re
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def read_xlsx_sheets(filepath: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """用 calamine 引擎一次性读取 xlsx 的三个工作表，返回 (cycle_df, step_df, record_df)"""
    sheets = pd.read_excel(filepath, sheet_name=[0, 1, 2], header=None, engine='calamine')
    return sheets[0], sheets[1], sheets[2]


def extract_test_date_from_xls(filepath: str) -> str:
    """
    从 Excel 文件中提取 Test Date 字段

    用 calamine 引擎只读取各工作表前 20 行，搜索 "Test Date" 或 "测试日期"
    单元格，尝试多种日期格式解析。如果无法提取，尝试从文件名解析。

    Args:
        filepath: Excel 文件路径

    Returns:
        str: 格式化的日期字符串 (YYYYMMDD)，如果无法提取则返回默认值
    """
    try:
        sheets = pd.read_excel(
            filepath, sheet_name=None, header=None, nrows=20, engine="calamine")

        # 搜索所有工作表中的 "Test Date" 字段（只查前 20 行）
        for sheet_df in sheets.values():
            for row in range(min(20, len(sheet_df))):
                for col in range(len(sheet_df.columns)):
                    cell_value = sheet_df.iloc[row, col]
                    if isinstance(cell_value, str) and (
                        "Test Date" in cell_value or "测试日期" in cell_value
                    ):
                        # 右侧相邻单元格
                        if col + 1 < len(sheet_df.columns):
                            parsed = _parse_date_str(sheet_df.iloc[row, col + 1])
                            if parsed:
                                return parsed
                        # 下方单元格
                        if row + 1 < len(sheet_df):
                            parsed = _parse_date_str(sheet_df.iloc[row + 1, col])
                            if parsed:
                                return parsed

        # 找不到 Test Date 字段，尝试从文件名提取
        file_name = os.path.basename(filepath)
        logger.debug("Parsing date from file name: %s", file_name)
        parsed = _parse_date_from_filename(file_name)
        if parsed:
            return parsed

    except Exception as e:  # pylint: disable=broad-exception-caught
        # 日期提取是尽力而为：任何读取/解析失败都回退默认值
        logger.error(
            "Failed to extract Test Date from Excel: %s, error: %s", filepath, e)

    # 确保总是有返回值
    return "00000000"


def _parse_date_str(date_value) -> str | None:
    """尝试把单元格值解析为日期，返回 YYYYMMDD；无法解析返回 None"""
    if not isinstance(date_value, str) or not date_value.strip():
        return None
    date_str = date_value.strip()
    # 格式1: 10.06.2025 - 08.07.2025（取起始日期）
    if "-" in date_str and "." in date_str:
        start = date_str.split("-")[0].strip()
        parts = start.split(".")
        if len(parts) == 3:
            day, month, year = parts
            return f"{year.zfill(4)}{month.zfill(2)}{day.zfill(2)}"
    # 格式2: 2025-06-10
    if "-" in date_str:
        parts = date_str.split("-")
        if len(parts) >= 3:
            year, month, day = parts[:3]
            return f"{year.zfill(4)}{month.zfill(2)}{day.zfill(2)}"
    return None


def _parse_date_from_filename(file_name: str) -> str | None:
    """尝试从文件名提取日期，返回 YYYYMMDD；无法解析返回 None"""
    # 匹配文件名中所有连续的数字组，取最后一组的前 8 位
    digit_groups = re.findall(r"(\d+)", file_name)
    if digit_groups:
        last_digit_group = digit_groups[-1]
        if len(last_digit_group) >= 8:
            date_str = last_digit_group[:8]
            try:
                year = int(date_str[:4])
                if 2000 <= year <= 2100:
                    return date_str
                logger.warning("Extracted year %s is not in valid range", year)
            except ValueError:
                logger.error("Could not parse year")

    # 其他常见日期格式
    date_patterns = [
        (r"(\d{4})-(\d{2})-(\d{2})", False),  # 2025-06-10
        (r"(\d{2})\.(\d{2})\.(\d{4})", True),  # 10.06.2025
    ]
    for pattern, is_dmy in date_patterns:
        match = re.search(pattern, file_name)
        if match:
            groups = match.groups()
            if is_dmy:
                day, month, year = groups
                return f"{year}{month.zfill(2)}{day.zfill(2)}"
            year, month, day = groups
            return f"{year}{month.zfill(2)}{day.zfill(2)}"
    return None
