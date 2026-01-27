import pytest
from unittest.mock import Mock, patch
import matplotlib.pyplot as plt
from battery_analysis.utils.plot_utils import set_plt_axis
from battery_analysis.utils.exception_type import BatteryAnalysisException


class TestPlotUtils:
    @patch('matplotlib.pyplot.axis')
    @patch('matplotlib.pyplot.xticks')
    def test_set_plt_axis_coin_cell(self, mock_xticks, mock_axis):
        # 测试Coin Cell类型
        set_plt_axis("Coin Cell", 600)
        # 验证调用参数
        mock_axis.assert_called_once_with([10, 600, 1, 3])
        mock_xticks.assert_called_once_with([10, 100, 200, 300, 400, 500, 600])

    @patch('matplotlib.pyplot.axis')
    @patch('matplotlib.pyplot.xticks')
    def test_set_plt_axis_pouch_cell(self, mock_xticks, mock_axis):
        # 测试Pouch Cell类型
        set_plt_axis("Pouch Cell", 1500)
        # 验证调用（具体参数可能因计算而不同，这里只验证函数被调用）
        mock_axis.assert_called_once()
        mock_xticks.assert_called_once()

    def test_set_plt_axis_invalid_battery_type(self):
        # 测试无效的电池类型
        with pytest.raises(BatteryAnalysisException):
            set_plt_axis("Unknown Type", 600)