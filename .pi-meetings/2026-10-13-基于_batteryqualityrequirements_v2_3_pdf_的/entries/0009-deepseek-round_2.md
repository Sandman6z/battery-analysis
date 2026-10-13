# DeepSeek (Round 2): 认领纠偏、复核争议点并重构优先级：三处"格选错"是同一根因

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
