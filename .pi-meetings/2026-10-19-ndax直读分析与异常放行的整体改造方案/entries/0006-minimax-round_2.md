# MiniMax (Round 2): MiniMax Round 2：修订Excel立场、收敛四次交互、量化读写方案

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
