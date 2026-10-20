# GPT (Round 3): Round 3：提交时序与版本机制最小改动为核心的分阶段方案（GPT）

# GPT（Round 3）：提交时序与版本机制最小改动为核心的整体分阶段方案

> 身份说明：本轮为第三轮顾问。已通读黑板 0001–0010 全文（Round 1 四家、Round 2 三家 + 用户反馈 0005/0009/0010）。GLM Round 2 因资源不足无有效条目，本文不代其立言；对 GLM 的引用仅限其 Round 1（0001）原文。用户 0005/0009/0010 新裁决为最高约束，不重开、不改源码，只给方案。本轮我重点核查**提交时序与现有版本机制的最小改动**，并对一次读取内存论据做了代码级复核。

---

## 0. 约束固化（用户裁决，全部按"沿用现状最小改动"落地）

1. 原有 Excel/Word/CSV/JSON/图像报告全部保留（四家 R1 的删 Excel 清单已作废，R2 已收敛）；Excel 仅退出分析输入/中间链。
2. profile 不一致 → 点击分析**前**确认；实测档位/通道异常 → 点击分析**后**汇总、两次确认。
3. 一次读取优先（内存论据见 §2，已按代码结构复核成立，附校准假设）。
4. 版本机制沿用 `SHA256.csv` 主/次版本递增；删除 `analysis_worker.py` 两处"同名即 rmtree"；**不引入 `_r{n}` 等新版本体系**（R2 各家的 `_r2`/后缀/backup 改名方案随 0009/0010 一并作废，包括我 R2 §5 的 `_r{n}` 提案，如实撤回）。
5. **只有全部报告成功产出后次版本才递增**；失败或取消仅清理本次运行独占创建的半成品；旧目录绝不动。

---

## 1. 【重点】提交时序与版本机制核查（全部为本轮已证实代码事实）

### 1.1 "失败/取消也递增版本"的完整链路实锤

| 环节 | 代码事实 | 后果 |
|---|---|---|
| `analysis_worker.py:261-280` | `finally` 中无条件 `self.signals.thread_end.emit()`（:277 注释自证"必须无条件发射"，否则 UI 卡 Running） | 成功/失败/取消一律发"结束" |
| `main_controller.py:137-144` | `_on_analysis_completed` 无条件 `analysis_completed.emit()` | 结束=完成，无成功判别 |
| `signal_connector.py:76` | `analysis_completed.connect(version_manager.set_version)` | 结束即计次 |
| `version_manager.py:221-327` | `set_version()` 无条件对 `sha256_checksum_run` 对应行 `times+1`、写回 SHA256.csv、更新 `lineEdit_Version` | **失败/取消也递增次版本**，与用户裁决 5 直接冲突 |

### 1.2 版本机制本体：天然就是"预登记 + 成功计次"两级，最小改动只需挪挂点

- `version_manager.py:105-196`：`get_version()` 异步算输入目录 xlsx 校验和 → `_on_checksum_ready` → `_compute_version_number`（:122-146）：新校验和**追加** `checksums` 行 + `times="0"`（=预登记、分配主版本）；已有校验和读现 `times`。落盘格式为 4 行 CSV（Checksums:/行/Times:/行），`_write_sha256_csv` 先删后写。
- `set_version()`：在 `sha256_checksum_run`（**Run 时快照**，`analysis_runner.py:182`）上 `times+1`（=成功计次）。
- 结论：**SHA256.csv 格式、主/次语义、`{td}_v{ver}` 目录命名全部不动**。用户 0010"区分预登记与成功计次"的最小落地 = 预登记保持现状（checksums 行 + times=0），把计次（times+1）挂到"全部报告成功"条件上即可。不需新表、不需新字段。

### 1.3 "全部报告成功"的判定现状与缺口

- 现状成功判据分散：`str_error_battery==""`（分析错，:143）与 `str_error_xlsx==""`（报告错，:206-208，`FileWriter.UFW_GetErrorLog`）+ 未取消；`finally` 的 `info.emit` 分支据此报 success/error/cancelled。
- 缺口 1：`os.rename` 失败（:188-190）**静默降级** `final_dir = version_dir` 继续跑完——半成品落在 `v{ver}`，报告写进 `{td}_v{ver}`，两处开花。这不应算成功。
- 缺口 2：`_start_visualizer` 在报告错误分支之外执行（:209 附近，if/else 之外）——visualizer 启动失败不应影响成功判定（建议仅日志），但它可能持有结果文件句柄，干扰失败清理（见 §7 残余风险）。
- 最小改法：worker 内设**唯一显式 `b_reports_ok`**，仅在"Info_Image.csv / Info_Plot.json / Excel 双工作簿 / Word / CSV / JSON / 图像全部写完、各自无错误、且全部落在最终目录"时置真，并经独立信号上报（见 §5 阶段 2）。

### 1.4 两处 rmtree 的删除与"同名安全拒绝"替换语义

现状（已核实行号）：
- `analysis_worker.py:112-114`：`version_dir = f"{str_output_path}/v{list_test_info[16]}"`，存在即 `shutil.rmtree`；
- `analysis_worker.py:173-176`：`final_dir = f"{str_output_path}/{str_test_date}_v{...}"`，存在即 `shutil.rmtree`，随后 `os.rename(version_dir, final_dir)`（:186）。

按 0010 替换为**存在即安全拒绝、绝不覆盖**：
- 启动点：`version_dir` 已存在 → 拒绝启动（主线程提示该路径 + 建议人工处置），不创建、不删除；
- rename 点：`final_dir` 已存在 → 中止本次运行 → 清理本次自有半成品 → 不递增版本；
- 报告点：同名 `_TD{td}_v{ver}.docx`（写在输出根，见 1.5）已存在 → 记为报告失败 → 同上。

**所有权不变量（失败清理的合法性依据）**：本次运行独占创建物 = ①启动时经存在性检查后新建的 `version_dir`；②rename 后的 `final_dir`（rename 前已确认不存在）；③本次写出的 docx/日志/临时文件（写前已确认不存在）。因创建前一律"存在即拒绝"，故失败/取消时**整目录删除自有物是安全的**，旧目录（任何预先存在的路径）全程零接触。清理用精确路径白名单，禁宽泛 glob（DeepSeek R2 §5.4 的 `file_service.py` 通用 rmtree 不得复用，维持）。

### 1.5 【关键前置】写入器独立拼目录——防覆盖方案若不先修此处必然失效（已证实）

- `report_coordinator.py:325-326`：`os.path.join(strResultPath, f"{td}_v{listTestInfo[16]}")` + `os.makedirs(..., exist_ok=True)`；
- `json_writer.py:24` + 文末 `os.makedirs(..., exist_ok=True)`：同样独立拼 `{td}_v{ver}`；
- **td 有三套独立推导**：worker（`parse_test_date(test_date, original_cycle_date, fallback)`，`analysis_worker.py:160-170`）／`report_coordinator._extract_test_date`（:350-379，`parse_test_date` + 电池名数字正则回退）／`json_writer`（:21-25，直接 `split("-")`，异常时 `td="00000000"`）；
- `excel_report_writer.py:82-88`、`word_report_writer.py:71-72` 又用 `basename.split("_v")[0]` 反推 td 拼 docx 名；且 `report_coordinator.py:486-489` 把 **Word docx 写到结果目录的父目录**（`result_dir = Path(self.strResultPath).parent`）——docx 是输出根下的散件，失败清理清单必须包含它。

风险（结构性）：worker 侧一旦拒绝/改名/回退，写入器仍按自己拼的名字 `makedirs` + 写入——要么写进旧同名目录（静默覆盖旧报告），要么造出第二个目录；失败清理也不知道这些路径。**硬前置工单：输出目录名一次决议、统一传入全部写入器**（`write_all`/`FileWriter`/`ReportCoordinator`/`JsonWriter` 增加显式 `result_dir` 参数，旧签名向后兼容回退）；td 单一来源；写入器不得自行 `makedirs` 新目录（只允许对传入目录 `exist_ok=True`）。验收 = 全仓仅一处 `f"{td}_v{...}"` 拼名。此项与 0009 主持人要求"全部报告路径一次决议并统一传入写入器"完全一致。

### 1.6 大小写 V/v（已证实字符串事实；跨平台后果为平台语义推断）

- `battery_analysis.py:88`（日志路径）与 `:263`（`UBA_WriteCsv(f"{strResultPath}/V{...}")`）用**大写 `V{ver}`**；`analysis_worker.py:112` 创建**小写 `v{ver}`**。
- Windows（大小写不敏感，本项目现状依赖 `win32api`）两者落同一目录，rename 时 Info_Image.csv/Info_Plot.json 随行——现状能跑；POSIX 上会分裂成两个目录，rename 只搬 `v{ver}`，CSV/JSON 掉队成半成品。
- 最小修：version_dir 由 worker 一次算好**传入** `BatteryAnalysis`，全仓路径常量唯一，消灭大小写双写。测试矩阵加静态检查（grep 无 `V{` 路径拼接）。

### 1.7 其他提交时序毛刺（已证实）

1. `rename_path` 信号在 `os.rename` **之前**发（:180 vs :186），rename 失败时 UI 已收到新路径 → 信号挪到 rename 成功后发。
2. `set_version` 用 Run 时快照 `sha256_checksum_run` 而非实时 `sha256_checksum`——正确，保留。
3. **已知竞态**（`_on_checksum_ready` 注释自证"已知限制"）：校验和未就绪就点 Run → `analysis_runner.py:182` 快照到空/旧值 → 该次 `set_version` 找不到行（:294-297 warning 后直接 return）→ 不递增 → 同名碰撞概率上升，直接冲击"同名拒绝"的用户体验。最小修：**Run 前置门槛**——`sha256_checksum_run` 非空且与当前输入匹配才允许启动（未就绪则禁用 Run/提示等待）。这是"同名拒绝"不被误触发的关键配套。
4. `get_version()` 预登记会在输入扫描时向 SHA256.csv 追加新 checksum（times=0）——属"预登记"，符合 0010 口径，保留；失败/取消**不动它**（"版本保持上一版"= times 不变）。

---

## 2. 一次读取内存论据复核（用户点名核实）

**已证实的代码结构**：
- `_parallel_process_file`（`battery_analysis.py:277-370`）在子进程内读单文件 → 派生 posi/charge/voltage/时间戳等列表后返回（:364-370），**DataFrame 不出 worker 进程**；主进程 `results` 只收派生列表。
- 并行度：Windows/冻结态走 `ProcessPoolExecutor`（`ResourceManager.get_optimal_process_count`，默认上限 8）；非 Windows 走 `multiprocessing.Pool(min(cpu, 4))`（:154-212）。

**结论**：峰值内存 ≈ 并行度 × 单文件 DataFrame（+派生结果小头），**与读一遍还是两遍无关**；两遍读取只是把同样的峰值付两遍解析时间（DeepSeek R2 已自行撤回两遍推荐）。一次读取（先算不写、逐文件流式、派生完即丢）在时间和内存两维同时占优，且与"异常点击后汇总"的用户时序天然吻合。R2 的论证在代码结构上成立。

**假设（尚无真实 NDAX 样本支持，须如实标注）**：
- 单文件 DataFrame 实际体积、`nda.read()` 的内存/耗时系数——无实测；"百万行级"仅由 converter 的 104 万行拆表阈值反推；
- "列投影约减半内存"是估计非实测；
- ndax 直读后列契约以 `ndax/converter.py:186` 的取列为准，需真实样本校准（四家共识，维持）。
- 适用边界：若单文件投影后仍超单 worker 可用内存，一次/两次读取同样失败，属分块解析问题，不构成改选两遍的理由。

---

## 3. 数据结构与占位契约（收敛定稿）

1. **Info_Image.csv 零结构改动**：每电池恒 `1 + 3*C` 行，缺失槽位三行写空行 = 缺失（现行事实格式，旧文件天然兼容）。唯一必改在读端：`data_loader._process_csv_data` 空行也 append 占位，恒保 `len(listPlt[c]) == 电池数`（错位 bug 本体）。
2. **禁文本 token 进 CSV**（`MISSING`/`N/A`）：`_process_csv_data` 按 `index % intPerBatteryRows` 取模定长定位，插行/注入非数字 token 都会错位或被旧读取器静默丢弃（DeepSeek R2 §2.3 反证成立，维持否决 GLM R1 哨兵行与我 R1 的 (b) 显式 MISSING 行）。
3. **禁 0 哨兵**：`pulse_matcher` 的 `listLevelToRow` 初值 0 与合法行 0 不可分 → 改 `None`，`ChargeCalculator` 遇 `None` 显式返回 `None`。
4. **Info_Plot.json 增量键**：`slot_status`/`channel_status`/`format_version`/`profile_validation`（`policy_version: "2026.10"`）；`write_info_json` 改 read-merge-write，已存在的 `profile_validation` 不可覆盖（注意它在 rename 前写入、随目录搬移，留痕写入时机放在提交段内一次完成）。
5. **内存契约**：`BatteryResult{battery_idx, name, status: OK|MISSING_PULSE|CHANNEL_FAILED|FILE_FAILED, slot[b][c] = 数据|None, 原因}`；维度 B×C×V 恒定；**废除 `results = [r for r in results if r is not None]` 压缩**（`battery_analysis.py:198-199` 实锤，异常清单与报告必须同坐标系）。
6. **用户可见提示**（内容增强，不删报告类型）：图=空区+灰字"缺失(原因)"；Excel/Word/CSV 单元格="N/A(原因)"；报告增"数据缺失汇总"区块。内部标记（机器）与可见标记（人）严格两层，CSV 里永远不放给人看的文本。

---

## 4. GUI 线程边界（硬红线）

- `AnalysisWorker` 跑在 `QThreadPool`（TaskRunner），`run()` 全程非 GUI 线程；现有 worker 内无 QMessageBox（grep 证实，这条纪律目前靠"还没做"维持）。
- 硬规则：**一切弹框（profile 阻断/免责、异常两弹、同名拒绝告知）经信号回主线程构造执行**；worker 阻塞在 `threading.Event` 等决定；超时/取消/信号对象销毁一律按"停止整批"。实现禁例：MiniMax R1 §6.2 的内联 `QMessageBox.question`、GLM R1 §5-3 在替换点弹框——均不得照抄进 worker 路径。
- `thread_end` **保持无条件发射**（复位 `is_analysis_running`/Run 按钮，:277 注释语义）；成功判别走独立信号，绝不给 `thread_end` 加条件——否则 UI 卡死在 Running。
- 验收：pytest-qt 断言全部弹框发生在 GUI 线程。

---

## 5. 分阶段方案（以提交时序/版本最小改动为轴）

- **阶段 0（P0 独立合入）**：`filter_data` 两处空列表越界防御（含 IndexError 兜底）；`pulse_matcher` 0 哨兵→`None`；`battery_analysis` 保位合并（废压缩）。
- **阶段 1（硬前置：路径一次决议）**：最终目录名一次算出、显式传入 `write_all`/`ReportCoordinator`/`JsonWriter`；td 单一来源；V/v 大小写统一；docx 名与位置（输出根）统一登记进运行路径清单；写入器不再独立拼名/自建目录。验收 = grep 拼名唯一。
- **阶段 2（提交时序与版本门槛——最小改动本体）**：
  a. 删两处 rmtree → 三处"存在即安全拒绝"（启动/rename/报告）；
  b. 新增 `analysis_succeeded` 信号（或 `thread_end(bool)`），仅"全部报告成功"发；`signal_connector` 把 `set_version` 的连接从 `analysis_completed` 挪到 `analysis_succeeded`；`analysis_completed` 保留专责 UI 复位；
  c. 失败/取消清理：`finally` 中按本次运行路径白名单删除自有半成品（version_dir 或 final_dir、本次 docx、运行日志、临时文件），SHA256.csv 的 times 不动；
  d. Run 前置门槛：`sha256_checksum_run` 就绪校验（堵 §1.7-3 竞态）；
  e. `rename_path` 信号挪到 rename 成功后。
- **阶段 3（点击后异常汇总两次确认）**：一次读取先算不写 → 冻结 `AnomalyReport`（决策层 MISSING_PULSE/CHANNEL_FAILED/FILE_FAILED 与提示层 中位数偏差/完成性 unknown 分区呈现，DeepSeek R2 §3.2 分层维持）→ 弹框①"是否停止整批"（默认停止）→ 弹框②空位清单"确认放行"（默认中止）→ 进入阶段 2 提交段。profile 不一致/免责留在点击前（`analysis_runner._check_inputs` 后、启动 worker 前是天然挂点，0005 裁决 5 的字面时序）。
- **阶段 4（占位契约贯通 + 报告增强）**：§3 全链路 + 统计排除缺失槽位（n 标注、禁 0 入分母）。
- **阶段 5（输入链切 ndax，Excel 退输入层）**：ndax reader 复用 converter 拆表逻辑（共享函数，禁两份实现）；`file_validator`/`path_manager`/`version_manager` 校验源切 ndax（版本语义不变，见 §8 未决 2）；删输入侧 `xlsx_reader`/`excel_validator`/`excel_processor` 链；报告侧 Excel/Word/CSV/JSON/图全部保留。Step.xml 三态 `complete/incomplete/unknown`，unknown 放行留痕（不假定字段存在）。
- **阶段 6（回归与守卫）**：§6 矩阵 + 架构守卫（分析链无 xlsx 读取；报告链 Excel 在场；全仓仅一处目录拼名）。

阶段依赖：0 与 1 可并行先行；2 依赖 1；3 依赖 2 的成功信号接口；4 依赖 3；5 独立性较强但版本校验源切换并入 2d 一起验；6 贯穿。

---

## 6. 成功门槛/失败清理测试矩阵（提交时序专项）

| # | 场景 | 期望 |
|---|---|---|
| S1 | 全报告成功 | 次版本 +1、UI 版本更新、`{td}_v{ver}` 内报告齐全、输出根 docx 存在、无残留 |
| S2 | 分析失败（坏文件/异常冒泡） | 版本不递增、SHA256.csv 逐字节不变、无 `v{ver}`/`{td}_v{ver}`/docx 残留、旧目录完好 |
| S3 | 取消（分别在：建 version_dir 后/分析中/rename 后/报告写一半） | 同 S2；取消点覆盖全部进度点 |
| S4 | rename 失败注入（预占目录/权限） | 不降级继续、按失败清理、不递增 |
| S5 | 报告中途失败注入（Excel 抛错/磁盘满） | 不算成功、清理本次 docx+目录、预置旧 docx 字节不变 |
| S6 | 同名拒绝：预置 `v{ver}`、`{td}_v{ver}`、同名 docx | 各拒绝点生效且预置物零改动 |
| S7 | 竞态：校验和未就绪点 Run | 拒绝启动；就绪后正常走 S1 |
| S8 | 双击 Run 并发 | 第二次被 `is_analysis_running` 拒绝（现有机制回归） |
| S9 | 清理白名单 | 输出根预置无关文件，失败清理后仍在 |
| S10 | 大小写 | grep 无 `V{` 路径拼接；version_dir 常量唯一 |
| S11 | 版本往返 | 成功×2 → `v1.0`/`v1.1` 两目录并存；失败×2 再成功 → 仅一个 `v1.0`；`set_version` 只认 `sha256_checksum_run` 行 |
| S12 | 路径决议 | 注入 td 推导分歧夹具，断言写入器与 worker 落同一目录（一次决议生效） |

---

## 7. 已证实代码事实 vs 尚无真实 NDAX 样本支持的假设

**已证实（本轮行级核查）**：§1.1–1.7 全部条目；`results` 压缩丢位（`battery_analysis.py:198-199`）；`_parallel_process_file` 只回派生列表；并行结构与上限；`write_info_json` 整体覆写；SHA256.csv 4 行结构与预登记/计次两段；docx 写在输出根（`report_coordinator.py:488-489`）；三套 td 推导与两处 `makedirs(exist_ok=True)`；`UBA_WriteCsv` 同时写 Info_Image.csv 与 Info_Plot.json（rename 前写入、随目录搬移）；`_start_visualizer` 在报告错误时也会执行。

**假设（须标注，不得当事实写进实现）**：`nda.read()` 列名/单位/内存系数（以 converter 取列契约为准，需真实样本校准）；Step.xml 完成状态字段存在性与字段名（三态兜底）；"列投影约减半"内存（估计）；POSIX 下 V/v 分裂行为（平台语义推断，本项目部署为 Windows）；`excel_sample` "word" 工作表对"N/A(原因)"标注的承载能力（模板未探测）；QThreadPool 下 `Event` 等待的超时语义（需集成测试实证）。

---

## 8. 最终推荐与未决事项

**推荐主线（一句话版）**：一次读取先算不写 → 点击前只做 profile/目录/校验和门槛检查、点击后异常汇总两弹 → 路径一次决议 → 删两处 rmtree 改同名安全拒绝 → **全部报告成功才计次（挪一个信号连接点即可）**、失败/取消只清本次独占半成品 → 空行占位契约 + 报告内容增强；版本机制零新体系、SHA256.csv 与 `{td}_v{ver}` 命名不动。

**未决事项（请拍板，均不重开已裁决项）**：
1. 同名拒绝后的用户出口：纯文本提示人工处置（推荐、最省），还是附"打开目录/复制路径"辅助（不自动删）？
2. 校验源切 ndax 后 SHA256.csv 口径换代：主版本从 1 重新编号（旧 xlsx 校验和行保留不动），还是需要一次性迁移/并存标记？（碰撞由"拒绝"兜底，主要是版本观感问题）
3. "全部报告成功"边界：ImageMaker/visualizer 启动失败建议不算失败（仅日志）；Word docx 停留在输出根（父目录）的位置是否维持现状（建议不动，避免动报告命名）——请确认。
4. 硬崩溃（断电/kill -9）残片无人清理，下次同名拒绝需人工处理——是否接受？（或加"启动时残片检测提示"，仍不自动删）
5. 弹框总数上界：点击前最多 2（profile 阻断/免责）+ 点击后 2（异常两弹）+ 同名拒绝告知 1——是否接受。
6. 失败清理是否保留运行日志 `.txt`（在独占 `v{ver}` 目录内）：建议随半成品删除，如需排障先复制到输出根 `.logs`——待定。

**残余风险**：一次读取的单文件内存上界无实测（列投影缓解，极端需分块解析）；visualizer 可能持文件句柄导致 Windows 上清理失败（清理失败须报残留清单而非静默）；`_on_checksum_ready`/`set_version` 对 SHA256.csv 的"先删后写"非原子，断电可损 CSV（现状如此，建议顺手改临时文件+replace，属低风险增强）；无真实 NDAX 样本前，ndax 链路所有数值 parity 都是待验证项。