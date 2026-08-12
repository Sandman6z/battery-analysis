"""xlsx 文件读取器，封装 pandas/xlrd 读取逻辑"""
import os
import re
import logging

import pandas as pd
import xlrd as rd

logger = logging.getLogger(__name__)


def read_xlsx_sheets(filepath: str):
    """用 pandas 读取 xlsx 的三个工作表，返回 (cycle_df, step_df, record_df)"""
    cycle_df = pd.read_excel(filepath, sheet_name=0, header=None, engine='openpyxl')
    step_df = pd.read_excel(filepath, sheet_name=1, header=None, engine='openpyxl')
    record_df = pd.read_excel(filepath, sheet_name=2, header=None, engine='openpyxl')
    return cycle_df, step_df, record_df


def extract_test_date_from_xls(filepath: str) -> str:
    """
    从 Excel 文件中提取 Test Date 字段

    使用 xlrd 读取，搜索 "Test Date" 或 "测试日期" 单元格，
    尝试多种日期格式解析。
    如果无法提取，尝试从文件名解析。

    Args:
        filepath: Excel 文件路径

    Returns:
        str: 格式化的日期字符串 (YYYYMMDD)，如果无法提取则返回默认值
    """
    try:
        rb = rd.open_workbook(filepath)

        # 搜索所有工作表中的"Test Date"字段
        for sheet_idx in range(len(rb.sheets())):
            sheet = rb.sheets()[sheet_idx]
            for row in range(min(20, sheet.nrows)):  # 只搜索前20行以提高效率
                for col in range(sheet.ncols):
                    cell_value = sheet.cell_value(row, col)
                    if isinstance(cell_value, str):
                        # 搜索包含Test Date的单元格
                        if "Test Date" in cell_value or "测试日期" in cell_value:
                            # 尝试从相邻单元格获取日期值
                            if col + 1 < sheet.ncols:
                                date_value = sheet.cell_value(row, col + 1)
                                if isinstance(date_value, str) and date_value.strip():
                                    # 处理多种日期格式
                                    date_str = date_value.strip()
                                    # 格式1: 10.06.2025 - 08.07.2025
                                    if "-" in date_str and "." in date_str:
                                        start_date_part = date_str.split(
                                            "-")[0].strip()
                                        if "." in start_date_part:
                                            parts = start_date_part.split(
                                                ".")
                                            if len(parts) == 3:
                                                try:
                                                    day, month, year = parts
                                                    # 确保值可以转换为整数并直接使用
                                                    return f"{year.zfill(4)}" \
                                                            f"{month.zfill(2)}" \
                                                            f"{day.zfill(2)}"
                                                except ValueError:
                                                    logger.warning(
                                                        "Date parts could not be converted to integers: %s", parts)
                                    # 格式2: 2025-06-10
                                    elif "-" in date_str:
                                        parts = date_str.split("-")
                                        if len(parts) >= 3:
                                            try:
                                                year, month, day = parts[:3]
                                                # 确保值可以转换为整数并直接使用
                                                return f"{year.zfill(4)}" \
                                                        f"{month.zfill(2)}" \
                                                        f"{day.zfill(2)}"
                                            except ValueError:
                                                logger.warning(
                                                    "Date parts could not be converted to integers: %s", parts[:3])

                            # 尝试从下方单元格获取日期值
                            if row + 1 < sheet.nrows:
                                date_value = sheet.cell_value(row + 1, col)
                                if isinstance(date_value, str) and date_value.strip():
                                    # 处理多种日期格式
                                    date_str = date_value.strip()
                                    if "-" in date_str and "." in date_str:
                                        start_date_part = date_str.split(
                                            "-")[0].strip()
                                        if "." in start_date_part:
                                            parts = start_date_part.split(
                                                ".")
                                            if len(parts) == 3:
                                                try:
                                                    day, month, year = parts
                                                    # 确保值可以转换为整数并直接使用
                                                    return f"{year.zfill(4)}" \
                                                            f"{month.zfill(2)}" \
                                                            f"{day.zfill(2)}"
                                                except ValueError:
                                                    logger.warning(
                                                        "Date parts could not be converted to integers: %s", parts)
                                    elif "-" in date_str:
                                        parts = date_str.split("-")
                                        if len(parts) >= 3:
                                            try:
                                                year, month, day = parts[:3]
                                                # 确保值可以转换为整数并直接使用
                                                return f"{year.zfill(4)}" \
                                                        f"{month.zfill(2)}" \
                                                        f"{day.zfill(2)}"
                                            except ValueError:
                                                logger.warning(
                                                    "Date parts could not be converted to integers: %s", parts[:3])

        # 如果找不到Test Date字段，尝试从文件名提取
        file_name = os.path.basename(filepath)
        logger.debug("Parsing date from file name: %s", file_name)

        # 尝试从文件名中提取日期
        # 匹配文件名中所有连续的数字组
        digit_groups = re.findall(r'(\d+)', file_name)
        if digit_groups:
            # 取最后一组连续数字
            last_digit_group = digit_groups[-1]
            # 提取前8位作为日期（如果长度足够）
            if len(last_digit_group) >= 8:
                date_str = last_digit_group[:8]
                logger.debug("Extracted date: %s", date_str)
                # 验证提取的日期是否有效（简单验证：年份在合理范围）
                try:
                    year = int(date_str[:4])
                    if 2000 <= year <= 2100:
                        return date_str
                    logger.warning("Extracted year %s is not in valid range", year)
                except ValueError:
                    logger.error("Could not parse year")
        # 然后尝试其他常见的日期格式
        date_patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # 2025-06-10
            r'(\d{2})\.(\d{2})\.(\d{4})'  # 10.06.2025
        ]

        for pattern in date_patterns:
            match = re.search(pattern, file_name)
            if match:
                try:
                    if pattern == r'(\d{2})\.(\d{2})\.(\d{4})':
                        day, month, year = match.groups()
                        result = f"{year}{month.zfill(2)}{day.zfill(2)}"
                        logger.debug("Extracted date from file name: %s", result)
                        return result
                    year, month, day = match.groups()
                    result = f"{year}{month.zfill(2)}{day.zfill(2)}"
                    logger.debug("Extracted date from file name: %s", result)
                    return result
                except (ValueError, AttributeError) as e:
                    logger.warning("Failed to parse date from file name: %s", e)

    except (rd.XLRDError, FileNotFoundError, PermissionError, ValueError) as e:
        logger.error("Failed to extract Test Date from Excel: %s, error: %s", filepath, e)

    # 确保总是有返回值
    return "00000000"
