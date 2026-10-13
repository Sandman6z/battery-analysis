# DeepSeek (Round 3): 四人共识收敛为 5 项确认缺陷 + 1 项前置仲裁 + 2 项观察项；总体结论：核心判定公式正确但"格选错→全错"是系统性硬伤，代码总体遵照 PDF 但存在 3 处静默偏离

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