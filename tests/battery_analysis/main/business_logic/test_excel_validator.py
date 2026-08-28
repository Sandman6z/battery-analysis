"""excel_validator 引擎回归锁测试"""

from unittest.mock import patch

import pandas as pd

from battery_analysis.main.business_logic.excel_validator import validate_excel_file
from battery_analysis.utils.processors.excel_processor import optimize_dataframe_memory


class _FakeCache:
    """满足 validate_excel_file 缓存接口的最小内存实现"""

    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def put(self, key, value):
        self._store[key] = value


class TestValidateExcelFileEngine:
    def test_validate_excel_file_uses_calamine_engine(self, sample_xlsx):
        """validate_excel_file 内部必须经 pandas.read_excel 以 engine='calamine' 读取"""
        with patch("pandas.read_excel") as mock_read:
            mock_read.return_value = pd.DataFrame({"Capacity": [1.0, 2.0]})
            is_valid, error_msg, df = validate_excel_file(
                str(sample_xlsx), "DC1,mA2.xlsx", _FakeCache(), optimize_dataframe_memory
            )
        assert mock_read.call_args.kwargs["engine"] == "calamine"
        assert is_valid is True
        assert error_msg == ""
        assert df is not None


def test_pandas_import_is_deferred():
    """excel_validator 顶层不再 import pandas（启动路径延迟导入）"""
    import subprocess
    import sys

    code = (
        "import sys;"
        "from battery_analysis.main.business_logic import excel_validator;"
        "assert 'pandas' not in sys.modules"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
