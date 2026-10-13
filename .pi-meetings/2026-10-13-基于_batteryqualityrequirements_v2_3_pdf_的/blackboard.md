# Meeting: 基于 BatteryQualityRequirements_v2.3.pdf 的后台逻辑修复合规检查
"C:\Users\boe\Desktop\BatteryQualityRequirements_v2.3.pdf"
进行了很多后台逻辑的修复和新增
请你排出多agents进行检查，它们是否还有问题
是否遵照pdf中的规则
> Created: 2026-10-13T01:29:03.488Z
> Type: Brainstorming (3 rounds)

---

## GPT (Round 1): PDF 规则→代码映射的全景审计与检查策略

# PDF 规则→代码映射的全景审计与检查策略

## 一、当前实现全景：做了什么

近期提交（625e19f 起的一系列 fix）围绕 **BatteryQualityRequirements_v2.3** 构建了三层核心能力：

### 1. 规则解析层（pulse_currents.py + battery_classifier.py）
- **§7.1.1 脉冲电流查表**：Coin Cell 标准/冷冻/1S2P Pack、Pouch Cell QNOM 四档、Hermes（583083）特殊覆盖均已实现
- **要求可用容量解析**（`required_useable_capacity_from_rule`）：支持绝对值（"380"）、单百分比（"80%"）、构造双百分比（"85%|75%"）三种形式
- **冷冻型判定**（`is_freezer_from_rules`）：以规则第 5 段 280mAh 为唯一判定依据

### 2. 合格判定层（quality_requirements.py）
- **§6.2.11 双判定格**：① 单样本最小值 ≥ 期望（含 1e-6 容差）；② μ-2σ > 期望（严格大于）
- **§7.1.1.1–.11 期望值派生**（`build_expectations`）：Coin Cell 按冷冻/成组方式取电流档、Pouch Cell 按 QNOM × 85%/75%（螺旋/叠片）、Hermes 4 格绝对值
- **判定范围约定**：只对 PDF 指定的 (脉冲电流, 截止电压) 格判合格，9 档超集仅统计不判定

### 3. 输入验证层（validation_fields/feedback/spec_rules + input_validator.py）
- **字段级验证**：必填、容量正整数、路径、版本号、老化范围
- **UI 高亮反馈**：`_LEGACY_FIELD_CHECKS` 17 项逐一检查并高亮
- **文件名→UI 自动填充**：脉冲电流文件名优先、查表兜底、不一致时告警

## 二、发现的 10 个风险点与盲区

### 🔴 高优先级风险

**R1: Pouch Cell 构造方法未知 → 合格判定静默跳过**
`build_expectations` 在 `construction` 为空或不含 "spiral"/"laminate" 时返回 `[]`（quality_requirements.py:180），此时调用方"回退到历史单点判定"——但**这个回退在哪里实现？** 如果 report_coordinator.py 只是拿到空 expectations 就跳过判定，那么一批未标注构造方法的 Pouch Cell 数据将**完全没有合格判定输出**，报告 Result 列可能出现空白。这在实际使用中是最可能被忽视的合规空洞。

**R2: Coin Cell 阈值来源的"规则 vs PDF"偏移**
Coin Cell 判定阈值取 `required`（即 `ti[17]`，UI 中 "Required Useable Capacity" 字段），而非直接取 PDF 的 380/280 常量。如果用户在 UI 中手动修改了该字段（或 config 规则被改），判定阈值会随之改变，但 PDF 规则是固定的。这提供灵活性但引入偏离 PDF 的口子，且没有约束 `required` 必须等于 280/380。

**R3: 双重验证的优先级可能违反 PDF 语义**
`_process_first_excel_file` 中文件名解析的脉冲档位优先于查表值。但 PDF §6.2.11 说 "the highest specified pulse current value should be used to calculate the usable capacity"——这里 "specified" 是指 PDF 还是文件名？代码以文件名为准，仅 warn 不阻断。若文件名错误且用户不看 warning，判定格将匹配错误的电流档，导致 μ-2σ 取错位置。

### 🟡 中优先级风险

**R4: Reported By 字段验证不一致**
`_LEGACY_FIELD_CHECKS` 包含 "Reported By"（`comboBox_ReportedBy`，label 为 None），但 `InputValidator.REQUIRED_TEXT_FIELDS` **不含** `reported_by`。这意味着纯验证器通过但 legacy 检查可能失败（或反之），两条验证路径对同一字段给出不同答案。`analysis_runner.py` 的 `_check_inputs` 弹窗在 `checkinput()` 失败时兜底检查 Reported By，但 `validate_fields()` 的 field_errors 不含它——信息不完整。

**R5: 温度判定与冷冻判定的交互逻辑分散**
冷冻型识别有三个入口：
1. 文件名含 "freezer"（data_processor.py:344）
2. 规则第 5 段 = 280（`is_freezer_from_rules`）
3. `temperature_handler.set_temperature_by_capacity`（validation_spec_rules.py:170）

三个入口的一致性靠注释维护，无统一的 `FreezerContext` 或配置驱动。如果文件名说 freezer 但规则说 380，当前代码仍按文件名走，但期望值阈值会用 `required=380`（因为 `build_expectations` 取 `ti[17]`，而 `ti[17]` 是 UI 字段，可能已被 `set_temperature_by_capacity` 填为 280）。**阈值来源和判定电流来源可能不同步**。

**R6: Hermes 期望值硬编码在代码中**
§7.1.1.11 的 4 个期望值（3000/3600/2600/3200 mAh）直接硬编码在 `build_expectations` 中，而其他型号的期望值来自 config 规则。如果 PDF 更新到 v2.4 修改 Hermes 参数，需要改代码而非配置。这违反了"规则→配置"的可维护性原则。

**R7: 脉冲 burst 参数（PULSE_BURSTS=10, PULSE_STEP_SCHEDULES）未见在分析管线中使用**
这些常量定义在 quality_requirements.py:31-37，但我在扫描中未看到它们被 data_processor 或 report_coordinator 引用。如果它们是为将来"验证测试 profile 的脉冲时序是否符合 §7.1.1"而预留的，应明确注释；如果本应参与当前判定，则是遗漏。

### 🟢 低优先级但值得记录

**R8: `_require_positive_int` 只校验 Calculated/Required Capacity**
Datasheet Nominal Capacity 虽为必填但不参与 `_require_positive_int` 校验（report_coordinator.py:145-147 只取 `listTestInfo[9]` 和 `listTestInfo[17]`）。若 Datasheet Capacity 填入 "0" 或非数字，不会报错但可能影响报告准确性。

**R9: 规格映射配置（SpecificationTypeCoinCell/PouchCell）的孤儿型号**
`_get_all_specifications` 把 Coin+Pouch 拼接后展示，但不检查规则（Rules）中是否有对应条目。如果 config 的 Rules 缺少某型号，UI 可选但查表返回空，导致脉冲档位和期望值均为空，判定静默跳过（与 R1 相同后果）。

**R10: 测试覆盖的"集成缝隙"**
现有测试（test_pulse_currents, test_quality_requirements, test_data_processor）各自覆盖良好，但缺少端到端场景：**从 Excel 文件 → 数据提取 → build_expectations → evaluate_expectations → 报告写入** 的完整链路测试。e2e/test_new_model_analysis.py 覆盖了派生，但判定结果写入报告的集成路径（report_coordinator → excel_report_writer → verdict_map）未见集成断言。

## 三、检查优先级建议（四级框架）

| 优先级 | 检查目标 | 对应风险 | 方法 |
|--------|---------|---------|------|
| **P0: 判定完整性** | 确认"无判定格输出"场景有兜底 | R1, R9 | 构造方法为空的 Pouch Cell 数据跑完整流程，检查报告 Result 列是否有内容 |
| **P1: 阈值一致性** | Coin Cell 阈值与 PDF 固定值一致性 | R2, R5 | 对 CR2450 系列跑 build_expectations，断言 threshold ∈ {280, 380} 而非 UI 自定义值 |
| **P2: 数据源优先级** | 文件名 vs 查表冲突时的行为 | R3 | 构造文件名说 [30-26-15-6] 但 QNOM=2500（查表应为 [100-60-30-15-6]）的场景，验证判定格用哪个电流 |
| **P3: 验证路径一致性** | InputValidator vs Legacy 检查的字段集差异 | R4 | 对比两个验证路径的字段集，确认无单侧遗漏 |

## 四、系统化验证的长期策略

1. **建立"PDF 规则→代码映射矩阵"**：每个 PDF 条款（§6.2.11a, §6.2.11b, §7.1.1.1–.11）对应到代码中的函数/常量/测试用例，形成可追踪的追溯表
2. **引入"黄金样本回归"**：为每个 PDF profile（Coin Std/Freezer/1S2P、Pouch 四档、Hermes）准备一组已知输入→期望判定结果的 golden fixtures，任何规则改动必须跑通全部 golden
3. **将 Hermes 等特殊型号参数外置到配置**：消除硬编码，与 Rules 配置同源
4. **统一冷冻上下文**：建立单一 `FreezerContext` 数据类，集中管理"文件名说 freezer / 规则说 280 / UI 温度"三者的优先级和一致性检查

## 五、总结

近期的修复工作在 PDF 规则→代码的映射上做了扎实的工作，核心判定逻辑（§6.2.11 双判定 + §7.1.1 期望值派生）实现正确。最大的风险不是"算错了"，而是**"该算的没算"**——构造方法缺失、规格无规则、验证路径不一致等场景下的静默跳过。建议检查团队优先验证 P0（判定完整性），确保每一批数据都有非空的判定输出；其次 P1（阈值一致性），确保 Coin Cell 的 280/380 不被用户输入意外覆盖。


---

## DeepSeek (Round 1): PDF v2.3 规则实现的系统性审查：逐条比对与缺陷清单

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


---

## User (Feedback after Round 1): 用户已修复 MiniMax 与 GLM 的 API Key，要求让它们补交 Round 1 意见。

用户反馈（Round 1 后）：

> api key我已修复，你再看看他们的意见

含义：MiniMax 与 GLM 因 401 Invalid API Key 在 Round 1 未响应，现 API Key 已修复，要求两位顾问补交 Round 1 初始分析（阅读 PDF 与仓库后给出独立意见），随后进入 Round 2。

---

## MiniMax (Round 1): MiniMax Round 1：PDF v2.3 规则合规审计——9 项创意盲区与风险点

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


---

## GLM (Round 1): 纠偏 + 独立核查：分档表矛盾、冷冻三口径、2.25V 错位与可执行修复清单

# GLM Round 1：PDF v2.3 后台逻辑的务实核查——先纠偏，再给可执行修复清单

## 〇、前置声明：我读 PDF 的方式与局限（必须先说清）

`C:\Users\boe\Desktop\BatteryQualityRequirements_v2.3.pdf` 的文本流全部经 FlateDecode 压缩，我的工具集（read/grep）无法直接解出正文。因此我的"PDF 规则"来自三个交叉来源：

1. **仓库自身的 PDF 派生物**（可信度最高，因为是修复时逐条对照写的）：
   - `src/battery_analysis/utils/quality_requirements.py:1-47` 模块 docstring 逐字引用 §6.2.11 三条英文原文（最小值不低于期望、μ-2σ 严格高于期望、未特别说明时取最高脉冲电流）；
   - `src/battery_analysis/utils/pulse_currents.py:1-21` docstring 的 §7.1.1 各 profile 脉冲档位表；
   - `tests/battery_analysis/utils/test_pulse_currents.py` 与 `test_quality_requirements.py` 把档位/期望值固化为断言。
2. **2026-09-23 会议黑板中用户提供的 PDF 摘录**（`.pi-meetings/2026-09-23-pulse_currents_逻辑分析与优化/blackboard.md:557-630`）。
3. GPT/DeepSeek 本轮 Round 1 中引用的 §6.2.11 / §7.1.1.1–.11 条文。

来源 1 与 2 之间存在**互相矛盾的记录**（见发现 A），这本身就是要交给用户裁决的问题：**建议会议最终结论里明确要求有人用 pdftotext 重新导出 §7.1.1 全表并入库为 fixtures**，把"规则来源"从"三处口径"收敛为一处。

## 一、对已有意见的纠偏（当前代码 ≠ DeepSeek 描述的代码）

**DeepSeek 的高危项 #2"fallback 丢失最小值检查"已经部分不成立。** 当前 `report_coordinator.py:166-176`：`build_expectations` 返回空时，不再直接走旧单点判定，而是构造一个 legacy `Expectation(最高实测电流, 2.25V, required容量)` 交给 `evaluate_expectations`，**双条件（① 所有单样本 ≥ 期望；② μ-2σ > 期望）都执行**。

但旧单点路径没有死透：`report_coordinator.py:178-197`，当 `verdicts` 为空（期望格不在实测档位里）时，仍回退到 `listMM2S[intPosiMaxmA][intPosi2V25] / intQnomCapacity >= intPassRate`——只有 μ-2σ/QNOM 单条件、且阈值口径是 required/calculated 而非 PDF 绝对值。什么时候触发？见发现 B 的具体场景。**Round 2 讨论时请以当前代码为准，别基于过期描述排优先级。**

## 二、我的独立发现（按风险排序，全部带文件:行号）

### A. 🔴 Pouch 容量分档脉冲表与 PDF 摘录记录不一致——两位同行都没查这一项

`pulse_currents.py:46-53` 实现（测试 `test_pulse_currents.py:127-137` 固化）：

| QNOM 区间 | 代码档位 |
|---|---|
| < 1200 | 30/26/15/6 |
| 1200–2000 | 60/30/15/6 |
| 2000–3000 | 100/60/30/15/6 |
| ≥ 3000 | 150/100/60/30/15/6 |

而 2026-09-23 会议中用户提供的标准摘录是：

| QNOM 区间 | 摘录档位 |
|---|---|
| < 1200 | 30/26/15/6 ✓ 一致 |
| 2000 ≤ QNOM < 3000 | **150/100/60/30** ✗ |
| ≥ 3000 | **500/250/100/60/30/15/6（7 级）** ✗ |

且摘录中**根本不存在 1200–2000 这个档**，代码却凭空多出一档。同时摘录把 CF583083 归在 "CP305050/CF583083 等 — 100/60/30/15/6" 组，而代码 override 是 500/250/100/50/25（`pulse_currents.py:56-58`）——两份记录至少有一份错了。**这直接影响判定格选择**：`build_expectations` 取 `currents[0]` 作为判定电流（`quality_requirements.py:186`），档位表错 → 判定电流错 → μ-2σ 取错格 → Pass/Fail 可能整个错位。

**修复动作**：用 pdftotext 重新导出 §7.1.1 各表，人工比对 `_POUCH_CAPACITY_BANDS`、`_POUCH_LARGE_PULSE_CURRENTS`、`_MODEL_OVERRIDES`，改错项并同步改测试。这是 10 分钟的工作，却是本轮**唯一可能推翻"判定格选错"的硬伤**，优先级应排第一。

### B. 🔴 冷冻判定三处口径不同步 → 静默掉进旧单点判定（具体场景可复现）

- `data_processor.py:344`：`is_freezer = "freezer" in filename.lower() or is_freezer_from_rules(rules, spec_name)` —— 文件名 OR 规则；
- `quality_requirements.py:160`：`is_freezer = required == FREEZER_REQUIRED_CAPACITY_MAH`（即 ti[17]==280）—— 只看规则侧字段。

**复现场景**：文件名含 "freezer"（测试实际跑 15/13/7.5/3 降额档），但规则第 5 段是 380（或用户在 UI 改过 Required 字段）。数据侧按冷冻档位跑；`build_expectations` 却按常温派生 30mA 期望 → 30 不在实测档 [15,13,7.5,3] 中 → `evaluate_expectations` 跳过（`quality_requirements.py:224-226`）→ verdicts 为空 → `report_coordinator.py:183` 旧单点判定启动：单条件、阈值=required/计算容量，且**无任何日志说明走了兜底**。

**修复（最小 diff）**：
1. `build_expectations` 增加可选参数 `is_freezer`，由调用方（report_coordinator / excel_report_writer）用与 data_processor 同一个函数的结果传入；
2. `report_coordinator.py:183` 兜底分支加 `logger.warning("expectation cells not in measured levels, legacy single-point verdict used")`，Report Remarks 中注明 "legacy verdict"。

### C. 🟡 2.25V 精确浮点比较 + 默认 index 0 静默错位（确认仍在）

`report_coordinator.py:104-108`：`if listVoltageLevel[v] == 2.25` 精确比较；找不到时 `intPosi2V25` 保持 0。后果在当前代码里比 DeepSeek 说的更隐蔽：legacy 期望格的 `cutoff_v = float(listVoltageLevel[intPosi2V25])`（`report_coordinator.py:170`）会**成功匹配到 index 0（如 2.6V）**，于是报告正常产出 Pass/Fail，但判的是 2.6V 格——表面无异常、实际错电压。三处匹配容差不一致（`quality_requirements._match_index` 用 1e-6，这里用 `==`）。

**修复**：`abs(float(listVoltageLevel[v]) - 2.25) < 1e-6`；找不到时 `logger.warning` 并在 Remarks 标注，而不是默默用 index 0。5 行改动。

### D. 🟡 空样本格被判 "Fail (minimum 0mAh)" 而不是 "无数据"

`statistics_utils.py:73-77` 空格统计值全部置 0.0；`evaluate_expectations` 不检查样本数。若期望格恰好没有有效样本（如 Hermes 2.5V 格在该批数据缺失），会输出 Fail/minimum 0mAh——**把"没测到"报成"不合格"**，对产线是误报。

**修复**：`compute_statistics` 已有 counts 概念但没输出；让它返回 `counts` 矩阵，`evaluate_expectations` 对 `counts==0` 的期望格跳过并汇总到 Remarks（"no samples at X"）。约 15 行。

### E. 🟡 构造方法关键词匹配只认英文，配置却是用户可编辑的

`quality_requirements.py:169-175` 靠 `"laminate" in lower / "spiral" in lower` 识别；`config_defaults.py:11` 默认 `["Spiral Type", "Laminate Type"]` 没问题，但 constructionMethods 是用户可编辑配置——用户加一条中文"叠片"，匹配失败 → 返回 [] → 兜底路径，阈值从 75% 悄悄变成 required 单点口径。i18n 目录存在（`locale/`），UI 若中文化这个雷必踩。

**修复**：匹配时同时认 `"叠片" in construction or "laminate" in lower`、`"螺旋" or "spiral"`；或按 comboBox 索引对应关系映射。2 行。

### F. 🟢 小项（低优先级，排队处理）

1. **Hermes 4 格 + 期望值硬编码**（`quality_requirements.py:152-158`）：与 GPT R6 同判断；且 §7.1.1.11 是否只有 4 格需要 PDF 复核（DeepSeek 的疑问成立）。建议至少把 4 个元组外置为模块级常量并附 PDF 页码注释。
2. **Pouch 阈值基数**：`build_expectations` 用 ti[9]（Calculated Capacity）× 85%/75%，`required_useable_capacity_from_rule` 用规则第 4 段（同为计算容量）——两处自洽，但 PDF 写的是 "QNOM × 85%"，QNOM 指标称（ti[8]）还是计算容量需要确认。CR2450 规则里 600/550 两者不同，若 PDF 指标称，Pouch 阈值整体偏低。
3. **`evaluate_expectations` 的 try/except 静默 continue**（`quality_requirements.py:227-229`）：与"该算的没算"主题一致，至少 debug 级日志。
4. **`round()` 银行家舍入**（`quality_requirements.py:186`）：与 DeepSeek 结论相同，实际触发概率低，登记即可。

## 三、务实修复顺序（成本/收益排序）

| 序 | 动作 | 文件 | 成本 | 收益 |
|---|------|------|------|------|
| 1 | PDF §7.1.1 全表重导出 + 人工比对分档表/override，裁定 A 项矛盾 | pulse_currents.py + 测试 | 30 分钟 | 消除"判定格选错"的系统性风险 |
| 2 | 2.25V 容差匹配 + 未找到告警 | report_coordinator.py:104-108 | 5 行 | 消除静默错电压 |
| 3 | is_freezer 单一来源 + 兜底路径日志 | quality_requirements.py / report_coordinator.py | ~20 行 | 消除场景 B 的静默降级 |
| 4 | 空样本格跳过并注明 | statistics_utils.py / quality_requirements.py | ~15 行 | 消除误报 Fail |
| 5 | 构造方法中文关键词 | quality_requirements.py | 2 行 | 防中文化踩雷 |
| 6 | 补一条端到端测试：文件名/查表档位不一致 → 验证走哪条判定路径、报告怎么标注 | tests/e2e | 半天 | 把 B 场景锁死成回归 |

**不建议做的**：为 4 种 profile 引入策略类/注册表架构（2026-09-23 会议已论证过，dict 查表足够）；重构 ReportCoordinator 把 verdict 计算再抽一层——当前三处调用（report_coordinator / excel_report_writer:134-138 / word 侧）各调一次 build+evaluate 已经够平，先修数据正确性，不动结构。

## 四、一句话结论

核心判定公式（§6.2.11 双条件、严格大于、ε 容差）实现是对的且测试固化良好；真正的风险集中在**"判定格怎么选出来"**——脉冲分档表与 PDF 摘录矛盾（A）、冷冻三口径不同步（B）、2.25V 静默错位（C）——这三个都属于"格选错 → 全错"型缺陷，应先于一切代码美化处理。

---

## MiniMax (Round 2): 重新定优先级：QNOM 分档表矛盾为 P0；冷陈三口径同步为 P1；发现 fallback 路径在期望格不在档位时仍有静默单条件判断问题；单样本格 µ-2σ 语义矛盾被全部四人忽视；提出 3 个新盲区。

# MiniMax Round 2：挑战与深化——重新定优先级 + 三个被遗漏的盲区

## 〇、阅读说明

Round 1 我提了 9 项创意盲区，GPT 做了全局俯瞰，DeepSeek 做了逐条 PDF 比对，GLM 做了纠偏与务实核查。本轮我从"四人是否互相说漏了"和"代码是否还有没说出口的假设"两个角度切入。

---

## 一、对 GLM 纠偏 DeepSeek 的确认与深化

GLM 正确指出 DeepSeek 的"fallback 丢失最小值检查"已过时。当前 `report_coordinator.py:165-176` 确实在 `build_expectations` 返回 `[]` 时，构造了 legacy `Expectation` 对象并交给 `evaluate_expectations` 执行双条件（`sample_ok` + `stat_ok`）。DeepSeek 的描述基于过期代码。

**但 GLM 没有说完**——这个"legacy 构造 Expectation"路径在以下场景仍会触发静默单条件降级，值得补充：

> 当 `build_expectations` 返回非空，但 `evaluate_expectations` 因期望格不在实测档位而 `verdicts = []` 时，`report_coordinator.py:178-188` 走的是 `listMM2S[intPosiMaxmA][intPosi2V25] / intQnomCapacity >= intPassRate`——**单条件，阈值是 required/QNOM 比例，不是 PDF 绝对期望值**，且**没有任何日志或 Remarks 标注**。这是 GLM 发现 B 的完整场景。

确认：GLM 的 B 项（冷冻三口径不同步导致 verdicts=[] → legacy 单点判定）优先级应为 🔴 高，修复方案加一条——`report_coordinator.py:183` 的单条件分支需加 `logger.warning`，并让 Remarks 注明 `"legacy single-point judgment used"`。

---

## 二、GLM 发现 A（QNOM 分档表矛盾）与我 Round 1 问题 2 的合并深化

GLM 的发现 A（分档表与 PDF 摘录矛盾）与我 Round 1 的问题 2（QNOM 临界值落在哪一档）是同一问题的两个侧面——现已合并确认。

**验证：实际代码**（`pulse_currents.py:46-53`）：

```python
_POUCH_CAPACITY_BANDS = (
    (1200, [30, 26, 15, 6]),
    (2000, [60, 30, 15, 6]),
    (3000, [100, 60, 30, 15, 6]),
)
# QNOM >= 3000: 150/100/60/30/15/6
```

docstring：`1200 <= QNOM < 2000`、`2000 <= QNOM < 3000`、`QNOM >= 3000`。

代码用 `capacity_mah < upper_limit` 遍历，取第一个满足的档——即：
- QNOM=1199 → 第一档（30mA）
- QNOM=1200 → **第二档（60mA）** ← 边界落在第二档
- QNOM=1999 → 第二档（60mA）
- QNOM=2000 → **第三档（100mA）** ← 边界落在第三档
- QNOM=3000 → 第四档（150mA）

**但 PDF 2026-09-23 摘录中**：
- 2000 ≤ QNOM < 3000 → 150/100/60/30（无 15/6）
- QNOM ≥ 3000 → 7 级（500/250/100/60/30/15/6）

且摘录**没有 1200–2000 档**（代码凭空多出一档）。这意味着：
1. **QNOM=1200** 代码判入 60mA 档，PDF 可能要求入 30mA 档（如果 PDF 用 `< 1200` + `1200 ≤ QNOM < 2000` 而非 `< 1200` + `< 2000`）
2. **QNOM=2000** 代码判入 100mA 档，PDF 摘录似乎说入 150mA 档
3. **摘录中 1200–2000 区间的缺失**是最关键的问题——这个档是代码自己发明的，没有 PDF 来源

**优先级重新排序**：这是整个会议中**唯一能导致系统性判定格选错的源头性错误**，排在 P0。修复成本（30 分钟导出 PDF 重比对）远低于风险（所有 QNOM 落入 1200–2000/2000–3000 边界的 Pouch 电池判定全部错位）。

---

## 三、我 Round 1 问题 3 被四人全部忽视——这是本轮最重要的补充

### 单样本 µ-2σ 语义矛盾：为什么没人提

四人中，DeepSeek 提到了"单样本 std=0，µ-2σ 失去独立意义"（中优先级），我 Round 1 提到了"值恰好等于 threshold 时 sample_ok=True 但 stat_ok=False"的矛盾。但没有一个人把这个矛盾推进到**它实际上是一个合规性漏洞**。

**完整场景**：

样本数据：n=1，值=380mAh，threshold=380mAh

```
sample_ok = (380 >= 380 - 1e-6) = True   # 单样本 ≥ 期望 → Pass
stat_ok   = (380 > 380)             = False  # µ-2σ 不"严格高于" → Fail
```

**PDF §6.2.11 原文**："no single measured sample must have a usable capacity **less than** the specified expected usable capacity" AND "the µ-2σ value ... must be **higher than** the specified usable capacity"。

两个条件都要求报告为"符合"。但代码在此场景下输出 Fail——因为单样本的 µ-2σ = 样本值，严格"高于"要求样本值 > 阈值。这在字面意义上是 PDF 的字面意思，但语义上：
- 若 PDF 意图是"样本代表的质量稳定性足以覆盖到 threshold"，那么 n=1 时，µ-2σ=样本值，样本值=threshold 应该判 Pass
- 若 PDF 意图是"µ-2σ 是一个独立于单样本的统计保证"，那么 n=1 时 µ-2σ 无法提供统计保证，样本值=threshold 判 Fail 是合理的

**PDF 没有明确 n=1 的处理方式，这是设计缺陷，不是实现缺陷。** 但代码选择了"Fail"这一边，而没有在报告里注明"单样本，统计保证不足"。

**为什么其他四人没提**：DeepSeek 提到但标记为"中优先级无建议"；GLM 完全没提；GPT 和我的 Round 1 都只停留在"矛盾"描述，没有追问"这个 Fail 结论对产线意味着什么"。

**实际影响**：CR2450 冷冻型 threshold=280mAh，若实测值恰好是 280mAh（极罕见但可能），所有电池判 Fail。但最小值检查通过了（280 >= 280），用户看到的是一个"似乎合格的电池被统计检查拒绝"的困惑报告。

**修复方向**（两条路二选一）：
- A：在 `statistics_utils.py` 对 n=1 返回 `mu2sigma=None`，`evaluate_expectations` 对 `mu2sigma is None` 输出 `"stat_ok=N/A (single sample)"`，由人判断
- B：在报告 Remarks 里注明"single sample, statistical criterion not applicable"

---

## 四、三个新盲区（其他四人完全没提）

### 盲区 N1：legacy fallback 的 µ-2σ 计算用的是实测最高电流档，而非 PDF 指定档

`report_coordinator.py:178-188` 的 legacy fallback 路径：

```python
if listMM2S[intPosiMaxmA][intPosi2V25] / intQnomCapacity >= intPassRate:
    strResult = "Pass"
```

这里用的是**实测数据中的最高电流档**（`intPosiMaxmA`），而不是 PDF 对该 profile 规定的判定电流。举例：
- Pouch Cell QNOM=2500，PDF 规定 100mA 档，但实测文件只有 30mA 测试
- legacy fallback 用 `listMM2S[30mA index][2.25V]` 判断
- 30mA 档的 µ-2σ 通常远高于 100mA 档（放电更慢，容量更大）
- **结论：legacy fallback 更容易让不合格电池 Pass**

这与 GLM 的发现 B 场景结合——当冷冻三口径不同步导致 verdicts=[] 时，走的是这个偏向宽松的 legacy 路径。GLM 发现了同步问题，但我补充了"即使触发 legacy，它本身也比 PDF 标准宽松"。

### 盲区 N2：PDF 没有规定 µ-2σ 的分母，legacy 路径和 `evaluate_expectations` 用了不同的分母

- `evaluate_expectations`（新路径）：`stat_ok = mu2sigma > threshold_mah`（阈值直接来自 PDF，是 mAh 绝对值）
- legacy fallback（`report_coordinator.py:178`）：`mu2sigma / intQnomCapacity >= intPassRate`（阈值是 required/QNOM 比例）

两个路径用**不同量纲**做判断：新路径比较 mAh 绝对值，legacy 路径比较百分比。当 required ≠ QNOM × 比例时，两条路径对同一数据的判定可能相反。例如：QNOM=3000，ratio=0.85，required=2550。legacy 用 2550/3000=85%；新路径直接用 2550mAh。数值相同，但如果 required 字段被人为改过（见 GPT R2），两条路径会给出不同答案。

### 盲区 N3：测试覆盖了 Hermes 走 legacy 逻辑，但没验证 legacy 结论的正确性

`test_hermes_expectation_outside_levels_uses_legacy_logic` 只验证"触发了 legacy 逻辑"，不验证"legacy 逻辑对 Hermes 来说结论是什么"。若 Hermes 文件只有 30mA 档（没有 500/100mA），legacy 用 30mA 数据判断 Hermes 是否合格——这个结论在工程上是否合理，没有任何测试。

---

## 五、对四人共识区的挑战与回应

**四人共识**：
1. 核心判定公式（双条件、严格大于）实现正确 ✅
2. 2.25V 精确比较风险存在 ✅（四人全认）
3. 冷冻三口径同步问题存在 ✅（GLM B + 我 Round 1 问题 7）

**挑战点**：

- **"构造方法英文匹配"只是中优先级**（GLM E）——我认为应该是高优先级。UI 有 i18n 目录，`locale/` 存在，一旦 UI 推出中文版，所有 Pouch Cell 的构造方法字段将无法匹配，100% 的 Pouch Cell 判定会静默回退到 legacy。不是说"可能"踩雷，而是"只要中文化就必然"踩雷。

- **"Hermes 期望值硬编码"**（GPT R6, GLM F）四人列为低/中——我认为应该提升。§7.1.1.11 的 4 个值（3000/3600/2600/3200）是硬编码常量，没有任何外部配置或其他来源可查。如果 PDF 更新这 4 个值，需要改代码+测试，而没有任何配置文件驱动。这意味着"规则来源的唯一性"（GLM 的核心关切）在这里完全失效。

---

## 六、Round 2 改进优先级（推翻/修正四人排序）

| 优先级 | 项目 | 修正理由 |
|--------|------|----------|
| **P0** | PDF §7.1.1 全表重导出 + QNOM 分档表比对（GLM A + 我的 QNOM 边界） | 唯一系统性源头错误；所有 1200/2000/3000 边界档位的判定都可能错位 |
| **P0** | 冷冻三口径统一 + 兜底路径日志（GLM B + legacy 结论宽松性补充） | 静默降级到错误标准，且 legacy 比 PDF 标准更宽松 |
| **P1** | 2.25V 容差匹配 + 未找到告警（GLM C） | 精确比较 + index 0 默认静默错位 |
| **P1** | 单样本 µ-2σ 语义矛盾（我的 Round 1 问题 3，他人完全忽视） | n=1 且样本值=threshold 时，双条件一个 Pass 一个 Fail，报告无说明 |
| **P1** | Hermes 测试只验证路径不验证结论（盲区 N3） | 当前测试让有缺陷的 legacy 路径变成了"通过测试的正确逻辑" |
| **P2** | 构造方法中文化雷（GLM E，我提升优先级） | i18n 存在时必然踩雷 |
| **P2** | Hermes 期望值外置到配置（GPT R6, GLM F，我提升优先级） | 规则来源唯一性原则在此处完全失效 |
| **P2** | 空样本格误报 Fail（GLM D） | "没测到"报成"不合格" |
| **P3** | 补全 Pouch Cell 自动化测试（我的 Round 1 问题 1） | 防止 build_expectations 回归 |
| **P3** | µ-2σ 计算 ddof 假设（我的 Round 1 问题 9） | 低样本量下偏乐观，登记即可 |

---

## 七、一句话行动项（用户决策点）

1. **必须**：用 pdftotext 重导出 §7.1.1 全表，裁定 `_POUCH_CAPACITY_BANDS` 与 PDF 是否一致，1200–2000 档是否有 PDF 来源
2. **必须**：在 `report_coordinator.py:183` 加 `logger.warning`，Remarks 标注 "legacy single-point judgment used"
3. **建议**：`build_expectations` 增加 `is_freezer` 参数，接受调用方传入的冷冻标识，而非自己重新从 required 字段推断
4. **建议**：单样本场景的 `stat_ok` 返回 None 或在 Remarks 里注明"single sample, statistical criterion not independently verified"


---

## GLM (Round 2): Round 2：以当前代码为基准裁决四方分歧，收敛为 8 步修复清单

# GLM Round 2：挑战、裁决与收敛后的修复清单

Round 2 我做了三件事：重新验证自己 Round 1 的两个核心主张在当前代码中是否仍成立、对 MiniMax 的 9 项和 GPT 的 R4–R9 逐条裁决（该验证的都去仓库验证了）、给出调整后的优先级清单。结论先行：**四位顾问的分歧大部分是"基于不同版本的代码描述"造成的，以当前代码为基准后，真正的争议只剩 PDF 分档表这一个，而它只能靠 pdftotext 重导出裁决。**

## 一、我的 Round 1 两项主张的复核结果

### 1. 纠偏 DeepSeek 🔴2（fallback 丢失最小值检查）——仍成立，且得到 MiniMax 间接印证

本轮重新读 `report_coordinator.py` 当前代码确认：`build_expectations` 返回空时，先构造 legacy `Expectation(最高实测电流, listVoltageLevel[intPosi2V25], intRequiredCapacity, source="legacy")` 交给 `evaluate_expectations`，**双条件都执行**；旧的单条件判定只在 `verdicts` 为空（期望格不在实测档位中）时触发。DeepSeek 的修复建议 #2（"在 fallback 中增加最小值检查"）针对的代码已经不存在，不需要做。

MiniMax 的问题 5 描述的正是当前真实路径（"期望格全部跳过 → verdicts = [] → legacy fallback"），说明他读的是当前代码——这一点上 MiniMax 的基准比 DeepSeek 准。但 MiniMax 对 fallback 的批评（"用 30mA 档数据判 Hermes 是否合格，完全不符合 PDF 意图"）只对了**一半**：该路径的阈值口径是 `intRequiredCapacity`（required 容量），不是 Hermes PDF 的 3000/3600mAh 绝对值，所以确实不合规；但它的存在是有意的安全网（代码注释写明"行为与历史一致"），问题是**静默**——没有 warning、Remarks 也没有标注。所以正确修法不是删掉它，而是让它"出声"。

### 2. 发现 A（Pouch 分档表与 PDF 摘录矛盾）——无人正面回应，仍是第一优先

GPT 把四档表当"已实现"列出，没质疑它与 2026-09-23 会议摘录的矛盾；DeepSeek 完全没碰脉冲档位表；MiniMax 问题 2 触及了，但**引码有误**（见下）。A 项维持原判：代码 `_POUCH_CAPACITY_BANDS`（pulse_currents.py:44-49）与 2026-09-23 黑板摘录（2000–3000 档为 150/100/60/30、≥3000 档为 500/250/100/60/30/15/6 七级、且不存在 1200–2000 档）至少有一份错了。这直接影响 `build_expectations` 取 `currents[0]` 作判定电流，是"格选错 → 全错"型缺陷，必须最先裁决。

## 二、对 MiniMax 9 项的逐条裁决（含代码验证）

**问题 2（QNOM 边界值）——引码错误，但问题本身并入 A。** MiniMax 引用的 `_POUCH_CAPACITY_BANDS` 少抄了一个元组。实际代码是四档：

```
(1200, [30,26,15,6]), (2000, [60,30,15,6]), (3000, [100,60,30,15,6]) + ≥3000: [150,100,60,30,15,6]
```

按"取第一个满足 QNOM < 上限的档"：1200 → [60,30,15,6]（不是 MiniMax 说的第一档）、2000 → [100,60,30,15,6]、3000 → [150,...]。MiniMax 的边界映射结论全部错位。但"PDF 区间是 < 还是 ≤、1200–2000 档是否存在"这个疑问本身有效——它与发现 A 是同一个问题，一次 PDF 重导出同时裁定，不必单列。

**问题 3（单样本 μ-2σ）——确认行为属实，但反对改判定逻辑。** 我验证了 `statistics_utils.py`：`stds = np.where(counts > 1, stds, 0.0)`，n=1 时 std=0、mm2s=mean，于是出现 MiniMax 说的"样本值=380=阈值 → sample_ok=True 但 stat_ok=False → Fail"。**这是 PDF "higher than" 严格语义的正确执行，不是 bug。** 单样本时 μ-2σ 退化为样本值本身，等于要求唯一样本严格大于阈值——数学上无可指摘。务实修法：不改判定，只在 n=1 的格的 Remarks 标注 "single sample, μ-2σ equals the sample value"，消除产线对"自相矛盾"的困惑。降级为观察项。

**问题 5（Hermes 期望格不在实测档）——认同，并入兜底告警修复。** 见上文第一节。与我的 B 场景同根：都是 `verdicts` 为空 → 静默旧单点。合并成一个修复动作。

**问题 9（t 分布替代 1.96σ）——明确反对。** PDF 白纸黑字写 μ-2σ，没写置信区间推断。n=3~5 时 t_{0.975} 在 3.18~4.30 之间，改 t 分布等于把判定区间放宽近一倍，**整批历史判定结果会翻转**，这是无依据地改变验收口径。工程上不可接受。最多在模块 docstring 注明"小样本下 μ-2σ 覆盖率低于 96%"。不采纳。

**问题 8（ε 只加在 sample_ok 不加在 stat_ok）——不修。** 与 DeepSeek 的 ε 语义质疑同源。PDF 对两个条件用了不同措辞（"less than" vs "higher than"），代码的对称差（一边 ≥-ε、一边严格 >）恰好忠实映射了措辞差异。登记即可。

**问题 1（Pouch profile 无测试）——认同，纳入清单。** 6 个 profile 是裸代码路径是事实，且 Pouch 恰好是构造方法/分档两个高风险点的交汇处。测试成本低（照抄现有 Coin Cell 测试的形状），收益高。

**零值安全网观察——认同，且我带回一个让修复更便宜的事实。** 我验证了 `compute_statistics`：`counts` 矩阵在函数内部**已经算出来了**（`counts[i] = np.count_nonzero(~np.isnan(vals))`），只是返回的 dict 里没有它。所以我的发现 D（空样本格误报 Fail）的修复比 Round 1 估计的还便宜：把 `counts` 加进返回 dict、`evaluate_expectations` 接收 stats 后对 counts==0 的期望格跳过并在 Remarks 汇总，改动不到 15 行。MiniMax 提的"mm2s 异常低时提示数据异常"可以作为同一机制的扩展，但先做"跳过+注明"，异常启发式不做。

**问题 4、6、7** 分别与我的 C、E、B 重复，维持原判；问题 7 的"型号不在规则列表"场景是 B 的一个补充复现用例，测试时一起覆盖。

## 三、对 GPT R4–R9 的裁决（含代码验证）

**R4（Reported By 验证不一致）——验证成立，但实际影响比 GPT 说的小，一行修复。** 我确认 `input_validator.py:59-75` 的 `REQUIRED_TEXT_FIELDS`（16 项）确实不含 `reported_by`；但 `main_presenter.py:176` 有 `if not reported_by:` 拦截，`analysis_runner.py:83` 也有兜底。所以运行路径不会漏，只是 `validate_fields()` 的 field_errors 缺这一项、报错信息不完整。修法：REQUIRED_TEXT_FIELDS 加一行。纳入清单，低优先级。

**R7（PULSE_BURSTS / PULSE_STEP_SCHEDULES 未被管线使用）——验证成立。** 全仓库 grep 结果：这两个常量只在 `quality_requirements.py:32-37` 定义、在 `test_quality_requirements.py:52-61` 被断言，分析管线零引用。它们是"文档常量"（把 PDF §7.1.1 的 burst 时序固化成代码），测试断言只防手滑改错。**建议保留但在定义处加一行注释："仅作 PDF 条款文档，不参与判定管线"**——GPT 担心的"本应参与判定而是遗漏"可以排除，因为 §6.2.11 判定不需要 burst 时序，那是测试 profile 生成侧的事。不删（删了要连测试一起删，收益为零）。

**R8（Datasheet Nominal Capacity 不做正整数校验）——成立，顺手修。** `_require_positive_int` 只作用于 ti[17] 和 ti[9]。给 Datasheet 字段加一行同款校验即可。低优先级。

**R9（孤儿型号 → 判定静默跳过）——后果描述需要修正，且这暴露了 GPT Round 1 的一个基准问题。** 当前代码下，`lookup_pulse_currents` 返回空 → `build_expectations` Pouch 分支 `if not currents: return []` → report_coordinator **不会**跳过判定，而是构造 legacy Expectation（最高实测电流 × required 容量）。所以后果不是 GPT 说的"完全没有合格判定输出、Result 列空白"，而是"有输出，但判定格与阈值口径退化为 legacy"——依然不对，但严重度低一档。修法：`build_expectations` 各返回空的分支加 `logger.warning`。**GPT 的 R1"回退在哪里实现"之问，答案就是这里：report_coordinator.py 的 `if not expectations:` 分支，Round 1 时他就没找到的这段代码现在明确存在。**

**R2（Coin Cell 阈值取 UI 字段而非 PDF 常量）——降级为设计观察，不改。** `build_expectations` docstring 明写优先级约定"数据准确 > PDF > 原有行为"，阈值取规则侧 380/280 是有意为之（用户可通过规则覆盖 PDF）。PDF 重导出入库后可加一条一致性提示（required ≠ 280/380 时 warn），但不必强制绑定。

**R6（Hermes 期望值硬编码）——认同，与 PDF 重导出同批做。** 4 个元组外置为模块级常量并附 PDF 页码注释，或迁入规则配置。不必单独排期。

**对 GPT 四级框架的评价**：P0（判定完整性）方向对，但基于修正后的代码事实，"无判定输出"场景已被 legacy Expectation 兜住，P0 的真实内容变成"legacy 兜底何时触发、是否可见"——即告警问题，不是空白问题。P1/P2/P3 保留。

## 四、收敛后的修复清单（替代我 Round 1 的 6 步）

| 序 | 动作 | 来源 | 成本 | 说明 |
|---|------|------|------|------|
| 1 | pdftotext 重导出 §7.1.1 全表，人工比对 `_POUCH_CAPACITY_BANDS`/`_POUCH_LARGE_PULSE_CURRENTS`/`_MODEL_OVERRIDES`/Hermes 4 格，改错项并同步测试；Hermes 参数顺带外置 | 我的 A + MiniMax 问题2 + DeepSeek Hermes 疑问 + GPT R6 | 30–60 分钟 | **唯一能裁决"分档表矛盾"的动作，一箭四雕** |
| 2 | `verdicts` 为空的兜底分支：`logger.warning` + Remarks 标注 "legacy verdict (expected cells not in measured levels)" | 我的 B + MiniMax 问题5 | ~10 行 | 让安全网出声，不改行为 |
| 3 | 2.25V 容差匹配（`abs(x-2.25)<1e-6`），未找到时告警而非默认 index 0 | 我的 C + MiniMax 问题4 + DeepSeek #1 | 5 行 | |
| 4 | `is_freezer` 单一来源：`build_expectations` 加可选参数，由调用方传 data_processor 同口径结果 | 我的 B + MiniMax 问题7 + GPT R5 | ~20 行 | |
| 5 | `compute_statistics` 返回 `counts`（已算好，只需加进 dict）；`evaluate_expectations` 对 counts==0 的期望格跳过并汇总 Remarks | 我的 D + MiniMax 零值安全网 | <15 行 | 比 Round 1 估计更便宜 |
| 6 | 构造方法关键词认中文（"叠片"/"螺旋"） | 我的 E + MiniMax 问题6 | 2 行 | |
| 7 | `reported_by` 加入 REQUIRED_TEXT_FIELDS；Datasheet 容量加正整数校验；`build_expectations` 各空返回分支 + lookup 空时 logger.warning | GPT R4/R8/R9 | 各 1–3 行 | 三个一行修，顺手打包 |
| 8 | 测试：Pouch 各 profile 期望值单测（Spiral/Laminate 各至少一档）+ 端到端"文件名/查表档位不一致 → 验证判定路径与 Remarks 标注"（覆盖 B 与 MiniMax 问题7 场景） | MiniMax 问题1 + 我原第 6 步 | 半天 | 锁死回归 |

**观察项（明确不修，防止过度工程）**：ε 不对称（MiniMax 问题8）、round 银行家舍入（触发概率≈0）、单样本 Remarks 标注（可并入第 5 步顺手做）。

**明确反对/不做**：t 分布改造（MiniMax 问题9，会翻转历史判定口径，无 PDF 依据）、策略类/注册表重构（dict 查表足够，2026-09-23 会议已有结论）、ReportCoordinator 再分层。

## 五、一句话结论

四位顾问 20+ 条发现里，以当前代码为基准去重、验证、裁决后，真正需要改代码的收敛为 8 个动作（其中 4 个是十行以内的小修），唯一的结构性风险仍是 PDF 分档表与摘录的矛盾——**先做第 1 步的 PDF 重导出，它可能让后面几步的优先级重排，也可能全部确认无需改动；在没看到 §7.1.1 原表之前，任何人都不要再基于"记忆中的 PDF"争论档位对错。**

---

## GPT (Round 2): Round 2：裁定争议、纠举引证错误、重建优先级（P0=PDF 事实源仲裁）

# GPT (Round 2): 裁定争议、纠举引证错误、重建优先级

## 〇、方法声明

本轮我读取了全部五条 Round 1 条目，并**实际读码验证了争议点**（`src/battery_analysis/utils/report_coordinator.py:95-205`、`src/battery_analysis/utils/quality_requirements.py:140-250`、`src/battery_analysis/utils/pulse_currents.py:30-110`、`src/battery_analysis/utils/writers/statistics_utils.py:40-90`、`tests/battery_analysis/utils/test_quality_requirements.py`）。以下每个裁定都带代码证据。

---

## 一、裁定一：GLM 对 DeepSeek "fallback 丢最小值检查"的纠偏——**GLM 对，但要三分而不是二分**

读码确认 `report_coordinator.py:166-176`：`build_expectations` 返回空时，当前代码构造 `Expectation(current_ma=最高实测电流, cutoff_v=listVoltageLevel[intPosi2V25], threshold_mah=intRequiredCapacity, source="legacy")` 交给 `evaluate_expectations`，**双条件（① min ≥ 期望；② μ-2σ > 期望）确实都执行**。DeepSeek 高危 #2 按其字面描述已过期，GLM 的纠偏成立。

但我不同意把 #2 简单"部分不成立"带过，正确的裁定是把 fallback 拆成**三段**，每段风险不同：

1. **派生失败 → legacy Expectation（双条件）**：判定形式对，但**语义降级**——阈值从 PDF 口径（380/280 或 QNOM×85%/75%）退化为 UI 字段 `ti[17]`，电流从 PDF 指定档退化为"最高实测电流"。形式合规、内容可偏离，这是 DeepSeek #2 的残余风险，应降级保留而非删除。
2. **期望格不在实测档位 → 旧单点判定（`report_coordinator.py:183-197`）**：确实只剩 `listMM2S[intPosiMaxmA][intPosi2V25] / intQnomCapacity >= intPassRate` 单条件、且**无任何日志**。DeepSeek #2 的精神在此完整存活，GLM 自己也承认（"旧单点路径没有死透"）。**这一段必须修**（加 min 检查 + 告警日志 + Remarks 标注）。
3. **`_require_positive_int(listTestInfo[17])`（`report_coordinator.py:145`）**：required 为 0/空时**直接抛 ValueError**，根本不进入判定——DeepSeek #13 成立，但这属于"输入验证该拦没拦、拖到报告期才炸"，与 GPT R4（验证路径不一致）同根。

**结论**：DeepSeek #2 从"高危缺陷"降级为"残余语义风险 + 第 2 段单条件兜底待修"；但**优先级不应因此后移**，因为第 2 段正是 GLM 场景 B（冷冻口径不同步）的落点——两个问题在同一条代码路径上汇合。

---

## 二、裁定二：GLM 发现 A（Pouch 分档表 vs PDF 摘录）——**升级为全局第一优先级，并纠举 MiniMax 的引证错误**

我读码核实 `_POUCH_CAPACITY_BANDS`（`pulse_currents.py:36-43`）实际为：

```python
_POUCH_CAPACITY_BANDS = (
    (1200, [30, 26, 15, 6]),
    (2000, [60, 30, 15, 6]),
    (3000, [100, 60, 30, 15, 6]),
)
_POUCH_LARGE_PULSE_CURRENTS = [150, 100, 60, 30, 15, 6]
_MODEL_OVERRIDES = (("583083", [500, 250, 100, 50, 25]),)
```

**GLM 对代码的描述准确。MiniMax 的引证是错的**：MiniMax 问题 2 把 `_POUCH_CAPACITY_BANDS` 引作 `(1200,[30,26,15,6]), (2000,[100,60,30,15,6]), (3000,[150,100,60,30,15,6])`——**整体错位一档**（把 2000 档写成 100 顶档、3000 档写成 150 顶档）。其"边界值落在哪档"的分析建立在错误的表上。不过**边界问题本身仍然成立**，且比 MiniMax 想的更尖锐：代码语义是"取第一个满足 `QNOM < 上限` 的档"（`pulse_currents.py:35` 注释），即 QNOM=1200 → **60mA 顶档**、QNOM=2000 → 100mA 顶档、QNOM=3000 → 150mA 顶档——区间实际是 [0,1200)/[1200,2000)/[2000,3000)/[3000,∞)。PDF 究竟写 `≤` 还是 `<` 必须在仲裁时一并裁定。

对 GLM 发现 A 我做三点修正与强化：

1. **证据链要诚实标注为"二手"**。GLM 的"PDF 摘录"来自 2026-09-23 会议黑板（`.pi-meetings/2026-09-23-pulse_currents_逻辑分析与优化/blackboard.md:557-630`），不是 PDF 本身。修复措辞应是"**裁定哪份记录正确**"而不是"改错项"——GLM 修复动作的措辞已预设代码错了，这不中立。
2. **摘录自身有内伤，代码有内部一致性佐证**。摘录说 CF583083 属于 "CP305050/CF583083 等 — 100/60/30/15/6" 组，但同一摘录体系里 §7.1.1.11 的 Hermes 期望格是 (500,2.25)/(100,2.25)/(500,2.5)/(100,2.5)——**500mA 格根本不在 100/60/30/15/6 里**。而代码侧 `_MODEL_OVERRIDES`（500/250/100/50/25）与 Hermes 期望格（500/100）**互相自洽**。这降低了"代码全错"的概率、提高了"摘录某行串档"的概率——但**不能替代 PDF 原文**，这正是必须重导出的理由。
3. **A 与 Hermes 之争是同一个根因**。DeepSeek #5（Hermes 只验 4 格）与 MiniMax 问题 5（Hermes 档位不匹配静默走 legacy）表面上是"覆盖度"问题，实际上都悬在"583083 到底是什么档位表"这一个事实之上。**四人共识区里的"Hermes"不应单列，应并入 A 的仲裁包**。

**结论：A 升级为 P0**——它是唯一可能"判定格系统性选错"的硬伤，且修复成本最低（pdftotext 导出 + 人工比对 + fixture 入库，半小时）。所有"补测试"类建议都必须排在它后面，否则 golden test 会把可能错误的表**固化**下来。

---

## 三、对四人共识区的逐项裁定（同意 / 升级 / 降级）

| 共识项 | 我的裁定 | 理由 |
|---|---|---|
| Pouch 分档表仲裁（A） | **升级 → P0** | 唯一系统性错格风险，成本最低，且是 Hermes 争议的根因 |
| 2.25V 静默错位（C） | **维持 P0/P1** | 读码确认 `report_coordinator.py:104-108` 精确 `==` + 默认 0；且 legacy Expectation 的 `cutoff_v` 会"成功匹配"index 0（如 2.6V）→ 报告表面正常、判错电压。5 行改动，收益极高 |
| 冷冻三口径不同步（B） | **升级 → P1 前列** | GLM 的复现场景（文件名 freezer + required=380 → 30mA 期望不在实测 [15,13,7.5,3] → verdicts 空 → 旧单点兜底）逻辑链我逐步读码验证成立，且落点就是裁定一里的"第 2 段"缺陷 |
| Pouch 构造识别（E/DeepSeek #10） | 维持 P2 | 后果同样是掉进 legacy，但触发面窄（需用户自定义中文构造名）；2 行改动顺手做 |
| Hermes | **并入 A 仲裁包**，不单列 | 见裁定二第 3 点 |
| 端到端测试 | **降级为仲裁后的动作** | 在分档表存疑时写 e2e 是"把错误刻进回归"；正确顺序是 P0 裁定 → golden fixtures（从 PDF 派生而非从代码常量抄）→ e2e 锁路径 |
| 空样本格（GLM D vs MiniMax 零值安全网） | **升级 → P1，但两人都只对一半** | 见裁定四 |

---

## 四、裁定四：空样本格——MiniMax 与 GLM 直接冲突，两人各遗漏一半，需要合成

- **MiniMax**（问题 3 / 零值安全网）：空格 mm2s=0 → `sample_ok=False`、`stat_ok=False` → Fail，"这是正确的安全网行为"。
- **GLM**（发现 D）：这是"把没测到报成不合格"，产线误报，应跳过并注明。

读码确认双方事实都对、结论都偏：`statistics_utils.py:53-59` 空格全 0.0，`statistics_utils.py:62-69` **`counts` 确实已计算但未输出**（GLM 说得准）；`evaluate_expectations` 只读 `min`/`mm2s`，不看样本数。

**我不同意 GLM 的修复方案原样落地**，因为它埋了一个两人**都没看到的聚合风险**：如果按 D 方案"对 `counts==0` 的期望格跳过"，而 `report_coordinator.py:181` 的聚合是 `all(v.passed for v in verdicts)`——**被跳过的格从聚合里消失，剩下的全 Pass 就输出 Pass**。也就是说 D 方案会把"误报 Fail"翻转成"漏报 Pass"，后者对质量门是**更危险**的方向。且若所有期望格都空，`verdicts=[]` 会掉进旧单点判定（mm2s=0 → Fail），行为又跳回误报——同一个修复在不同情形下两个方向都错。

**改进方案（三态判定，我的原创补充）**：
1. `compute_statistics` 输出 `counts` 矩阵（已有计算，只差放进返回字典）；
2. `evaluate_expectations` 对 `counts==0` 的期望格产出第三种状态 `NoData`（既不是 Pass 也不是 Fail）；
3. 聚合规则改为：存在 `NoData` 格 → 整批结果为 **"Incomplete / 需复测"**（绝不允许聚合成 Pass），Remarks 列明缺哪个 (电流,电压) 格；无 NoData 时才按 `all(passed)` 判 Pass/Fail；
4. 真实低值（counts>0 但 mm2s 极低）保持 Fail，可附加 MiniMax 建议的"数据异常"提示。

这样 MiniMax 的"零值不能误 Pass"与 GLM 的"没测到不能报 Fail"同时满足。

---

## 五、逐条挑战：我不同意或认为遗漏的点

**1. 挑战 DeepSeek 修复建议 #4（is_freezer 改从温度字段 ti[7] 推断）——不采纳。**
DeepSeek 建议 `is_freezer = "freezer" in str(ti[7]) or float(ti[7]) < 0`。这是**用一个启发式换掉另一个启发式，且语义更错**："Freezer 型"是**产品规格**（CR2450 Freezer 型，要求 280mAh），不是**测试工况**——常温型电池做低温测试时 ti[7] 可能是负温，按此修法会把常温型误判为冷冻型、把期望从 380 错拉到 280。规则第 5 段 280/380 本来就是产品规格的权威标记。正确方向是 **GLM 的修法**：`build_expectations` 增加 `is_freezer` 参数，由调用方用与 `data_processor.py:344` **同一个**判定函数（文件名 OR 规则）传入，消除三口径而非换第四口径。

**2. 挑战 MiniMax 问题 1（"§7.1.1.3–.10 Pouch profile 全部缺失测试"）——言过其实。**
读 `tests/battery_analysis/utils/test_quality_requirements.py:69-141`：`test_pouch_spiral_uses_85_percent`、`test_pouch_laminate_uses_75_percent`、`construction=""` 返回 `[]` 等用例都在，`test_config_migration.py:109-121` 还固化了 920×85%=782 / 2000×75%=1500 等换算。**`build_expectations` 层的 Pouch 派生是有测试的**。真正缺的是：(a) 跨 QNOM 分档边界（1200/2000/3000）的档位选择测试；(b) 判定结果写入报告的集成路径（GPT R10 的缝隙，这点 MiniMax 和我一致）。请勿按"6 个裸代码路径"的描述排工作量。

**3. 挑战 MiniMax 问题 9（改用 t 分布）——明确反对。**
合规审计的标尺是 **PDF 写什么就实现什么**。§6.2.11 明文是 "µ - 2σ"，改成 `t_{0.975,n-1}` 是用统计洁癖替换文档合规，反而制造"代码与 PDF 不一致"的新缺陷。小样本下 2σ 偏乐观这一点值得**写进报告说明或会议纪要**（供 PDF 修订委员会参考），但不进代码。

**4. 降级 DeepSeek #7/#8/#14（ε 语义、banker's rounding、百分比 floor）——同意 GLM "登记即可"。**
触发需要 mAh 恰好落在 0.5 或 1e-6 边界上，实测数据是整数/一位小数，成本远超收益。维持"登记、不动代码"。唯一例外：给 `_MIN_EPSILON` 补一句注释说明"浮点补偿而非语义放宽"（DeepSeek 原建议的后半句），0 成本。

**5. 挑战 GLM 的修复顺序表第 6 行（e2e 半天）——顺序对、时机错。**
如上，e2e 必须在 PDF 仲裁之后，用**从 PDF 派生的 fixture**写断言。GLM 第 1 行（仲裁）与第 6 行（e2e）之间还缺一步：**golden fixtures 入库**（GPT R10/四、2 的长期策略），否则下次 PDF 升 v2.4 还要重新人肉比对。

**6. 补一个四人都漏掉的验证缺口：`build_expectations` 的 QNOM 基数歧义（GLM F.2 提了但排太低）。**
代码用 `ti[9]`（report_coordinator 称其为 "Calculated Capacity"）× 85%/75%；而 `required_useable_capacity_from_rule` 用规则第 4 段。PDF 原文是 "QNOM × 85%"——**QNOM 在电芯行业通常指 Datasheet Nominal（ti[8]）**。若 PDF 本意是标称容量，全体 Pouch 阈值系统性偏差（CR2450 规则里 600/550 两者不同，偏差可见）。这不是"确认一下"的小项，**必须并入 P0 仲裁包**，与分档表一次性裁定。

**7. 补一个验证路径缺口（GPT R2 的具体化）：Coin 阈值越界无守卫。**
`build_expectations` 对 Coin Cell 直接用 `required`（ti[17]）做阈值，无任何约束。低成本守卫：当 `classify_spec=="Coin Cell"` 且 `required not in (280, 380)` 时 `logger.warning` + 报告 Remarks 注明"阈值偏离 PDF 标准值"。保持灵活性但让偏离可见。

---

## 六、我改进后的优先级（取代 GLM 六步表）

| 序 | 动作 | 涉及 | 成本 | 为什么在这个位置 |
|---|---|---|---|---|
| **P0** | **PDF 事实源仲裁包**：pdftotext 重导出 §7.1.1 全表，一次裁定 4 件事：① `_POUCH_CAPACITY_BANDS` 四档位与区间开闭（1200/2000/3000 归属）；② `_MODEL_OVERRIDES` 583083 档位 + Hermes 期望格是否 4 格；③ QNOM = ti[8] 标称还是 ti[9] 计算容量；④ 结果固化为 fixtures 入库（`tests/…/fixtures/`），三处口径收敛为一处 | pulse_currents.py / quality_requirements.py / 测试 | 半天 | 唯一能系统性推翻"判定格选错"的硬伤；Hermes、分档、QNOM 三争议同根；不裁定就写测试=固化错误 |
| **P1** | 2.25V 容差匹配（`abs(x-2.25)<1e-6`，与 `_match_index` 同口径）+ 未找到时 `logger.warning` + Remarks 标注 | report_coordinator.py:104-108 | 5 行 | 静默错电压、报告表面正常，典型"看起来对其实错" |
| **P2** | is_freezer 单一来源（GLM 修法：参数传入 + 与 data_processor 同函数）；**拒绝 DeepSeek 温度修法**；同时给 `report_coordinator.py:183` 旧单点分支加 min 检查 + `logger.warning` + Remarks "legacy verdict" | quality_requirements.py / report_coordinator.py | ~20 行 | 修掉 B 场景的静默降级落点，与裁定一第 2 段同路径合并修 |
| **P3** | 空样本格**三态判定**（NoData → 整批 Incomplete，绝不聚合成 Pass）：`compute_statistics` 输出 counts（已计算未输出）→ `evaluate_expectations` 增加第三态 → 聚合规则改写 | statistics_utils.py / quality_requirements.py / report_coordinator.py | ~25 行 | 比 GLM D 多 10 行，堵住"跳格→漏报 Pass"的反向风险 |
| **P4** | 构造方法中文关键词（"叠片"/"螺旋"）；Coin 阈值越界 warning；`_MIN_EPSILON` 注释 | quality_requirements.py | 5 行 | 顺手防御 |
| **P5** | Golden fixtures + e2e：Excel→提取→派生→判定→报告写入全链路断言，覆盖 QNOM 边界值、freezer 不同步场景、Hermes 档位不匹配场景 | tests/e2e | 半天 | 必须用 P0 裁定后的 fixture 写 |
| **登记不动** | ε 语义、banker's rounding、百分比 floor、t 分布讨论、PULSE_BURSTS 用途确认 | — | — | 见挑战 3/4 |

**不做的**（同意 GLM）：策略类/注册表架构、ReportCoordinator 再抽层——数据正确性问题用结构重构治不了。

---

## 七、一句话结论

四人共识区方向正确但排序错位：**"补测试"被高估、"定事实"被低估**。真正的第一优先级不是任何一行代码，而是把 §7.1.1 的规则事实从"三处互相矛盾的口径"收敛为一处权威源（P0）；代码侧最危险的三个点是 2.25V 静默错位、冷冻口径分叉掉进无日志的旧单点判定、以及 GLM 修复方案 D 自带的"跳格→漏报 Pass"反向风险。DeepSeek #2 按 GLM 纠偏降级但不删除；MiniMax 的分档表引证错误和"Pouch 无测试"结论应纠正；t 分布、rounding 类洁癖项不进代码。

---

## DeepSeek (Round 2): 认领纠偏、复核争议点并重构优先级：三处"格选错"是同一根因

# DeepSeek (Round 2): 认领纠偏、复核争议点、重构优先级

## 〇、方法说明

Round 2 我以**当前代码为准**重新读取了争议点的全部相关行：`report_coordinator.py:90-220`、`quality_requirements.py:1-273`、`pulse_currents.py:1-210`、`statistics_utils.py:39-106`、`tests/battery_analysis/utils/test_quality_requirements.py`、`tests/battery_analysis/e2e/test_new_model_analysis.py`，以及 2026-09-23 会议黑板的 PDF 摘录（`.pi-meetings/2026-09-23-pulse_currents_逻辑分析与优化/blackboard.md:557-630`）。以下每条结论都附验证依据。

---

## 一、对 GLM 纠偏的正式回应：🔴2 认错 + 缩范围保留

### 1.1 GLM 的纠偏准确，我认错（针对主路径）

我 Round 1 的 🔴2 断言"`report_coordinator.py:173-183` fallback 只查 μ-2σ、丢最小值检查"。**以当前代码验证，GLM 说得对，主路径已不成立**：

`report_coordinator.py:167-175`（实测确认）：
```python
expectations = build_expectations(listTestInfo)
if not expectations:
    expectations = [
        Expectation(
            current_ma=float(listCurrentLevel[intPosiMaxmA]),
            cutoff_v=float(listVoltageLevel[intPosi2V25]),
            threshold_mah=float(intRequiredCapacity),
            source="legacy",
        )
    ]
verdicts = evaluate_expectations(stats, listCurrentLevel, listVoltageLevel, expectations)
```
`build_expectations` 返回 `[]` 时，现在构造一个 legacy 期望格交给 `evaluate_expectations`，而后者（`quality_requirements.py:224-246`）严格执行**双条件**（`sample_ok = minimum >= threshold - 1e-6` 且 `stat_ok = mu2sigma > threshold`）。我 Round 1 描述的是过期代码形态，排优先级时不应再以它为据。**GLM 的纠偏完全成立，我收回"fallback 丢最小值检查"作为高危主项的定性。**

### 1.2 但单条件旧判定没有死透——缩小范围后仍然成立

`report_coordinator.py:181-193`（实测确认）存在**第二级 fallback**：
```python
else:
    # 期望格不在实测档位中：保留原有单点判定（安全网，行为与历史一致）
    if listMM2S[intPosiMaxmA][intPosi2V25] / intQnomCapacity >= intPassRate:
```
触发条件是 `evaluate_expectations` 返回空——即 `build_expectations` 非空、但期望格**都不在实测档位里**（`quality_requirements.py:224-226` 对 `c is None or v is None` 静默 `continue`）。这条路径：
- **只有单条件**（μ-2σ/QNOM ≥ pass_rate），最小值检查确实丢失；
- 阈值口径是 required/calculated，不是 PDF 绝对值；
- **无任何日志或 Remarks 标注**走了兜底。

而它有三个已被本轮会议确认的现实触发器：
1. **Hermes 档位错配**（MiniMax 问题 5）：实测文件是 30mA 档而期望是 500/100mA → 四格全跳过 → 用 30mA 档数据下 Hermes 结论；
2. **冷冻三口径不同步**（GLM 发现 B）：数据侧按 15/13/7.5/3 跑，`build_expectations` 派生 30mA 期望 → 不匹配 → 兜底；
3. **Pouch 分档表错位**（GLM 发现 A）：档位表错 → 判定电流错 → 不匹配 → 兜底。

**结论**：🔴2 应改写为"单条件兜底在期望格错配时静默生效"——它不再是'空期望就丢最小值'，而是'格错配就丢最小值'。GLM B 中给出的修复方向（兜底分支加 `logger.warning` + Remarks 注明 "legacy verdict"）我完全赞同，并建议追加：兜底也补上最小值检查（`stats["min"][intPosiMaxmA][intPosi2V25] >= intRequiredCapacity`），彻底消灭单条件判定。

---

## 二、逐条复核争议点

### 2.1 我的 🔴1（2.25V 精确比较）：仍成立，且后果比 Round 1 描述更隐蔽

实测确认 `report_coordinator.py:104-108` 仍是 `if listVoltageLevel[v] == 2.25:` 精确比较 + 未找到时 `intPosi2V25` 静默保持 0。**GLM 发现 C 准确，我补充一个连 GLM 都没说透的放大效应**：

由于 167-175 行的 legacy 期望格直接取 `cutoff_v=float(listVoltageLevel[intPosi2V25])`，当 2.25V 未匹配、`intPosi2V25=0`（如 2.6V）时，这个期望格的 cutoff_v 就是 2.6V，`_match_index`（1e-6 容差）会**成功匹配到 index 0**——于是 `verdicts` 非空、报告"正常"产出 Pass/Fail，**双条件判定完整执行了，但判的是 2.6V 格**。也就是说错电压不只是走老 fallback 的问题，连"新"的双条件路径也会静默判错格。这是全链路里最难被发现的误判：无异常、无空值、无日志。维持 P1（5 行改动：`abs(float(...) - 2.25) < 1e-6` + 未找到 `logger.warning` + Remarks 标注）。

### 2.2 GLM 发现 A（Pouch 分档表与 PDF 摘录矛盾）：复核成立，并补一条"摘录自相矛盾"的新证据

代码侧（`pulse_currents.py:46-58`，实测确认）：
- `_POUCH_CAPACITY_BANDS = ((1200, [30, 26, 15, 6]), (2000, [60, 30, 15, 6]), (3000, [100, 60, 30, 15, 6]))`
- `_POUCH_LARGE_PULSE_CURRENTS = [150, 100, 60, 30, 15, 6]`
- `_MODEL_OVERRIDES = (("583083", [500, 250, 100, 50, 25]),)`

摘录侧（blackboard.md:570-607，实测确认 GLM 转述准确）：
- `< 1200`：30/26/15/6（一致）；
- `2000 ≤ QNOM < 3000`：**150/100/60/30**（代码此档是 100/60/30/15/6）；
- `≥ 3000`：**500/250/100/60/30/15/6**（代码是 150/100/60/30/15/6）；
- 摘录**无 1200–2000 档**，代码却有 60/30/15/6；
- 摘录把 CF583083 归入 "CP305050/CF583083 等 — 100/60/30/15/6"，代码 override 是 500/250/100/50/25。

**我的新证据（GLM 未发现）**：摘录自身也前后矛盾——同一份 blackboard.md:735 的文件名示例写的是 `CF583083(500-250-100-60-30-15-6mA,4000mAh)`（7 级、无 50/25mA），与 blackboard.md:594 的 "CP305050/CF583083 等" 分组表（100/60/30/15/6）**互相冲突**，也与代码 override（500/250/100/50/25）三方不一致。这证明"两份记录至少一份错"低估了——**是三份互不一致**，唯一出路就是 GLM 说的 pdftotext 重导出 §7.1.1 全表入库为 fixtures，把口径收敛为一处。

**再补一个 GLM 没提的系统性后果**：现有测试把矛盾口径**钉死**了。`tests/battery_analysis/utils/test_quality_requirements.py:87-91` 的 `test_pouch_band_2000_to_3000` 断言 2000mAh → 最高档 100mA（即代码口径），`test_pulse_currents.py:127-137` 同样固化分档表。若 PDF 重导出后证明摘录才对，**当前测试会阻止修复**（回归钉钉错了值）。所以 P0 的动作必须是"PDF 导出 → 改 `_POUCH_CAPACITY_BANDS`/`_MODEL_OVERRIDES` → 同步改测试断言"三步原子完成，不能只改代码。测试全绿 ≠ 符合 PDF——这是本轮最值得记住的教训。

### 2.3 MiniMax 单样本 µ-2σ"矛盾"：数学对、定性错，应改名为"报告误导 + 统计退化"

MiniMax 问题 3 的算术我复核过，与 `statistics_utils.py:76,83` 一致（`stds = np.where(counts > 1, stds, 0.0)` → n=1 时 σ=0，μ-2σ=mean）。但我不同意"矛盾"这个定性：

1. **不是逻辑矛盾**。PDF §6.2.11 要求两个条件**同时**成立：无样本低于期望、μ-2σ **严格高于**期望。单样本 380=阈值 380 时 `sample_ok=True` 且 `stat_ok=False` → Fail，是 PDF 字面语义的**正确**执行——"所有样本不低于"与"μ-2σ 高于"本来就是两个独立门槛，一过一不过不构成矛盾。若按 MiniMax 暗示的"单样本放行"，等于对 n=1 数据免检统计条件，那才是偏离 PDF。
2. **真正的问题是报告误导**：Remarks 输出 "μ-2σ … not higher than expected" 时用户看到的是"我唯一一个样本明明合格"。应在 n=1 时追加说明（"single sample: μ-2σ equals sample value; σ has no discriminating power"），或在报表标注 `insufficient samples (n=1)`。
3. **真正的问题之二是统计退化被掩盖**：`np.where(counts > 1, stds, 0.0)` 把"σ 不可估"伪装成"σ=0"。这与 GLM 发现 D（n=0 → min=0 → 误报 Fail "minimum 0mAh"）是同一个根因——**compute_statistics 算了 counts 却不输出**（实测确认输出 dict 只含 mean/med/std/mm3s/mm2s/mp2s/mp3s/min/max），下游无法区分"n=0 没测到 / n=1 不可估 / n≥2 正常"。统一修复：输出 counts，`evaluate_expectations` 引入三态（见 §3）。

**顺带反驳 MiniMax 问题 9（t 分布替代 2σ）**：不同意。PDF 写死 "µ-2σ"，用 t 分位数是**改标准**不是修 bug，合规审计的基准就是纸面条文。最多在文档里记"小样本下 2σ 偏乐观"作为已知局限，动它反而制造"与 PDF 不符"的新缺陷。

### 2.4 MiniMax 问题 2（分档边界）：引错代码，结论作废一半

MiniMax 引用的 `_POUCH_CAPACITY_BANDS = ((1200,[30,26,15,6]), (2000,[100,60,30,15,6]), (3000,[150,100,60,30,15,6]))` **与实际代码不符**（实际第二档是 `[60,30,15,6]`，第三档是 `[100,60,30,15,6]`，各错一档）。据此推出的"1200 → 第一档 30mA"也是错的：`lookup_pulse_currents` 用严格 `<`（`if capacity_mah < upper_limit`），1200 不小于 1200，落第二档 **60mA**；2000 → 第三档 100mA；3000 → 大容量档 150mA。**不过**"< 还是 ≤"的区间语义问题本身成立，且与 GLM A 的分档矛盾合并处理——P0 的 PDF 重导出顺带裁定边界开闭。

### 2.5 MiniMax 问题 1（"Pouch profile 全部裸代码无测试"）：不实

实测反驳：`tests/battery_analysis/utils/test_quality_requirements.py:69-91` 已覆盖 Pouch 螺旋 85%（920→782）、叠片 75%（920→690）、2000-3000 档、构造未知返回空；`tests/battery_analysis/e2e/test_new_model_analysis.py:235-265` 又有 `test_new_pouch_expectation_at_pdf_cell`、`test_pouch_expectation_derives_from_qnom_even_without_required` 等端到端用例。"9 个 profile 只有 3 个有测试"不成立。**但**如 §2.2 所述，这些测试钉的是可能错误的档位口径——真实风险不是"没测试"，而是"测试把错的钉住了"。

### 2.6 对 GPT 的两处异议

- **R1（构造未知 → Result 列空白）：过虑**。`report_coordinator.py:167-175` 的 legacy 双条件兜底保证了 Result 列总有内容；唯一无输出的路径是 `_require_positive_int`（`report_coordinator.py:149-150`）抛 ValueError，而那是带字段名的显式报错弹窗（fail-fast，符合设计）。R1 的"合规空洞"应降级为"口径偏差"（阈值=required 而非 PDF 派生值），不是空白输出。
- **R2（Coin 阈值被 UI 覆盖）：半成立**。阈值取 `ti[17]` 确实可被 UI 改写，但该字段由规则自动填充且空值会显式抛错，不是静默口子。降为低优先级配置面问题。

### 2.7 对 GLM 发现 D 修复方案的挑战：跳过 ≠ 安全，可能把"缺数据"放成 Pass

GLM 建议"`counts==0` 的期望格跳过并汇总到 Remarks"。**这个修法有新缺陷**：Hermes 4 格中若 2.5V 格整格无数据、其余 3 格全过，跳过后 `all(v.passed)` 为真 → **报告 Pass，而 PDF 要求的判定格根本没测**。对质量门禁而言，"没测到"绝不能升格为"合格"。正确语义是**三态**：
- n=0（缺数据）→ 结果不得为 Pass，置 "Incomplete / Fail(missing data at …)" 并在 Remarks 点名；
- n=1 → 按 PDF 字面判定（保持现状），但注明 σ 无判别力；
- n≥2 → 现行双条件。

也就是说 GLM 的"跳过"应改为"标记 + 否决 Pass"。这一条我列为 P3 必改项。

---

## 三、系统视角的新发现：三个 bug 是一个根因

把 GLM A/B/C 摆在一起看，它们不是三个独立缺陷，而是**同一个结构问题的三个症状**："该判哪个格"由三处各自独立解析，且用三套不同匹配规则：

| 解析点 | 位置 | 匹配规则 |
|---|---|---|
| 数据侧（测哪些档） | `data_processor.py:344` 文件名解析 + `lookup_pulse_currents` 查表 | 文件名 ±5% 容差匹配，优先于查表 |
| 期望侧（判哪些格） | `build_expectations`（quality_requirements.py:152-186） | 内部派生 + `_match_index` 1e-6 容差 |
| 报告侧（legacy 格） | `report_coordinator.py:104-108` | `== 2.25` 精确比较 |

三者任意两不同步，就产生"格选错 → μ-2σ 取错格 → Pass/Fail 整体错位"，而三者**没有任何交叉校验**。GLM A（分档表错）错在期望侧，B（冷冻口径）错在数据侧与期望侧之间，C（2.25V）错在报告侧——修完 A、B、C 之后，第四种错配（如未来新增 profile）仍会以同样方式复发。

**结构性建议（不阻塞本轮修复，作为长期方向）**：抽一个唯一的"判定格解析层"——输入 (spec, construction, qnom, is_freezer, spec_method, 实测档位)，输出带来源标注的 (current_index, voltage_index, threshold)，数据采集、期望派生、报告判定三方只消费它的结果并断言一致，不一致时显式报错而非静默兜底。这与 GPT R5 的"统一 FreezerContext"、R10 的"集成缝隙"是同一方向，但范围更准：要统一的不只是冷冻标志，是**整个格选择过程**。

---

## 四、改进后的优先级排序（P0–P5）

| 序 | 动作 | 依据 | 成本 | 备注 |
|---|---|---|---|---|
| **P0** | pdftotext 重导出 §7.1.1 全表 → 裁定 `_POUCH_CAPACITY_BANDS`/`_POUCH_LARGE_PULSE_CURRENTS`/`_MODEL_OVERRIDES` 矛盾（含 583083 三方不一致、1200–2000 档存废、区间开闭）→ **同步改测试断言** | GLM A + §2.2/2.4 新证据 | 1h | 唯一能推翻"判定格选错"的硬伤；测试钉错值必须同批改 |
| **P1** | 2.25V 容差匹配 + 未找到告警 + Remarks 标注 | 我的 🔴1（仍成立）+ GLM C + §2.1 放大效应 | 5 行 | 错电压误判连双条件路径都会静默发生 |
| **P2** | 冷冻单一来源（统一 helper，而非 GLM 提议的多调用点传参）+ 183 行兜底补最小值检查 + `logger.warning`/Remarks "legacy verdict" | GLM B + 收窄后的 🔴2 + MiniMax 问题 5 | ~25 行 | 传参方案在 3 个调用点各自传错就复发，建议 `build_expectations` 内部调用与 data_processor 同一个 `is_freezer_context()` |
| **P3** | `compute_statistics` 输出 counts → `evaluate_expectations` 三态：n=0 标记并否决 Pass、n=1 保留 PDF 判定加 σ 说明 | GLM D（修正其跳过语义）+ MiniMax 问题 3 + 我的 #6 | ~20 行 | "缺数据"不能升格 Pass |
| **P4** | 构造方法中英文关键词（"叠片/螺旋"）+ QNOM 基数裁定（ti[9] 计算容量 vs ti[8] 标称，PDF 写 "QNOM"） | GLM E/F2 | 2 行 + P0 顺带 | QNOM 基数并入 P0 的 PDF 复核 |
| **P5** | e2e 回归：文件名/查表错配 + Hermes 档位不匹配场景，断言走哪条判定路径且报告有 "legacy verdict" 标注 | GLM 第 6 步 + GPT R10 | 半天 | 把 B/C 场景锁死 |

**不做的**（同意 GLM）：策略类/注册表架构重构、再抽一层 verdict 计算。但 §3 的"判定格解析层"建议列入长期路线图，它是 A/B/C 的共同疫苗。

---

## 五、遗留风险与需用户裁决事项

1. **PDF 正文仍不可机读**（GLM 前置声明属实），本会议所有"PDF 规则"均为二手来源。P0 的 pdftotext 导出是硬性前置，导出结果应入库为 fixtures，终结"三处口径"。
2. P0 裁定结果可能推翻现行测试与部分历史报告的判定结论——若历史报告基于错档位表产出，是否需要回溯重跑，需用户决策。
3. Hermes §7.1.1.11 是否仅 4 个判定格（我的 Round 1 疑问）仍待 PDF 复核，一并在 P0 解决。

## 六、一句话结论

GLM 对 🔴2 的纠偏准确（已亲自验证 report_coordinator.py:166-176 的 legacy 双条件构造），我认错；但 183 行的单条件兜底在 Hermes/冷冻/分档三种错配下仍会静默激活，🔴2 收窄保留；🔴1（2.25V）经验证仍成立且比原述更隐蔽；GLM A 成立并有"摘录自相矛盾"新证据，维持 P0；MiniMax 的分档表引文与"Pouch 无测试"两项不实、单样本 µ-2σ 应改称报告误导而非逻辑矛盾；GLM 的"跳过空样本格"修法会把缺数据放成 Pass，必须改三态。三个高危项（A/B/C）同根同源——"判定格解析"散落三处且互不校验，先修数据正确性，长期收敛为单一解析层。


---

## GLM (Round 3): GLM Final：收敛修复清单（P0–P5）、放弃立场声明与 PDF v2.3 合规总体结论

# GLM（Round 3 / FINAL）：收敛后的最终修复清单与合规结论

## 〇、本轮方法声明

我重读了黑板全部 9 条条目（Round 1 全部、User 反馈、Round 2 全部）。Round 3 我只做三件事：认账（我被说服的立场明确放弃）、裁决（遗留分歧给出合并方案）、收敛（一份可直接执行的清单）。

## 一、我明确放弃/修正的立场（吸收他人正确观点）

1. **放弃发现 D 的"跳过空样本格"方案。** GPT（裁定四）和 DeepSeek（§2.7）指出的反向风险成立：跳过 `counts==0` 的格后，`report_coordinator.py:181` 的 `all(v.passed for v in verdicts)` 聚合会让"剩下的全 Pass"输出整批 Pass——把误报 Fail 翻转成漏报 Pass，对质量门禁是更危险的方向。我原方案在"部分格缺数据"和"全部格缺数据"两种情形下会朝两个相反方向出错。**采纳三态判定**：n=0 → 第三态 NoData，整批结果置 "Incomplete / 需复测"，绝不聚合成 Pass，Remarks 点名缺失的 (电流,电压) 格；n=1 → 保持 PDF 字面判定（Fail 就是 Fail），但 Remarks 注明 "single sample: σ has no discriminating power"；n≥2 → 现行双条件。
2. **接受 DeepSeek 对我 is_freezer 修法的改进。** 我 Round 1 提议 `build_expectations` 增加可选参数、由各调用方传入；DeepSeek 指出 3 个调用点（report_coordinator / excel_report_writer / word 侧）各自传错就复发。**合并方案**：抽一个共享 helper（如 `is_freezer_context(spec_name, filename, rules)`，内部即文件名 OR 规则第 5 段=280 的现行逻辑），`data_processor.py:344` 与 `build_expectations` **内部调用同一个函数**——这同时满足 GPT 的核心诉求（拒绝 DeepSeek Round 1 的温度启发式；"Freezer 型"是产品规格不是测试工况）和 DeepSeek 的安全诉求（单一实现、无传参失误面）。GPT 与 DeepSeek 的分歧本质是"参数传入 vs 内部调用"，两者都反对温度推断，合并后无实质冲突。
3. **接受 GPT 对我 e2e 时机安排的批评。** 我 Round 1 第 6 步"补 e2e 半天"顺序对、时机错：在分档表存疑时写 e2e 等于把可能错误的口径刻进回归。e2e 必须排在 P0 仲裁与 golden fixtures 之后，且断言要从 PDF 派生的 fixture 写，不从代码常量抄。
4. **接受 DeepSeek 的"测试钉死错误值"教训。** `test_quality_requirements.py:87-91`（test_pouch_band_2000_to_3000 断言 100mA 顶档）、`test_pulse_currents.py:127-137` 固化的是**待裁定**的口径。P0 必须三步原子完成：PDF 导出 → 改 `_POUCH_CAPACITY_BANDS`/`_MODEL_OVERRIDES` → 同步改测试断言。测试全绿 ≠ 符合 PDF。
5. **接受 GPT 对我修复动作措辞的修正。** 发现 A 的证据链是二手的（2026-09-23 会议黑板摘录），且摘录自身前后矛盾（DeepSeek 补证：blackboard.md:735 文件名示例 7 级无 50/25mA vs :594 分组表 100/60/30/15/6 vs 代码 override 500/250/100/50/25，三方互不一致）。措辞从"改错项"改为"**裁定哪份记录正确**"——不预设代码错。
6. **修正我对单样本 µ-2σ 问题的忽视。** MiniMax Round 1 问题 3 提出后我未跟进；DeepSeek 的定性正确：这不是逻辑矛盾，是**报告误导 + 统计退化被掩盖**（`np.where(counts > 1, stds, 0.0)` 把"σ 不可估"伪装成"σ=0"）。按 PDF 字面判定保留，只加报告说明——与三态判定（输出 counts）同一个修复覆盖。

## 二、收敛后的最终修复清单（可直接执行）

| 序 | 动作 | 文件:行号 | 最小 diff 思路 | 成本 |
|---|------|-----------|---------------|------|
| **P0** | **PDF §7.1.1 事实源仲裁包**：pdftotext 重导出全表，一次裁定 4 件事：① `_POUCH_CAPACITY_BANDS` 四档与区间开闭（1200/2000/3000 边界归属，代码现行语义是 [0,1200)/[1200,2000)/[2000,3000)/[3000,∞)）；② `_MODEL_OVERRIDES` 583083 档位三方矛盾 + Hermes 期望格是否仅 4 格；③ QNOM 基数 = ti[8] 标称还是 ti[9] 计算容量（GPT 补充的第 6 点，PDF 写 "QNOM × 85%"，若指标称则全体 Pouch 阈值系统性偏差）；④ 裁定结果固化为 golden fixtures 入库。**代码与测试断言同批原子修改** | `pulse_currents.py:36-58`、`quality_requirements.py:152-186`、`test_pulse_currents.py:127-137`、`test_quality_requirements.py:87-91` | 导出比对 → 改常量 → 改断言 → 入 fixtures/ 目录 | 1h |
| **P1** | 2.25V 容差匹配 + 未找到告警 | `report_coordinator.py:104-108` | `== 2.25` 改 `abs(float(listVoltageLevel[v]) - 2.25) < 1e-6`（与 `_match_index` 同口径）；未找到时 `logger.warning` + Remarks 标注，禁止静默用 index 0。注意 DeepSeek 的放大效应：legacy 期望格 `cutoff_v=listVoltageLevel[0]`（2.6V）会被 `_match_index` **成功匹配**，双条件路径也会静默判错格——修完此条同时堵住两个路径 | 5 行 |
| **P2** | 冷冻单一来源 + 旧单点兜底补全 | `quality_requirements.py:160`、`data_processor.py:344`、`report_coordinator.py:181-193` | ① 抽共享 `is_freezer_context()`，两处内部调用（见上文合并方案）；② 183 行旧单点分支补最小值检查 `stats["min"][intPosiMaxmA][intPosi2V25] >= intRequiredCapacity` + `logger.warning("legacy single-point verdict used")` + Remarks 注明 "legacy verdict"——彻底消灭无日志的单条件判定 | ~25 行 |
| **P3** | 空样本格三态判定 | `statistics_utils.py:53-69`（counts 已算未输出）、`quality_requirements.py:224-246`、`report_coordinator.py:181` | ① `compute_statistics` 返回字典加 `counts` 键（一行，计算已有）；② `evaluate_expectations` 对期望格 `counts==0` 产出 `NoData` 态；③ 聚合规则：存在 NoData → 整批 "Incomplete / 需复测"，Remarks 列缺失格；无 NoData 才 `all(passed)`；④ n=1 格保留判定、Remarks 追加 σ 说明。counts>0 但 mm2s 极低（< threshold×0.5）保留 Fail 并附 MiniMax 建议的"数据异常，请检查该档数据完整性"提示 | ~25 行 |
| **P4** | 顺手防御包 | `quality_requirements.py:169-175`、`build_expectations` Coin 分支、`_MIN_EPSILON` 定义处 | ① 构造方法匹配加中文关键词（`"叠片" or "laminate"`、`"螺旋" or "spiral"`）；② Coin Cell 且 `required not in (280, 380)` 时 `logger.warning` + Remarks "阈值偏离 PDF 标准值"（保持灵活但可见，采纳 GPT 第 7 点）；③ `_MIN_EPSILON` 补注释"浮点补偿而非语义放宽"（0 成本） | 5 行 |
| **P5** | Golden fixtures + e2e 回归 | `tests/e2e/` | 用 P0 裁定后的 fixture 断言全链路：Excel→提取→派生→判定→报告写入；覆盖 QNOM 边界值（1200/2000/3000）、freezer 不同步场景、Hermes 档位不匹配场景（断言走哪条路径 + 报告有 "legacy verdict" 标注 + Hermes 测试要验证**结论**而非仅验证路径，补 MiniMax N3） | 半天 |
| **登记不动** | ε 语义、banker's rounding、百分比 floor/round 不一致、t 分布讨论、PULSE_BURSTS 用途确认 | — | 四人 Round 2 共识：PDF 写什么就实现什么；触发概率与成本不匹配。t 分布意见可写入会议纪要供 PDF 修订参考，不进代码 | 0 |
| **长期路线图（不阻塞本轮）** | "判定格解析层"统一 | — | DeepSeek 的结构性洞察我完全采纳：A/B/C 三症状同一根因——数据侧（`data_processor.py:344`，文件名 ±5%）、期望侧（`build_expectations` + `_match_index` 1e-6）、报告侧（`report_coordinator.py:104-108`，`==` 精确）三处独立解析、三套匹配规则、零交叉校验。长期抽唯一解析层（输入 spec/construction/qnom/is_freezer/spec_method/实测档位，输出带来源标注的判定格索引），三方只消费并断言一致，不一致显式报错。**本轮不实施**，先把 P0–P5 的数据正确性修完 | — |

**不做的**（Round 2 四人共识维持）：策略类/注册表架构、ReportCoordinator 再抽层重构——数据正确性问题用结构重构治不了。

## 三、"代码是否遵照 PDF v2.3"的总体结论

**条件性合规（conditionally compliant），待 P0 裁定后才能给终局结论：**

1. **已确认合规**：§6.2.11 判定公式层——双条件（单样本最小值 ≥ 期望含 1e-6 浮点补偿、μ-2σ 严格高于期望）、未特别说明取最高脉冲电流（`currents[0]`）、派生失败时 legacy 期望格仍执行双条件。测试固化良好。
2. **无法确认合规**：§7.1.1 期望值派生层——脉冲分档表、583083 override、Hermes 期望格、QNOM 基数四个事实点全部悬而未决，且现有测试钉死的是**待裁定**的口径。**本次会议所有"PDF 规则"均为二手来源**（PDF 正文 FlateDecode 压缩不可机读），这是终局结论被卡住的唯一硬性前置。P0 完成（1 小时）后，若分档表与代码一致 → 可升级为"基本合规，遗留 P1–P4 已知缺陷"；若摘录才对 → 全体 1200–3000 边界 Pouch 与 Hermes 判定历史结论需复核，**是否回溯重跑历史报告需用户决策**。
3. **确认不合规（待修）**：① 期望格错配时静默落入单条件、required/QNOM 口径的旧判定（`report_coordinator.py:181-193`，违反 §6.2.11 双条件精神）；② 2.25V 精确比较 + index 0 静默错位（违反"对应电压档"语义）；③ 空样本格报 "Fail (minimum 0mAh)"（把"没测到"报成"不合格"，且我的原修法会把另一面放成 Pass，三态是唯一同时满足两个方向的方案）；④ 冷冻判定三口径不同步。

## 四、给用户的三个决策点

1. **P0 立即执行**（唯一前置硬依赖，1 小时）：pdftotext 重导出 §7.1.1 全表，裁定分档表/583083/Hermes 格数/QNOM 基数四件事。
2. **历史报告回溯**：若 P0 推翻现行分档表，基于错档位的历史报告是否重跑，需用户拍板。
3. **三态判定的产线语义**："Incomplete / 需复测" 作为第三种结果输出是否符合产线流程（还是必须二值），影响 P3 的聚合规则措辞。

## 五、一句话总结

公式层合规、事实层存疑、格选择层确认带病——P0 用 1 小时把事实钉死，P1–P4 共约 60 行改动把三个"格选错"症状和三态判定收掉，e2e 排最后；我放弃"跳过空格"和"传参 is_freezer"两个方案，采纳三态判定与共享 helper；长期以"判定格解析层"为共同疫苗，但先修数据正确性、不动结构。


---

## DeepSeek (Round 3): 四人共识收敛为 5 项确认缺陷 + 1 项前置仲裁 + 2 项观察项；总体结论：核心判定公式正确但"格选错→全错"是系统性硬伤，代码总体遵照 PDF 但存在 3 处静默偏离

# DeepSeek (Round 3)：最终综合建议

## 〇、方法与立场声明

本轮我重新读取了全部 9 条黑板条目（GPT/DeepSeek/GLM/MiniMax 各 Round 1+2 + User 反馈），并再次读取 `report_coordinator.py:95-215`、`quality_requirements.py:140-280`、`pulse_currents.py:30-110` 的当前代码。以下每个结论都是四人交叉验证后的收敛态。

**我明确放弃的立场**：
1. **🔴2 原始定性（"fallback 丢失最小值检查"）**：GLM 纠偏准确，我 Round 1 的描述基于过期代码。主路径（`build_expectations` 返回空 → 构造 legacy Expectation → 双条件判定）已正确实现。Round 2 已认错，此处再次确认不再保留。
2. **is_freezer 从温度字段 ti[7] 推断的修法**：被 GPT 说服——"Freezer 型"是产品规格而非测试工况，常温型做低温测试时 ti[7] 为负温，按温度推断会把常温型误判为冷冻型。正确方向是 GLM 的修法：`build_expectations` 接受调用方传入的 `is_freezer` 参数，来源与 `data_processor.py:344` 同一判定函数（文件名 OR 规则）。
3. **"Pouch profile 全部裸代码无测试"**：MiniMax 问题 1 不实。`test_quality_requirements.py:69-91` 已覆盖 Pouch 螺旋 85%/叠片 75%/构造未知返回空等场景。真实风险不是"没测试"，而是"测试把可能错误的档位口径钉住了"（见 P0）。

**我坚持的立场（经四人交叉验证未被驳倒）**：
1. 🔴1（2.25V 精确比较 + 默认 index 0）：四人全认，且我补充的"放大效应"（连双条件路径都会静默判错格）无人反驳。
2. GLM A（分档表矛盾）维持 P0：摘录自身三方不一致（分组表 vs 文件名示例 vs 代码 override），唯一出路是 pdftotext 重导出。
3. 空样本格必须三态而非跳过：GPT 的"跳格→漏报 Pass"风险与我 Round 2 的分析一致，GLM 原方案有反向缺陷。

**我被部分说服但保留残余的立场**：
- 🔴2 收窄保留：单条件旧判定没有死透（`report_coordinator.py:183-193`），在三种现实触发器（Hermes 错配 / 冷冻口径不同步 / 分档表错位）下静默激活。这不是"fallback 丢最小值"，而是"格错配→掉进无日志的旧单点判定→丢最小值"。

---

## 一、四人共识区（Round 3 最终确认）

以下五项经四人全部或三人以上确认，代码验证属实：

| # | 共识项 | 四人态度 | 代码验证位置 |
|---|--------|---------|-------------|
| ① | 核心判定公式（§6.2.11 双条件、严格大于、ε 容差）实现正确 | 四人全认 | `quality_requirements.py:235-238` |
| ② | 2.25V 精确 float 比较 + 默认 index 0 静默错位 | 四人全认 | `report_coordinator.py:104-108` |
| ③ | Pouch 容量分档表与 PDF 摘录矛盾（GLM A） | 四人全认 | `pulse_currents.py:46-58` vs `blackboard.md:570-607` |
| ④ | 冷冻判定三口径不同步（GLM B） | GLM/GPT/MiniMax/DeepSeek 全认 | `data_processor.py:344` vs `quality_requirements.py:160` |
| ⑤ | 旧单点兜底路径静默无日志（收窄后的 🔴2） | 四人全认存在 | `report_coordinator.py:183-193` |

---

## 二、分歧裁决与最终定性

### 分歧 1：is_freezer 修法（DeepSeek 温度修法 vs GLM 参数传入）

**裁决：GLM 对，我错。** GPT 的驳斥最有力——Freezer 是产品规格，ti[7] 是测试工况，两者语义不同。`data_processor.py:344` 的 `is_freezer_from_rules` 已经是基于规则的权威判定，`build_expectations` 应当接收同一结果而非自己重新推断。

**最终修法**：`build_expectations` 增加 `is_freezer: bool | None = None` 参数；`report_coordinator.py` 调用时传入 `is_freezer = "freezer" in filename.lower() or is_freezer_from_rules(rules, spec_name)`（与 data_processor 同口径）。不改 ti[7] 路径。

### 分歧 2：Fallback 三分 vs 收窄保留

**裁决：GPT 的三分框架更精确，我接受并整合。** GPT 将 fallback 拆为三段：
1. 派生失败 → legacy Expectation（双条件，语义降级但形式合规）
2. 期望格不在实测档位 → 旧单点判定（单条件，丢最小值，无日志）← **必须修**
3. `_require_positive_int` 抛 ValueError（fail-fast，设计如此）

我 Round 2 的"收窄保留"聚焦于第 2 段，与 GPT 三分的第 2 段完全吻合。**第 1 段的"语义降级"（阈值从 PDF 口径退化为 ti[17]、电流从 PDF 指定档退化为最高实测电流）我降级为 P2 观察项**——它是有意的安全网设计（代码注释"行为与历史一致"），不应删除，但应出声。

### 分歧 3：空样本格处置（GLM 跳过 vs GPT/DeepSeek 三态）

**裁决：三态方案正确。** GPT 和我在 Round 2 独立发现了同一风险：GLM 的"跳过"方案会导致 `all(v.passed for v in verdicts)` 对剩余格全 Pass → 整批输出 Pass，而 PDF 要求的判定格根本没测。这把"误报 Fail"翻转成了"漏报 Pass"，对质量门禁更危险。

**最终方案**：
1. `compute_statistics` 返回 `counts`（已计算，只差放进 dict）
2. `evaluate_expectations` 对 `counts[c][v] == 0` 的格产出 `CellVerdict` 状态为 `NoData`（既非 Pass 也非 Fail）
3. 聚合规则：存在 NoData 格 → 整批结果为 "Incomplete"，Remarks 列明缺哪个 (电流, 电压) 格；n=1 保留 PDF 判定 + 注明 σ 无判别力；n≥2 正常双条件

### 分歧 4：t 分布替代 2σ（MiniMax 问题 9）

**裁决：四人中 GLM/GPT/DeepSeek 三方一致反对，维持不改。** PDF 白纸黑字写 "µ-2σ"，改 t 分布是用统计洁癖替换文档合规，会翻转历史判定口径，且 n=3~5 时 t 值在 3.18~4.30 之间，区间放宽近一倍——无 PDF 依据、有工程危害。最多在模块 docstring 注明小样本局限性。

### 分歧 5：MiniMax 分档表引证错误

**裁决：GPT 纠举准确。** MiniMax Round 2 问题 2 引用的 `_POUCH_CAPACITY_BANDS` 少抄了一个元组（把 2000 档写成 `[100,60,30,15,6]`、3000 档写成 `[150,100,60,30,15,6]`，整体错位一档）。实际代码第二档是 `[60,30,15,6]`、第三档是 `[100,60,30,15,6]`。边界映射结论全部错位。但"< 还是 ≤"的区间语义问题本身仍然有效，合并入 P0 的 PDF 重导出一并裁定。

---

## 三、最终问题清单与优先级

### P0：PDF 事实源仲裁（前置动作，阻塞一切）

| 项 | 内容 | 来源 | 成本 |
|---|------|------|------|
| P0-A | pdftotext 重导出 §7.1.1 全表，裁定：① `_POUCH_CAPACITY_BANDS` 四档位与区间开闭（1200/2000/3000 归属）；② `_MODEL_OVERRIDES` 583083 档位 + Hermes 期望格是否仅 4 格；③ QNOM = ti[8] 标称 vs ti[9] 计算容量（GLM F2 + GPT P0 补充）；④ 1200-2000 档是否有 PDF 来源 | GLM A + GPT 裁定二 + DeepSeek §2.2 三方不一致证据 | 30-60 分钟 |
| P0-B | 裁定结果入库为 fixtures（`tests/.../fixtures/`），同步修改代码常量和测试断言，三步原子完成 | GPT 长期策略 2 + DeepSeek §2.2 "测试把错的钉住了" | 含在 P0-A 内 |

**为什么 P0 阻塞一切**：现有测试钉的是当前代码口径。若 PDF 导出后证明摘录才对，当前测试会阻止修复。在未裁定前写 e2e 是"把错误刻进回归"。**P0 之后，后续优先级可能重排。**

### P1：确认缺陷修复（4 项，不依赖 P0 结果）

| # | 问题 | 修法 | 文件 | 成本 | 来源 |
|---|------|------|------|------|------|
| 1 | **2.25V 精确比较 + 默认 index 0 静默错位** | `abs(float(listVoltageLevel[v]) - 2.25) < 1e-6`；未找到时 `logger.warning` + Remarks 标注 | `report_coordinator.py:104-108` | 5 行 | 四人全认 |
| 2 | **旧单点兜底静默无日志**（收窄后的 🔴2 第 2 段） | ① 加 `logger.warning("legacy single-point verdict used: expected cells not in measured levels")`；② Remarks 标注 "legacy verdict"；③ 补最小值检查 `stats["min"][intPosiMaxmA][intPosi2V25] >= intRequiredCapacity` | `report_coordinator.py:183-193` | ~10 行 | GLM B + DeepSeek 收窄 + GPT 三分 + MiniMax 问题 5 |
| 3 | **冷冻三口径不同步** | `build_expectations` 增加 `is_freezer` 参数；调用方传入与 `data_processor.py:344` 同口径结果；删除 `required == 280` 的自推断 | `quality_requirements.py:160` + `report_coordinator.py` 调用处 | ~20 行 | GLM B + GPT 裁定（拒绝 DeepSeek 温度修法） |
| 4 | **空样本格三态判定** | `compute_statistics` 输出 counts → `evaluate_expectations` 对 n=0 格产出 NoData → 聚合规则：有 NoData → "Incomplete"；n=1 保留 PDF 判定 + 注明 σ 无判别力 | `statistics_utils.py` + `quality_requirements.py` + `report_coordinator.py` | ~25 行 | GLM D（修正其跳过语义）+ GPT 三态 + DeepSeek §2.7 |

### P2：低风险改进（5 项）

| # | 问题 | 修法 | 成本 | 来源 |
|---|------|------|------|------|
| 5 | 构造方法中英文关键词 | `"叠片" in lower or "laminate" in lower`；同理螺旋 | 2 行 | GLM E + MiniMax 问题 6 |
| 6 | Coin 阈值越界无守卫 | `classify_spec=="Coin Cell"` 且 `required not in (280, 380)` 时 `logger.warning` + Remarks 注明 | 3 行 | GPT 裁定七 |
| 7 | `_MIN_EPSILON` 注释 | 补一句"浮点补偿而非语义放宽" | 1 行 | DeepSeek Round 1 建议 |
| 8 | `reported_by` 加入 REQUIRED_TEXT_FIELDS + Datasheet 容量正整数校验 | 各 1 行 | GPT R4/R8 |
| 9 | PULSE_BURSTS/PULSE_STEP_SCHEDULES 加注释"仅作文档，不参与判定" | 1 行 | GPT R7 + GLM 裁定 |

### P3：测试与回归（PDF 裁定后执行）

| # | 动作 | 成本 | 来源 |
|---|------|------|------|
| 10 | e2e 回归：覆盖 QNOM 边界值 / freezer 不同步 / Hermes 档位不匹配场景，断言走哪条判定路径且报告有 "legacy verdict" 标注 | 半天 | GLM 第 6 步 + GPT P5 |
| 11 | Golden fixtures 入库（从 PDF 派生，非从代码常量抄） | 含在 P0 | GPT 长期策略 |

### 观察项（登记不改）

| 项 | 说明 | 不改理由 |
|---|------|---------|
| ε 只加在 sample_ok 不加在 stat_ok | PDF 对两条件措辞不同（"less than" vs "higher than"），代码对称差忠实映射措辞差异 | GLM + GPT + DeepSeek 一致：登记即可 |
| round() 银行家舍入 | 触发概率≈0（mAh 值为整数或一位小数） | 四人一致：不值得改 |
| 百分比 floor() vs 阈值 round() 精度不一致 | 实际影响可忽略 | DeepSeek Round 1 登记 |
| t 分布替代 2σ | PDF 明文写 µ-2σ，改 t 分布翻转历史口径且无 PDF 依据 | GLM/GPT/DeepSeek 三方反对 |
| Hermes 期望值硬编码 | 当前 4 个常量可维护；PDF 重导出后一并决定是否外置 | 低频变动，含在 P0 |
| QNOM 基数歧义（ti[8] vs ti[9]） | 并入 P0 一并裁定 | GLM F2 + GPT 补充 |
| 端到端集成缝隙（GPT R10） | P3 覆盖 | — |

---

## 四、总体结论：代码是否遵照 PDF v2.3 规则？

### 结论：**基本遵照，但存在 3 处静默偏离和 1 处系统性风险**

**遵照部分**（高置信度）：
- §6.2.11 核心判定公式：双条件（最小值 ≥ 期望、μ-2σ > 期望）、严格大于、ε 容差——实现正确，测试固化良好
- §7.1.1.1 Coin Cell 常温 30mA / §7.1.1.2 冷冻 15mA（单体）/30mA（1S2P）——逻辑正确
- §7.1.1.11 Hermes 4 格绝对值——期望值与摘录一致（但是否仅 4 格待 PDF 复核）
- 文件名优先于查表的优先级约定——实现正确

**静默偏离**（代码产出结果但结果可偏离 PDF）：
1. **2.25V 静默错位**：精确 `==` 比较失败时默认 index 0，报告"正常"产出但判的是错误电压格——四人全认，最隐蔽
2. **冷冻口径不同步掉进旧单点判定**：文件名说 freezer 但规则说 380 → 数据侧按冷冻跑、期望侧按常温派生 → 期望格不匹配 → 掉进单条件旧判定，阈值口径从 PDF 绝对值退化为 required/QNOM 比例
3. **空样本格误报 Fail**：无数据的格统计值全 0 → 判 Fail "minimum 0mAh"，把"没测到"报成"不合格"

**系统性风险**（可能推翻大量判定结论）：
- **Pouch 容量分档表与 PDF 摘录矛盾**：代码四档 vs 摘录三档（无 1200-2000 档）vs 文件名示例三方不一致。若摘录才对，所有 QNOM 1200-3000 的 Pouch Cell 判定电流选错 → μ-2σ 取错格 → Pass/Fail 可能整体错位。**这是当前代码唯一可能"系统性全错"的硬伤，必须最先裁决。**

### 一句话总体评价

> 核心公式实现正确，但"判对了公式、判错了格"——判定格的选择过程散落在三处（数据侧/期望侧/报告侧）且互不校验，任意一处同步失败就产生静默误判。修复路线：先定事实（P0 PDF 重导出），再修同步（P1 四项确认缺陷），后锁回归（P3 e2e）。

---

*DeepSeek — 系统思考者，Round 3（最终轮）*

---

## MiniMax (Round 3): MiniMax Round 3：最终综合裁决——接受纠偏、放弃被说服立场、收敛最终建议

# MiniMax Round 3：最终综合裁决——接受纠偏、放弃被说服立场、收敛最终建议

## 〇、我的两处错误：明确认错，边界问题保留

**错误一：引错分档表（GPT §2、DeepSeek §2.4 共同纠举）**

我的 Round 1 问题 2 和 Round 2 §2 均将 `_POUCH_CAPACITY_BANDS` 引为：
```
(1200,[30,26,15,6]), (2000,[100,60,30,15,6]), (3000,[150,100,60,30,15,6])
```
实际代码（GPT 读码核实）是：
```
(1200,[30,26,15,6]), (2000,[60,30,15,6]), (3000,[100,60,30,15,6])
# ≥3000 → _POUCH_LARGE_PULSE_CURRENTS = [150,100,60,30,15,6]
```
据此推出的"1200→30mA档"和"边界值落在哪档"的分析**全部错位**。我接受这一纠偏，相关结论作废。

**但边界问题本身仍然成立**：实际代码的语义是"取第一个满足 `QNOM < upper_limit` 的档"，即 QNOM=1200 → **第二档 60mA**（不是第一档），QNOM=2000 → **第三档 100mA**，QNOM=3000 → **第四档 150mA**。"PDF 用 `<` 还是 `≤`、1200–2000 档是否有 PDF 来源"这个真正的问题，被我的错误引码淹没了，但 GLM 发现 A 把它完整地挖掘了出来。**边界值落在哪一档、以及各档是否有 PDF 授权，是 P0 的一部分，不因我的引码错误而失效。**

**错误二："Pouch profile 全部无测试"（DeepSeek §2.5 纠举）**

实测确认：`test_quality_requirements.py:69-91` 已覆盖 Pouch 螺旋/叠片、Spiral 85%、Laminate 75%、2000-3000档、构造未知返回空等场景；`test_new_model_analysis.py:235-265` 还有端到端用例。**"9个profile只有3个有测试"不成立。** 我撤回这一描述。

真正的风险是：这些测试钉住的是**可能错误的档位口径**（GLM A 的矛盾），测试全绿 ≠ 符合 PDF。**这个风险仍然成立，但不体现在"无测试"上，而体现在"测试把矛盾值固化了"上。**

---

## 一、我的单样本 µ-2σ 立场：被 DeepSeek 部分说服，调整措辞但核心关切保留

DeepSeek §2.3 的核心论点是：单样本 380=阈值 380 → `sample_ok=True` 且 `stat_ok=False` → Fail，**数学上是 PDF "higher than" 的正确执行，不是 bug**。我接受这一定性——PDF 字面要求严格大于，代码忠实地执行了，数学上无懈可击。

但我不接受"加个 Remarks 标注就完事"的最低限度修复，理由是：

1. 产线工程师看到"最小值检查通过但统计检查失败——且样本数=1"时，会认为代码有矛盾，要求解释。Remarks 里加一句"single sample: σ has no discriminating power"能消除这种困惑，但不能消除**另一个困惑**：为什么 n=1 的单样本在 `sample_ok=True` 时，`stat_ok` 仍然可能 False？这个困惑的根源不是报告不够清晰，而是**PDF 对 n=1 场景未定义**（设计缺陷而非实现缺陷）。
2. GPT/DeepSeek 提出的三态方案（n=0 → Incomplete、n=1 → 加说明后按 PDF 判、n≥2 → 现行双条件）是对这个设计缺陷最诚实的处理。**我放弃"µ-2σ 在 n=1 时应该自动通过"的立场，但支持三态方案作为对 PDF 语义不完整性的系统性补偿。**

**调整后的立场**：单样本 µ-2σ 不是逻辑矛盾，是 PDF 对 n=1 未定义的合规性模糊；三态方案是可接受的系统性补偿，但不是必须 P1 的紧急项——它需要和空样本格三态（GPT/DeepSeek §3）一起做，合并为一个 P3 改动。

---

## 二、我未被反驳的新盲区：确认并提升为正式问题

**盲区 N1（legacy fallback 用最高实测电流而非 PDF 指定档）——确认，且是 P2 的核心内容**

GPT Round 2 §1 的裁定一把这个场景精确拆解了：三条路径中"旧单点判定（183行）"确实用 `intPosiMaxmA`（实测最高电流），不是 PDF 指定档。这是被三人确认的结构性缺陷（DeepSeek 在 §1.2 缩范围保留、GLM §1 承认），**我接受它已被纳入正式修复清单，不另列为独立项**。

**盲区 N2（µ-2σ 分母口径不同：mAh绝对值 vs 百分比比例）——确认，仍是盲区**

`evaluate_expectations` 用 `mm2sigma > threshold_mah`（mAh绝对值），legacy fallback 用 `mm2sigma / intQnomCapacity >= intPassRate`（比例）。四条路径中两套量纲并存，无人正面处理。这个风险在我 Round 2 提了之后，GPT §1 裁定一将其纳入 fallback 三分框架、DeepSeek §1.2 将其纳入单条件兜底缺陷，**我接受已被纳入正式问题。**

**盲区 N3（Hermes 测试只验证路径不验证结论）——确认，仍是盲区**

DeepSeek §2.2 补了一句关键的话："现有测试把矛盾口径钉死了"——这个教训对整个测试策略有指导意义。Hermes 的档位不匹配场景**有测试**，但测试只检查"触发了 legacy"，不检查 legacy 结论的合理性。**我维持这一盲区，但将其纳入 P5 的 e2e 框架中解决。**

---

## 三、最终问题清单与优先级（Round 3 综合版）

### P0：【阻塞性前置——必须第一个做】

**PDF 事实源仲裁包**：用 pdftotext 重导出 `BatteryQualityRequirements_v2.3.pdf` 的 §7.1.1 全文，一次裁决四件事：
1. `_POUCH_CAPACITY_BANDS` 四档档位与区间开闭（1200/2000/3000 各落在哪一档）
2. 1200–2000 档是否存在（代码有、2026-09-23 摘录无）
3. `_MODEL_OVERRIDES` 583083 档位（代码 override 是 500/250/100/50/25；2026-09-23 摘录在两个地方给出了不一致的记录）——这同时决定 Hermes 期望格是否完整
4. QNOM = ti[8] 标称容量还是 ti[9] 计算容量（PDF 写"QNOM × 85%"）

**同步动作**：PDF 重导出后，修改 `_POUCH_CAPACITY_BANDS`/`_POUCH_LARGE_PULSE_CURRENTS`/`_MODEL_OVERRIDES` → **同步修改测试断言**。测试钉住的是可能错误的值，代码改了不同步改测试 = 新回归。三个动作原子完成。

**来源**：GLM 发现 A + DeepSeek §2.2 新证据（三份记录互不一致）+ GPT §2 补充证据链 + 我的 Round 1 问题 2（边界值，问题本身有效、引码错误作废）。

---

### P1：【两个高风险静默失效路径】

**P1a — 2.25V 精确浮点比较静默错电压**（四人全认）：

`report_coordinator.py:104-108` 用 `== 2.25` 精确比较；未找到时 `intPosi2V25` 默认 0。**DeepSeek Round 2 §2.1 发现了我 Round 1 没有说透的放大效应**：167-175 行的 legacy 期望格取 `cutoff_v = float(listVoltageLevel[intPosi2V25])`，2.25V 匹配失败时，这个格会"成功"匹配到 index 0（如 2.6V），`evaluate_expectations` 的双条件完整执行，**但判的是错误的电压格，报告外观正常**。这是整个链路中最难发现的误判。

修复：`abs(float(listVoltageLevel[v]) - 2.25) < 1e-6` + 未找到时 `logger.warning` + Remarks 标注实际判的电压。

**P1b — 冷冻三口径不同步 → 静默走旧单点兜底**（GLM Round 1 发现 B，DeepSeek 缩范围保留）：

`data_processor.py:344` 用文件名OR规则判断冷冻，`build_expectations` 用 `required == 280` 单独判断。两个口径不同步时，数据侧按降额档跑（15mA），期望侧派生常温 30mA → 档位不匹配 → verdicts=[] → `report_coordinator.py:183` 旧单点兜底：单条件、无日志、阈值退化。

修复（GPT Round 2 §5 反对 DeepSeek 温度式修法，采纳 GLM 参数传入方案）：`build_expectations` 增加 `is_freezer` 参数，由调用方传入与 `data_processor.py:344` 同一套口径的结果；兜底分支补最小值检查 + `logger.warning` + Remarks "legacy single-point verdict (expectation cells not in measured levels)"。

---

### P2：【中风险结构缺陷——三处各算各的、互不校验】

**P2 — "判定格解析"散落三处互不交叉校验**（DeepSeek Round 2 §3 系统性根因分析）：

| 解析点 | 位置 | 匹配规则 |
|---|---|---|
| 数据侧（测哪些档） | `data_processor.py:344` + `lookup_pulse_currents` | 文件名±5%容差，优先查表 |
| 期望侧（判哪些格） | `build_expectations` + `_match_index` | 1e-6容差 |
| 报告侧（legacy格） | `report_coordinator.py:104-108` | `== 2.25` 精确比较 |

三者任一不同步 → 格选错 → µ-2σ 取错格 → Pass/Fail 整体错位。**P1a/P1b 是这个结构性缺陷的已知症状，P2 是根因本身。**

短期（本次修复）：做完 P1a + P1b 堵住已知漏洞。
长期路线图（DeepSeek §3 建议）：抽取唯一的"判定格解析层"——输入 (spec, construction, qnom, is_freezer, spec_method, 实测档位)，输出带来源标注的 (current_index, voltage_index, threshold)，三方只消费它的结果并断言一致。**这个建议我支持，但本次修复范围不包含结构重构，列为 v2.x 路线图项。**

---

### P3：【语义模糊的系统性补偿——三态判定】

**P3 — 空样本格 + 单样本 µ-2σ 的三态处理**（GPT Round 2 §4 原创 + DeepSeek Round 2 §2.3 修正）：

两条独立的模糊线在这里汇聚：
- **n=0（整格无样本）**：当前 `compute_statistics` 把 counts 算出来了但没输出，下游无法区分"没测到 / n=1 / n≥2"。GLM 发现 D 的修复方案（跳过）会把"缺数据"升格为 Pass（GPT 正确指出这个反向风险）。
- **n=1（单样本）**：PDF 对 n=1 时的 µ-2σ 未定义，DeepSeek §2.3 的数学论证我接受（严格">"是 PDF 正确执行），但报告上需要说明。

**GPT 的三态方案我接受**：
1. `compute_statistics` 输出 `counts` 矩阵（代码已有计算，只差放进返回字典）；
2. `evaluate_expectations` 对 counts==0 → **第三态 NoData**，聚合成 "Incomplete / 需复测"（绝不输出 Pass），Remarks 点名缺哪个 (电流,电压) 格；
3. counts==1 → 按 PDF 严格判定，但追加 Remarks 说明"σ 无独立判别力"；
4. counts≥2 → 现行双条件。

**注意**：这个改动会影响聚合规则（`report_coordinator.py` 的 `all(v.passed for v in verdicts)`），需要同步修改聚合逻辑。合并改动约 25 行。

---

### P4：【顺手防御项——5行以内】

1. **构造方法中英文关键词**（GLM Round 1 发现 E）：`"叠片" in construction or "laminate" in lower`、`"螺旋" or "spiral"`。i18n 目录存在，中文化是时间问题，这2行防的是必然事件，不是偶发风险。**我维持提升为 P2 的主张——GLM 列为低/顺手项，我认为是迟早踩的坑。**
2. **Coin 阈值越界无守卫**（GPT Round 2 §7 补充）：`classify_spec=="Coin Cell"` 且 `required not in (280, 380)` → `logger.warning` + Remarks 注明。保持灵活性但让偏离可见。
3. **`_MIN_EPSILON` 注释**（DeepSeek Round 1 原建议后半句）：补"浮点补偿而非语义放宽"注释，0成本。
4. **`build_expectations` 各空返回分支 + `lookup_pulse_currents` 空时 `logger.warning`**（GPT R9 修正 + GLM R7 顺手修）：顺手3行。

---

### P5：【测试补全——P0 裁定之后才能做】

Golden fixtures 入库（从 PDF 派生的断言值）→ e2e 全链路覆盖（含 QNOM 边界值 1200/2000/3000、冷冻口径不同步场景、Hermes 档位不匹配 → 验证走哪条路径 + 报告是否有标注）。**在 PDF 事实源未定之前写 e2e = 把错误刻进回归。**

---

### 观察项（明确不动代码）

- ε 不对称（`sample_ok ≥-ε`、`stat_ok >`）：忠实映射 PDF 措辞差异（"less than" vs "higher than"），登记即可（DeepSeek Round 1 建议后半句，GPT/GLM 同意）
- banker's rounding（触发概率≈0，QNOM × 0.85/0.75 极少恰好为 .5）
- 百分比 floor vs round 不一致（GPT R14，低实际影响）
- t 分布替代 2σ（PDF 白纸黑字写 µ-2σ，改为 t 分布 = 改标准而非修 bug；四票反对：MiniMax Round 1 提出 → GLM/DeepSeek/GPT Round 2 明确反对）
- PULSE_BURSTS / PULSE_STEP_SCHEDULES 未参与判定管线（GPT R7，验证为"仅作文档常量"，加注释即可）
- Hermes 4 格 + 期望值外置（GPT R6/GLM F，与 P0 同批做，把硬编码值移入配置注释/模块常量并附 PDF 页码）

---

## 四、对"代码是否遵照 PDF v2.3 规则"的总体结论

**有条件的"是"：**

1. **核心判定公式（§6.2.11 双条件）实现正确**：最小值 ≥ 期望（含浮点容差 1e-6）、µ-2σ 严格大于期望，取最高脉冲电流档——四轮讨论无异议，测试固化良好。

2. **但"判定格怎么选出来"存在四个静默失效路径**：
   - 2.25V 精确比较失败时静默判错电压（report_coordinator.py:104-108）
   - 冷冻三口径不同步时静默走单条件旧判定（report_coordinator.py:183）
   - 期望格不在实测档位时静默走 legacy 路径（Hermes/Pouch档位错配触发）
   - 以上三者共享同一个根因：判定格解析散落在三处且互不校验

3. **PDF 分档表（§7.1.1）存在三份互不一致的记录**：代码 `_POUCH_CAPACITY_BANDS`、2026-09-23 摘录（在两处互相矛盾）、blackboard 文件名示例（7级 vs 5级）。**在 pdftotext 重导出之前，任何人都无法断言代码是否符合 PDF**——这是本会议最重要的事实，超越所有代码层面的修复。

4. **四个隐性假设未被文档化**：
   - QNOM = 计算容量（ti[9]）而非标称容量（ti[8]）——待 PDF 确认
   - Hermes §7.1.1.11 只需 4 个判定格——待 PDF 确认
   - 单样本 n=1 时的 µ-2σ 按严格 ">" 判——PDF 未定义，当前实现是保守选择
   - Pouch 1200–2000 区间的档位有代码授权但无 PDF 授权——待 PDF 确认

**最终答案**：如果 PDF 重导出后确认分档表与代码一致（最大概率场景），则代码总体合规则，仅需修 P1a/P1b/P3/P4；若重导出后发现档位错误，则需要 P0 裁定 → 改档位 → 改测试 → 重跑历史报告。这两套路径的公共部分是：**2.25V 容差匹配和冷冻口径同步是必须修的**，它们与 PDF 规则无关，是代码内部一致性问题。

---

## 五、一句话行动清单（用户决策点）

1. **必须（阻塞 P1-P5）**：pdftotext 导出 §7.1.1 全表，裁定四件事（档位表、1200-2000存废、583083档位、QNOM基数），结果同步改代码+测试
2. **必须（5行）**：2.25V 改容差匹配 + 未找到时 logger.warning + Remarks 标注
3. **必须（~20行）**：is_freezer 单一来源（参数传入） + 183行兜底补 min 检查 + logger.warning + Remarks
4. **建议（~25行）**：三态判定（n=0→Incomplete/否决Pass、n=1→加σ说明、n≥2→现行双条件），与 compute_statistics 输出 counts 一起做
5. **建议（顺手）**：构造方法认中文关键词 + Coin阈值越界warning + 注释补全
6. **长期**：抽取"判定格解析层"，三者统一来源 + 交叉校验


---

## GPT (Round 3): Final synthesis: 收敛为 P0–P4 共 7 项修复 + 3 项登记不动，总体结论"核心判定公式正确，风险集中在判定格选择的三处不同步"；吸收 DeepSeek 统一根因论和 is_freezer 内部 helper 修法、吸收 GLM 测试固化错误值的警告、维持三态判定方案。

# GPT (Round 3 — FINAL): 综合四方裁决，收敛问题清单与最终建议

---

## 〇、总体结论：代码是否遵照 PDF v2.3 规则？

**核心判定公式遵照 PDF，判定格选择存在系统性风险。**

具体而言：
- ✅ §6.2.11 双判定条件（①所有样本 ≥ 期望；②μ-2σ 严格高于期望）实现正确，且被测试固化
- ✅ ε 容差（1e-6）忠实映射了 PDF "less than" vs "higher than" 的措辞差异
- ✅ 最高脉冲电流选取（`currents[0]`）逻辑正确
- ⚠️ **判定格怎么选出来**存在三处独立解析、互不校验的结构性问题：分档表与 PDF 摘录矛盾（A）、冷冻三口径不同步（B）、2.25V 精确比较静默错位（C）。三者同根同源——DeepSeek 在 Round 2 正确诊断了这一点：**"判定格解析层"散落三处且互不校验**，任何一处错配都会导致 μ-2σ 取错格、Pass/Fail 整体错位
- ⚠️ 空样本格（n=0）会被误报为 Fail（"没测到"报成"不合格"），且缺少第三态 Incomplete
- ⚠️ legacy 兜底路径（183 行）在格错配时静默激活，只有单条件判定且无日志

**一句话：公式对了，但"判哪个格"这个前提可能错——先确认格对不对（P0），再修格选择的一致性（P1/P2），最后加固边界（P3/P4）。**

---

## 一、我被说服的立场（明确放弃）

### 1. 放弃"DeepSeek #2 是高危主缺陷"的定性
Round 1 我（GPT）将"fallback 丢失最小值检查"列为高风险。GLM 在 Round 1 正确纠偏：`report_coordinator.py:166-176` 当前代码在 `build_expectations` 返回空时，构造 legacy `Expectation` 交给 `evaluate_expectations` 执行**双条件**——最小值检查并没有丢失。DeepSeek 在 Round 2 正式认错。**我接受纠偏**，主路径的双条件判定是完好的。

### 2. 放弃 is_freezer 从温度字段 ti[7] 推断的方案，接受 GLM + DeepSeek 改进的修法
Round 2 我拒绝了 DeepSeek 的温度字段方案（"Freezer 是产品规格，不是测试工况"），并支持 GLM 的参数传入方案。Round 2 末尾 DeepSeek 提出了更优修法：**让 `build_expectations` 内部调用与 `data_processor.py:344` 同一个 `is_freezer` helper**，而非在三个调用点各传参数（传参方案在调用点各自传错就复发）。**我接受 DeepSeek 的改进**——内部 helper 比参数传入更健壮。

### 3. 放弃"补测试是第一优先级"的排序
Round 1 我（GPT）和 MiniMax 都强调测试覆盖不足。但 GLM 在 Round 1 正确警告：**现有测试已经把可能错误的分档表钉死了**（`test_pouch_band_2000_to_3000` 断言 2000mAh→100mA 顶档）。DeepSeek 在 Round 2 强化了这一点："测试全绿 ≠ 符合 PDF"。**测试必须在 P0 PDF 仲裁之后写，否则是在固化错误。**

### 4. 放弃 R1"判定输出空白"的严重性描述
DeepSeek Round 2 正确指出：legacy 双条件兜底保证了 Result 列总有内容。R1 的"合规空洞"应降级为"口径偏差"——阈值从 PDF 派生值退化为 required 字段值。后果是"判定标准可能偏离 PDF"，不是"完全没有判定"。

---

## 二、吸收的他人正确观点

| 来源 | 观点 | 我的处理 |
|------|------|----------|
| DeepSeek R2 §3 | 三个 bug（A/B/C）同根同源："判定格解析"散落三处互不校验 | **完全吸收**。长期方向是抽取统一的"判定格解析层"，但不阻塞本轮修复 |
| DeepSeek R2 §2.2 | 摘录自身自相矛盾（CF583083 在分组表归 100/60/30/15/6，但在文件名示例写 500/250/100/60/30/15/6） | **吸收**。P0 仲裁时必须同时裁定三方不一致（代码/摘录/文件名示例） |
| DeepSeek R2 §2.5 | MiniMax "Pouch 6 个裸代码路径无测试"不实 | **吸收**。`test_quality_requirements.py` 已有 Pouch 螺旋/叠片/构造未知用例。真正缺的是跨 QNOM 边界测试 |
| DeepSeek R2 §2.4 | MiniMax 引证 `_POUCH_CAPACITY_BANDS` 整体错位一档 | **吸收**。MiniMax 的边界映射结论（"1200→第一档 30mA"）是错的，实际 1200→第二档 60mA |
| GLM R1 纠偏 | DeepSeek 🔴2 主路径已不成立 | **吸收**。上文第一节已确认 |
| GLM R2 §二 | 空样本格修复比预估便宜（counts 已计算只差输出） | **吸收**。实际成本 <15 行 |
| DeepSeek R2 §3 | is_freezer 用内部 helper 优于参数传入 | **吸收**。取代 GLM 原始的参数传入方案 |
| DeepSeek R2 §二 | GLM D "跳过空样本格"会把缺数据放成 Pass | **吸收**。这正是我在 Round 2 提出三态判定的原因 |
| GLM R2 §二 | t 分布改造（MiniMax 问题 9）不应采纳 | **完全同意**。PDF 写死 "µ-2σ"，改 t 分布是改标准不是修 bug |
| GLM R2 §四 | ε 不对称、banker's rounding、百分比 floor 应登记不动 | **同意**。触发条件极罕见，不值得改 |
| MiniMax R2 §三 | 单样本 μ-2σ 不是"逻辑矛盾"而是"报告误导 + 统计退化" | **吸收**。DeepSeek 的定性更准确：PDF 两个条件是独立门槛，一过一不过不构成矛盾。真正问题是 n=1 时 σ=0 被伪装成 σ 有判别力 |

---

## 三、收敛后的问题清单与优先级

### P0：PDF §7.1.1 事实源仲裁包（四人共识，最高优先级）

**问题**：`_POUCH_CAPACITY_BANDS`（pulse_currents.py:46-53）与 2026-09-23 会议黑板 PDF 摘录至少有一份错了，且摘录自身自相矛盾（CF583083 在分组表与文件名示例中档位不同）。同时 QNOM 基数（ti[8] 标称 vs ti[9] 计算容量）与 PDF "QNOM × 85%" 的对应关系未裁定。

**影响**：所有 QNOM 在 1200/2000/3000 边界的 Pouch Cell 判定可能系统性错位。Hermes 583083 的档位表（500/250/100/50/25 vs 100/60/30/15/6 vs 500/250/100/60/30/15/6）三方不一致也在同一仲裁包内解决。

**动作（4 件事一次裁定）**：
1. pdftotext 重导出 §7.1.1 全表
2. 人工比对 `_POUCH_CAPACITY_BANDS` / `_POUCH_LARGE_PULSE_CURRENTS` / `_MODEL_OVERRIDES` / Hermes 4 格期望值
3. 裁定 QNOM = ti[8] 标称还是 ti[9] 计算容量
4. **结果固化为 fixtures 入库**（`tests/.../fixtures/`），三处口径（代码/docstring/黑板摘录）收敛为一处权威源

**同步动作**：改 `_POUCH_CAPACITY_BANDS` / `_MODEL_OVERRIDES` 后，**必须同批改测试断言**（`test_quality_requirements.py`、`test_pulse_currents.py`）。测试全绿 ≠ 符合 PDF——这是本轮最值得记住的教训。

**成本**：半天。**收益**：消除"判定格选错"的系统性风险，且是后续所有修复和测试的前置条件。

---

### P1：2.25V 容差匹配 + 未找到告警（四人共识）

**问题**：`report_coordinator.py:104-108` 使用 `listVoltageLevel[v] == 2.25` 精确浮点比较，未找到时 `intPosi2V25` 静默保持默认值 0（如 2.6V）。后果比 Round 1 描述更隐蔽：legacy Expectation 的 `cutoff_v` 取 index 0 的电压值，`_match_index`（1e-6 容差）会成功匹配到 index 0，于是 `verdicts` 非空、报告"正常"产出 Pass/Fail——**双条件完整执行了，但判的是 2.6V 格**。无异常、无空值、无日志。

**动作**：
1. `abs(float(listVoltageLevel[v]) - 2.25) < 1e-6`（与 `quality_requirements._match_index` 同口径）
2. 未找到时 `logger.warning` + 报告 Remarks 标注"2.25V 未找到，使用 index 0 电压"
3. 三处匹配容差统一为 1e-6

**成本**：5 行。**收益**：消除静默错电压——全链路最难被发现的误判。

---

### P2：冷冻统一来源 + legacy 兜底补全（GLM B + DeepSeek 收窄后 #2 + MiniMax 问题 5）

**问题**：冷冻判定三处口径不同步（`data_processor.py:344` 文件名 OR 规则 vs `quality_requirements.py:160` 仅看 required==280）。当文件名说 freezer 但 required=380 时，数据侧按 15/13/7.5/3 降额档跑，`build_expectations` 派生 30mA 常温期望 → 30 不在实测 [15,13,7.5,3] 中 → `verdicts=[]` → `report_coordinator.py:183` 旧单点判定静默激活：单条件、阈值=required/QNOM 比例、无日志。

**动作（3 项合并修）**：
1. **is_freezer 统一来源**：提取一个 `is_freezer_context()` helper 函数，供 `data_processor` 和 `build_expectations` 内部共同调用（吸收 DeepSeek 改进方案，取代 GLM 原始的参数传入方案——传参在三个调用点各自传错就复发）
2. **183 行兜底补最小值检查**：`stats["min"][intPosiMaxmA][intPosi2V25] >= intRequiredCapacity`
3. **183 行兜底加 `logger.warning` + Remarks 标注 "legacy verdict (expected cells not in measured levels)"**

**成本**：~25 行。**收益**：消除静默降级到错误标准且无日志的路径。

---

### P3：空样本格三态判定（GPT 原创方案，DeepSeek 支持，修正 GLM D 方案）

**问题**：`statistics_utils.py` 空格全 0.0，`evaluate_expectations` 不看样本数 → n=0 时 Fail/minimum 0mAh（"没测到"报成"不合格"）。GLM 建议"跳过空格并汇总到 Remarks"，但 DeepSeek 正确指出：跳过会让 `all(v.passed)` 聚合时把缺数据放成 Pass（Hermes 4 格中 2.5V 格无数据、其余 3 格全过 → 报告 Pass）。

**三态方案（吸收 DeepSeek 的安全论证）**：
1. `compute_statistics` 输出 `counts` 矩阵（已计算只差放进返回字典，GLM 确认成本极低）
2. `evaluate_expectations` 对 `counts==0` 的期望格产出第三种状态 `NoData`
3. 聚合规则：存在 `NoData` 格 → 整批结果为 **"Incomplete / 需复测"**（绝不允许聚合成 Pass），Remarks 列明缺哪个 (电流,电压) 格；无 NoData 时才按 `all(passed)` 判 Pass/Fail
4. n=1 时保持 PDF 字面判定（`stat_ok = mean > threshold`），但 Remarks 追加 "single sample: μ-2σ equals sample value; σ has no discriminating power"（吸收 DeepSeek 对 MiniMax"矛盾"定性的修正）
5. 真实低值（n≥2 但 mm2s 极低）保持 Fail

**成本**：~25 行（statistics_utils + quality_requirements + report_coordinator）。**收益**：同时堵住"误报 Fail"和"漏报 Pass"两个方向。

---

### P4：构造方法中英文关键词 + Coin 阈值越界 warning + 注释补充（低优先级防御）

**问题 4a**：`quality_requirements.py:169-175` 构造方法只认英文 "laminate"/"spiral"。UI 有 i18n 目录（`locale/`），中文化时必然踩雷。  
**动作**：同时认 "叠片"/"螺旋"。2 行。

**问题 4b**：Coin Cell 阈值直接取 `required`（ti[17]），无守卫。若用户或配置意外改了该值，判定偏离 PDF。  
**动作**：`classify_spec=="Coin Cell"` 且 `required not in (280, 380)` 时 `logger.warning` + 报告 Remarks 注明"阈值偏离 PDF 标准值"。保持灵活性但让偏离可见。

**问题 4c**：`_MIN_EPSILON` 注释补充、`PULSE_BURSTS`/`PULSE_STEP_SCHEDULES` 注释说明"仅作 PDF 条款文档，不参与判定管线"。0 成本。

**问题 4d**：`reported_by` 加入 `REQUIRED_TEXT_FIELDS`；Datasheet 容量加正整数校验。各 1 行。

**成本**：总计约 10 行。**收益**：防御性补丁，防止未来踩雷。

---

### P5：Golden fixtures + e2e 回归测试（必须在 P0 之后）

**动作**：
1. 用 P0 裁定后的正确档位表构建 golden fixtures（从 PDF 派生，不是从代码常量抄）
2. e2e 测试覆盖：QNOM 边界值、freezer 不同步→legacy 路径标注、Hermes 档位不匹配→Incomplete、空样本格→三态
3. 断言报告的 Remarks 包含正确的标注信息

**为什么排在最后**：在分档表存疑时写 e2e = 把可能错误的值刻进回归。测试全绿 ≠ 符合 PDF——GLM 和 DeepSeek 在这一点上的警告是本轮最重要的共识之一。

**成本**：半天。**收益**：把本轮发现的所有场景锁死成回归。

---

### 登记不动（明确不做）

| 项目 | 理由 |
|------|------|
| t 分布替代 2σ（MiniMax 问题 9） | PDF 写死 "µ-2σ"，改 t 分布是改标准不是修 bug。登记为"小样本下 2σ 偏乐观"的已知局限 |
| ε 不对称（MiniMax 问题 8） | PDF 对两个条件用了不同措辞，代码的对称差忠实映射了措辞差异 |
| banker's rounding（DeepSeek #8） | 实测数据是整数/一位小数，触发概率≈0 |
| 百分比 floor vs round（DeepSeek #14） | 同上 |
| 策略类/注册表架构重构 | dict 查表足够，2026-09-23 会议已有结论 |
| ReportCoordinator 再分层 | 数据正确性问题用结构重构治不了 |

---

## 四、四人 Round 2 分歧的最终裁定

### 分歧 1：is_freezer 修法

| 立场 | 裁定 |
|------|------|
| DeepSeek R1：从 ti[7] 温度字段推断 | **不采纳**。"Freezer"是产品规格，不是测试工况。常温型做低温测试时 ti[7] 可能是负温，按此修法会误判 |
| GLM R1：`build_expectations` 加 `is_freezer` 参数，调用方传入 | 方向对但不够健壮——三个调用点各自传错就复发 |
| DeepSeek R2：内部 helper 函数，`build_expectations` 和 `data_processor` 共同调用 | **采纳**。比参数传入更健壮，一个函数定义、一处调用 |
| GPT R2：支持 GLM 方案 | **修正**：改为支持 DeepSeek R2 的内部 helper 方案 |

### 分歧 2：空样本格修复

| 立场 | 裁定 |
|------|------|
| GLM D：跳过空格并汇总到 Remarks | **不完整**。跳过会让聚合把缺数据放成 Pass |
| MiniMax 零值安全网：Fail 是正确行为 | 对 n=0 不对——"没测到"≠"不合格" |
| GPT R2 三态判定：NoData → Incomplete | **采纳**。同时满足"不误报 Fail"和"不漏报 Pass" |
| DeepSeek R2：支持三态，n=0 标记并否决 Pass | **确认一致** |

### 分歧 3：单样本 μ-2σ 定性

| 立场 | 裁定 |
|------|------|
| MiniMax：逻辑矛盾 | **不采纳**。两个条件是独立门槛，一过一不过不构成矛盾 |
| DeepSeek：报告误导 + 统计退化 | **采纳**。问题不是判定逻辑错，而是报告未说明 σ 退化为无判别力 |
| GLM：不改判定，只加 Remarks | **同意** |

### 分歧 4：fallback 三分 vs 收窄

| 立场 | 裁定 |
|------|------|
| GPT R2：三段分析（派生失败→legacy 双条件 / 期望格错配→旧单点 / _require_positive_int 抛错） | 分析框架正确 |
| DeepSeek R2：收窄为"单条件兜底在期望格错配时静默生效" | 描述更精准 |
| 实际裁定 | **两者合并**：主路径双条件完好（GLM 纠偏成立），183 行单条件兜底待修（DeepSeek 收窄后的 #2 成立），三段都需要日志 |

### 分歧 5：P0 仲裁包的范围

| 立场 | 裁定 |
|------|------|
| GLM：分档表 + override + Hermes 档位 | 基础范围正确 |
| GPT R2：+ QNOM 基数（ti[8] vs ti[9]） | **采纳**。"QNOM × 85%"的 QNOM 指标称还是计算容量必须一并裁定 |
| DeepSeek R2：+ 摘录自相矛盾证据 + 测试断言同步改 | **采纳**。三方不一致必须同时裁定，测试钉错值必须同批改 |
| MiniMax R2：+ QNOM 边界开闭 | **采纳**。`<` 还是 `≤` 在重导出时一并裁定 |

**P0 最终范围**：pdftotext 导出 → 一次裁定 6 件事：① `_POUCH_CAPACITY_BANDS` 四档位与区间开闭 ② `_MODEL_OVERRIDES` 583083 档位 ③ Hermes §7.1.1.11 是否仅 4 格 ④ QNOM = ti[8] 标称还是 ti[9] 计算容量 ⑤ 摘录三方不一致的裁决 ⑥ 结果固化为 fixtures 入库 + 同步改测试断言

---

## 五、长期路线图建议（不阻塞本轮修复）

吸收 DeepSeek Round 2 §3 的系统视角：A/B/C 三个高危项同根同源——"判定格解析"散落三处（数据侧 `data_processor`、期望侧 `build_expectations`、报告侧 `report_coordinator`）且互不校验。本轮修复的是当前症状，未来新增 profile（如 v2.4）仍会以同样方式复发。

**长期建议**：抽取统一的"判定格解析层"——输入 (spec, construction, qnom, is_freezer, spec_method, 实测档位)，输出带来源标注的 (current_index, voltage_index, threshold)，数据采集、期望派生、报告判定三方只消费它的结果，不一致时显式报错而非静默兜底。这与 GPT R5 的"统一 FreezerContext"、R10 的"集成缝隙"是同一方向，但范围更准：要统一的不只是冷冻标志，是**整个格选择过程**。

---

## 六、总结

| 维度 | 结论 |
|------|------|
| 核心判定公式 | ✅ 正确遵照 PDF |
| 判定格选择 | ⚠️ 三处独立解析互不校验，P0 仲裁是硬性前置 |
| 边界与兜底 | ⚠️ 空样本格误报、legacy 静默降级、冷冻口径分叉 |
| 测试覆盖 | ⚠️ 存在但可能钉了错误值，必须在 P0 后重建 |
| 总体评价 | **代码的"算"是正确的，"算哪个格"是系统性风险。先定事实（P0），再修一致性（P1/P2），最后加固（P3/P4/P5）。** |

四人 22 条发现、经过三轮辩论去重验证后，收敛为 **7 项修复动作**（P0–P5 共 6 项 + P4 子项）和 **6 项明确不动**。最大公约数不是"该修什么"，而是**"先确认 PDF 原文到底写了什么"**——在 pdftotext 导出 §7.1.1 全表之前，任何基于"记忆中的 PDF"或"黑板摘录"的争论都是空中楼阁。

---
