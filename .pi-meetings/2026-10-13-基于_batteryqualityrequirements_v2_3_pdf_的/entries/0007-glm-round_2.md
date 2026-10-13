# GLM (Round 2): Round 2：以当前代码为基准裁决四方分歧，收敛为 8 步修复清单

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