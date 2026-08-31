"""Excel 文件读取与数据处理工具"""

import logging
import os

logger = logging.getLogger(__name__)

# 标准列名关键字——用于识别真正的表头行
_KNOWN_COLUMNS = frozenset(
    {
        "capacity",
        "容量",
        "voltage",
        "电压",
        "current",
        "电流",
        "cycle",
        "循环",
        "temperature",
        "温度",
        "time",
        "时间",
        "step",
        "record",
        "test date",
        "测试日期",
    }
)


def _is_numeric_str(val: str) -> bool:
    """判断字符串是否可解析为数值。"""
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False


def _row_header_score(row) -> float:
    """评估一行作为表头的置信度（0~1）。

    表头行的特征：多个非空单元格、大部分是非纯数值的短文本。
    元数据行的特征：只有 1 个非空单元格、或单元格是长描述/纯数值。
    """
    values = [str(v).strip() for v in row if str(v).strip()]
    if not values:
        return 0.0
    # 非空单元格占总列数的比例
    fill_ratio = len(values) / len(row)
    # 非纯数值的短文本比例（表头通常是短字符串）
    header_like = sum(
        1 for v in values if not _is_numeric_str(v) and len(v) < 40
    )
    text_ratio = header_like / len(values)
    return fill_ratio * 0.4 + text_ratio * 0.6


def detect_header_row(file_path: str, max_scan: int = 10) -> int:
    """探测 Excel 首个工作表的真实表头行号。

    策略：
    1. 优先匹配已知列名关键字（Capacity/Voltage/…）
    2. 若无匹配，跳过元数据行（只有 1 个非空单元格或长描述），
       取第一个"表头得分"最高的行。
    3. 均失败则回退 0。
    """
    import pandas as pd

    try:
        preview = pd.read_excel(
            file_path, sheet_name=0, header=None, nrows=max_scan, engine="calamine"
        )
    except Exception:
        return 0

    # ── 策略 1：已知列名关键字 ──
    for row_idx in range(len(preview)):
        row_values = [str(v).strip().lower() for v in preview.iloc[row_idx]]
        if any(val in _KNOWN_COLUMNS for val in row_values):
            return row_idx

    # ── 策略 2：跳过元数据行，找得分最高的行 ──
    best_idx = 0
    best_score = 0.0
    for row_idx in range(min(max_scan, len(preview))):
        score = _row_header_score(preview.iloc[row_idx])
        if score > best_score:
            best_score = score
            best_idx = row_idx

    # 阈值：至少 60% 的列有非空非数值的短文本，才认为是表头行
    return best_idx if best_score >= 0.6 else 0


def is_metadata_header(columns) -> bool:
    """判断列名是否属于"元数据独占首行"模式。

    典型特征：第 0 列是一个长字符串（设备/测试描述），其余列为 Unnamed。
    """
    if len(columns) < 2:
        return False
    first_col = str(columns[0])
    rest_unnamed = all(str(c).startswith("Unnamed") for c in columns[1:])
    return rest_unnamed and len(first_col) > 30


def read_excel_smart(file_path: str):
    """读取 Excel 首个工作表，自动探测表头行并跳过合并的元数据行。"""
    import pandas as pd

    header_row = detect_header_row(file_path)
    df = pd.read_excel(file_path, sheet_name=0, engine="calamine", header=header_row)
    if header_row > 0:
        logger.info("Skipped %d merged header row(s) in %s", header_row, file_path)
    return optimize_dataframe_memory(df)


def optimize_dataframe_memory(df):
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
    try:
        df = read_excel_smart(file_path)

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
        logger.error("Failed to process Excel file %s: %s", file_path, str(e))
        return {}


def analyze_single_excel(file_path: str, filename: str) -> dict:
    """分析单个 Excel 文件，返回分析摘要

    Args:
        file_path: Excel 文件完整路径
        filename: 文件名

    Returns:
        包含分析结果的字典，失败时 error 键记录错误信息
    """
    try:
        df = read_excel_smart(file_path)

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
