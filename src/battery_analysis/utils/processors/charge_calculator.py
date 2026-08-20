"""充电量计算器"""
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class ChargeCalculator:
    """封装充电量计算逻辑，预计算累积数据以加速后续查询"""

    def __init__(self, cycle_df, step_df, record_df):
        """
        Args:
            cycle_df: 工作表0 (Cycle) 的 DataFrame，已用 pandas 读取
            step_df:  工作表1 (Step)  的 DataFrame，已用 pandas 读取
            record_df: 工作表2 (Record) 的 DataFrame，已用 pandas 读取
        """
        self._cycle_cycle = cycle_df.iloc[:, 0]
        self._record_cycle = record_df.iloc[:, 0]
        self._cycle_df_len = len(cycle_df)
        self._record_df_len = len(record_df)

        # 预计算 cycle 累积充电量
        cycle_charge = pd.to_numeric(cycle_df.iloc[:, 3], errors='coerce').fillna(0).abs()
        self._cycle_cumsum = cycle_charge.cumsum().tolist()

        # 预计算 step 数据（按 cycle 分组，排除脉冲步骤）
        step_data = step_df.iloc[2:].copy() if len(step_df) > 2 else step_df.iloc[0:0].copy()
        if len(step_data) > 0:
            step_data['_abs_charge'] = pd.to_numeric(step_data.iloc[:, 2], errors='coerce').fillna(0).abs()
            non_pulse = ~step_data.iloc[:, 1].astype(str).str.strip().isin(["脉冲", "Pulse"])
            self._step_charge_by_cycle = step_data[non_pulse].groupby(step_data.iloc[:, 0])['_abs_charge'].sum()
        else:
            self._step_charge_by_cycle = pd.Series(dtype=float)

        # 预计算 record 充电量绝对值
        self._record_charge_values = pd.to_numeric(record_df.iloc[:, 4], errors='coerce').fillna(0).abs()

    def calculate(self, position_idx, is_single=True):
        """计算指定行位置的累积充电量"""
        if is_single:
            positions = [position_idx]
            single_result = True
        else:
            positions = position_idx
            single_result = False

        results = [0] * len(positions) if not single_result else [0]

        for i, pos in enumerate(positions):
            if not pos or pos < 2:
                if single_result:
                    return 0
                continue
            if pos >= self._record_df_len:
                if single_result:
                    return 0
                continue

            try:
                row_cycle = self._record_cycle.iloc[pos]
            except IndexError:
                if single_result:
                    return 0
                continue

            if pd.isna(row_cycle):
                if single_result:
                    return 0
                continue

            # 找 cycle 索引（用 < 而非 !=，容错 cycle 跳号）
            cycle_idx = 2
            while cycle_idx < self._cycle_df_len and self._cycle_cycle.iloc[cycle_idx] < row_cycle:
                cycle_idx += 1

            charge = self._cycle_cumsum[cycle_idx - 1] if cycle_idx > 2 else 0

            try:
                charge += self._step_charge_by_cycle.get(row_cycle, 0)
            except (TypeError, KeyError):
                pass

            try:
                charge += abs(self._record_charge_values.iloc[pos])
            except (ValueError, TypeError):
                pass

            if single_result:
                results[0] = round(charge)
            else:
                results[i] = charge

        return results[0] if single_result else results
