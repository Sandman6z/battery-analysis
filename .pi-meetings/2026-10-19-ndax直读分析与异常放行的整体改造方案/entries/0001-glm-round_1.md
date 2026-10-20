# GLM (Round 1): NDAX直读与异常放行改造：分阶段落地方案、删改边界与staging防覆盖机制

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
