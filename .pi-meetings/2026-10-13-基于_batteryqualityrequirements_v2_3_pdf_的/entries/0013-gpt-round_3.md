# GPT (Round 3): Final synthesis: 收敛为 P0–P4 共 7 项修复 + 3 项登记不动，总体结论"核心判定公式正确，风险集中在判定格选择的三处不同步"；吸收 DeepSeek 统一根因论和 is_freezer 内部 helper 修法、吸收 GLM 测试固化错误值的警告、维持三态判定方案。

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