# DeepSeek (Round 1): DeepSeek Round 1：端到端改造方案（数据模型/不变量/失败恢复视角）

# DeepSeek Round 1：系统视角的端到端改造方案

以下全部为顾问意见，不改任何代码。用户已决定事项（transcript §用户最新决定 1–6）一律作为约束遵守，只在互相冲突或与代码现状冲突处如实指出。代码证据均已独立复核。

---

## 0. 约束回顾（只列与系统设计相关的口径）

- R1 完成性：Step.xml 有明确完成状态且完成→通过；无字段/无文件→默认放行，不再硬阻断"未完成"。
- R2 异常处理：某档位找不到脉冲/某通道失败不默认中止；预检汇总全部异常 → 弹框①「是否停止整批」→ 选继续 → 弹框②二次明确确认 → 确认后保留故障通道/档位的固定索引空位，**不可错位、不可伪造零值**；异常清单与用户决定必须留痕。
- R3 主链路全程 ndax：Step.xml = 配方档位来源；`NewareNDA.nda.read()` 读 data.ndc 时序 DataFrame 派生分析结构；**分析输入链路禁止扫描/读取 2_xlsx，不经 xlsx 中间层**；Excel 只保留在独立 ndax→Excel 导出功能。
- R4 profile 可选：无 profile 免责声明一次（QSettings `validation/profile_disclaimer_version`）；有 profile 只做与 ndax 档位比较；同数不同档→明确阻断+「以 ndax 为准继续」按钮（默认中止）；档数不一致→人工确认出口；多 ndax 配方档位不一致→硬阻断（保留旧定案）；实测中位数偏差 >max(1%, 0.5mA)→黄色告警放行留痕（与"找不到脉冲"分清）。
- R5 校验/用户确认必须发生在删除旧结果**之前**；成功后写 `Info_Plot.json.profile_validation`（policy_version `2026.10`），留痕不可被后续写入覆盖。
- R6 `filter_data()` 空档位越界是 P0 修复项；缺脉冲可放行但不能静默丢通道；图表/Word/JSON 需显式缺失语义+固定通道索引。

---

## 1. NDAX 真实数据模型与核心不变量

### 1.1 数据模型（基于 converter.py 现有列契约复核）

`ndax/converter.py` 已证明 `nda.read(path, software_cycle_number=False)` 输出 DataFrame 至少含列：`Cycle, Step, Status, Current(mA), Voltage, Charge_Capacity(mAh), Discharge_Capacity(mAh), Timestamp`（见 `_build_record_sheet/_build_step_sheet/_build_cycle_sheet` 的取列）。这正是分析所需的全部原料：

- **配方元数据**：Step.xml（脉冲电流档序列、截止电压档序列、工步完成状态）。
- **时序事实**：data.ndc（经 `nda.read()` 成 DataFrame）。
- **派生三视图**：现有 `read_xlsx_sheets()` 返回的 `(cycle_df, step_df, record_df)` 三表语义可直接由 DataFrame `groupby` 派生（converter 的 `_build_*_sheet` 就是同一派生逻辑的写盘版）。**建议定义 `NdaDataset` 适配层**，暴露与三表同构的只读视图（列位语义与 `iloc[:,0..4]` 保持一致），使 `pulse_detector / pulse_matcher / charge_calculator` 的算法层改动降到最低——只换数据来源，不换匹配/计算语义。

> ⚠ 需澄清（见分歧 P1）：transcript 说"nda.read() 读取 data.ndc"，而 `converter.convert_one` 现在传的是 `.ndax` 文件（converter.py:185）。`1_ndax/` 目录里到底是 `*.ndax` 容器还是解包的 `Step.xml + data.ndc` 目录，决定 Step.xml 的读取路径和 `nda.read()` 的参数形态。建议无论哪种，都收敛到一个 `ndax/reader.py` 适配器统一归一化。

### 1.2 通道/档位不变量（整个改造必须成立的 5 条）

- **I1 维度恒定**：结果结构维度恒为 `B（电池/文件序）× C（电流档）× V（电压档）`。任何缺失只改变该槽位的 `status`，绝不改变维度，绝不压缩列表。
- **I2 序号稳定**：电池顺序 = 输入文件自然排序序号，Info_Image.csv、统计、图表、Word 全部使用同一序号。当前代码有一个**错位隐患**：`battery_analysis.py` run() 里 `results = [r for r in results if r is not None]`（约 185 行）静默剔除失败文件，"通道"（原始文件序号）从此丢失；文件名与数据虽仍成对，但"第 n 号通道数据缺失"无法表达。新模型必须按 `idx` 保留槽位。
- **I3 档位只读**：`C/V` 序列一旦从 Step.xml 解析出来，全程只读；profile、文件名解析、全局 `battery.pulseCurrents` 都不得改写它（现 `data_processor._process_first_excel_file` 会把文件名解析档位写进全局配置并被 `data_loader._get_pulse_current_level` 读回解释 CSV——这是隐藏耦合，必须切断，见 §4）。
- **I4 缺失显式**：缺失值 = `None/NaN + status 枚举`。**禁止 0 哨兵**：`pulse_matcher._init_level_structures` 把 `listLevelToRow[c][v]` 初始化为 `0`，而 0 是合法行索引，"未匹配"与"第一行匹配"不可区分，下游 `ChargeCalculator.calculate(0)` 会静默算出伪造值——直接违反 R2"不可伪造零值"。这是与 R2 冲突的现存代码（X3），必须改。
- **I5 留痕只增不减**：`profile_validation`、异常放行记录一经写入，任何后续写盘不得覆盖/丢失。

`status` 枚举建议：`OK / MISSING_PULSE（档位找不到脉冲） / CHANNEL_FAILED（通道数据异常） / FILE_FAILED（文件解析失败） / NOT_COLLECTED（用户确认前即缺）`。

### 1.3 失败恢复与一致性

- **进程池崩溃**：`battery_analysis.py` 并行段只捕获 `(FileNotFoundError, PermissionError, ValueError, KeyError, IndexError, BatteryAnalysisException)`；`BrokenProcessPool`（子进程崩溃）不在此列，会穿透 run() 的 except 列表直达 worker 顶层，表现为整批失败且报错含糊。新方案应把"单文件异常"归为通道级空位、"进程池破裂"归为基础设施级失败（整批中止、旧结果不动、journal 留痕），二者分开分类。
- **取消一致性**：`AnalysisWorker.request_cancel` 是协作式；只要取消点不晚于"写盘完成"，且全程无 `rmtree`，旧结果天然零风险（见 §6）。
- **幂等/重跑**：同一批数据重跑 = 新目录（后缀递增），永不覆盖；中断残留的 staging 目录定期清理，不影响任何既有结果。

---

## 2. 端到端实施阶段（依赖序 + 可独立验收）

**Phase 0 — P0 防御（可立即独立合入，不等 ndax 改造）**
- `data_utils.filter_data`：循环头空判 `if not charge_data: append([]); continue`（旧定案修法）。
- `data_loader.filter_data`：同样空判（`charge_single[0]` 同根因）。
- `pulse_matcher`：0 哨兵改 `None`（或先加 `matched` 标志位，Phase 4 收敛）。
- 验收：空档/单点/全空输入不崩、不产伪造值。

**Phase 1 — ndax 读取层（新模块 `ndax/reader.py`）**
- Step.xml 解析：配方档位（C、V 序列）、完成状态（complete / unknown）；坏 XML / 缺文件 → 结构化错误对象（不是异常即死）。
- `nda.read()` → `NdaDataset`（三视图派生，接口对齐现有 `read_xlsx_sheets` 列位语义）。
- 测试日期/时间戳改由 `Timestamp` 首末派生（替代 `extract_test_date_from_xls`）。
- 验收：同一 fixture，`NdaDataset` 三视图与 converter 写出的 xlsx 三表数值一致（parity 基准）。

**Phase 2 — profile 校验层（纯函数 + UI 适配）**
- `input_validator`：`test_profile` 从两处必填清单移除（`REQUIRED_TEXT_FIELDS` 与 `_validate_required_fields`）；`validation_feedback` 对应 label 规则同步。
- 无 profile：免责声明一次（QSettings `validation/profile_disclaimer_version`="2026.10"，UI 层写，engine 保持无 Qt）。
- 有 profile：仅与 ndax（Step.xml）档位比较 →（a）同数同值通过；（b）同数异值：阻断弹窗 +「以 ndax 为准继续」按钮，默认中止；（c）档数不一致：人工确认出口，默认中止；（d）多 ndax 文件间档位不一致：硬阻断无放行（保留旧定案，优先级高于一切放行）。
- 完成性检查：`check_completion(step_xml)`：complete→通过；unknown/缺字段/缺文件→默认放行（R1）。
- 成功写 `Info_Plot.json.profile_validation`：`{result, mismatch_type, decision, policy_version:"2026.10"}`；枚举需按 R1/R4 重定义（见冲突 X1）。
- 验收：分支矩阵全覆盖（见 §7）。

**Phase 3 — 异常预检 + 两次确认（见 §3）**

**Phase 4 — 分析核心改造**
- `battery_analysis.BatteryAnalysis`：`scan_sorted_xlsx`→ndax 扫描；`_parallel_process_file` 的 `read_xlsx_sheets`→`NdaDataset`；`detect_pulse_rows`/`match_pulse_levels`/`ChargeCalculator` 输入改为数据集视图。
- 文件失败/档位失败不再剔除（废除 `results = [r ... if r is not None]`），按 idx 产出带 status 的槽位（I2）。
- `UBA_GetTestDateFromExcel / extract_test_date_from_xls / UBA_AnalysisXlsx` 的 xlsx 依赖拆除。

**Phase 5 — 输出层缺失语义（见 §5）**
- `info_csv_writer`（占位 schema + 合并写留痕）、`data_loader`（固定索引读取）、统计/图表/Word 的缺失呈现。

**Phase 6 — 删改边界落地（见 §4）**
- 删除 Excel 报告链与 xlsx 输入链；保留独立 ndax→Excel 导出；架构守卫测试（grep/imports）防止 2_xlsx 回流分析链。

**Phase 7 — 输出安全机制 + 迁移收尾（见 §6）**
- staging+rename、去 rmtree、run_journal；回归 parity 与故障注入测试。

依赖关系：0 独立；1→2→3→4→5 严格串行（后者消费前者契约）；6 在 4/5 后做删代码最安全；7 与 3/5 有接口耦合（journal、留痕时机），建议与 3 同期设计、与 5 同期落地。每阶段可单独验收回滚，任一阶段失败不影响旧链路（旧链路删除放最后一步）。

---

## 3. 异常预检汇总 + 两次确认（流程与一致性设计）

### 3.1 固定交互序（同一次 run 的弹框总序必须钉死）

```
① 多 ndax 档位一致性        → 不一致=硬阻断（无放行）
② profile 校验/免责声明      → 阻断+按钮 / 确认出口 / 免责一次
③ 完成性检查                → complete 或 unknown（默认放行，仅记 warning）
④ 异常预检汇总 → 弹框①「是否停止整批」→ 继续 → 弹框②二次确认
⑤ 以上全部完成之后，才允许触碰输出目录/写盘
```

②④ 都是"人工决定"，但性质不同：②是配方级（profile vs ndax）逐类阻断，④是数据级（缺脉冲/坏通道）批量汇总。不把二者混进同一个弹框，避免"放行一次=放行全部"的语义污染。

### 3.2 预检内容与成本

- 预检 = 对每个输入文件做 `read + derive + detect_pulse + match_levels`（不含电荷计算、写盘），产出 `AnomalyReport`：
  `{file, battery_idx, current_level, voltage_level?, type(MISSING_PULSE/CHANNEL_FAILED/FILE_FAILED), detail}`。
- **成本权衡（分歧 P2）**：预检必然要读全量数据。方案 A：轻量预检（只做脉冲检测/匹配，随后丢弃 DataFrame，分析阶段重读一遍）——内存安全、CPU ~2×；方案 B：解析一次缓存 DataFrame 供两阶段使用——快、但大批次内存不可控；方案 C：按批缓存（折中）。我推荐 A（可再生、失败恢复简单），除非实测 `nda.read()` 是瓶颈。

### 3.3 弹框①/② 与留痕

- 弹框①：异常汇总表（固定列：电池/通道、档位、异常类型、详情），默认按钮**「停止整批」**；选停止→中止，零写盘零删除。
- 弹框②：仅当选继续才弹，明确列出"N 个空位、报告将出现 N/A 标注"，勾选「我已知悉」+ 默认**「返回中止」**。
- 留痕（R2/R5）：确认结果立即 append 到输出根目录 `run_journal.jsonl`（append-only，含时间戳、异常清单 hash、决定、policy_version），结果目录落定后在 `Info_Plot.json`（或 `anomaly_decisions` 键）中复制引用。journal 先行的原因：结果目录此刻尚未创建/命名（见冲突 X6）。
- 弹框跨线程机制：预检在 worker 线程跑，结果经信号回主线程弹框，worker 阻塞在 `threading.Event` 等决定（可取消）；取消/超时一律按"停止整批"处理。

### 3.4 边界澄清

- 黄色中位数偏差告警**不进**两次确认（它是质量告警，不是数据缺失），只在预检汇总里以 warning 行展示+留痕（分歧 P7 待确认）。
- "完成性 unknown"（R1 默认放行）建议作为 warning 行列入汇总，但不触发弹框②。
- 整文件无脉冲：现代码 `raise "Pulse data not found"` 直接丢文件——改为 FILE/CHANNEL 级空位进汇总（除非用户在弹框①选停止）。

---

## 4. Excel 删改边界（仅保留独立 ndax→Excel 导出）

### 4.1 保留（唯一 Excel 功能）
- `ndax/converter.py`（`convert_one/convert_batch/get_ndax_files`、Record 超行拆表逻辑）、`ndax/worker.py`（ConvertWorker）、`main/tabs/ndax_tab.py` 导出 UI。
- 改动点：`ndax_tab._find_and_fill_test_profile`（约 178 行起）经 `path_manager.set_input_path` 自动填 **2_xlsx** 为分析输入路径——必须改为指向 ndax 数据目录；导出目标 `../2_xlsx` 命名可保留（导出是独立功能），但分析输入校验必须**拒绝** 2_xlsx 目录（防呆）。
- 导出功能自带的"已存在→覆盖确认"（`_start_convert`）语义独立于 §6 的"输出不覆盖旧结果"（那是分析结果），需用户确认豁免（分歧 P5）。

### 4.2 删除
- Excel 报告链：`utils/writers/excel_report_writer.py / excel_overview.py / excel_sample.py / excel_formats.py / excel_utils.py`，及 `report_coordinator.write()`（581–584 行）的 `ExcelReportWriter` 调用（Word/CsvWriter 保留）。
- xlsx 输入链：`utils/readers/xlsx_reader.py`（`read_xlsx_sheets`、`extract_test_date_from_xls`）、`utils/file_finder.scan_sorted_xlsx`、`main/business_logic/excel_validator.py`、`utils/processors/excel_processor.py`（`read_excel_smart` 仅被 excel_validator 引用，已复核）、`file_validator.validate_excel_filename`、`validate_input_directory` 的 `basename=="2_xlsx"` 强制、`data_processor` 的 `_scan_excel_files_task/_process_excel_files_task` 等 xlsx 扫描校验段、`battery_analysis.py` 对上述的引用。
- `data_processor._process_first_excel_file` 中文件名档位解析→全局 `battery.pulseCurrents` 的写入链拆除/降级（档位主导权归 Step.xml，I3）；`filename_parser` 的型号/批次/制造商识别**保留**（旧定案：其余调用点不动）。`_verify_pulse_currents`（文件名 vs 查表双重验证）建议降级为"filename/table vs Step.xml"的 warning 交叉检查（分歧 P9）。

### 4.3 连带影响（必须拍板，见 P4）
- `word_overview.py:142,181` 的 `word_utils.add_hyperlink` 指向 `strResultXlsxPath/strSampleXlsxPath`（Word 报告里的 Excel 相对链接）；Excel 报告删除后链接悬空。
- `excel_sample._write_sample_word` 写的是 **Sample xlsx 里的 "word" 工作表**（人工复制模板用途），不是 docx——Sample xlsx 本身也是 Excel 产物，按"其他 Excel 逻辑全部移除"应删，但会失去该模板功能。
- 选项：A（推荐）Word 去掉 Excel 链接、Sample xlsx 删除；B 链接指向用户手动导出的 xlsx（路径不可预测，不推荐）；C 保留 Sample xlsx（与用户决定冲突，需用户明确豁免）。

---

## 5. 缺档/坏通道的固定索引空位与报告处理

### 5.1 数据模型
- 内存：`results[b][c][v] = (charge|None, status)`；`curves[b][c] = [(charge,voltage)...] | None`（I1/I4）。
- `pulse_matcher`：`listLevelToRow` 初值 `None`；`ChargeCalculator.calculate(None)` 显式返回 `None`（不返回 0）。

### 5.2 Info_Image.csv 固定槽位 schema
- 每电池固定 `1 + 3*C` 行（BATTERY + 每档 posi/charge/voltage 三行）——缺失档位的三行写显式标记（如 `MISSING:MISSING_PULSE`），**不允许空行跳过**。
- `data_loader._process_csv_data` 现状是"空行不 append"（float_data 空则跳过）→ `listPlt[c]` 长度 < `intBatteryNum` → 后续"按电池下标访问"错位。改为：任何行都 append（标记→`None` 占位），保持 `len(listPlt[c]) == B`；绘图处跳过 `None` 并在旁注标注缺失数量；所有按 b 索引处加 `len==B` 断言。
- 解释权修正（I3）：`_get_pulse_current_level` 现读全局 `battery.pulseCurrents` 解释 CSV，与写端 `listTestInfo[14]`（Step.xml 档位）存在漂移风险；改读 `Info_Plot.json.current_levels`（写端已有该键），消灭全局状态耦合。

### 5.3 报告/统计/图表
- 统计（`statistics_utils.compute_list_cpt/compute_statistics`）：`None` 排除并输出 `valid_n/missing_n`；箱线图/曲线跳过缺失电池；不得把缺失当 0 参与中位数（关联分歧 P10 的中位数口径）。
- Word（Excel 删除后是唯一报告）：样本表缺格写 `N/A（缺脉冲/通道失败）`；报告头部新增"数据缺失汇总"段（引用预检清单）。
- Info_Plot.json：`profile_validation` + 异常决定记录合并写入（§6）。

---

## 6. 输出不覆盖旧结果的安全机制

现状（必须改）：`analysis_worker.py` 分析前 `shutil.rmtree(version_dir)`，重命名前 `shutil.rmtree(final_dir)`——旧结果被删，且删除发生在分析异常/取消之前，中途失败 = 旧结果已没、新结果没有。

新机制四件套：
1. **确认先行**：§3.1 的 ①–④ 全部完成前，禁止任何删除/写盘（R5；天然满足"校验/确认先于删除"）。
2. **零删除**：废除两处 `rmtree`；同名已存在 → 新目录后缀 `{date}_v{ver}_r{n}`（或时间戳，分歧 P5）。注意 `rename_path` 信号、`version_manager`、`data_loader/battery_selection` 的 `"_v"` 目录名解析需兼容后缀。
3. **原子写**：全部产物先写 `{final}.staging/<uuid>/`，成功后同卷 `os.rename` 到最终名；失败/取消 → staging 保留供诊断、旧结果原样；启动时清理 >24h 的过期 staging。
4. **留痕不可覆盖**：`write_info_json` 现为整体 `json.dump` 覆写——改为 read-merge-write，`profile_validation/anomaly_decisions` 键只增不减（I5）；写入时机因目录命名依赖分析后的 test_date（冲突 X6），方案：确认时刻先写 `run_journal.jsonl`（append-only，输出根目录），结果目录落定后把留痕合并进 `Info_Plot.json` 一次性写入（staging 内完成），并在测试中断言"后续任何写盘不得删除该键"。

---

## 7. 测试矩阵

| # | 层次 | 用例 |
|---|------|------|
| T1 | unit | `filter_data`（data_utils + data_loader）空/单点/全空/混合档位不崩、不产伪造值（P0 回归） |
| T2 | unit | `pulse_matcher`：档位全匹配 / 部分缺脉冲（返回 None 槽位非 0）/ 全缺（结构化失败） |
| T3 | unit | Step.xml 解析：完成/未完成/无字段/缺文件/坏 XML → R1 语义矩阵 |
| T4 | unit | `check_completion`：complete 通过、unknown 默认放行 |
| T5 | unit | profile 比较分支：无 profile（免责+QSettings 记忆）、同数同值、同数异值（默认中止+以 ndax 继续）、档数不一致（确认出口）、多 ndax 档位不一致（硬阻断） |
| T6 | unit | `profile_validation` 留痕 schema（mismatch_type/decision/policy_version="2026.10"）+ 只增不减（写后重跑 write_info_json 不丢） |
| T7 | integration | 预检汇总聚合（缺脉冲/坏通道/坏文件）+ 弹框①②顺序、默认按钮、第二次拒绝→中止零写盘（pytest-qt + mock） |
| T8 | integration | 固定索引不变量：混合缺失批次，`B×C×V` 维度恒定、Info_Image.csv 占位往返后 `len(listPlt[c])==B` |
| T9 | integration | 统计/图表/Word 缺失语义：N/A 显示、统计排除、箱线图跳过、缺失汇总段 |
| T10 | integration | 输出安全：旧目录不删、重跑 `_r2` 新目录、staging 原子 rename、fault injection（kill/取消）后旧结果完好、journal 有记录 |
| T11 | parity/golden | 同一 fixture 旧管线（converter→xlsx→分析）vs 新 ndax 直读：Info_Image/统计数值一致（容差内） |
| T12 | e2e/UI | 端到端：ndax 目录→预检→放行→报告；无 profile 免责只弹一次 |
| T13 | e2e | Excel 边界：分析结果目录不再出现 Excel 报告；独立 ndax→Excel 导出回归（含 Record 拆表、覆盖确认） |
| T14 | arch | 静态守卫：分析链路 import/字符串不含 `read_xlsx_sheets/scan_sorted_xlsx/2_xlsx`；`validate_input_directory` 拒绝 2_xlsx |
| T15 | robustness | `BrokenProcessPool` 分类为基础设施失败；单文件异常=通道空位不炸批；取消协作点覆盖全阶段 |

Fixture 策略：需要真实录制的 ndax/Step.xml+data.ndc 样本（合成 data.ndc 不现实）；T11 的 parity 基准由 converter 现状生成，冻结为 golden。

---

## 8. 冲突与需拍板分歧（如实列出，不替用户决定）

### 8.1 决策之间的冲突
- **X1**：旧会议裁决④（Step.xml 工步完成状态做档数仲裁、truncated/missing_evidence 硬阻断）被新决定 1/4 覆盖：完成状态不再用于档数判断、缺证据默认放行。`mismatch_type` 旧三值（`level_count_mismatch_complete/truncated/missing_evidence`）作废，建议新枚举 `level_count_mismatch` + `evidence=complete|unknown` + `decision`。需用户确认命名。
- **X2**：决定 2 的"预检汇总+两次确认"与决定 4 的逐类阻断弹框并存 → 同一 run 弹框可达 4+ 次；且决定 5 要求全部确认先于删除旧结果 → 预检必须在输出目录变更前全量解析（引出 P2 成本问题）。我给出的固定弹框总序（§3.1）需用户认可。
- **X3**：决定 2"不可伪造零值" vs 现存 0 哨兵（`pulse_matcher._init_level_structures`、`UBA_AnalysisXlsx` 日志、`ChargeCalculator.calculate(0)`）与 `filter_data` 空列表崩溃同根因，必须一并改（P0 范围扩大）。
- **X4**：决定 3"分析链路禁 2_xlsx" vs 现状三处绑定：`path_manager.set_input_path`（2_xlsx）、`file_validator.validate_input_directory`（basename=="2_xlsx"）、`data_processor` xlsx 扫描；另 `ndax_tab` 自动填输入路径指向 2_xlsx。全改，但导出功能仍写 2_xlsx（独立功能，允许）。
- **X5**："Excel 全部移除" vs Word 报告超链接（word_overview.py:142,181）与 Sample xlsx 模板功能（P4）。
- **X6**："成功写 Info_Plot.json.profile_validation 留痕" vs 留痕时刻结果目录尚未创建/将重命名（`version_dir→final_dir`），且 `write_info_json` 整体覆写（P6，§6 给了 journal+合并写方案）。
- **X7**："输出不覆盖旧结果" vs 现有 rmtree+rename 与"同版本重跑即覆盖"的既有语义（P5）。

### 8.2 需用户拍板的分歧
- **P1 输入物理形态**：`1_ndax/` 是 `*.ndax` 文件还是解包 `Step.xml + data.ndc` 目录？Step.xml 从哪读（容器内/导出目录）？`nda.read()` 参数形态随之确定。
- **P2 预检成本**：解析两遍（A，推荐）/解析一次全缓存（B）/按批缓存（C）。
- **P3 "通道"定义与文件级失败语义**："坏通道"=一个电池文件还是仪器通道号？坏文件是否也走两次确认保留整电池空位，还是硬中止？
- **P4** Word Excel 链接与 Sample xlsx 去留（A/B/C 选项见 §4.3）。
- **P5** 新目录命名策略（`_r{n}` 后缀 vs 时间戳 vs 弹框选择）；导出功能覆盖确认是否豁免"不覆盖"原则。
- **P6** 留痕写入时机确认（journal 先行 + staging 内合并写 `Info_Plot.json`）。
- **P7** 中位数偏差黄色告警是否列入预检汇总弹框（建议：列 warning 行、不进两次确认）。
- **P8** 多 ndax 档位不一致硬阻断的边界确认：它优先于决定 2 的"不默认中止"，即属配置级错误，不给放行（沿用旧定案，请确认与决定 2 不矛盾）。
- **P9** `test_profile` 退出必填后的联动清理范围（`validation_fields/validation_manager` 的 `_temperature_set_from_xml` 等 legacy 逻辑）；`_verify_pulse_currents` 是否降级为 warning。
- **P10** 缺档/缺通道批次中"实测中位数偏差"的计算口径（排除缺失后计算？`valid_n` 下限？）。

---

## 9. 残余风险（本方案自身的）

- `nda.read()` 对目标数据形态（P1）的列契约以 converter.py 为准，但未在本目录见到真实 fixture，列名/单位若有出入需在 Phase 1 用真实样本校准。
- Word 模板（`Battery Measurement Report of TypeC...docx`）占位符机制对"空位/缺失汇总段"的承载能力未验证，Phase 5 需先做模板探测。
- `os.rename` 原子性以同卷为前提，输出根目录若跨卷（网络盘），需退化为 copy+校验+rename。
