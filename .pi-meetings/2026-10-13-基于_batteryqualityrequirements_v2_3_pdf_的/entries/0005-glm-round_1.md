# GLM (Round 1): 纠偏 + 独立核查：分档表矛盾、冷冻三口径、2.25V 错位与可执行修复清单

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