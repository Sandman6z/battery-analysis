"""charge_calculator searchsorted 契约锁测试"""

import numpy as np
import pandas as pd

from battery_analysis.utils.processors.charge_calculator import ChargeCalculator


def _make_calculator():
    """golden 数据：手算 calculate(2)=17 / calculate(3)=28 / calculate(4)=609

    cycle_df: col0=[1,2,3,4], col3=[100,200,300,400] → cumsum=[100,300,600,1000]
    step_df: 前两行被 iloc[2:] 跳过；剩 cycle2=10 / cycle3=20（非脉冲）
    record_df: col0=[1,2,2,3,4], col4=[0,0,7,8,9]
    """
    cycle_df = pd.DataFrame(
        {
            0: [1, 2, 3, 4],
            1: [0, 0, 0, 0],
            2: [0, 0, 0, 0],
            3: [100.0, 200.0, 300.0, 400.0],
        }
    )
    step_df = pd.DataFrame(
        {
            0: [1, 1, 2, 3],
            1: ["充电", "充电", "充电", "放电"],
            2: [0.0, 0.0, 10.0, 20.0],
        }
    )
    record_df = pd.DataFrame(
        {
            0: [1, 2, 2, 3, 4],
            1: [0, 0, 0, 0, 0],
            2: [0.0, 0.0, 0.5, 0.5, 0.5],
            3: [0.0, 0.0, 3.0, 3.0, 3.0],
            4: [0.0, 0.0, 7.0, 8.0, 9.0],
        }
    )
    return ChargeCalculator(cycle_df, step_df, record_df)


class TestChargeCalculator:
    def test_single_values(self):
        calc = _make_calculator()
        assert calc.calculate(2) == 17  # idx=2 → base=0 + step 10 + rec 7
        assert calc.calculate(3) == 28  # idx=2 → base=0 + step 20 + rec 8
        assert calc.calculate(4) == 609  # idx=3 → base=cumsum[2]=600 + step 0 + rec 9

    def test_batch_equals_single(self):
        calc = _make_calculator()
        batch = calc.calculate([2, 3, 4], is_single=False)
        assert batch == [17.0, 28.0, 609.0]
        # 批量与逐个单值一致
        singles = [float(calc.calculate(p)) for p in [2, 3, 4]]
        assert batch == singles

    def test_invalid_positions_zero(self):
        calc = _make_calculator()
        assert calc.calculate(0) == 0  # pos < 2
        assert calc.calculate(1) == 0
        assert calc.calculate(5) == 0  # pos >= record len
        assert calc.calculate(100) == 0
        assert calc.calculate([0, 1, 5, 100], is_single=False) == [0.0, 0.0, 0.0, 0.0]

    def test_nan_row_cycle_zero(self):
        record_df = pd.DataFrame(
            {
                0: [1.0, 2.0, np.nan],
                1: [0, 0, 0],
                2: [0.0, 0.0, 0.5],
                3: [0.0, 0.0, 3.0],
                4: [0.0, 0.0, 7.0],
            }
        )
        cycle_df = pd.DataFrame({0: [1, 2, 3], 1: [0, 0, 0], 2: [0, 0, 0], 3: [10.0, 20.0, 30.0]})
        step_df = pd.DataFrame({0: [0, 0, 1], 1: ["充电", "充电", "充电"], 2: [0.0, 0.0, 5.0]})
        calc = ChargeCalculator(cycle_df, step_df, record_df)
        assert calc.calculate(1) == 0  # pos < 2
        assert calc.calculate(2) == 0  # pos>=2 但 row_cycle 是 NaN → 0

    def test_degenerate_cycle_df_rows(self):
        """cycle_df 0/1 行：_cycle_cycle_search 空 → idx 恒 2 → base=0（防 cumsum 越界）"""
        cycle_df = pd.DataFrame({0: [1], 1: [0], 2: [0], 3: [100.0]})
        step_df = pd.DataFrame({0: [0, 0, 1], 1: ["充电", "充电", "充电"], 2: [0.0, 0.0, 5.0]})
        record_df = pd.DataFrame(
            {
                0: [1, 1, 1],
                1: [0, 0, 0],
                2: [0.0, 0.0, 0.5],
                3: [0.0, 0.0, 3.0],
                4: [0.0, 0.0, 7.0],
            }
        )
        calc = ChargeCalculator(cycle_df, step_df, record_df)
        assert calc.calculate(2) == 12  # base 0 + step 5 + rec 7（与旧实现一致）
        assert calc.calculate([2], is_single=False) == [12.0]

    def test_cycle_gap_jump_tolerance(self):
        """cycle 跳号：row_cycle=3.5 落在 3 与 4 之间 → 取前一个累积（searchsorted 左边界）"""
        # pylint: disable=protected-access  # 设计需要：monkey-patch 新私有字段
        calc = _make_calculator()
        # 直接替换预计算结构（_cycle_cumsum/_cycle_cycle_search 复用 _make_calculator 的）
        calc._record_cycle_np = np.asarray([1.0, 1.0, 3.5], dtype=float)
        calc._record_charge_np = np.asarray([0.0, 0.0, 9.0], dtype=float)
        calc._record_df_len = 3
        assert calc.calculate(2) == 609  # searchsorted([3,4], 3.5, 'left')=1 → idx=3 → base=600
        # pylint: enable=protected-access
