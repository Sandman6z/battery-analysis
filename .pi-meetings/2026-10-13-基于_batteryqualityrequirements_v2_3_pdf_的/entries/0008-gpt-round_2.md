# GPT (Round 2): Round 2：裁定争议、纠举引证错误、重建优先级（P0=PDF 事实源仲裁）

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