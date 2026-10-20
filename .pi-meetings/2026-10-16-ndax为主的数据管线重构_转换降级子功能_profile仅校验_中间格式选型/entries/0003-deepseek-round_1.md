# DeepSeek (Round 1): 从数据流/模块契约/失败模式角度全面分析五问，指出档位来源切换是核心契约变更，中间格式应选内存DataFrame直传，filter_data越界必须兜底。

# DeepSeek Round 1 系统分析：数据流·模块契约·失败模式

---

## 一、逐条评估提案 A–D

### A. ndax 为主，降级为子功能

**合理性**：高。当前 ndax 是数据唯一权威来源（5 项目零例外验证），理应成为主入口。把 xlsx 转换降级为与 batteryChartViewer 同级的辅助工具，语义正确。

**风险**：
- **UI 入口重路由**：`ui_builder.py:53-55` 当前 `NdaxConverterTab` 是 Tab 0（主位）。降级需要改 `QTabWidget` 结构或改为按钮弹窗，涉及 `mw._ndax_tab` 引用链路（`ui_builder.py:65`）。需确认是否有其他模块通过 `mw._ndax_tab` 直接访问。
- **隐性依赖**：ndax_tab 内部的 `convert_batch` → `ProcessPoolExecutor` → `convert_one` 流程无变化，但主 UI 交互路径变了，原有"先转 xlsx 再点分析"的用户习惯需要引导。

**遗漏**：提案未提及 ndax 主入口的扫描逻辑——主分析 Tab（`battery_tab`）当前扫描 xlsx 文件，切换为 ndax 主入口后需要扫描 .ndax 文件，这是入口变更的连锁反应。

### B. 界面不再通过 xml profile 带出数据，改通过 ndax 识别

**合理性**：中高。ndax 的 `data.ndc` → DataFrame 包含 Status、Current、Voltage 等完整时序数据，足以支撑脉冲检测和等级匹配。

**风险——这是本次重构的核心契约变更**：
- **档位来源链路重塑**：当前 `data_processor.py:340-352` 的链路是 `文件名解析 → config 查表兜底 → 写入 config`。切换为 ndax 后，档位应从 `data.ndc` 的 Status=Pulse 行按电流值分组提取，替代文件名解析。这要求新增一个 `extract_pulse_levels_from_ndax(ndax_path)` 函数，并在 `data_processor` 中替换 `filename_parser.extract_pulse_current` 的调用。
- **下游 7 处读取 `pulseCurrents` 的位置全受影响**：
  1. `data_processor.py:349` → `mw.listCurrentLevel`
  2. `config_manager.py:34` → `BatteryConfig/PulseCurrent` 映射
  3. `data_loader.py:140` → `_get_pulse_current_level()` 读 config
  4. `battery_config_initialization_step.py:38` → 初始化
  5. `analysis_runner.py:155` → `_prepare_test_info`
  6. `report_coordinator.py:329` → 报告
  7. `quality_requirements.py:204` → 容量校验

  若档位从 ndax 实测提取，上述 1-7 的写入链路应统一为：ndax 提取 → 写入 config + `mw.listCurrentLevel`，下游读取端不需要改动（它们只关心 config 和 `mw.listCurrentLevel` 的值）。

**遗漏**：文件名仍需解析 SN、批次码、制造商等非档位信息。提案 B 说"通过 ndax 识别其他所有数据"，但 ndax 的 `TestInfo.xml` 不含制造商、批次码、规格型号——这些仍需从文件名或 UI 手动输入。需明确"重新识别"的边界。

### C. profile xml 仅做验证

**合理性**：高。profile 的 `<PulseData>` 与 ndax `Step.xml` 的 `<PulseData>` 经 41 个文件核验为良性序列化差异，仅做交叉验证是正确使用。

**风险**：
- **验证粒度**：仅比较脉冲电流档位集合（set 相等），还是逐一比较每个 pulse step 的电流值+持续时间？建议仅比较电流值集合（set），因为 profile 和 Step.xml 的工步编号/时序可能不同。
- **验证时机**：应在 ndax 档位提取完成后、进入分析流水线前执行。在 `data_processor` 中插入验证步骤。

### D. 中间格式选型

**合理性**：需要结合 B 的实施方案一并决策。详见下方五问二。

---

## 二、中间格式单选建议：**内存 DataFrame 直传**

### 多维度对比

| 维度 | xlsx | csv | parquet | 内存 DataFrame 直传 |
|------|------|-----|---------|-------------------|
| **效率** | 最差（xlsxwriter 写 + calamine 读，两次 I/O） | 中等（csv 快于 xlsx 但仍需磁盘往返） | 好（列式，但需额外依赖） | **最优**（零 I/O，Python 进程内直接传递） |
| **出错面** | 大（百万行拆表 Record_2/3、文件名行+表头行偏移、calamine 引擎兼容性） | 中（无拆表但仍有 header 行对齐问题） | 小 | **最小**（无序列化/反序列化，无格式歧义） |
| **可审计性** | 好（用户可打开 xlsx 检查） | 好 | 差（需专门工具） | 可通过新增"保存 xlsx"按钮按需导出 |
| **重复分析成本** | 低（已转 xlsx 可复用） | 低 | 低 | 需重新读 ndax（~秒级，可接受） |
| **改动量** | 零 | 小（改读取器） | 中（新依赖+读取器） | **中等**（核心改动在 `battery_analysis.py:277-386` 的 `_parallel_process_file`，当前从 xlsx 路径读取改为接收 DataFrame 参数） |

### 推荐理由

1. **消除最大失败源**：当前 `converter.py` 的 xlsxwriter 拆表逻辑（`_build_record_sheet` 63 行）和 `xlsx_reader.py` 的 read_xlsx_sheets 拼接逻辑（12-34 行）是维护负担最重的代码。百万行拆表→多表拼接是一对脆弱的映射关系，任何不对齐都会导致分析数据错位。内存直传彻底消除这段代码。

2. **converter.py 可大幅简化**：`convert_one` 当前写 Cycle/Step/Record 三张表，改为只返回 `(cycle_df, step_df, record_df)` 三个 DataFrame。用户需要 xlsx 时再调用 `_build_*_sheet` 按需导出。

3. **`read_xlsx_sheets` 成为可选路径**：保留作为兼容接口（用户手动打开已有 xlsx 时），但主路径变为 ndax → DataFrame 直传。

4. **改动范围可控**：
   - `converter.py`：`convert_one` 增加 `return_dfs=True` 模式
   - `battery_analysis.py`：`_parallel_process_file` 签名扩展为接受 DataFrame
   - 下游 `pulse_detector`、`pulse_matcher`、`charge_calculator` **不需要改动**（它们已经是 DataFrame → DataFrame 的纯函数）

---

## 三、"通过 ndax 识别其他所有数据"重新识别清单

### ndax 各子文件能提供什么

| 数据项 | Step.xml | TestInfo.xml | data.ndc | 原来源 | 能否替代 |
|--------|----------|-------------|----------|--------|---------|
| **脉冲电流档位** | `<PulseData>` 含真实电流值 | — | Status=Pulse 按 Current 分组 | 文件名解析 | ✅ **必须替代** |
| **测试开始时间** | — | `StartTime` 字段 | DataFrame Timestamp 首行 | xlsx Cycle 表首行 | ✅ |
| **SN / 设备信息** | — | `SN`、设备型号 | — | 无（从未提取） | ✅ 可新增 |
| **电流量程** | — | `CurrentRange` | — | 无 | ✅ 可用于校验 |
| **电池名 / 文件名** | — | — | — | **xlsx 文件名（行 0）** | ❌ ndax 文件名可能不含足够信息 |
| **制造商** | — | — | — | 文件名正则提取 | ❌ ndax 不含 |
| **批次码 / BatchDateCode** | — | — | — | 文件名正则提取 | ❌ ndax 不含 |
| **规格型号 (Specification Type)** | — | — | — | 文件名正则 + UI 选择 | ❌ ndax 不含 |
| **规格方法 (1S1P/1S2P)** | — | — | — | 文件名正则 | ❌ ndax 不含 |
| **构造方法 (Coin/Pouch)** | — | — | — | 文件名推断 + UI | ❌ ndax 不含 |
| **CC 恒流电流** | — | — | — | 文件名正则 | ❌ ndax 不含 |
| **测试日期** | — | `StartTime` 或 Cycle 首行 | — | xlsx 搜索 "Test Date" | ⚠️ 部分（ndax 有时间戳但格式不同） |
| **截止电压档位** | `<Limit>` 含截止条件 | — | — | config 固定值 | ⚠️ 可提取但无需（config 已固定） |

### 关键结论

- **能完整替代的**：脉冲电流档位（核心）、测试时间、设备信息
- **不能替代的**：制造商、批次码、规格型号/方法、构造方法——这些仍需从文件名解析或 UI 手动输入
- **实施方案**：ndax 入口下，`data_processor` 的识别链路变为：`ndax data.ndc 提取档位（权威） → 文件名解析剩余字段（兜底） → UI 手动补充 → profile xml 交叉验证`

---

## 四、profile 验证策略边界情况

### 4.1 不一致报错 vs 告警放行

**强烈建议：报错阻断，不允许放行。**

理由：
- 背景事实 3 证明 profile 与 ndax 一致性是可验证的，不一致意味着用了错误模板（如 CF224642T 崩溃案例）
- 档位错误会导致 `match_pulse_levels` 匹配不到数据 → 下游全部计算结果错误 → 报告无意义
- 如果放行，用户可能在不知情下生成错误报告，后果远大于中断流程

实现：验证失败时弹 `QMessageBox.Critical`，显示 `profile 档位: [x, y, z] ≠ ndax 实测: [a, b, c, d]`，提供"查看详情"和"关闭"按钮。不提供"忽略继续"按钮。

### 4.2 无 xml 弹框声明一次够不够

**不够，需要分两层处理**：

1. **首次无 xml**：弹 `QMessageBox.Information`，说明"未找到 profile xml，将完全依赖 ndax 数据分析"，提供"确定"和"选择 xml 文件"两个按钮。声明一次后记入该批分析的日志。
2. **批次级记忆**：同一目录下所有文件共享同一个分析批次，弹框一次合理。但应将"无 xml 警告"写入 `Info_Plot.json` 的 metadata 字段，使报告可追溯。
3. **不应静默跳过**：即使用户上次选了"确定"，下次新批次仍应弹框（新数据可能有新风险）。

### 4.3 多 ndax 文件间档位不一致

**这是提案未覆盖的关键场景**。

同一分析批次（同目录）的所有 ndax 文件理论上应使用相同测试配方。如果文件 A 实测 `[60, 30, 15, 6]`、文件 B 实测 `[100, 60, 30, 15, 6]`，说明：
- 可能是不同型号/容量的电池混放在同一批次
- 可能是测试设备配置变更

**处理策略**：
1. **预扫描阶段**：在 `convert_batch` 或新增的 `scan_ndax_batch` 中，先遍历所有 ndax 的 data.ndc 提取各自档位集合
2. **一致性校验**：档位集合不一致时，弹对话框列出差异，提供选项：
   - "以多数文件的档位为准"
   - "选择一个文件的档位"
   - "取消分析"
3. **运行时防御**：即使预扫描通过，`match_pulse_levels` 对每个文件独立匹配——如果某文件的某个档位无匹配数据，结果应为该档位数据缺失（留空），而非崩溃

---

## 五、报告阶段空档位防御（filter_data 越界）是否仍需兜底

**必须兜底，即使档位来源已修正。**

### 理由

1. **崩溃机制**：`data_utils.py:42` 的 `filtered_mask[0] = True` 在 `charge_np` 为空数组时 IndexError。当前触发条件是档位不匹配导致 `match_pulse_levels` 返回空的 position 列表 → `ChargeCalculator.calculate` 收到空输入 → 生成空数据传递给 `filter_data`。

2. **即使 ndax 实测提取了正确档位，仍存在空数据场景**：
   - 测试中途断电，某个档位的脉冲未完成（数据不全）
   - 数据采集异常，某个档位的脉冲行缺失
   - 文件损坏，`data.ndc` 部分可解析
   - 用户手动指定了错误档位（override 场景）

3. **防御是分层的**，应修三层：

   | 层级 | 位置 | 修复 |
   |------|------|------|
   | **L1 数据源** | `match_pulse_levels` 返回结构 | 已有：空数据返回 None，调用方 `battery_analysis.py:322` 检查 `pulse_mask.sum()==0` |
   | **L2 中间处理** | `ChargeCalculator.calculate` + 空数据传递 | **需补**：calculate 收到空 position 列表时返回空列表，不传给 filter_data |
   | **L3 终端过滤** | `data_utils.py:42` | **必须修**：`filtered_mask[0] = True` 前加 `if len(charge_np) == 0: return [], []` |

4. **这是独立于本次重构的安全修复**：无论档位来源如何改变，`filter_data` 的空数组防御都不应依赖上游保证。作为防御性编程的基本要求，应在本次重构中一并修复。

### 具体修复建议

`data_utils.py` 的 `filter_data` 函数中，每个内层循环的 `charge_np` 和 `voltage_np` 为空时应提前 continue：

```python
# data_utils.py filter_data 内层循环
for charge_data, voltage_data in zip(plt_charge_list, plt_voltage_list):
    if not charge_data or len(charge_data) == 0:
        plt_charge_filtered.append([])
        plt_voltage_filtered.append([])
        continue
    # ... existing logic
```

---

## 六、整体风险矩阵与建议优先级

| 风险 | 影响 | 概率 | 优先级 |
|------|------|------|--------|
| 档位来源切换导致下游 7 处读取不一致 | 崩溃/错误报告 | 中 | **P0** |
| 多 ndax 间档位不一致未处理 | 错误报告 | 中 | **P0** |
| filter_data 空数组越界未修 | 崩溃 | 高（已复现） | **P0** |
| 中间格式改动影响现有 read_xlsx_sheets 兼容性 | 崩溃 | 低 | P1 |
| UI 入口重路由影响用户习惯 | 体验退化 | 高 | P2 |
| profile xml 验证逻辑实现复杂度 | 延期 | 低 | P2 |

**建议实施顺序**：P0 filter_data 兜底 → P0 ndax 档位提取 + 多文件一致性 → P1 内存 DataFrame 直传 → P2 UI 重构 → P2 profile 验证。