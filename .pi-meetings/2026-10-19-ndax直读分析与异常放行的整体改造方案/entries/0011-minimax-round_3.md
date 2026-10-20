# MiniMax (Round 3): Round 3：风险红线核查、分阶段方案与可交付整体设计

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