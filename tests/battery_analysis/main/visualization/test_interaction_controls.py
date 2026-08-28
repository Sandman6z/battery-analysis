"""测试 interaction_controls 模块的纯函数逻辑"""

from battery_analysis.main.visualization.interaction_controls import (
    _battery_line_indices,
    _select_hover_lines,
)


class TestBatteryLineIndices:
    """曲线按电池主序构建时，电池->曲线索引映射"""

    def test_single_current_level(self):
        # 1 电流档：线索引 == 电池索引
        assert list(_battery_line_indices(0, 1)) == [0]
        assert list(_battery_line_indices(3, 1)) == [3]

    def test_multi_current_level(self):
        # 3 电池 × 4 电流档：线 = b*4 + c
        assert list(_battery_line_indices(0, 4)) == [0, 1, 2, 3]
        assert list(_battery_line_indices(1, 4)) == [4, 5, 6, 7]
        assert list(_battery_line_indices(2, 4)) == [8, 9, 10, 11]

    def test_edge_battery_index_zero(self):
        assert list(_battery_line_indices(0, 2)) == [0, 1]


class TestSelectHoverLines:
    """悬停曲线集合应反映过滤按钮的 dict 状态"""

    def test_filtered_active(self):
        assert _select_hover_lines({"active": True}, "F", "U") == "F"

    def test_all_data_active(self):
        assert _select_hover_lines({"active": False}, "F", "U") == "U"

    def test_missing_active_key_defaults_to_filtered(self):
        assert _select_hover_lines({"text": "x"}, "F", "U") == "F"

    def test_none_defaults_to_filtered(self):
        assert _select_hover_lines(None, "F", "U") == "F"
