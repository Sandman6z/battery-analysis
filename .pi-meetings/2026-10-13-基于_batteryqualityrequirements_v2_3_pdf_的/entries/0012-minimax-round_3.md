# MiniMax (Round 3): MiniMax Round 3：最终综合裁决——接受纠偏、放弃被说服立场、收敛最终建议

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
