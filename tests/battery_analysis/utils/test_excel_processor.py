"""测试 Excel 处理器模块"""

import os
import tempfile
import pandas as pd
from battery_analysis.utils.processors.excel_processor import (
    optimize_dataframe_memory,
    read_excel_file,
    analyze_single_excel,
)


class TestOptimizeDataframeMemory:
    def test_downcast_int64(self):
        df = pd.DataFrame({"col": [1, 2, 3]})
        df["col"] = df["col"].astype("int64")
        result = optimize_dataframe_memory(df)
        assert result["col"].dtype in ("int8", "int16", "int32")

    def test_downcast_float64(self):
        df = pd.DataFrame({"col": [1.0, 2.0, 3.0]})
        df["col"] = df["col"].astype("float64")
        result = optimize_dataframe_memory(df)
        assert result["col"].dtype in ("float32",)

    def test_category_low_cardinality(self):
        """2 unique / 5 rows = 0.4 < 0.5 → 转为 category"""
        df = pd.DataFrame({"col": ["a", "a", "a", "a", "b"]})
        result = optimize_dataframe_memory(df)
        assert result["col"].dtype.name == "category"


class TestReadExcelFile:
    def test_success(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            df = pd.DataFrame({"Voltage": [3.7, 3.6], "Capacity": [1000, 950]})
            df.to_excel(path, index=False)

            result = read_excel_file(path)
            assert result["filename"] == os.path.basename(path)
            assert result["row_count"] == 2
            assert result["column_count"] == 2
            assert "Voltage" in result["numeric_columns"]
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_file_not_found(self):
        result = read_excel_file("nonexistent.xlsx")
        assert result == {}


class TestAnalyzeSingleExcel:
    def test_success(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            df = pd.DataFrame({"A": [1, 2, 3], "B": [4.0, 5.0, 6.0]})
            df.to_excel(path, index=False)

            result = analyze_single_excel(path, "test.xlsx")
            assert result["filename"] == "test.xlsx"
            assert result["total_records"] == 3
            assert "error" not in result
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_file_not_found(self):
        result = analyze_single_excel("nonexistent.xlsx", "test.xlsx")
        assert result["filename"] == "test.xlsx"
        assert "error" in result
