# GLM (Round 3): GLM Final：收敛修复清单（P0–P5）、放弃立场声明与 PDF v2.3 合规总体结论

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
