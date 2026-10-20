# DeepSeek (Round 2): Round 2：用户裁决吸收、占位最小兼容协议、全套报告完整性与异常汇总正确性（含交叉质询）

# DeepSeek Round 2：占位协议、报告完整性、异常汇总正确性与交叉质询

> 立场不变：只讨论不改码。本轮以用户 Round 1 后反馈（0005）为最高优先级，其余 Round 1 意见（含我自己 0004）凡与之冲突的一律撤回或修正。以下代码证据均在本轮重新独立核查（行级引用）。

---

## 0. 用户新裁决的吸收与自我修正（先认错）

**裁决 1（原话"原来所有生成的报告不要变，都得有"）推翻了四家顾问共同的"删 Excel 报告"建议——包括我 Round 1 §4.2/§4.3。现正式撤回。** 具体作废清单：

| 出处 | 被推翻的建议 | 处置 |
|---|---|---|
| DeepSeek R1 §4.2、X5 | 删 `excel_report_writer` 五件套、Sample xlsx 删除、Word 去 Excel 链接 | **撤回** |
| GLM R1 §4、§7-6 | 删 Excel 报告链、Word 链接改指 JSON/CSV | **作废** |
| MiniMax R1 §5.2、分歧 1 | 删 Excel 报告、"Word 报告存废"三选一 | **作废（Word/Excel 全保留，该分歧整体消失）** |
| GPT R1 §2.2、§4、T13 | 删 Excel 报告五件套、"分析结果目录不再出现 Excel 报告"验收项 | **作废（T13 验收项必须删除，它现在直接违反用户裁决）** |

修正后的边界只有八个字：**Excel 退出输入与中间层，报告 Excel 原样保留**。下面 §1 给出精确边界。

**裁决 5（交互时序）**：profile 不一致→点击运行**前**确认；实测数据异常→点击分析**后**汇总+两次确认。这修正了我 R1 §3.1 的固定弹框总序（把 profile 校验放在运行序列②）——前移到输入/运行按钮前阶段。GPT 的"先算不写"结构本身与新时序天然吻合（数据异常本来就只能点击后知道），无需推翻，只需把 profile 段摘出去。

**裁决 2/3/4** 分别对应本轮 §4（一次/两次读取单选）、§2（占位协议释义与最小兼容）、§3（同名报告安全处理）。

---

## 1. 全套报告完整性（重点一）

### 1.1 保留清单（一个都不许少，代码实证全在）

现有报告链 `file_writer.write_all → ReportCoordinator.write()`（`file_writer.py:7-20`）产出**四类交付物**，全部保留：

1. **Excel 报告**：`excel_report_writer.py:96-99` 同时写 Result xlsx 与 Sample xlsx 两个工作簿；`excel_overview/excel_sample/excel_formats/excel_utils` 是其拆分实现，**全部保留**。`excel_sample` 里的 "word" 工作表是人工复制模板用途（我 R1 §4.3 提醒过别误删，现在明确：在保留清单内）。
2. **Word 报告**：`word_report_writer/word_front_matter/word_overview` 保留；`word_overview.py:142,181` 指向 sample/result xlsx 的相对超链接**目标仍然存在，问题自动消失，一个字都不用改**。
3. **CSV 报告**（`csv_writer`/`statistics_utils`）与 **JSON**（`Info_Plot.json` + `json_writer`）保留。
4. **图表**（visualizer 链路）保留。

**内容只增不删**：允许在 Excel/Word/CSV 中增加"数据缺失汇总"区块与缺格标注（见 §2），但表数量、表结构、文件命名（`excel_report_writer.py:88` / `word_report_writer.py:126` 的 `_TD{td}_v{ver}.docx` 命名）、sheet 构成一律不变。

### 1.2 Excel 真正退出的范围（只限输入与中间层）

- `utils/readers/xlsx_reader.py`（`read_xlsx_sheets`/`extract_test_date_from_xls`，分析输入读取）→ 由 ndax 直读取代；
- `utils/file_finder.scan_sorted_xlsx` → 换 ndax 扫描；
- `file_validator.validate_input_directory` 的 `basename=="2_xlsx"` 强制（输入校验）→ 改 ndax 目录规则；
- `excel_processor`/`excel_validator`（**输入** xlsx 校验链）→ 随输入链下线；
- `data_processor` 的 xlsx 扫描、文件名档位解析写 `battery.pulseCurrents` → 档位归 Step.xml。

**易踩坑警告**：删"Excel 输入"时严禁顺手把 `writers/excel_*` 报告模块、`report_coordinator.py:581-586` 的 `ExcelReportWriter` 调用、`strSampleXlsxPath/strResultXlsxPath`（`report_coordinator.py:87-88,159,173`）当输入层垃圾清掉——它们全部属于报告层。删除 PR 必须逐 import 核对消费方，凭"excel"字样批量删文件是本改造最可能"误删报告输出"的路径。

### 1.3 测试清单翻转

我 R1/GPT/GLM 都建议裁剪 `test_excel_report_writer/test_excel_utils/test_excel_processor/test_excel_validator/test_xlsx_reader` 等——**翻转**：报告侧测试（`test_excel_report_writer/test_excel_utils/test_report_qualification` 等）保留并**增补**空位语义用例（缺格写 `N/A（原因）`、不写 0、表结构不变）；只有输入侧测试（`test_xlsx_reader/test_excel_validator` 等服务输入链的）随输入链下线。每个删除测试必须注明它守的是输入链还是报告链，报给用户过目后才许删。

---

## 2. 内部缺失空位：最小兼容协议（重点二，回应用户"显示标记啥意思"）

### 2.1 先解释两个层次（用户问的"标记"到底是什么）

- **内部/中间层标记（机器用，用户看不见）**：`Info_Image.csv` 中某电池某档位的 posi/charge/voltage **三行写成空行**；内存里是 `None/空列表 + 状态枚举`。它的唯一职责是**占住位置**，保证行数恒定、后续电池不前移。
- **用户可见标记（人看）**：图表该电池×档位区域留空 + 灰色文字"缺失(缺脉冲/通道失败)"；Excel/Word/CSV 报告对应单元格写"N/A（缺脉冲）"；报告头部/新增区块列"数据缺失汇总：3# 电池 500mA 档缺脉冲（已放行）"。**人看的标记永远在报告和图上，不在 CSV 里。**

### 2.2 最小兼容协议（单选推荐）：**行数恒定 + 空行=缺失 + 原因进 JSON**

代码实证说明这几乎零改动：

1. **写端现状已经如此**：`info_csv_writer.py:31-37` 每电池固定写 `1 + 3*C` 行（BATTERY 行 + 每档 3 行），缺失档位 `listAllPosiForInfoImageCsv[b][c]` 为空列表 → `csv.writer.writerows` 写出**空行**。即"空行=缺失"就是现行事实格式，旧结果文件里已是这样——**CSV 结构不需要任何改变，这就是最小兼容**。
2. **唯一必改点在读端**：`data_loader.py:303-329` 的 `_process_csv_data` 按 `index % intPerBatteryRows` 取模定位行，但 :325 `if float_data:` 把空行**跳过不 append** → 某电池缺档后 `listPlt[c]` 长度 < 电池数，按电池下标访问即错位。修法：空行也 append 占位（内部 `None`），保证 `len(listPlt[c]) == B`，所有按 b 索引处加 `len==B` 断言。**错位 bug 在读端，不在格式上。**
3. **原因/状态进 JSON（附加键，向后兼容）**：`Info_Plot.json` 增 `slot_status[b][c] = {state: OK|MISSING_PULSE|CHANNEL_FAILED|FILE_FAILED, reason: "..."}`、`channel_status`、`format_version`。旧读取器忽略未知键不受影响；新读取器读旧文件时缺键 → 默认"空行=缺失、其余 OK"。`write_info_json`（`info_csv_writer.py:53-92`）现为整体 `json.dump` 覆写，须改 read-merge-write 且 `profile_validation/slot_status` 只增不减（我 R1 I5 不变量，维持）。
4. **0 哨兵一并铲除**：`pulse_matcher.py:30-31` 把 `listLevelToRow/listLevelToCharge` 初始化为 `0`，而 :116 注释自证"有意去掉 listLevelToRow==0 哨兵保护"——"未匹配"与"第 0 行"不可区分，下游会算出伪造值，直接违反"不可伪造零值"。初值改 `None`，`ChargeCalculator` 遇 `None` 显式返回 `None`（P0 范围，与 `filter_data` 空列表越界同批修）。

### 2.3 否决其他标记法（交叉质询，均有代码级反证）

- **否决 MiniMax 的 `["N/A"]` 占位**（其 §4.1）：①同一槽位内 posi=`[]`、charge=`["N/A"]` 表示不自洽，下游无法用统一判据识别缺失；②字符串混入 float 列表 → `statistics_utils` 算中位数/均值时崩溃或被迫全链 isinstance 防御；③写进 CSV 的 "N/A" 令牌被旧读取器 `float()` 失败后在 :321-323 静默丢弃，退化成空行——等于绕一圈回到我的协议但更脏。
- **否决 GLM 的 `MISSING,<档位>,<原因>` 哨兵行**（其 §7-2）与 **GPT 方案 (b) 显式 MISSING 行**：`_process_csv_data` 用 `loop = index % intPerBatteryRows`（`intPerBatteryRows = 1 + C*3`）**按行号取模定位**，插入任何额外行都会让该电池之后的所有电池整体错位——这是比现状 bug 更糟的回归。若坚持行内标记（如 charge 行写单个 `MISSING:...` 令牌），旧读取器同样退化为跳过→错位。**任何改变行数/注入非数字令牌的方案都破坏兼容，不予采纳。**
- 结论：**CSV 格式不动、空行即缺失、原因去 JSON、可见标注在报告图**。这是唯一同时满足"零迁移成本（旧文件可读）/不错位/不伪造零值/最小改动"四条的协议，请直接单选。

---

## 3. 异常汇总正确性（重点二）

### 3.1 单一事实源 + 四处消费

异常清单必须是**一个冻结的 `AnomalyReport` 对象**（battery_idx、档位、类型、原因、证据、级别），被四处**渲染消费**而非各自重算：弹窗①汇总表、弹窗②空位清单、`run_journal.jsonl`、`Info_Plot.json`/报告缺失汇总。任何"弹窗说 N 个空位、报告写 M 个"的漂移都源于多处重算——MiniMax 的 `exception_collector` 方向对，但没给出冻结与消费约束。

**冻结规则**：弹窗①展示的清单即最终清单（hash 入 journal）；用户确认后若运行期又冒出新异常，**不得静默带新异常写盘**，必须回到弹窗①重新汇总再走两次确认。否则"用户确认的清单"≠"写盘的结果"，留痕失真。

### 3.2 两层分类，弹窗分区呈现（修正 MiniMax 弹窗 mock 的语义污染）

MiniMax §3.2 的弹窗把"缺脉冲"“无法解析"“中位数偏差 1.2mA"混排在同一异常清单、勾一次"我已了解"全放行——**危险**：用户以为放行了缺失，实际连质量告警一起背书。必须分层：

- **决策层（结构性缺失，进两次确认、产生空位）**：`MISSING_PULSE`（档位找不到脉冲）、`CHANNEL_FAILED`（通道数据异常）、`FILE_FAILED`（文件解析失败）。后果：图表留空位、报告标 N/A、统计排除。
- **提示层（质量告警，不进确认、不产生空位，仅提示+留痕）**：中位数偏差 >max(1%,0.5mA) 黄色告警（数据在、槽位照常出数）；Step.xml 完成性 unknown/incomplete 信息行。

弹窗①分区列出；弹窗②的"N 个空位"计数**只含决策层**；两层计数分开留痕。

### 3.3 固定索引不变量（汇总正确性的地基）

- **I1 维度恒定** B×C×V，缺失只改 status 不改维度；
- **I2 序号稳定**：实锤 `battery_analysis.py:198-199`——`results = [results_map.get(i) ...]` 之后紧跟 `results = [r for r in results if r is not None]` **压缩列表**，失败文件的下标被后续电池顶替。这直接违反"不可错位"，且让异常清单的"电池 3 号"与报告的"3 号电池"不是同一坐标系。修法：废除压缩，`None → 占位 BatteryResult`。**汇总清单与最终报告必须共用同一电池序号（输入文件自然排序），这是异常汇总正确性的第一判据。**
- 档位索引 c = Step.xml 配方顺序，全程只读（我 R1 I3，维持）。

### 3.4 两次确认的线程纪律（严禁后台线程弹 Qt 对话框）

分析跑在 QThread worker（`task_runner.py` 的 QRunnable/信号体系，`rename_path` 等信号即证）。grep 实证：**现有 worker 代码里没有任何 QMessageBox**——这条纪律现在是靠"还没做"维持的，改造时极易破坏：

- **反面教材**：MiniMax §6.2 在输出保护流程里内联 `QMessageBox.question(...)`（该函数将在 worker 执行路径上被调）；GLM §5 第 3 步"默认中止并弹框"若实现在替换动作处（worker 内）同罪。二者都违反"不得直接从后台线程弹 Qt 对话框"。
- **正确机制**（我 R1 §3.3，维持）：worker 发信号 → 主线程弹框 → 结果经 `threading.Event`/信号回传，worker 阻塞等待且可取消；**超时/取消/信号对象已销毁一律按「停止整批」处理**（安全默认）。
- 弹窗顺序（点击分析后）：分析完成、异常冻结 → 弹窗①「是否停止整批」（默认停止）→ 继续 → 弹窗②「逐条空位清单 + 确认放行」（默认中止）→ 写盘。弹窗②取消 = 整批中止、零写入、决定入 journal。

### 3.5 Step.xml 完成状态：三态，绝不假定存在

MiniMax 分歧 2 自己承认"代码中未找到 Step.xml 解析逻辑"——**现有代码没有 Step.xml 解析器，NewareNDA 是否暴露完成状态字段也未验证**。因此任何方案都不得写"Step.xml 一定有完成状态"。处理：`complete / incomplete / unknown` 三态；**unknown（无字段/无文件/坏 XML）默认放行 + 留痕**（用户 R1 决定 1 口径）；"未完成=硬阻断"的旧裁决（我 R1 X1 与 GPT C1 都点过名）不得借"档数仲裁"还魂。解析失败本身也只是一条提示层信息行，不是运行阻断。

---

## 4. 一次读取 vs 两次读取：单选「一次读取（先算不写、确认后提交）」

回应用户"哪个时间短、效率高"。结论先行：**单选一次读取**，两次读取在本方案的时序约束下没有任何收益。

**成本账（基于代码结构）**：

- 主开销 = `nda.read()` 解析 data.ndc → DataFrame（磁盘 I/O + 反序列化 CPU）+ 进程池调度/结果序列化（`battery_analysis.py:210-224` `multiprocessing.Pool.map`）。脉冲检测/匹配/电荷计算相对解析成本是小头。
- **两次读取 = 解析成本 ×2 + I/O ×2 + 进程池开销 ×2**。它唯一省的是"确认前不保留结果"，但见下条——本来就不贵。
- **内存账**：一次读取的峰值 ≠ 缓存全批原始时序。逐文件原始 DataFrame 在 worker 进程内派生出脉冲段后即丢弃，主进程只累积**派生结果**（B×C×V 槽位 × 每档脉冲段几十~几千个 float 点，通常远小于百 MB）；进程池并发的原始 DataFrame 峰值是**现状本来就付的成本**，一次读取不增加它。反倒是"读一遍缓存 DataFrame 供两阶段用"（我 R1 P2 方案 B）会把全批时序留在内存，峰值不可控——**撤回我 R1 对方案 A（两遍）的推荐，改推荐 GPT 的先算不写**。
- **时序账（决定性）**：用户裁决要求实测异常只能点击分析后汇总确认。就算做两遍，第一遍也发生在点击后，无法把确认提前到运行前；确认后还要再读一遍才正式分析——纯浪费。预检里真正可以便宜做的是**不解全量的轻探测**（zip/容器完整性、文件计数、Step.xml 存在性），这不是"第二遍读取"。

**适用边界（如实给出）**：若未来出现"必须保留全时序导出/全曲线回放"的需求，派生结果不再是小头，届时按批流式处理，而不是回到两遍读取。当前需求下不存在该场景。

---

## 5. 同名已有报告的安全处理（回应"旧结果是啥/最省事的保护"）

### 5.1 旧结果与覆盖时机（代码实锤）

"旧结果" = `3_analysis results/{test_date}_v{version}/`，内含 §1.1 全部报告（Excel/Word/CSV/JSON/图表数据）。现状覆盖时机**两处都是无确认硬删**：

- `analysis_worker.py:114`：开工先 `shutil.rmtree(version_dir)`（`version_dir = f"{output}/v{ver}"`）；
- `analysis_worker.py:173-176`：rename 前 `shutil.rmtree(final_dir)`（`final_dir = f"{output}/{test_date}_v{ver}"`）——**这正是旧报告目录（Excel/Word 全在其中）在分析成功前一刻被删除的窗口**；中途崩溃/取消 = 新旧报告全无。这就是"误删报告输出"的真实风险源，不是假想。

### 5.2 最省事保护（单选）：**零删除 + 新目录自动避让**

- 两处 `rmtree` 直接删除；分析完成后若 `{date}_v{ver}` 已存在，**新结果自动改名 `{date}_v{ver}_r{n}`（递增）**，旧目录一律不碰、不弹框、不 rename 旧目录。
- 为什么优于其他方案：GLM"默认中止并弹框"和 MiniMax"覆盖/新建/取消弹框"都要在 rename 时刻弹框——此时人在 worker 线程（§3.4 违规）且 test_date 只有分析后才知道（`analysis_worker.py:160-170` 从数据派生），弹框时机晚、实现还容易踩线程坑；GPT 的 `backup_{timestamp}` 改名旧目录虽然不删，但"动了旧结果"（改名失败需回滚，有残余风险）。**自动避让是唯一零触碰旧目录、零对话框、零恢复逻辑的方案**，最符合"最省事"。
- 命名兼容已验证：`excel_report_writer.py:83`/`word_report_writer.py:72` 的 `basename.split("_v")[0]` 对 `_r{n}` 后缀取前段仍得 date；`report_manager.py:66` 的 `f"_v{ver}" in docx_file.name` 是子串匹配，天然兼容。仍建议在 `data_loader/battery_selection` 的目录解析处补一条带后缀的回归测试。

### 5.3 本轮新发现的关键隐患（四家 R1 都没抓到）：**输出目录名被多处重复计算**

`report_coordinator.py:325`（`os.path.join(strResultPath, f"{td}_v{listTestInfo[16]}")`）和 `json_writer.py:24` **各自独立重新拼** `{td}_v{ver}` 目录名，而 `analysis_worker.py:173` 也拼同一个名字再 `os.rename`。这意味着：若防覆盖策略只在 worker 端给目录加 `_r{n}` 后缀，**Excel/Word/CSV/JSON 写入器仍按原名拼路径，会把新报告写进旧的同名目录里——静默覆盖旧报告，恰好犯了"误删报告输出"的大忌**。因此任何防覆盖方案的前置条件是：**输出目录名只解析一次（worker 端裁决最终名），经参数统一下发给全部写入器；禁止写入器各自拼名**。此项应列为实现工单的硬前置，验收 = 全仓 grep 无第二处 `f"{td}_v{...}"` 拼名。

### 5.4 其他防误删纪律

- staging/临时目录清理用**白名单前缀**（只删自己创建的 `.staging_*`），禁止宽 glob；`file_service.py:121` 的通用 `shutil.rmtree` 删除服务不得被输出保护流程复用（它是用户主动删除用的通用设施，别把它串进自动清理）。
- 用户在任何确认点选择停止 → 只弃 staging，正式目录零接触。

---

## 6. 交叉质询汇总（对三家证据弱点 + 自我修正）

| 对象 | 弱点 | 反证/修正 |
|---|---|---|
| GLM §7-2 哨兵行 | `MISSING,<档位>,<原因>` 插行破坏 `index % intPerBatteryRows` 定长解析 | `data_loader.py:305-307` 取模定位实锤，插行使后续电池全部错位；改用 §2.2 空行协议 |
| MiniMax §4.1 `["N/A"]` | 字符串污染数值列表、槽位表示不自洽 | 统计链崩溃风险；且旧读取器退化为空行，无收益 |
| MiniMax §3.2 弹窗 mock | 质量告警与结构缺失混排、一次勾选全放行 | §3.2 两层分离，弹窗分区、计数分开 |
| MiniMax §1.3 | 称 filter_data P0"无需改动" | 与三家 `filtered_mask[0]=True` 空数组 IndexError 实锤冲突（except 不含 IndexError），必须修 |
| MiniMax §6.2 / GLM §5-3 | 在 worker 流程内弹 QMessageBox | 违反"后台线程不弹 Qt 对话框"；改信号+Event（§3.4） |
| GPT §3.1 时序 | profile 校验放在运行序列内 | 用户裁决要求前移到点击运行前；数据异常两次确认留点击后 |
| GPT §5 backup 改名 | rename 旧目录仍有失败恢复残余风险 | 换 `_r{n}` 自动避让，零触碰旧目录 |
| GPT T13 | "结果目录不再出现 Excel 报告"验收项 | 直接违反用户裁决，删除该验收项 |
| 全体（含我 R1） | 未发现 `{td}_v{ver}` 路径重复拼名 | §5.3 新证据：防覆盖必须先统一下发目录名 |
| 我 R1 P2 推荐两遍读取 | 成本估错 | 撤回，单选一次读取（§4） |
| 我 R1 §4.2 删 Excel | 被用户推翻 | 撤回（§0） |

---

## 7. 收敛后的单选清单（请直接拍板采纳）

1. **报告**：全部报告种类保留（Excel 双工作簿 + Word + CSV + JSON + 图表），Excel 仅退出输入/中间层（§1.2 清单），报告内容只增缺失标注不删类型。
2. **占位协议**：行数恒定 `1+3*C` + 空行=缺失 + 原因进 `Info_Plot.json` 附加键 + 读端对齐修复；`pulse_matcher` 0 哨兵改 `None`（§2.2）。
3. **读取次数**：一次读取（先算不写、确认后提交）；预检只做不解全量的轻探测（§4）。
4. **同名报告**：零删除，`{date}_v{ver}_r{n}` 自动避让；前置条件 = 输出目录名统一下发（§5.3）。
5. **交互时序**：profile 不一致在点击运行前确认（决定 4 语义不变）；数据异常在点击分析后汇总、两次确认（弹窗①默认停止、弹窗②默认中止），全程主线程弹框。
6. **Step.xml**：三态 complete/incomplete/unknown，unknown 默认放行留痕，不假定字段存在。
7. **异常汇总**：单一冻结 AnomalyReport 四处消费；决策层/提示层分离；序号与报告同坐标系（废除 `results` 压缩）。

## 8. 残余风险

- `nda.read()` 列契约仍以 `ndax/converter.py` 为准，尚无真实 fixture 校准（沿 R1）。
- 独立 BatteryChartViewer 若为外部旧版二进制，读新文件的空行槽位仍会错位（我们只保证本仓读端修复；旧文件本就含空行，无新增破坏）。
- `_r{n}` 后缀对 `data_loader/battery_selection` 目录解析的兼容已静态推断（split/子串匹配），未跑运行时验证，需补回归测试。
- `excel_sample` 的 "word" 工作表模板机制对"N/A（原因）"单元格的承载未实测，报告增补标注前先做模板探测。
