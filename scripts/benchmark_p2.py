"""P2 核心计算基准（可复跑，测向量化后实现）

对照旧实现基线（2026-08-21 main 实测）：
  match_pulse_levels(5 万行, C=10/V=15): 0.1682 s
  charge batch(1 万 pos):                17.4730 s
  charge single x1000:                   0.1390 s
验收目标：10-100 倍提速。

实测（2026-08-21, feat/p2-vectorization）：match_pulse_levels=0.0090s、charge batch=0.0015s、charge single=0.1452s
"""
import time

import numpy as np
import pandas as pd

from battery_analysis.utils.processors.pulse_matcher import match_pulse_levels
from battery_analysis.utils.processors.charge_calculator import ChargeCalculator

N_ROWS = 50000
listCurrentLevel = [500, 1000, 2000, 3000, 4000, 6000, 8000, 12000, 16000, 20000]
listVoltageLevel = [3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 4.4, 4.6, 4.8,
                    5.0, 5.2, 5.4, 5.6, 5.8]
rng = np.random.default_rng(42)

cycle_rows = 25
cycle_count = N_ROWS // cycle_rows
record_cycle = np.repeat(np.arange(1, cycle_count + 1), cycle_rows)

pulse_rows = np.zeros(N_ROWS, dtype=bool)
pulse_rows[::2] = True
cur_levels = np.array(listCurrentLevel)
current = np.zeros(N_ROWS)
current[pulse_rows] = -cur_levels[rng.integers(0, len(cur_levels), pulse_rows.sum())] / 1000.0
voltage = rng.uniform(3.0, 4.5, N_ROWS)
charge = rng.uniform(0, 10, N_ROWS)
record_df = pd.DataFrame({0: record_cycle, 1: np.zeros(N_ROWS), 2: current, 3: voltage, 4: charge})

cycle_df = pd.DataFrame({
    0: np.arange(1, cycle_count + 1),
    1: np.zeros(cycle_count), 2: np.zeros(cycle_count),
    3: rng.uniform(100, 500, cycle_count),
})
step_cycle = np.arange(cycle_count)
step_charge = rng.uniform(1, 20, cycle_count)
step_df = pd.DataFrame({
    0: np.concatenate([[0, 0], step_cycle]),
    1: np.concatenate([["占位", "占位"], ["充电"] * cycle_count]),
    2: np.concatenate([[0.0, 0.0], step_charge]),
})
pulse_mask = pd.Series(pulse_rows)

t0 = time.perf_counter()
matched = match_pulse_levels(
    record_df.iloc[:, 2].to_numpy(dtype=float),
    record_df.iloc[:, 3].to_numpy(dtype=float),
    pulse_mask.to_numpy(dtype=bool),
    listCurrentLevel, listVoltageLevel, start_row=2,
)
t1 = time.perf_counter()
print(f"match_pulse_levels(n={N_ROWS}, C={len(listCurrentLevel)}, V={len(listVoltageLevel)}): {t1 - t0:.4f}s  (old 0.1682s)")

calculator = ChargeCalculator(cycle_df, step_df, record_df)
BATCH_N = 10000
SINGLE_N = 1000
pos_list = list(range(2, 2 + BATCH_N))

t0 = time.perf_counter()
res = calculator.calculate(pos_list, is_single=False)
t1 = time.perf_counter()
print(f"charge batch(n={BATCH_N}): {t1 - t0:.4f}s  (old 17.4730s)")

t0 = time.perf_counter()
for p in pos_list[:SINGLE_N]:
    calculator.calculate(p)
t1 = time.perf_counter()
print(f"charge single x{SINGLE_N}: {t1 - t0:.4f}s  (old 0.1390s)")

print("matched is None:", matched is None)
print("charge batch len:", len(res))
