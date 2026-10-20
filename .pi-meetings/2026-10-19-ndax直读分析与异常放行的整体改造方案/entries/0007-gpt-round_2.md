# GPT (Round 2): Round 2：一次读取胜出的时/存论证、点击后决策时序、最小空位协议与同名报告保护——并全面纠正 Excel 删除清单

# GPT（Round 2）：交叉质询与收敛——一次读取 vs 两次读取、点击后决策时序、报告完整性

> 前提：用户 Round 1 后反馈为最高优先级裁决，覆盖 Round 1 一切与之冲突的提案。以下所有代码证据均为本轮独立复核（含行号）。只讨论，不改代码。

---

## 1. 用户裁决效力：Excel 报告必须保留——四家 Round 1 的删除清单全部作废

用户原话「原来所有生成的报告不要变，都得有」直接推翻了「删除 Excel 报告」的一致提案。**必须如实承认：GLM §4、MiniMax 阶段 5、DeepSeek §4.2、以及我（GPT）Round 1 §4 的 Excel 报告删除清单整体作废，不得再提删 Excel 报告、不得再提处理 Word 超链接。**

按代码证据把 Excel 的三重身份拆清楚，删除边界只砍第二项：

| 身份 | 代码证据 | 裁决 |
|---|---|---|
| ① 报告交付物（Result xlsx + Sample xlsx） | `report_coordinator.py:584` 调 `ExcelReportWriter.write()`；`excel_report_writer.py:96-100` 生成 Result 工作簿（overview/result 表）与 Sample 工作簿（word 表，人工复制模板用，DeepSeek §4.3 已考证） | **保留，报告种类一个不减**；内容只可增加异常说明列/缺失标注 |
| ② 分析输入与中间层 | `xlsx_reader.read_xlsx_sheets`、`excel_validator.py`、`excel_processor.py`、`scan_sorted_xlsx`、`file_validator.py` 强制 `2_xlsx`、`data_processor` 文件名档位解析进主配置 | **退出**：主分析全程 ndax 直读，不经 xlsx |
| ③ 独立 ndax→Excel 导出页 | `ndax/converter.py`、`ndax/worker.py`、`main/tabs/ndax_tab.py` | 保留（各家一致，无争议） |

**连带结论反转**：Word 超链接问题自动消失——`word_overview.py:142,181` 的 `add_hyperlink` 指向 `strResultXlsxPath/strSampleXlsxPath`（`report_coordinator.py:173` 的 `strRelResultPath`），这些目标文件在报告生成时继续由 ExcelReportWriter 产出，链接天然有效。Round 1 里"删链接/改指 CSV/改指 JSON"的分歧 5、P4、§7-6 全部**撤案**。架构守卫测试口径同步修正：不是"全仓无 Excel"，而是"分析输入链路不含 xlsx 读取"（`read_xlsx_sheets/scan_sorted_xlsx/2_xlsx 强制` 从分析链消失）。

---

## 2. 【重点】一次读取 vs 两次读取：时间/内存的严格论证与单选

这是用户点名要答案的问题（「哪个时间短，效率高？」），我给出明确单选：**一次读取（先算不写、逐文件流式）**。并正面质询 DeepSeek §3.2 推荐的方案 A（轻量预检读一遍 + 正式分析再读一遍）。

### 2.1 成本模型（以代码证据为基）

- 解析是大头：`converter.py:186` 证实 `nda.read()` 是一次性把整个 data.ndc 解析成单一 DataFrame；converter 里「Record 超 104 万行拆表」逻辑反证单文件数据量可达百万行级。解析成本 = 二进制解码 + DataFrame 物化（CPU + 内存带宽 + 磁盘 IO）。
- 派生是小头：脉冲检测（numpy 广播比较，`pulse_matcher.py:52` 注释明确是向量化实现）、档位匹配、电荷计算，均在已物化的 DataFrame 上做，成本远低于解析。
- 并行结构：`battery_analysis.py:157`（ProcessPoolExecutor）与 `:207-210`（Windows 分支 `multiprocessing.Pool`，`cpu_count = min(cpu, 4)`）——每 worker 独立解析各自文件。

**时间**：两次读取 = 解析成本 × 2（DeepSeek 自己承认「CPU ~2×」），而其预检内容「read + derive + detect_pulse + match_levels」（§3.2 原文）恰恰就是分析主体，省掉的只有便宜的电荷计算和写盘。**2× 解析换 ≈0 计算节省，纯亏。**

**内存**：DeepSeek 方案 A 的「内存安全」是错觉。峰值内存 = 并行度 × 单文件 DataFrame 体积，与读几遍无关：两次读取的预检阶段同样要物化每个 DataFrame（4 worker × 百万行级 DataFrame），一次读取同样如此。真正的差别是：**一次读取在"派生完成即丢弃 DataFrame、只留派生结果"后，第二阶段内存 ≈ 0**；两次读取则把同样的峰值付了两遍时间。因此一次读取在两个维度上同时占优（时间 ~1× vs 2×，峰值内存 ≤）。

### 2.2 单选方案：逐文件流式 + 列投影

1. worker 内逐文件：`nda.read` → 取分析所需列（Cycle/Step/Status/Current(mA)/Voltage/Charge_Capacity/Discharge_Capacity/Timestamp，即 converter 现用列契约）→ **列投影可再砍约半数内存**；
2. 同一次物化上完成：脉冲检测、档位匹配、电荷计算、中位数、异常判定（缺脉冲/坏通道/读失败全部收齐）；
3. 只保留 KB 级派生结果（posi/charge/voltage 列表 + 状态 + 异常条目，即 `BatteryResult`），立刻丢弃 DataFrame；
4. 全批完成后：异常汇总 → 两次确认 → 才进入写盘提交段。

峰值内存 = `min(worker 数, 文件数) × 单文件投影后 DataFrame`，与方案 A 相同；总时间 = 1× 解析。**适用边界**：任意批大小均适用；唯一残余风险是「单文件投影后仍超单 worker 内存」，但这与读取次数无关（两次读取也要完整读一遍），只能靠列投影/未来分块解析缓解，需列入残余风险而非改选两次读取。例外情形（何时两次读取才合理）：若未来出现"预检逻辑远轻于正式计算"的场景——现不存在；或内存极端受限到连一次物化都需错峰——现无证据。**结论：单选一次读取。**

### 2.3 与用户新时序的契合（架构动机反转）

用户裁决：数据异常在**点击分析后**汇总确认。这直接消灭了两次读取的架构动机——Round 1 各家（含我）默认的"预检一遍→确认→正式跑一遍"里，那个"预检"必须读数据、又不许发生在点击前，于是它只能发生在点击后；而点击后它就是分析本身的第一半。**两次读取在新时序下是把点击后的同一份计算重复两遍，只为在中间插弹窗——而一次读取天然在"计算完成、写盘之前"留出确认点（先算不写的结构红利）。**

---

## 3. 【重点】点击运行后的决策时序（单选钉死）

### 3.1 运行前（点击 Run 之前的校验阶段，主线程）——只做不打开 ndax 数据的廉价检查

1. 多 ndax 配方一致性：Step.xml 档位互比，不一致 = 硬阻断（旧定案，与决定 2 不矛盾——属配置级错误）；
2. profile 比较（有 profile）：同数异档 = 阻断 + 「以 ndax 为准继续」按钮（默认中止）；档数不一致 = 人工确认出口（默认中止）；
3. 无 profile = 一次性免责声明（QSettings `validation/profile_disclaimer_version`）；
4. 目录级：目录非空、文件数与 Samples Qty 一致性提示。

**红线 1（不得假称 Step.xml 一定有完成状态）**：全仓 grep 证实当前没有任何 Step.xml 解析代码（仅 `converter.py:186` 一处 `nda.read`），完成状态字段的存在性、字段名均未经验证（MiniMax 分歧 2 的怀疑成立，我背书并加强）。必须实现为三态 `complete / incomplete / unknown`：无文件、无字段、解析失败一律归 `unknown` → **放行 + 留痕**，绝不因缺字段阻断或崩。任何方案若写"读 Step.xml 完成状态即可判定"，都属未经证据支持的断言。

**红线 2**：GLM §3 预检第 3 条「每文件轻量探测（解 zip 校验内部结构）」放在启动 worker 之前——zip 探测必须打开 ndax 容器，属数据读取，按用户裁决**移到点击后**的 Phase A 一并做（反正一次读取里顺带完成，成本为零）。运行前打开数据文件 = 变相把数据异常预检塞到运行按钮之前，正是用户禁止的形态。

### 3.2 点击分析后（worker 线程）——一次读取 → 汇总 → 两弹 → 提交

```
点击「分析」
  → Phase A（worker）：逐文件一次读取计算全部 + 收集异常；不写盘、不删除任何旧文件
  → 信号回主线程：异常汇总（电池/档位/类型/证据，缺脉冲=结构性缺失 vs 中位数偏差=质量告警，分型分列）
  → 【弹框①】是否停止整批？（默认「停止」）——停止 → 零写入零删除，留痕
  → 继续 → 【弹框②】二次明确确认：列出将保留的空位清单与后果（图留空位、报告标 N/A、统计不含该槽位）
  → 确认 → 决定传回 worker（threading.Event）→ Phase B 提交（staging 写盘 → 原子切换）
```

**红线 3（不得从后台线程弹 Qt 对话框）**：`AnalysisWorker` 经 `TaskRunner` 跑在 QThreadPool（`task_runner.py:42` `QThreadPool.globalInstance().start(runner)`），`run()` 全程在非 GUI 线程。弹框必须发信号回主线程执行，worker 阻塞在 `threading.Event` 等决定；**超时/取消一律按「停止整批」**。MiniMax §9.2 与 DeepSeek §3.3 都点到了这一点，我明确背书并建议升为验收项：pytest-qt 断言两次弹框都发生在 GUI 线程。这是硬性禁项，不是风格建议——后台线程 QMessageBox 是 Qt 未定义行为。

**确认归属**：中位数偏差（>max(1%, 0.5mA)）只能在 Phase A 算出，是点击后信息，进汇总的 warning 区但**不进两次确认、不产生空位**（四位顾问此点一致，维持）；Step.xml 完成状态 `unknown/incomplete` 同样只是 warning 行。预检两弹 = 决定 2 的字面满足，不再加第三弹（见 §5）。

---

## 4. 内部缺失空位的最小兼容协议（回应「显示标记啥意思」）

先回答概念：「缺失标记」有两层，绝不能混——

- **内部标记**（机器用）：`Info_Image.csv` 里缺失槽位的占位行，供 `data_loader` 解析、保证按下标对位不错乱；
- **用户可见提示**（人用）：图表上灰色虚框「缺失(缺脉冲/通道失败)」、Word/Excel/CSV 单元格「N/A(原因)」、报告头部「数据缺失汇总」段。这些是**内容增强**，符合用户「报告种类不变、可加异常说明」。

**单选推荐（真正最小兼容）：写端格式不变、空行即缺失、读端补位。**

1. `Info_Image.csv` 结构**不改**：每电池仍 `1 + 3*C` 行，缺失槽位三行照旧写空行（`info_csv_writer.write_info_csv` 现状即按定长写空列表→空行，写端零改动）；
2. 唯一必改在读端：`data_loader.py:325` 的 `if float_data:` 把空行整个跳过 → 改为空行也 append 占位，恒保 `len(listPlt[c]) == 电池数`——这就是 Round 1 已定位的错位 bug 本体，修它就是协议的全部；
3. 语义补充放 JSON：`Info_Plot.json` 增 `slot_status/channel_status`（新增键，旧读取端忽略未知键，天然向前兼容）；
4. 禁 0 哨兵（维持 DeepSeek X3 判断）：`pulse_matcher.py:30` `listLevelToRow=0` 与合法行 0 不可分，必须改 `None`。

**为什么不用 `MISSING`/`N/A` 文本 token**：旧读取端对 token 的行为是 `float()` 抛 ValueError → `continue` → `if float_data:` 跳过 → **照样错位**，token 救不了旧读取端，还破坏 CSV 纯数值格式；空行方案对旧文件、旧读取端双向安全。回答用户「有没有必要改变 CSV 结构」：**没有必要，改一处读端逻辑即可**。这同时解释了 Round 1 各家 `MISSING,<档位>,<原因>`（GLM §7-2）/ `MISSING:MISSING_PULSE`（DeepSeek §5.2）提案过重，建议降级采纳空行协议；若坚持 token，必须同步声明"旧版 BatteryChartViewer 读新文件会错位"的兼容代价——用户在意旧结果兼容，故不选。

---

## 5. 同名已有报告（「旧结果」）的安全处理

**核实结论**：旧结果 = `<输出目录>/{test_date}_v{version}/` 同名报告目录。覆盖时机（本轮复核）：`analysis_worker.py:113-114` 在分析开始前 `shutil.rmtree(version_dir)`，`:175-176` 在 rename 前 `shutil.rmtree(final_dir)`。**现状是：只要本次运行的日期+版本号与旧目录相同，旧报告在点击分析的瞬间就被删除，之后新分析若失败/取消，旧结果已经没了**——风险窗口覆盖整个分析期。另注意 `version_manager.py:75` 版本号取自输入文件校验和，切 ndax 后口径变化，同日同版本号的复现概率不可假设为零。

**单选推荐（最省事且零风险）：零删除 + 自动后缀 + staging 原子提交。**

1. 移除两处 `rmtree`（这是现状唯一的数据毁灭点，`filter_data` 崩溃窗口内旧结果已亡）；
2. 新结果先写同盘 staging（`.staging_{uuid}`），全部写完自检后 `os.rename` 提交；
3. 同名已存在 → **不弹框、不删除**，自动改名 `{date}_v{ver}_r2`（递增至空闲）——确定性、不打断用户、旧结果永存；
4. `_v` 目录名的解析处（`data_loader`/电池选择等）兼容 `_r{n}` 后缀（DeepSeek P5 已提示，须落实为测试项）。

备选（需要"覆盖"语义时再用）：改名备份 `backup_{ts}` 后替换——仅在用户显式选择覆盖时走，默认路径不弹框。对比 GLM §5-3「正式目录存在→默认中止并弹框」：那是第三弹，叠加前面两弹一次运行可弹 4~5 次（GLM 自己在冲突 B 里也担心弹框过多），与后缀方案相比无安全增益、徒增打断，**否决**。

---

## 6. 交叉质询：其他方案的证据弱点清单

1. **DeepSeek P2 推荐方案 A（两次读取）——论据不成立**（§2 详述）：其内存收益在逐文件流式下不存在，时间成本实付 2×；新时序下"预检读一遍"被用户裁决架空。请 DeepSeek 在 Round 3 回应：若坚持两次读取，需给出"一次读取峰值内存高于两次"的具体场景，否则改判。
2. **GLM §3 预检含 zip 结构探测且置于运行前**——与用户"数据异常在点击后"冲突（§3 红线 2），须移入 Phase A。
3. **GLM §5-3 同名弹框默认中止**——第三弹问题，改后缀方案。
4. **MiniMax §1.3「filter_data 无需改动」——错误判断**：`data_utils.py:41-42` 空数组时 `filtered_mask = np.zeros(0)` 后 `filtered_mask[0] = True` 直接 IndexError，`:48` 的 `except (ValueError, TypeError)` 捕不住；fallback `:96` `charge_data[0]` 同样越界。此为 P0 必修，四家中仅 MiniMax 漏判，请修正。
5. **Excel 删除清单（四家皆有）——被用户整体推翻**（§1），含 MiniMax 分歧 1「Word 报告存废」、DeepSeek P4 选项 A/B/C 在内全部撤案；报告种类一个不删。
6. **Step.xml 完成状态**：GLM §3-1「有完成字段且已完成→直通」的表述暗含字段必然存在，须按三态降级（§3 红线 1）。MiniMax 分歧 2 的怀疑方向正确。
7. **弹框线程安全**：MiniMax §9.2、DeepSeek §3.3（信号 + Event + 超时按停止）正确，升为验收红线（§3 红线 3）。
8. **维持一致的正确判断**（不重复争论）：`battery_analysis.py:199` `results = [r for r in results if r is not None]` 压缩丢位必改保位；`write_info_json`（`info_csv_writer.py:91-92`）整体 `json.dump` 覆写须改 merge 保护 `profile_validation`；staging/审计留痕先行（journal）方向正确；缺脉冲与中位数偏差分型。

---

## 7. 清晰单选汇总 + 残余风险

| # | 问题 | 单选裁决 |
|---|---|---|
| 1 | 读取次数 | **一次读取**（逐文件流式 + 列投影，派生完即丢 DataFrame）；时间 1× vs 2×、峰值内存不劣，两次读取无成立场景 |
| 2 | 内部缺失协议 | **空行=缺失、读端补位**（CSV 结构零改动），`Info_Plot.json` 增 `slot_status`；不用文本 token |
| 3 | 同名报告 | **零删除 + 自动 `_r{n}` 后缀 + staging 原子提交**；不加第三弹 |
| 4 | 决策时序 | 运行前只做 Step.xml/profile/目录检查；**点击后**一次读取 → 异常汇总 → 两弹（主线程，默认「停止」）→ 提交 |
| 5 | Excel | 报告 Excel 全保留（含 Word 超链接、Sample 模板表）；只删 xlsx 输入/中间层 |

**残余风险**：① 单文件投影后仍超单 worker 内存（与读取次数无关，列投影缓解，极端时未来分块解析）；② Step.xml 解析可行性/字段名未证实（三态降级兜底，unknown 放行留痕）；③ `_v` 目录名后缀解析兼容点（data_loader/电池选择）需回归覆盖；④ QThreadPool 下 Event 等待的取消/超时语义需集成测试（超时=停止整批）；⑤ 切 ndax 后版本号口径变化，同名复现概率上升——靠单选 3 的后缀方案兜底；⑥ 本轮未见真实 ndax fixture，`nda.read` 列名/单位以 converter 取列契约为准，Phase 1 需用真实样本校准。