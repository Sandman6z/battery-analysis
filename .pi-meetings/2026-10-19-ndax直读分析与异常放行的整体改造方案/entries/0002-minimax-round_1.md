# MiniMax (Round 1): NDAX直读整体改造方案 Round 1 顾问意见

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