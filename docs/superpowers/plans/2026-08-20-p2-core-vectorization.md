# P2 核心算法向量化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 大数据量下核心计算（脉冲匹配、电荷量计算、统计量）提速 10-100 倍，并消除 `ProcessPoolExecutor` 假并行。

**Architecture:** 保持所有公开 API 签名与返回结构**完全不变**（下游 writer/调用方是硬契约），仅把内部三重嵌套循环 / while 线性扫描 / 逐 cell Python 统计替换为 numpy 广播 / `np.searchsorted` 批量定位 / pad+`np.nan*` 批量归约。用 TDD 契约锁锁定新旧行为一致，最后用提交入库的可复跑基准脚本做前后对比验收。

**Tech Stack:** numpy（向量化核心）、pandas（DataFrame 保持，仅取列转 numpy）、concurrent.futures（假并行修复）。

**旧实现基线（2026-08-21 08:40 在 main 上实测，Task 6 对比验收用）：**

| 场景 | 旧耗时 |
|---|---|
| `match_pulse_levels`（5 万行 record，C=10/V=15） | **0.1682 s** |
| `ChargeCalculator.calculate` 批量（1 万 pos） | **17.4730 s** |
| `ChargeCalculator.calculate` 单值 ×1000 | 0.1390 s |

---

## File Structure

| 文件 | 动作 | 职责 |
|---|---|---|
| `src/battery_analysis/utils/processors/pulse_matcher.py` | 修改 | 向量化 `match_pulse_levels`（广播比较） |
| `src/battery_analysis/utils/processors/charge_calculator.py` | 修改 | `np.searchsorted` 批量定位 + numpy 预计算 |
| `src/battery_analysis/utils/writers/statistics_utils.py` | 修改 | pad+`np.nan*` 2D 批量统计 |
| `src/battery_analysis/utils/processors/battery_analysis.py` | 修改 | `match_pulse_levels` 传 numpy 数组（去 `.tolist()` 降级） |
| `src/battery_analysis/main/business_logic/data_processor.py` | 修改 | 假并行修复（模块级 worker） |
| `tests/battery_analysis/utils/processors/test_pulse_matcher.py` | 新建 | pulse_matcher 契约锁 |
| `tests/battery_analysis/utils/processors/test_charge_calculator.py` | 新建 | charge_calculator 契约锁 |
| `tests/battery_analysis/utils/writers/test_statistics_utils.py` | 新建 | statistics_utils 契约锁 |
| `tests/battery_analysis/main/business_logic/test_data_processor.py` | 修改 | 假并行修复测试 |
| `scripts/benchmark_p2.py` | 新建 | 可复跑 P2 基准（提交入库） |

**硬契约（改返回结构即破坏，绝不触碰）：**
- `match_pulse_levels` 返回 `(listLevelToVoltage, listLevelToRow, listPosiForInfoImageCsv, listVoltageForInfoImageCsv)` 或 `None`。元素类型：listLevelToVoltage 为 float、listLevelToRow 为 int、两个 CSV 列表为 int/float。`listLevelToVoltage[c][v]` 未匹配时保留 `listVoltageLevel[v]` 初值。
- `ChargeCalculator.calculate`：单值返回 `round(charge)`（int），批量返回不 round 的列表；无效 pos（<2 / ≥len / NaN cycle）返回 0。
- `compute_list_cpt` 返回 `listCpt[c][v]`（非零收集）；`compute_statistics` 返回 dict（'mean'/'med'/'std'/'mm3s'/'mm2s'/'mp2s'/'mp3s'/'min'/'max'，每个为 list-of-list）。`excel_report_writer` 的 `_compute_list_cpt`/`_compute_statistics` 别名 identity 测试锁定这些函数对象本身。

---

### Task 1: pulse_matcher 广播向量化

**Files:**
- Modify: `src/battery_analysis/utils/processors/pulse_matcher.py`
- Test: `tests/battery_analysis/utils/processors/test_pulse_matcher.py`（新建）

**语义还原要点（向量化必须与原实现逐行为一致）：**
1. 外层行循环内 `for c_idx` **无 break**：同一行可同时匹配多个电流等级，每个匹配的 c_idx 都做 endpoint + 电压匹配。→ 向量化对各 c_idx 独立处理 `matched_row`。
2. endpoint = 当前行匹配该等级 **且** 下一行 `record_current` 不在该等级 ±5% 内（末尾行视为 endpoint；`in_range` 基于全数组，不看 pulse_mask）。
3. 电压匹配 = 每个 `(c, v)` 按行序**第一个** `voltage <= v_level` 的匹配行（`listLevelToRow==0` 保护确保只取首个）→ `np.argmax`。
4. `b_is_in_range(cur, neg) = abs(cur - neg) <= abs(neg * 0.05)`。
5. `pulse_mask` 可能比 record 短（原 `row >= len(pulse_mask)` 保护尾部行跳过）。

- [ ] **Step 1: 写契约锁测试**

```python
"""pulse_matcher 向量化契约锁测试"""
import numpy as np

from battery_analysis.utils.processors.pulse_matcher import match_pulse_levels


def _toy_data():
    """行2:0.5A, 行3:0.5A(endpoint), 行4:0.4A(无匹配), 行5:1.0A(endpoint)"""
    record_current = [0.0, 0.0, 0.5, 0.5, 0.4, 1.0]
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
        assert match_pulse_levels([0.5] * 4, [3.0] * 4, [False] * 4, [500], [3.0]) is None

    def test_last_row_endpoint(self):
        """末尾行是端点（row+1 >= data_len）"""
        result = match_pulse_levels(
            [0.0, 0.0, 0.5], [0.0, 0.0, 3.0], [False, False, True],
            [500], [3.0], start_row=2,
        )
        assert result is not None
        _, _, listPosi, _ = result
        assert listPosi == [[2]]

    def test_mid_sequence_not_endpoint(self):
        """连续匹配段中间行不是端点"""
        result = match_pulse_levels(
            [0.0, 0.0, 0.5, 0.5, 0.5], [0.0, 0.0, 3.0, 3.1, 3.2],
            [False, False, True, True, True], [500], [3.0], start_row=2,
        )
        _, _, listPosi, _ = result
        assert listPosi == [[4]]

    def test_same_row_matches_multiple_current_levels(self):
        """同一点可在多档 ±5% 重叠时匹配多个等级（原逻辑无 break，须保持）"""
        # 500 与 505 的 ±5% 范围重叠，电流 0.503A=503mA 同时落入两档
        result = match_pulse_levels(
            [0.0, 0.0, 0.503], [0.0, 0.0, 3.3], [False, False, True],
            [500, 505], [3.0, 4.0], start_row=2,
        )
        assert result is not None
        _, listLevelToRow, listPosi, _ = result
        assert listLevelToRow == [[2, 2], [2, 2]]
        assert listPosi == [[2], [2]]

    def test_accepts_numpy_arrays(self):
        """battery_analysis 将传 to_numpy() 数组，须兼容"""
        rc, rv, pm = _toy_data()
        result = match_pulse_levels(
            np.asarray(rc), np.asarray(rv), np.asarray(pm),
            [500, 1000], [3.0, 4.0], start_row=2,
        )
        assert result is not None
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run pytest tests/battery_analysis/utils/processors/test_pulse_matcher.py -v`
Expected: `test_same_row_matches_multiple_current_levels` FAIL（旧实现 `assert listPosi == [[2], [2]]` 对 503mA 只匹配第一档 500——因为旧实现第 4 档才迭代到 505；实际旧实现 503 在 500±25=[475,525] 和 505±25.25=[479.75,530.25] 都命中，两个 c_idx 都处理，listPosi 两个都有 [2]。若旧实现通过，则该测试作为契约锁保留）——**以实测为准**：本测试锁定"无 break"语义，若旧实现已符合则视为回归锁。

- [ ] **Step 3: 向量化实现**

```python
"""脉冲电流/电压等级匹配逻辑"""
from typing import List, Optional, Tuple

import numpy as np


def b_is_in_range(current: float, standard: float) -> bool:
    """检查电流是否在标准值的 ±5% 范围内"""
    return abs(current - standard) <= abs(standard * 0.05)


def _init_level_structures(
    listCurrentLevel: list,
    listVoltageLevel: list,
) -> Tuple[list, list, list, list, list]:
    """初始化等级匹配所需的嵌套列表结构"""
    listLevelToVoltage = []
    listLevelToRow = []
    listLevelToCharge = []
    listPosiForInfoImageCsv = []
    listVoltageForInfoImageCsv = []

    for c_idx in range(len(listCurrentLevel)):
        listLevelToVoltage.append([])
        listLevelToRow.append([])
        listLevelToCharge.append([])
        listPosiForInfoImageCsv.append([])
        listVoltageForInfoImageCsv.append([])
        for v_idx in range(len(listVoltageLevel)):
            listLevelToVoltage[c_idx].append(listVoltageLevel[v_idx])
            listLevelToRow[c_idx].append(0)
            listLevelToCharge[c_idx].append(0)

    return (
        listLevelToVoltage,
        listLevelToRow,
        listLevelToCharge,
        listPosiForInfoImageCsv,
        listVoltageForInfoImageCsv,
    )


def match_pulse_levels(
    record_current: List[float],
    record_voltage: List[float],
    pulse_mask: List[bool],
    listCurrentLevel: list,
    listVoltageLevel: list,
    start_row: int = 2,
) -> Optional[Tuple[list, list, list, list]]:
    """将脉冲行匹配到电流/电压等级（numpy 广播向量化）

    对每个电流等级一次性广播比较整个电流数组，替代逐行三重嵌套循环。
    返回结构与原实现完全一致：(listLevelToVoltage, listLevelToRow,
    listPosiForInfoImageCsv, listVoltageForInfoImageCsv)；无脉冲数据返回 None。
    """
    structures = _init_level_structures(listCurrentLevel, listVoltageLevel)
    listLevelToVoltage, listLevelToRow, _, listPosiForInfoImageCsv, listVoltageForInfoImageCsv = structures

    cur_ma = np.asarray(record_current, dtype=float) * 1000.0
    voltage = np.asarray(record_voltage, dtype=float)
    data_len = len(cur_ma)
    if data_len == 0:
        return None

    # pulse_mask 可能与 record 不等长（原代码 row >= len(pulse_mask) 保护尾部）
    mask = np.zeros(data_len, dtype=bool)
    pm = np.asarray(pulse_mask, dtype=bool)
    common = min(data_len, pm.size)
    mask[:common] = pm[:common]

    valid_row = np.zeros(data_len, dtype=bool)
    valid_row[max(start_row, 0):] = True
    valid_row &= mask

    if not valid_row.any():
        return None

    neg_levels = [-float(level) for level in listCurrentLevel]
    voltage_levels = [float(v) for v in listVoltageLevel]

    for c_idx, neg_level in enumerate(neg_levels):
        tolerance = abs(neg_level * 0.05)
        in_range = np.abs(cur_ma - neg_level) <= tolerance
        matched_row = valid_row & in_range

        # ── 脉冲结束点：当前行匹配、下一行不在范围内（末尾行视为端点）──
        next_in_range = np.empty(data_len, dtype=bool)
        next_in_range[:-1] = in_range[1:]
        next_in_range[-1] = False
        is_endpoint = matched_row & ~next_in_range
        endpoint_rows = np.nonzero(is_endpoint)[0]
        if endpoint_rows.size > 0:
            listPosiForInfoImageCsv[c_idx].extend(int(r) for r in endpoint_rows)
            listVoltageForInfoImageCsv[c_idx].extend(float(voltage[r]) for r in endpoint_rows)

        # ── 电压等级匹配：每 (c,v) 首个满足 voltage <= v_level 的匹配行 ──
        for v_idx, v_level in enumerate(voltage_levels):
            satisfies = matched_row & (voltage <= v_level)
            if satisfies.any():
                first_idx = int(np.argmax(satisfies))
                listLevelToVoltage[c_idx][v_idx] = float(voltage[first_idx])
                listLevelToRow[c_idx][v_idx] = first_idx

    return (
        listLevelToVoltage,
        listLevelToRow,
        listPosiForInfoImageCsv,
        listVoltageForInfoImageCsv,
    )
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run pytest tests/battery_analysis/utils/processors/test_pulse_matcher.py -v`
Expected: PASS（6 tests）。若 `test_same_row_matches_multiple_current_levels` 实现与旧行为不符，以旧实现为准调整测试断言（先 `git stash` 切 main 用临时脚本验证旧实现该场景的输出）。

- [ ] **Step 5: 跑全量回归 + commit**

Run: `uv run pytest -q` → Expected: 全部通过（529 + 6 新增，无失败）
Commit:
```bash
git add src/battery_analysis/utils/processors/pulse_matcher.py tests/battery_analysis/utils/processors/test_pulse_matcher.py
git commit -m "perf(p2): pulse_matcher 三重循环改 numpy 广播向量化

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: charge_calculator np.searchsorted 批量定位

**Files:**
- Modify: `src/battery_analysis/utils/processors/charge_calculator.py`
- Test: `tests/battery_analysis/utils/processors/test_charge_calculator.py`（新建）

**语义还原要点：**
- `cycle_idx` 从 2 起扫，找第一个 `cycle_cycle.iloc[cycle_idx] >= row_cycle` → `searchsorted(_cycle_cycle_np[2:], row_cycle, 'left') + 2`（全小于时返回子数组长度，+2=cycle_df_len，取 `cumsum[len-1]`，与 while 跑到 len 一致）。
- `charge = cumsum[cycle_idx-1] if cycle_idx > 2 else 0`（**保持 `>2` 原语义**）。
- 单值 `round(charge)` 返回 int；批量不 round。无效 pos（<2 / ≥len / NaN row_cycle）→ 0。
- step 批量取用 `.reindex(cycles).fillna(0.0)`。

- [ ] **Step 1: 写契约锁测试**

```python
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
    cycle_df = pd.DataFrame({
        0: [1, 2, 3, 4],
        1: [0, 0, 0, 0],
        2: [0, 0, 0, 0],
        3: [100.0, 200.0, 300.0, 400.0],
    })
    step_df = pd.DataFrame({
        0: [1, 1, 2, 3],
        1: ["充电", "充电", "充电", "放电"],
        2: [0.0, 0.0, 10.0, 20.0],
    })
    record_df = pd.DataFrame({
        0: [1, 2, 2, 3, 4],
        1: [0, 0, 0, 0, 0],
        2: [0.0, 0.0, 0.5, 0.5, 0.5],
        3: [0.0, 0.0, 3.0, 3.0, 3.0],
        4: [0.0, 0.0, 7.0, 8.0, 9.0],
    })
    return ChargeCalculator(cycle_df, step_df, record_df)


class TestChargeCalculator:
    def test_single_values(self):
        calc = _make_calculator()
        assert calc.calculate(2) == 17     # idx=2 → base=0 + step 10 + rec 7
        assert calc.calculate(3) == 28     # idx=2 → base=0 + step 20 + rec 8
        assert calc.calculate(4) == 609    # idx=3 → base=cumsum[2]=600 + step 0 + rec 9

    def test_batch_equals_single(self):
        calc = _make_calculator()
        batch = calc.calculate([2, 3, 4], is_single=False)
        assert batch == [17.0, 28.0, 609.0]
        # 批量与逐个单值一致
        singles = [float(calc.calculate(p)) for p in [2, 3, 4]]
        assert batch == singles

    def test_invalid_positions_zero(self):
        calc = _make_calculator()
        assert calc.calculate(0) == 0      # pos < 2
        assert calc.calculate(1) == 0
        assert calc.calculate(5) == 0      # pos >= record len
        assert calc.calculate(100) == 0
        assert calc.calculate([0, 1, 5, 100], is_single=False) == [0.0, 0.0, 0.0, 0.0]

    def test_nan_row_cycle_zero(self):
        record_df = pd.DataFrame({
            0: [1.0, 2.0, np.nan], 1: [0, 0, 0], 2: [0.0, 0.0, 0.5],
            3: [0.0, 0.0, 3.0], 4: [0.0, 0.0, 7.0],
        })
        cycle_df = pd.DataFrame({0: [1, 2, 3], 1: [0, 0, 0], 2: [0, 0, 0], 3: [10.0, 20.0, 30.0]})
        step_df = pd.DataFrame({0: [0, 0, 1], 1: ["充电", "充电", "充电"], 2: [0.0, 0.0, 5.0]})
        calc = ChargeCalculator(cycle_df, step_df, record_df)
        assert calc.calculate(1) == 0      # pos < 2
        assert calc.calculate(2) == 0      # pos>=2 但 row_cycle 是 NaN → 0

    def test_cycle_gap_jump_tolerance(self):
        """cycle 跳号：row_cycle=3.5 落在 3 与 4 之间 → 取前一个累积（searchsorted 左边界）"""
        calc = _make_calculator()
        # 直接替换预计算结构（_cycle_cumsum/_cycle_cycle_search 复用 _make_calculator 的）
        calc._record_cycle_np = np.asarray([1.0, 1.0, 3.5], dtype=float)
        calc._record_charge_np = np.asarray([0.0, 0.0, 9.0], dtype=float)
        calc._record_df_len = 3
        assert calc.calculate(2) == 609    # searchsorted([3,4], 3.5, 'left')=1 → idx=3 → base=600
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run pytest tests/battery_analysis/utils/processors/test_charge_calculator.py -v`
Expected: FAIL（新测试文件里的 `test_single_values` 若旧实现结果与 golden 不符，先核对手算——以旧实现为准；golden 手算依据原始代码逻辑推演，若旧实现不同说明原始逻辑与推演有出入，调整测试到旧实现输出，**这是 TDD 契约锁，锁定的是"新实现 == 旧实现"**）

- [ ] **Step 3: searchsorted 实现**

```python
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
            base = np.where(idx > 2, self._cycle_cumsum[idx - 1], 0.0)
            step_add = self._step_charge_by_cycle.reindex(cycles).fillna(0.0).to_numpy(dtype=float)
            rec_add = self._record_charge_np[good_pos]
            results[valid_full] = base + step_add + rec_add

        if is_single:
            return int(round(float(results[0])))
        return results.tolist()
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run pytest tests/battery_analysis/utils/processors/test_charge_calculator.py -v`
Expected: PASS（5 tests）。若 `step_add` reindex 对 int index vs float key 不匹配，将 `cycles` 转为 `_step_charge_by_cycle.index.dtype` 后 reindex。

- [ ] **Step 5: 全量回归 + commit**

Run: `uv run pytest -q` → 全部通过
Commit:
```bash
git add src/battery_analysis/utils/processors/charge_calculator.py tests/battery_analysis/utils/processors/test_charge_calculator.py
git commit -m "perf(p2): charge_calculator while 线性扫描改 np.searchsorted 批量定位

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: statistics_utils 2D numpy 批量统计

**Files:**
- Modify: `src/battery_analysis/utils/writers/statistics_utils.py`
- Test: `tests/battery_analysis/utils/writers/test_statistics_utils.py`（新建）

**语义还原要点：**
- `compute_list_cpt` 用 `np.asarray(listBatteryCharge, dtype=object)`（object 保持 `None != 0` 等 Python 比较语义）逐等级批量取非零；行不等长时回退原始逐元素循环。
- `compute_statistics` 两层循环收集 flat_cells → pad+NaN → `np.nan*` axis=1 批量 → counts 掩码对齐 `numeric_utils` 语义（空→0.0；样本≤1 的 std→0.0）。
- **返回 dict 结构与 4 个 writer 消费方式完全不变。**

- [ ] **Step 1: 写契约锁测试**

```python
"""statistics_utils 2D 批量统计契约锁测试"""
import numpy as np
import pytest

from battery_analysis.utils.writers.statistics_utils import (
    compute_list_cpt,
    compute_statistics,
)


def _sample_data():
    """B=3, C=2, V=2，等级平铺为 [c0v0, c0v1, c1v0, c1v1]"""
    return [
        [100, 0, 200, 50],   # 电池0（c0v1=0 被排除）
        [110, 90, 0, 60],    # 电池1（c1v0=0 被排除）
        [120, 95, 210, 0],   # 电池2（c1v1=0 被排除）
    ], 3, 2, 2


class TestComputeListCpt:
    def test_structure_and_collect(self):
        data, b, c, v = _sample_data()
        result = compute_list_cpt(data, b, c, v)
        assert result[0][0] == [100, 110, 120]
        assert result[0][1] == [90, 95]
        assert result[1][0] == [200, 210]
        assert result[1][1] == [50, 60]
        # 结构：len == V，每行 len == C
        assert len(result) == c and all(len(row) == v for row in result)


class TestComputeStatistics:
    def test_known_values(self):
        data, b, c, v = _sample_data()
        list_cpt = compute_list_cpt(data, b, c, v)
        stats = compute_statistics(list_cpt, c, v)

        assert stats['mean'][0][0] == pytest.approx(110.0)
        assert stats['med'][0][0] == pytest.approx(110.0)
        assert stats['std'][0][0] == pytest.approx(10.0)
        assert stats['min'][0][0] == pytest.approx(100.0)
        assert stats['max'][0][0] == pytest.approx(120.0)

        assert stats['mean'][0][1] == pytest.approx(92.5)
        assert stats['std'][0][1] == pytest.approx(np.std([90, 95], ddof=1))

        assert stats['mean'][1][0] == pytest.approx(205.0)
        assert stats['mean'][1][1] == pytest.approx(55.0)

        # 派生 ±Nσ
        assert stats['mp2s'][0][0] == pytest.approx(110.0 + 2 * 10.0)
        assert stats['mm3s'][0][0] == pytest.approx(110.0 - 3 * 10.0)

    def test_empty_cells_zero(self):
        list_cpt = [[[], []], [[], []]]
        stats = compute_statistics(list_cpt, 2, 2)
        assert stats['mean'] == [[0.0, 0.0], [0.0, 0.0]]
        assert stats['std'] == [[0.0, 0.0], [0.0, 0.0]]
        assert stats['min'] == [[0.0, 0.0], [0.0, 0.0]]
        assert stats['max'] == [[0.0, 0.0], [0.0, 0.0]]

    def test_matches_numeric_utils(self):
        """与逐 cell 调 numeric_utils 的结果一致（property 随机数据）"""
        from battery_analysis.utils import numeric_utils
        rng = np.random.default_rng(7)
        for _ in range(10):
            b, c, v = rng.integers(2, 6), rng.integers(1, 4), rng.integers(1, 4)
            data = rng.integers(0, 1000, size=(b, c * v)).tolist()
            list_cpt = compute_list_cpt(data, b, c, v)
            stats = compute_statistics(list_cpt, c, v)
            for ci in range(c):
                for vi in range(v):
                    cell = list_cpt[ci][vi]
                    assert stats['mean'][ci][vi] == pytest.approx(numeric_utils.np_mean(cell))
                    assert stats['med'][ci][vi] == pytest.approx(numeric_utils.np_med(cell))
                    assert stats['std'][ci][vi] == pytest.approx(numeric_utils.np_std(cell))
                    assert stats['min'][ci][vi] == pytest.approx(numeric_utils.np_min(cell))
                    assert stats['max'][ci][vi] == pytest.approx(numeric_utils.np_max(cell))
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run pytest tests/battery_analysis/utils/writers/test_statistics_utils.py -v`
Expected: 文件不存在 → collection error（新建即失败）。

- [ ] **Step 3: 2D 批量实现**

```python
"""
统计计算工具

提供电池容量数据的统计计算函数
"""

import numpy as np

from battery_analysis.utils import numeric_utils


def compute_list_cpt(listBatteryCharge, intBatteryNum, intCurrentLevelNum, intVoltageLevelNum):
    """从电池充电数据计算容量列表，用于后续统计计算"""
    listCpt = [[[] for _ in range(intVoltageLevelNum)] for _ in range(intCurrentLevelNum)]
    arr = np.asarray(listBatteryCharge, dtype=object)

    if arr.ndim == 2:
        # 批量非零收集（object 数组保持 None/str 的 Python 比较语义）
        i = 0
        for c in range(intCurrentLevelNum):
            for v in range(intVoltageLevelNum):
                col = arr[:, i]
                listCpt[c][v] = col[col != 0].tolist()
                i += 1
    else:
        # 行不等长：回退逐元素收集（与原始实现语义一致）
        for b in range(intBatteryNum):
            i = 0
            for c in range(intCurrentLevelNum):
                for v in range(intVoltageLevelNum):
                    if listBatteryCharge[b][i] != 0:
                        listCpt[c][v].append(listBatteryCharge[b][i])
                    i += 1
    return listCpt


def compute_statistics(listCpt, intCurrentLevelNum, intVoltageLevelNum):
    """从容量数据批量计算统计值（pad + np.nan* 2D 归约）"""
    flat_cells = []
    for c in range(intCurrentLevelNum):
        for v in range(intVoltageLevelNum):
            flat_cells.append(listCpt[c][v])

    n_cells = len(flat_cells)
    max_len = max((len(cell) for cell in flat_cells), default=0)

    if max_len == 0:
        zero = [[0.0 for _ in range(intVoltageLevelNum)] for _ in range(intCurrentLevelNum)]
        return {
            'mean': zero, 'med': zero, 'std': zero,
            'mm3s': zero, 'mm2s': zero, 'mp2s': zero, 'mp3s': zero,
            'min': zero, 'max': zero,
        }

    padded = np.full((n_cells, max_len), np.nan, dtype=float)
    counts = np.zeros(n_cells, dtype=np.int64)
    for i, cell in enumerate(flat_cells):
        vals = np.asarray(cell, dtype=float)
        k = vals.size
        if k > 0:
            padded[i, :k] = vals
            counts[i] = k

    with np.errstate(invalid='ignore', divide='ignore'):
        means = np.nanmean(padded, axis=1)
        meds = np.nanmedian(padded, axis=1)
        stds = np.nanstd(padded, axis=1, ddof=1)
        mins = np.nanmin(padded, axis=1)
        maxs = np.nanmax(padded, axis=1)

    # 对齐 numeric_utils 语义：空 cell → 0.0；样本<=1 的 std → 0.0
    means = np.where(counts > 0, means, 0.0)
    meds = np.where(counts > 0, meds, 0.0)
    stds = np.where(counts > 1, stds, 0.0)
    mins = np.where(counts > 0, mins, 0.0)
    maxs = np.where(counts > 0, maxs, 0.0)

    mm3s = means - 3 * stds
    mm2s = means - 2 * stds
    mp2s = means + 2 * stds
    mp3s = means + 3 * stds

    def to_nested(arr1d):
        return arr1d.reshape(intCurrentLevelNum, intVoltageLevelNum).tolist()

    return {
        'mean': to_nested(means),
        'med': to_nested(meds),
        'std': to_nested(stds),
        'mm3s': to_nested(mm3s),
        'mm2s': to_nested(mm2s),
        'mp2s': to_nested(mp2s),
        'mp3s': to_nested(mp3s),
        'min': to_nested(mins),
        'max': to_nested(maxs),
    }
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run pytest tests/battery_analysis/utils/writers/test_statistics_utils.py -v`
Expected: PASS（5 tests）。浮点断言用 `pytest.approx`，忽略位级差异。

- [ ] **Step 5: 全量回归 + commit**

Run: `uv run pytest -q` → 全部通过（含 excel_report_writer 的别名 identity 测试）
Commit:
```bash
git add src/battery_analysis/utils/writers/statistics_utils.py tests/battery_analysis/utils/writers/test_statistics_utils.py
git commit -m "perf(p2): statistics_utils 逐 cell 统计改 pad+np.nan 2D 批量归约

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: battery_analysis 去 .tolist() 降级

**Files:**
- Modify: `src/battery_analysis/utils/processors/battery_analysis.py:299-304`

- [ ] **Step 1: 改调用传 numpy 数组**

`_parallel_process_file` 内 `match_pulse_levels` 调用改为：

```python
        matched = match_pulse_levels(
            record_current.to_numpy(dtype=float),
            record_voltage.to_numpy(dtype=float),
            pulse_mask.to_numpy(dtype=bool),
            listCurrentLevel,
            listVoltageLevel,
            start_row=2,
        )
```

`pulse_mask = detect_pulse_rows(record_df)` 返回 bool pd.Series，`.to_numpy(dtype=bool)` 正确。

- [ ] **Step 2: 跑相关测试**

Run: `uv run pytest tests/battery_analysis/utils/test_battery_analysis.py -v`
Expected: PASS（`test_parallel_process_file_normalizes_read_failure` 验证 read 归一化仍生效；本 Task 不引入新测试——向量化契约由 Task 1 覆盖，此处只是把 pandas 数组直传 numpy 免降级）。

- [ ] **Step 3: 全量回归 + commit**

Run: `uv run pytest -q` → 全部通过
Commit:
```bash
git add src/battery_analysis/utils/processors/battery_analysis.py
git commit -m "perf(p2): battery_analysis 直传 numpy 数组，去除 tolist 降级

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: data_processor 假并行修复

**Files:**
- Modify: `src/battery_analysis/main/business_logic/data_processor.py`
- Modify: `tests/battery_analysis/main/business_logic/test_data_processor.py`

**问题：** `process_all_excel_files` 用 `executor.submit(self.process_excel_with_pandas, ...)`——实例绑定方法不可 pickle，Windows spawn 下必抛异常被外层 `except Exception` 静默吞掉回退串行（假并行）。
**修复：** 提取模块级 worker `_read_excel_worker`（可 pickle），主进程写缓存。`process_excel_with_pandas` 方法保留（其他调用方与串行回退路径仍用它）。

- [ ] **Step 1: 写测试（先失败）**

在 `tests/battery_analysis/main/business_logic/test_data_processor.py` 追加：

```python
import pickle


class TestProcessPoolFix:
    def test_worker_is_picklable_module_level(self):
        """模块级 worker 可 pickle；实例绑定方法不可 pickle（修复必要性证明）"""
        from battery_analysis.main.business_logic import data_processor
        pickle.dumps(data_processor._read_excel_worker)  # 不应抛
        with pytest.raises((pickle.PicklingError, AttributeError, TypeError)):
            pickle.dumps(DataProcessor(Mock()).process_excel_with_pandas)

    def test_process_all_excel_files_real_pool_skips_bad_files(self, tmp_path):
        """真实进程池：worker 可 pickle，坏文件被跳过不崩溃、不静默全串行"""
        for name in ["DC1,mA1.xlsx", "DC1,mA2.xlsx", "bad.xlsx"]:
            (tmp_path / name).write_bytes(b"not a real excel")
        processor = DataProcessor(Mock())
        result = processor.process_all_excel_files(str(tmp_path))
        # 两个文件名合法但内容损坏 → read_excel_file 返回 {} → 全部跳过
        assert result == []
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_data_processor.py::TestProcessPoolFix -v`
Expected: `test_worker_is_picklable_module_level` FAIL（`_read_excel_worker` 不存在 → ImportError/AttributeError）。

- [ ] **Step 3: 实现模块级 worker + 重构**

在 `data_processor.py` 顶部 import 区之后加模块级函数：

```python
def _read_excel_worker(file_path: str) -> dict:
    """进程 worker：读取单个 Excel 返回 info。

    模块级、不访问 self，确保 Windows spawn 下可 pickle。
    缓存由主进程写入（_cache 不可跨进程共享）。
    """
    return read_excel_file(file_path)
```

将 `process_all_excel_files` 中进程池段重构为：

```python
        excel_data = []
        with ProcessPoolExecutor(max_workers=actual_count) as executor:
            futures = {
                executor.submit(_read_excel_worker, os.path.join(directory, f)): f
                for f in listAllInXlsx
            }
            for future in as_completed(futures):
                f = futures[future]
                try:
                    info = future.result()
                except Exception as e:  # pylint: disable=broad-exception-caught
                    self.logger.warning("Skipped unreadable Excel file %s: %s", f, e)
                    continue
                if info:
                    self._cache['excel_files'].put(os.path.join(directory, f), info)
                    excel_data.append(info)
        return excel_data
```

外层 `try/except Exception` 保留（进程池初始化失败等仍回退串行，回退路径继续用 `self.process_excel_with_pandas`）。删除原 `self.process_excel_with_pandas` 的 submit 行。`as_completed` 的 `futures[future]` 取回文件名。

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_data_processor.py -v`
Expected: PASS（原测试 + 2 个新测试）。若真实进程池测试太慢，改为 mock `ProcessPoolExecutor` 验证 submit 目标是 `_read_excel_worker`（spy）。

- [ ] **Step 5: 全量回归 + commit**

Run: `uv run pytest -q` → 全部通过
Commit:
```bash
git add src/battery_analysis/main/business_logic/data_processor.py tests/battery_analysis/main/business_logic/test_data_processor.py
git commit -m "fix(p2): data_processor 绑定方法不可 pickle 假并行改模块级 worker

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: 基准脚本入库 + 验收对比

**Files:**
- Create: `scripts/benchmark_p2.py`

- [ ] **Step 1: 提交可复跑基准脚本（测新实现）**

```python
"""P2 核心计算基准（可复跑，测向量化后实现）

对照旧实现基线（2026-08-21 main 实测）：
  match_pulse_levels(5 万行, C=10/V=15): 0.1682 s
  charge batch(1 万 pos):                17.4730 s
  charge single x1000:                   0.1390 s
验收目标：10-100 倍提速。
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
```

- [ ] **Step 2: 跑基准并记录新数字**

Run: `uv run python scripts/benchmark_p2.py`
Expected: 三个耗时显著下降。目标：
- `match_pulse_levels` ≤ 0.017 s（旧 0.1682 → ≥10x）
- `charge batch` ≤ 0.17 s（旧 17.47 → ≥100x）
- 实际数字记录到脚本注释或 PR 描述。

- [ ] **Step 3: commit 基准脚本**

```bash
git add scripts/benchmark_p2.py
git commit -m "bench(p2): 提交可复跑核心计算基准脚本 benchmark_p2.py

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 7: final review + PR

- [ ] **Step 1: 全量验收**

Run: `uv run pytest -q`
Expected: 529 + 新增契约锁全部通过，0 failed。
Run: `uv run python scripts/run_pylint.py` → 无新增 error、评分 ≥ 7.46（用 `git log main..HEAD -- <文件>` 证明相关文件无存量 error 被触碰）。

- [ ] **Step 2: final code review**

按 superpowers:requesting-code-review 派最终 reviewer，重点：向量化语义是否逐位还原、返回结构是否不变、假并行是否真实生效。

- [ ] **Step 3: push + PR**

```bash
git push -u origin feat/p2-vectorization
gh pr create --base main --head feat/p2-vectorization --title "P2 核心算法向量化" --body "…"
```

PR 描述含基准对比表（旧基线 vs 新实现，达成 10-100 倍）。合并门槛 = ci-cd.yaml build-and-test 全绿。`gh pr merge` 被 auto mode classifier 拦截是已知模式 → **提示用户手动执行** `! gh pr merge <N> --merge --delete-branch`。

---

## Self-Review

- **Spec 覆盖**：路线图 P2 全部 5 项（#8 去 tolist → Task 4；pulse_matcher 广播 → Task 1；charge_calculator searchsorted → Task 2；统计量 2D 批量 → Task 3；#11 ProcessPoolExecutor → Task 5）均有任务。验收（基准 10-100 倍 + 脉冲边界回归）→ Task 6/7。
- **占位符扫描**：无 TBD/TODO；每步含完整代码与命令。
- **类型一致性**：`match_pulse_levels` 签名/返回、`calculate` 返回类型、`compute_statistics` dict 键名全计划一致；`_read_excel_worker` 名称在 Task 5 内统一。
