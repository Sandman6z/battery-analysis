# DeepSeek (Round 1): 从数据流/模块契约/失败模式角度全面分析五问，指出档位来源切换是核心契约变更，中间格式应选内存DataFrame直传，filter_data越界必须兜底。

# DeepSeek Round 1 系统分析

## 一、核心数据流与模块契约地图

当前管线的档位（pulse currents）数据流如下，这是本次重构的核心契约链：

```
文件名 extract_pulse_current()
        │
        ├─ 有值 ──→ _verify_pulse_currents() 双重校验 ←─ config 查表 lookup_pulse_currents()
        │                    │
        └─ 无值 ──→ 查表兜底 ──→ normalize_current_levels()
                                        │
                                        ▼
                    mw.listCurrentLevel ← 存入 → config.set("battery.pulseCurrents", ...)
                                        │
                                        ▼
                    data_processor.py: listTestInfo[14] = listCurrentLevel
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
            battery_analysis.py   info_csv_writer.py   Info_Plot.json
            (pulse_matcher匹配    (Info_Image.csv      (下游BatteryChartViewer
             档位到数据行)         写入posi/charge/voltage) 读取元数据)
```

关键依赖：**listCurrentLevel 是整条管线的单一真相来源**。一旦档位错误，下游全部级联失败——不是优雅降级，而是 IndexError 崩溃（data_utils.py:42 `filtered_mask[0]=True` 越界）。

## 二、提案 A–D 逐条评估

### A. ndax 转 excel 降级为子功能

**合理性**：高。当前 UI 把"ndax转excel"放在首位暗示它是主入口，但实际上用户最终要的是分析报告，不是中间 xlsx。降级为子功能符合用户目标。

**风险**：
- 改动极小（UI 层：ndax_tab.py 嵌套进一个按钮即可），不触碰数据流
- **遗漏**：降级后用户发现"先转换再分析"的两步流程变得不直观。建议保留快捷入口（右键菜单或工具栏按钮），而非完全埋入

**结论**：支持，低风险。

### B. 不再通过 xml profile 带出数据，改由 ndax 识别

**合理性**：中等偏高，但存在关键契约缺口。

**需要重新识别的数据清单（第3题详细展开）**：ndax 内嵌的 Step.xml 和 TestInfo.xml 能提供大量元数据，但有 3 项 xml profile 有而 ndax 没有的：
1. **Whole_Prt 整机保护配置**（背景事实4已确认为"良性差异，不参与数据分析"）
2. **容量规格（mAh）**——ndax TestInfo.xml 有电流量程但无额定容量，而 lookup_pulse_currents 依赖容量做查表
3. **规格方法（1S1P/1S2P 等）**——文件名可提取，但无文件名时缺失

**风险**：如果 B 完全切断 profile，档位识别退化为"文件名解析 + ndax 实测"，config 查表机制失去数据源（查表需要 spec_name + capacity）。这意味着 **Proposal B 实质上需要 ndax 层补充容量/规格识别能力**。

**遗漏**：未提及 ndax 的 TestInfo.xml 是否包含容量信息。如果 TestInfo.xml 有额定容量字段，B 可行；如果没有，需从其他途径获取（如用户手动输入或 config 规则表匹配文件名前缀）。

### C. profile xml 只做验证

**合理性**：高。这是风险最低的渐进方案。

**风险**：
- 验证逻辑设计不当会导致"误杀"——profile 有合理差异（如四舍五入精度、单位 mA vs A）时不应报错
- **关键边界**：profile 的脉冲电流值与 ndax Step.xml 的 PulseData 实测值之间，允许的容差是多少？pulse_matcher 用 ±5%，但配置设定值应该精确匹配（0 容差）

**遗漏**：C 提案未说明验证失败后的恢复路径——是阻断还是放行？用户能覆盖吗？

### D. 中间格式选型

**合理性**：问题定义正确。当前"先转 xlsx 再读 xlsx"是 I/O 冗余。

**评估**：见第三部分单选建议。

## 三、中间格式单选建议

### 推荐：**内存 DataFrame 直传**

**五维论证**：

| 维度 | 内存 DataFrame 直传 | xlsx | csv | parquet |
|------|-------------------|------|-----|---------|
| **效率** | 零 I/O，O(1)传递 | 双重序列化（写+读），百万行文件 5-10s | 比 xlsx 快但仍需 I/O | 读写快但需额外依赖 |
| **出错面** | 无格式解析错误 | xlsxwriter/ openpyxl 版本差异、分表拼接 bug | 编码/分隔符问题 | pyarrow 版本耦合 |
| **可审计性** | 无落盘审计（需补偿） | 人可直接打开 | 人可直接打开 | 需工具打开 |
| **重复分析成本** | 需重跑 ndax 解析（~1s/文件） | 直接读缓存 xlsx | 直接读缓存 csv | 直接读缓存 |
| **代码改动量** | 中：需重构 data_processor 入口 | 零：现状 | 小：改写入格式 | 中+新依赖 |

**关键论证**：
1. **效率决定性优势**：NewareNDA `nda.read()` 解析单个 ndax ~0.5-1s，而 xlsxwriter 写百万行再 openpyxl 读回需要 5-10s。16 电池批量分析时差距扩大到分钟级。
2. **出错面最小**：当前 converter.py 的分表逻辑（Record/Record_2/Record_3）和 read_xlsx_sheets 的拼接逻辑都是 bug 温床。直传消除整个环节。
3. **可审计性补偿方案**：提供"保存调试副本"开关——需要时将 DataFrame 导出为 xlsx 到 2_xlsx/，但不作为主数据通道。这样兼顾了日常效率和异常排查。

**架构变更**：converter.py 的 `convert_one()` 改为 `parse_ndax()` 返回 DataFrame，`convert_one()` 降级为可选的落盘包装器。data_processor.py 接受 DataFrame 参数而非 xlsx 路径。

**改动量评估**：约 3-4 个文件需修改（converter.py、data_processor.py、ndax_tab.py 调用链、battery_analysis.py 入口），涉及函数签名变更。中等复杂度但可分步推进。

**降级方案**：如果 DataFrame 直传的改动量在工期上不可接受，**xlsx 落项目级缓存目录**是务实次选（GLM 的建议），但必须修复分表拼接的已有风险。

## 四、ndax 重新识别清单

通过 ndax 识别替代 profile xml 时，逐一分析：

| 数据项 | 原来源 | ndax 可替代？ | 替代路径 | 风险 |
|--------|--------|-------------|---------|------|
| **脉冲档位（mA）** | 文件名解析 | ✅ Step.xml `<PulseData>` | 从 Step.xml 提取 Pulse 节点的电流值 | 权威来源，比文件名更可靠 |
| **电流量程** | profile xml | ✅ TestInfo.xml | `TestInfo.xml` 含 CurrentRange | 无风险 |
| **SN / 电池编号** | 文件名 / profile | ✅ TestInfo.xml | SN 字段 | 无风险 |
| **测试开始时间** | xlsx 文件名 | ✅ TestInfo.xml | StartTime 字段 | 无风险 |
| **温度条件** | 文件名 | ⚠️ 部分 | ndax 文件名通常含温度信息，但非结构化 | 需保留文件名解析 |
| **额定容量（mAh）** | profile + config 规则表 | ❌ **缺失** | ndax 无额定容量字段 | **关键缺口**：lookup_pulse_currents 依赖容量查表 |
| **规格型号** | profile + 文件名 | ⚠️ 部分 | 文件名可提取，但无法覆盖所有情况 | 与现况一致 |
| **规格方法（1S1P等）** | 文件名 | ⚠️ 部分 | 同上 | 现有默认 1S1P 机制可兜底 |
| **Whole_Prt 整机保护** | profile xml | ❌ 不需要 | 背景事实4确认为良性差异 | 无风险 |

**核心缺口**：额定容量。ndax/TestInfo.xml 不包含此信息，而它是 `lookup_pulse_currents()` 的关键入参。B 方案若完全切断 profile，当文件名也无法提取容量时，档位查表失效，只能依赖 ndax 实测档位或用户手动输入。建议：
- 优先从 config 的 `BatteryConfig/Rules` 按型号前缀匹配容量（现已有此逻辑）
- 次选：从 ndax Pulse 实测电流反推容量档（观察到 60mA 脉冲 → 大概率 1200-2000mAh 区间）
- 兜底：弹框让用户选择规格型号，再查表

## 五、profile 验证策略边界情况

### 5.1 不一致报错 vs 告警放行

**建议：分级处理**

- **设定值层面（config 查表 vs profile xml）**：应精确匹配（0 容差）。查表结果是标准定义，profile 也是人工维护的，两者不一致说明某一方有错（如 CF224642T 用了旧模板），应 **阻断 + 显示差异详情 + 提供"以 ndax 为准继续"按钮**
- **实测层面（ndax Pulse 实测 vs 设定值）**：允许 ±5% 容差（与 pulse_matcher 现有契约一致）。超出则告警但默认放行——BTS 设备的电流输出有物理公差

### 5.2 无 xml 弹框声明一次够不够

**不够**，但可以改进为够用：
- 声明应包含具体信息："未找到 profile xml，将完全依赖 ndax 数据进行分析。档位识别来源：[ndax Step.xml / config 查表 / 文件名解析]"
- 声明状态应持久化到本次分析的结果目录（写入 Info_Plot.json 的 `profile_source` 字段），供报告审计追溯
- 不需要每次弹框——同一 ndax 文件集 + 同一次分析会话只弹一次，跨会话重分析则重新弹

### 5.3 多 ndax 文件间档位不一致

**这是真实风险**。同一批次的 16 个电池理论上应该相同，但如果操作员在测试中途改了配方，不同电池可能有不同的脉冲档位。

**建议**：
- 第一个 ndax 解析后记录档位为基准
- 后续 ndax 解析时比对：一致则静默通过，不一致则弹框列出哪些文件有差异，让用户选择"以第一个为准 / 分组处理 / 全部中止"
- 当前管线假设所有电池档位相同（`listCurrentLevel` 是单一列表），如果允许不一致，下游 `battery_analysis.py` 和 `figure_builder.py` 需要支持多档位集——这是较大改动，建议 MVP 阶段先做"检测 + 报错"

## 六、filter_data 空档位防御——必须兜底

### 结论：**必须修，且应在本次重构之前或同时修复**

**理由**：

1. **crash 路径清晰**：当 `listCurrentLevel` 指定的某档位在实测数据中不存在时，`pulse_matcher` 的 `match_pulse_levels()` 返回该档位的位置列表为空 → `battery_analysis.py` 传给 `filter_data()` 的对应子列表为空 → `data_utils.py:42` 的 `filtered_mask[0] = True` 在空数组上越界 → **IndexError → 整个报告崩溃**。

2. **本次重构不能消除此风险**：即使 ndax 成为档位权威来源，仍存在：
   - BTS 设备跳过某档位测试（操作员手动中止某工步）
   - ndax 文件损坏导致部分数据缺失
   - 用户手动指定错误档位（config 覆盖场景）
   
3. **防御层次建议**：
   - **第一层**（pulse_matcher 输出）：返回时标记哪些档位无数据（已有 `None` 返回，但仅限全部无数据的情况）
   - **第二层**（battery_analysis.py）：遍历 listCurrentLevel 时，检查 `listLevelToRow[i]` 是否全为空 → 跳过该档位 + 日志警告
   - **第三层**（data_utils.py `filter_data`）：函数入口检查 `if not charge_data` → 直接 append 空列表，不执行 `filtered_mask[0] = True`。**这是最小改动、最大收益的必修项**

4. **改动量**：data_utils.py 加 2 行防御代码（`if not charge_data: ... continue`），测试补一个空列表 case。0.5 小时可完成。

### 优先级声明

filter_data 越界修复是 **P0 级 bug fix**，不应等待本次重构的架构决策。它可以在独立分支上先修复并合入，然后本次重构在此基础上调整档位来源。

---

## 七、总结：推荐实施路径

| 优先级 | 任务 | 依赖 |
|--------|------|------|
| P0 | filter_data 空档位防御（data_utils.py + 单测） | 无 |
| P1 | C 方案：profile xml 仅做验证（含分级处理逻辑） | P0 |
| P1 | B 方案：ndax 识别替代 profile 数据带出 | P0 + C |
| P2 | D 方案：DataFrame 直传（或 xlsx 缓存降级方案） | P1 |
| P3 | A 方案：UI 降级 ndax 转 excel | 独立 |