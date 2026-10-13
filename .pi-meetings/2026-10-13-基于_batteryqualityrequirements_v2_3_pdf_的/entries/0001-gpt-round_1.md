# GPT (Round 1): PDF 规则→代码映射的全景审计与检查策略

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
