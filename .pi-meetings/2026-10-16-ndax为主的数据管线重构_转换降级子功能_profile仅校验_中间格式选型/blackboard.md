# Meeting: ndax为主的数据管线重构：转换降级子功能、profile仅校验、中间格式选型
我是这么想的，ndax为主，把我们原来主UI上的第一个ndax转excel的功能去掉，变成一个子功能，和batterychartviewer一样，就放在它的上面作为一个按钮，点开才有这个功能
然后界面上不再通过xml的profile带出，通过ndax，依然能识别到其他所有的数据，这部分需要重新识别一下
profile的xml也还是自动查找，但是只进行验证，验证里面的脉冲电流和ndax的是不是一致，一致的话，就继续，如果不一致就报错。但是允许用户不提供xml，如果没有xml，弹框提示，允许继续，然后只依靠ndax分析，并声明一次
然后你具体分析是用excel还是现成转换ndax然后把excel放在临时文件夹，我觉得就按最高效率、最不容易出错误的方式，是不是还是将ndax转成csv或者excel格式，然后进行数据处理分析，最后得到结果，生成写入3_analysis results文件夹的相应版本的文件夹，再然后生成报告

Initial meeting folder: `C:\Users\boe\Documents\EwinDT\battery-analysis\.pi-meetings\2026-10-15-brainstorm-184239`

You are facilitating a round-robin brainstorming session using the MEETING BLACKBOARD.
Each consultant writes their FULL contribution to disk via meeting_append_entry.

## Consultants (3 rounds)
- **GPT**: use the gpt-brainstormer subagent. Visionary strategist.
- **DeepSeek**: use the deepseek-brainstormer subagent. Systems thinker.
- **MiniMax**: use the minimax-brainstormer subagent. Creative lateral thinker.
- **GLM**: use the glm-brainstormer subagent. Pragmatic implementer.

## PRE-ROUND STEP — Assign a Human-Readable Title

Before Round 1, choose a concise human-readable meeting title for "我是这么想的，ndax为主，把我们原来主UI上的第一个ndax转excel的功能去掉，变成一个子功能，和batterychartviewer一样，就放在它的上面作为一个按钮，点开才有这个功能
然后界面上不再通过xml的profile带出，通过ndax，依然能识别到其他所有的数据，这部分需要重新识别一下
profile的xml也还是自动查找，但是只进行验证，验证里面的脉冲电流和ndax的是不是一致，一致的话，就继续，如果不一致就报错。但是允许用户不提供xml，如果没有xml，弹框提示，允许继续，然后只依靠ndax分析，并声明一次
然后你具体分析是用excel还是现成转换ndax然后把excel放在临时文件夹，我觉得就按最高效率、最不容易出错误的方式，是不是还是将ndax转成csv或者excel格式，然后进行数据处理分析，最后得到结果，生成写入3_analysis results文件夹的相应版本的文件夹，再然后生成报告" and call:
  meeting_rename({ meetingDir: "C:\Users\boe\Documents\EwinDT\battery-analysis\.pi-meetings\2026-10-15-brainstorm-184239", title: "<your concise title>" })

Use the returned `newMeetingDir` for ALL subsequent meeting tools and subagent tasks. If rename fails, continue with the original meetingDir.

## CRITICAL INSTRUCTIONS

### Blackboard-first — do NOT paste prior participant text into subagent tasks

The meeting blackboard is the single source of truth. Subagent tasks must direct participants to READ from the blackboard, not receive pasted history.

- Round 1: subagents write initial analysis. No prior entries to read.
- Round 2: tell subagents to call meeting_read_index and meeting_read_entry on the current meetingDir to read Round 1 entries before responding.
- Round 3: tell subagents to call meeting_read_index and meeting_read_entry to read ALL prior round entries AND any User feedback entries from the blackboard.
- User feedback: if the user provides feedback that exists only in chat, APPEND it to the blackboard as `speaker: "User", phase: "Feedback after Round N"`, then tell participants to read it from the blackboard.

### For subagents (include in EVERY task):
1. When the task asks for prior context, read it from the blackboard using meeting_read_index and meeting_read_entry. Round 1 has no prior entries to read.
2. Write your FULL contribution using the meeting_append_entry tool with:
   - meetingDir: the current meetingDir (use the one returned by meeting_rename if rename succeeded)
   - speaker: your display name, e.g.:
   - speaker: "GPT"
   - speaker: "DeepSeek"
   - speaker: "MiniMax"
   - speaker: "GLM"
   - phase: "Round 1", "Round 2", or "Round 3"
   - summary: a ONE-SENTENCE summary of your contribution
   - content: your FULL analysis in Chinese (中文)
   - content must contain only the participant's analysis. Do not include wrapper tags, hidden thinking markers, tool-call text, or WROTE_ENTRY text inside content.
3. After writing, your FINAL ANSWER must be ONLY:
   `WROTE_ENTRY: <your one-sentence summary>`
4. DO NOT paste your full analysis into the chat. The main agent and user will read it from the blackboard.

### For you, the facilitator:
- Do NOT paste participant full text into chat. They are on the blackboard.
- Do NOT paste prior round content into subagent tasks. Tell subagents to read the blackboard.
- After each round, read the index with meeting_read_index and present a structural overview.
- Optionally read full entries with meeting_read_entry when needed.
- Present each consultant's summary + your structural overview (conflict matrix, consensus table).
- When the user gives feedback, append it to the blackboard as a User entry, then tell participants to read it.

## Protocol
Round 1: Each consultant gives initial analysis on the topic. Run all in parallel. Subagents do not need to read prior entries.
After Round 1: read the index, present summaries plus a structural overview, then STOP. Ask the user for feedback or permission to continue. Do NOT start Round 2 in the same assistant turn.
Round 2: only after the user replies, tell each subagent to call meeting_read_index and meeting_read_entry to read Round 1 entries, then challenge the others and propose improvements. If user feedback exists, append it to the blackboard first.
After Round 2: read the index, present summaries plus an updated structural overview, then STOP. Ask the user for feedback or permission to continue. Do NOT start Round 3 in the same assistant turn.
Round 3: only after the user replies, tell each subagent to read ALL prior round entries AND user feedback entries from the blackboard (via meeting_read_index and meeting_read_entry). Each gives FINAL recommendation, synthesizing the best ideas.

After Round 3, present the complete structural overview and ask whether to write the final conclusion. Only write conclusion.md after the user confirms.

## FAILURE HANDLING
Subagent calls can fail (timeout, API error, model unavailable, crash). You MUST detect and handle failures:

### Detecting failure
A subagent call has FAILED if:
- The tool result contains error text ("error", "failed", "timeout", "unavailable", "connection", etc.)
- The subagent returns no output or empty output
- The subagent output does NOT contain "WROTE_ENTRY:" (the expected success marker)
- The subagent produced no meeting_append_entry call (check with meeting_read_index after the parallel batch)

### Retry strategy
When you detect a failure:
1. Wait 5-10 seconds before retrying (API rate limits may have triggered the failure)
2. Retry the SAME consultant with the SAME task up to 2 more times (3 attempts total)
3. On retry, add to the task: "PREVIOUS ATTEMPT FAILED. This is retry N of 2. Focus only on completing your contribution and writing WROTE_ENTRY."
4. If the consultant succeeds on retry, proceed normally
5. If ALL retries are exhausted, treat this consultant as UNAVAILABLE for this round

### When a consultant is UNAVAILABLE
- Do NOT wait indefinitely or freeze the session
- Proceed with the remaining consultants who succeeded
- In your structural overview, clearly mark the failed participant as: "[displayName] ([agentName]): 本轮未响应 / did not respond"
- Continue to the next round normally — do NOT skip the consultant in future rounds (they may recover)
- If the same consultant fails in 2 consecutive rounds, warn the user with the real display name, e.g.: "DeepSeek 连续两轮失败，建议检查该模型是否可用"

### NEVER do this
- Do NOT fabricate or simulate a consultant's response
- Do NOT impose an extra manual timeout beyond the subagent tool's timeout; if the tool reports timeout, treat that attempt as failed
- Do NOT abort the entire session because one consultant failed

## IMPORTANT
- All responses in Chinese (中文).
- Save transcript.md and (after user confirms) conclusion.md per the MEETING OUTPUT PROTOCOL.
- The user can intervene at any time to steer the discussion.
> Created: 2026-10-16T00:38:20.266Z
> Type: Brainstorming (3 rounds)

---

## MiniMax (Round 1): 横向创意分析：五问深度评估与增强提案

# MiniMax Round 1 分析：从 ndax 废墟上重建信任

## 一、提案 A–D 横向评估

### 提案A：降级『ndax转excel』为主UI子功能

**合理性**：✅ 方向正确。ndax 本身已是完整数据容器，强拆成 excel 再处理是历史路径依赖。降级子功能让用户按需触发，减少强制转换的认知负担。

**风险**：
- 存量用户习惯突然改变，可能引发批量投诉（"我的工作流断了"）
- 子功能入口隐蔽，首次使用需要引导

**遗漏**：
- 没有定义"降级后原有 xlsx 兼容路径"——如果用户手里还有旧 xlsx，要不要支持？建议保留一个「导入已有 xlsx」的单次入口
- 缺少渐进迁移策略：存量数据如何一次性迁移？

**替代思路（横向创意）**：
> 不降级主 tab，而是新增「直接分析 ndax」入口作为默认，旧流程作为「兼容模式」在设置中可选。这样既保留旧用户路径，又逐步引导新习惯。

---

### 提案B：全部通过 ndax 识别数据

**合理性**：✅ 根本性正确。Step.xml 是「实际执行配方」而非「计划配置」，是最权威的数据源。文件名档位是历史遗留 bug 根源。

**风险**：
- Step.xml 的 `Limit` 截止条件与 profile 的 `Whole_Prt` 结构差异需要正确处理（背景已确认良性，但仍需代码体现这种"忽略差异"的逻辑）
- data.ndc 二进制解析依赖 NewareNDA 库，版本兼容性风险

**遗漏**：
- 没有说明「识别失败」的降级策略——如果 Step.xml 损坏，要不要 fallback 到 data.ndc 直接解析？还是报错？

**横向补充**：
> ndax 内置的元数据（TestInfo.xml 的 SN/开始时间）可以成为**数据血缘追踪**的基础——未来可以做到"这个报告对应哪批 ndax"的溯源能力，这是原方案完全缺失的。

---

### 提案C：profile 仅做验证

**合理性**：✅ 设计优雅。profile 是「计划」，ndax 是「执行」，用执行来验证计划符合度是合理的职责划分。

**风险**：
- 「不一致→报错」可能在边界情况过于粗暴——如果用户有合理的业务理由（比如临时调试改了档位）怎么办？

**边界情况深度分析**：
| 场景 | 建议策略 |
|------|---------|
| profile 有但 ndax 无对应档位 | 告警（Warning），显示缺失档位，允许继续分析有数据的部分 |
| ndax 有但 profile 无档位 | 告警，建议用户更新 profile 或确认是否遗漏配置 |
| 多 ndax 混合档位不一致 | 严重告警（Critical），列出所有不一致对，用户确认后才继续 |
| profile 文件损坏/解析失败 | 降级为「无 profile 模式」，弹框声明一次 |

**无 xml 弹框声明够不够？**
> 一次性的声明框容易被忽略，建议改成「首次无 xml 弹框 + 工具栏常驻警告图标（黄三角）」，直到用户手动确认为止。这样视觉上持续提醒，不会点完就忘。

---

### 提案D：中间格式选型

**我的明确建议：内存 DataFrame 直传 + parquet 作为可选缓存层**

**多维度论证**：

| 维度 | xlsx | csv | parquet | DataFrame 直传 |
|------|------|-----|---------|----------------|
| 序列化效率 | ❌ 最慢，百万行耗时 | ⚠️ 尚可 | ✅ 优秀，列式压缩 | ✅ 无需序列化 |
| 解析开销 | ❌ openpyxl 慢 | ⚠️ pandas read_csv | ✅ 极快 | N/A |
| 出错面 | ❌ 列名空格、合并单元格、格式丢失 | ⚠️ 编码问题、精度丢失 | ✅ 类型自描述 | ✅ 最小 |
| 可审计性 | ⚠️ 可人工打开 | ✅ 文本可见 | ⚠️ 需要工具 | ❌ 内存不持久 |
| 重复分析成本 | ❌ 需重新解析 | ⚠️ 需重新解析 | ✅ 可原地复用 | ⚠️ 需重新生成 |
| 改动量 | 已有大量代码 | 中等 | 中等 | 最大（需重构数据流）） |

**核心论点**：
- 当前管线 `ndax → xlsx → data_processor → 3_analysis` 存在两次磁盘 I/O 和一次格式转换，每次转换都是潜在出错点
- DataFrame 直传消除中间文件，但需要确保「错误时状态可复现」——所以 **parquet 作为可选缓存**（只在用户勾选「保存中间结果」时才写入）
- 改动量大的问题可以通过**渐进式重构**缓解：先保持 xlsx 路径，新增 DataFrame 直传路径为 experimental

---

## 二、『重新识别清单』——完整数据溯源

### 原来从哪里来

| 数据项 | 原来源 | 现在改从 ndax 哪里取 |
|--------|--------|---------------------|
| 脉冲档位（电流/时间） | 文件名解析 + profile 查表 | Step.xml `<PulseData>` |
| 电池 SN | 文件名或 profile | TestInfo.xml `<SerialNumber>` |
| 测试开始时间 | profile 或文件时间戳 | TestInfo.xml `<StartTime>` |
| 电流量程 | profile | TestInfo.xml `<CurrentRange>` |
| 原始脉冲数据（时序） | xlsx Record 表 | data.ndc（NewareNDA 解析） |
| 截止条件（Limit） | profile Whole_Prt | Step.xml `<Limit>` |
| Cycle/Step 编号 | xlsx Step 表 | Step.xml `<StepNumber>` |
| 工步类型（CC/CCCV 等） | xlsx Step 表 | Step.xml `<StepType>` |

### 哪些是 ndax 给不了的？

| 数据项 | ndax 能提供？ | 替代/兜底方案 |
|--------|--------------|---------------|
| 用户自定义备注 | ❌ 纯人工信息 | 保留文件名字段读取作为备注兜底 |
| 历史对比基准（上一批数据） | ❌ 跨文件概念 | 未来可扩展：基于 SN + 时间戳关联历史报告 |
| profile 中的 Whole_Prt 整机配置 | ⚠️ 部分有差异 | 记录差异为元数据，不影响分析 |
| 用户在 profile 的自定义计算公式 | ❌ 配置层 | 需在 UI 上单独迁移/映射 |

### 横向增强建议

> Step.xml 的 `<PulseData>` 可以反过来**生成 profile 缺失的档位信息**——如果用户导入一个完全没有 profile 的 ndax，系统可以自动「提议」生成一个 profile 模板。这样新用户无需手写配置文件。

---

## 三、Profile 验证边界——策略细化

### 不一致时的处理矩阵

```
ndax 档位 ⊆ profile 档位 → Warning + 缺失分析
ndax 档位 ⊇ profile 档位 → Warning + 额外数据
ndax 档位 ∩ profile 档位 = ∅ → Error（完全不一致）
ndax 档位 = profile 档位 → Pass（一致）
```

### 多 ndax 间档位不一致

**这是最复杂的边界**。建议分级处理：
1. **同批次分析内**多 ndax 档位不一致 → Critical，必须用户确认「以哪个档位为基准」或「分别分析」
2. **跨批次分析**多 ndax 档位不一致 → Warning，提示可能的数据来源混淆

---

## 四、空档位防御——明确意见

**明确建议：必须保留兜底，但实现方式升级**

现状：`data_utils.py:42` 的 `filtered_mask[0]=True` 越界是**最后一环**的防御缺口，当前管线修掉这个 bug 只能解决单一路径。

**升级方案**：
1. **上游拦截**：在 ndax 解析阶段（`converter.py` 或新增 `ndax_loader.py`）直接验证「Step.xml 档位 × 数据行数」的一致性，不一致则 abort 并给出具体哪个档位缺数据
2. **下游兜底**：保留 `filter_data` 的空档位处理，但改成 `filtered_mask[min(valid_idx, len(filtered_mask)-1)]` 避免越界，同时 log Warning 提示数据不完整

---

## 五、提案之外的增强点子

### 1. ndax 拖拽识别（Drag-and-Drop Intelligence）
- 用户直接把 ndax 拖入主界面，自动识别内部结构
- 如果检测到多个 ndax，弹出「批量分析」选项

### 2. 多档位并行分析（Multi-Profile Parallel）
- 同一批数据，支持按不同档位配置**并行生成多份报告**
- 特别适合研发场景：一批数据要同时按「软包规则」和「硬壳规则」出报告

### 3. 智能默认值（Smart Defaults）
- 当 profile 缺失且无法从 config 查表时，根据 TestInfo.xml 的 `CurrentRange` 和电池类型推断最可能的档位配置
- 推理结果写入日志，用户可事后确认修改

### 4. 校验可视化工具（Verification Dashboard）
- 新增一个「数据校验报告」tab，显示：
  - 每批次 ndax 的档位与 profile 对比（绿/黄/红）
  - 数据完整性评分
  - 历史迁移进度

### 5. 版本回溯（Report Versioning）
- 利用 ndax 内置的 `<StartTime>` + SN 实现**幂等报告**——同一个 ndax 文件，无论何时分析，结果应一致
- 写入 `3_analysis results` 时带上 ndax 的 hash 值，方便回溯

---

## 总结

| 评估项 | 我的立场 |
|--------|---------|
| 核心方向 | ✅ 全面转向 ndax 为权威数据源 |
| 中间格式 | 🏆 DataFrame 直传 + parquet 可选缓存 |
| profile 策略 | ✅ 仅验证，分级告警而非一刀切报错 |
| 空档位防御 | ✅ 必须兜底，上游拦截 + 下游容错 |
| 最大机会点 | Step.xml 反向生成 profile 模板，实现零配置新用户上手 |


---

## GLM (Round 1): GLM Round 1：最小改动路径与中间格式定论

# Round 1 · GLM（务实落地实现者）：五问分析

视角声明：我只关心三件事——改动量、回归面、能不能一周内跑通 5 个存量项目。以下所有结论按这个标准给。

## 一、提案 A–D 逐条评估

**A（ndax转excel 降级为子功能，同 batteryChartViewer 模式）——支持，改动最小。**
- 本质是 `src/battery_analysis/main/tabs/ndax_tab.py` 的 UI 重组：tab → 按钮 + 弹窗，`ndax/converter.py` 转换引擎零改动。工作量约 0.5–1 人天，回归面仅 UI 层。
- 风险：老用户习惯路径变化，需在按钮 tooltip/首次弹窗说明。不是技术风险。
- 遗漏：降级后该功能仍要保留完整能力（批量转换、多表拆分），因为 xlsx 仍是审计产物（见 D 的结论），不能"降级"成残缺版。

**B（不再通过 xml profile 带出数据，改 ndax 识别）——方向正确，但必须限定范围。**
- 正确之处：档位来源从"文件名（陈旧 Remark，已证实不可信）"切到 Step.xml/data.ndc，直接消灭本次崩溃根因。
- 关键限定：ndax 给不了全部语义字段。规格型号、成组方式、制造商、批次码这些业务语义仍只能来自文件名/profile/config（见第三问清单）。所以 B 的正确落地是"**仅档位（及可实测的 CC 电流、容量）改为 ndax 权威**，其余字段维持文件名解析不动"，而不是推倒重来。`data_processor.py:300-355` 里只动 `extract_pulse_current` 的优先级，`filename_parser` 其余调用原样保留——这样改动集中在一点。
- 风险：5 个存量项目需要回归验证档位识别结果。好消息是核验脚本已经跑过（4 项目全对、CF224642T 正确报不一致），把它固化成自动化测试即可。
- 遗漏：无 profile/无文件名语义时（CF224642T 正是 Rules 外型号），兜底链 Step.xml → data.ndc 实测 → config 查表，每层失败要有明确报错，不能静默空档位——那是原崩溃的触发条件。

**C（profile 只做验证；无 xml 弹框声明一次后放行）——支持，这是本次改动里性价比最高的部分。**
- 5 项目核验零例外（除 CF224642T 旧模板）证明 profile 与 Step.xml 天然一致，验证逻辑简单、误报率低。
- "声明一次"必须持久化（QSettings，见第四问实现细节），否则每次批量跑都弹框，用户会条件反射点确认，声明就失效了。
- 风险：profile 版本漂移（CF224642T 型）。验证失败恰恰是价值所在，不是缺陷。

**D（中间格式选型）——见第二问，结论：xlsx，写到项目内缓存目录而非 OS 临时目录。**

## 二、中间格式明确单选：**xlsx（放项目级缓存目录，转换结果直连后续分析）**

先给结论：**不要 csv、不要 parquet、第一期不要内存直传。用现成转换链产出 xlsx，落盘到受管理的缓存目录，后续管线原样读它。**

逐项对比：

| 方案 | 效率 | 出错面 | 可审计性 | 重复分析成本 | 既有改动量 |
|---|---|---|---|---|---|
| xlsx（缓存目录） | 中（calamine 读很快；写慢是现状已付成本） | 低——下游 `read_xlsx_sheets`/`battery_analysis.py:282`/figure_builder 全部不动 | 高：用户可直接打开与新威 GUI 导出比对 | 低：缓存命中则免重转 ndax | **最小**：只改输出路径+缓存清单 |
| csv | 中高 | 高：3 表拆 3 文件、编码（utf-8-sig）、日期/数值类型强转、读取端全部重写 | 中 | 同 xlsx | 大：`xlsx_reader.py` 重写 |
| parquet | 最高 | 中（类型安全但需 pyarrow 新依赖） | 低：无工具打不开 | 低 | 大：读取端重写 + 新依赖 |
| 内存 DataFrame 直传 | 最高 | 高：`data_loader.read_xlsx_sheets`、Info_Plot.json 流程、figure_builder 读文件路径的整条链全要改；崩溃即全丢 | 无中间产物 | 每次重跑都要重新 nda.read 解析 ndc | 最大 |

论证要点：
1. **出错面是第一权重**。本次议题的起因就是档位数据出错导致报告崩溃。xlsx 链路已被 5 个项目、41 个 ndax 实测验证过，Record_2/3 拆表、中英文表头映射都已处理（`converter.py:73-110`）。换任何格式都要重写读取端，等于在修 bug 的同时引入一批新 bug 面。
2. **效率账要算净增量**。真正慢的是 NewareNDA 解析 data.ndc，不是 xlsx 读写。保留 xlsx 缓存后，重复分析（改报告参数重跑是常态）直接命中缓存、**跳过最慢的 ndc 解析**——这比内存直传（每次重跑都重解析）在真实使用模式下更快。
3. **精度损失可忽略**：converter 现有 round(4) V / round(6) mAh / round(9) A，远低于报告和曲线精度要求，且是现状行为，零新增风险。
4. **parquet 留作后手**：如果未来 profiling 证明 xlsx 读写是热点，可在转换器内部加 parquet 缓存层，接口不变、决策可逆。现在不付这个复杂度。

**落地细节（D 的实现约定）：**
- 缓存目录建议 `2_xlsx/` 原位保留或 `项目根/_ndax_cache/`，**不要用系统 temp**——temp 会被清理，缓存命中和审计追溯都没了。
- 缓存失效判定：写一个 `manifest.json`，键 = ndax 文件名，值 = `{mtime, size}`；ndax 变了才重转。哈希不必上，mtime+size 足够。
- 主 UI 降级（A）与缓存目录不冲突：转换自动发生在分析前，"ndax转excel"按钮只是手动兜底入口。

## 三、"通过 ndax 识别其他所有数据"的重新识别清单

**ndax 三个成员能给的：**
- `Step.xml`（权威配方）：脉冲档位设定值（PulseData）、工步序列、单工步 Limit 截止条件（核验结论 4 已证实与 profile 差异为良性序列化差异）。
- `TestInfo.xml`：SN、测试开始时间（可用于批次/日期交叉校验）、电流量程。
- `data.ndc`（经 `nda.read` → DataFrame）：Cycle/Step/Status/Current(mA)/Voltage/Charge_Capacity(mAh)/Discharge_Capacity(mAh)/绝对时间——即现在 Record/Step/Cycle 三表的全部来源；**实测档位可由 Status=Pulse 分组的电流集合聚类得出**；CC 电流、实测容量同样可得。

**原来从 profile/文件名来、ndax 给不了的（必须保留原来源）：**
- 规格型号（CP224642A 等命名语义）——Step.xml 只有执行配方，没有型号命名；
- 成组方式（1S1P/1S2P）、制造商、批次码——纯业务语义；
- 标准要求侧（要求可用容量、规格方法）——来自 config Rules + PDF 标准，与数据文件无关。

**结论**：B 提案里"重新识别所有数据"应收敛为"档位 + CC 电流 + 容量实测改 ndax 权威，其余字段维持文件名/profile/config 来源不变"。`filename_parser` 的 spec/method/manufacturer/batch 四个调用点一行不动。

## 四、profile 验证策略的边界情况（含实现细节）

**1. 不一致：报错阻断 + 显式放行按钮，不是告警放行。**
理由：本次崩溃正是"不一致被放行"的产物；且 5 项目核验零误报说明真不一致时几乎必然是 profile 用错了。但完全硬阻断会卡住紧急分析，所以给弹窗两个按钮：[中止] / [以 ndax 实测为准继续]，用户点了"继续"才放行并记录日志。默认焦点在[中止]。

**2. 比对容差（分两层，不要一刀切）：**
- **设定值层（profile PulseData vs Step.xml PulseData）**：双方都是整数档设定值，容差 = 0（严格相等，比较前各自过 `normalize_current_levels` 规整）。档数不同直接判不一致，不逐项比。
- **实测层（Step.xml 设定 vs data.ndc/Record 实测）**：实测电流围绕设定值波动。取该档全部 Pulse 点电流的**中位数**与设定值比，容差 = max(设定值×1%, 0.5 mA)——覆盖 26mA 档 ±0.26mA 和小电流档的量化噪声。实测档位数（聚类后的 distinct 集合）≠ 设定档数 → 判不一致。
- 比对顺序：先做设定值层（快、准），通过后再做实测层（防"配方写了但没执行"）。

**3. 报错文案（草案，走 i18n `_()` 双语）：**
> 「脉冲电流档位不一致：profile『{profile_name}』设定 {profile_levels} mA；ndax『{ndax_name}』（SN {sn}）Step.xml 设定 {step_levels} mA，实测 {measured_levels} mA。请确认该 profile 是否为本电池的实际执行配方（注意年度模板复用导致的旧档位）。[中止] [以 ndax 实测为准继续]」

文案必须同时给出三个来源的值和 SN，让用户不用翻文件就能判断是模板问题还是数据问题。

**4. 无 xml 弹框"声明一次"的持久化：**
- QSettings 键：`battery_analysis/ndax/no_profile_ack_version`，值存**策略版本号字符串**（如 `"2026.10"`）而非布尔。验证策略或文案实质变更时递增版本号，用户会重新被提示一次——避免"三年前点的确认覆盖了新策略"。
- 声明内容明示后果：「无 profile 时档位完全以 ndax 实测为准，标准符合性无法交叉校验」。
- 机器级（QSettings）而非项目级：声明的是用户对风险的理解，不是对某批数据的判断，没必要每个项目重弹。

**5. 多 ndax 文件间档位不一致：**
- 同一分析批次先做批内一致性检查：所有 ndax 的 Step.xml 档位集合应相同（同型号同批的合理预期）。
- 不一致 → 报错并列出逐文件档位表，**禁止静默取并集或取第一个**——档位错一个，报告 16 只电池全崩，这正是前车之鉴。
- 弹窗给两个出路：[按档位分组分别分析] / [中止]。分组分析是锦上添花，第一期可以只做[中止]+清单，把分组留到确有此场景再加。

## 五、报告阶段空档位防御（filter_data 越界）：**仍需兜底，必须修，与 A–D 无关地修**

明确意见：**要，且是前置条件，不是可选项。**
- `src/battery_analysis/utils/processors/data_utils.py:42` 的 `filtered_mask[0] = True` 在空数组上必炸。即使档位来源全部改对，仍存在：测试中途终止（某档无 Pulse 数据）、数据导出缺行、用户手动改档位列表等路径，任何一条都能让空序列走到这里。
- 修法（约 5 行，回归风险极低）：`filter_data` 入口对每个 `(charge, voltage)` 对判 `len(charge_np) == 0` → 追加空列表并记 warning，跳过 numpy 分支；同时调用侧（plot/figure_builder）把"档位 {level} 无数据"写进报告 level 1，与现有空档位报告口径一致——让缺失可见，而不是画图时才发现。
- 原则：数据源修复（B/C）和消费端防御（本条）是两层独立的保险，前者不能作为取消后者的理由。

## 六、落地节奏建议（一句话版）

A（0.5–1 天）→ 五、空档位防御（0.5 天，先行修）→ C 验证 + 声明持久化（1–2 天）→ B 档位来源切换（2–3 天）+ D 缓存目录（0.5 天）→ 用现有 5 项目核验脚本固化为自动化回归测试收尾。全程 `converter.py` 引擎与 `xlsx_reader.py` 读取端零改动，回归面收敛在档位识别与验证逻辑两点上。

---

## DeepSeek (Round 1): 从数据流/模块契约/失败模式角度全面分析五问，指出档位来源切换是核心契约变更，中间格式应选内存DataFrame直传，filter_data越界必须兜底。

# DeepSeek Round 1 系统分析：数据流·模块契约·失败模式

---

## 一、逐条评估提案 A–D

### A. ndax 为主，降级为子功能

**合理性**：高。当前 ndax 是数据唯一权威来源（5 项目零例外验证），理应成为主入口。把 xlsx 转换降级为与 batteryChartViewer 同级的辅助工具，语义正确。

**风险**：
- **UI 入口重路由**：`ui_builder.py:53-55` 当前 `NdaxConverterTab` 是 Tab 0（主位）。降级需要改 `QTabWidget` 结构或改为按钮弹窗，涉及 `mw._ndax_tab` 引用链路（`ui_builder.py:65`）。需确认是否有其他模块通过 `mw._ndax_tab` 直接访问。
- **隐性依赖**：ndax_tab 内部的 `convert_batch` → `ProcessPoolExecutor` → `convert_one` 流程无变化，但主 UI 交互路径变了，原有"先转 xlsx 再点分析"的用户习惯需要引导。

**遗漏**：提案未提及 ndax 主入口的扫描逻辑——主分析 Tab（`battery_tab`）当前扫描 xlsx 文件，切换为 ndax 主入口后需要扫描 .ndax 文件，这是入口变更的连锁反应。

### B. 界面不再通过 xml profile 带出数据，改通过 ndax 识别

**合理性**：中高。ndax 的 `data.ndc` → DataFrame 包含 Status、Current、Voltage 等完整时序数据，足以支撑脉冲检测和等级匹配。

**风险——这是本次重构的核心契约变更**：
- **档位来源链路重塑**：当前 `data_processor.py:340-352` 的链路是 `文件名解析 → config 查表兜底 → 写入 config`。切换为 ndax 后，档位应从 `data.ndc` 的 Status=Pulse 行按电流值分组提取，替代文件名解析。这要求新增一个 `extract_pulse_levels_from_ndax(ndax_path)` 函数，并在 `data_processor` 中替换 `filename_parser.extract_pulse_current` 的调用。
- **下游 7 处读取 `pulseCurrents` 的位置全受影响**：
  1. `data_processor.py:349` → `mw.listCurrentLevel`
  2. `config_manager.py:34` → `BatteryConfig/PulseCurrent` 映射
  3. `data_loader.py:140` → `_get_pulse_current_level()` 读 config
  4. `battery_config_initialization_step.py:38` → 初始化
  5. `analysis_runner.py:155` → `_prepare_test_info`
  6. `report_coordinator.py:329` → 报告
  7. `quality_requirements.py:204` → 容量校验

  若档位从 ndax 实测提取，上述 1-7 的写入链路应统一为：ndax 提取 → 写入 config + `mw.listCurrentLevel`，下游读取端不需要改动（它们只关心 config 和 `mw.listCurrentLevel` 的值）。

**遗漏**：文件名仍需解析 SN、批次码、制造商等非档位信息。提案 B 说"通过 ndax 识别其他所有数据"，但 ndax 的 `TestInfo.xml` 不含制造商、批次码、规格型号——这些仍需从文件名或 UI 手动输入。需明确"重新识别"的边界。

### C. profile xml 仅做验证

**合理性**：高。profile 的 `<PulseData>` 与 ndax `Step.xml` 的 `<PulseData>` 经 41 个文件核验为良性序列化差异，仅做交叉验证是正确使用。

**风险**：
- **验证粒度**：仅比较脉冲电流档位集合（set 相等），还是逐一比较每个 pulse step 的电流值+持续时间？建议仅比较电流值集合（set），因为 profile 和 Step.xml 的工步编号/时序可能不同。
- **验证时机**：应在 ndax 档位提取完成后、进入分析流水线前执行。在 `data_processor` 中插入验证步骤。

### D. 中间格式选型

**合理性**：需要结合 B 的实施方案一并决策。详见下方五问二。

---

## 二、中间格式单选建议：**内存 DataFrame 直传**

### 多维度对比

| 维度 | xlsx | csv | parquet | 内存 DataFrame 直传 |
|------|------|-----|---------|-------------------|
| **效率** | 最差（xlsxwriter 写 + calamine 读，两次 I/O） | 中等（csv 快于 xlsx 但仍需磁盘往返） | 好（列式，但需额外依赖） | **最优**（零 I/O，Python 进程内直接传递） |
| **出错面** | 大（百万行拆表 Record_2/3、文件名行+表头行偏移、calamine 引擎兼容性） | 中（无拆表但仍有 header 行对齐问题） | 小 | **最小**（无序列化/反序列化，无格式歧义） |
| **可审计性** | 好（用户可打开 xlsx 检查） | 好 | 差（需专门工具） | 可通过新增"保存 xlsx"按钮按需导出 |
| **重复分析成本** | 低（已转 xlsx 可复用） | 低 | 低 | 需重新读 ndax（~秒级，可接受） |
| **改动量** | 零 | 小（改读取器） | 中（新依赖+读取器） | **中等**（核心改动在 `battery_analysis.py:277-386` 的 `_parallel_process_file`，当前从 xlsx 路径读取改为接收 DataFrame 参数） |

### 推荐理由

1. **消除最大失败源**：当前 `converter.py` 的 xlsxwriter 拆表逻辑（`_build_record_sheet` 63 行）和 `xlsx_reader.py` 的 read_xlsx_sheets 拼接逻辑（12-34 行）是维护负担最重的代码。百万行拆表→多表拼接是一对脆弱的映射关系，任何不对齐都会导致分析数据错位。内存直传彻底消除这段代码。

2. **converter.py 可大幅简化**：`convert_one` 当前写 Cycle/Step/Record 三张表，改为只返回 `(cycle_df, step_df, record_df)` 三个 DataFrame。用户需要 xlsx 时再调用 `_build_*_sheet` 按需导出。

3. **`read_xlsx_sheets` 成为可选路径**：保留作为兼容接口（用户手动打开已有 xlsx 时），但主路径变为 ndax → DataFrame 直传。

4. **改动范围可控**：
   - `converter.py`：`convert_one` 增加 `return_dfs=True` 模式
   - `battery_analysis.py`：`_parallel_process_file` 签名扩展为接受 DataFrame
   - 下游 `pulse_detector`、`pulse_matcher`、`charge_calculator` **不需要改动**（它们已经是 DataFrame → DataFrame 的纯函数）

---

## 三、"通过 ndax 识别其他所有数据"重新识别清单

### ndax 各子文件能提供什么

| 数据项 | Step.xml | TestInfo.xml | data.ndc | 原来源 | 能否替代 |
|--------|----------|-------------|----------|--------|---------|
| **脉冲电流档位** | `<PulseData>` 含真实电流值 | — | Status=Pulse 按 Current 分组 | 文件名解析 | ✅ **必须替代** |
| **测试开始时间** | — | `StartTime` 字段 | DataFrame Timestamp 首行 | xlsx Cycle 表首行 | ✅ |
| **SN / 设备信息** | — | `SN`、设备型号 | — | 无（从未提取） | ✅ 可新增 |
| **电流量程** | — | `CurrentRange` | — | 无 | ✅ 可用于校验 |
| **电池名 / 文件名** | — | — | — | **xlsx 文件名（行 0）** | ❌ ndax 文件名可能不含足够信息 |
| **制造商** | — | — | — | 文件名正则提取 | ❌ ndax 不含 |
| **批次码 / BatchDateCode** | — | — | — | 文件名正则提取 | ❌ ndax 不含 |
| **规格型号 (Specification Type)** | — | — | — | 文件名正则 + UI 选择 | ❌ ndax 不含 |
| **规格方法 (1S1P/1S2P)** | — | — | — | 文件名正则 | ❌ ndax 不含 |
| **构造方法 (Coin/Pouch)** | — | — | — | 文件名推断 + UI | ❌ ndax 不含 |
| **CC 恒流电流** | — | — | — | 文件名正则 | ❌ ndax 不含 |
| **测试日期** | — | `StartTime` 或 Cycle 首行 | — | xlsx 搜索 "Test Date" | ⚠️ 部分（ndax 有时间戳但格式不同） |
| **截止电压档位** | `<Limit>` 含截止条件 | — | — | config 固定值 | ⚠️ 可提取但无需（config 已固定） |

### 关键结论

- **能完整替代的**：脉冲电流档位（核心）、测试时间、设备信息
- **不能替代的**：制造商、批次码、规格型号/方法、构造方法——这些仍需从文件名解析或 UI 手动输入
- **实施方案**：ndax 入口下，`data_processor` 的识别链路变为：`ndax data.ndc 提取档位（权威） → 文件名解析剩余字段（兜底） → UI 手动补充 → profile xml 交叉验证`

---

## 四、profile 验证策略边界情况

### 4.1 不一致报错 vs 告警放行

**强烈建议：报错阻断，不允许放行。**

理由：
- 背景事实 3 证明 profile 与 ndax 一致性是可验证的，不一致意味着用了错误模板（如 CF224642T 崩溃案例）
- 档位错误会导致 `match_pulse_levels` 匹配不到数据 → 下游全部计算结果错误 → 报告无意义
- 如果放行，用户可能在不知情下生成错误报告，后果远大于中断流程

实现：验证失败时弹 `QMessageBox.Critical`，显示 `profile 档位: [x, y, z] ≠ ndax 实测: [a, b, c, d]`，提供"查看详情"和"关闭"按钮。不提供"忽略继续"按钮。

### 4.2 无 xml 弹框声明一次够不够

**不够，需要分两层处理**：

1. **首次无 xml**：弹 `QMessageBox.Information`，说明"未找到 profile xml，将完全依赖 ndax 数据分析"，提供"确定"和"选择 xml 文件"两个按钮。声明一次后记入该批分析的日志。
2. **批次级记忆**：同一目录下所有文件共享同一个分析批次，弹框一次合理。但应将"无 xml 警告"写入 `Info_Plot.json` 的 metadata 字段，使报告可追溯。
3. **不应静默跳过**：即使用户上次选了"确定"，下次新批次仍应弹框（新数据可能有新风险）。

### 4.3 多 ndax 文件间档位不一致

**这是提案未覆盖的关键场景**。

同一分析批次（同目录）的所有 ndax 文件理论上应使用相同测试配方。如果文件 A 实测 `[60, 30, 15, 6]`、文件 B 实测 `[100, 60, 30, 15, 6]`，说明：
- 可能是不同型号/容量的电池混放在同一批次
- 可能是测试设备配置变更

**处理策略**：
1. **预扫描阶段**：在 `convert_batch` 或新增的 `scan_ndax_batch` 中，先遍历所有 ndax 的 data.ndc 提取各自档位集合
2. **一致性校验**：档位集合不一致时，弹对话框列出差异，提供选项：
   - "以多数文件的档位为准"
   - "选择一个文件的档位"
   - "取消分析"
3. **运行时防御**：即使预扫描通过，`match_pulse_levels` 对每个文件独立匹配——如果某文件的某个档位无匹配数据，结果应为该档位数据缺失（留空），而非崩溃

---

## 五、报告阶段空档位防御（filter_data 越界）是否仍需兜底

**必须兜底，即使档位来源已修正。**

### 理由

1. **崩溃机制**：`data_utils.py:42` 的 `filtered_mask[0] = True` 在 `charge_np` 为空数组时 IndexError。当前触发条件是档位不匹配导致 `match_pulse_levels` 返回空的 position 列表 → `ChargeCalculator.calculate` 收到空输入 → 生成空数据传递给 `filter_data`。

2. **即使 ndax 实测提取了正确档位，仍存在空数据场景**：
   - 测试中途断电，某个档位的脉冲未完成（数据不全）
   - 数据采集异常，某个档位的脉冲行缺失
   - 文件损坏，`data.ndc` 部分可解析
   - 用户手动指定了错误档位（override 场景）

3. **防御是分层的**，应修三层：

   | 层级 | 位置 | 修复 |
   |------|------|------|
   | **L1 数据源** | `match_pulse_levels` 返回结构 | 已有：空数据返回 None，调用方 `battery_analysis.py:322` 检查 `pulse_mask.sum()==0` |
   | **L2 中间处理** | `ChargeCalculator.calculate` + 空数据传递 | **需补**：calculate 收到空 position 列表时返回空列表，不传给 filter_data |
   | **L3 终端过滤** | `data_utils.py:42` | **必须修**：`filtered_mask[0] = True` 前加 `if len(charge_np) == 0: return [], []` |

4. **这是独立于本次重构的安全修复**：无论档位来源如何改变，`filter_data` 的空数组防御都不应依赖上游保证。作为防御性编程的基本要求，应在本次重构中一并修复。

### 具体修复建议

`data_utils.py` 的 `filter_data` 函数中，每个内层循环的 `charge_np` 和 `voltage_np` 为空时应提前 continue：

```python
# data_utils.py filter_data 内层循环
for charge_data, voltage_data in zip(plt_charge_list, plt_voltage_list):
    if not charge_data or len(charge_data) == 0:
        plt_charge_filtered.append([])
        plt_voltage_filtered.append([])
        continue
    # ... existing logic
```

---

## 六、整体风险矩阵与建议优先级

| 风险 | 影响 | 概率 | 优先级 |
|------|------|------|--------|
| 档位来源切换导致下游 7 处读取不一致 | 崩溃/错误报告 | 中 | **P0** |
| 多 ndax 间档位不一致未处理 | 错误报告 | 中 | **P0** |
| filter_data 空数组越界未修 | 崩溃 | 高（已复现） | **P0** |
| 中间格式改动影响现有 read_xlsx_sheets 兼容性 | 崩溃 | 低 | P1 |
| UI 入口重路由影响用户习惯 | 体验退化 | 高 | P2 |
| profile xml 验证逻辑实现复杂度 | 延期 | 低 | P2 |

**建议实施顺序**：P0 filter_data 兜底 → P0 ndax 档位提取 + 多文件一致性 → P1 内存 DataFrame 直传 → P2 UI 重构 → P2 profile 验证。

---

## GPT (Round 1): 从架构愿景/长期演进/用户价值视角全面分析五问：A-D提案评估、中间格式单选xlsx落缓存目录、ndax重新识别清单、profile验证分层策略、filter_data兜底仍需。

# GPT 愿景战略家 — Round 1 完整分析

## 一、提案 A–D 逐条评估

### A. ndax 降级为子功能入口

**合理性：极高。** 当前 "ndax转excel" 占据主 Tab 首位，暗示 xlsx 是主角、ndax 是辅助——这与数据流事实完全相反。ndax 才是权威数据源（Step.xml 含真实档位，data.ndc 含原始时序），xlsx 只是中间衍生物。将 ndax 降为子功能入口（类似 batteryChartViewer 按钮展开），在视觉层级上修正了"中间格式 > 权威源"的错位。

**风险：低。** 改动仅限 UI 布局（ndax_tab.py 的 tab 注册 + 按钮触发），不涉及数据流逻辑。唯一注意：降级后入口发现性下降——新用户可能找不到 ndax 转换功能。建议在主 Tab 留一个"导入 ndax"的明显按钮（非隐藏），点击后展开完整转换面板。

**遗漏：** 未提及批量 ndax 导入的 UX 改善。当前批量转换需要用户手动选目录，未来可考虑拖拽 ndax 文件到主窗口直接触发分析。

### B. 数据识别从 profile/xml 切换为 ndax

**合理性：高，但范围需精确界定。** "通过 ndax 识别其他所有数据"是本次重构的核心契约变更。ndax 的三个文件确实携带了绝大多数必要信息（详见第三节清单），但原文表述"依然能识别到其他所有数据"过于乐观——有些信息 ndax 给不了，需要明确降级策略。

**风险：中高。** 这是本次改动中影响面最大的一项。当前 `data_processor.py:340-352` 的档位解析链是"文件名 → config 查表 → 存入 `mw.listCurrentLevel`"。切换为 ndax 权威后，整条链路的输入源、时序、错误处理都要重新设计。特别是：ndax 档位提取发生在 converter.py 解析阶段（`nda.read` + `Status==Pulse` 分组），而当前 data_processor 在 UI 层读 xlsx 才拿档位——两个阶段的时间差可能导致 UI 状态不一致。

**遗漏：** 提案 B 没有说明"识别"的边界。是仅指脉冲电流档位？还是包括型号、规格方法、制造商、批次日期码等全部 filename_parser 当前负责的字段？需要逐一定义。

### C. profile xml 仅做验证

**合理性：高。** profile 作为验证而非数据源是正确的分层——它本质上是"人写的期望值"，ndax 是"机器记录的实际值"。用期望值校验实际值，符合质量管控逻辑。

**风险：中。** "一致 → 继续，不一致 → 报错"的二元策略过于刚硬。实测发现 5 个项目中 4 个完全一致，唯一不一致的是 CF224642T（旧模板改文件名）——这种 case 应该允许用户选择"以 ndax 为准继续"而非硬阻断。如果硬阻断，用户唯一出路是删掉 xml 或改 xml，体验很差。

**遗漏：** 未提及 profile 验证的粒度。是只验脉冲电流档位？还是也验工步结构、截止条件？建议 Round 1 先定"只验脉冲电流"，后续迭代扩展。

### D. 中间格式选型

**合理性：问题定义正确，但需要收敛。** 这是一个典型的"别想太多，先做对"的决策点。详细论证见第二节。

**风险：** 选型本身风险低，但"按最高效率、最不易出错"的标准暗示可能存在过度优化倾向——对这个规模的数据（单文件百万行级、16 只电池），任何格式的 I/O 差异都在毫秒级，不值得为此增加架构复杂度。

---

## 二、中间格式：明确单选建议

### 建议：xlsx 落项目级缓存目录（非 OS temp），保留现有架构

**五维论证：**

| 维度 | xlsx（推荐） | csv | parquet | 内存 DataFrame 直传 | 混合 |
|------|-------------|-----|---------|-------------------|------|
| **效率** | 够用，百万行写入 ~2-5s，读取 ~1-3s | 最快写入，但读取需类型推断 | 最快读写，但引入 pyarrow 依赖 | 零 I/O，最快 | 取决于组合 |
| **出错面** | 最小——现有代码已验证，xlsxwriter 行为确定 | 中——编码/分隔符/类型推断陷阱多（中文列名、科学计数法） | 中——pyarrow 版本兼容、列类型映射 | 最小——纯内存，但跨进程传参需序列化 | 最大——多条路径意味着多套 bug |
| **可审计性** | 最高——用户可直接打开 xlsx 检查中间数据 | 高——文本可读，但不如 xlsx 结构化 | 低——二进制格式，需专门工具 | 无——内存数据无持久化 | 混乱 |
| **重复分析成本** | 低——已有 xlsx 直接复用，无需重新解析 ndax | 低——同上 | 低——同上 | 高——每次重分析必须重新解析 ndax | 取决于缓存策略 |
| **代码改动量** | 最小——保留现有 converter.py 输出 + data_loader.py 读取链路 | 中——需改写输出 + 读取逻辑 | 大——新增依赖 + 全链路适配 | 大——需重构 data_processor/data_loader/figure_builder 的整个调用链 | 最大 |

**核心论点：**

1. **xlsx 是当前架构的"脊柱"。** `converter.py` 用 xlsxwriter 写三表（Record/Step/Cycle），`data_loader.py` 的 `read_xlsx_sheets` 按表名读取，`plot_writer.py` 从 xlsx 生成 CSV 中间数据。整条链路已经过 5 个项目全量核验，是已验证的路径。
2. **"效率"在此场景是伪命题。** 单文件百万行 xlsx 写入 2-5 秒、读取 1-3 秒——对电池分析场景（用户等的是报告生成，不是中间格式转换）完全可接受。为省这几秒引入 parquet 依赖或内存直传的架构复杂度，ROI 为负。
3. **可审计性是隐性刚需。** 当分析结果异常时，工程师需要检查中间数据（"转换后的 xlsx 对不对？"）。xlsx 可直接用 Excel 打开，csv 也可但结构化差，parquet 和内存数据无法直接检查。
4. **重复分析成本是关键差异。** 内存 DataFrame 直传方案看似优雅，但意味着每次重分析（调参、换电池组合）都要重新解析 ndax——ndax 解析耗时远超读 xlsx。保留 xlsx 作为缓存，用户可以"转换一次，分析多次"。
5. **缓存目录建议用项目级 `2_xlsx/`（现有路径），不用 OS temp。** OS temp 会被清理工具删除，且多项目并行时文件名冲突。现有 `2_xlsx/` 已经是事实标准，保持不变。

**唯一改进点：** 当前 converter.py 总是写满三张表。如果只为分析（不为人工审阅），可以只写 Record 表（Step/Cycle 可从 Record 聚合）。但这是优化，不是必须——先保持现状，后续有性能问题再改。

---

## 三、ndax 重新识别清单

### ndax 三个文件各自能给什么

| 信息项 | 来源文件 | 提取方式 | 当前来源（需替换） |
|--------|---------|---------|------------------|
| **脉冲电流档位（权威）** | Step.xml `<PulseData>` | XML 解析，取各 Pulse 工步的电流值去重排序 | 文件名正则 `extract_pulse_current` + config 查表兜底 |
| **工步结构（搁置/恒流放电/脉冲顺序）** | Step.xml 完整工步定义 | XML 解析 | 无（当前不解析 Step.xml） |
| **截止条件（Limit）** | Step.xml 单工步 Limit 节点 | XML 解析 | 无（当前不使用） |
| **电流量程** | TestInfo.xml | XML 解析 | 无（当前不使用） |
| **序列号（SN）** | TestInfo.xml | XML 解析 | 文件名猜测 |
| **测试开始时间** | TestInfo.xml | XML 解析 | 文件名中的批次日期码 |
| **原始时序数据（电流/电压/容量/状态）** | data.ndc | NewareNDA `nda.read` → DataFrame | xlsx Record 表 |
| **循环号/工步号/状态分类** | data.ndc | `nda.read` 输出的 Cycle/Step/Status 列 | xlsx Record 表 |

### 原来从 profile xml 来的、ndax 给不了的

| 信息项 | profile xml 来源 | ndax 能否替代 | 降级策略 |
|--------|-----------------|-------------|---------|
| **Whole_Prt 整机保护配置** | profile 多出的节点 | ❌ 给不了 | 该信息不参与数据分析（取证事实 #4），直接丢弃 |
| **记录配置（采样频率等）** | profile 记录配置段 | ❌ 给不了 | 同上，不参与分析 |
| **用户自定义的工步名称/备注** | profile 工步备注 | 部分——Step.xml 有工步名但可能不同 | 不影响数据分析 |

### 原来从文件名来的、ndax 替代方案

| 信息项 | 文件名解析（当前） | ndax 替代 | 可靠性对比 |
|--------|------------------|----------|-----------|
| 脉冲电流档位 | 正则 `\(([\d.]+[-\d.]+)mA` | Step.xml PulseData | ndax 更可靠（文件名来自陈旧 Remark） |
| 型号/规格类型 | 文件名关键词匹配 | TestInfo.xml（有限） | 文件名更丰富（含中文型号名），ndax 可能只有代码 |
| 规格方法（1S1P） | 文件名关键词匹配 | ❌ ndax 无此字段 | 保留文件名解析或 config 查表 |
| 制造商 | 文件名关键词匹配 | ❌ ndax 无此字段 | 保留文件名解析或 config 查表 |
| 批次日期码 | 文件名正则提取 | TestInfo.xml 开始时间 | 可互补，ndax 更精确 |
| 容量（用于查表） | 文件名正则提取 | ❌ ndax 直接给电流不给容量 | ndax 不需要容量（直接有档位） |

### 关键结论

**ndax 能完全替代文件名解析的核心功能（脉冲电流档位），且更可靠。** 但文件名仍携带型号、规格方法、制造商等 UI 填充信息——这些 ndax 给不了。建议分层：
- **必选信息（档位）：** 100% 切换到 ndax Step.xml
- **UI 填充信息（型号/规格/制造商）：** 保留文件名解析作为默认值，ndax TestInfo.xml 作为补充校验
- **不可替代信息（规格方法、容量查表）：** 保留现有逻辑

---

## 四、profile 验证策略边界情况

### 4.1 不一致时：报错 vs 告警放行？

**建议：分层策略，而非一刀切。**

- **第一层（设定值 vs 设定值）：** profile xml 中的脉冲电流是人写的设计值，ndax Step.xml 中的是机器实际执行值。两者的比较本质是"设计意图 vs 实际执行"。
  - **数值完全一致：** 静默通过，日志记录。
  - **数值不一致但属于已知规格层级差异（如 profile 写 30/26/15/6，ndax 实测 60/30/15/6）：** 这正是 CF224642T 的 case——旧模板未更新。此时应 **告警 + 允许用户选择"以 ndax 为准继续"**，而非硬阻断。硬阻断迫使用户去改 xml 或删文件，增加无谓操作。
  - **数值完全不匹配（档位数都不一样）：** 阻断 + 提示"数据可能不完整，请检查"。

- **第二层（实测数据验证）：** 可选的更深层验证——从 data.ndc 的 `Status==Pulse` 分组统计实际出现的电流值，与 ndax Step.xml 声明的档位比对。这能发现"Step.xml 声明有 4 个档位但实测只有 3 个"的情况（如某个档位的工步被跳过）。建议作为后续迭代，不在 Round 1 范围内。

### 4.2 无 xml 弹框声明一次够不够？

**够，但需要持久化声明记录。**

- "声明一次"的语义是"本项目无 profile，所有结果仅基于 ndax 数据"。这个声明应该：
  1. **写入分析结果目录**（如 `3_analysis results/{date}_v{ver}/NO_PROFILE_DISCLAIMER.txt`），让报告审阅者知道此批结果无 profile 校验。
  2. **存入 QSettings 按项目维度**（不是全局），避免下次打开同一项目又弹框。
  3. **弹框内容要明确**：不是简单的"未找到 xml"，而是"未找到 profile xml 文件，将仅使用 ndax 数据进行分析。分析结果将不包含 profile 交叉验证。是否继续？"

- **不够的场景：** 如果用户在同一目录下混放了不同型号的 ndax 文件（部分有 xml、部分没有），"声明一次"会掩盖部分文件无校验的事实。建议：如果同一批次中部分有 xml、部分没有，按文件粒度提示（"3 个文件有 profile 校验，2 个文件无 profile"）。

### 4.3 多 ndax 文件间档位不一致怎么办？

**这是一个被忽略的重要边界情况。** 当前流程假设同一批次的所有 ndax 文件档位相同（基于"同型号同批次"的业务假设）。但现实中：

- **同批次不同模组可能有不同档位配置**（如高低温测试只跑部分档位）
- **测试中途修改配方**（工程师调试时改了后半段的档位）

**建议策略：**
1. **解析阶段：** 每个 ndax 文件独立提取档位，汇总到一个 `{filename: [档位列表]}` 字典。
2. **校验阶段：** 取所有文件档位的并集作为 `listCurrentLevel`，而非假设全部一致。
3. **报告阶段：** 对每个文件，只画它实际有的档位曲线，缺失的档位标注"N/A"。
4. **告警：** 如果同批次文件间档位数不一致，在 UI 上提示"批次内档位不一致，已取并集"。

---

## 五、filter_data 空档位防御是否仍需兜底

### 明确意见：必须兜底，且应作为本次重构的前置修复项

**理由：**

1. **根因未消除。** 当前 IndexError 发生在 `data_utils.py:42` `filtered_mask[0]=True`（空数组越界）。根因是 `listPlt[c]` 中某个档位的充放电数据为空列表（因为文件名解析出 4 个档位但实测只有 3 个有数据）。即使切换到 ndax 识别档位，仍然存在"ndax 声明有 4 个 Pulse 工步但某个工步实际无数据点"的边界情况——比如测试中断、工步被跳过、数据采集故障。

2. **防御是分层架构的基本纪律。** 在"数据源 → 中间格式 → 分析 → 报告"的管线中，每一层都应该对输入做基本的合法性检查。"上游修好了所以下游不用防"是经典的架构反模式——上游的 bug 会变种重现，下游的防御成本极低（一个 `if len(data) == 0: skip`），不防的代价极高（整个报告崩溃）。

3. **修复成本极低。** `data_utils.py` 的 `filter_data` 函数只需在循环头加一个空数据检查：
   ```python
   for charge_data, voltage_data in zip(plt_charge_list, plt_voltage_list):
       if not charge_data or not voltage_data:
           plt_charge_filtered.append([])
           plt_voltage_filtered.append([])
           continue
   ```
   同理 `data_loader.py:403` 的 `_filter_all_data` 已有 `if self.listPlt[c][0] and self.listPlt[c][1]` 检查，但缺少对空子列表的防护。

4. **时间顺序上应该先修。** 本次重构会改变档位来源（从文件名到 ndax），在过渡期间（部分项目用旧逻辑、部分用新逻辑），空档位风险反而更高。先修好防御，再改数据源，是更安全的顺序。

**建议：** 将 `filter_data` 空档位防御作为 P0 修复项，在 ndax 重构之前单独提交。这不是"兜底"，而是"基本功"。

---

## 六、整体战略建议

### 重构路径（推荐顺序）

1. **Phase 0（前置，1-2 天）：** 修复 `filter_data` 空档位防御 + 加单元测试。独立于主重构，可立即合并。
2. **Phase 1（核心，3-5 天）：** 实现 ndax 档位识别（Step.xml PulseData 解析）→ 替换 `data_processor.py` 的文件名解析链路 → 保留 config 查表兜底。
3. **Phase 2（验证，2-3 天）：** 实现 profile xml 验证层（只验档位，分层告警/阻断）→ 无 xml 声明机制。
4. **Phase 3（UI，1-2 天）：** ndax 降级为子功能入口 → 5 个项目全量回归测试。

### 长期愿景

这次重构的本质是**建立"数据源权威性层级"**：ndax（机器记录）> profile xml（人写期望）> 文件名（用户约定）> config（默认值）。这个层级一旦建立，未来扩展新数据源（如云平台 API、数据库直连）时，只需定义它在层级中的位置，而非重新设计整条链路。

中间格式选 xlsx 不是妥协，是务实——它让这条链路的每一步都可检查、可复现、可回溯。等项目规模增长到需要优化 I/O 时（比如千电池级别），再引入 parquet 或内存直传也不迟——但那是 Phase 10 的事，不是现在。

---

## DeepSeek (Round 1): 从数据流/模块契约/失败模式角度全面分析五问，指出档位来源切换是核心契约变更，中间格式应选内存DataFrame直传，filter_data越界必须兜底。

# DeepSeek Round 1 系统分析

## 一、核心数据流与模块契约地图

当前管线的档位（pulse currents）数据流如下，这是本次重构的核心契约链：

```
文件名 extract_pulse_current()
        │
        ├─ 有值 ──→ _verify_pulse_currents() 双重校验 ←─ config 查表 lookup_pulse_currents()
        │                    │
        └─ 无值 ──→ 查表兜底 ──→ normalize_current_levels()
                                        │
                                        ▼
                    mw.listCurrentLevel ← 存入 → config.set("battery.pulseCurrents", ...)
                                        │
                                        ▼
                    data_processor.py: listTestInfo[14] = listCurrentLevel
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
            battery_analysis.py   info_csv_writer.py   Info_Plot.json
            (pulse_matcher匹配    (Info_Image.csv      (下游BatteryChartViewer
             档位到数据行)         写入posi/charge/voltage) 读取元数据)
```

关键依赖：**listCurrentLevel 是整条管线的单一真相来源**。一旦档位错误，下游全部级联失败——不是优雅降级，而是 IndexError 崩溃（data_utils.py:42 `filtered_mask[0]=True` 越界）。

## 二、提案 A–D 逐条评估

### A. ndax 转 excel 降级为子功能

**合理性**：高。当前 UI 把"ndax转excel"放在首位暗示它是主入口，但实际上用户最终要的是分析报告，不是中间 xlsx。降级为子功能符合用户目标。

**风险**：
- 改动极小（UI 层：ndax_tab.py 嵌套进一个按钮即可），不触碰数据流
- **遗漏**：降级后用户发现"先转换再分析"的两步流程变得不直观。建议保留快捷入口（右键菜单或工具栏按钮），而非完全埋入

**结论**：支持，低风险。

### B. 不再通过 xml profile 带出数据，改由 ndax 识别

**合理性**：中等偏高，但存在关键契约缺口。

**需要重新识别的数据清单（第3题详细展开）**：ndax 内嵌的 Step.xml 和 TestInfo.xml 能提供大量元数据，但有 3 项 xml profile 有而 ndax 没有的：
1. **Whole_Prt 整机保护配置**（背景事实4已确认为"良性差异，不参与数据分析"）
2. **容量规格（mAh）**——ndax TestInfo.xml 有电流量程但无额定容量，而 lookup_pulse_currents 依赖容量做查表
3. **规格方法（1S1P/1S2P 等）**——文件名可提取，但无文件名时缺失

**风险**：如果 B 完全切断 profile，档位识别退化为"文件名解析 + ndax 实测"，config 查表机制失去数据源（查表需要 spec_name + capacity）。这意味着 **Proposal B 实质上需要 ndax 层补充容量/规格识别能力**。

**遗漏**：未提及 ndax 的 TestInfo.xml 是否包含容量信息。如果 TestInfo.xml 有额定容量字段，B 可行；如果没有，需从其他途径获取（如用户手动输入或 config 规则表匹配文件名前缀）。

### C. profile xml 只做验证

**合理性**：高。这是风险最低的渐进方案。

**风险**：
- 验证逻辑设计不当会导致"误杀"——profile 有合理差异（如四舍五入精度、单位 mA vs A）时不应报错
- **关键边界**：profile 的脉冲电流值与 ndax Step.xml 的 PulseData 实测值之间，允许的容差是多少？pulse_matcher 用 ±5%，但配置设定值应该精确匹配（0 容差）

**遗漏**：C 提案未说明验证失败后的恢复路径——是阻断还是放行？用户能覆盖吗？

### D. 中间格式选型

**合理性**：问题定义正确。当前"先转 xlsx 再读 xlsx"是 I/O 冗余。

**评估**：见第三部分单选建议。

## 三、中间格式单选建议

### 推荐：**内存 DataFrame 直传**

**五维论证**：

| 维度 | 内存 DataFrame 直传 | xlsx | csv | parquet |
|------|-------------------|------|-----|---------|
| **效率** | 零 I/O，O(1)传递 | 双重序列化（写+读），百万行文件 5-10s | 比 xlsx 快但仍需 I/O | 读写快但需额外依赖 |
| **出错面** | 无格式解析错误 | xlsxwriter/ openpyxl 版本差异、分表拼接 bug | 编码/分隔符问题 | pyarrow 版本耦合 |
| **可审计性** | 无落盘审计（需补偿） | 人可直接打开 | 人可直接打开 | 需工具打开 |
| **重复分析成本** | 需重跑 ndax 解析（~1s/文件） | 直接读缓存 xlsx | 直接读缓存 csv | 直接读缓存 |
| **代码改动量** | 中：需重构 data_processor 入口 | 零：现状 | 小：改写入格式 | 中+新依赖 |

**关键论证**：
1. **效率决定性优势**：NewareNDA `nda.read()` 解析单个 ndax ~0.5-1s，而 xlsxwriter 写百万行再 openpyxl 读回需要 5-10s。16 电池批量分析时差距扩大到分钟级。
2. **出错面最小**：当前 converter.py 的分表逻辑（Record/Record_2/Record_3）和 read_xlsx_sheets 的拼接逻辑都是 bug 温床。直传消除整个环节。
3. **可审计性补偿方案**：提供"保存调试副本"开关——需要时将 DataFrame 导出为 xlsx 到 2_xlsx/，但不作为主数据通道。这样兼顾了日常效率和异常排查。

**架构变更**：converter.py 的 `convert_one()` 改为 `parse_ndax()` 返回 DataFrame，`convert_one()` 降级为可选的落盘包装器。data_processor.py 接受 DataFrame 参数而非 xlsx 路径。

**改动量评估**：约 3-4 个文件需修改（converter.py、data_processor.py、ndax_tab.py 调用链、battery_analysis.py 入口），涉及函数签名变更。中等复杂度但可分步推进。

**降级方案**：如果 DataFrame 直传的改动量在工期上不可接受，**xlsx 落项目级缓存目录**是务实次选（GLM 的建议），但必须修复分表拼接的已有风险。

## 四、ndax 重新识别清单

通过 ndax 识别替代 profile xml 时，逐一分析：

| 数据项 | 原来源 | ndax 可替代？ | 替代路径 | 风险 |
|--------|--------|-------------|---------|------|
| **脉冲档位（mA）** | 文件名解析 | ✅ Step.xml `<PulseData>` | 从 Step.xml 提取 Pulse 节点的电流值 | 权威来源，比文件名更可靠 |
| **电流量程** | profile xml | ✅ TestInfo.xml | `TestInfo.xml` 含 CurrentRange | 无风险 |
| **SN / 电池编号** | 文件名 / profile | ✅ TestInfo.xml | SN 字段 | 无风险 |
| **测试开始时间** | xlsx 文件名 | ✅ TestInfo.xml | StartTime 字段 | 无风险 |
| **温度条件** | 文件名 | ⚠️ 部分 | ndax 文件名通常含温度信息，但非结构化 | 需保留文件名解析 |
| **额定容量（mAh）** | profile + config 规则表 | ❌ **缺失** | ndax 无额定容量字段 | **关键缺口**：lookup_pulse_currents 依赖容量查表 |
| **规格型号** | profile + 文件名 | ⚠️ 部分 | 文件名可提取，但无法覆盖所有情况 | 与现况一致 |
| **规格方法（1S1P等）** | 文件名 | ⚠️ 部分 | 同上 | 现有默认 1S1P 机制可兜底 |
| **Whole_Prt 整机保护** | profile xml | ❌ 不需要 | 背景事实4确认为良性差异 | 无风险 |

**核心缺口**：额定容量。ndax/TestInfo.xml 不包含此信息，而它是 `lookup_pulse_currents()` 的关键入参。B 方案若完全切断 profile，当文件名也无法提取容量时，档位查表失效，只能依赖 ndax 实测档位或用户手动输入。建议：
- 优先从 config 的 `BatteryConfig/Rules` 按型号前缀匹配容量（现已有此逻辑）
- 次选：从 ndax Pulse 实测电流反推容量档（观察到 60mA 脉冲 → 大概率 1200-2000mAh 区间）
- 兜底：弹框让用户选择规格型号，再查表

## 五、profile 验证策略边界情况

### 5.1 不一致报错 vs 告警放行

**建议：分级处理**

- **设定值层面（config 查表 vs profile xml）**：应精确匹配（0 容差）。查表结果是标准定义，profile 也是人工维护的，两者不一致说明某一方有错（如 CF224642T 用了旧模板），应 **阻断 + 显示差异详情 + 提供"以 ndax 为准继续"按钮**
- **实测层面（ndax Pulse 实测 vs 设定值）**：允许 ±5% 容差（与 pulse_matcher 现有契约一致）。超出则告警但默认放行——BTS 设备的电流输出有物理公差

### 5.2 无 xml 弹框声明一次够不够

**不够**，但可以改进为够用：
- 声明应包含具体信息："未找到 profile xml，将完全依赖 ndax 数据进行分析。档位识别来源：[ndax Step.xml / config 查表 / 文件名解析]"
- 声明状态应持久化到本次分析的结果目录（写入 Info_Plot.json 的 `profile_source` 字段），供报告审计追溯
- 不需要每次弹框——同一 ndax 文件集 + 同一次分析会话只弹一次，跨会话重分析则重新弹

### 5.3 多 ndax 文件间档位不一致

**这是真实风险**。同一批次的 16 个电池理论上应该相同，但如果操作员在测试中途改了配方，不同电池可能有不同的脉冲档位。

**建议**：
- 第一个 ndax 解析后记录档位为基准
- 后续 ndax 解析时比对：一致则静默通过，不一致则弹框列出哪些文件有差异，让用户选择"以第一个为准 / 分组处理 / 全部中止"
- 当前管线假设所有电池档位相同（`listCurrentLevel` 是单一列表），如果允许不一致，下游 `battery_analysis.py` 和 `figure_builder.py` 需要支持多档位集——这是较大改动，建议 MVP 阶段先做"检测 + 报错"

## 六、filter_data 空档位防御——必须兜底

### 结论：**必须修，且应在本次重构之前或同时修复**

**理由**：

1. **crash 路径清晰**：当 `listCurrentLevel` 指定的某档位在实测数据中不存在时，`pulse_matcher` 的 `match_pulse_levels()` 返回该档位的位置列表为空 → `battery_analysis.py` 传给 `filter_data()` 的对应子列表为空 → `data_utils.py:42` 的 `filtered_mask[0] = True` 在空数组上越界 → **IndexError → 整个报告崩溃**。

2. **本次重构不能消除此风险**：即使 ndax 成为档位权威来源，仍存在：
   - BTS 设备跳过某档位测试（操作员手动中止某工步）
   - ndax 文件损坏导致部分数据缺失
   - 用户手动指定错误档位（config 覆盖场景）
   
3. **防御层次建议**：
   - **第一层**（pulse_matcher 输出）：返回时标记哪些档位无数据（已有 `None` 返回，但仅限全部无数据的情况）
   - **第二层**（battery_analysis.py）：遍历 listCurrentLevel 时，检查 `listLevelToRow[i]` 是否全为空 → 跳过该档位 + 日志警告
   - **第三层**（data_utils.py `filter_data`）：函数入口检查 `if not charge_data` → 直接 append 空列表，不执行 `filtered_mask[0] = True`。**这是最小改动、最大收益的必修项**

4. **改动量**：data_utils.py 加 2 行防御代码（`if not charge_data: ... continue`），测试补一个空列表 case。0.5 小时可完成。

### 优先级声明

filter_data 越界修复是 **P0 级 bug fix**，不应等待本次重构的架构决策。它可以在独立分支上先修复并合入，然后本次重构在此基础上调整档位来源。

---

## 七、总结：推荐实施路径

| 优先级 | 任务 | 依赖 |
|--------|------|------|
| P0 | filter_data 空档位防御（data_utils.py + 单测） | 无 |
| P1 | C 方案：profile xml 仅做验证（含分级处理逻辑） | P0 |
| P1 | B 方案：ndax 识别替代 profile 数据带出 | P0 + C |
| P2 | D 方案：DataFrame 直传（或 xlsx 缓存降级方案） | P1 |
| P3 | A 方案：UI 降级 ndax 转 excel | 独立 |

---

## MiniMax (Round 2): MiniMax Round 2 辩论

# MiniMax Round 2 辩论

---

## 议题1：中间格式——主链路 DataFrame 直传，审计层 xlsx manifest 管控

### 对 xlsx 缓存方案的最强攻击

xlsx 方案的真实伤害不在"写盘慢"（5-10s 对整体流程是小头），而在**路径依赖引发的系统脆弱性**：

1. **converter.py 已有 XLSX 脆弱映射**：现有 `read_xlsx_sheets` 拼接逻辑是 Round 1 已确认的"已验证的脆弱映射"，在它上面再叠一层 xlsx 写→读循环，相当于在危楼地基上继续盖楼。
2. **审计缓存与主逻辑耦合**：一旦 xlsx 缓存进入主链路，后续所有依赖 ndax→DataFrame 的组件都必须处理"缓存存在时跳过重算"的分叉逻辑——等于把缓存一致性维护的复杂度扩散到整个代码库。
3. **无法向后兼容过渡**：重构期新旧逻辑并存时，xlsx 缓存的 mtime/size 失效策略需要精确对齐 converter 内部状态，而 ndax 结构随时可能变（用户已在引入临时文件夹提案）。

### 我方退让：接受"审计缓存"需求，但拒绝进入主链路

audit 需求是合理的（GPT 提出的"重复分析免重转"也有价值），但实现位置应在**主链路下游**，用 manifest 控制：

```
DataFrame 直传（主链路，无任何中间文件）
    ↓
report_writer 写报告前
    ↓
if audit_mode: write xlsx to 3_analysis results/{date}_v{ver}/cache/
               update manifest.json (ndax_path, mtime, size, parquet_path?)
```

这样 xlsx 永远不在计算主链路中出现，converter 的脆弱映射与它无关，且 manifest 可追踪"这份 xlsx 是哪次 run 的哪个 ndax 生成的"。

### 混合方案成立的条件

- **主链路**：内存 DataFrame，无中间文件
- **审计层**（可选开关）：manifest.json + 按需 xlsx 落盘，manifest 记录 cache hit 逻辑
- **pyarrow 问题**：审计层 xlsx 不需要 pyarrow，用 openpyxl 即可（已有 xlsx 写能力）
- **用户新提案（临时文件夹）**：临时文件夹用于中间结果（parquet 可选缓存），3_analysis results/{date}_v{ver}/ 用于最终报告，两层分离清晰

**结论**：主链路 DataFrame 直传单选，审计 xlsx 缓存作为独立可选层，不进 converter。

---

## 议题2：profile 不一致——四级告警矩阵收敛为分层决策树

### 合并各家合理元素

| 层级 | 条件 | 动作 | 放行按钮 | 留痕 |
|------|------|------|----------|------|
| **L1 阻断** | 档数不一致（子集/超集/不相交） | 弹框阻断，NDaxWizard 不可继续 | 无 | 写 Info_Plot.json `profile_mismatch: {type: "slot_count_mismatch", slots: {...}}` |
| **L2 阻断（可放行）** | 档位数相同，设定值层不一致 | 弹框阻断，显示 diff | "以 Step.xml 为准继续" | 同上 `type: "setpoint_mismatch"` |
| **L3 告警** | 档位数相同，设定值一致，实测值层超限（>5%） | 黄三角 toast，可继续 | 无按钮（自动放行） | 写 `type: "measured_deviation"` |
| **L4 通过** | 全部一致 | 静默 | 无 | 无 |

**CF224642T case 命中 L2**：档位从 30/26/15/6 → 60/30/15/6，档数相同但设定值有差异——验证器拦住此处，弹出 diff 框，"以 Step.xml 为准"放行按钮存在，用户知情+可追溯。

**放行按钮文案**（采纳 DeepSeek 的"以…为准"语义）：`「以 Step.xml 为准，继续分析」`；L1 无按钮是因为子集/超集意味着档位定义本身已被破坏，继续输出无意义。

**留痕字段**（Info_Plot.json）：
```json
"profile_validation": {
  "xml_found": true,
  "xml_path": "...",
  "result": "setpoint_mismatch_allowed",  // 或 blocked/measured_deviation
  "slots": {
    "xml": [30, 26, 15, 6],
    "step": [60, 30, 15, 6]
  },
  "user_override": true,
  "timestamp": "..."
}
```

---

## 议题3：多 ndax 档位不一致——MVP 仅检测+告警，二期留并集接口

### 承认我 Round 1 方案的错误

Round 1 我提出"并集+告警"，但**下游链路是单一列表**（listCurrentLevel/intCurrentLevelNum/figure_builder/plot_writer 全链路假设统一档位），并集意味着：

- 下游 4 个模块全部需要改造 list→list-of-lists
- listCurrentLevelNum 假设单一 int，现在可能是 [3, 4, 5]
- figure_builder 每张图需要决定"用哪组档位画哪组数据"

真实工作量估计：5-7 个文件改动，触及所有数据消费端，测试用例翻倍。

### MVP 收敛方案（采纳 GLM 的"只做检测+中止"合理内核）

**第一期 MVP（强制）**：
- 多 ndax 加载后比对档位：`assert all(ndax.slots == ref.slots)`，不一致则弹框并中止
- 弹框内容：显示各文件档位列表，用户确认"使用哪个文件为基准"或"中止"
- 报告头注明"本次分析包含 N 个 ndax，档位已对齐"

**二期接口（预埋）**：
```python
# data_loader.py
def load_multi_ndax_with_union(ndax_files, mode="strict"):  # "strict" | "union"
    # mode="union" 时，返回 (merged_df, slot_union, per_file_slot_map)
    # figure_builder 接收 slot_union 并处理 N/A 档位
```

### 为什么二期才做并集

- 并集的价值只在"同一个分析中必须同时呈现所有档位数据"时才成立——这个需求从未被用户明确提出
- 当前主要场景是"批量处理多个相似电池文件"，每个文件独立分析，并集无意义

---

## 议题4：无 xml 声明持久化——三层叠加

### 采纳 GPT 的 Info_Plot.json 方案（最佳可追溯性）

这是最合理的持久化方案——直接进报告归档，不需要额外的文本文件。

### 采纳 GLM 的 QSettings 版本号方案（防重复弹框）

QSettings 存键 `profile_disclaimer_version`，值 `"2026.10"` 或 `True`，首次弹框后写入，下次进入检测版本号，版本不变则不重复弹。

### 维持我的"首弹+黄三角常驻"作为 UI 层

黄三角不是持久化机制，是**当前会话内的可见性提示**——即使声明已写进 Info_Plot.json，用户在分析过程中仍需感知"当前无 profile，正在以 Step.xml 为准"。

### 最终三层设计

| 层次 | 机制 | 触发时机 | 目标 |
|------|------|----------|------|
| **P1 弹框** | QMessageBox 一次 | 会话首次检测到无 xml | 用户知情 |
| **P2 常驻提示** | QLabel 黄三角，status bar | 当前 session 无 xml | 分析过程可见性 |
| **P3 持久化** | Info_Plot.json `no_profile: {version: "2026.10", timestamp: "..."}` | 每次写报告前 | 报告可追溯 |

**QSettings 键名**：`AnalysisSession/no_profile_disclaimer_acknowledged`（含版本，版本变了则重新弹）

**Info_Plot.json 字段**：
```json
"no_profile": {
  "acknowledged": true,
  "version": "2026.10",
  "timestamp": "...",
  "note": "Analysis conducted without profile XML; step values from Step.xml used as reference."
}
```

---

## 实施顺序 + 改动文件清单

### Phase 1（P0，阻断崩溃）
1. `data_utils.py` — filter_data 空档位防御（已裁决，立即修）
2. `data_loader.py` — profile_validator.xml_profile_validator，档位一致性验证，命中 L1/L2 时弹框阻断
3. `main_window.py` — profile 不一致弹框 UI，L2 放行按钮逻辑

### Phase 2（P1，本会议题落地）
4. `data_loader.py` — 多 ndax 一致性检测，弹框+中止（MVP）
5. `info_plot_writer.py` — profile_validation / no_profile 字段写入
6. `config.py` — QSettings 键定义
7. `main_window.py` — 无 xml 首弹 + 黄三角 status bar 提示
8. `report_writer.py` — 审计 xlsx 缓存逻辑（manifest 管控，可选）

### Phase 3（预留）
9. `data_loader.py` — load_multi_ndax_with_union(mode="union") 接口预埋
10. `figure_builder.py` — slot_union 处理，N/A 档位展示

---

**收敛声明**：MiniMax 在议题1、2、4均接受混合方案收敛；议题3主动撤回并集方案，改为 MVP 检测+二期接口。


---

## GLM (Round 2): GLM Round 2 辩论

# GLM Round 2 辩论

## 议题1：中间格式 —— 我方改判，单选「内存 DataFrame 直传」

**结论：单选内存 DataFrame 直传 + 会话内缓存复用；xlsx 仅由已裁决降级的『ndax转excel』按钮按需导出，不进主分析链路。**

### 我方（xlsx缓存）最强论证，先摆出来

1. **审计刚需**：电池测试报告是工程交付物，客户质疑某只电池数据时要能打开中间数据人工核对。DataFrame 转瞬即逝，xlsx 是唯一人肉可读载体。
2. **内存压力**：converter.py 的 XLSX_MAX_ROWS=1_048_576 说明 record 表能逼近百万行；16 文件 × 百万行 × 十来列 float64，会话内全量驻留内存可能上 GB，Windows 上不是闹着玩的。
3. **已验证路径**：read_xlsx_sheets 的拆表/续表跳2行拼接虽然脆弱，但它是目前唯一被实测验证过的读取路径，DataFrame 直传是新代码。

### 为什么我放弃：诚实评估后的三个事实

1. **性能叙事被实测数据推翻**：nda.read ≈1s/文件，而 xlsx 写+读 5–10s/文件。缓存存在的全部意义是"花一次成本换后续快"，但这里后续读 xlsx（数秒）比直接重解析 ndax（1s）还慢——**缓存比它要替代的操作更贵**。16 文件首次分析：直传 ≈16s，xlsx 路径 ≈16s + 80–160s 写盘。这不是权衡问题，是被数据单方面否决。
2. **审计有更便宜的替代**：裁决1已把『ndax转excel』降级为子功能按钮——人工审计需求由按钮按需导出满足；程序化追溯由结果目录 3_analysis results/{date}_v{ver}/ 落关键提取字段（档位、循环数、每电池摘要）满足。为低频审计在主链路常驻 5–10s/文件的写盘成本，是拿高频操作付低频需求的账。
3. **脆弱映射能少走就少走**：拆表续表那套映射（converter.py:33, xlsx_reader.py:12-17）是已识别的脆弱面。直传方案让主链路根本不经过它，攻击面缩小；xlsx 往返只在用户显式点按钮时发生。

### 混合方案评估

「DataFrame 直传主链路 + manifest 控制的 xlsx 落盘缓存兼审计」——**部分成立但不值得**。混合里的 xlsx 腿只服务"跨会话加速"，而实测时序证明该加速为负。混合实质退化为「直传 + 按钮导出」，那就不叫混合，叫直传加一个已有的按钮。Round 1 我提的 manifest(mtime+size) 机制随按钮缓存的实现保留（若按钮选择落盘 2_xlsx/），主管线不依赖它。

### 回应用户新提案（中间格式放临时文件夹）

反对。Windows 临时目录受清理策略支配，审计时文件可能已经没了——临时 xlsx 既不快（同 5–10s/文件）又不可靠（会被清），两头的好处一个不占。结果落 3_analysis results/{date}_v{ver}/ 部分采纳：落的是**分析结果与关键提取字段**，不是全量中间数据。

### 内存压力的解法（回应我自己的论证2）

会话级缓存 dict（analysis_runner 持有 parsed DataFrames），重复分析（高频操作）零成本命中；会话结束即弃，下次重解析 1s/文件完全可接受。不做 LRU 不做落盘——等真实 OOM 出现再说，届时最便宜的修复是只缓存 step/cycle 层、record 层按需重解析，仍不需要 xlsx 中间层。

---

## 议题2：profile 不一致分层决策树

**结论树：**

```
Step.xml PulseData（ndax，权威） ← 自动查找同目录 profile xml
├─ 未找到 profile → 弹框声明（QSettings 版本号记忆，见议题4）→ 放行，留痕
├─ 档位数不同 → 阻断，无放行按钮
├─ 档位值不同·设定值层（容差 0，逐项精确比对）→ 阻断弹框
│     列出双方档位+差异高亮；[以 ndax 为准继续]为次要按钮，默认焦点=[中止]
│     点继续 → 留痕后放行
├─ 档位值不同·实测层（容差 max(1%, 0.5mA)）→ 黄色告警，默认继续，留痕
└─ 全部一致 → 静默通过，logging.info
```

- **档位数不同必须硬阻断无放行**：intCurrentLevelNum 驱动全部下游表格/图/统计（data_loader.py:88,305,318，statistics_utils.py:14,31 等全按它建矩阵），数不同 = 下游必然错位，没有任何"继续"语义成立。
- **CF224642T 正是值层拦截的意义**：profile 30/26/15/6 vs Step.xml 60/30/15/6，档位数相等（4=4），只查档位数会漏过。设定值层容差 0 才能拦住它——这也是我对"只做轻量检查"的所有折中方案的否定理由。
- **对 DeepSeek「硬阻断无放行」的回应**：设定值层确实该阻断，但不给放行按钮过刚。profile 是人工产物，可能过期/复制错目录；ndax 已裁决为权威，知情用户应能显式继续。放行的安全性由留痕保证，不由禁止保证。
- **对 GPT「值差异仅告警」的回应**：CF224642T 就是设定值差异且直接触发崩溃的 case，把它降为告警等于验证器形同虚设。设定值层和实测层必须分治——实测层有仪器噪声（我的 max(1%,0.5mA) 对 DeepSeek 的 ±5%：5% 太宽，60mA 档 3mA 偏差已属异常），设定值层没有噪声借口。

**留痕设计（写 Info_Plot.json 顶层新字段，与议题4共用）：**

```json
"profile_check": {
  "profile_found": true,
  "result": "pass | warned | overridden | blocked",
  "profile_levels_ma": [30, 26, 15, 6],
  "ndax_levels_ma": [60, 30, 15, 6],
  "user_action": "continue_with_ndax | abort | null",
  "checked_at": "ISO8601"
}
```

---

## 议题3：多 ndax 档位不一致 —— MVP = 检测 + 中止

**结论：第一期只做检测+中止（弹框列出每个文件的档位与差异，引导用户核对文件）；二期接口预留，优先做「以基准为准、跳过不匹配文件」；并集放最后或不做。**

### 并集方案的真实工作量（grep 已核实）

单一列表假设遍布全链路，改并集意味着：

- `src/battery_analysis/main/visualization/data_loader.py:88`（intCurrentLevelNum=len）、`:305`（行布局 1+intCurrentLevelNum×3）、`:318`（矩阵索引）
- `src/battery_analysis/main/visualization/figure_builder.py:62,273`
- `src/battery_analysis/main/visualization/battery_selection.py:157,289`（_battery_line_indices 行索引推导）
- `src/battery_analysis/main/visualization/filter_controls.py:52-55`
- `src/battery_analysis/utils/writers/statistics_utils.py:12-46`（compute_list_cpt/compute_statistics 按 intCurrentLevelNum×intVoltageLevelNum 建满矩阵——缺档位后均值/中位数/箱线图全要定义 N/A 语义）
- `src/battery_analysis/utils/report_coordinator.py:101,418,522`（报告正文、图标题、图例）
- `src/battery_analysis/utils/writers/excel_overview.py:42-174`、`csv_writer.py:86-174`、`excel_report_writer.py`、`word_front_matter.py:135-163`（所有 writer 表格形状）

≥12 文件、每个 writer 的表结构变化、统计 N/A 语义、图例/颜色/行索引三处推导重写。**诚实估计：2–4 周纯开发 + 全 writer 回归**，且新增"部分电池缺某档位"这个 bug 面。收益场景是"用户故意混装不同档位电池进一个批"——低频，且这类批在议题2的设定值检查下多半本来就该被拦。

**检测+中止的成本：批量加载入口一次逐文件比对 + 一个弹框，1–2 天含测试。** 收益成本比差两个数量级。

**接口预留**：一致性检查函数返回结构化结果 `{consistent: bool, base_levels_ma: [...], per_file: {filename: levels}}`，调用方据此决策。二期若真出现合法混装需求，先做 DeepSeek 基准方案的最小版——以第一个文件为基准、不匹配文件跳过并告警（单一列表不变量保持，改动只在加载端过滤，估 2–3 天）。并集永不进 MVP。

---

## 议题4：无 xml 声明持久化 —— 主方案 QSettings 版本号 + 叠加 Info_Plot.json 每次留痕

**结论：QSettings 存策略版本号为主，Info_Plot.json 留痕为强制叠加项，黄三角状态栏提示为二期可选叠加。**

- **QSettings 键名**：`validation/profile_disclaimer_version`，值为策略版本字符串（首发 `"2026.10"`）。免责文案/检查策略变更时 bump 版本 → 老用户重新弹框。用版本号而非 bool：改文案不需要担心已确认用户被旧声明覆盖。
- **对 GPT 项目级 NO_PROFILE_DISCLAIMER.txt 的回应**：项目目录会被拷贝/重命名/换机器，txt 跟着目录走，换个数据集仍带着"已声明"状态，语义错位；且每个数据目录多一个噪音文件。QSettings 键跟安装走，粒度对。
- **对 DeepSeek 会话级弹一次的回应**：太碎。同一项目重复分析（高频操作）每次启动都弹 = 训练用户无脑点确认，声明失去知情意义。
- **报告可追溯（目的b）必须每次运行写**：复用议题2的 `profile_check.profile_found: false`——无 xml、通过、告警、放行四种状态统一进这一个字段，两个议题一套机制，不另发明字段。
- **MiniMax 黄三角**：采纳为低优先级叠加——状态栏常驻图标，hover 提示"本批次未经 profile 验证"。成本一个控件，二期。

---

## 实施顺序 + 改动文件清单

1. **P0（全票前置）**：`src/battery_analysis/utils/processors/data_utils.py` filter_data 循环头加 `if not charge_data: append([]); continue`；`src/battery_analysis/utils/processors/charge_calculator.py` L2 空位返回空；`tests/` 补边界用例（空档位电池、全空批）。
2. **ndax 直读**：新增 `src/battery_analysis/ndax/loader.py`（Step.xml PulseData → 内存 DataFrame，含会话级缓存 dict）；`src/battery_analysis/main/managers/analysis_runner.py` 持有缓存并接入。
3. **profile 验证器**：新增 `src/battery_analysis/utils/validators/profile_validator.py`（议题2决策树）；弹框接入 `src/battery_analysis/main/ui_components/`。
4. **留痕**：`src/battery_analysis/utils/writers/info_csv_writer.py` write_info_plot_json 增加 profile_check 参数；调用点 `src/battery_analysis/utils/processors/battery_analysis.py:479` UBA_WriteCsv 传参。
5. **多 ndax 一致性检查**：`src/battery_analysis/ndax/loader.py` 批量入口实现，返回结构化结果 + 中止弹框。
6. **UI 降级**：`src/battery_analysis/main/ui_components/` 主 tab 改子功能按钮；`src/battery_analysis/ndax/converter.py` 保留原样服务按钮。
7. **结果目录**：`3_analysis results/{date}_v{ver}/` 路径生成（strResultPath 来源处，battery_analysis.py / report_coordinator.py）。

每步独立可测、可单独提交；1–2 是其余全部的地基，顺序不可换。

---

## GPT (Round 2): GPT Round 2 辩论

# GPT Round 2 辩论（四议题收敛）

> 开场声明：**议题1我改判**。Round 1 我站「xlsx 落 2_xlsx 缓存」，本轮在性能账重算后倒向 DataFrame 直传。立场变更的理由放在议题1内，不回避。

---

## 议题1：中间格式 —— 单选【内存 DataFrame 直传 + 会话内指纹缓存】

**结论**：单选 DataFrame 直传。xlsx 退出主链路，降级为审计副本（新数据集首次分析落一份）与「ndax转excel」子功能的导出格式；混合方案的 manifest 思想保留，「缓存」语义废弃。

### 对 xlsx 阵营的最强论证：xlsx 当数据契约会真实伤害这个项目

1. **脆弱映射是主链路必经之路**。`src/battery_analysis/ndax/converter.py:33` `XLSX_MAX_ROWS = 1_048_576` 分表 Record_2/3 + `src/battery_analysis/utils/readers/xlsx_reader.py:12` `read_xlsx_sheets` 拼接，是已验证的脆弱映射。16 文件 × 百万行 = 每次批量都在掷骰子，且一旦拼接错位，错误数据会静默流进报告。
2. **性能账算不平，"重复分析免重转"是幻觉**（这是我改判的直接原因）：`nda.read` 重解析 ~1s/文件 = 16s/批；而 xlsx 写+读 5-10s/文件中读回约占一半（2-4s/文件 ≈ 32-64s/批）。**缓存命中比重解析还慢**，写 xlsx 的 3-6s/文件是纯沉没成本。重复分析是高频操作，每一次都被 xlsx 税抽血。
3. **Windows 特有伤害**：百万行 xlsx 被 Excel/资源管理器预览占用时写入失败（文件锁）；杀毒软件实时扫描拖慢写入；单文件数十 MB × 16 的磁盘与备份负担。

### 诚实自评：DataFrame 阵营的真弱点

无落盘审计、崩溃后无凭据排查、批量中途失败全量重跑。这些是真的，但解法不是"把 xlsx 当数据契约"，而是审计副本 + 会话缓存（见下）。

### 混合方案诚实评估：「主链路 DataFrame 直传 + manifest 控制的 xlsx 落盘缓存兼审计」

- **当缓存：不成立**。读路径按数字永远不划算，却要完整保留分表写 + 拼接读两套脆弱代码——纯负资产。
- **当审计副本：成立**，但砍掉"缓存"语义后它只写不读，本质是"随报告归档的转换快照"，与已裁决的「ndax转excel」子功能共用同一导出代码即可，不构成第二条数据通道。
- **可保留的部分**：manifest（数据集指纹 = 路径 + 文件名集 + mtime + size）不驱动 xlsx，改驱动 ①会话内 DataFrame 缓存（改参数重跑零重转，彻底解决高频重复分析）②审计副本仅在新数据集首次分析时落盘一次。

### 用户新提案（临时文件夹 + 3_analysis results/{date}_v{ver}/）的采纳与修正

- 持久结果 → `3_analysis results/{date}_v{ver}/`：**采纳**。
- 中间产物 → 临时文件夹：**采纳但修正一处**——审计副本不进临时目录。审计件要随报告可追溯，应放 `3_analysis results/{date}_v{ver}/0_convert/`；临时目录只放可再生的调试 dump（按需）。

**最终单选：内存 DataFrame 直传（+ 会话内指纹缓存）**。无新依赖（pyarrow 不需要、pickle 不用）、脆弱映射整体退役出主链路、重复分析最快（会话内 0s / 跨会话 16s）、Windows 文件锁问题消失。

---

## 议题2：profile 不一致 —— 两层决策树

**结论（决策树）**：

```
输入 profile xml + ndax Step.xml PulseData
├─ 无 xml → 弹框声明一次 → 放行（已裁决，留痕见议题4）
├─ 层1 设定值层比对（0 容差：档数 与 逐档值）
│   └─ 不一致（含 CF224642T: 30/26/15/6 vs 60/30/15/6）→ 阻断
│      弹窗给逐档对照表 + 按钮【以 ndax 档位为准继续（记录差异）】
│      默认焦点 =【中止】→ 显式放行后留痕
└─ 层2 实测层比对（Step.xml PulseData vs 实测电流中位数，容差 max(1%, 0.5mA)）
    └─ 超差 → 黄色告警横幅 + 继续分析 → 留痕 warning（不阻断）
```

- **层1 采用 GLM 的 0 容差 + 阻断 + 显式放行**。关键理由：CF224642T 是档数相同、档**值**差异（30/26/15/6 vs 60/30/15/6）——若按我 R1"值差异仅告警"，这个崩溃 case 会被放过去，验证器就白建了。我修正自己 R1 的分层阈值：**档数不同与值不同同属设定值层、同为 0 容差阻断**，差异类型只影响留痕里的 `mismatch_type`。
- **层2 容差采纳 GLM 的 max(1%, 0.5mA)**（中位数比对），比 pulse_matcher 的 ±5% 严。两者职责不同：±5% 是匹配契约，max(1%, 0.5mA) 是体检告警阈值，漂移早发现；层2 不阻断（BTS 电流输出有物理公差）。
- **放行按钮文案**：【以 ndax 档位为准继续（记录差异）】（i18n key：`validation.override_continue`），默认焦点在【中止】，防手快。
- **放行留痕**：写 Info_Plot.json，字段 schema 见议题4（同一字段承载，不散落别处）。

---

## 议题3：多 ndax 档位不一致 —— MVP 检测+阻断+剔除，二期留并集接口

**结论**：MVP = 批内两两比对 Step.xml PulseData → 不一致弹框列出差异文件 →【剔除异常文件继续】/【中止】。**不做并集、不做自动分组**。

### 对并集方案（含我 R1 自我修正）

下游 `listCurrentLevel` 是单一列表——`src/battery_analysis/main/visualization/data_loader.py`（intCurrentLevelNum）、`src/battery_analysis/main/visualization/figure_builder.py`、`src/battery_analysis/utils/writers/plot_writer.py`、`src/battery_analysis/utils/writers/info_csv_writer.py`（Info_Image.csv posi 列）、`src/battery_analysis/main/business_logic/data_processor.py`（listTestInfo[14]）全链路按"统一档位集"假设写死。并集 = 全链路改造：档位索引→档位键重构 + N/A 渲染（图上缺口线段会误导读图）+ 报告版式回归。**诚实估 3-5 人日**（编码 2-3 + 版式/视觉回归 1-2）。触发场景却罕见（操作员中途改配方），且真发生时"剔除/分批"几乎总能覆盖。ROI 不成立，二期再议。

### 对 DeepSeek「基准 + 三选」

"以第一个为准"是危险默认——第一个文件凭什么是基准？"自动分组"= 一次操作出两份报告 + UI 状态分叉，一期不值，用户手动分两次跑即可。三选里两选都是坑，MVP 只留安全的两选。

### 对 GLM「纯检测 + 中止」

无放行路径太硬。真实场景"16 个里 1 个档位不同，剔掉继续"是刚需，纯中止会逼用户手动移文件。补【剔除异常文件继续】就是完整 MVP。

### 二期接口

Step.xml 解析时天然产出 `levels_by_file` 映射，数据层保留在解析结果元数据里（不进 listCurrentLevel）；若混档需求真出现，并集改造立专项。MVP 工作量 ≈ **0.5-1 人日**（解析层比对 + 弹框 + 剔除）。

---

## 议题4：无 xml 声明持久化 —— Info_Plot.json 为主，QSettings 免打扰，黄三角常驻

**结论**：主方案 = Info_Plot.json `profile_validation` 字段（审计）+ QSettings 指纹键（免重复弹框）；可叠加 = MiniMax 的黄三角常驻（成本近零、视觉持续提醒，好点子）。**撤回我 R1 的项目级 NO_PROFILE_DISCLAIMER.txt**：目的 (a)(b) 均被上述组合覆盖，报告目录多一个游离文本反而破坏 `{date}_v{ver}` 目录整洁。诚实说：我 R1 低估了 Info_Plot.json 已是 BatteryChartViewer 元数据入口（`src/battery_analysis/main/visualization/data_loader.py:105`）这一事实——那里才是可追溯的自然落点。

### 具体设计

```json
"profile_validation": {
  "result": "no_profile | ok | mismatch_overridden | measured_warning",
  "profile_levels": [30, 26, 15, 6],
  "ndax_levels": [60, 30, 15, 6],
  "mismatch_type": "count | values | none",
  "decision": "use_ndax | abort | remove_files",
  "policy_version": "2026.10",
  "ack_time": "2026-10-16T10:00:00"
}
```

- **QSettings 键**：`validation/policy_version = "2026.10"`（策略升级后重新弹）；`validation/no_profile_ack/<dataset_fingerprint>`（fingerprint = sha1(目录 + 排序文件名 + size + mtime)，同一数据集不重复弹，换数据集重弹）。
- **黄三角**：主窗状态栏常驻，点击展开差异详情，用户确认后消失——Info_Plot.json 留痕永久。
- **职责一句话**：QSettings 只管"别烦我"，Info_Plot.json 只管"可追溯"，二者不互相备份（换机器/归档场景 QSettings 不可见，它绝不能当审计）。

---

## 实施顺序 + 改动文件清单

**P0（独立先行，半天）**
- `src/battery_analysis/utils/processors/data_utils.py` — filter_data 循环头空档位防御（`if not charge_data: append([]); continue`）
- `src/battery_analysis/utils/processors/charge_calculator.py` — 上游空位列表返回空
- `tests/test_battery_analysis_pandas.py` — 补空档位 case

**P1（议题2+4，同一 Info_Plot.json schema，一次交付）**
- 新增 `src/battery_analysis/utils/validators/profile_validator.py` — profile 读取 + 两层比对（纯函数，可单测）
- `src/battery_analysis/utils/processors/battery_analysis.py:479` — Info_Plot.json 写 `profile_validation` 字段
- `src/battery_analysis/main/business_logic/data_processor.py` — 档位权威切 Step.xml + 调验证器 + 层1 阻断钩子
- `src/battery_analysis/main/workers/analysis_worker.py` — 阻断/放行流转
- `src/battery_analysis/main/window_init.py` / `window_actions.py` — QSettings 键 + 黄三角状态栏

**P2（议题1，DataFrame 直传）**
- `src/battery_analysis/ndax/converter.py` — 新增 `parse_ndax() -> DataFrame` + 会话指纹缓存；`convert_one()` 降级为导出包装器（子功能/审计副本共用）
- `src/battery_analysis/utils/processors/battery_analysis.py:282` — 入口接受 DataFrame，`read_xlsx_sheets` 调用移出主链路
- `src/battery_analysis/utils/readers/xlsx_reader.py` — 保留，仅供"导入旧 xlsx"兼容路径
- `src/battery_analysis/main/business_logic/data_processor.py` — 透传 DataFrame

**P3（议题3 MVP）**
- `src/battery_analysis/ndax/converter.py`（或 validators 下新增 `batch_consistency.py`）— `levels_by_file` 比对
- `src/battery_analysis/main/workers/analysis_worker.py` — 剔除/中止弹框流转

**P4（已裁决，独立收尾）**
- `src/battery_analysis/main/tabs/ndax_tab.py` — 「ndax转excel」降级为子功能按钮

**不动**：`filename_parser.py` 其余调用点、`pulse_currents.py`、`quality_requirements.py`、`file_validator.py`（2_xlsx 校验留给兼容路径）。


---

## DeepSeek (Round 2): DeepSeek Round 2 辩论

# DeepSeek Round 2 辩论

## 议题1：中间格式（2:2平票 → 必须收敛）

### 最终选择：**内存 DataFrame 直传**

---

### 我方对 xlsx 缓存方案的最强攻击

GLM/GPT 的核心论点是"xlsx 是已验证路径，改动最小"。我要指出这个论证的三个真实漏洞：

**漏洞1：converter.py 分表逻辑是已知定时炸弹**

`converter.py` 的 `XLSX_MAX_ROWS=1_048_576` 触发 Record_2/Record_3 分表，`read_xlsx_sheets` 再拼接。这不是"已验证"，是"还没炸"。xlsx 单表行数限制是 Excel 格式硬约束，分表拼接的边界条件（最后一行是否截断、表头是否重复、列对齐）每一个都是隐性 bug。GLM 说"converter.py 引擎零改动"——恰恰相反，**保留 xlsx 路径意味着永久保留这段脆弱映射**，而 DataFrame 直传直接消除它。

**漏洞2："缓存命中免重转"的账算错了**

GLM 说"保留 xlsx 缓存后，重复分析直接命中缓存、跳过最慢的 ndc 解析"。但仔细看数据流：

- xlsx 缓存路径：首次 = ndax解析(~1s) + xlsx写(~5s) + xlsx读(~3s) = **~9s/文件**；缓存命中 = xlsx读(~3s) = **~3s/文件**
- DataFrame 直传：每次 = ndax解析(~1s) + 内存传递(0s) = **~1s/文件**

16 文件批量时：xlsx 首次 = ~144s，缓存命中 = ~48s；DataFrame 每次 = ~16s。**即使缓存命中，xlsx 路径仍然比 DataFrame 直传慢 3 倍**。所谓"跳过最慢的 ndc 解析"是对的，但 xlsx 读取本身就比 ndc 解析慢——用一个更慢的缓存来"跳过"一个更快的解析，逻辑不成立。

**漏洞3："可审计性"是可选需求，不应驱动架构**

GPT 说"可审计性是隐性刚需"。但在当前项目规模（16 电池/批、5 个项目）下，审计频率极低。用一个高频操作（每次分析都走 xlsx）来服务一个低频需求（偶尔审计），ROI 为负。审计需求完全可以通过按需导出补偿（见下文）。

---

### 诚实评估混合方案

主持人提出"主链路 DataFrame 直传 + manifest 控制的 xlsx 落盘缓存兼审计"。我诚实评估：

**混合方案的吸引力**：
- 日常走 DataFrame（快），需要审计时有 xlsx（可查）
- manifest 控制缓存，ndax 不变则不重转

**混合方案的真实成本**：
1. **双路径维护**：converter.py 要同时支持"返回 DataFrame"和"写 xlsx"两条路径，data_processor.py 要同时支持"接受 DataFrame"和"读 xlsx 路径"两条入口。每次改动都要测两条路径。
2. **缓存失效逻辑**：manifest 的 mtime+size 判定在 Windows 上有精度问题（NTFS mtime 精度 100ns，但跨时区/夏令时可能漂移），且用户手动改 ndax 文件名不触发 mtime 变化。
3. **分表问题依然存在**：只要保留 xlsx 落盘能力，Record_2/3 分表逻辑就不能删，脆弱映射继续存在。

**我的判断**：混合方案在理论上优雅，但在当前项目规模下增加了不必要的复杂度。**单一路径 > 双路径**，除非有明确证据表明审计需求频繁到值得维护双路径。

---

### 最终选择理由

| 考虑因素 | DataFrame 直传 | xlsx 缓存 | 胜出方 |
|---------|---------------|----------|-------|
| 首次分析效率(16文件) | ~16s | ~144s | DataFrame |
| 重复分析效率(16文件) | ~16s | ~48s(缓存命中) | DataFrame |
| 分表脆弱性 | 消除 | 保留 | DataFrame |
| 可审计性 | 需按需导出 | 天然有 | xlsx |
| 代码改动量 | 中(函数签名变更) | 小(改输出路径) | xlsx |
| 双路径复杂度 | 无 | 混合方案有 | DataFrame |

**关键决策因素**：效率差距是 3 倍（不是微优化），分表脆弱性是硬风险（不是假设），而可审计性可以通过"调试模式导出 xlsx"补偿。权衡后，DataFrame 直传胜出。

**审计补偿方案**：在 UI 加一个"保存中间数据"复选框（默认关闭），勾选时 DataFrame 额外导出为 xlsx 到 `2_xlsx/` 目录。这样日常零开销，需要时一键导出。

---

## 议题2：profile 不一致时的处理深度

### 收敛结论：分层决策树

基于 CF224642T 案例（profile 30/26/15/6 vs Step.xml 60/30/15/6）和四家方案，我提出以下决策树：

```
Step1: 设定值层比对（profile PulseData vs Step.xml PulseData）
  │
  ├─ 档位数不同 → 阻断
  │     弹窗：「档位数量不一致：profile {n}档 vs ndax {m}档」
  │     按钮：[中止]（默认焦点） / [以 ndax 为准继续]
  │     放行 → Info_Plot.json 写 "profile_override": {"type": "level_count_mismatch", "profile": [...], "step_xml": [...], "user_action": "accepted_ndax"}
  │
  ├─ 档位数相同但值不同（0容差）→ 阻断
  │     弹窗：「设定值不一致：profile {v1}mA vs Step.xml {v2}mA」
  │     按钮：[中止]（默认焦点） / [以 ndax 为准继续]
  │     放行 → Info_Plot.json 写 "profile_override": {"type": "value_mismatch", ...}
  │
  └─ 一致 → 进入 Step2

Step2: 实测层比对（data.ndc Pulse 实测电流 vs Step.xml 设定值）
  │
  ├─ 实测档位数 ≠ 设定档位数 → 告警（不阻断）
  │     状态栏提示：「实测档位 {k} 个，设定 {n} 个，缺失档位将标注 N/A」
  │     Info_Plot.json 写 "measured_level_discrepancy": {"expected": n, "actual": k, "missing": [...]}
  │
  ├─ 实测值偏差 > max(设定值×1%, 0.5mA) → 告警（不阻断）
  │     Info_Plot.json 写 "measured_level_drift": {...}
  │
  └─ 通过 → 静默继续
```

**关键设计决策**：

1. **设定值层阻断，实测层放行**。理由：设定值不一致意味着"用了错的 profile"（如 CF224642T），这是致命错误；实测偏差是设备物理公差，不应阻断分析。

2. **放行按钮文案**：`[以 ndax 为准继续]`——明确告知用户以哪个数据源为准，不是模糊的"继续"。

3. **放行留痕**：写入 Info_Plot.json 的 `profile_override` 字段，包含不一致类型、双方值、用户操作。报告生成时在页脚标注"⚠ 档位以 ndax 实测为准，profile 校验未通过"。

4. **与 GLM 方案的差异**：GLM 提议实测层用中位数比对，我同意这个思路但认为实测层不应阻断——中位数比对的结果是告警信息，不是阻断条件。

---

## 议题3：多 ndax 间档位不一致的 MVP 边界

### 收敛结论：MVP 仅检测 + 阻断，二期再做分组

**MVP 做什么**：
1. 批量导入时，逐文件提取 Step.xml PulseData
2. 以第一个文件为基准，后续文件逐一比对
3. 不一致 → 阻断弹窗，列出差异文件清单
4. 弹窗按钮：`[中止]`（默认） / `[以第一个文件为准继续]`

**MVP 不做什么**：
- 不做并集（理由见下）
- 不做分组分析
- 不做自动选择基准

**为什么不做并集**：

GPT/MiniMax 提议取并集。我反对，理由是**下游全链路改造成本极高**：

当前 `listCurrentLevel` 是单一列表，下游假设：
- `data_loader.py`: `intCurrentLevelNum = len(listCurrentLevel)` → 循环次数
- `figure_builder.py`: 按 `listCurrentLevel[i]` 索引绘图
- `plot_writer.py`: 按档位数生成 CSV 列
- `info_csv_writer.py`: 按档位数写 Info_Image.csv

并集方案意味着：每个文件的档位集不同，下游要支持"文件A有档位[60,30,15,6]，文件B有档位[60,30,15]"——这需要把 `listCurrentLevel` 从全局变量改为 per-file 字典，所有下游循环从 `for i in range(n)` 改为 `for level in file_levels[file]`。

**工作量估计**：至少 5 个文件（data_loader、battery_analysis、figure_builder、plot_writer、info_csv_writer），每个文件的核心循环都要改，加上 Info_Plot.json 结构变更、报告模板适配。保守估计 **3-5 人天**，且测试矩阵爆炸（每个文件 × 每种档位组合）。

**二期接口预留**：
- `listCurrentLevel` 改名为 `current_levels`，类型从 `list[float]` 改为 `dict[str, list[float]]`（key=文件名）
- 先在 MVP 阶段统一为 `{"*": [基准档位]}` 的 dict 结构，二期再扩展 per-file 支持
- 这样二期改动是渐进的，不需要推翻 MVP

---

## 议题4：无 xml 声明持久化

### 收敛结论：Info_Plot.json 为主 + QSettings 版本号为辅

**主方案：写入 Info_Plot.json**

```json
{
  "profile_status": "absent",
  "profile_ack": {
    "acknowledged": true,
    "timestamp": "2026-10-16T14:30:00",
    "strategy_version": "2026.10",
    "level_source": "ndax_step_xml"
  }
}
```

字段设计：
- `profile_status`: `"absent"` | `"validated"` | `"override"` | `"mismatch_ack"` — 覆盖所有 profile 状态
- `profile_ack.acknowledged`: 布尔，用户是否已确认
- `profile_ack.strategy_version`: 策略版本号，与 QSettings 同步
- `profile_ack.level_source`: 档位实际来源（`"ndax_step_xml"` / `"config_lookup"` / `"filename_parser"`）

**辅助方案：QSettings 存版本号**

- 键名：`battery_analysis/ndax/profile_ack_version`
- 值：`"2026.10"`（策略版本号字符串）
- 用途：跨会话记忆"用户已确认过当前版本的策略"，避免重复弹窗
- 版本递增触发重新弹窗（如策略从 `2026.10` 更新到 `2026.11`）

**为什么不选其他方案**：
- GLM 的 QSettings 存版本号（仅）：缺少项目级审计痕迹，报告审阅者看不到"此报告无 profile 校验"
- GPT 的 `NO_PROFILE_DISCLAIMER.txt`：单独文件容易丢失（复制报告时忘带），不如嵌入 Info_Plot.json（它已经是报告元数据的一部分）
- MiniMax 的黄三角常驻：UI 层方案，不解决"报告可追溯"需求，且跨会话状态管理复杂

**声明弹窗文案**：
> 「未找到 profile xml 文件。档位将完全以 ndax Step.xml 为准，标准符合性无法交叉校验。」
> [中止] / [确认继续]（默认焦点在中止）

---

## 实施顺序 + 改动文件清单

| 顺序 | 任务 | 改动文件 |
|------|------|---------|
| 1 | filter_data 空档位防御（P0） | `src/battery_analysis/utils/processors/data_utils.py:42` |
| 2 | profile 验证 + 不一致决策树 | `src/battery_analysis/utils/pulse_matcher.py`(新增比对函数), `src/battery_analysis/main/tabs/ndax_tab.py`(弹窗UI) |
| 3 | 无 xml 声明机制 | `src/battery_analysis/main/tabs/ndax_tab.py`(弹窗), `src/battery_analysis/utils/info_plot_writer.py`(写JSON字段), QSettings 键 |
| 4 | 多 ndax 批内一致性检测 | `src/battery_analysis/main/tabs/ndax_tab.py`(批量导入逻辑), `src/battery_analysis/utils/pulse_matcher.py`(比对函数复用) |
| 5 | DataFrame 直传主链路 | `src/battery_analysis/core/converter.py`(parse_ndax返回DataFrame), `src/battery_analysis/core/data_processor.py`(接受DataFrame参数), `src/battery_analysis/core/data_loader.py`(read_xlsx_sheets改为read_dataframe) |
| 6 | 可选 xlsx 导出（调试模式） | `src/battery_analysis/core/converter.py`(convert_one降级为可选落盘), `src/battery_analysis/main/tabs/ndax_tab.py`(UI复选框) |
| 7 | UI 降级 ndax 为子功能 | `src/battery_analysis/main/tabs/ndax_tab.py`(tab→按钮) |

---

## MiniMax (Round 3): MiniMax Round 3 补辩

## 立场：有条件给

**结论：给放行按钮，但附加可判定的条件约束。**

---

### 核心洞察：档位数不一致不是一件事，是两件方向相反的事

正反前提都正确，但它们描述的不是同一个问题：

- **ndax 档位 < profile**：操作员中途停止测试 → 后续档位根本没有数据，继续运行等于"拿残缺测试出完整报告"——**危险**
- **ndax 档位 > profile**：操作员临时加档或 profile 模板过期 → 数据完整，只是对齐信息过时——**安全**

这两种场景在技术上都叫"档位数不同"，但数据完整性语义完全相反。一刀切给或一刀切不给，都是用同一把钥匙开两把锁。

---

### 可实现判定条件

```
if ndax档位数 > profile档位数:
    → 给 [以ndax为准继续] 按钮（数据完整，只是 profile 陈旧）
elif ndax档位数 < profile档位数:
    → 读取 Step.xml 的 Cycle_Count / 工步完成状态
    → 若所有工步已标记完成: 给出"档位数不匹配，但工步已完成，是否视为有效"弹窗（条件放行）
    → 若存在未完成工步: 硬阻断，不给按钮（数据不完整）
else:
    → 回到档值对比逻辑（Round 2 已裁决路径）
```

**关键可实现点：** Step.xml 中 Cycle_Count 和工步状态是 ndax 文件自带字段，不依赖 profile，可在离线状态下读取判断。这提供了客观的仲裁证据，不依赖用户主观判断。

---

### 为何优于硬阻断

纯硬阻断的代价：ndax 档位 > profile 时（现实操作中频繁发生），用户被迫中止一个数据完整的测试，只能重新跑。  
纯给的代价：ndax 档位 < profile 时（测试截断），用户可能习惯性点继续，生成有误导性的报告。

有条件给消除了这两种代价，同时将决策自动化——用户不需要判断"为什么少一档"，系统替用户做了证据检查。

---

**单选结果：有条件给**  
**判定维度：档位多少方向 + 工步完成状态**  
**技术可行性：Step.xml 字段可读取，条件可程序化实现**


---

## GLM (Round 3): GLM Round 3 补辩

# GLM Round 3 补辩：档位数不一致时是否给 [以ndax为准继续] 按钮

## 结论：有条件给

## 判定条件（可实现，两个证据源）

仲裁条件用现有数据即可实现，无需新采集：

1. **工步完成性**：读 Step.xml 的 Cycle_Count / 工步完成状态。若 ndax 声明的档位对应工步**全部执行完成**，判定为"数据完整、profile 陈旧"→ 弹出 [以ndax为准继续] 按钮，流程复用已定裁决1的交互（默认焦点[中止]、放行写 Info_Plot.json.profile_validation 留痕，mismatch_type 记 `level_count_mismatch`）。
2. **实测佐证（可选加强）**：data.ndc 实测脉冲档位数 ≥ ndax 声明档数，进一步确认无截断。

两个证据都拿不到或结论矛盾 → 按"硬阻断不给按钮"处理，报错文案提示用户检查工步是否跑完，不给一键放行。

## 论据

1. **档数不一致是两种不同故障的混合信号**：ndax 少一档可能是测试截断（数据不完整，继续=把废测试当完整测试出报告，危险）；ndax 多一档是操作员临时加档（数据完整，只是 profile 过期，继续无害）。一刀切"给"或"不给"都会在其中一种情形下做错。既然 Step.xml 与 data.ndc 就在手边，花一个 if 的成本把两种情形分开，比赌用户判断力便宜。
2. **技术上自洽不等于语义上安全**：正方"重构后下游全由 ndax 驱动，继续运行无错位"是对的，但它只回答了"跑不跑得起来"，没回答"这份报告该不该出"。filter_data P0 修复同理——防崩溃是底线，不是放行理由。
3. **不给按钮的成本也可控**：工步完成性判定是纯读取+比较，实现量 < 20 行；判定为"截断"时不给按钮、直接报错，把用户从"当庭判断谁对"的困境里解放出来——这正是硬阻断方最有力的论据，但只在截断情形下成立。
4. **放行按钮的前提是"ndax 是完整配方"**：已定裁决1之所以敢给按钮，是因为档数值不同时 ndax 仍是完整配方。本辩题只有当工步完成性确认后，ndax 才重新具备"完整配方"资格——条件给按钮在逻辑上与已定裁决1同构，不引入新原则。

## 实现要点（最小改动）

- 校验阶段新增 `check_step_completeness(step_xml, ndax_levels) -> bool`，结果并入 `profile_validation.mismatch_type` 区分 `level_count_mismatch_complete` / `level_count_mismatch_truncated`。
- UI：complete → 复用裁决1的三按钮弹窗（默认焦点[中止]）；truncated/unknown → 纯报错对话框，无放行按钮。
- policy_version 沿用 "2026.10" 即可，无需另立版本。

**一句话**：档数不一致时"给不给按钮"不该二选一，用工步完成性把截断和 profile 陈旧分开——完整给按钮、截断硬阻断，两个证据源现成，实现成本一个 if。

---

## GPT (Round 3): GPT Round 3 补辩

# GPT Round 3 补辩：档位数不一致时是否给 [以ndax为准继续] 按钮

## 结论：有条件给

**判定条件：先拆方向，再看工步完成性——两个分支可程序化，无主观判断。**

```
ndax档位数 > profile档位数 → 直接给按钮（profile陈旧，数据完整）
ndax档位数 < profile档位数 → 读 Step.xml Cycle_Count/工步完成状态
  ├─ 所有对应工步均已完成 → 给按钮，复用裁决1三按钮交互
  └─ 存在未完成工步 → 硬阻断，报错提示"测试可能未跑完，检查数据"
证据不可用（无Step.xml或字段缺失）→ 硬阻断（安全兜底）
```

## 论据

**1. 四家共识的"推土机逻辑"已经决定了答案。** 重构后下游全由 ndax 档位驱动 listCurrentLevel，profile 的角色已被限缩为"校验参考"。既然裁决1（档值不同时给按钮）的底层逻辑是"ndax 才是真实配方"，档位数不一致时如果能确认 ndax 数据完整，同一逻辑就应该给同样的出口——否则同一个架构下出现两种矛盾的安全策略，用户无法形成稳定预期。

**2. ndax 多于 profile 和 ndax 少于 profile 是完全不同的信号。** ndax 多 → 操作员临时加档，数据完整、profile 陈旧，本质和"值不一致"同构，不应阻断。ndax 少 → 可能测试截断、工步未跑完，这才是真正的数据完整性风险。如果放弃这个方向拆分而一刀切"硬阻断"，ndax 多的常见场景（操作员临场加档）就会被误杀；如果一刀切"给"，截断数据可能泄漏进报告。

**3. "有条件"的判定证据必须是客观仲裁，不是策略声明。** GLM 和 MiniMax 都提到了 Step.xml 工步完成性，这是正确的——它来自 ndax 自身携带的元数据，不依赖 profile，是唯一可信的客观仲裁源。我强调一个关键约束：如果 Step.xml 字段不可用（比如该格式版本没有 Cycle_Count），**应默认硬阻断**，而非默认放行。这保证"有条件"的判定基础是可信的，不存在"证据缺失时碰运气"的灰色地带。

**4. 与已定裁决的同构性是关键检验标准。** 本轮"有条件给"不应引入新原则——它的唯一依据是"ndax 是完整配方时可放行"。判据（工步完成性）把这个问题从"用户猜"变成"机器判"，策略逻辑与裁决1 完全一致：默认[中止]，放行留痕 `level_count_mismatch`，policy_version 沿用 "2026.10"。

**5. 成本极低。** 方向拆分 + Step.xml 完成性判断，实现量约 15-20 行，不引入新依赖，不新建弹窗——完整分支复用裁决1 的三按钮交互，截断分支复用已有的报错对话框。

---

## DeepSeek (Round 3): DeepSeek Round 3 补辩

# DeepSeek Round 3 补辩：档位数不一致时是否给 [以ndax为准继续] 按钮

## 结论：有条件给

---

## 核心分析：四种故障态的穷举

档位数不一致不是一种情况，而是方向×完整性的四格矩阵：

| 场景 | ndax方向 | 数据完整性 | 危险等级 |
|------|----------|-----------|---------|
| A | ndax > profile | 测试多跑了1档 | **无害**——数据存在，profile过期 |
| B | ndax < profile，Step.xml全工步完成 | profile从5档改4档没回存 | **无害**——协议精简，数据完整 |
| C | ndax < profile，Step.xml存在未完成工步 | 测试中途截断 | **危险**——残缺数据出完整报告 |
| D | Step.xml缺失/不可读 | 无法判定 | **未知**——无证据即不可放行 |

硬阻断错杀A和B；无条件放行放过C。两者都是用"一刀切"回避本可程序化解决的问题。真正的分界线不在档位数本身，而在**数据完整性**——而这正是 Step.xml 工步完成状态能提供的仲裁证据。

---

## 判定规则

```
if ndax档位数 > profile档位数:
    → 直接给 [以ndax为准继续] 按钮（场景A，数据完整）

elif ndax档位数 < profile档位数:
    → 读 Step.xml 工步完成状态
    → 全部完成 → 给按钮，mismatch_type = level_count_mismatch_complete（场景B）
    → 存在未完成工步 → 硬阻断，不给按钮（场景C）

Step.xml缺失/解析失败:
    → 硬阻断，报错提示"无法确认数据完整性，请检查工步执行状态"（场景D）
```

放行时复用已定裁决1交互：默认焦点[中止]，放行写 Info_Plot.json.profile_validation 留痕，policy_version沿用"2026.10"。

---

## 论据

**1. 场景A（ndax>profile）应当直接放行。** MiniMax与我观点一致：ndax多一档说明测试**实际跑过**那些工步，数据已存在于ndax文件中。Step.xml在此场景是冗余校验——测试本身已完成，无需工步状态佐证。GLM要求此场景也查Step.xml完成性，过于保守，可能误杀操作员临时加档的合法场景。

**2. 场景B（ndax<profile，工步完成）与已定裁决1同构。** 裁决1中档值不同时ndax仍是"完整配方"，故敢给按钮。此处工步完成状态确认ndax同样是完整配方——协议精简（profile从5档缩到4档）而非数据截断。两处放行的逻辑前提一致，不引入新原则。

**3. 场景C是唯一真正危险的场景，也正好是Step.xml能唯一可靠识别的场景。** 工步未完成 = 测试中途被截断 = 数据不完整，这个判定的误报率极低（工步状态是硬件写入的客观事实，不受profile或用户主观影响）。这正是"有条件"比"纯给"和"纯不给"都优越的地方：系统替用户做了证据检查，用户无需猜测"为什么少一档"。

**4. 场景D（Step.xml缺失）必须硬阻断。** "无证据"不等于"安全"。如果允许在证据缺失时放行，等于把场景D退化为"纯给"，场景C的保护被绕过。硬阻断的成本可控：报错文案提示用户检查数据，比生成误导性报告的代价小得多。

**5. "习惯性点击"风险被系统判定化解。** 反方最有力的论据是用户会习惯性点放行。但在本方案中，场景C（真正危险的情况）系统根本不给按钮，用户想点也点不了。按钮只在A和B出现——此时数据完整，放行在技术上是安全的。默认焦点[中止]仍保留为额外防线。

---

## 与GLM/MiniMax的分歧点

| 维度 | MiniMax | GLM | DeepSeek |
|------|---------|-----|----------|
| ndax>profile | 直接给按钮 ✅ | 也要查Step.xml ⚠️ | 直接给按钮 ✅ |
| ndax<profile | 查Step.xml ✅ | 查Step.xml ✅ | 查Step.xml ✅ |
| Step.xml缺失 | 未明确 | 硬阻断 ✅ | 硬阻断 ✅ |
| data.ndc佐证 | 无 | 可选加强 | 不引入（增加复杂度，Step.xml已足够） |

**一句话：** 档位数不一致时给不给按钮，答案取决于数据完整性而非档位数本身。ndax多档直接放行，ndax少档用工步完成状态仲裁——完整给按钮、截断硬阻断、无证据硬阻断。三种结果覆盖四种故障态，每条路径都有客观判定条件，不依赖用户主观判断。

---

## 主持 (Final): Final 全部裁决收口（裁决①-⑦ + 拍板记录）

# Final：全部裁决收口（主持人汇总）

## 裁决① 档位数相同的档值不一致（设定值层，0 容差）
- 阻断 + [以ndax档位为准继续] 按钮，默认焦点 [中止]
- 放行写 Info_Plot.json.profile_validation 留痕（mismatch_type 档值类）
- 依据：Round 2 四家共识；ndax 是完整配方，同一逻辑可放行

## 裁决② 实测层偏差
- 实测脉冲中位数偏差 > max(1%, 0.5mA) → 黄色告警放行 + 留痕（Round 2 四家共识，不变）

## 裁决③ 多 ndax 文件间档位不一致
- **硬报错，不能运行**，提示用户检查数据
- 不给任何放行选项（替代 Round 2 的剔除文件/基准文件方案，用户拍板）

## 裁决④ 档位数不一致（profile 档数 ≠ ndax 档数）—— Round 3 + 用户三项拍板
Round 3 四家 4/4 一致「有条件给」：分界线是数据完整性，不是档位数本身；用 Step.xml 工步完成状态做客观仲裁（机器判，非用户猜）。

```
ndax档数 > profile档数
  → 直接给 [以ndax准继续] 按钮                    【用户拍板：采三家方案，不查工步】
     （数据完整、profile 陈旧；操作员临时加档不被误杀）

ndax档数 < profile档数
  → 查 Step.xml 工步完成状态
     ├─ 全部完成 → 给按钮（协议精简，非截断）
     │            留痕 mismatch_type = level_count_mismatch_complete
     └─ 存在未完成工步 → 硬阻断，报错"测试可能未跑完，请检查数据"
                          mismatch_type = level_count_mismatch_truncated

Step.xml 缺失 / 字段不可读 / 解析失败
  → 硬阻断（无证据=不可放行）                     【用户拍板：从严】
```

- 放行一律复用裁决①交互：默认焦点 [中止]、写 Info_Plot.json.profile_validation、policy_version 沿用 "2026.10"
- **不引入 data.ndc 实测佐证**（用户拍板：Step.xml 工步状态已足够，避免解析私有二进制的复杂度与性能成本）
- mismatch_type 取值补全：`level_count_mismatch_complete` / `level_count_mismatch_truncated` / `level_count_missing_evidence`（Step.xml 缺失）
- 实现量约 15-20 行，一个判定函数（如 check_step_completeness(step_xml)），无新依赖、不新建弹窗（完整分支复用裁决①三按钮弹窗，截断分支复用报错对话框）

## 裁决⑤ 字段/键名统一（用户已同意，Round 2）
- Info_Plot.json：`profile_validation`（result / mismatch_type / decision / policy_version）
- QSettings：`validation/profile_disclaimer_version`，版本值 `"2026.10"`

## 裁决⑥ 中间格式（Round 2 四家全票改判）
- 内存 DataFrame 直传（nda.read → 分析管线），xlsx 退出主链路
- 按需导出 xlsx 落 3_analysis results/{date}_v{ver}/（复用降级按钮/复选框，审计用途）
- 不用 OS 临时目录（会被清理且不更快）；临时目录只放可再生调试 dump

## 裁决⑦ P0 前置修复（Round 2 四家全票）
- filter_data 空档位防御必修：循环头空判 `append([]) continue`，上游空档位与下游过滤逻辑解耦
- 裁决④场景 C（截断）与 P0 各管一层：P0 防崩溃是底线，裁决④决定该不该出报告

## 已裁决不重开项
- 无 profile 时：弹框声明一次（QSettings 记忆版本号），允许继续只靠 ndax 分析
- 重新识别边界：档位/CC电流/型号/批次/日期以 ndax 为准；制造商/成组方式等非分析字段 UI 人为配置，filename_parser 其余调用点不动
- filter_data 修法、多 ndax 硬阻断、字段命名：均定案

---
会议状态：全部议题收敛，无残余分歧。四轮（Round 1 提案评估 → Round 2 四议题收敛 → 用户裁决 → Round 3 单点补辩 + 用户三项拍板）完成。


---
