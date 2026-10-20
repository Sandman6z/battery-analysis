# DeepSeek (Round 3): Round 3：报告写入路径、半成品所有权与成功门槛的实证收敛（含整体分阶段方案与测试矩阵）

# DeepSeek (Round 3)：报告写入路径、半成品所有权与成功门槛——整体分阶段方案的最终收敛

> 立场：只讨论不改码（用户 0010 明确"会议顾问仍只写方案"）。用户裁决（0005/0009/0010 及主持人释义）为最高约束，一律不重开。本轮聚焦指派重点：**报告写入路径、半成品所有权、成功条件**，并按要求核实一次读取内存论据、检查实际调用链/大小写 V/v/写入器独立拼目录/信号无条件递增四类风险。GLM Round 2 无有效条目，不为其编造观点。以下所有代码证据均为本轮独立复查（行级引用）；`src/` 为实际包根（黑板旧条目里的 `utils/...`、`main/...` 均位于 `src/battery_analysis/` 下，行号以本轮复查为准）。

---

## 0. 被约束钉死的裁决（不再讨论）

1. 报告全保留：Excel（Result+Sample 双工作簿）/Word/CSV/JSON/图像一个不减；Excel 仅退出**分析输入与中间链**（`xlsx_reader`、`excel_validator`、`excel_processor`、`scan_sorted_xlsx`、`file_validator` 的 `2_xlsx` 强制、`data_processor` 文件名档位解析链）。报告内容可增缺失标注，不删类型、不改命名。
2. 交互时序：profile 不一致在**点击分析前**确认；实测档位/通道数据异常在**点击分析后**汇总、两次确认。
3. 一次读取优先（本轮核实内存论据，见 §4）。
4. 版本体系：沿用 SHA256.csv 主/次版本递增；删除 `analysis_worker.py` 两处"同名即 rmtree"；**不加 `_r2` 等新后缀体系**；遇同名目标**安全拒绝**而非覆盖。
5. 成功门槛：**只有全部报告成功产出才递增次版本**；失败/取消仅清理**本次运行独占创建**的半成品，旧目录/旧报告绝不动。

---

## 1. 【重点一】报告写入路径全景——已证实的代码事实

### 1.1 写盘段实际调用链（逐环核实）

```
analysis_runner.check_and_start_analysis (managers/analysis_runner.py:174-186)
  → main_controller.start_analysis → thread_pool.start(AnalysisWorker)  (controllers/main_controller.py:82-93)
    → AnalysisWorker.run (workers/analysis_worker.py:80-)
        ① os.makedirs(output)；建 version_dir = output/v{listTestInfo[16]}（小写 v，:112-117）
        ② BatteryAnalysis(...) (utils/processors/battery_analysis.py:50-116)
             → run() 并行逐文件分析 → UBA_WriteCsv(f"{strResultPath}/V{listTestInfo[16]}")（大写 V，:263）
                 → write_info_csv / write_info_json (utils/writers/info_csv_writer.py) —— Info_Image.csv、Info_Plot.json
             → 日志 txt 也拼 f"{strResultPath}/V{listTestInfo[16]}/..."（大写 V，:88）
        ③ test_date → str_test_date = parse_test_date(test_date, original_cycle, fallback=时间戳) (analysis_worker.py:150-158)
        ④ os.rename(version_dir → output/{str_test_date}_v{ver})（:173-186；rename 前已先 rmtree final_dir）
        ⑤ file_writer.FileWriter → write_all → ReportCoordinator.write() (utils/file_writer.py:7-51)
             → 绘图 png/svg → ExcelReportWriter（Result+Sample xlsx）→ WordReportWriter（docx）→ CsvWriter
        ⑥ JsonWriter（{...}.json，utils/json_writer.py）
```

### 1.2 交付物落点清单（与"半成品"直接相关）

| 产物 | 落点 | 证据 |
|---|---|---|
| Info_Image.csv / Info_Plot.json | `output/V{ver}/`（rename 后随目录成为 `{td}_v{ver}/`） | battery_analysis.py:263 → info_csv_writer.py:31-37/:78-93 |
| 分析日志 txt | 同上（`V{ver}/` 内） | battery_analysis.py:88,505-512 |
| 图像 png/svg | `{td}_v{ver}/` | report_coordinator.py:423-436 |
| Result xlsx / Sample xlsx | `{td}_v{ver}/` | report_coordinator.py:447-454、excel_report_writer.py:72-76 |
| CSV 报告 | `{td}_v{ver}/` | csv_writer.py:46 |
| **Word docx** | **输出根目录 `3_analysis results/`，不在版本目录内** | report_coordinator.py:483-489、word_report_writer.py:123-128：`result_dir = Path(self.strResultPath).parent` |
| JsonWriter 的 `{...}.json` | 自拼的 `{td_json}_v{ver}/` | json_writer.py:22-24,93 |

### 1.3 风险实证 A：三处独立的 td（测试日期）派生 + 独立拼目录 + 自建目录

同一份 `{td}_v{ver}` 目录名被**三个模块各自重新计算、各自 `os.makedirs`**：

1. **worker**：`parse_test_date(test_date, original_cycle_date, fallback=list_battery_info[2][0])`（analysis_worker.py:150-158,173）——fallback 链第 3 级是**时间戳字符串**；
2. **ReportCoordinator**：`_extract_test_date()` 调 `parse_test_date(test_date, original_cycle)`（**无 fallback 参数**）→ 失败再从**电池名数字**提 8 位（report_coordinator.py:348-377）→ 再失败 "00000000"；随后 `os.path.join(strResultPath, f"{td}_v{listTestInfo[16]}")` + `os.makedirs(exist_ok=True)`（:325-326）；
3. **JsonWriter**：`listBatteryInfo[2][0].split(" ")[0].split("-")` 直接切字符串，仅捕 ValueError，失败即 "00000000"（json_writer.py:22-24），且 :93 再 `makedirs`。

三条 fallback 链语义互不相同。**一旦标准日期解析失败**（这恰是异常放行场景的常态边缘），worker 把 `v{ver}` rename 成 `{时间戳日期}_v{ver}`，ReportCoordinator 却另建 `{电池名日期或00000000}_v{ver}` 并把**全部报告**写进去，JsonWriter 再建第三个目录写 JSON——一次运行产出 2~3 个"半成品目录"，且哪个都算"本次独占创建"，清理与所有权全部失明。rename 失败时 worker 还会 `final_dir = version_dir` 继续执行（analysis_worker.py:183-186），同样触发分裂。**这是"报告写入器独立拼目录"的最坏后果，不是理论风险。**

另注：`word_report_writer._init_report_paths` 与 `excel_report_writer` 的 docx 名是从**目录 basename split("_v")[0]** 反推 td（word_report_writer.py:69-73、excel_report_writer.py:81-88），与 coordinator 的 `strReportWordPath`（解析式 td）是两套算法；通常因目录名由 coordinator 拼出而巧合一致，但若目录名来自 worker rename（td 不同）或 basename 含 "_v"，Excel/Word 里的 docx 超链接与实际写出的 docx 文件名会不一致。

### 1.4 风险实证 B：大小写 V/v

- worker 创建并 rename 的是**小写** `v{ver}`（analysis_worker.py:112,173）；
- BatteryAnalysis 写 Info CSV/JSON 与日志的是**大写** `V{ver}`（battery_analysis.py:88,263；info_csv_writer 的 `os.makedirs` 会把它建出来）。

Windows 大小写不敏感 → 碰巧同目录、碰巧正确；**macOS/Linux（大小写敏感 FS）上这是两个目录**：rename 只搬走 `v{ver}`，`V{ver}`（含 Info_Image.csv/Info_Plot.json/日志）滞留原地，报告目录里没有 Info 文件，图表工具读不到数据。当前代码事实上是"Windows-only 正确"，跨平台声明与实现不符。

### 1.5 风险实证 C：docx 落输出根且同名静默覆盖

docx 由 python-docx `save()` 直接写 `3_analysis results/{manuf}_{model}_DC{batch}_TD{td}_v{ver}.docx`（输出根）。同名文件存在时**无检查、无确认、直接覆盖**——它在版本目录之外，任何"保护版本目录"的方案都罩不住它；"旧报告绝不动"必须把它显式纳入碰撞检查与所有权清单。`report_manager.py:66` 用 `f"_v{version}" in docx_file.name` 子串匹配定位 docx（命名规则不能破坏的又一实证）。

---

## 2. 【重点二】半成品所有权——RunManifest 白名单方案

### 2.1 "本次运行独占创建"的完整清单（多位置，必须登记而非猜测）

一次运行会触碰的路径（全部已证实）：
1. `output/v{ver}/`（运行中目录，analysis_worker.py:112-117）；
2. `output/V{ver}/`（大写，Info/日志落点，battery_analysis.py:88,263）；
3. `output/{td}_v{ver}/`（rename 目标 + coordinator/json_writer 的 makedirs 目标）；
4. `output/{manuf}_{model}_DC{batch}_TD{td}_v{ver}.docx`（输出根 docx）；
5. `output/SHA256_temp.csv`（set_version 写盘瞬间的临时文件，version_manager.py:301-319）；
6. 副作用：`rename_path` 信号 → `config_manager.rename_pltPath`（signal_connector.py:80-81）把配置里的图表路径改指向新目录——失败清理后该配置指向已删路径，需随清理回滚或失效化（analysis_worker.py:165-171 且注意 **rename_path 在 `os.rename` 之前发出**，rename 失败时配置已改）。

### 2.2 RunManifest（数据结构，占位契约的一部分）

```python
# 落点：output/.run_manifest_{run_id}.json（run_id = uuid4），运行开始即创建，append 更新
RunManifest = {
  "run_id": str,
  "version_snapshot": "1.1",          # Run 时刻 UI 版本（listTestInfo[16] 快照）
  "checksum_run": str,                 # analysis_runner.py:182 的 sha256_checksum_run 快照
  "phase": "created|analyzing|confirmed|writing|committing|committed|failed|cancelled",
  "owned_paths": [                     # 只增；每创建一个文件/目录立即登记
      {"path": "...", "kind": "dir|file", "created_at": iso, "state": "created|finalized"}
  ],
  "created_at": iso, "finished_at": iso, "outcome": None | "success" | "failed" | "cancelled"
}
```

**清理规则（失败/取消时）**：
- 只删 `owned_paths` 白名单内且 `state=="created"` 的路径；逐条删除、逐条记日志；**禁止宽 glob**（不得复用 `file_service.py:121` 的通用 rmtree 删除服务——它是用户主动删除设施）；
- 任何未登记路径一律不碰（"旧目录绝不动"的操作化定义）；
- 清理失败（文件被占用等）→ 不重试破坏性动作，把残留写进 manifest 的 `leftovers[]` 并在状态栏提示人工处理；
- 成功时 manifest 标记 `committed`，保留（供审计/追踪），不删。

### 2.3 同名安全拒绝（沿裁决，无 `_r2`）

- **运行前**（点击 Run 时，td 未知）：`v{ver}` 已存在 → 安全拒绝启动（弹提示说明"存在同版本目录，疑为上次未清理残留，请人工确认后删除"），不 rmtree、不改名、不加后缀；
- **写盘/提交前**（td 已知）：`{td}_v{ver}`、`V{ver}`、docx 同名 任一存在 → 拒绝提交，清理本次已登记半成品后退出；
- 拒绝提示与清理日志都引用 run_id，方便用户甄别残留归属。

---

## 3. 【重点三】成功条件与版本递增——信号无条件递增的实证与最小修法

### 3.1 实证链（四环，全部已证实）

1. `analysis_worker.py:277-282`：`finally` 中 **thread_end 无条件 emit**（注释原文："thread_end 必须无条件发射：_on_analysis_completed 依赖它来重置 is_analysis_running"）——失败/取消同样发；
2. `main_controller.py:88` `thread_end → _on_analysis_completed`；`:137-144` `_on_analysis_completed` **无条件** `analysis_completed.emit()`；
3. `signal_connector.py:76` `analysis_completed → version_manager.set_version`（同时 :78 挂 `_reset_run_button`）；
4. `version_manager.set_version()`（:221-327）把 `sha256_checksum_run` 对应的 `times[c] += 1` 并写回 SHA256.csv、更新 UI 版本。

→ **失败/取消也递增次版本**，违反用户裁决"只有全部报告成功才递增"。这是"信号无条件递增"的完整闭环。

### 3.2 预登记 vs 计次（0010 点名区分）

- `get_version → _on_checksum_ready`（version_manager.py:145-190 + `_compute_version_number` :118-143）：**新校验和会 append 进 SHA256.csv（times="0"）**——这是**预登记**，决定主版本号（major = index+1），不是计次；同校验和只读取当前 times；
- `set_version`：唯一**计次点**（times+1 = 次版本）；
- 版本号语义：`v = f"{major}.{times}"`，即目录名里的版本 = **此前成功次数**，成功后 +1 供下次使用（与 0009 主持人核查一致）；
- `analysis_runner.py:182` `sha256_checksum_run = sha256_checksum` 是 Run 时刻快照；代码注释（version_manager.py:156-160）自认"异步 checksum 未就绪时点 Run，快照可能为空/旧值"——竞态已知，纳入测试矩阵 S8。

### 3.3 成功门槛（唯一递增条件）

```
success := 未取消 ∧ 无未处理异常
         ∧ UFW_GetErrorLog()==""（write_all 整链无异常，file_writer.py:42-51）
         ∧ 交付物全数存在且非空：Info_Image.csv、Info_Plot.json、日志 txt、
           全部 png/svg、Result xlsx、Sample xlsx、CSV 报告、JsonWriter 的 json、docx
         ∧ manifest.phase == "committing" 走完
```

即"全部报告成功产出"操作化为**交付物清单逐项校验**，而非仅看异常串（现状 `str_error_xlsx` 只反映 write_all 抛出的异常，Excel 写完 Word 抛错时已写出的 Excel 会留在目录里成半成品——恰是必须逐项校验的原因）。

### 3.4 信号拆分（最小修法，不动 UI 复位语义）

- **thread_end 保持无条件发射**（UI 复位依赖它，不破坏）；
- 把 `version_manager.set_version` 从 `analysis_completed` 上摘下，改挂**新信号 `analysis_succeeded`**——仅在 success==True 时由 controller 发射；`_reset_run_button` 仍挂 `analysis_completed`；
- 失败/取消：不调 set_version、UI 版本与 SHA256.csv 保持上一版（预登记行保留不动——它是登记不是计次）、状态栏提示"本次未成功，版本不递增"；
- 该改法只动 signal_connector 的一处 connect + controller 增一个信号，版本递增逻辑本体（SHA256.csv 规则）零改动，符合"沿用现有递增机制"。

### 3.5 现状两处 rmtree 的处置（按裁决）

- `analysis_worker.py:113-114`（`v{ver}` 存在即删）与 `:174-175`（`{td}_v{ver}` 存在即删）**删除**，替换为 §2.3 的安全拒绝；`os.mkdir(version_dir)` 前先登记 manifest。

---

## 4. 一次读取内存论据核实（用户点名，修正并给出边界）

**核实结论：GPT Round 2 的论证成立，我 Round 2 撤回"两遍预检"的立场维持，但需补三条精确边界。**

- **峰值内存与读几遍无关（论据核实为真）**：并行结构是 ProcessPool（Windows 分支 `ProcessPoolExecutor(max_workers=ResourceManager.get_optimal_process_count()，默认上限 8)`，battery_analysis.py:157-160；非 Windows 分支 `multiprocessing.Pool(min(cpu,4)).map`，:205-210），DataFrame 只在子进程 `_parallel_process_file` 内物化，回传主进程的仅是 6 元组派生结果（:281-293）。峰值 = `min(并行度, 文件数) × 单文件 DataFrame`。两遍方案的"预检遍"同样要在子进程物化同样大的 DataFrame——**所谓"两遍更省内存"不成立**；差别只是一遍付 1× 解析时间、两遍付 2×。
- **量级（估算，非实测）**：converter 的"Record 超 104 万行拆表"逻辑（ndax/converter.py）反证单文件可达百万行级；按分析所需 8 个数值列 × 8B × 1M 行 ≈ 64MB 纯数据，pandas 物化 + 中间拷贝按 2–4× 估 **150–400MB/文件**；8 worker 满并发峰值 ≈ 1.2–3.2GB。该数字是估算（假设 H3），须真实样本校准，但**它对一次/两遍读取同样成立**，不改变结论。
- **"一次读取"的正确形态（必须钉死，否则内存论据会被做坏）**：逐文件"读→列投影（只取 Cycle/Step/Status/Current(mA)/Voltage/Charge_Capacity/Discharge_Capacity/Timestamp）→派生→**立即丢弃 DataFrame**→回传派生结果"。**严禁**"缓存全批 DataFrame 等确认"（那是被否决的变体，峰值不可控）。确认前主进程持有的只是派生结果：B×C×V 脉冲段浮点列表，百电池×5 档×4 电压档×每段数百点 ≈ 数 MB~几十 MB，用户把确认框晾多久都无压力。
- **残余边界**：① 单文件投影后仍超单 worker 内存（>百万行级）——与读取次数无关，列投影缓解，未来分块解析；② 两遍读取唯一合理的场景是"预检远轻于正式计算"——现预检主体（脉冲检测/匹配）就是分析大头，不成立。

---

## 5. 数据结构与占位契约（汇总定稿，沿 Round 2 收敛 + RunManifest）

1. **内存模型**：`results[b][c][v] = 数值列表 | None`，旁挂 `battery_status[b]`、`slot_status[b][c] = OK|MISSING_PULSE|CHANNEL_FAILED|FILE_FAILED`；I1 维度恒定 B×C×V、I2 序号稳定（废除 `results = [r for r in results if r is not None]` 压缩，battery_analysis.py:195-198，改 None→占位 BatteryResult）、I3 档位以配方为源全程只读、I4 禁 0 哨兵（`pulse_matcher.py:30-31` 初值 `0` 与合法行号 0 不可分 → 改 `None`，`ChargeCalculator` 遇 None 返 None）、I5 留痕只增不减。
2. **Info_Image.csv**：**结构零改动**——每电池 `1+3*C` 行定长，缺失槽位三行写空行（`info_csv_writer.write_info_csv` 现状即如此，:33-37）；不插行、不写文本 token（`data_loader` 按 `index % intPerBatteryRows` 取模定位，插行/token 都会错位或退化为跳过）。**唯一必改在读端**：`data_loader.py:325` `if float_data:` 空行跳过 append → 改为补 `None` 占位，恒保 `len(listPlt[c]) == B`。
3. **Info_Plot.json**：增 `format_version`、`slot_status`、`channel_status`、`profile_validation`（policy_version "2026.10"）、`analysis_anomalies`（异常清单 hash + 用户决定）；`write_info_json`（info_csv_writer.py:89-93 现为整体 `json.dump` 覆写）改 read-merge-write，上述键只增不减。
4. **AnomalyReport**：单一冻结对象（battery_idx、档位、类型、证据、级别），弹窗①/②、run_journal.jsonl、Info_Plot.json/报告缺失汇总四处**渲染消费**不重算；弹窗①展示的清单即最终清单（hash 入 journal），确认后冒出新异常必须重走两弹。决策层（结构性缺失，进两弹产生空位）与提示层（中位数偏差黄色告警、完成性 unknown——不进两弹不产生空位）分区呈现、分开计数。
5. **RunManifest**：见 §2.2，是半成品所有权与清理的唯一依据。
6. **路径解析单点化（PathResolver）**：`{td}_v{ver}` 目录名、docx 名、`V/v` 前缀**只允许解析一次**，由 worker 计算后参数下发给 BatteryAnalysis/ReportCoordinator/JsonWriter/各 writer；写入器禁止自拼目录名、禁止各自 makedirs 别处（消灭 §1.3/§1.4）。td 派生收敛为一个函数（固定 fallback 链：标准日期→时间戳→电池名数字→"00000000"，三处消费者同一条链）。验收 = 全仓 grep 只剩一处 `f"{td}_v{...}"` 拼名、一处 "V{ver}/v{ver}" 前缀（且统一小写）。

---

## 6. GUI 线程边界（硬红线）

- **事实**：AnalysisWorker 是 QRunnable，跑在 QThreadPool（main_controller.py:93 `thread_pool.start`）；`run()` 全程非 GUI 线程；现有 worker 里没有任何 QMessageBox——这条纪律目前靠"还没做"维持。
- **规则**：
  1. profile 不一致确认在点击前的主线程阶段做（天然安全）；数据异常两弹由 worker 发信号→**主线程构造 QDialog**→结果经 `threading.Event`/信号回传，worker 阻塞等待且可取消；**超时/取消/信号对象销毁一律按「停止整批」**。
  2. 弹窗①②默认按钮「停止」；两弹都必须在 GUI 线程（pytest-qt 断言为验收项）。
  3. SHA256.csv 读写、UI 版本显示保持主线程（现状如此）；manifest 登记/清理在 worker 内做，但只按白名单。
  4. 任何"在 worker 流程里内联 QMessageBox"的实现（Round 2 已点名 MiniMax §6.2 / GLM §5-3 形态）一律禁用。

---

## 7. 整体分阶段方案（每阶段独立验收、可回滚；旧链路删除放最后）

| 阶段 | 内容 | 验收判据 |
|---|---|---|
| **P0 底线修复**（独立先行） | `filter_data` 两处空防御（data_utils + data_loader 同根因）；`pulse_matcher` 0 哨兵→None；`results` 压缩改保位 | 空档/单点/坏文件输入不崩不错位、不产伪造值 |
| **P1 路径统一（本方案地基）** | PathResolver 单点：td 派生唯一化（含 fallback 链统一）、V/v 统一小写、`{td}_v{ver}` 只解析一次下发全部写入器；docx 落点纳入统一清单 | 全仓 grep 单一拼名；构造 td 解析失败用例三处同目录；大小写敏感 FS 断言单目录 |
| **P2 所有权与输出安全** | 删两处 rmtree；RunManifest；同名安全拒绝（运行前查 `v{ver}`、提交前查 `{td}_v{ver}`/docx）；失败/取消白名单清理 | 故障注入矩阵 C1-C6 全绿 |
| **P3 成功门槛** | 交付物逐项校验；`analysis_succeeded` 新信号挂 set_version（thread_end 保持无条件仅 UI 复位）；预登记/计次语义测试 | 矩阵 S1-S8 全绿 |
| **P4 ndax 直读** | `NdaDataset` 适配层（复用 converter 拆表逻辑，禁止两份实现）+ 列投影 + 逐文件流式；输入链 xlsx 退出（xlsx_reader/scan_sorted_xlsx/excel_validator/excel_processor/2_xlsx 强制/文件名档位解析）；**报告 Excel 链一根手指都不动** | parity golden：同 fixture 直读 vs 现链路逐槽位一致；分析链 grep 无 xlsx 读取；报告链测试全保留 |
| **P5 点击后异常汇总** | 一次读取→AnomalyReport 冻结→两弹（主线程）→留痕（run_journal.jsonl 先行 + Info_Plot.json merge 写） | 两弹顺序/默认按钮/停止零写入/journal 有记录 |
| **P6 占位契约贯通** | 读端补位、slot_status、图表/Word/Excel/CSV 缺失标注（N/A（原因），不写 0、不进分母、标注 valid_n）、profile 点击前确认流程 | 空位往返不错位；三端缺失语义一致 |

依赖：P0 独立；P1→P2→P3 串行；P4 依赖 P1（路径单点）；P5/P6 依赖 P3/P4。任一阶段失败不影响旧链路。

---

## 8. 成功门槛 / 失败清理测试矩阵（重点交付；其余增量附后）

### 8.1 成功门槛（S 组）

| # | 场景 | 期望 |
|---|---|---|
| S1 | 全部报告成功 | times+1、UI 版本+1、`{td}_v{ver}` 全交付物齐、manifest=committed |
| S2 | Word 写失败（mock 模板缺失） | 判失败、**不递增**、本次半成品全清、旧目录/旧 docx 逐字节完好 |
| S3 | Excel 成功但 CSV 失败 | 同 S2（部分产物也在 manifest 内被清） |
| S4 | JsonWriter 失败（mock json.dump 抛 OSError） | 同 S2 |
| S5 | 取消（确认前/两弹间/写盘中） | 不递增、白名单清理、旧目录不动 |
| S6 | 硬崩溃注入（kill 进程） | 残留 manifest+半成品；同版本重试→**安全拒绝**并提示归属 run_id；人工清理后可跑（已知限制） |
| S7 | 失败/取消跑完 | thread_end 仍发（UI 复位）、set_version **不被触发**（信号拆分回归） |
| S8 | get_version 新校验和预登记(times=0)、失败不计次、成功计次、checksum 异步未就绪点 Run 的快照竞态 | 预登记与计次语义不混、不误计 |

### 8.2 失败清理与所有权（C 组）

| # | 场景 | 期望 |
|---|---|---|
| C1 | 预置旧 `v1.0`/`{td}_v1.0`/旧 docx/输出根其它文件，本次失败 | 清理后旧物逐字节完好、其它文件完好（禁宽 glob） |
| C2 | 同名碰撞（`v{ver}` 或 `{td}_v{ver}` 或 docx 同名） | 运行前/提交前安全拒绝、零写入、不 rmtree 不改名 |
| C3 | 大小写敏感 FS（或 mock os）跑全链 | 只存在一个版本目录，Info 文件与报告同目录 |
| C4 | td 解析失败用例 | worker/coordinator/json_writer 产出同一目录（PathResolver 单点） |
| C5 | docx 根目录产物 | 失败时本次 docx 半成品被清、同名旧 docx 不被写不被清 |
| C6 | rename 失败注入（目标占用） | 按安全拒绝退出、manifest 如实记录、无分裂目录 |

### 8.3 其余增量（沿 Round 2 矩阵不重复，仅补新增项）

- 两弹线程断言（pytest-qt：弹窗均在 GUI 线程、worker Event 等待可取消、超时=停止整批）；
- AnomalyReport 冻结：确认后注入新异常 → 必须重走两弹；
- 报告链回归：Excel 双工作簿/Word/CSV/JSON/图表一个不少、缺格 N/A（原因）、统计 valid_n/missing_n 分离；
- parity golden（P4 验收）+ 架构守卫（分析链 grep 无 `read_xlsx_sheets/scan_sorted_xlsx/2_xlsx` 强制；**报告链测试全保留**，每个被删测试须注明守的是输入链还是报告链）。

---

## 9. 已证实代码事实 vs 未证实假设（按要求严格区分）

**已证实（行级证据，见前文引用）**：两处 rmtree 位置；thread_end 无条件发→set_version 无条件递增的四环闭环；get_version 预登记/set_version 计次；三处 td 派生、三处独立拼目录 + makedirs；V/v 大小写分裂；docx 落输出根且同名静默覆盖；`write_info_json` 整体覆写；CSV 空行=缺失的写端现状与读端 `if float_data:` 错位；`pulse_matcher` 0 哨兵；`results` 压缩丢位；并行结构与派生结果形态；全仓仅 `ndax/converter.py:186` 一处 `nda.read`、**无任何 Step.xml 解析代码**。

**未证实（无真实 NDAX 样本支撑的假设）**：
- H1 `nda.read()` 列契约（Cycle/Step/Status/Current(mA)/Voltage/…/Timestamp）系由 converter 取列反推，列名/单位/Status 值域未校准；
- H2 Step.xml 的物理形态（ndax 容器内 or 解包目录）、档位字段、**完成状态字段的存在性**均未验证——必须三态 `complete/incomplete/unknown` 兜底，unknown 放行留痕，任何"读完成状态即可判定"的写法都是无据断言；
- H3 单文件内存量级 150-400MB/文件为估算（104 万行是实证，字节数/放大系数是估）；
- H4 Word 模板与 excel_sample "word" 工作表对"N/A（原因）"标注的承载未实测（增补标注前先做模板探测）；
- H5 ndax 模式下测试日期来源（Timestamp 首末派生）能否稳定产出 YYYYMMDD 未验证——这是 td 统一方案的前提之一，Phase 4 开工前须用真实样本确认。

---

## 10. 交叉质询增量（简短，含自我修正）

1. **对 Round 2 全体（含我）**：`_r{n}` 后缀方案（GPT §5、DeepSeek R2 §5.2、MiniMax 后缀递增）按用户 0010 全部**撤案**，收敛为"SHA256.csv 递增为主 + 同名安全拒绝"；相应地"`_v` 目录名后缀解析兼容"测试项作废。
2. **对 GPT R2 §5**：`backup_{timestamp}` 改名旧目录方案同样触碰旧结果，撤案。
3. **对我 R2 §5.3 的加强**："输出目录名只解析一次"从建议升为 **P1 硬前置**——本轮新实证（三套 td 派生 + JsonWriter 第三拼名 + rename 失败 fallback）表明这不是防御性编程，是当前就会分裂写入的现实缺陷。
4. **对 GLM R1 §5-3 / MiniMax R2 §3.1**：弹框在 rename/写盘时刻弹的方案维持否决（线程违规 + td 此刻才知）。
5. **对 MiniMax R2 §3.1 "后缀递增改动小"**：已被裁决覆盖，不再讨论。
6. **对 GPT R2 红线 1/2/3、DeepSeek R2 §3.2 两层分类、§3.1 冻结规则**：本轮复核代码后背书，纳入 §5/§6/§8 验收。
7. **自我修正**：我 R1 的"P2 推荐两遍读取"（0004 §3.2）维持撤回；本 §4 补齐了 GPT 要求的"一次读取峰值高于两遍的具体场景"举证义务——**不存在**该场景（峰值同式、时间 1× vs 2×），除非"缓存全批 DataFrame"这一被否决变体被错误实现。

---

## 11. 最终推荐（简洁）与未决事项

**推荐（直接采纳）**：
1. **路径单点化**（P1）：td 派生唯一化 + V/v 统一小写 + 目录名只解析一次下发全部写入器，docx 落点纳入清单——这是输出安全的硬前置；
2. **RunManifest 白名单**（P2）：删两处 rmtree、同名安全拒绝、失败/取消只清本次独占创建的半成品，旧目录绝不动；
3. **成功门槛**（P3）：交付物逐项校验为唯一递增条件；thread_end 保持无条件（UI 复位），新增 `analysis_succeeded` 专挂 set_version；SHA256.csv 预登记/计次语义分开测试；
4. **一次读取**（§4 形态钉死）：逐文件流式 + 列投影 + 派生完即丢 DataFrame；禁缓存全批；
5. **占位契约**（§5）：CSV 结构零改动（空行=缺失）、读端补位、原因/状态进 JSON、禁 0 哨兵；异常汇总单一冻结、决策层/提示层分离、两弹主线程；
6. **报告全保留**：Excel 只退输入/中间链，报告链与 Word 超链接一字不动；删测试须逐个注明守的是输入链还是报告链。

**未决事项（需用户拍板，不替用户决定）**：
1. **硬崩溃残留的恢复路径**：kill/断电后 manifest 与半成品残留，同版本重试会被安全拒绝卡住——是"提示用户手动删除"还是提供"人工确认接管/废弃残留"的 UI 出口？
2. **docx 同名是否纳入安全拒绝**：docx 在输出根、同名即静默覆盖（python-docx save）；建议纳入拒绝，但用户裁决字面只说"目标目录"，请确认文件级同名的处置。
3. **非 Windows 分支语义统一**：`multiprocessing.Pool.map` 单文件异常=整批失败，与 Windows 分支 skip 语义不一致；建议统一为保位空槽，请确认是否还需维护非 Windows 支持（项目现状 win32api 强依赖）。
4. **预登记行的长期保留**：get_version 追加的 times=0 校验和行（从未成功过）是否长期留存在 SHA256.csv（我建议保留，属登记非计次）。
5. **真实 NDAX 样本**（H1/H2/H5）：Phase 4 开工的前置条件——无样本不得开工，parity golden 无法建立。
6. **失败状态栏文案/版本显示细节**（纯 UI）：失败时"版本保持上一版"的提示语与显示形态。