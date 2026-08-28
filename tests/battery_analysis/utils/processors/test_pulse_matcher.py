"""pulse_matcher 向量化契约锁测试

注意：放电电流记录为负值（如 -0.5A = -500mA），
原实现用 neg_current_levels = [-level] 与之比较。
"""

import numpy as np

from battery_analysis.utils.processors.pulse_matcher import match_pulse_levels


def _toy_data():
    """行2:-0.5A, 行3:-0.5A(endpoint), 行4:-0.4A(无匹配), 行5:-1.0A(endpoint)"""
    record_current = [0.0, 0.0, -0.5, -0.5, -0.4, -1.0]
    record_voltage = [0.0, 0.0, 3.2, 2.9, 3.1, 3.5]
    pulse_mask = [False, False, True, True, True, True]
    return record_current, record_voltage, pulse_mask


class TestMatchPulseLevels:
    def test_basic_match(self):
        result = match_pulse_levels(*_toy_data(), [500, 1000], [3.0, 4.0], start_row=2)
        assert result is not None
        listLevelToVoltage, listLevelToRow, listPosi, listVoltage = result

        assert listLevelToVoltage == [[2.9, 3.2], [3.0, 3.5]]
        assert listLevelToRow == [[3, 2], [0, 5]]
        assert listPosi == [[3], [5]]
        assert listVoltage == [[2.9], [3.5]]

    def test_no_pulse_returns_none(self):
        assert match_pulse_levels([-0.5] * 4, [3.0] * 4, [False] * 4, [500], [3.0]) is None

    def test_last_row_endpoint(self):
        """末尾行是端点（row+1 >= data_len）"""
        result = match_pulse_levels(
            [0.0, 0.0, -0.5],
            [0.0, 0.0, 3.0],
            [False, False, True],
            [500],
            [3.0],
            start_row=2,
        )
        assert result is not None
        _, _, listPosi, _ = result
        assert listPosi == [[2]]

    def test_mid_sequence_not_endpoint(self):
        """连续匹配段中间行不是端点"""
        result = match_pulse_levels(
            [0.0, 0.0, -0.5, -0.5, -0.5],
            [0.0, 0.0, 3.0, 3.1, 3.2],
            [False, False, True, True, True],
            [500],
            [3.0],
            start_row=2,
        )
        _, _, listPosi, _ = result
        assert listPosi == [[4]]

    def test_same_row_matches_multiple_current_levels(self):
        """同一点可在多档 ±5% 重叠时匹配多个等级（原逻辑无 break，须保持）"""
        # 500 与 505 的 ±5% 范围重叠，电流 -0.503A=-503mA 同时落入两档
        # 电压 2.9 同时 <= 3.0 与 4.0，故两个电压档都记录到行 2
        result = match_pulse_levels(
            [0.0, 0.0, -0.503],
            [0.0, 0.0, 2.9],
            [False, False, True],
            [500, 505],
            [3.0, 4.0],
            start_row=2,
        )
        assert result is not None
        listLevelToVoltage, listLevelToRow, listPosi, listVoltage = result
        assert listLevelToVoltage == [[2.9, 2.9], [2.9, 2.9]]
        assert listLevelToRow == [[2, 2], [2, 2]]
        assert listPosi == [[2], [2]]
        assert listVoltage == [[2.9], [2.9]]

    def test_short_pulse_mask_skips_tail(self):
        """pulse_mask 短于 record：尾部越界行跳过（原 row >= len(pulse_mask) 保护）"""
        result = match_pulse_levels(
            [0.0, 0.0, -0.5, -0.5],
            [0.0, 0.0, 3.0, 3.1],
            [False, True],
            [500],
            [3.0],
            start_row=2,
        )
        assert result is None  # 行 2、3 均 >= len(pulse_mask)=2 被跳过

    def test_accepts_numpy_arrays(self):
        """battery_analysis 将传 to_numpy() 数组，须兼容（ndarray 结果须与 list 输入逐项一致）"""
        rc, rv, pm = _toy_data()
        list_result = match_pulse_levels(rc, rv, pm, [500, 1000], [3.0, 4.0], start_row=2)
        np_result = match_pulse_levels(
            np.asarray(rc),
            np.asarray(rv),
            np.asarray(pm),
            [500, 1000],
            [3.0, 4.0],
            start_row=2,
        )
        assert np_result is not None
        assert np_result == list_result

    def test_bts_header_rows_with_strings_are_skipped(self):
        """回归：真实 BTS 导出头部行含非数值单元格（行0 测试名、行1 '电流(A)'/'电压(V)' 列名）
        不得触发 'could not convert string to float'；行索引须含头部偏移。

        数据行与 _toy_data() 完全一致（行2-7），故匹配结果同 test_basic_match，
        但 listLevelToRow / listPosi 的行号整体 +2（头部两行偏移）。
        """
        record_current = [None, "电流(A)", 0.0, 0.0, -0.5, -0.5, -0.4, -1.0]
        record_voltage = [None, "电压(V)", 0.0, 0.0, 3.2, 2.9, 3.1, 3.5]
        pulse_mask = [False, False, False, False, True, True, True, True]

        result = match_pulse_levels(
            record_current,
            record_voltage,
            pulse_mask,
            [500, 1000],
            [3.0, 4.0],
            start_row=2,
        )
        assert result is not None
        listLevelToVoltage, listLevelToRow, listPosi, listVoltage = result
        assert listLevelToVoltage == [[2.9, 3.2], [3.0, 3.5]]
        assert listLevelToRow == [[5, 4], [0, 7]]
        assert listPosi == [[5], [7]]
        assert listVoltage == [[2.9], [3.5]]
