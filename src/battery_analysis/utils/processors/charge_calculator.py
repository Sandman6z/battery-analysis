"""充电量计算器"""
import logging

import numpy as np
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

        # 预计算 cycle 累积充电量（numpy 数组）
        cycle_charge = pd.to_numeric(cycle_df.iloc[:, 3], errors='coerce').fillna(0).abs()
        self._cycle_cumsum = cycle_charge.cumsum().to_numpy(dtype=float)

        # 列转 numpy 数组，供 searchsorted 批量定位
        self._cycle_cycle_np = pd.to_numeric(self._cycle_cycle, errors='coerce').to_numpy(dtype=float)
        self._record_cycle_np = pd.to_numeric(self._record_cycle, errors='coerce').to_numpy(dtype=float)
        self._record_charge_np = (
            pd.to_numeric(record_df.iloc[:, 4], errors='coerce').fillna(0).abs().to_numpy(dtype=float)
        )
        # searchsorted 子数组：原逻辑从 cycle_idx=2 起扫描，隐含该段升序
        self._cycle_cycle_search = self._cycle_cycle_np[2:]

        # 预计算 step 数据（按 cycle 分组，排除脉冲步骤）
        step_data = step_df.iloc[2:].copy() if len(step_df) > 2 else step_df.iloc[0:0].copy()
        if len(step_data) > 0:
            step_data['_abs_charge'] = pd.to_numeric(step_data.iloc[:, 2], errors='coerce').fillna(0).abs()
            non_pulse = ~step_data.iloc[:, 1].astype(str).str.strip().isin(["脉冲", "Pulse"])
            self._step_charge_by_cycle = step_data[non_pulse].groupby(step_data.iloc[:, 0])['_abs_charge'].sum()
        else:
            self._step_charge_by_cycle = pd.Series(dtype=float)

    def calculate(self, position_idx, is_single=True):
        """计算指定行位置（或批量行位置）的累积充电量"""
        positions = [position_idx] if is_single else list(position_idx)
        if not positions:
            return 0 if is_single else []

        pos_arr = np.asarray(positions, dtype=np.int64)
        valid = (pos_arr >= 2) & (pos_arr < self._record_df_len)
        safe_pos = pos_arr[valid]
        row_cycles = self._record_cycle_np[safe_pos]
        not_nan = ~np.isnan(row_cycles)
        valid_full = np.zeros(len(positions), dtype=bool)
        valid_full[valid] = not_nan

        results = np.zeros(len(positions))
        if valid_full.any():
            good_pos = safe_pos[not_nan]
            cycles = row_cycles[not_nan]
            # 批量定位 cycle 索引（第一个 cycle >= row_cycle，等价原 while 循环）
            idx = np.searchsorted(self._cycle_cycle_search, cycles, side='left') + 2
            # 行为等价 np.where(idx>2, cumsum[idx-1], 0.0)，但惰性求值避免越界：
            # 0/1 行 cycle_df 时 search 子数组为空 → idx 恒 2 → cumsum 恒不取。
            base = np.zeros_like(idx, dtype=float)
            mask = idx > 2
            if mask.any():
                base[mask] = self._cycle_cumsum[idx[mask] - 1]
            step_add = self._step_charge_by_cycle.reindex(cycles).fillna(0.0).to_numpy(dtype=float)
            rec_add = self._record_charge_np[good_pos]
            results[valid_full] = base + step_add + rec_add

        if is_single:
            return int(round(float(results[0])))
        return results.tolist()
