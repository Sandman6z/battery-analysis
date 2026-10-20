# DeepSeek (Round 2): DeepSeek Round 2 辩论

# DeepSeek Round 2 辩论

## 议题1：中间格式（2:2平票 → 必须收敛）

### 最终选择：**内存 DataFrame 直传**

---

### 我方对 xlsx 缓存方案的最强攻击

GLM/GPT 的核心论点是"xlsx 是已验证路径，改动最小"。我要指出这个论证的三个真实漏洞：

**漏洞1：converter.py 分表逻辑是已知定时炸弹**

`converter.py` 的 `XLSX_MAX_ROWS=1_048_576` 触发 Record_2/Record_3 分表，`read_xlsx_sheets` 再拼接。这不是"已验证"，是"还没炸"。xlsx 单表行数限制是 Excel 格式硬约束，分表拼接的边界条件（最后一行是否截断、表头是否重复、列对齐）每一个都是隐性 bug。GLM 说"converter.py 引擎零改动"——恰恰相反，**保留 xlsx 路径意味着永久保留这段脆弱映射**，而 DataFrame 直传直接消除它。

**漏洞2："缓存命中免重转"的账算错了**

GLM 说"保留 xlsx 缓存后，重复分析直接命中缓存、跳过最慢的 ndc 解析"。但仔细看数据流：

- xlsx 缓存路径：首次 = ndax解析(~1s) + xlsx写(~5s) + xlsx读(~3s) = **~9s/文件**；缓存命中 = xlsx读(~3s) = **~3s/文件**
- DataFrame 直传：每次 = ndax解析(~1s) + 内存传递(0s) = **~1s/文件**

16 文件批量时：xlsx 首次 = ~144s，缓存命中 = ~48s；DataFrame 每次 = ~16s。**即使缓存命中，xlsx 路径仍然比 DataFrame 直传慢 3 倍**。所谓"跳过最慢的 ndc 解析"是对的，但 xlsx 读取本身就比 ndc 解析慢——用一个更慢的缓存来"跳过"一个更快的解析，逻辑不成立。

**漏洞3："可审计性"是可选需求，不应驱动架构**

GPT 说"可审计性是隐性刚需"。但在当前项目规模（16 电池/批、5 个项目）下，审计频率极低。用一个高频操作（每次分析都走 xlsx）来服务一个低频需求（偶尔审计），ROI 为负。审计需求完全可以通过按需导出补偿（见下文）。

---

### 诚实评估混合方案

主持人提出"主链路 DataFrame 直传 + manifest 控制的 xlsx 落盘缓存兼审计"。我诚实评估：

**混合方案的吸引力**：
- 日常走 DataFrame（快），需要审计时有 xlsx（可查）
- manifest 控制缓存，ndax 不变则不重转

**混合方案的真实成本**：
1. **双路径维护**：converter.py 要同时支持"返回 DataFrame"和"写 xlsx"两条路径，data_processor.py 要同时支持"接受 DataFrame"和"读 xlsx 路径"两条入口。每次改动都要测两条路径。
2. **缓存失效逻辑**：manifest 的 mtime+size 判定在 Windows 上有精度问题（NTFS mtime 精度 100ns，但跨时区/夏令时可能漂移），且用户手动改 ndax 文件名不触发 mtime 变化。
3. **分表问题依然存在**：只要保留 xlsx 落盘能力，Record_2/3 分表逻辑就不能删，脆弱映射继续存在。

**我的判断**：混合方案在理论上优雅，但在当前项目规模下增加了不必要的复杂度。**单一路径 > 双路径**，除非有明确证据表明审计需求频繁到值得维护双路径。

---

### 最终选择理由

| 考虑因素 | DataFrame 直传 | xlsx 缓存 | 胜出方 |
|---------|---------------|----------|-------|
| 首次分析效率(16文件) | ~16s | ~144s | DataFrame |
| 重复分析效率(16文件) | ~16s | ~48s(缓存命中) | DataFrame |
| 分表脆弱性 | 消除 | 保留 | DataFrame |
| 可审计性 | 需按需导出 | 天然有 | xlsx |
| 代码改动量 | 中(函数签名变更) | 小(改输出路径) | xlsx |
| 双路径复杂度 | 无 | 混合方案有 | DataFrame |

**关键决策因素**：效率差距是 3 倍（不是微优化），分表脆弱性是硬风险（不是假设），而可审计性可以通过"调试模式导出 xlsx"补偿。权衡后，DataFrame 直传胜出。

**审计补偿方案**：在 UI 加一个"保存中间数据"复选框（默认关闭），勾选时 DataFrame 额外导出为 xlsx 到 `2_xlsx/` 目录。这样日常零开销，需要时一键导出。

---

## 议题2：profile 不一致时的处理深度

### 收敛结论：分层决策树

基于 CF224642T 案例（profile 30/26/15/6 vs Step.xml 60/30/15/6）和四家方案，我提出以下决策树：

```
Step1: 设定值层比对（profile PulseData vs Step.xml PulseData）
  │
  ├─ 档位数不同 → 阻断
  │     弹窗：「档位数量不一致：profile {n}档 vs ndax {m}档」
  │     按钮：[中止]（默认焦点） / [以 ndax 为准继续]
  │     放行 → Info_Plot.json 写 "profile_override": {"type": "level_count_mismatch", "profile": [...], "step_xml": [...], "user_action": "accepted_ndax"}
  │
  ├─ 档位数相同但值不同（0容差）→ 阻断
  │     弹窗：「设定值不一致：profile {v1}mA vs Step.xml {v2}mA」
  │     按钮：[中止]（默认焦点） / [以 ndax 为准继续]
  │     放行 → Info_Plot.json 写 "profile_override": {"type": "value_mismatch", ...}
  │
  └─ 一致 → 进入 Step2

Step2: 实测层比对（data.ndc Pulse 实测电流 vs Step.xml 设定值）
  │
  ├─ 实测档位数 ≠ 设定档位数 → 告警（不阻断）
  │     状态栏提示：「实测档位 {k} 个，设定 {n} 个，缺失档位将标注 N/A」
  │     Info_Plot.json 写 "measured_level_discrepancy": {"expected": n, "actual": k, "missing": [...]}
  │
  ├─ 实测值偏差 > max(设定值×1%, 0.5mA) → 告警（不阻断）
  │     Info_Plot.json 写 "measured_level_drift": {...}
  │
  └─ 通过 → 静默继续
```

**关键设计决策**：

1. **设定值层阻断，实测层放行**。理由：设定值不一致意味着"用了错的 profile"（如 CF224642T），这是致命错误；实测偏差是设备物理公差，不应阻断分析。

2. **放行按钮文案**：`[以 ndax 为准继续]`——明确告知用户以哪个数据源为准，不是模糊的"继续"。

3. **放行留痕**：写入 Info_Plot.json 的 `profile_override` 字段，包含不一致类型、双方值、用户操作。报告生成时在页脚标注"⚠ 档位以 ndax 实测为准，profile 校验未通过"。

4. **与 GLM 方案的差异**：GLM 提议实测层用中位数比对，我同意这个思路但认为实测层不应阻断——中位数比对的结果是告警信息，不是阻断条件。

---

## 议题3：多 ndax 间档位不一致的 MVP 边界

### 收敛结论：MVP 仅检测 + 阻断，二期再做分组

**MVP 做什么**：
1. 批量导入时，逐文件提取 Step.xml PulseData
2. 以第一个文件为基准，后续文件逐一比对
3. 不一致 → 阻断弹窗，列出差异文件清单
4. 弹窗按钮：`[中止]`（默认） / `[以第一个文件为准继续]`

**MVP 不做什么**：
- 不做并集（理由见下）
- 不做分组分析
- 不做自动选择基准

**为什么不做并集**：

GPT/MiniMax 提议取并集。我反对，理由是**下游全链路改造成本极高**：

当前 `listCurrentLevel` 是单一列表，下游假设：
- `data_loader.py`: `intCurrentLevelNum = len(listCurrentLevel)` → 循环次数
- `figure_builder.py`: 按 `listCurrentLevel[i]` 索引绘图
- `plot_writer.py`: 按档位数生成 CSV 列
- `info_csv_writer.py`: 按档位数写 Info_Image.csv

并集方案意味着：每个文件的档位集不同，下游要支持"文件A有档位[60,30,15,6]，文件B有档位[60,30,15]"——这需要把 `listCurrentLevel` 从全局变量改为 per-file 字典，所有下游循环从 `for i in range(n)` 改为 `for level in file_levels[file]`。

**工作量估计**：至少 5 个文件（data_loader、battery_analysis、figure_builder、plot_writer、info_csv_writer），每个文件的核心循环都要改，加上 Info_Plot.json 结构变更、报告模板适配。保守估计 **3-5 人天**，且测试矩阵爆炸（每个文件 × 每种档位组合）。

**二期接口预留**：
- `listCurrentLevel` 改名为 `current_levels`，类型从 `list[float]` 改为 `dict[str, list[float]]`（key=文件名）
- 先在 MVP 阶段统一为 `{"*": [基准档位]}` 的 dict 结构，二期再扩展 per-file 支持
- 这样二期改动是渐进的，不需要推翻 MVP

---

## 议题4：无 xml 声明持久化

### 收敛结论：Info_Plot.json 为主 + QSettings 版本号为辅

**主方案：写入 Info_Plot.json**

```json
{
  "profile_status": "absent",
  "profile_ack": {
    "acknowledged": true,
    "timestamp": "2026-10-16T14:30:00",
    "strategy_version": "2026.10",
    "level_source": "ndax_step_xml"
  }
}
```

字段设计：
- `profile_status`: `"absent"` | `"validated"` | `"override"` | `"mismatch_ack"` — 覆盖所有 profile 状态
- `profile_ack.acknowledged`: 布尔，用户是否已确认
- `profile_ack.strategy_version`: 策略版本号，与 QSettings 同步
- `profile_ack.level_source`: 档位实际来源（`"ndax_step_xml"` / `"config_lookup"` / `"filename_parser"`）

**辅助方案：QSettings 存版本号**

- 键名：`battery_analysis/ndax/profile_ack_version`
- 值：`"2026.10"`（策略版本号字符串）
- 用途：跨会话记忆"用户已确认过当前版本的策略"，避免重复弹窗
- 版本递增触发重新弹窗（如策略从 `2026.10` 更新到 `2026.11`）

**为什么不选其他方案**：
- GLM 的 QSettings 存版本号（仅）：缺少项目级审计痕迹，报告审阅者看不到"此报告无 profile 校验"
- GPT 的 `NO_PROFILE_DISCLAIMER.txt`：单独文件容易丢失（复制报告时忘带），不如嵌入 Info_Plot.json（它已经是报告元数据的一部分）
- MiniMax 的黄三角常驻：UI 层方案，不解决"报告可追溯"需求，且跨会话状态管理复杂

**声明弹窗文案**：
> 「未找到 profile xml 文件。档位将完全以 ndax Step.xml 为准，标准符合性无法交叉校验。」
> [中止] / [确认继续]（默认焦点在中止）

---

## 实施顺序 + 改动文件清单

| 顺序 | 任务 | 改动文件 |
|------|------|---------|
| 1 | filter_data 空档位防御（P0） | `src/battery_analysis/utils/processors/data_utils.py:42` |
| 2 | profile 验证 + 不一致决策树 | `src/battery_analysis/utils/pulse_matcher.py`(新增比对函数), `src/battery_analysis/main/tabs/ndax_tab.py`(弹窗UI) |
| 3 | 无 xml 声明机制 | `src/battery_analysis/main/tabs/ndax_tab.py`(弹窗), `src/battery_analysis/utils/info_plot_writer.py`(写JSON字段), QSettings 键 |
| 4 | 多 ndax 批内一致性检测 | `src/battery_analysis/main/tabs/ndax_tab.py`(批量导入逻辑), `src/battery_analysis/utils/pulse_matcher.py`(比对函数复用) |
| 5 | DataFrame 直传主链路 | `src/battery_analysis/core/converter.py`(parse_ndax返回DataFrame), `src/battery_analysis/core/data_processor.py`(接受DataFrame参数), `src/battery_analysis/core/data_loader.py`(read_xlsx_sheets改为read_dataframe) |
| 6 | 可选 xlsx 导出（调试模式） | `src/battery_analysis/core/converter.py`(convert_one降级为可选落盘), `src/battery_analysis/main/tabs/ndax_tab.py`(UI复选框) |
| 7 | UI 降级 ndax 为子功能 | `src/battery_analysis/main/tabs/ndax_tab.py`(tab→按钮) |