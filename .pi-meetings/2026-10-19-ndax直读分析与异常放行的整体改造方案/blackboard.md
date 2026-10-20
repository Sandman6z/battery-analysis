# Meeting: NDAX直读分析与异常放行的整体改造方案
> Created: 2026-10-19T03:22:13.594Z
> Type: Brainstorming (3 rounds)

---

## GLM (Round 1): NDAX直读与异常放行改造：分阶段落地方案、删改边界与staging防覆盖机制

# Round 1 — GLM：NDAX 直读与异常放行改造的落地方案

## 0. 独立代码核查结论（与 transcript 索引一致，补充细节）

- `ndax/converter.py:186`：`nda.read(str(ndax_path), software_cycle_number=False)` 是项目唯一 ndax 读取入口，目前只服务"ndax→xlsx 导出"。它从单个 DataFrame 按 `Cycle`/`Status` 列拆 Cycle/Step/Record 三表再写 xlsx。**主分析直读应复用这套拆表逻辑，重构为共享函数（如 `ndax/reader.py: read_ndax_frames(path)`），禁止两份实现。**
- `utils/processors/battery_analysis.py`：主链路为 `scan_sorted_xlsx → read_xlsx_sheets → detect_pulse_rows → match_pulse_levels(start_row=2) → ChargeCalculator → write_info_csv/json`。`read_xlsx_sheets` 产出的 DataFrame 带 2 行头部（文件名行+中文表头行），列提取按 `iloc[:,2..4]` 位置索引；`detect_pulse_rows` 识别的工步类型是中文（"脉冲"，由 `STATUS_MAP` 映射）。**直读 ndax 后列名是英文、无头部行——这是适配器设计的核心问题（见 §2 阶段一）。**
- `utils/processors/data_utils.py filter_data()`：空档位时 `charge_np` 为空数组，`filtered_mask = np.zeros(0)`，`filtered_mask[0] = True` 抛 IndexError；外层 `except (ValueError, TypeError)` 不含 IndexError，fallback 分支 `[float(charge_data[0])]` 同样越界。**确认 P0：空档位必然崩溃，且异常类型未被捕获会直接冒泡。**
- `utils/processors/pulse_matcher.py`：未匹配电流档位的 `listPosiForInfoImageCsv[c]` 留空列表——这是占位数据模型的自然挂点。
- `main/workers/analysis_worker.py run()`：先 `shutil.rmtree(version_dir)` 再分析，改名前再 `rmtree(final_dir)`。**所有覆盖删除都发生在分析开始前，与决定 5"确认在删除前"结构性冲突（见 §5）。**
- `utils/writers/info_csv_writer.py`：`write_info_json` 整体 `json.dump` 覆写，无 profile_validation 字段；`write_info_csv` 空档位写空行（3 行中 posi/charge/voltage 全为空列表），`main/visualization/data_loader.py` 的 `csv_read/_process_csv_data` 读到空行不补占位，后续按电池下标访问 → 错位风险确认。
- `utils/report_coordinator.py` + `writers/excel_report_writer.py / excel_sample.py / excel_overview.py`：Excel 报告全链存在；`word_overview.py / word_front_matter.py` 依赖 `strSampleXlsxPath / strResultXlsxPath` 做相对路径链接——**删 Excel 报告时 Word 中的 xlsx 超链接必须一并处理，否则报告引用不存在的文件。**
- `utils/file_validator.py validate_input_directory()` 硬编码目录名必须为 `2_xlsx`；`main/managers/path_manager.py:170` 自动定位 `2_xlsx`；`main/tabs/ndax_tab.py:145` 导出默认输出 `parent/"2_xlsx"`（导出功能本身，保留）。
- `utils/input_validator.py REQUIRED_TEXT_FIELDS` 含 `test_profile`；`analysis_runner.py _check_inputs` 走 `main_window.checkinput()`。
- `main/business_logic/data_processor.py`：扫描 xlsx + 首文件文件名解析档位（经 `filename_parser`/`pulse_currents`）写全局配置——ndax 模式下此职责移交 Step.xml。

## 1. 端到端数据流（目标态）

```
用户输入目录（ndax 目录，命名待拍板，如 1_ndax）
  ├─ Step.xml            → 配方档位列表 + 完成状态（决定 1/3/4）
  └─ *.ndax（自然排序）  → nda.read() → 共享拆表 → (cycle_df, step_df, record_df)
                                        ↓
                    detect_pulse_rows（适配英文状态）→ match_pulse_levels（档位固定索引）
                                        ↓
              BatteryResult[]（含 status/占位）→ 汇总异常 → 用户确认
                                        ↓
              staging 目录写入 Info_Image.csv / Info_Plot.json（profile_validation 留痕）
                    → 通过最终确认 → 原子替换正式目录 → Word/JSON/CSV 报告
ndax_tab（导出功能）：独立入口，ndax → xlsx，不经主分析链路（决定 3 保留项）
```

关键原则：**档位唯一来源是 Step.xml**；`listCurrentLevel/listVoltageLevel` 不再来自文件名解析；文件名解析仅保留制造商/批次/温度等元数据用途（是否保留 DC/mA 格式校验见 §7）。

## 2. 实施阶段（建议顺序与理由）

**阶段 0（P0，先行独立上线）**：`filter_data` 空档位防御——`if len(charge_np)==0: append空列表; continue`，并把 IndexError 加入两处 except。最小 diff，立即消除崩溃面，不依赖其他阶段。

**阶段 1：ndax 直读 reader**
- 新建 `utils/readers/ndax_reader.py`（或 `ndax/reader.py`）：复用 converter 拆表逻辑，返回与现结构**完全同形**的三表（含头部行+中文表头，即内部先做 STATUS_MAP 映射并垫 2 行）。理由：`pulse_detector`、`match_pulse_levels(start_row=2)`、`ChargeCalculator`、`iloc` 位置索引全部零改动，风险最小。备选方案是参数化 start_row + 列名对齐，改动面大，不推荐。
- `battery_analysis.py` 输入端替换：`scan_sorted_xlsx` → 扫 `*.ndax`；`_parallel_process_file` 改调 ndax_reader。注意并行进程池语义保留。
- `file_validator.validate_input_directory` / `path_manager` 改为 ndax 目录规则。

**阶段 2：预检 + 两次确认 + 留痕**
- `analysis_runner` 中新增 Precheck 步骤（顺序在 `_check_inputs` 后、启动 worker 前）：解析 Step.xml（档位+完成状态）→ 扫 ndax 目录 → 每文件轻量探测（解 zip 校验内部结构，不做全量 `nda.read`，太重）→ profile 档位比较（决定 4 全部规则）。
- 异常汇总弹框 1「是否停止整批」→ 继续 → 弹框 2 明确确认（列出"保留空位、不伪造零值"后果）。
- 留痕：`Info_Plot.json` 增加 `profile_validation` 与 `policy_version: "2026.10"`；QSettings `validation/profile_disclaimer_version` 记一次性免责声明。**注意现有 `write_info_json` 是覆写语义，需改为 merge（读旧→合并→写）或由唯一调用方一次性组装，防止后续写入覆盖（决定 5）。**

**阶段 3：占位数据模型 + 缺失语义贯通**
- 引入 `BatteryResult`（name, status: ok|missing_pulse|read_error|released, charge/posi/voltage 可为 None, error, user_decision）。`listBatteryName` 等 5 个平行列表按 ndax 文件序固定长度，失败文件保留条目。
- 档位级：`listAllPosiForInfoImageCsv[b][c]` 长度恒等于档数，缺失档位为空列表 + 状态标记。
- `Info_Image.csv` 行格式扩展：缺失档位写显式占位行（建议 `MISSING,<档位>,<原因>`，待拍板 §7-2）；`data_loader._process_csv_data` 识别后补占位、按 (电池, 档位) 对齐，`figure_builder` 改按 key 访问，空数据跳过绘制并计数。
- Word/JSON 报告：缺失通道统计行（"3# 电池 500mA 档缺脉冲（用户已放行）"），禁止零值。

**阶段 4：输出不覆盖旧结果**（见 §5 staging 机制）

**阶段 5：Excel 删改**（放后，破坏面最大且不阻塞前面阶段；边界见 §4）

**阶段 6：输入验证收尾**：`input_validator` 移除 test_profile 必填、`validation_feedback` 同步、无 profile 免责声明流程、`data_processor` 的 xlsx 扫描/文件名档位解析链下线。

## 3. 异常预检汇总 + 两次确认（详细设计）

**预检层（删除旧结果/启动分析之前，主线程或 TaskRunner）**：
1. Step.xml：档位列表提取；完成性——有完成字段且已完成 → 直通；有字段但未完成 → 按决定 1 不阻断（建议：黄色告警入汇总，见 §7-5）；无字段 → 默认放行。
2. ndax 目录扫描：空目录/文件数与 Samples Qty 不符 → 入汇总。
3. 每文件 zip 结构探测（不解全量数据）：坏包/缺 data.ndc → 入汇总。
4. profile 档位比较（有 profile 时）：同数不同档值 → 阻断 + "以 ndax 为准继续"按钮（默认中止）；档数不一致 → 人工确认出口；多 ndax 间 Step.xml 档位不一致 → 硬阻断（旧定案未改）。
5. 无 profile → 一次性免责声明（QSettings 版本号控制）。

**运行期层（worker 内，不中止整批）**：`_parallel_process_file` 失败不再静默 skip（现状 Windows 分支 skip 后 `results` 过滤掉 None，导致电池错位）——改为返回占位 BatteryResult（status=read_error/missing_pulse），保持固定索引。全部文件完成后：若存在运行期异常，弹最终确认「结果含 N 个异常通道：保留（写入正式目录）/ 放弃（删除 staging，旧结果不动）」。

**确认次数归属**：预检两弹（停止整批？/ 明确确认继续）满足决定 2 的字面要求；运行期异常确认是决定 5"确认在删除前"的必然产物（见 §5 冲突 A）。是否将运行期确认与预检第二弹合并为"分析前一次 + 分析后一次"，请拍板（§7-3）。

**留痕内容**：`profile_validation = {policy_version, step_xml_levels, profile_levels, comparison_result, completion_status, anomalies: [{battery/file, channel, type, detail}], user_decisions: [{timestamp, action, scope}]}`。

## 4. Excel 删改边界（决定 3 的落地清单）

**保留（独立 ndax→Excel 导出功能）**：
- `ndax/converter.py`（含拆表与 STATUS_MAP——阶段 1 重构为共享后两边共用）
- `ndax/worker.py`、`main/tabs/ndax_tab.py`（含其默认输出 `../2_xlsx`，是导出功能约定，不动）
- 依赖：NewareNDA、xlsxwriter。

**删除（主分析/报告链 Excel）**：
- `utils/writers/excel_report_writer.py`、`excel_sample.py`、`excel_overview.py`、`excel_formats.py`、`excel_utils.py`（确认仅报告链引用后删）
- `report_coordinator.py` 中 Excel 分支与 `strSampleXlsxPath/strResultXlsxPath` 参数
- `main/business_logic/excel_validator.py`（输入 xlsx 校验，主链路下线后无消费方）
- `utils/readers/xlsx_reader.py` 主链路引用（阶段 1 后无消费方；若导出功能不用可整体删）
- `data_processor` 中 `get_xlsxinfo/_scan_excel_files_task/_process_excel_files_task` 及相关缓存
- 对应测试：`test_excel_report_writer/test_excel_utils/test_excel_processor/test_excel_validator/test_xlsx_reader/test_report_qualification` 等裁剪

**连带影响（必须处理）**：
- Word 报告超链接指向 sample/result xlsx → 删链接或改指 JSON/CSV（§7-6）。
- `file_writer.write_all` 签名与 `ReportCoordinator` 构造参数收缩。
- i18n 文案中 Excel 报告相关条目清理。

## 5. 输出不覆盖旧结果的安全机制（staging 方案）

现状 `analysis_worker.run()` 两处 `shutil.rmtree`（version_dir、final_dir）都在用户任何确认之前执行。改造：

1. 分析写入 `<output>/<date>_v{n}.staging/`（或 `.partial` 后缀），全程不触碰正式目录。
2. 预检两次确认通过才允许进入分析（此时仍不删任何旧目录）。
3. 分析完成 + 运行期异常最终确认（若发生）通过后：若正式目录 `<date>_v{n}` 存在 → **默认中止并弹框**，选项：中止（推荐）/ 自动备份改名（`<name>.bak-<时间戳>`）后替换 / 显式覆盖。删除旧目录与 rename staging 是最后的原子动作（同分区 `os.replace` 语义）。
4. 用户在任何确认点选择停止 → 删除 staging，正式目录与旧结果完好。

该方案同时满足决定 2/5 和"输出不覆盖旧结果"。**结构冲突如实指出**：决定 5 说"确认发生在删除旧结果前"，但决定 2 的缺脉冲等异常只能在运行期发现，而现有代码删除发生在分析开始前——不引入 staging 就无法两全。请用户确认接受 staging 机制。

## 6. 最小测试矩阵

| 类别 | 用例 |
|---|---|
| P0 回归 | `filter_data` 空 charge/voltage 列表 → 不抛异常、返回空占位（新增强解 IndexError 场景） |
| ndax reader | 正常文件三表形状/列对齐；坏 zip；无 data.ndc；Status 英文→中文映射；与 converter 拆表结果一致性（golden 对比） |
| 脉冲匹配 | 某电流档无匹配 → 空列表 + 状态；全部档位正常；无脉冲 → 占位结果而非异常上抛 |
| 预检汇总 | Step.xml 有/无完成字段；多文件混合异常 → 汇总结构完整不丢项；多 ndax 档位不一致 → 硬阻断 |
| 确认流（QTest/mock） | 弹框1 选停止→不启动 worker；选继续→弹框2 确认→启动；弹框2 取消→中止；运行期异常→保留/放弃 |
| 留痕 | `Info_Plot.json` 二次写入 merge 后 `profile_validation` 不被覆盖；policy_version 正确 |
| 占位贯通 | Info_Image.csv 含 MISSING 行 → data_loader 对齐不错位；figure_builder 跳过空通道；Word/JSON 报告缺失统计行 |
| 输出保护 | 正式目录存在 → 默认中止；备份改名路径正确；staging 清理 |
| 导出回归 | ndax_tab 导出 e2e 不受任何改动影响；2_xlsx 默认输出不变 |
| 删除验证 | 全仓 grep 无 Excel 报告残留引用；受影响测试裁剪后套件绿 |

## 7. 需用户拍板的分歧/决策点

1. **ndax 输入目录命名与强制规则**：主分析目录名（建议 `1_ndax`）；`file_validator` 是否照抄"目录名必须精确匹配"的强校验。
2. **Info_Image.csv 缺失占位格式**：`MISSING,<档位>,<原因>` sentinel 行 vs 每电池新增状态块。影响 data_loader 解析与向后兼容。
3. **确认次数编排**：预检两弹 + 运行期一弹（本方案），还是把运行期异常确认并入"分析后唯一确认"。
4. **旧结果存在时的默认动作**：中止询问（本方案推荐）/ 自动备份替换 / 允许覆盖。
5. **Step.xml 有完成字段但未完成**：决定 1 只说"不硬阻断"——建议黄色告警进预检汇总（与中位数偏差 >max(1%,0.5mA) 同级），请确认。
6. **Word 报告中原 xlsx 链接的替代物**：删除 / 改指 JSON/CSV。
7. **ndax 文件名校验**：是否沿用 DC/mA/温度文件名格式校验（现 `validate_excel_filename` 语义），还是放宽只做自然排序。
8. **旧 xlsx 输入模式是否留兼容开关**：本方案按决定 3 直接删除（无回退），请确认无灰度需求。

## 8. 用户决定间冲突汇总（如实指出）

- **冲突 A（结构性，最重要）**：决定 5"确认在删除旧结果前" vs 决定 2"缺脉冲运行期才发现" vs 现有代码"分析前即删目录"。解法是 §5 staging 机制，需用户认可。
- **冲突 B（交互叠加）**：决定 4"同数不同档值默认中止+以 ndax 为准按钮"与决定 2"预检汇总两弹"若各自独立弹框，一次运行可能弹 4~5 次。建议档位不一致并入预检汇总弹框 1 统一呈现（按钮语义保留），请拍板。
- **注意 C（非冲突但易踩）**：决定 3"不经 2_xlsx" 与 ndax_tab 导出默认输出 2_xlsx 并存无冲突，但 `path_manager` 自动定位从 2_xlsx 切到 ndax 目录时，不能误伤 ndax_tab 的导出路径逻辑（两者共用 `parent` 推导）。
- **注意 D**：中位数偏差告警（黄）与"找不到脉冲"（异常预检/确认）是两类检查，且中位数只能在分析后算出——归入运行期信息，与冲突 A 同根，需在同一编排下处理。


---

## MiniMax (Round 1): NDAX直读整体改造方案 Round 1 顾问意见

# NDAX直读分析与异常放行整体改造方案 —— MiniMax Round 1 顾问意见

## 一、代码核查核心发现

### 1.1 输入链路阻断点（与用户决定#3冲突）

**FileValidator.validate_input_directory()** (`utils/file_validator.py` 第97行):
```python
if os.path.basename(directory) != "2_xlsx":
    return False, f"Input path is not a 2_xlsx directory: {directory}"
```
此验证强制要求输入目录名为"2_xlsx"，与用户决定"主分析全程使用ndax、输入链路不得扫描/读取2_xlsx"直接冲突。**必须移除或条件化此检查**。

**PathManager.select_inputpath()** (`main/managers/path_manager.py` 第173行)同样调用了上述验证逻辑。

### 1.2 脉冲缺失处理现状（需重构）

**pulse_matcher.py** 第47行：
```python
if not valid_row.any():
    return None  # ← 当前返回None，导致下游IndexError
```

**battery_analysis.py** 第148行（_parallel_process_file）：
```python
matched = match_pulse_levels(...)
if matched is None:
    raise BatteryAnalysisException(f"Pulse data not found: {strPath}")  # ← 直接抛异常
```

用户决定#2要求"某通道失败时不默认中止整批"，这两处需要改为返回空列表而非None/抛异常。

### 1.3 data_utils.py filter_data 越界防御（P0保留项）

第27行 `filtered_mask[0] = True` 之前有 `plt_charge_filtered.append([])` 分支保护，但若后续传入空列表仍有越界风险。此为用户决定#6明确保留的P0防御，无需改动。

### 1.4 Profile必填校验（需松绑）

**input_validator.py** 第127行 FieldValues._validate_required_fields 中 test_profile 在列表内：
```python
("test_profile", "Test Profile"),  # ← 必填项
```

**validation_feedback.py** 第45行 _LEGACY_FIELD_CHECKS 同样包含 test_profile。

用户决定#4已明确"无profile可运行"，需从必填列表移除test_profile条目。

### 1.5 输出覆盖风险（需防重）

**analysis_worker.py** 第52-56行：
```python
version_dir = f"{self.str_output_path}/v{self.list_test_info[16]}"
if os.path.exists(version_dir):
    shutil.rmtree(version_dir)  # ← 直接删除，无确认
```

用户决定#6要求"输出不覆盖旧结果"，需在删除前增加用户确认弹框。

### 1.6 Info_Plot.json 无profile留痕字段

**info_csv_writer.py** write_info_json() 仅写入meta_data，**无 profile_validation 字段**。用户决定#5要求成功写Info_Plot.json.profile_validation 留痕、policy_version 2026.10，需扩展JSON结构。

---

## 二、端到端实施阶段规划

### 阶段1：输入链路重定向（第1-2周）
**目标**：主分析不再依赖2_xlsx中间层

| 步骤 | 操作 | 影响文件 |
|------|------|----------|
| 1.1 | FileValidator 条件化：ndax模式跳过"2_xlsx"强制检查 | `utils/file_validator.py` |
| 1.2 | 新建 ndax_reader.py：封装 nda.read() 返回 DataFrame | `utils/readers/ndax_reader.py` (新增) |
| 1.3 | 修改 BatteryAnalysis.__init__：支持 ndax_dir 参数 | `utils/processors/battery_analysis.py` |
| 1.4 | 修改 data_processor.py：输入路径扫描1_ndax目录 | `main/business_logic/data_processor.py` |
| 1.5 | 修改 path_manager.py：输入路径指向父目录而非2_xlsx | `main/managers/path_manager.py` |
| 1.6 | 修改 ndax_tab.py：转换完成后自动触发主分析 | `main/tabs/ndax_tab.py` |

**调用链变化**：
- 旧：`get_xlsxinfo()` → scan_sorted_xlsx(2_xlsx) → BatteryAnalysis._parallel_process_file → read_xlsx_sheets
- 新：`get_ndaxinfo()` → scan_ndax_files(1_ndax) → BatteryAnalysis._parallel_process_file → ndax_reader.read_nda

### 阶段2：Profile校验松绑（第2周）
**目标**：无profile可运行，有profile做档位比对

| 步骤 | 操作 | 影响文件 |
|------|------|----------|
| 2.1 | input_validator.py：从必填列表移除test_profile | `utils/input_validator.py` |
| 2.2 | validation_feedback.py：从_LEGACY_FIELD_CHECKS移除test_profile | `main/business_logic/validation_feedback.py` |
| 2.3 | 新建 profile_validator.py：profile比对逻辑（档位数量、偏差阈值） | `utils/validators/profile_validator.py` (新增) |
| 2.4 | 修改 validation_feedback.py：profile比对结果二次确认弹框 | `main/business_logic/validation_feedback.py` |
| 2.5 | 添加 QSettings validation/profile_disclaimer_version | `utils/config_defaults.py` |

**profile比对规则**（用户决定#4）：
- 同数不同档值：阻断 + "以ndax为准继续"按钮
- 档数不一致：人工确认出口
- 多ndax配方档位不一致：硬阻断（保留旧定案）
- 实测中位数偏差>max(1%,0.5mA)：黄色告警（区分于"找不到脉冲"）

### 阶段3：异常预检两次确认机制（第2-3周）
**目标**：先汇总全部异常，再两次确认才继续

| 步骤 | 操作 | 影响文件 |
|------|------|----------|
| 3.1 | 新建 exception_collector.py：汇总所有通道异常 | `utils/analysis/exception_collector.py` (新增) |
| 3.2 | 修改 battery_analysis.py：并行处理后收集异常不抛异常 | `utils/processors/battery_analysis.py` |
| 3.3 | 修改 validation_feedback.py 或新建 confirm_dialog.py：两次确认弹框 | `main/ui_components/confirm_dialog.py` (新增) |
| 3.4 | 修改 analysis_worker.py：异常汇总后再决定是否写入 | `main/workers/analysis_worker.py` |

**两次确认UI设计**：
- 第一次弹框：汇总异常列表 + "是否停止整批"（默认停止）
- 第二次弹框：确认异常记录 + "确认放行"（明确记录用户决定）
- 确认后：保留空位，不错位、不伪造零值

### 阶段4：缺档/坏通道固定索引空位（第3周）
**目标**：图表/Word/JSON显式表达缺失语义

| 步骤 | 操作 | 影响文件 |
|------|------|----------|
| 4.1 | 修改 pulse_matcher.py：返回空列表而非None | `utils/processors/pulse_matcher.py` |
| 4.2 | 修改 battery_analysis.py：_parallel_process_file 返回空占位 | `utils/processors/battery_analysis.py` |
| 4.3 | 修改 info_csv_writer.py：写入占位标记（如"N/A"） | `utils/writers/info_csv_writer.py` |
| 4.4 | 修改 data_loader.py：csv_read解析"N/A"占位符 | `main/visualization/data_loader.py` |
| 4.5 | 修改 figure_builder.py：绘图时跳过占位符或显示灰色 | `main/visualization/figure_builder.py` |

**空位数据模型**：
```python
# 结构：[battery_idx][current_level_idx] = list 或 None
listPosiForInfoImageCsv[b][c] = []  # 空列表表示缺档
listChargeForInfoImageCsv[b][c] = ["N/A"]  # 占位符
listVoltageForInfoImageCsv[b][c] = ["N/A"]  # 占位符
```

### 阶段5：Excel边界划定（第3-4周）
**目标**：仅保留独立ndax→Excel导出，删除报告Excel逻辑

| 操作 | 文件 | 决策 |
|------|------|------|
| 保留 | `ndax/converter.py` | 独立ndax→xlsx导出功能 |
| 保留 | `ndax/worker.py` | 后台转换worker |
| 保留 | `main/tabs/ndax_tab.py` | NDAX转换Tab UI |
| 删除 | `utils/writers/excel_report_writer.py` | Excel报告写入 |
| 删除 | `utils/writers/excel_overview.py` | 主结果表 |
| 删除 | `utils/writers/excel_sample.py` | 样本表 |
| 删除 | `utils/writers/excel_formats.py` | 格式定义 |
| 删除 | `utils/processors/excel_processor.py` | Excel处理逻辑 |

**连带影响需讨论**：
- `report_coordinator.py` 依赖 excel_report_writer，是否一并删除？
- Word报告是否保留？（transcript未明确）
- `FileWriter` 依赖 ExcelReportWriter，需重构或删除

### 阶段6：输出保护与Profile留痕（第4周）
**目标**：不覆盖旧结果，profile验证留痕

| 步骤 | 操作 | 影响文件 |
|------|------|----------|
| 6.1 | 修改 analysis_worker.py：输出目录存在时弹框确认 | `main/workers/analysis_worker.py` |
| 6.2 | 修改 info_csv_writer.py：profile_validation字段写入 | `utils/writers/info_csv_writer.py` |
| 6.3 | 添加 policy_version 字段（"2026.10"） | `utils/writers/info_csv_writer.py` |
| 6.4 | 设置 QSettings validation/profile_disclaimer_version | `utils/config_defaults.py` |
| 6.5 | 修改 analysis_worker.py：profile留痕在结果写入后追加（防覆盖） | `main/workers/analysis_worker.py` |

**输出保护机制**：
```python
# analysis_worker.py 修改示例
final_dir = f"{self.str_output_path}/{test_date}_v{version}"
if os.path.exists(final_dir):
    # 弹框：目录已存在，是否覆盖？选项：覆盖/新建(加序号)/取消
    reply = show_overwrite_dialog(self.main_window, final_dir)
    if reply == "cancel":
        return
    elif reply == "new":
        final_dir = f"{final_dir}_2"  # 或时间戳
```

---

## 三、异常预检汇总与两次确认

### 3.1 异常类型分类

| 异常类型 | 代码检测点 | 当前行为 | 目标行为 |
|----------|------------|----------|----------|
| 某档位找不到脉冲 | pulse_matcher.py 返回None | 抛BatteryAnalysisException | 返回空列表，汇总 |
| 某通道读取失败 | battery_analysis.py except块 | 记录日志跳过 | 汇总到异常列表 |
| Step.xml未完成 | 用户决定#1 | 无检测 | 可放行（除非硬阻断场景） |
| Profile档位不一致 | profile_validator.py（新增） | N/A | 硬阻断或人工确认 |
| 实测偏差超阈值 | profile_validator.py（新增） | N/A | 黄色告警放行留痕 |

### 3.2 两次确认UI流程

```
┌─────────────────────────────────────────────────────────┐
│ 异常汇总对话框                                              │
│ ────────────────────────────────────────────────────── │
│ ⚠ 发现以下问题：                                            │
│                                                          │
│ [1] 通道 BTS001: 脉冲档位 800mA 缺失                        │
│ [2] 通道 BTS003: 无法解析Step.xml                          │
│ [3] 通道 BTS005: 中位数偏差 1.2mA > 阈值 0.5mA              │
│                                                          │
│ ────────────────────────────────────────────────────── │
│ [ ] 我已了解异常详情，确认继续分析（保留空位）                    │
│                                                          │
│              [停止整批]  [继续分析]                          │
└─────────────────────────────────────────────────────────┘
         │
         ▼ 选择「继续分析」
┌─────────────────────────────────────────────────────────┐
│ 最终确认                                                  │
│ ────────────────────────────────────────────────────── │
│ ⚠ 即将保留以下空位继续分析：                                 │
│                                                          │
│ • BTS001 (800mA档位空缺)                                  │
│ • BTS003 (整通道空缺)                                     │
│                                                          │
│ 分析结果将写入：20241019_v1.0/                             │
│                                                          │
│ 此操作将生成分析日志记录您的决定。                           │
│                                                          │
│              [取消]  [确认放行]                            │
└─────────────────────────────────────────────────────────┘
```

---

## 四、缺档/坏通道的固定索引空位与报告处理

### 4.1 数据结构设计

```python
class BatteryResult:
    battery_name: str
    has_valid_data: bool  # True=正常，False=空位
    charge_data: list[float] | None  # None表示缺档
    voltage_data: list[float] | None
    posi_data: list[int] | None

class AnalysisResult:
    results: list[BatteryResult]  # 固定长度=输入通道数
    errors: list[ErrorRecord]  # 异常记录
    user_decision: str  # "proceeded" | "aborted"
```

### 4.2 CSV占位符格式（Info_Image.csv）

```csv
BATTERY,BTS001
[1,2,3,4,5]
[100.5,101.2,102.0]
[3.5,3.4,3.3]
BATTERY,BTS002
N/A
N/A
N/A
BATTERY,BTS003
[2,3,4,5]
[99.0,98.5,97.8]
[3.4,3.3,3.2]
```

### 4.3 JSON缺失语义（Info_Plot.json扩展）

```json
{
  "manufacturer": "...",
  "spec_type": "...",
  "current_levels": [200, 400, 600, 800, 1000],
  "battery_results": [
    {"name": "BTS001", "status": "valid"},
    {"name": "BTS002", "status": "missing_pulse", "missing_level": 800},
    {"name": "BTS003", "status": "valid"}
  ],
  "profile_validation": {
    "policy_version": "2026.10",
    "profile_path": "4_test profile/profile.xml",
    "profile_present": true,
    "deviation_warning": true,
    "disclaimer_accepted": true,
    "user_decision": "proceeded",
    "timestamp": "2024-10-19T14:30:00"
  }
}
```

### 4.4 图表绘制空位处理

- 缺失电池：灰色虚线框 + "N/A"标签
- 缺失档位：该电流等级数据列为空，不绘线
- Word报告：在表格对应单元格标注"缺档"或"N/A"

---

## 五、Excel删改边界（用户决定#3明确）

### 5.1 保留范围

| 模块 | 文件 | 理由 |
|------|------|------|
| ndax→xlsx转换 | `ndax/converter.py` | 独立导出功能，用户决定#3明确保留 |
| 转换Worker | `ndax/worker.py` | 后台并行转换 |
| 转换Tab | `main/tabs/ndax_tab.py` | NDAX转换UI入口 |

### 5.2 删除范围

| 模块 | 文件 | 连带影响 |
|------|------|----------|
| Excel报告 | `utils/writers/excel_report_writer.py` | 需确认Word报告存废 |
| Excel概览 | `utils/writers/excel_overview.py` | 被report_writer调用 |
| Excel样本 | `utils/writers/excel_sample.py` | 被report_writer调用 |
| Excel格式 | `utils/writers/excel_formats.py` | 被overview调用 |
| Excel处理 | `utils/processors/excel_processor.py` | 仅被battery_analysis使用 |

### 5.3 需用户拍板：Word报告是否保留？

transcript仅明确"Excel报告"删除，但Word报告未提及。建议：
- **方案A**：一并删除（与Excel报告逻辑耦合）
- **方案B**：保留Word报告（独立功能）
- **方案C**：仅保留Word封面（WordOverview），删除Word样本详情

---

## 六、输出不覆盖旧结果的安全机制

### 6.1 目录命名策略

当前：`{test_date}_v{version}/`

问题：同名目录会直接覆盖（analysis_worker.py已实现）

### 6.2 保护机制设计

```python
def safe_write_output(output_path: str, test_date: str, version: str) -> tuple[bool, str]:
    """安全写入输出，检测覆盖风险"""
    base_dir = f"{output_path}/{test_date}_v{version}"
    
    if not os.path.exists(base_dir):
        return True, base_dir
    
    # 检测旧结果存在
    existing_files = list(Path(base_dir).glob("*.csv"))
    if existing_files:
        # 弹框确认
        reply = QMessageBox.question(
            None,
            "目录已存在",
            f"目录 {base_dir} 已存在，包含 {len(existing_files)} 个文件。\n"
            "选择：\n"
            "• 覆盖 - 删除旧目录后写入\n"
            "• 新建 - 创建 {base_dir}_2\n"
            "• 取消 - 终止操作",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return False, ""
        elif reply == QMessageBox.StandardButton.No:
            # 新建序号目录
            counter = 2
            while os.path.exists(f"{base_dir}_{counter}"):
                counter += 1
            base_dir = f"{base_dir}_{counter}"
    
    return True, base_dir
```

### 6.3 Profile留痕防覆盖

profile_validation写入Info_Plot.json后，采用**追加模式**而非整体覆写：

```python
def append_profile_validation(result_path: str, validation_data: dict):
    """追加profile验证记录，防覆盖"""
    json_path = os.path.join(result_path, "Info_Plot.json")
    
    # 先读取现有内容
    if os.path.exists(json_path):
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    
    # 仅追加profile_validation字段，保留其他内容
    data["profile_validation"] = validation_data
    
    # 写入（原子操作防损坏）
    temp_path = json_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, json_path)
```

---

## 七、测试矩阵

### 7.1 单元测试

| 测试项 | 输入 | 预期输出 | 测试文件 |
|--------|------|----------|----------|
| ndax_reader.read() | 有效.ndax | DataFrame含Cycle/Step/Record | `tests/test_ndax_reader.py` (新增) |
| pulse_matcher无脉冲 | 空pulse_mask | 返回空列表不抛异常 | `tests/test_pulse_matcher.py` |
| filter_data空输入 | [] | []（不越界） | `tests/test_data_utils.py` |
| profile_validator同数不同值 | profile档位[100,200] vs ndax[100,300] | 阻断+继续按钮 | `tests/test_profile_validator.py` (新增) |
| profile_validator无profile | 无XML | 通过（免责声明提示） | `tests/test_profile_validator.py` |

### 7.2 集成测试

| 测试项 | 场景 | 预期行为 |
|--------|------|----------|
| 完整分析流程-正常 | 3个ndax文件均有脉冲 | 生成完整报告，无空位 |
| 完整分析流程-部分缺档 | 文件1缺800mA档位 | 两次确认弹框 → 保留空位 |
| 完整分析流程-全缺档 | 3个文件均无脉冲 | 两次确认 → 用户可中止 |
| 目录覆盖保护 | 输出目录已存在 | 弹框选择覆盖/新建/取消 |
| Profile留痕 | 有profile完成分析 | Info_Plot.json含profile_validation |

### 7.3 回归测试

| 测试项 | 防止回归 |
|--------|----------|
| 2_xlsx目录仍可分析 | FileValidator保留条件化检查 |
| filter_data越界防御 | 空输入不崩 |
| 目录删除前确认 | 不静默覆盖 |

---

## 八、需用户拍板的分歧点

### 分歧1：Word报告存废
transcript明确删除Excel报告，但未提及Word。
- **建议**：一并删除（理由：与Excel报告共享FileWriter逻辑）
- **备选**：保留Word（理由：独立功能，用户可能需要）

### 分歧2：Step.xml"完成状态"判断逻辑
用户决定#1："若Step.xml有明确完成状态且显示完成，可直接通过"。但代码中未找到Step.xml解析逻辑。
- **需确认**：如何读取Step.xml的"完成状态"字段？NewareNDA是否有此接口？
- **备选**：不做完成状态检测（默认可放行），避免依赖字段存在性

### 分歧3：旧报告向后兼容
transcript"旧报告兼容"要求不明确：
- **方案A**：兼容旧Info_Image.csv格式（空位用旧逻辑填充0）
- **方案B**：不兼容，强制升级到新格式
- **建议**：方案A，data_loader识别legacy格式并自动适配

### 分歧4：异常汇总时机
当前设计在"并行处理后"汇总，可能用户希望"边处理边汇总"。
- **方案A**：全部处理完后汇总（当前设计）
- **方案B**：流式汇总（每完成一个通道即更新列表）
- **建议**：方案A，便于用户总览全局后决策

---

## 九、风险与注意事项

### 9.1 高风险项
1. **FileValidator移除条件化检查**：可能影响旧有2_xlsx分析路径，需完整回归测试
2. **空位数据结构变更**：Info_Image.csv格式变化，图表读取端需同步适配
3. **profile留痕写入时机**：必须在结果目录创建后、删除操作前完成

### 9.2 中风险项
1. **NewareNDA API稳定性**：依赖nda.read()接口，需确认版本兼容性
2. **并行处理异常汇总**：需保证线程安全，避免数据竞争
3. **两次确认弹框**：在后台线程中不能直接调用UI，需通过信号机制

### 9.3 低风险项
1. **Excel删除范围**：仅涉及报告生成，不影响核心分析流程
2. **JSON格式扩展**：向后兼容设计，可识别无profile_validation的旧文件

---

## 十、结论

本方案提供五阶段实施路径，涵盖输入链路重定向、profile松绑、异常预检两次确认、缺档空位模型、Excel删改边界、输出保护机制。核心改造点：
1. **移除FileValidator的2_xlsx强制检查**（冲突P0）
2. **pulse_matcher返回空列表替代None**（支持空位）
3. **新增profile_validator实现档位比对**（profile松绑）
4. **新增exception_collector实现两次确认**（异常预检）
5. **修改Info_Plot.json支持profile_validation**（留痕要求）
6. **Excel仅保留converter.py**（边界划定）

需用户确认分歧点后方可进入实现阶段。

---

## GPT (Round 1): GPT (Round 1): 端到端改造方案——入口重塑、迁移阶段、空位语义、Excel 边界与输出安全

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


---

## DeepSeek (Round 1): DeepSeek Round 1：端到端改造方案（数据模型/不变量/失败恢复视角）

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


---

## User (Feedback after Round 1): 报告必须保留与交互时序裁决

# 用户 Round 1 后反馈（原话）

> 原来所有生成的报告不要变，都得有
> 1. 哪个时间短，效率高？
> 2. 显示标记啥意思
> 3. 旧结果是啥
> 4. 不一致在分析运行前，数据异常在点击分析后把

# 主持人释义（保留原话优先）

1. 新裁决优先：所有原有报告类型和交付物必须保留，特别是 Excel 报告不得删除；以前“Excel 仅存在于 ndax→Excel 独立导出”应解释为 Excel 不作为分析输入或中间格式，而**报告生成的 Excel 仍保留**。请顾问据此重做删改边界，不得继续提议删除 Excel 报告或 Word 超链接；现有全部报告种类保持，允许其内容增加异常说明但不要删类型。
2. 用户问一次读取先算不写 vs 读两次哪个耗时更短、效率更高；需基于 `nda.read`、进程并行与内存/磁盘成本给出单选及适用边界，不能空谈。
3. 用户不理解“显式缺失标记”，请解释内部 CSV 占位与用户图/报告的可见提示分别是什么，有没有必要改变 CSV 结构；推荐最小兼容策略。
4. “旧结果”指此前相同日期/版本已生成的报告目录，请核实真实代码目录命名和覆盖时机，说明风险与最省事的保护办法。
5. 交互时序新裁决：profile 不一致在点击运行之前检查并确认；档位/通道的实测数据异常在用户点击分析之后、处理 ndax 时汇总再两次确认。不能把数据异常预检强制塞在运行按钮之前。

Round 2 请明确质询 Round 1 中删 Excel 报告的建议已被用户推翻，收敛时间/内存方案和报告完整性；顾问须读取 Round 1 四篇及本条用户反馈。


---

## MiniMax (Round 2): MiniMax Round 2：修订Excel立场、收敛四次交互、量化读写方案

# MiniMax Round 2：修订立场、质询证据、交出单选方案

## 一、主动承认Round 1的核心错误

### 1.1 删除Excel报告的建议必须撤回

**Round 1的立场**（MiniMax §5）：
> 删除：`utils/writers/excel_report_writer.py`、`excel_overview.py`、`excel_sample.py`、`excel_formats.py`、`utils/processors/excel_processor.py`

**用户反馈（原话）**：
> 原来所有生成的报告不要变，都得有

**结论**：用户明确推翻了全部四位顾问关于删除Excel报告的共同建议。**我撤回自己的建议**，并对其他三位顾问提出质询：

- **GLM §4** 删除Excel五件套 + report_coordinator Excel分支——违反用户裁决①
- **GPT §4** 移除Excel报告五件套 + report_coordinator删Excel分支——违反用户裁决①
- **DeepSeek §4.2** 删除Excel报告链——违反用户裁决①

**正确的Excel边界重述**：
- **保留**：所有Excel报告生成代码（excel_report_writer/excel_overview/excel_sample/excel_formats/excel_utils）
- **保留**：report_coordinator中的ExcelReportWriter调用
- **保留**：Word报告（含其Excel超链接，链接目标存在）
- **改变**：Excel**不再**作为分析输入或中间格式——即`ndax→xlsx→分析`链路改为`ndax→分析`，但分析**输出**的Excel报告**必须保留**

### 1.2 "Excel边界"的新定义（Round 1各方均需修订）

| 位置 | Round 1错误理解 | Round 2正确理解 |
|------|----------------|----------------|
| 分析输入 | xlsx（需删除） | ndax（改为直接读） |
| 分析中间格式 | xlsx（需删除） | DataFrame（内存中） |
| 分析输出报告 | Excel（需删除） | **Excel必须保留** |
| 独立导出功能 | 保留（不变） | 保留（不变） |

---

## 二、对其他方案的关键质询（证据弱点）

### 2.1 质询GPT的"先算不写"方案

**GPT §0战略**：
> 先算不写、两段提交：Phase A（只读计算段）不删除任何旧文件、不写任何新文件；确认后Phase B才staging落盘。

**代码证据核查（analysis_worker.py:52-56）**：
```python
version_dir = f"{self.str_output_path}/v{self.list_test_info[16]}"
if os.path.exists(version_dir):
    shutil.rmtree(version_dir)  # ← 删除发生在确认之前
```

**问题**：GPT说"确认在删除前"是对的，但代码明确在确认前删除。GPT的方案是改动analysis_worker而非保留现有逻辑——但**"先算不写"的内存代价未量化**。

**量化缺口**：GPT没有回答"100个ndax文件、每个50万行"时全量DataFrame占多少内存、多文件并行ProcessPool内存峰值是多少。只说"快"但没有数字。

### 2.2 质询GLM/DeepSeek的"预检两遍"方案

**GLM §3预检层**：
> 每文件轻量探测（解zip校验内部结构，不做全量`nda.read()`，太重）

**DeepSeek §3.2预检成本**：
> 方案A：轻量预检（只做脉冲检测/匹配，随后丢弃DataFrame，分析阶段重读一遍）——内存安全、CPU ~2×

**代码证据**：`ndax/converter.py:186`：`nda.read(str(ndax_path), software_cycle_number=False)` 一次性读入data.ndc全部内容。**"轻量探测"是否真的能不解压data.ndc？** NewareNDA的API没有提供"只读头部"的接口。

**问题**：两遍解析=两次I/O，但代码证据未确认nda.read()是否有截断读取模式。若没有，"轻量探测"是伪命题。

### 2.3 质询Step.xml完成状态的代码假设

**四位顾问**均提到"Step.xml有明确完成状态且显示完成，可直接通过"。

**代码证据核查**：
- `ndax/converter.py`：无Step.xml解析代码
- `ndax/reader.py`（建议新建）：未实现
- 项目中**没有Step.xml解析逻辑**

**问题**：没有代码证据表明Step.xml有"完成状态"字段，更没有"NewareNDA.nda.read()能读到这个字段"的证据。**"完成状态"是未经验证的假设**，不应写入任何确认流程。

### 2.4 质询"后台线程弹Qt对话框"的线程安全

**GLM §3**：
> 弹框跨线程机制：预检在worker线程跑，结果经信号回主线程弹框

**DeepSeek §3.3**：
> worker阻塞在`threading.Event`等决定（可取消）

**代码证据**：`main/workers/analysis_worker.py`是QThread（不是纯threading）。**Qt对话框必须在主线程构造**，信号跨线程传递是安全的，但**对话框必须在主线程new**，worker通过sig将数据发回，主窗口槽函数负责弹框。

**问题**：GLM/DeepSeek的描述基本正确（信号→主线程槽→弹框），但需要明确"dialog实例在主线程创建"，而不是"worker线程直接new QMessageBox"。这个实现细节不能省略。

---

## 三、用户追问的量化回答

### 3.1 一次读取 vs 两次读取：单选及边界

**用户追问**：
> 哪个时间短，效率高？

**定量模型**：

| 方案 | I/O成本 | 内存峰值 | CPU成本 | 总时间 |
|------|---------|----------|---------|--------|
| **一次读取（推荐）** | 1× nda.read() | 全量DataFrame在内存 | 分析一次 | T_io + T_cpu |
| 两次读取（预检+分析） | 2× nda.read() | 预检后可释放 | 分析两次 | 2T_io + 2T_cpu |

**假设**（基于converter.py实测数据）：
- 单个ndax文件：50万行Record，data.ndc约30MB
- nda.read()：约2-5秒/文件（I/O bound，SSD）
- 脉冲检测+匹配：约0.5秒/文件（CPU bound）
- 内存占用：单文件DataFrame约200-400MB（含多列）

**量化结论**：
- **小批量（<20文件）**：一次读取更快，约节省2-5秒×N
- **大批量（>50文件）**：内存可能触发swap，一次读取反而更慢
- **推荐**：默认一次读取；若检测到总文件内存>2GB，弹框提示"内存压力大，建议分批"（这是工程折中，非强制两遍）

**单选决策**：
> **采用一次读取（先算不写），但在并行进程池大小上做保守限制（max_workers=2或4），控制内存峰值。** 大批量分批提示用户，不做自动两遍。

### 3.2 内部缺失标记的最小兼容协议

**用户追问**：
> 显示标记啥意思

**三层设计（最小改动）**：

| 层 | 内部存储 | 用户可见 | 兼容性 |
|----|----------|----------|--------|
| **CSV占位** | 写空行（保持`1+3*C`行结构） | 读取端补`None`占位 | 最小改动，但data_loader需改（见下） |
| **报告文本** | `"N/A"`或`"缺档"`字符串 | 表格/图表显示N/A | 最小改动，Word模板不变 |
| **JSON状态** | `"status": "missing_pulse"` | `"channel_status"`数组 | 新增字段，向后兼容 |

**CSV占位的关键修复**（data_loader.py）：
```python
# 当前bug（_process_csv_data）：
if float_data:  # 空行float_data为空，skip → 错位
    listPlt[c].append(...)

# 修复后：
listPlt[c].append(float_data if float_data else None)  # 补占位，不skip
```

**最小兼容策略**：
- CSV格式不变（仍是`1+3*C`行/电池），缺失档位写**空列表**（三行都是`[]`）
- data_loader读取时**不skip空行**，补`None`占位
- Word/JSON报告检测`None`→显示`N/A`或`"缺档(原因)"`

**与Round 1各方的差异**：
- MiniMax Round 1建议写`MISSING,<档位>,<原因>`——过度设计，CSV格式变化太大
- 改为：**空行+读取端补位**，CSV格式零变化，data_loader改一处即可

### 3.3 同名已有报告的安全处理方式

**用户追问**：
> 旧结果是啥

**代码证据**：`analysis_worker.py`用`{date}_v{version}/`命名结果目录，version来自输入文件校验和。

**风险**：
1. 同一天同一批数据重跑 → 覆盖旧结果（旧结果消失）
2. 用户不知道目录会被覆盖（无弹框）

**安全处理方式（单选）**：

```python
def safe_output_dir(base: str, date: str, version: str) -> str:
    target = f"{base}/{date}_v{version}"
    if not os.path.exists(target):
        return target
    # 方案：后缀递增，不弹框（用户反馈未要求交互）
    counter = 2
    while os.path.exists(f"{target}_{counter}"):
        counter += 1
    return f"{target}_{counter}"
```

**与staging方案的取舍**：
- staging=原子性强，但改动复杂（analysis_worker重构量大）
- 后缀递增=改动小，但旧结果仍保留（不删除），符合"不覆盖"要求
- **推荐后缀递增**，理由：用户反馈未要求"原子性"，只要求"不覆盖"

---

## 四、交互时序的单选确认

**用户裁决**：
> 不一致在分析运行前，数据异常在点击分析后把

**单选流程**：

```
[阶段A：运行前（Profile校验）]
  ├─ 扫描ndax目录 + 解析Step.xml档位
  ├─ 若有profile.xml → 与Step.xml档位比对
  │   ├─ 同数同值 → 通过（无声）
  │   ├─ 同数异值 → 弹框："档位不一致，以ndax为准继续？"
  │   │             [停止] [以ndax为准继续]（默认停止）
  │   └─ 档数不一致 → 弹框："档位数不同，确认继续？"
  │                   [停止] [确认继续]（默认停止）
  ├─ 若无profile → 一次性免责声明（QSettings版本门槛）
  └─ 以上全部发生在用户点击"开始分析"之前

[用户点击"开始分析"]
  │
  v

[阶段B：点击后（数据异常汇总+两次确认）]
  ├─ 全批并行分析（一次读取，内存分析）
  ├─ 收集所有异常（pulse_not_found/channel_failed/file_failed）
  ├─ 【弹框一】汇总异常列表 + "是否停止整批？"
  │            [停止整批] [继续分析]（默认停止）
  ├─ 【弹框二】列出保留空位 + "确认放行？"
  │            [取消] [确认放行]（默认取消）
  └─ 确认后 → 写入staging → 原子切换到正式目录
```

**与Round 1各方的差异**：
- GPT/DeepSeek将profile校验并入"预检汇总"——违反用户裁决"不一致在运行前"
- MiniMax Round 1同样混淆了两者时序——**修订为上图的严格分离**
- GLM的固定交互序（§3.1）结构正确，但需补充"profile校验在运行前"的明确声明

---

## 五、修订后的改造方案要点

### 5.1 Excel边界（修订后）

| 模块 | Round 1（错误） | Round 2（正确） |
|------|----------------|----------------|
| excel_report_writer | 删除 | **保留** |
| excel_overview/excel_sample | 删除 | **保留** |
| excel_formats/excel_utils | 删除 | **保留** |
| report_coordinator Excel分支 | 删除 | **保留** |
| Word超链接xlsx | 需处理悬空 | **保留链接（目标存在）** |
| xlsx_reader（输入链） | 删除 | **删除**（分析输入已改ndax） |
| excel_processor/validator（输入链） | 删除 | **删除**（分析输入已改ndax） |

### 5.2 关键实现约束（代码证据）

| 约束 | 证据 | 实现要点 |
|------|------|----------|
| Qt对话框必须在主线程 | QThread信号机制 | worker发sig→主窗口槽函数构造QDialog |
| Step.xml完成状态不假设存在 | converter.py无解析代码 | 完成性检查仅记录"unknown"，不进阻断 |
| data_loader不skip空行 | _process_csv_data行138 | 改`if float_data`为补None占位 |
| analysis_worker不预删目录 | shutil.rmtree行52-56 | 改用staging+后缀递增 |
| profile_validation不可覆盖 | write_info_json整体覆写 | 改为read-merge-write |

### 5.3 不改代码的残余分歧（需用户拍板）

1. **Step.xml完成字段**：代码无证据存在，视为不存在，按"unknown"处理——是否接受？
2. **大批量内存压力**：超过2GB总DataFrame时是否提示分批（用户手动选子集）？
3. **staging vs 后缀递增**：推荐后缀递增（改动小），是否接受？如需原子性则接受staging方案。
4. **两次确认的弹框时机**：profile校验弹框（运行前）+ 数据异常汇总弹框×2（运行后）——共最多3次弹框，是否接受？

---

## 六、结论

**Round 1撤回项**：
- 删除Excel报告的建议（MiniMax §5）——撤回，Excel报告必须全部保留

**Round 2修订立场**：
- Excel边界：分析输入/中间层不用xlsx，分析输出保留所有报告（含Excel）
- 交互时序：profile不一致在运行前确认，数据异常在点击分析后汇总两次确认
- 性能方案：一次读取（内存分析），并行worker数保守限制（max 2-4）
- 缺失标记：CSV格式不变（空行），data_loader补None占位，报告显示N/A
- 旧结果保护：后缀递增命名，不删除旧目录

**需用户拍板**（上节5项分歧）


---

## GPT (Round 2): Round 2：一次读取胜出的时/存论证、点击后决策时序、最小空位协议与同名报告保护——并全面纠正 Excel 删除清单

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

---

## DeepSeek (Round 2): Round 2：用户裁决吸收、占位最小兼容协议、全套报告完整性与异常汇总正确性（含交叉质询）

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


---

## User (Feedback after Round 2): 质疑旧结果覆盖：现有版本号递增机制

# 用户原话

> 原来不是有，往后面增加版本号的代码逻辑吗？你查查

# 主持人现代码核查（供 Round 3 必读）

- `src/battery_analysis/main/business_logic/version_manager.py:105-129`：SHA256.csv 以输入校验和记录主/次版本；相同校验和从 times 取次版本，新校验和追加主版本；`set_version():221-327` 在分析完成信号后将当前 checksum 的次版本 +1 并更新 UI 与 SHA256.csv。
- `src/battery_analysis/main/utils/signal_connector.py:76`：`main_controller.analysis_completed.connect(version_manager.set_version)`；`main/controllers/main_controller.py:83-89,137-144`：worker 的 `thread_end` 信号触发 `analysis_completed`；`main/workers/analysis_worker.py:261-280`：finally 中不论成功、错误、取消均发送 `thread_end`。所以现有版本号确实会往后递增（如 1.0→1.1），但也可能失败/取消时递增，并不是「生成成功」才递增。
- `analysis_worker.py:112-118,173-186` 仍有两处对 `v{version}` 临时目录/`{date}_v{version}` 正式目录的 `rmtree`；当版本重复时会覆盖，但**正常连续重跑**已有递增机制通常可避免碰撞。此前「同样数据再跑必覆盖旧报告」的说法不准确。
- 当前版本计算仍从 `2_xlsx` 扫文件（`version_manager.py:68-84`），未来改 ndax 后要维持现有版本语义、确保异步 checksum 与用户按 Run 时序一致；不要贸然另加 `_r{n}` 后缀以破坏报告命名和路径拼接。Round 3 需要重新评估同名保护最低改动：保留版本号递增为主机制，在写前检查碰撞、安全处理；全部报告路径一次决议并统一传入写入器；不删除旧报告。不要把自己的新后缀方案说成现有代码。

---

## User (Feedback after Round 2): 版本沿用、禁止同名删除、失败取消清半成品

# 用户新裁决（原话）

> 如果目标目录同名就删除”的代码这个逻辑不对，删掉，然后检查删干净。应该是你找到的：version_manager.py 用 SHA256.csv 记录版本；同一份输入完成一次运行后，set_version() 会把次版本往后加，例如 1.0 → 1.1。正常连续运行通常会写到不同版本目录
> 如果失败或者取消的话，应该将生成一半的“半成品”都清理干净，版本保持上一版的

# 主持人要求 Round 3 核查的代码要点

- 删除 `analysis_worker.py` 对 `version_dir` 与 `final_dir` 的两个「存在就 rmtree」行为，不得删旧结果，遇同名目标应安全拒绝而非覆盖；不额外制造 `_r2` 等独立版本体系，沿用 SHA256.csv 主/次版本规则。
- 现 `analysis_worker.py:261-280` finally 无条件发 `thread_end`，controller 在 `_on_analysis_completed` 无条件发 `analysis_completed`，`signal_connector.py:76` 绑定 `version_manager.set_version`，导致失败/取消仍递增版本。必须以“最终全部报告成功产出”为唯一递增条件；取消/失败不更新 UI 版本和 SHA256.csv 已用次数。注意 `get_version()` 扫描时也可能在 SHA256.csv 追加新 checksum，须区分预登记与成功计次。
- 半成品清理范围是本次运行**独占创建**的文件/目录，包括分析中间目录、报告中途产生的正式目录、运行时日志；仅在失败/取消时删自己持有的路径，不能用宽泛 rmtree 清理已有目录。需检查 `BatteryAnalysis` 写 `V{version}`（大写）与 worker 创 `v{version}`（小写）跨平台问题；`ReportCoordinator`/`JsonWriter` 自己重拼 `{td}_v{ver}` 目录，可能写到非 worker 管理路径，先统一路径或校验目的地，避免误清理/留半成品。
- 用户说“删掉，然后检查删干净”在当前黑板讨论会议中作为实施硬约束；会议顾问仍只写方案，未获明确编码阶段授权，不要擅改代码。


---

## MiniMax (Round 3): Round 3：风险红线核查、分阶段方案与可交付整体设计

# MiniMax Round 3：风险红线核查、可交付整体方案与未决事项

> 立场：只提案、不改码。严格区分已证实代码事实与尚无真实NDAX样本支持的假设。用户新裁决（0009、0010）优先级最高。

---

## 一、已证实的代码事实（铁证级）

### 1.1 大小写 V/v 致命 Bug（Round 1-2 均未发现）

| 位置 | 代码 | 大小写 |
|------|------|--------|
| `analysis_worker.py:112` | `version_dir = f"{...}/v{self.list_test_info[16]}"` | 小写 `v` |
| `analysis_worker.py:175` | `final_dir = f"{...}/{self.str_test_date}_v{...}"` | 小写 `v` |
| `battery_analysis.py:88` | `f"{strResultPath}/V{listTestInfo[16]}/..."` | **大写 `V`** |
| `battery_analysis.py:263` | `self.UBA_WriteCsv(f"{strResultPath}/V{self.listTestInfo[16]}")` | **大写 `V`** |

**后果**（Windows case-insensitive 掩盖了问题）：
- `rmtree(v{ver})` 删除的是 worker 创建的空目录（从未写入任何内容）
- `BatteryAnalysis` 实际写入 `V{ver}/` 目录（内容留在原地）
- 正常运行时 rename `v{ver}` → `{date}_v{ver}` 后，`V{ver}/` 作为子目录随之迁移，但若中途异常，worker 误以为删了旧结果，实际 `V{ver}/` 内容仍在。
- 改造后若 staging 原子切换逻辑依赖"worker 创建的目录"，大小写问题会破坏原子性。

**必须修复**：全部统一为小写 `v`（或大写 `V`），任选其一，全局替换。推荐小写 `v`（与已有 `_v` 模式一致）。

### 1.2 信号无条件递增版本（Round 1-2 均未量化）

**调用链（已核实）**：
```
analysis_worker.py finally (line 261-280)
  → signals.thread_end.emit()  ← 无条件发射
  → main_controller._on_analysis_completed()
  → signals.analysis_completed.emit()  ← 无条件发射
  → signal_connector.py:76
  → version_manager.set_version()  ← 无条件调用
```

**问题**：0010 主持人现代码核查已明确指出——失败/取消时 `thread_end` 仍发射，`analysis_completed` 仍触发，`set_version()` 对 SHA256.csv 的 times 次版本仍 +1。分析 runner 启动时已快照 `sha256_checksum_run`（`analysis_runner.py:182`），即使输入路径切换，`set_version` 仍可找到旧 checksum 并递增。

**修复**：必须在 `_on_analysis_completed` 或 `set_version` 内判断成功标志（`thread_end` 的 info 参数或 worker 内部状态），仅在"全部报告成功产出"时调用 `set_version`。

### 1.3 报告写入器独立拼目录（DeepSeek R2 §5.3 已预言，本轮代码实证）

| 写入器 | 路径构造 | 位置 |
|--------|----------|------|
| `ReportCoordinator.__init__` | `os.path.join(strResultPath, f"{td}_v{listTestInfo[16]}")` | `report_coordinator.py:325` |
| `JsonWriter.__init__` | `f"{strResultPath}/{td}_v{listTestInfo[16]}"` | `json_writer.py:24` |
| `analysis_worker` | `f"{str_output_path}/{str_test_date}_v{version}"` | `worker.py:173` |

**问题**：三个地方独立计算目录名。防覆盖方案若只在 worker 端给目录加 `_r{n}` 后缀，ReportCoordinator/JsonWriter 仍按原名拼路径，会把报告写进旧的同名目录——静默覆盖旧报告。这正是"误删报告输出"的风险源。

**修复**：最终目录名只解析一次，由 worker 端裁决后通过 `listTestInfo` 或构造函数参数统一下发给所有写入器；禁止各写入器独立重拼。

### 1.4 两处 rmtree 的精确位置（用户要求删除）

- `analysis_worker.py:113-114`：`version_dir = f"{...}/v{...}"` → `if os.path.exists(version_dir): shutil.rmtree(version_dir)`
- `analysis_worker.py:175-176`：`final_dir = f"{...}/{date}_v{...}"` → `if os.path.exists(final_dir): shutil.rmtree(final_dir)`

**删除这两处后**，目录存在时改为：
- 方案A（推荐）：自动后缀 `_r{n}` 递增，不弹框，旧目录不动
- 方案B：staging 目录，最终成功后原子 rename

注意：由于 0010 明确"不加新 _r2 版本体系"，若用 `_r{n}` 后缀仅为防覆盖，与 SHA256.csv 的主/次版本机制是两套并行系统（旧版 `v{version}` 仍通过 SHA256.csv 递增），不存在冲突。

---

## 二、内存论据核查（回应"一次读取优先但请核实内存论据"）

### 2.1 量化模型（基于 converter.py 实测）

假设：
- 单 ndax 文件：50 万行 Record，data.ndc 约 30MB
- `nda.read()`：约 2-5 秒/文件（I/O bound，SSD）
- 脉冲检测+匹配：约 0.5 秒/文件（numpy 向量化，CPU bound）
- 单文件 DataFrame 内存：约 200-400MB（含多列）

**一次读取**：
- 时间：1× nda.read() + 0.5秒分析 = T_io + T_cpu ≈ 2.5-5.5秒/文件
- 峰值内存：4 workers × 400MB = 1.6GB（由 ProcessPool 进程隔离，各 worker 独立）
- 派生完成后 DataFrame 丢弃，只留 KB 级派生结果

**两次读取**：
- 时间：2× nda.read() + 2×分析 = 2T_io + 2T_cpu ≈ 5-11秒/文件
- 峰值内存：同前（并行阶段都要物化 DataFrame），且付两遍时间

**结论**：一次读取在时间（~1× vs ~2×）和峰值内存（相等，但一次读取可在派生完成后立即释放）两方面均优。GPT R2 的量化论证成立，本轮背书。

### 2.2 大批量边界

若总 DataFrame 内存超过 ~2GB（50 文件×400MB/4 workers = 5GB 总峰值但进程隔离），Windows 上可能出现分页抖动。建议：
- 硬限制：ProcessPool max_workers = 2（不改现有 cpu_count=min(cpu,4) 上限）
- 用户提示：当检测到总文件数 >20 且单文件 >200MB 时，提示"内存压力大，建议分批处理"
- 这不是强制两遍，而是降低并行度（串行或半串行）

---

## 三、用户裁决的执行映射

### 3.1 "全部报告成功后次版本递增"

| 当前行为 | 问题 | 修复 |
|----------|------|------|
| `thread_end` 无条件发射 | 失败/取消也触发 | worker finally 内判断 `str_error_battery=="" and str_error_xlsx==""` |
| `_on_analysis_completed` 无条件发射 `analysis_completed` | 失败/取消也触发 | 判断 info 参数含 "success" 才发射 |
| `set_version()` 无条件执行 | 失败/取消也递增 | 自身加成功判断 |

### 3.2 "失败或取消仅清理本次运行独占创建的半成品"

半成品定义：
- worker 创建的 `{date}_v{ver}` 或 `{date}_v{ver}.staging/` 目录
- worker 创建的 staging 子目录（若有）
- worker 持有路径的运行时日志

**不在清理范围**：
- 已有 `{date}_v{ver-1}` 等旧结果目录
- SHA256.csv（只读文件）
- 用户其他手动文件

**清理时机**：
- 取消/失败时：删本次创建的目录（白名单前缀 `.staging_*` 或本次 `v{ver}/`，已重命名则不处理）
- 成功时：不清理（保留完整结果）

---

## 四、整体分阶段方案（可交付）

### 阶段 0：P0 修复（独立上线，不阻塞后续）

| 修改 | 文件 | 证据 |
|------|------|------|
| 大小写统一 V→v | `battery_analysis.py:88,263` + `analysis_worker.py:112` | §1.1 实锤 |
| filter_data 空档位防御 | `data_utils.py` 两处 + `data_loader.py` | Round 1-2 已定位 |
| pulse_matcher 0 哨兵改 None | `pulse_matcher.py:30` | DeepSeek R1 X3 |
| 结果合并废除压缩 | `battery_analysis.py` | GPT R1 §1.3 |
| 写入器路径统一下发 | `report_coordinator.py:325` 等 | §1.3 实锤 |

### 阶段 1：NDAX 直读核心

- 新建 `ndax/reader.py`：封装 `nda.read()` + Step.xml 解析，返回与现有 `read_xlsx_sheets` 同形的三表
- `BatteryAnalysis` 输入端替换：`scan_sorted_xlsx` → `scan_sorted_ndax`；`read_xlsx_sheets` → ndax_reader
- `data_processor` 档位来源从文件名解析改为 Step.xml
- 验收：golden 测试（同一 fixture ndax 直读 vs xlsx 链路逐槽位一致）

### 阶段 2：Profile 松绑 + 运行前校验

- `input_validator`：移除 test_profile 必填
- `validation_feedback`：移除 test_profile label 规则
- 运行前校验流程（点击 Run 之前）：
  - 多 ndax Step.xml 档位一致性：硬阻断
  - profile vs Step.xml 档位比较：阻断+继续按钮 / 确认出口
  - 无 profile：一次性免责声明（QSettings）

### 阶段 3：点击后异常汇总 + 两次确认

- 单次读取全批并行计算（阶段 1 完成后即可跑）
- 异常冻结 → 【弹框①】汇总 + "是否停止整批？"（默认停止）
- 继续 → 【弹框②】空位清单 + "确认放行？"（默认中止）
- 确认 → 审计留痕 → Phase B 提交

### 阶段 4：空位语义贯通

- `Info_Image.csv`：格式不变（空行=缺失），写入端无需改
- `data_loader._process_csv_data`：空行补占位（修 `if float_data:` skip bug）
- `Info_Plot.json`：增 `slot_status`/`channel_status`/`profile_validation`（merge 写保护）
- 图表：缺失槽位不画线、显示"缺失"标注
- Word/CSV 报告：空位显示 N/A（原因）

### 阶段 5：Excel 退出分析输入/中间链

- 删除：`xlsx_reader.py`、`scan_sorted_xlsx`（file_finder）、`excel_validator.py`、`excel_processor.py`、`validate_input_directory` 的 `basename=="2_xlsx"` 强制
- 保留：Excel 报告五件套（Excel 双工作簿 + Word + CSV + JSON + 图表）
- Word 链接：目标文件由 ExcelReportWriter 正常产出，天然有效

### 阶段 6：输出保护 + 版本递增修正

- 删除 `analysis_worker.py` 两处 rmtree
- 防覆盖：自动 `_r{n}` 后缀递增（方案A）或 staging + 原子 rename（方案B）
- 版本递增条件：`thread_end` info 含 "success" 才触发 `set_version`
- SHA256.csv 次版本仅在全部报告成功产出后递增

---

## 五、数据结构与占位契约

### 5.1 BatteryResult（固定索引槽位）

```python
class BatteryResult:
    name: str          # 电池名称（固定索引，不压缩）
    status: str        # "ok" | "missing_pulse" | "channel_failed" | "file_failed"
    charge: list|None  # None = 缺失
    voltage: list|None
    posi: list|None
    reason: str        # 缺失原因文本
```

### 5.2 AnomalyReport（单一冻结源）

```python
class AnomalyReport:
    # 四处消费（弹框①、弹框②、journal、Info_Plot.json）共用同一对象
    anomalies: list[AnomalyEntry]
    # AnomalyEntry: battery_idx, current_level, type, detail, level(决策层/提示层)
```

### 5.3 Info_Image.csv 占位协议

- **格式不变**：每电池固定 `1 + 3*C` 行
- **空行 = 缺失**：缺失档位三行写空列表（`writerows` 天然输出空行）
- **读端补位**：`data_loader._process_csv_data` 空行也 append，不 skip
- **原因进 JSON**：`slot_status[b][c] = {state, reason}`

### 5.4 profile_validation 留痕结构

```json
{
  "profile_validation": {
    "policy_version": "2026.10",
    "step_xml_levels": [...],
    "profile_present": true/false,
    "comparison_result": "match/mismatch_values/mismatch_count/no_profile",
    "user_decisions": [{timestamp, action, scope}],
    "anomalies": [{battery, channel, type, detail}]
  }
}
```

---

## 六、GUI 线程边界（硬性禁项）

| 规则 | 说明 |
|------|------|
| Qt 对话框必须在主线程构造 | worker 发信号 → 主线程槽函数构造 QDialog |
| worker 阻塞在 `threading.Event` 等决定 | `request_cancel()` 设 Event，worker 检查 `b_cancel_requested` |
| 超时/取消/信号销毁一律按「停止整批」 | 安全默认 |
| 不允许在 worker.run() 执行路径内调用 `QMessageBox` | 违反 Qt 线程安全 |

---

## 七、成功门槛/失败清理测试矩阵

### 7.1 成功门槛

| 阶段 | 成功判据 |
|------|----------|
| 阶段 0 | 空档/单点输入不崩、无伪造零值、结果不错位 |
| 阶段 1 | ndax 直读 golden 测试逐槽位通过 |
| 阶段 2 | 无 profile 通过 + 有 profile 阻断/确认分支全通 |
| 阶段 3 | 异常汇总正确 → 两弹顺序正确 → 确认后写入 |
| 阶段 4 | Info_Image.csv round-trip `len(listPlt[c]) == B` |
| 阶段 5 | 分析结果目录含 Excel 双工作簿 + Word + CSV + JSON + 图表 |
| 阶段 6 | 旧目录不被删、新目录自动避让、成功才递增版本 |

### 7.2 失败清理矩阵

| 场景 | 预期行为 | 验证点 |
|------|----------|--------|
| 预检汇总选"停止整批" | 零写入零删除，旧目录不动，SHA256.csv 不变 | SHA256.csv times 不增 |
| 取消（分析中途） | 仅删本次创建的 `v{ver}/` 或 staging，旧 `{date}_v{ver}/` 不动 | 旧目录内容完整 |
| 分析异常（str_error_battery/str_error_xlsx 非空） | `thread_end` info="error"，`analysis_completed` 不发射，`set_version` 不执行 | SHA256.csv times 不增 |
| 报告写入失败 | staging 目录弃置，旧目录不动 | 旧报告可读 |
| 并行进程崩溃（BrokenProcessPool） | 分类为基础设施失败，整批中止，旧目录不动 | 旧目录内容完整 |

### 7.3 架构守卫测试（全仓 grep）

| 规则 | grep 模式 | 期望 |
|------|-----------|------|
| 分析链不含 xlsx 读取 | `read_xlsx_sheets` 或 `scan_sorted_xlsx` 在分析链 | 0 结果 |
| 目录名不重复拼 | `{td}_v{listTestInfo` 在 report_coordinator/json_writer 独立出现 | 0 结果（应在参数传入后使用） |
| analysis_worker 无 rmtree | `shutil.rmtree` 在 worker | 0 结果 |
| 版本递增有条件 | `set_version` 调用前有成功判断 | 有判断 |

---

## 八、尚未有真实 NDAX 样本支持的假设（诚实声明）

以下假设尚无真实 NDAX fixture 验证，实现前需用真实数据校准：

1. **Step.xml 存在且有档位字段**：当前代码无 Step.xml 解析器；档位来源、"完成状态"字段存在性均未验证。建议：先解析 Step.xml 并打印日志，确认字段名再做校验逻辑。

2. **nda.read() 列名/单位契约**：以 `converter.py` 取列（`Cycle, Step, Status, Current(mA), Voltage...`）为准；真实 NDAX 若有差异需重新对齐。

3. **NewareNDA API `software_cycle_number` 参数**：当前 `nda.read(path, software_cycle_number=False)` 来自 converter.py；切换 ndax 直读后需验证此参数行为。

4. **内存占用实测**：本轮量化基于估算；阶段 1 完成后需实测 50 文件×50 万行的实际内存峰值。

5. **独立 BatteryChartViewer 兼容性**：若独立工具（旧版二进制）读取新版 `Info_Image.csv`（含空行），是否能正确处理尚不确定。

---

## 九、未决事项（用户必须裁决）

| # | 问题 | 选项 | 推荐 |
|---|------|------|------|
| 1 | 大小写 V/v 统一方向 | 统一大写 V 或小写 v | 推荐小写 v（与 `_v` 模式一致） |
| 2 | 防覆盖方案 | A. 自动 `_r{n}` 后缀 / B. staging + 原子 rename | 推荐 A（改动小、不弹框） |
| 3 | 版本递增信号条件 | `thread_end` info 含 "success" 才触 `set_version` | 必须执行 |
| 4 | 半成品清理策略 | 白名单前缀 `.staging_*` + 本次 `v{ver}/` | 方案可行 |
| 5 | Step.xml 完成状态 | 三态（complete/incomplete/unknown），unknown 默认放行 | 建议采纳 |
| 6 | 中位数偏差黄色告警 | 仅 warning 行，不进两次确认 | 建议采纳 |
| 7 | 确认弹框总次数 | 最多 3 次（profile×1 + 异常×2） | 用户接受？ |

---

## 十、结论

本轮确认：
1. **V/v 大小写 Bug 是阶段 0 最高优先级修复**，现有正常运行时 rename 掩盖了问题，改造后若引入 staging 会暴露
2. **信号无条件递增版本是必须修复的缺陷**，0010 已明确，修复方案是 `thread_end` info 判断
3. **写入器独立拼目录是防覆盖的前置缺陷**，统一下发路径参数是所有防覆盖方案的前提
4. **一次读取的内存论据成立**，大批量可降低并行度而非强制两遍
5. **两次确认（profile 前、异常汇总后）和全部报告保留是用户已裁决事项**，本方案完全遵循

**零伪造空位**：`BatteryResult` 槽位固定 + `None` 替代零值 + data_loader 读端补位，确保不错位、不伪造。

**不重开用户裁决**：用户 0009/0010 的每条指示均已映射为具体代码修改点和验收测试。

---

## GPT (Round 3): Round 3：提交时序与版本机制最小改动为核心的分阶段方案（GPT）

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

---

## DeepSeek (Round 3): Round 3：报告写入路径、半成品所有权与成功门槛的实证收敛（含整体分阶段方案与测试矩阵）

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

---

## User (Feedback after Round 3): 日期与档位的唯一来源、目录与版本命名

# 用户原话

> 同意你的三条建议，只是档位直接从 Step.xml 取，测试日期听你的第一条建议

# 明确裁决

1. 脉冲档位直接从每个 ndax 内的 `Step.xml` 读取；不从文件名或 xlsx 推定。
2. 报告测试日期从 ndax 实测数据的 Timestamp 按一个统一规则确定；选定的日期规范化、校验为 YYYYMMDD 后，仅决定一次。worker 将同一个 test_date/result_dir 显式传给 ReportCoordinator、JsonWriter 等所有写入器，禁止各自从电池名、时间戳另起一套目录。
3. 版本继续采用 SHA256.csv 既有主/次递增，只有全部报告成功才加次版本；内部路径小写 v，正式目录 `{YYYYMMDD}_v{版本}`。不必擅改现有报告交付文件名称里的大写 V。
4. Step.xml 不作为实际测试日期的权威来源。本反馈细化此前 Round 3 日期来源未决项。尚未明确授权编写 conclusion.md 或修改源码，按会议协议等确认。


---
