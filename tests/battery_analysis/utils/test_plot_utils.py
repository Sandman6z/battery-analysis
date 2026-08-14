import pytest
from unittest.mock import Mock, patch
import matplotlib.pyplot as plt
from battery_analysis.utils.writers.plot_utils import set_plt_axis
from battery_analysis.utils.exceptions import BatteryAnalysisException


class TestPlotUtils:
    @patch('matplotlib.pyplot.axis')
    @patch('matplotlib.pyplot.xticks')
    def test_set_plt_axis_coin_cell(self, mock_xticks, mock_axis):
        # 测试Coin Cell类型（max_xaxis=600 → 动态计算）
        set_plt_axis("Coin Cell", 600)
        mock_axis.assert_called_once_with([18, 600, 1, 3])
        mock_xticks.assert_called_once_with([18, 100, 200, 300, 400, 500, 600])

    @patch('matplotlib.pyplot.axis')
    @patch('matplotlib.pyplot.xticks')
    def test_set_plt_axis_pouch_cell(self, mock_xticks, mock_axis):
        # 测试Pouch Cell类型（所有类型统一走动态计算）
        set_plt_axis("Pouch Cell", 1500)
        mock_axis.assert_called_once_with([45, 1500, 1, 3])
        mock_xticks.assert_called_once_with([45, 200, 400, 600, 800, 1000, 1200, 1400, 1600])

    @patch('matplotlib.pyplot.axis')
    @patch('matplotlib.pyplot.xticks')
    def test_set_plt_axis_unknown_type(self, mock_xticks, mock_axis):
        # 未知电池类型不再抛出异常，统一走动态计算
        set_plt_axis("Unknown Type", 600)
        mock_axis.assert_called_once()
        mock_xticks.assert_called_once()