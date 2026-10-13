# MiniMax (Round 1): MiniMax Round 1：PDF v2.3 规则合规审计——9 项创意盲区与风险点

# MiniMax Round 1：PDF v2.3 规则合规审计——创意/横向视角

## ⚠️ 阅读说明

GPT 做了全局俯瞰，DeepSeek 做了逐条比对。我从**打破隐性假设**和**非常规边界**角度切入，专门找"代码没想过要问的问题"。

---

## 🔴 高优先级：未被测试覆盖的 PDF §7.1.1 Profile

### 问题 1：9 个 Profile 中只有 3 个有自动化测试，6 个是裸代码路径

测试覆盖情况：
- ✅ §7.1.1.1 Coin Cell 常温（30mA/380mAh）→ 有测试
- ✅ §7.1.1.2 Coin Cell 冷冻（单/1S2P）→ 有测试
- ✅ §7.1.1.11 Hermes（CF583083，4 格绝对值）→ 有测试
- ❌ §7.1.1.3–.10 **全部 Pouch Cell profile 缺失测试**（Spiral/Laminate 各档 QNOM）

如果 `build_expectations` 中 `classify_spec` 把某个 Pouch 型误分类为 Coin Cell，或者 `extract_capacity` 解析失败，会静默返回 `[]`，回退到 legacy 逻辑。**没有任何测试会捕捉到这个回归。**

### 问题 2：PDF 的 QNOM 分档临界值测试缺失

代码中：
```python
_POUCH_CAPACITY_BANDS = (
    (1200, [30, 26, 15, 6]),
    (2000, [100, 60, 30, 15, 6]),
    (3000, [150, 100, 60, 30, 15, 6]),
)
```
边界值 `QNOM == 1200`、`QNOM == 2000`、`QNOM == 3000` 落在哪个档？
- `capacity_mah < upper_limit`：1200 → 第一档（30mA），2000 → 第二档（100mA），3000 → 第三档（150mA）
- 但 PDF §7.1.1.6–.8 的容量区间是否用 `<` 而非 `<=`？若 PDF 是 `1200 ≤ QNOM < 2000`，则 `QNOM=1200` 应该属于第二档！

### 问题 3：单样本格（n=1）的 µ-2σ 语义矛盾

当某个 (电流, 电压) 格只有 1 个有效样本时：
- `std = 0`（`ddof=1`，自由度为 0 时归零）
- `mm2s = mean - 2×0 = mean`
- `sample_ok`：取决于 `minimum >= threshold - ε`（可能 Pass）
- `stat_ok`：`mean > threshold`（严格大于，可能 Fail 若 mean == threshold）

**矛盾场景**：1 个样本，值 = 385mAh，threshold = 380mAh → `sample_ok=True`（385 ≥ 380），`stat_ok=True`（385 > 380）→ **Pass**。
**矛盾场景**：1 个样本，值 = 380mAh，threshold = 380mAh → `sample_ok=True`（380 ≥ 380），`stat_ok=False`（380 > 380 不成立）→ **Fail**。

这意味着 PDF 的 "µ-2σ must be **higher than** expected" 对单样本场景的解读存在争议：1 个样本的 µ-2σ 等于其自身，严格"高于"需要样本值 > 阈值。但 `stat_ok=False` 而 `sample_ok=True` 的组合会导致同一样本"所有样本通过但统计量不通过"的矛盾印象。

---

## 🟡 中优先级：数据流与边界假设

### 问题 4：2.25V 不存在时的静默降级陷阱

```python
intPosi2V25 = 0
for v in range(intVoltageLevelNum):
    if listVoltageLevel[v] == 2.25:  # 精确相等比较（浮点风险）
        intPosi2V25 = v
        break
```

若配置/文件中的电压档位是 `2.250` 而非 `2.25`（字符串形式），`==` 比较失败，`intPosi2V25` 保持为 0。然后 legacy fallback 使用 `listMM2S[intPosiMaxmA][0]`（第一个电压档），而不是 2.25V。**这会导致合格判定在错误的电压位置进行，静默产生误判。**

### 问题 5：Hermes 期望格全部跳过后的 legacy fallback 可能给出错误结论

```python
# Hermes 期望：500mA/100mA × 2.25V/2.5V
# 实测档位：[30, 26, 15, 6]（没有 500/100mA）
# → 全部期望格跳过，verdicts = []
# → 进入 legacy fallback：
if listMM2S[intPosiMaxmA][intPosi2V25] / intQnomCapacity >= intPassRate:
```

问题：
- `intPosiMaxmA` 是实测文件中的最高电流（可能是 30mA），不是 Hermes PDF 要求的 500mA 或 100mA
- 30mA 档的 µ-2σ 值可能远高于 500mA 档（放电更慢，可用容量更大）
- **用 30mA 档的数据来判断 Hermes 是否合格，完全不符合 PDF §7.1.1.11 的意图**
- 当前测试 `test_hermes_expectation_outside_levels_uses_legacy_logic` 验证了这个路径存在，但**没有验证其结论的正确性**——它只检查了"走 legacy 逻辑"，而不是"legacy 逻辑给出了合理的 Hermes 结论"

### 问题 6：Pouch 构造方法的字符串脆弱性

```python
lower = construction.lower()
if "laminate" in lower:
    ratio = 0.75
elif "spiral" in lower:
    ratio = 0.85
else:
    return []  # 构造未知 → 回退
```

**假设破坏场景**：
- `"SpiralType"` → `"spiraltype"` → 不含 `"spiral"` → 回退 legacy ⚠️
- `"Laminate"` → 含 `"laminate"` → OK
- `"laminated"` → 含 `"laminate"` → OK
- `"Laminiate"`（拼写错误）→ 不含 `"laminate"` → 回退 ⚠️
- `""`（空）→ 回退 → 用户看到的是"构造方法未填写"还是"不参与判定"？

`data_processor.py` 中 `comboBox_ConstructionMethod` 有值时会设置 `construction_method`，但如果是 Pouch Cell 而用户没填，UI 验证层可能不拦（因为 `_get_types_requiring_construction` 只对 Pouch Cell 要求，但 `_apply_specification_rules` 清空字段）。

### 问题 7：Freezer 识别的"规则覆盖 vs 型号后缀"不一致

```python
# pulse_currents.py
is_freezer = "freezer" in filename.lower() or is_freezer_from_rules(rules, spec_name)
```

`is_freezer_from_rules` 按规则第 5 段「要求可用容量」= 280mAh 判断，不看型号名。但 `build_expectations` 中的冷冻检测：

```python
# quality_requirements.py
is_freezer = required == FREEZER_REQUIRED_CAPACITY_MAH
```

**不一致场景**：
- 型号不在规则列表中 → `is_freezer_from_rules` → False（安全值）
- 但如果某型号在规则中，且 QNOM = 800mAh，`capacity_mah >= 800` → classify_spec 返回 Pouch Cell
- `is_freezer_from_rules` 返回 False（因为规则中没有该型号）
- → 使用 Coin Cell 标准档位 `[30, 26, 15, 6]`，而不是 Freezer 降额档 `[15, 13, 7.5, 3]`
- **如果该型号实际上应该是 Freezer，会用错误的脉冲档位进行测试**

---

## 🟢 低优先级：创意观察

### 问题 8：`_MIN_EPSILON = 1e-6` 只用于 `sample_ok`，不用于 `stat_ok`

```python
sample_ok=minimum >= exp.threshold_mah - _MIN_EPSILON,  # 有 epsilon
stat_ok=mu2sigma > exp.threshold_mah,                   # 无 epsilon！
```

浮点噪声在 `sample_ok` 上被压制，但在 `stat_ok` 上是严格 `>`。这在语义上不一致——如果 `mu2sigma = 380.000001` 而 `threshold = 380`，Pass；但 `mu2sigma = 379.999999`，Fail。这两个值在数值上几乎等价，判定结果却截然不同。这不是 bug（符合 PDF "higher than"），但是一个**隐藏的精度陷阱**。

### 问题 9：µ-2σ 计算的 ddof 假设与 PDF 语义不完全对齐

代码使用 `np.nanstd(padded, axis=1, ddof=1)`（样本标准差），对应"从样本推断总体"的统计推断场景。PDF §6.2.11 说 "µ-2σ value of the corresponding pulse current / cut-off voltage step must be higher than the specified usable capacity"，其中 "µ" 和 "σ" 通常指**总体均值和总体标准差**。

但实际测试中：
- 只有有限样本（可能 n=3~5）
- 用 `ddof=1` 的样本标准差 `s` 估计总体标准差 `σ`
- 严格来说应该用 t 分布（`µ - t_{0.975, n-1} × s`）而不是正态分布（`µ - 1.96 × σ`）
- 当前实现用 `1.96` 的近似（2.0），在 n 小的时候偏乐观（区间太窄，更容易 Pass）

这不是"错误"，但**是 PDF 精神的轻微偏离**：PDF 说 ±2σ 对应约 96% 正态分布覆盖，小样本下 96% 覆盖需要更宽的区间。

---

## 🎯 总结：最重要的三件事

1. **补全 §7.1.1.3–.10 Pouch Cell 的自动化测试**（至少覆盖 Spiral 和 Laminate 各一个 QNOM 档）
2. **在 `build_expectations` 中加入 QNOM 临界值测试**（1200/2000/3000 落在哪一档必须明确）
3. **Hermes 文件档位与 PDF 期望档位不匹配时，应该报错而非静默走 legacy 逻辑**——让用户知道"你的文件没有包含 Hermes PDF 要求的 500mA/100mA 测试档"

---

## 📌 MiniMax 原创洞察：被忽略的"零值安全网"

`compute_statistics` 中：
```python
if max_len == 0:
    zero_keys = ("mean", "med", "std", "mm3s", "mm2s", ... "min", "max")
    return {key: [[0.0]*...] for key in zero_keys}
```

如果某格完全没有有效样本（全是 0 或全是 None），`mm2s = 0.0`。然后在判定中：
- `sample_ok`：`minimum >= threshold - ε` → `0 >= 380` → **False** → Fail ✓（正确）
- `stat_ok`：`0.0 > 380` → **False** → Fail ✓（正确）

**这是正确的安全网行为**——零数据不导致误 Pass。但问题是：这个"零格"是因为文件读取失败（FileNotFoundError）？还是因为脉冲检测失败（`detect_pulse_rows` 返回全 0）？还是真的就是电池样品在某档没有数据？

`BatteryAnalysis._parallel_process_file` 中用 `BatteryAnalysisException` 包装文件读取错误，由 worker 层跳过该文件。这可能导致：某电池的某个档位数据在所有样本中都缺失 → 该格 `mm2s=0` → Fail。但**失败原因被隐藏在数据层面，而非报告层面**，用户看到的只是"Fail"，不知道是因为某个格的数据采集出了问题。

**建议**：在报告的 Remarks 中，当 `stat_ok=False` 且 `mm2s` 异常低（如 < threshold × 0.5）时，提示"数据异常：某档统计量过低，请检查该档数据是否完整"。
