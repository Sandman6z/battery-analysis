# GPT (Round 1): GPT (Round 1): 端到端改造方案——入口重塑、迁移阶段、空位语义、Excel 边界与输出安全

# GPT（Round 1）：NDAX 直读分析与异常放行的整体改造方案（战略/入口/迁移/边界）

> 立场：只提案、不改码。用户已定事项（transcript「用户最新决定」1–6 与旧会议未被覆盖的定案）一律视为约束，不重开；发现互相冲突之处在文末如实列出。以下结论均基于我对关键代码的独立核查（含行级证据）。

---

## 0. 战略总纲：把管线重构成「先算不写、两段提交」

本次改造的本质不是换数据源，而是把「分析 = 边算边写、失败即弃」重构为：

- **Phase A（只读计算段）**：ndax 直读 → 配方/profile 校验 → 全批内存分析 + 异常收集。**不删除任何旧文件、不写任何新文件**。
- **确认段**：profile 校验交互 → 异常预检汇总弹窗（是否停止整批）→ 二次明确确认。全部决定留痕。
- **Phase B（提交段）**：staging 目录落盘 → 原子切换到最终目录，旧结果只在新结果完整落盘后才被替换。

这个结构一次性满足用户的三条硬约束：①「校验/用户确认应发生于删除旧结果前」（决定 5）；②「先预检汇总全部异常再决定」（决定 2）；③输出不覆盖旧结果。且**不需要读两遍 ndax**——预检所依据的「哪个电池哪个档位找不到脉冲」恰恰就是分析本身产生的副产品，全批分析做完、结果暂存内存，异常清单自然完整。相比「先跑一遍预检再跑一遍正式分析」的双倍解析成本，先算不写是零额外成本的方案。

---

## 1. 端到端目标数据流与实施阶段

### 1.1 目标数据流（替换现状）

```
[现状] 选 2_xlsx → DataProcessor 扫 xlsx/文件名解析档位 → InputValidator(test_profile 必填)
      → AnalysisWorker：rmtree(v{ver}) → BatteryAnalysis(scan xlsx → read_xlsx_sheets
      → detect_pulse_rows → match_pulse_levels → ChargeCalculator)
      → 写 Info_Image.csv/Info_Plot.json → rmtree(final) + rename → Excel/Word/CSV 报告 → visualizer

[目标] 选 ndax 目录（+可选 profile XML）
      → NDaxDataSource：Step.xml 配方档位 + nda.read() 时序（不经任何 xlsx）
      → 多 ndax 配方一致性检查（不一致=硬阻断，保留旧定案）
      → profile 可选校验：无 profile=一次性免责声明；有 profile=档位比较（专属弹窗，决定 4）
      → Phase A：并行逐文件内存分析（固定索引结果 + 槽位状态 + 异常收集）
      → 预检汇总弹窗（是否停止整批）→ 二次确认（决定 2）
      → 审计留痕（异常 + 用户决定）
      → Phase B：staging 落盘（Info_Image.csv 占位版 / Info_Plot.json / 日志 / Word/CSV 报告）
      → 成功后原子切换 {date}_v{ver}，失败则弃 staging、旧结果原样保留
      → visualizer 读占位语义
[旁路] 独立 NDAX→Excel 导出页（唯一保留的 Excel 逻辑，与分析链路完全解耦）
```

### 1.2 七个实施阶段（建议顺序，每阶段可独立验收）

| 阶段 | 内容 | 交付判据 |
|---|---|---|
| **P0 底线修复** | `filter_data` 空档位防御（`utils/processors/data_utils.py:48` `filtered_mask[0]=True` 对空数组越界；`main/visualization/data_loader.py` 的 `filter_data` 对空列表 `charge_single[0]` 越界）；结果合并错位复现测试（见 §1.3） | 空档位不再崩溃；错位测试先红后绿 |
| **P1 ndax 直读核心** | 新增 `ndax_data_source`（Step.xml 配方解析器 + `nda.read()` DataFrame 适配层）；`BatteryAnalysis` 输入从 xlsx 目录切为「(文件, cycle/step/record DataFrame) 序列」；`detect_pulse_rows`/`match_pulse_levels`/`ChargeCalculator` 不动（它们已按 DataFrame 工作） | 同一批数据 ndax 直读结果与旧 xlsx 链路逐槽位一致（黄金对照测试） |
| **P2 校验与预检框架** | 多 ndax 一致性硬阻断；profile 可选校验（免责声明/比较/阻断确认，决定 4）；完成性检查降为信息字段（决定 1）；异常收集模型 `AnomalyReport`；预检汇总弹窗 + 二次确认；审计记录器 | 三段交互顺序固定；任一确认点取消→零写入零删除 |
| **P3 空位数据模型** | 固定索引结果结构（§3）；Info_Image.csv 占位行协议 + 读取端补占位；Info_Plot.json 增 `channel_status`/`slot_status`/`completion_status`/`profile_validation`；图表/Word/CSV 显式缺失语义 | 缺档/坏通道端到端不错位、不伪造零值 |
| **P4 Excel 删减** | §4 边界清单执行；Word 报告去 Excel 依赖；版本号口径切 ndax 校验和 | 全仓 grep 无分析链路 xlsx 读写；导出页独立可用 |
| **P5 输出安全** | staging + 原子切换 + 旧结果备份策略（§5）；`write_info_json` 改 merge 写保护 `profile_validation` | 任意失败路径旧结果完好可读 |
| **P6 收尾** | i18n 文案、文档/roadmap 更新、`battery.pulseCurrents` 来源改为 Step.xml 配方（`data_loader._get_pulse_current_level` 消费端不变）、回归 | 测试矩阵全绿 |

### 1.3 必须先写出来的两个「错位」复现测试（P0 就绪）

代码证据表明现状有两处静默错位，正是用户「不可错位」要求的反面：

1. **文件级丢档**：`utils/processors/battery_analysis.py` Windows 路径下逐文件失败仅 `logging.error` 跳过，随后 `results = [r for r in results if r is not None]` **压缩列表**——第 3 个电池失败后，其结果块整体消失，后续电池顶替其下标。全批无脉冲时更直接丢整批（`"Pulse data not found"` 异常）。违反决定 2「不能静默丢通道」。
2. **槽位级丢档**：`main/visualization/data_loader.py::_process_csv_data` 中 `if float_data:` 对空行**跳过 append**——某电池某档位空位写成空行后，读取端该档位的曲线列表比电池名列表短，绘图按下标对位即错位。Info_Image.csv 写入端（`info_csv_writer.write_info_csv`）本来就是按 `1+3*C` 定长写行的，**坏的是读取端**。

---

## 2. 影响文件与调用链清单

### 2.1 主链路（必须改）

| 文件 | 现状职责 | 改造动作 |
|---|---|---|
| `utils/processors/battery_analysis.py` | 扫 xlsx、`read_xlsx_sheets`、并行逐文件、结果压缩合并 | 输入改 ndax/DataFrame；合并改为**保位**（`results_map.get(i)` 不过滤 None，None→缺失记录）；`extract_test_date_from_xls` 改从 `nda.read()` 的 Timestamp 取 |
| `utils/readers/xlsx_reader.py` | `read_xlsx_sheets`/`extract_test_date_from_xls` | 移除（功能由 ndax 适配层取代） |
| `utils/file_finder.py` | `scan_sorted_xlsx` | 移除，替换为 `scan_sorted_ndax`（自然排序=电池固定索引的基准） |
| `main/business_logic/data_processor.py` | 扫 xlsx、`excel_validator` 逐文件解析、首文件名解析档位写 `battery.pulseCurrents` | 重塑为 ndax 元信息识别；`_scan_excel_files_task`/`_process_excel_files_task`/excel 缓存删除；档位改由 Step.xml 提供 |
| `utils/file_validator.py` | `validate_input_directory` 强制 basename==`2_xlsx`（:176） | 改为「目录存在且含 .ndax」校验 |
| `main/managers/path_manager.py` | `set_input_path` 自动定位 `2_xlsx`（:183） | 改定位 ndax 目录 |
| `main/business_logic/version_manager.py` | 对输入目录全部 xlsx 算 SHA-256 得版本号（:61-75） | 校验源切 ndax 文件（**版本号口径变化，见分歧 6**） |
| `utils/writers/info_csv_writer.py` | `write_info_json` 整体覆写 | merge 写 + `profile_validation` 不可变保护 + 新增状态字段 |
| `main/visualization/data_loader.py` | 按全局 `battery.pulseCurrents` 解释列、空行压缩 | 补占位修复；缺失槽位显式标记；档位数以结果文件内声明为准（自描述化，消除全局配置错配） |
| `main/workers/analysis_worker.py` | 开头 `shutil.rmtree(version_dir)`（:100）与 rename 前 `shutil.rmtree(final_dir)`（:158） | 两处删除移除，改为 §5 staging 提交 |
| `utils/input_validator.py` / `main/business_logic/validation_feedback.py` | `test_profile` 在必填清单（`input_validator.py:73,129`） | 移出必填，保留可选校验 |
| `utils/processors/data_utils.py::filter_data` | 空列表越界 | P0 防御（循环头空判 `append([]) continue`，与旧裁决⑦一致） |

### 2.2 报告与可视化连带（Excel 删除波及）

| 文件 | 动作 |
|---|---|
| `utils/writers/excel_report_writer.py` / `excel_sample.py` / `excel_overview.py` / `excel_formats.py` / `excel_utils.py` | 删除 |
| `utils/report_coordinator.py` | 删 Excel 分支：`_build_document_paths` 的 `strSampleXlsxPath`/`strResultXlsxPath`、`write()` 中 `ExcelReportWriter` 调用（:581-586）；`compute_report_content_base` 裁掉 Excel 专用参数（保留 Word 半边） |
| `utils/file_writer.py`（`FileWriter`/`write_all`） | 去 Excel 输出 |
| `utils/writers/word_report_writer.py` / `word_front_matter.py` / `word_overview.py` | 保留，但：缺失槽位显式「缺失(原因)」、统计标注有效 n、**Word 内指向 result xlsx 的相对链接 `strRelResultPath`（`report_coordinator.py:173`）失去目标**（分歧 5） |
| `utils/writers/csv_writer.py` / `statistics_utils.py` | 保留；统计跳过缺失槽位（`nanmedian` 已天然支持，配合占位数据即可），禁止按 0 计入 |
| `utils/processors/excel_processor.py` / `main/business_logic/excel_validator.py` | 删除（仅服务 xlsx 输入校验） |

### 2.3 新增模块（建议）

- `utils/ndax_data_source.py`：`nda.read()` 封装 + Step.xml 定位与解析（配方档位、CC 电流、工步完成状态）+ 完成性信息提取（决定 1）。
- `utils/processors/anomaly_report.py`：异常条目模型（battery_index/档位/类型/证据/级别）+ 汇总渲染。
- `main/dialogs/preflight_dialogs.py`：预检汇总弹窗 + 二次确认弹窗（复用现有 `data_error_dialog`/`countdown_message_box` 风格）。
- `utils/audit_logger.py`：异常与用户决定的 append-only 留痕（见 §3.4 的落点问题）。

---

## 3. 异常预检汇总 + 两次确认 + 固定索引空位

### 3.1 交互时序（严格前置，全部发生在删除旧结果之前）

```
1. 无 profile？→ 一次性免责声明（QSettings validation/profile_disclaimer_version，已定）
2. 有 profile？→ 档位比较校验（决定 4 专属弹窗：同数异档=阻断+以ndax为准继续/默认中止；
   档数不一致=人工确认出口/默认中止；多 ndax 配方不一致=硬阻断无出口，保留旧定案）
3. 完成性检查（决定 1）：Step.xml 有明确完成状态→记 complete/incomplete；无字段→记 unknown。
   一律不阻断，仅作为预检汇总中的一条信息/告警行 + Info_Plot.json 留痕字段
4. Phase A 全批内存分析 → AnomalyReport（含全部异常，一次收齐）
5. 【弹窗一】异常预检汇总：逐条列出（电池/档位/异常类型/证据），问「是否停止整批？」
   - 停止 → 结束，零写入零删除，决定仍留痕
   - 继续 → 【弹窗二】二次明确确认：列出将保留空位的电池×档位清单与后果
     （图表留空位、报告标缺失、统计不含该槽位），默认焦点「中止」（与裁决①默认一致）
6. 确认 → 审计留痕 → Phase B 提交
```

异常分类（级别决定它在汇总里的呈现，不决定是否阻断——阻断权统一在两次确认）：

| 类型 | 来源（代码证据） | 级别 |
|---|---|---|
| `channel_error`：文件解析失败/记录损坏 | `battery_analysis._parallel_process_file` 现在抛 `BatteryAnalysisException` 后被静默跳过 | 警告（进确认） |
| `pulse_not_found`：某档位找不到脉冲 | `match_pulse_levels` 对该档返回空 posi 列表；或 `pulse_mask.sum()==0` 整电池无脉冲 | 警告（进确认） |
| `incomplete_hint`：Step.xml 明确显示未完成 | 决定 1：不硬阻断 | 信息/警告行（分歧 1） |
| `median_deviation`：实测中位数偏差 > max(1%, 0.5mA) | 旧裁决②黄色告警放行留痕 | **黄色告警，不进两次确认、不产生空位**，仅提示+留痕 |
| `file_unreadable`：ndax 无法打开 | nda.read 异常 | 警告（进确认，整电池空位） |

> 关键分界（用户点名要求分清）：**「找不到脉冲」= 结构性缺失**（该槽位没有数据，走空位+两次确认）；**「中位数偏差」= 质量性告警**（数据在，只是实测偏离设定，黄色放行留痕，槽位照常出数）。二者在 AnomalyReport 中类型、级别、后果三者都不同，绝不可合并成一条「异常」。

### 3.2 固定索引空位的数据模型

- **电池索引 b** = `scan_sorted_ndax` 自然排序（与现状 xlsx 排序语义一致）；文件失败/无脉冲**不删块**，块内状态置 `channel_failed` / `pulse_missing`，名称保留。
- **档位索引 c** = Step.xml 配方档位顺序（多 ndax 一致是运行前提，硬阻断保证全局唯一序）；电压档索引 v 同理。
- 结构：`results[b][c][v] = 数据 | None`，旁挂 `battery_status[b]`、`slot_status[b][c]`（`ok | pulse_not_found | channel_error | file_unreadable`）+ 原因文本。
- **禁止伪造零值**：缺失槽位一律 `None`/空占位，下游任何统计/绘图/报告不得将其当 0。

### 3.3 输出端的空位协议

- **Info_Image.csv**：每电池仍写固定 `1 + 3*C` 行；空位槽位**必须写出三行占位**（空行或显式 `MISSING` 标记，见分歧 3）。写入端已定长，读取端 `_process_csv_data` 必须「空行也 append 占位」，修掉 `if float_data:` 压缩 bug。
- **Info_Plot.json**：新增 `channel_status`、`slot_status`、`completion_status`、`analysis_anomalies`（异常+决定记录副本）、`profile_validation`（决定 5，policy_version `2026.10`）。
- **图表**：缺失槽位不画曲线、不画零值线；对应电池/档位位置保留（空图区+灰色「缺失」标注），图例与悬浮信息显式缺失语义。
- **Word/CSV 报告**：行列索引固定；缺失显示「缺失(原因)」；Mean/Median/Std 只基于有效槽位并标注 n；缺失不填 0、不参与分母。
- **P0 联动**：`filter_data`（两处实现）空输入防御——空槽位 `append([]) continue`，与占位协议解耦（旧裁决⑦不变）。

### 3.4 留痕的落点缺口（必须拍板，见分歧 4）

决定 2 要求「留下异常与用户决定记录」，决定 5 要求成功后写 `Info_Plot.json.profile_validation`。但若用户在确认点选择**停止**、或确认后分析失败，新结果目录根本不存在，记录写到哪？建议：**append-only 审计文件**（如 `3_analysis results/analysis_audit.jsonl`，不受单次运行目录生命周期影响）持久化全部异常+决定；成功落盘时再把本轮内容镜像进 `Info_Plot.json`。`profile_validation` 本身按「写入后不可被后续写入覆盖」实现为 merge 写保留（`write_info_json` 改为读-改-写，已有 `profile_validation` 键一律不覆盖）。

---

## 4. Excel 删改边界（仅保留独立 ndax→Excel 导出）

### 4.1 保留（导出子系统，切断与分析的一切耦合）

- `ndax/converter.py`（`convert_one`/`convert_batch`：`nda.read()`→xlsx，含超 104 万行拆表逻辑）。
- `ndax/worker.py`（导出后台任务）。
- `main/tabs/ndax_tab.py`（导出 UI）。**删改点**：`_find_and_fill_test_profile` 自动带出 analysis 页信息、`sigSetVersion.emit()` 触发版本计算（:216-217）属于导出→分析的反向耦合，应切断（导出页变成纯导出：选 ndax 目录→选输出目录→转换）。现有「2_xlsx 已存在将覆盖，是否继续」的覆盖确认保留并强化（xlsx 不再是分析输入，覆盖无数据风险，但保留确认防手误）。

### 4.2 移除（xlsx 中间层与 Excel 报告，明细见 §2.2）

xlsx 读取（`xlsx_reader.py`）、xlsx 输入校验（`excel_processor.py`/`excel_validator.py`/`validate_excel_filename`/`2_xlsx` 目录强制）、xlsx 扫描与文件名档位解析进主配置的路径（`data_processor` 对应部分）、xlsx 版本校验和（`version_manager`）、Excel 报告五件套（`excel_report_writer/excel_sample/excel_overview/excel_formats/excel_utils`）与 `report_coordinator`/`file_writer` 的 Excel 分支。

### 4.3 边界连带（不重开决定，仅提示实施时必须处理）

- **旧裁决⑥与新决定 3 直接冲突**（见冲突 C2）：旧定案的「按需导出 xlsx 落 3_analysis results/{date}_v{ver}/（复用降级按钮/复选框）」被新决定覆盖——分析结果目录**不再**提供按需 xlsx 导出复选框，该降级按钮/复选框 UI 一并移除，导出统一走独立导出页。
- Word 报告对 result xlsx 的超链接目标消失（分歧 5）。
- `filename_parser.extract_pulse_current`（文件名解析档位）失去主链路地位：档位以 Step.xml 为准（旧定案「档位以 ndax 为准」+新决定 3）。建议保留为**预检告警级交叉校验**（文件名档位与配方不一致→黄色提示），不进主配置；`data_processor._verify_pulse_currents` 的「文件名 vs 查表」双重验证随之简化或删除。

---

## 5. 输出不覆盖旧结果的安全机制

1. **一切校验与确认前置**：profile 校验、预检汇总、二次确认全部发生在任何删除/写入之前（决定 5）。
2. **删除 `analysis_worker.py` 现有两处 `shutil.rmtree`**（开头删 `v{ver}`、rename 前删 final）——这是现状唯一的数据丢失窗口：分析在删除后失败，旧结果已被毁。
3. **staging 提交**：确认通过后写入同盘临时目录 `3_analysis results/.staging_{date}_{ver}_{uuid}`（同盘保证 rename 原子性；不用 OS 临时目录，沿旧裁决⑥精神）。
4. **原子切换**：staging 全部写完（Info_Image.csv、Info_Plot.json、日志、Word/CSV 报告）并自检通过后：
   - final 不存在 → 直接 rename；
   - final 已存在 → **改名为 `backup_{timestamp}`**（而非删除），rename staging→final 成功后再按保留策略清理（建议保留最近 1–2 代备份，超期自动清）；
   - 任一步失败/用户取消 → 弃 staging（可留作调试 dump），backup 改名还原，旧结果零损伤。
5. **merge 写保护**：`write_info_json` 读-改-写，`profile_validation` 一经写入不可覆盖（决定 5）；审计记录独立 append-only（§3.4）。
6. **磁盘空间预检**：staging 需要双份空间（若走备份改名），空间不足作为一条预检汇总告警行前置提示。

---

## 6. 测试矩阵（最小可验证集）

| # | 场景 | 层 | 期望 |
|---|---|---|---|
| T1 | `filter_data` 空档位/单点输入（两处实现） | 单元 | 返回 `([],[])` 不抛 IndexError |
| T2 | `match_pulse_levels` 某档位零匹配 | 单元 | 该档空列表、其余档不受影响 |
| T3 | 结果合并：第 i 个文件失败 | 单元 | `results[i]` 为缺失记录，后续索引不移位（§1.3 复现测试） |
| T4 | Info_Image.csv 空位 round-trip | 单元 | 写空位→读回每档位条数==电池数，占位对位 |
| T5 | `write_info_json` merge：预置 `profile_validation` 后再写 | 单元 | 原留痕逐字节保留 |
| T6 | profile 校验分支：无 profile/同数同值/同数异档/档数不一致/多 ndax 不一致 | 单元 | 免责一次/通过/阻断+按钮默认中止/确认出口默认中止/硬阻断 |
| T7 | 完成性三态：complete/incomplete/unknown | 单元 | 三态均放行且留痕字段正确（决定 1） |
| T8 | 预检汇总→停止整批 | 集成(UI mock) | 零写入零删除，审计有记录 |
| T9 | 预检汇总→继续→二次确认→中止 | 集成 | 同 T8 |
| T10 | 预检汇总→继续→二次确认→确认 | 集成 | 空位保留、索引固定、审计含两次决定 |
| T11 | 坏通道+缺档混合批端到端 | 集成 | 图/Word/CSV 三处缺失语义一致、统计 n 正确、无零值伪造 |
| T12 | 分析中途异常（写盘失败/取消） | 集成 | staging 弃置、backup 还原、旧结果完好可读 |
| T13 | ndax 直读 vs 旧 xlsx 链路黄金对照 | 集成 | 逐槽位 posi/charge/voltage 一致（P1 验收） |
| T14 | Excel 导出页独立运行（不触分析页状态） | UI | 转换成功、覆盖确认保留、`sigSetVersion` 不再触发 |
| T15 | test_profile 留空启动分析 | UI | 通过校验、免责声明仅一次（QSettings 版本门槛） |
| T16 | Windows ProcessPool 路径 + 大文件（>104 万行拆表导出回归） | 性能/回归 | 内存不随批数线性涨（逐文件流式）、导出拆表仍正确 |
| T17 | `battery.pulseCurrents` 改由 Step.xml 写入后 visualizer 列解释 | 回归 | 图例/档位标签与配方一致 |

---

## 7. 需用户拍板的分歧（按紧急度排序）

1. **Step.xml 明确显示「未完成」时的处置级别**：决定 1 说不硬阻断，但未说是否进两次确认。建议：作为预检汇总中的一条**警告行**随两次确认处理，不单独弹框、不单独阻断。请确认。
2. **中位数偏差的基准与适用范围**（冲突 C3）：实测中位数与什么比——ndax 配方设定值（推荐，无 profile 也能跑）还是 profile 值？无 profile 时是否照常执行该黄色告警？
3. **Info_Image.csv 空位表示法**：(a) 保留空行+读取端补占位（改动最小）；(b) 显式 `MISSING` 标记（自描述、防旧读取端误读）；(c) 借机换 JSON/Parquet 结果格式（一劳永逸但波及独立 BatteryChartViewer 兼容）。建议 (b) 并在 Info_Plot.json 记 `format_version`，visualizer 双版本兼容。**注意任何选择都要求读取端同步改**，否则错位 bug 仍在。
4. **`profile_validation` 留痕结构**：单对象（首写即冻结）还是 `validation_runs[]` 追加列表（同目录多次运行各留一条）？「不能被后续写入覆盖」语义上更贴追加列表；另请确认 §3.4 的独立审计文件落点方案（用户选「停止」时的记录去处）。
5. **Word 报告中 result xlsx 链接的替代物**：删除链接 / 改指 CSV / 改指 Info_Plot.json？
6. **版本号口径切换确认**：版本号从「输入目录 xlsx 校验和」切「ndax 校验和」后，同一份数据的版本号会跳变（旧 `{date}_v{ver}` 目录不会被误删，属安全方向），是否接受？
7. **输入目录约定**：`validate_input_directory` 的 `2_xlsx` 强制改为什么规则——「目录含 .ndax 即可」还是约定新目录名（如 `1_ndax`）？`path_manager.set_input_path` 自动定位同步改。
8. **导出页与分析页的联动切断**（§4.1）：`_find_and_fill_test_profile` 自动带出是否一并移除（我建议移除，入口唯一化：分析入口=选 ndax 目录）。
9. **两次确认弹窗的默认按钮与文案**：建议默认「停止/中止」（安全默认，与裁决①一致），二次确认列出空位清单逐条可见。
10. **ndax 解析失败的坏文件**在预检里记 `channel_error`（无法预检脉冲，只能标整电池空位）——是否接受其与「缺档」在报告中使用不同的缺失原因文案。

## 8. 决策间冲突与旧定案的修订需求（如实列出，不重开）

- **C1（新决定覆盖旧裁决④）**：旧裁决④用 Step.xml 工步完成状态仲裁「档数不一致」（`level_count_mismatch_complete`/`truncated`/`missing_evidence` 三型，缺失=硬阻断）。新决定 1+4 明确：完成状态不再硬阻断、档数不一致走人工确认出口、不用不可验证的完成状态判断。**裁决④的仲裁分支整体作废**，mismatch_type 只保留档值类与档数类；`level_count_mismatch_truncated`/`level_count_missing_evidence` 两型不再产生。实施时按新决定，但请用户确认这份「作废清单」以免实现者按旧文档返工。
- **C2（新决定覆盖旧裁决⑥部分）**：旧裁决⑥「按需导出 xlsx 落结果目录（降级按钮/复选框）」与新决定 3「Excel 只存在于独立导出功能」冲突，新决定优先：结果目录无 xlsx、降级复选框移除（§4.3）。旧裁决⑥「内存 DataFrame 直传」的其余部分与新决定一致，继续有效。
- **C3（裁决②需补定义）**：黄色告警的偏差基准未定，见分歧 2；且必须与「找不到脉冲」分型分层（§3.1 表），否则实现时极易把两者混成一类「异常」而误走两次确认。
- **C4（决定 2/5 与现状删除时机的冲突）**：现 `analysis_worker` 先删后算，与「确认在删除前」直接冲突，必须按 §5 拆除两处 rmtree——这不是可选项，是决定 2/5 的前置条件。
- **C5（决定 5 与 `write_info_json` 整体覆写的冲突）**：merge 写 + 不可变键保护是「留痕不被覆盖」的唯一实现路径（§3.4）。
- **一致性提示（非冲突）**：决定 1「无字段默认放行」与旧定案「无 profile 一次性免责声明」同属「缺证据时放行但留痕」哲学，与旧裁决④「无证据=不可放行」相反——C1 修订后全仓口径统一为前者，建议在 policy_version `2026.10` 的说明文档里明写这条原则迁移，避免后续实现回潮。

---

## 9. 一句话收束

以「先算不写、两段提交」为主轴：P0 先修两处错位/越界底线 → ndax 直读核心 → 预检汇总两次确认 → 固定索引空位语义贯穿图/报告/JSON → Excel 收缩为独立导出页 → staging 原子切换保旧结果；待用户对 §7 十项与 §8 作废清单拍板后即可拆分为可验收的实现工单。
