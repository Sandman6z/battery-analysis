"""脉冲检测器 (pulse_detector) 测试

测试 pulse_detector.py 中的 is_pulse_step 和 detect_pulse_rows 函数，
覆盖中英文脉冲标记、边界值和非脉冲数据。
"""

import pandas as pd
import pytest

from battery_analysis.utils.processors.pulse_detector import detect_pulse_rows, is_pulse_step


class TestIsPulseStep:
    """is_pulse_step 单值判断测试。"""

    def test_chinese_pulse(self):
        """中文 '脉冲' 应返回 True。"""
        assert is_pulse_step("脉冲") is True

    def test_english_pulse(self):
        """英文 'Pulse' 应返回 True。"""
        assert is_pulse_step("Pulse") is True

    def test_pulse_with_whitespace(self):
        """带前后空格的脉冲标记应返回 True。"""
        assert is_pulse_step("  脉冲  ") is True
        assert is_pulse_step(" Pulse ") is True

    def test_non_pulse_string(self):
        """非脉冲字符串应返回 False。"""
        assert is_pulse_step("Charge") is False
        assert is_pulse_step("Discharge") is False
        assert is_pulse_step("Rest") is False

    def test_numeric_step(self):
        """数值类型的步骤应转为字符串后判断。"""
        assert is_pulse_step(123) is False

    def test_empty_string(self):
        """空字符串应返回 False。"""
        assert is_pulse_step("") is False

    def test_none_value(self):
        """None 应转为字符串 'None'，返回 False。"""
        assert is_pulse_step(None) is False


class TestDetectPulseRows:
    """detect_pulse_rows DataFrame 掩码测试。"""

    def test_detect_chinese_and_english(self):
        """应同时检测中文和英文脉冲行。"""
        df = pd.DataFrame(
            {
                "Cycle": [1, 1, 1, 2],
                "Step": ["脉冲", "Charge", "Pulse", "Rest"],
            }
        )
        mask = detect_pulse_rows(df, step_col=1)
        assert mask.tolist() == [True, False, True, False]

    def test_no_pulse_rows(self):
        """无脉冲行时应返回全 False 掩码。"""
        df = pd.DataFrame(
            {
                "Cycle": [1, 2, 3],
                "Step": ["Charge", "Discharge", "Rest"],
            }
        )
        mask = detect_pulse_rows(df, step_col=1)
        assert mask.sum() == 0

    def test_all_pulse_rows(self):
        """所有行都是脉冲时应返回全 True 掩码。"""
        df = pd.DataFrame(
            {
                "Cycle": [1, 2],
                "Step": ["脉冲", "Pulse"],
            }
        )
        mask = detect_pulse_rows(df, step_col=1)
        assert mask.all()

    def test_custom_step_column(self):
        """应支持自定义 step_col 索引。"""
        df = pd.DataFrame(
            {
                "A": ["脉冲", "Charge"],
                "B": ["Charge", "脉冲"],
            }
        )
        mask_b = detect_pulse_rows(df, step_col=1)
        assert mask_b.tolist() == [False, True]

    def test_whitespace_handling(self):
        """步骤值中的前后空格应被正确处理。"""
        df = pd.DataFrame(
            {
                "Cycle": [1, 2, 3],
                "Step": ["  脉冲 ", " Pulse  ", "Charge"],
            }
        )
        mask = detect_pulse_rows(df, step_col=1)
        assert mask.tolist() == [True, True, False]

    def test_empty_dataframe(self):
        """空 DataFrame 应返回空 Series。"""
        df = pd.DataFrame({"Cycle": [], "Step": []})
        mask = detect_pulse_rows(df, step_col=1)
        assert len(mask) == 0
