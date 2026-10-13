# DeepSeek (Round 1): PDF v2.3 规则实现的系统性审查：逐条比对与缺陷清单

# PDF v2.2.3 规则实现的系统性审查（Round 1 — DeepSeek）

## 审查范围

比对 `BatteryQualityRequirements_v2.3.pdf` 的 §6.2.11（合格判定）和 §7.1.1（各 profile 期望可用容量）与以下代码文件的实现：

| 核心文件 | 职责 |
|---|---|
| `src/battery_analysis/utils/quality_requirements.py` | 期望值派生 + 合格判定核心 |
| `src/battery_analysis/utils/pulse_currents.py` | 脉冲电流表 + 要求可用容量解析 |
| `src/battery_analysis/utils/battery_classifier.py` | 电池类型分类 |
| `src/battery_analysis/utils/report_coordinator.py` | 报告协调（fallback 判定） |
| `src/battery_analysis/utils/writers/statistics_utils.py` | 统计量计算（μ-2σ） |
| `src/battery_analysis/main/business_logic/validation_spec_rules.py` | 规则应用与 UI 联动 |
| `src/battery_analysis/utils/config_defaults.py` | 默认档位配置 |

---

## 一、§6.2.11 合格判定逻辑逐条比对

### 规则 ①：最小值检查
> PDF: "no single measured sample must have a usable capacity of **less than** the specified expected usable capacity"

**代码** (`quality_requirements.py:235`):
```python
sample_ok=minimum >= exp.threshold_mah - _MIN_EPSILON  # _MIN_EPSILON = 1e-6
```

**判定**：⚠️ 基本正确，但引入微小放宽窗口。

- PDF 语义是"不得低于"（即 `>=`），代码使用 `>= (threshold - 1e-6)` 使比较更宽松。
- 极端情况：若 `minimum = threshold - 0.5e-6`，代码判 Pass，PDF 应判 Fail。实际 mAh 值通常为整数或一位小数，此误差可忽略，但**语义上不精确**。
- **建议**：改为 `minimum >= exp.threshold_mah`（直接整数比较），或在注释中明确"ε 是对浮点存储精度的补偿，不是对 PDF 语义的放宽"。

### 规则 ②：μ-2σ 检查
> PDF: "the µ - 2 value of the corresponding pulse current / cut-off voltage step must be **higher than** the specified usable capacity"

**代码** (`quality_requirements.py:238`):
```python
stat_ok=mu2sigma > exp.threshold_mah
```

**判定**：✅ 正确。严格大于（`>`）与 PDF 的 "higher than" 一致。

### 规则 ③：最高脉冲电流
> PDF: "if not specified otherwise, the highest specified pulse current value should be used to calculate the usable capacity"

**代码** (`quality_requirements.py:178`):
```python
Expectation(float(currents[0]), ...)  # currents[0] 是最高档
```

**判定**：✅ 正确。`lookup_pulse_currents` 返回的列表按降序排列，`[0]` 即最高档。

---

## 二、§7.1.1 各 profile 期望值实现比对

### §7.1.1.1 Coin Cell 常温
> 30mA / >380mAh / 2.25V

**代码** (`quality_requirements.py:160-163`):
```python
current = 15.0 if (is_freezer and spec_method != "1S2P") else 30.0
return [Expectation(current, _EXPECTATION_CUTOFF_V, float(required), "§7.1.1.1/.2")]
```

**判定**：⚠️ **is_freezer 判定逻辑脆弱（高风险）**

- `is_freezer = required == FREEZER_REQUIRED_CAPACITY_MAH`（即 `== 280`）。
- 这将"是否冷冻"等价于"要求容量是否为 280"。若未来冷冻规格要求 300mAh 或其他值，`is_freezer` 将错误判定为 False，使用 30mA 而非 15mA。
- **建议**：将冷冻/常温标识从温度字段（`ti[7]`）或独立标志获取，而非从容量值反推。

### §7.1.1.2 Coin Cell 冷冻
> 单体 15mA / 1S2P 30mA / >280mAh / 2.25V

**代码**：同上，`spec_method != "1S2P"` 时取 15mA。

**判定**：⚠️ **spec_method 匹配不完整**
- 仅处理了 `"1S2P"` 与"非 1S2P"两种情况。
- 若 spec_method 为 `"2S1P"`、`"1S3P"` 等其他成组方式，代码按单体（15mA）处理。
- PDF 对非 1S2P 成组方式的冷冻电流未明确（可能仍按单体），但代码至少应有注释说明此假设。

### §7.1.1.3–.10 Pouch Cell
> QNOM × 85%（螺旋）/ 75%（叠片），最高脉冲电流，2.25V

**代码** (`quality_requirements.py:166-185`):
```python
if "laminate" in lower: ratio = 0.75
elif "spiral" in lower: ratio = 0.85
else: return []  # 构造未知 → 调用方回退历史判定
```

**判定**：🔴 **构造未知时两条路径不一致（高风险）**

当构造方法未识别时：
1. `quality_requirements.py` 返回 `[]` → `report_coordinator.py` 走 **fallback 单点判定**（仅查 μ-2σ ÷ QNOM ≥ pass_rate，**不查最小值**）。
2. `pulse_currents.py:101` 中 `required_useable_capacity_from_rule` 使用 **第一个百分比（85%）** 作为阈值。

结果：fallback 路径用 85% 作为阈值，但只检查 μ-2σ 一个条件，**丢失了最小值检查**。这与 PDF 的双条件要求不符。

**建议**：
- 统一两处的 fallback 策略：若构造未知，`build_expectations` 不返回 `[]` 而是使用默认 85% 并标记 source="default-spiral"，保持双条件检查。
- 或至少在 fallback 路径中增加最小值检查。

**另一问题**：构造方法字符串匹配 `"laminate"` / `"spiral"` 仅支持英文。若用户在配置中添加中文"叠片"/"螺旋"，将无法识别。配置默认值 `["Spiral Type", "Laminate Type"]` 可以匹配，但用户可编辑。

### §7.1.1.11 Hermes (583083)
> 4 个绝对值判定格

**代码** (`quality_requirements.py:152-158`):
```python
if "583083" in spec.upper():
    return [
        Expectation(500, 2.25, 3000, "§7.1.1.11"),
        Expectation(100, 2.25, 3600, "§7.1.1.11"),
        Expectation(500, 2.5, 2600, "§7.1.1.11"),
        Expectation(100, 2.5, 3200, "§7.1.1.11"),
    ]
```

**判定**：⚠️ **仅验证 4 格，未覆盖全部脉冲档位**

- Hermes 有 5 档电流（500/250/100/50/25mA）和 7 档电压（2.5–1.8V）。
- 代码仅验证 (500, 2.25)、(100, 2.25)、(500, 2.5)、(100, 2.5) 共 4 格。
- **250mA、50mA、25mA 档位以及 2.4V/2.3V/2.2V/2.0V/1.8V 电压档位均未验证**。
- 若 PDF §7.1.1.11 表格对这些档位也有期望值，则存在遗漏。

**另一问题**：`"583083" in spec.upper()` 是子串匹配，会匹配任何包含 "583083" 的型号（如 "CP583083A"、"CF583083"）。通常合理，但若存在 "5830830" 等近似型号会误匹配。

---

## 三、电压档位匹配与索引安全

### 2.25V 查找
**代码** (`report_coordinator.py:104-108`):
```python
intPosi2V25 = 0
for v in range(intVoltageLevelNum):
    if listVoltageLevel[v] == 2.25:  # 精确 float 比较
        intPosi2V25 = v
        break
```

**判定**：🔴 **精确浮点比较 + 默认值 0 的静默失败（高风险）**

1. `listVoltageLevel[v] == 2.25` 是精确比较。若电压值来自浮点运算（如 `2.2500000000000004`），将永远不匹配。
2. 未找到 2.25V 时，`intPosi2V25` 保持默认值 `0`，即使用**第一个电压档位**（默认配置为 2.6V）。fallback 判定将使用错误的 μ-2σ 值。
3. **没有任何警告或日志**。

**建议**：
- 改用容差比较：`abs(listVoltageLevel[v] - 2.25) < 1e-6`（与 `quality_requirements._match_index` 一致）。
- 找不到时抛出明确异常或记录警告，而非静默回退到 index 0。

### _match_index 容差不一致
**代码** (`quality_requirements.py:203-209`): 使用 `1e-6` 容差。
**代码** (`report_coordinator.py:106`): 使用精确 `==` 比较。
**代码** (之前版本): 使用 `abs(...) < 0.001` 容差。

**判定**：⚠️ 三处匹配逻辑容差不同，可能导致同一电压值在不同路径中匹配/不匹配。

---

## 四、统计量计算（μ-2σ）

**代码** (`statistics_utils.py:88`):
```python
mm2s = means - 2 * stds
```

**判定**：⚠️ **单样本 std=0 问题**

- 单样本时 `std(ddof=1)` 返回 0.0，μ-2σ = mean。
- 此时 `stat_ok = mean > threshold`，与 `sample_ok = min >= threshold` 几乎等价（仅差 ε），**失去统计判别的独立意义**。
- PDF 未明确 n=1 时的处理方式，但代码无警告。
- **建议**：当样本数 < 2 时，标记 `stat_ok` 为"insufficient data"或添加警告。

---

## 五、单位与舍入

### round() 使用
**代码** (`quality_requirements.py:178`):
```python
float(round(qnom * ratio))
```

Python `round()` 使用 banker's rounding（round-half-to-even）：
- `round(2.5) = 2`，`round(3.5) = 4`
- 若 `qnom × ratio` 恰好为 `.5`，结果可能与 PDF 预期的"四舍五入"不同。
- 实际中 `qnom × 0.85` 或 `× 0.75` 很少恰好为 `.5`，风险低。
- **建议**：若 PDF 明确"四舍五入"（round-half-up），使用 `math.floor(x + 0.5)`。

### 报告输出取整
**代码** (`quality_requirements.py:94,273`): `round(exp.threshold_mah)` 用于报告文本。
**代码** (`word_overview.py:49`): `math.floor(100 * mm2s / intQnom)` 用于百分比。

- 百分比使用 `math.floor`（向下取整），与阈值计算的 `round()` 不一致。
- 若 PDF 规定百分比精度，需确认 floor 是否正确。

---

## 六、Fallback 路径的完整性

**代码** (`report_coordinator.py:173-183`):
```python
if not verdicts:
    # 旧版判定
    if listMM2S[intPosiMaxmA][intPosi2V25] / intQnomCapacity >= intPassRate:
        strResult = "Pass"
    else:
        strResult = "Fail"
```

**判定**：🔴 **Fallback 丢失最小值检查（高风险）**

- PDF §6.2.11 要求**两个条件**同时满足：①所有样本 ≥ 期望，②μ-2σ > 期望。
- Fallback 仅检查 μ-2σ ÷ QNOM ≥ pass_rate，**完全跳过最小值检查**。
- 当 `build_expectations` 返回空列表时（Coin Cell required=None、Pouch 构造未知、型号不匹配等），此 fallback 激活。
- **建议**：在 fallback 中增加最小值检查，或确保 `build_expectations` 尽可能不返回空列表。

---

## 七、验证与 UI 联动的边界条件

### required_useable_capacity_from_rule 的双百分比默认值
**代码** (`pulse_currents.py:101`):
```python
pct_text = dual.group(2) if "laminate" in ... else dual.group(1)
```

构造未知时默认取第一个百分比（85%，螺旋）。但 `quality_requirements.py` 此时返回 `[]`。

**判定**：⚠️ 同一规则在两处产生不同的阈值，见 §2 Pouch Cell 部分。

### _require_positive_int 的强制性
**代码** (`report_coordinator.py`): 对 `listTestInfo[17]` 和 `listTestInfo[9]` 调用 `_require_positive_int`，若 ≤ 0 抛 ValueError。

**判定**：⚠️ 若 Coin Cell 的 `required` 字段为空（旧数据），`listTestInfo[17]` 为 0，将抛异常而非降级处理。

---

## 八、缺陷汇总（按风险排序）

| # | 风险 | 文件 | 问题 |
|---|------|------|------|
| 1 | 🔴 高 | `report_coordinator.py:106` | 2.25V 精确 float 比较 + 默认 index 0 静默失败 |
| 2 | 🔴 高 | `report_coordinator.py:173-183` | Fallback 路径丢失最小值检查 |
| 3 | 🔴 高 | `quality_requirements.py:169-173` | 构造未知时返回 []，两路径阈值不一致 |
| 4 | ⚠️ 中 | `quality_requirements.py:160` | is_freezer 依赖 `required == 280`，脆弱 |
| 5 | ⚠️ 中 | `quality_requirements.py:152-158` | Hermes 仅验证 4 格，未覆盖全部档位 |
| 6 | ⚠️ 中 | `statistics_utils.py:88` | 单样本 μ-2σ 失去判别意义 |
| 7 | ⚠️ 中 | `quality_requirements.py:235` | 最小值检查的 ε 放宽语义不精确 |
| 8 | ⚠️ 低 | `quality_requirements.py:178` | round() banker's rounding 可能与 PDF 不符 |
| 9 | ⚠️ 低 | `quality_requirements.py:161` | spec_method 仅处理 1S2P vs 其他 |
| 10 | ⚠️ 低 | `quality_requirements.py:169` | 构造方法匹配仅支持英文关键词 |
| 11 | ⚠️ 低 | `quality_requirements.py:152` | "583083" 子串匹配可能误判 |
| 12 | ⚠️ 低 | `report_coordinator.py` | 三处电压匹配容差不一致 |
| 13 | ⚠️ 低 | `report_coordinator.py` | `_require_positive_int` 对旧数据抛异常而非降级 |
| 14 | ⚠️ 低 | `word_overview.py:49` | 百分比 floor() 与阈值 round() 精度不一致 |
| 15 | ℹ️ 信息 | `quality_requirements.py` | PULSE_STEP_SCHEDULES 未验证是否与 PDF 一致 |

---

## 九、具体修复建议

1. **`report_coordinator.py:106`**：将 `listVoltageLevel[v] == 2.25` 改为 `abs(float(listVoltageLevel[v]) - 2.25) < 1e-6`，并在未找到时抛出异常或 `logger.warning`。

2. **`report_coordinator.py` fallback**：增加最小值检查：
   ```python
   if (listMM2S[intPosiMaxmA][intPosi2V25] / intQnomCapacity >= intPassRate
       and listMin[intPosiMaxmA][intPosi2V25] >= intRequiredCapacity):
   ```

3. **`quality_requirements.py:169-173`**：构造未知时不要返回 `[]`，改为使用默认 85% 并标记来源：
   ```python
   else:
       ratio = 0.85  # 默认螺旋
       source = "§7.1.1.3-.10 (default spiral)"
   ```

4. **`quality_requirements.py:160`**：is_freezer 应从温度字段（`ti[7]`）获取，而非从容量反推：
   ```python
   is_freezer = "freezer" in str(ti[7] or "").lower() or float(ti[7] or 0) < 0
   ```

5. **`quality_requirements.py`**：Hermes 补全所有 PDF 列出的判定格，或至少注释说明为何仅取 4 格。

6. **`statistics_utils.py`**：当 `n < 2` 时返回 `stat_ok=None`（"insufficient data"）而非强制 True/False。

---

*DeepSeek — 系统思维者，Round 1*
