# GLM (Round 1): 从可行性角度审视当前 pulse currents 逻辑：核心流程已经够用，真正的痛点在边界处理和用户可见性，而非架构重构

# Pulse Currents 逻辑务实分析

## 一、现状评估：能用，但脆

我通读了所有核心文件（pulse_detector.py、pulse_matcher.py、charge_calculator.py、battery_analysis.py、filename_parser.py、config_defaults.py）以及对应的测试文件。说实话：**当前逻辑在正常路径上工作得不错**。

### 做得好的地方
1. **pulse_matcher 从三重循环升级为 numpy 广播**——这是正确的优化方向，测试覆盖也到位（BTS 头部行、短 pulse_mask、多电流等级重叠等边界都有）。
2. **ChargeCalculator 的 searchsorted 批量定位**——避免了逐行扫描，batch 模式和单值模式结果一致。
3. **测试契约锁**——test_pulse_matcher.py 和 test_charge_calculator.py 用具体数值锚定了行为，重构时不容易出错。

### 但要注意
整个脉冲逻辑**完全依赖一个假设**：Excel 文件的 Step 列中脉冲步骤被标记为"脉冲"或"Pulse"。如果 BTS 设备固件版本不同、导出格式不同、或者用户手动编辑过 Excel——这个假设就崩了。当前代码的处理方式是直接抛 `BatteryAnalysisException("Pulse data not found")`，对用户来说就是"分析失败了，不知道为什么"。

## 二、痛点识别

### 用户痛点（高优先级）
1. **静默失败，无诊断信息**：`detect_pulse_rows` 返回全 False 时，`battery_analysis.py` 直接抛异常。用户不知道是文件里没有脉冲步骤、还是步骤名拼写不同、还是列索引错了。这是最影响用户体验的问题。
2. **文件名格式依赖太强**：`extract_pulse_current` 用正则 `\(([\d.]+[-\d.]+)mA` 匹配。如果文件名是 `CP305050(30-26-15-6mA,2000mAh)` 可以匹配，但如果多了个空格 `30 - 26 - 15 - 6mA` 或者用了全角括号，就静默返回空列表。用户发现 pulse_currents 没被自动提取，只能手动填。
3. **±5% 容差不可调**：硬编码在 `b_is_in_range` 和 `match_pulse_levels` 中。不同电池类型的测试精度不同，有些场景可能需要 ±3% 或 ±10%。当前只能改代码。

### 开发者痛点（中优先级）
1. **中文字符串硬编码**：`"脉冲"` 散落在 pulse_detector.py、charge_calculator.py（`step_data[non_pulse]` 的过滤条件）、battery_analysis.py 多处。虽然目前只有两种写法，但如果将来要支持其他语言或新增步骤类型，需要改多个文件。
2. **数据流隐式约定**：`listTestInfo[14]` 是 pulseCurrents，`listTestInfo[15]` 是 cutOffVoltages——魔法索引，无类型安全。`start_row=2` 硬编码在多处。
3. **pulse_matcher 的 listLevelToRow 初始化为 0**：注释里专门讨论了 0 哨兵与行索引 0 冲突的问题。当前用 `np.argmax` 取首个匹配行，如果首个匹配行恰好是索引 0（不可能，因为 start_row=2），语义会错。这个设计决策虽然在当前使用场景下安全，但依赖隐式假设。

## 三、成本效益分析

| 改进项 | 预估工作量 | 收益 | 判定 |
|--------|-----------|------|------|
| 给 pulse detection 加诊断日志 | 0.5天 | **高**：用户能自己排查问题 | ✅ 值得做 |
| 容差参数化（从配置读取） | 0.5天 | **中**：灵活性提升，但当前 5% 够用 | ⚠️ 低优先级 |
| 步骤名常量化（提取到 constants.py） | 0.25天 | **中**：减少散落的硬编码 | ✅ 顺手做 |
| 文件名解析鲁棒性增强 | 0.5天 | **中**：覆盖更多文件名格式 | ⚠️ 看需求频次 |
| 完全重构 pulse 逻辑为策略模式 | 3-5天 | **低**：过度设计，当前只有 NEWARE 一种设备 | ❌ 不值得 |
| listTestInfo 改为 dataclass/namedtuple | 2天 | **中**：类型安全，但改动面大 | ⚠️ 作为技术债排期 |

## 四、最小可行改进

**核心原则：不改架构，只加能见度和容错。**

### 改进 1：pulse detection 加诊断（ROI 最高）
在 `detect_pulse_rows` 返回全 False 时，记录实际出现的 Step 值去重列表。在 `battery_analysis.py` 的异常消息中包含这些信息。

```python
# pulse_detector.py
def detect_pulse_rows(record_df, step_col=1):
    step_series = record_df.iloc[:, step_col].astype(str).str.strip()
    mask = step_series.isin(["脉冲", "Pulse"])
    if not mask.any():
        unique_steps = step_series.unique().tolist()
        logger.warning("No pulse rows found. Unique step values: %s", unique_steps)
    return mask
```

```python
# battery_analysis.py - 异常消息改进
if pulse_mask.sum() == 0:
    unique_steps = record_df.iloc[:, 1].astype(str).str.strip().unique().tolist()
    raise BatteryAnalysisException(
        f"Pulse data not found: {strPath}. "
        f"Step column contains: {unique_steps}"
    )
```

**成本**：10 行代码，0.5 小时。**收益**：用户能自己看到"原来步骤名是 'Pulse_Test' 不是 'Pulse'"。

### 改进 2：步骤名常量化
在 `constants.py` 中定义 `PULSE_STEP_NAMES = ("脉冲", "Pulse")`，所有引用处统一使用。这是防止未来扩展时漏改的安全网。

**成本**：改 3 个文件各 1 行。**收益**：单一来源，改一处生效。

### 改进 3：文件名解析容错
`extract_pulse_current` 返回空列表时，当前静默忽略。可以在日志中记录"文件名不匹配脉冲电流模式"，让用户知道需要手动填写。

**成本**：加 2 行日志。**收益**：减少用户困惑。

## 五、执行路径（按优先级排序）

### 第一步（立即可做，1小时内）
1. 在 `constants.py` 新增 `PULSE_STEP_NAMES` 常量
2. `pulse_detector.py`、`charge_calculator.py`、`battery_analysis.py` 引用该常量
3. `detect_pulse_rows` 加诊断日志（unique step values）
4. `battery_analysis.py` 异常消息包含诊断信息

### 第二步（如需，半天内）
5. `extract_pulse_current` 加日志
6. 考虑将 `±5%` 提取为 `PULSE_CURRENT_TOLERANCE` 常量（不急着做成可配置，先常量化）

### 第三步（技术债，排期做）
7. `listTestInfo` 重构为 dataclass（改动面大，需要与上下游协调）
8. `start_row=2` 提取为配置或常量

### 不建议做的
- ❌ 策略模式重构（只有一种设备类型，没必要）
- ❌ 支持多种步骤名变体（先确认用户是否真的遇到这个问题）
- ❌ 容差 UI 可配置（5% 是行业标准，改了反而可能引入错误）

## 六、一句话总结

**当前 pulse currents 逻辑的核心算法已经优化到位（numpy 广播 + searchsorted），不需要大改。最值得做的是加诊断可见性——让用户在分析失败时能看到"为什么失败"，而不是面对一个无意义的错误弹窗。架构层面的重构（策略模式、dataclass 化）是技术债，可以排期但不紧急。**
