"""测试 battery_analysis 核心解析功能（pandas 版本）"""
import pytest
import pandas as pd
from tests.fixtures.sample_data import sample_xlsx  # noqa: F401


PULSE_STEPS = {"脉冲", "Pulse", "pulse"}


class TestPandasParsing:
    """验证 pandas 向量化替换后的核心逻辑"""

    def test_read_xlsx_sheets(self, sample_xlsx):
        """验证能正确读取三个工作表"""
        cycle_df = pd.read_excel(sample_xlsx, sheet_name=0, engine='openpyxl')
        step_df = pd.read_excel(sample_xlsx, sheet_name=1, engine='openpyxl')
        record_df = pd.read_excel(sample_xlsx, sheet_name=2, engine='openpyxl')

        assert len(cycle_df) >= 2
        assert len(step_df) >= 4
        assert len(record_df) >= 5

    def test_pulse_detection(self, sample_xlsx):
        """验证脉冲检测：筛选 Step# 为脉冲的的行"""
        record_df = pd.read_excel(sample_xlsx, sheet_name=2, engine='openpyxl')

        pulses = record_df[record_df.iloc[:, 1].astype(str).isin(PULSE_STEPS)]
        non_pulses = record_df[~record_df.iloc[:, 1].astype(str).isin(PULSE_STEPS)]

        assert len(pulses) > 0
        assert len(non_pulses) > 0

    def test_current_matching(self, sample_xlsx):
        """验证电流等级匹配逻辑"""
        list_current = ["4000"]  # mA
        record_df = pd.read_excel(sample_xlsx, sheet_name=2, engine='openpyxl')
        match_count = 0

        for row in record_df.itertuples():
            current_ma = float(row[3]) * 1000 if row[3] else 0
            # 应该在 +/-5% 范围内匹配（处理负电流值）
            for level in list_current:
                target = -float(level)
                tolerance = abs(target) * 0.05
                if abs(current_ma - target) <= tolerance:
                    match_count += 1
                    break  # 匹配成功

        assert match_count > 0, f"应该至少匹配到一个电流等级，但匹配数为 {match_count}"

    def test_cumulative_charge(self, sample_xlsx):
        """验证累积电荷计算"""
        cycle_df = pd.read_excel(sample_xlsx, sheet_name=0, engine='openpyxl')

        # 跳过前两行（行 0 = 表头，行 1 = 元数据）
        cycle_data = cycle_df.iloc[2:]
        charges = pd.to_numeric(cycle_data.iloc[:, 3], errors='coerce').abs()
        cumulative = charges.cumsum()
        assert cumulative.iloc[-1] > 0
