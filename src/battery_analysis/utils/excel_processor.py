"""Excel 文件读取与数据处理工具"""

import os
import logging

logger = logging.getLogger(__name__)


def optimize_dataframe_memory(df) -> "pd.DataFrame":
    """优化 DataFrame 内存占用

    向下转型数值列，对低基数对象列使用 category 类型。
    """
    import pandas as pd

    for col in df.select_dtypes(include=["int64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")
    for col in df.select_dtypes(include=["object"]).columns:
        if len(df[col].unique()) / len(df[col]) < 0.5:
            df[col] = df[col].astype("category")
    return df


def read_excel_file(file_path: str) -> dict:
    """读取 Excel 文件并返回结构化信息

    Args:
        file_path: Excel 文件路径

    Returns:
        包含文件信息的字典，读取失败时返回空字典
    """
    import pandas as pd

    try:
        df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl", header=0)
        df = optimize_dataframe_memory(df)

        return {
            "filename": os.path.basename(file_path),
            "sheet_name": df.columns.tolist(),
            "row_count": len(df),
            "column_count": len(df.columns),
            "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
            "non_numeric_columns": df.select_dtypes(exclude=["number"]).columns.tolist(),
            "missing_values": df.isnull().sum().to_dict(),
            "basic_stats": df.describe().to_dict(),
        }
    except Exception as e:
        logger.error("处理Excel文件失败 %s: %s", file_path, str(e))
        return {}


def analyze_single_excel(file_path: str, filename: str) -> dict:
    """分析单个 Excel 文件，返回分析摘要

    Args:
        file_path: Excel 文件完整路径
        filename: 文件名

    Returns:
        包含分析结果的字典，失败时 error 键记录错误信息
    """
    import pandas as pd

    try:
        df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl", header=0)
        df = optimize_dataframe_memory(df)

        return {
            "filename": filename,
            "total_records": len(df),
            "columns": df.columns.tolist(),
            "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
            "non_numeric_columns": df.select_dtypes(exclude=["number"]).columns.tolist(),
            "missing_values": df.isnull().sum().to_dict(),
            "basic_stats": df.describe().to_dict(),
        }
    except Exception as e:
        return {"filename": filename, "error": str(e)}
