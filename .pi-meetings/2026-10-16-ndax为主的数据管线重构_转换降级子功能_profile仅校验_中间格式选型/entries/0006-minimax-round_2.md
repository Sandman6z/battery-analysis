# MiniMax (Round 2): MiniMax Round 2 辩论

# MiniMax Round 2 辩论

---

## 议题1：中间格式——主链路 DataFrame 直传，审计层 xlsx manifest 管控

### 对 xlsx 缓存方案的最强攻击

xlsx 方案的真实伤害不在"写盘慢"（5-10s 对整体流程是小头），而在**路径依赖引发的系统脆弱性**：

1. **converter.py 已有 XLSX 脆弱映射**：现有 `read_xlsx_sheets` 拼接逻辑是 Round 1 已确认的"已验证的脆弱映射"，在它上面再叠一层 xlsx 写→读循环，相当于在危楼地基上继续盖楼。
2. **审计缓存与主逻辑耦合**：一旦 xlsx 缓存进入主链路，后续所有依赖 ndax→DataFrame 的组件都必须处理"缓存存在时跳过重算"的分叉逻辑——等于把缓存一致性维护的复杂度扩散到整个代码库。
3. **无法向后兼容过渡**：重构期新旧逻辑并存时，xlsx 缓存的 mtime/size 失效策略需要精确对齐 converter 内部状态，而 ndax 结构随时可能变（用户已在引入临时文件夹提案）。

### 我方退让：接受"审计缓存"需求，但拒绝进入主链路

audit 需求是合理的（GPT 提出的"重复分析免重转"也有价值），但实现位置应在**主链路下游**，用 manifest 控制：

```
DataFrame 直传（主链路，无任何中间文件）
    ↓
report_writer 写报告前
    ↓
if audit_mode: write xlsx to 3_analysis results/{date}_v{ver}/cache/
               update manifest.json (ndax_path, mtime, size, parquet_path?)
```

这样 xlsx 永远不在计算主链路中出现，converter 的脆弱映射与它无关，且 manifest 可追踪"这份 xlsx 是哪次 run 的哪个 ndax 生成的"。

### 混合方案成立的条件

- **主链路**：内存 DataFrame，无中间文件
- **审计层**（可选开关）：manifest.json + 按需 xlsx 落盘，manifest 记录 cache hit 逻辑
- **pyarrow 问题**：审计层 xlsx 不需要 pyarrow，用 openpyxl 即可（已有 xlsx 写能力）
- **用户新提案（临时文件夹）**：临时文件夹用于中间结果（parquet 可选缓存），3_analysis results/{date}_v{ver}/ 用于最终报告，两层分离清晰

**结论**：主链路 DataFrame 直传单选，审计 xlsx 缓存作为独立可选层，不进 converter。

---

## 议题2：profile 不一致——四级告警矩阵收敛为分层决策树

### 合并各家合理元素

| 层级 | 条件 | 动作 | 放行按钮 | 留痕 |
|------|------|------|----------|------|
| **L1 阻断** | 档数不一致（子集/超集/不相交） | 弹框阻断，NDaxWizard 不可继续 | 无 | 写 Info_Plot.json `profile_mismatch: {type: "slot_count_mismatch", slots: {...}}` |
| **L2 阻断（可放行）** | 档位数相同，设定值层不一致 | 弹框阻断，显示 diff | "以 Step.xml 为准继续" | 同上 `type: "setpoint_mismatch"` |
| **L3 告警** | 档位数相同，设定值一致，实测值层超限（>5%） | 黄三角 toast，可继续 | 无按钮（自动放行） | 写 `type: "measured_deviation"` |
| **L4 通过** | 全部一致 | 静默 | 无 | 无 |

**CF224642T case 命中 L2**：档位从 30/26/15/6 → 60/30/15/6，档数相同但设定值有差异——验证器拦住此处，弹出 diff 框，"以 Step.xml 为准"放行按钮存在，用户知情+可追溯。

**放行按钮文案**（采纳 DeepSeek 的"以…为准"语义）：`「以 Step.xml 为准，继续分析」`；L1 无按钮是因为子集/超集意味着档位定义本身已被破坏，继续输出无意义。

**留痕字段**（Info_Plot.json）：
```json
"profile_validation": {
  "xml_found": true,
  "xml_path": "...",
  "result": "setpoint_mismatch_allowed",  // 或 blocked/measured_deviation
  "slots": {
    "xml": [30, 26, 15, 6],
    "step": [60, 30, 15, 6]
  },
  "user_override": true,
  "timestamp": "..."
}
```

---

## 议题3：多 ndax 档位不一致——MVP 仅检测+告警，二期留并集接口

### 承认我 Round 1 方案的错误

Round 1 我提出"并集+告警"，但**下游链路是单一列表**（listCurrentLevel/intCurrentLevelNum/figure_builder/plot_writer 全链路假设统一档位），并集意味着：

- 下游 4 个模块全部需要改造 list→list-of-lists
- listCurrentLevelNum 假设单一 int，现在可能是 [3, 4, 5]
- figure_builder 每张图需要决定"用哪组档位画哪组数据"

真实工作量估计：5-7 个文件改动，触及所有数据消费端，测试用例翻倍。

### MVP 收敛方案（采纳 GLM 的"只做检测+中止"合理内核）

**第一期 MVP（强制）**：
- 多 ndax 加载后比对档位：`assert all(ndax.slots == ref.slots)`，不一致则弹框并中止
- 弹框内容：显示各文件档位列表，用户确认"使用哪个文件为基准"或"中止"
- 报告头注明"本次分析包含 N 个 ndax，档位已对齐"

**二期接口（预埋）**：
```python
# data_loader.py
def load_multi_ndax_with_union(ndax_files, mode="strict"):  # "strict" | "union"
    # mode="union" 时，返回 (merged_df, slot_union, per_file_slot_map)
    # figure_builder 接收 slot_union 并处理 N/A 档位
```

### 为什么二期才做并集

- 并集的价值只在"同一个分析中必须同时呈现所有档位数据"时才成立——这个需求从未被用户明确提出
- 当前主要场景是"批量处理多个相似电池文件"，每个文件独立分析，并集无意义

---

## 议题4：无 xml 声明持久化——三层叠加

### 采纳 GPT 的 Info_Plot.json 方案（最佳可追溯性）

这是最合理的持久化方案——直接进报告归档，不需要额外的文本文件。

### 采纳 GLM 的 QSettings 版本号方案（防重复弹框）

QSettings 存键 `profile_disclaimer_version`，值 `"2026.10"` 或 `True`，首次弹框后写入，下次进入检测版本号，版本不变则不重复弹。

### 维持我的"首弹+黄三角常驻"作为 UI 层

黄三角不是持久化机制，是**当前会话内的可见性提示**——即使声明已写进 Info_Plot.json，用户在分析过程中仍需感知"当前无 profile，正在以 Step.xml 为准"。

### 最终三层设计

| 层次 | 机制 | 触发时机 | 目标 |
|------|------|----------|------|
| **P1 弹框** | QMessageBox 一次 | 会话首次检测到无 xml | 用户知情 |
| **P2 常驻提示** | QLabel 黄三角，status bar | 当前 session 无 xml | 分析过程可见性 |
| **P3 持久化** | Info_Plot.json `no_profile: {version: "2026.10", timestamp: "..."}` | 每次写报告前 | 报告可追溯 |

**QSettings 键名**：`AnalysisSession/no_profile_disclaimer_acknowledged`（含版本，版本变了则重新弹）

**Info_Plot.json 字段**：
```json
"no_profile": {
  "acknowledged": true,
  "version": "2026.10",
  "timestamp": "...",
  "note": "Analysis conducted without profile XML; step values from Step.xml used as reference."
}
```

---

## 实施顺序 + 改动文件清单

### Phase 1（P0，阻断崩溃）
1. `data_utils.py` — filter_data 空档位防御（已裁决，立即修）
2. `data_loader.py` — profile_validator.xml_profile_validator，档位一致性验证，命中 L1/L2 时弹框阻断
3. `main_window.py` — profile 不一致弹框 UI，L2 放行按钮逻辑

### Phase 2（P1，本会议题落地）
4. `data_loader.py` — 多 ndax 一致性检测，弹框+中止（MVP）
5. `info_plot_writer.py` — profile_validation / no_profile 字段写入
6. `config.py` — QSettings 键定义
7. `main_window.py` — 无 xml 首弹 + 黄三角 status bar 提示
8. `report_writer.py` — 审计 xlsx 缓存逻辑（manifest 管控，可选）

### Phase 3（预留）
9. `data_loader.py` — load_multi_ndax_with_union(mode="union") 接口预埋
10. `figure_builder.py` — slot_union 处理，N/A 档位展示

---

**收敛声明**：MiniMax 在议题1、2、4均接受混合方案收敛；议题3主动撤回并集方案，改为 MVP 检测+二期接口。
