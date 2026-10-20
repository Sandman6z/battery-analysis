# GLM (Round 2): GLM Round 2 辩论

# GLM Round 2 辩论

## 议题1：中间格式 —— 我方改判，单选「内存 DataFrame 直传」

**结论：单选内存 DataFrame 直传 + 会话内缓存复用；xlsx 仅由已裁决降级的『ndax转excel』按钮按需导出，不进主分析链路。**

### 我方（xlsx缓存）最强论证，先摆出来

1. **审计刚需**：电池测试报告是工程交付物，客户质疑某只电池数据时要能打开中间数据人工核对。DataFrame 转瞬即逝，xlsx 是唯一人肉可读载体。
2. **内存压力**：converter.py 的 XLSX_MAX_ROWS=1_048_576 说明 record 表能逼近百万行；16 文件 × 百万行 × 十来列 float64，会话内全量驻留内存可能上 GB，Windows 上不是闹着玩的。
3. **已验证路径**：read_xlsx_sheets 的拆表/续表跳2行拼接虽然脆弱，但它是目前唯一被实测验证过的读取路径，DataFrame 直传是新代码。

### 为什么我放弃：诚实评估后的三个事实

1. **性能叙事被实测数据推翻**：nda.read ≈1s/文件，而 xlsx 写+读 5–10s/文件。缓存存在的全部意义是"花一次成本换后续快"，但这里后续读 xlsx（数秒）比直接重解析 ndax（1s）还慢——**缓存比它要替代的操作更贵**。16 文件首次分析：直传 ≈16s，xlsx 路径 ≈16s + 80–160s 写盘。这不是权衡问题，是被数据单方面否决。
2. **审计有更便宜的替代**：裁决1已把『ndax转excel』降级为子功能按钮——人工审计需求由按钮按需导出满足；程序化追溯由结果目录 3_analysis results/{date}_v{ver}/ 落关键提取字段（档位、循环数、每电池摘要）满足。为低频审计在主链路常驻 5–10s/文件的写盘成本，是拿高频操作付低频需求的账。
3. **脆弱映射能少走就少走**：拆表续表那套映射（converter.py:33, xlsx_reader.py:12-17）是已识别的脆弱面。直传方案让主链路根本不经过它，攻击面缩小；xlsx 往返只在用户显式点按钮时发生。

### 混合方案评估

「DataFrame 直传主链路 + manifest 控制的 xlsx 落盘缓存兼审计」——**部分成立但不值得**。混合里的 xlsx 腿只服务"跨会话加速"，而实测时序证明该加速为负。混合实质退化为「直传 + 按钮导出」，那就不叫混合，叫直传加一个已有的按钮。Round 1 我提的 manifest(mtime+size) 机制随按钮缓存的实现保留（若按钮选择落盘 2_xlsx/），主管线不依赖它。

### 回应用户新提案（中间格式放临时文件夹）

反对。Windows 临时目录受清理策略支配，审计时文件可能已经没了——临时 xlsx 既不快（同 5–10s/文件）又不可靠（会被清），两头的好处一个不占。结果落 3_analysis results/{date}_v{ver}/ 部分采纳：落的是**分析结果与关键提取字段**，不是全量中间数据。

### 内存压力的解法（回应我自己的论证2）

会话级缓存 dict（analysis_runner 持有 parsed DataFrames），重复分析（高频操作）零成本命中；会话结束即弃，下次重解析 1s/文件完全可接受。不做 LRU 不做落盘——等真实 OOM 出现再说，届时最便宜的修复是只缓存 step/cycle 层、record 层按需重解析，仍不需要 xlsx 中间层。

---

## 议题2：profile 不一致分层决策树

**结论树：**

```
Step.xml PulseData（ndax，权威） ← 自动查找同目录 profile xml
├─ 未找到 profile → 弹框声明（QSettings 版本号记忆，见议题4）→ 放行，留痕
├─ 档位数不同 → 阻断，无放行按钮
├─ 档位值不同·设定值层（容差 0，逐项精确比对）→ 阻断弹框
│     列出双方档位+差异高亮；[以 ndax 为准继续]为次要按钮，默认焦点=[中止]
│     点继续 → 留痕后放行
├─ 档位值不同·实测层（容差 max(1%, 0.5mA)）→ 黄色告警，默认继续，留痕
└─ 全部一致 → 静默通过，logging.info
```

- **档位数不同必须硬阻断无放行**：intCurrentLevelNum 驱动全部下游表格/图/统计（data_loader.py:88,305,318，statistics_utils.py:14,31 等全按它建矩阵），数不同 = 下游必然错位，没有任何"继续"语义成立。
- **CF224642T 正是值层拦截的意义**：profile 30/26/15/6 vs Step.xml 60/30/15/6，档位数相等（4=4），只查档位数会漏过。设定值层容差 0 才能拦住它——这也是我对"只做轻量检查"的所有折中方案的否定理由。
- **对 DeepSeek「硬阻断无放行」的回应**：设定值层确实该阻断，但不给放行按钮过刚。profile 是人工产物，可能过期/复制错目录；ndax 已裁决为权威，知情用户应能显式继续。放行的安全性由留痕保证，不由禁止保证。
- **对 GPT「值差异仅告警」的回应**：CF224642T 就是设定值差异且直接触发崩溃的 case，把它降为告警等于验证器形同虚设。设定值层和实测层必须分治——实测层有仪器噪声（我的 max(1%,0.5mA) 对 DeepSeek 的 ±5%：5% 太宽，60mA 档 3mA 偏差已属异常），设定值层没有噪声借口。

**留痕设计（写 Info_Plot.json 顶层新字段，与议题4共用）：**

```json
"profile_check": {
  "profile_found": true,
  "result": "pass | warned | overridden | blocked",
  "profile_levels_ma": [30, 26, 15, 6],
  "ndax_levels_ma": [60, 30, 15, 6],
  "user_action": "continue_with_ndax | abort | null",
  "checked_at": "ISO8601"
}
```

---

## 议题3：多 ndax 档位不一致 —— MVP = 检测 + 中止

**结论：第一期只做检测+中止（弹框列出每个文件的档位与差异，引导用户核对文件）；二期接口预留，优先做「以基准为准、跳过不匹配文件」；并集放最后或不做。**

### 并集方案的真实工作量（grep 已核实）

单一列表假设遍布全链路，改并集意味着：

- `src/battery_analysis/main/visualization/data_loader.py:88`（intCurrentLevelNum=len）、`:305`（行布局 1+intCurrentLevelNum×3）、`:318`（矩阵索引）
- `src/battery_analysis/main/visualization/figure_builder.py:62,273`
- `src/battery_analysis/main/visualization/battery_selection.py:157,289`（_battery_line_indices 行索引推导）
- `src/battery_analysis/main/visualization/filter_controls.py:52-55`
- `src/battery_analysis/utils/writers/statistics_utils.py:12-46`（compute_list_cpt/compute_statistics 按 intCurrentLevelNum×intVoltageLevelNum 建满矩阵——缺档位后均值/中位数/箱线图全要定义 N/A 语义）
- `src/battery_analysis/utils/report_coordinator.py:101,418,522`（报告正文、图标题、图例）
- `src/battery_analysis/utils/writers/excel_overview.py:42-174`、`csv_writer.py:86-174`、`excel_report_writer.py`、`word_front_matter.py:135-163`（所有 writer 表格形状）

≥12 文件、每个 writer 的表结构变化、统计 N/A 语义、图例/颜色/行索引三处推导重写。**诚实估计：2–4 周纯开发 + 全 writer 回归**，且新增"部分电池缺某档位"这个 bug 面。收益场景是"用户故意混装不同档位电池进一个批"——低频，且这类批在议题2的设定值检查下多半本来就该被拦。

**检测+中止的成本：批量加载入口一次逐文件比对 + 一个弹框，1–2 天含测试。** 收益成本比差两个数量级。

**接口预留**：一致性检查函数返回结构化结果 `{consistent: bool, base_levels_ma: [...], per_file: {filename: levels}}`，调用方据此决策。二期若真出现合法混装需求，先做 DeepSeek 基准方案的最小版——以第一个文件为基准、不匹配文件跳过并告警（单一列表不变量保持，改动只在加载端过滤，估 2–3 天）。并集永不进 MVP。

---

## 议题4：无 xml 声明持久化 —— 主方案 QSettings 版本号 + 叠加 Info_Plot.json 每次留痕

**结论：QSettings 存策略版本号为主，Info_Plot.json 留痕为强制叠加项，黄三角状态栏提示为二期可选叠加。**

- **QSettings 键名**：`validation/profile_disclaimer_version`，值为策略版本字符串（首发 `"2026.10"`）。免责文案/检查策略变更时 bump 版本 → 老用户重新弹框。用版本号而非 bool：改文案不需要担心已确认用户被旧声明覆盖。
- **对 GPT 项目级 NO_PROFILE_DISCLAIMER.txt 的回应**：项目目录会被拷贝/重命名/换机器，txt 跟着目录走，换个数据集仍带着"已声明"状态，语义错位；且每个数据目录多一个噪音文件。QSettings 键跟安装走，粒度对。
- **对 DeepSeek 会话级弹一次的回应**：太碎。同一项目重复分析（高频操作）每次启动都弹 = 训练用户无脑点确认，声明失去知情意义。
- **报告可追溯（目的b）必须每次运行写**：复用议题2的 `profile_check.profile_found: false`——无 xml、通过、告警、放行四种状态统一进这一个字段，两个议题一套机制，不另发明字段。
- **MiniMax 黄三角**：采纳为低优先级叠加——状态栏常驻图标，hover 提示"本批次未经 profile 验证"。成本一个控件，二期。

---

## 实施顺序 + 改动文件清单

1. **P0（全票前置）**：`src/battery_analysis/utils/processors/data_utils.py` filter_data 循环头加 `if not charge_data: append([]); continue`；`src/battery_analysis/utils/processors/charge_calculator.py` L2 空位返回空；`tests/` 补边界用例（空档位电池、全空批）。
2. **ndax 直读**：新增 `src/battery_analysis/ndax/loader.py`（Step.xml PulseData → 内存 DataFrame，含会话级缓存 dict）；`src/battery_analysis/main/managers/analysis_runner.py` 持有缓存并接入。
3. **profile 验证器**：新增 `src/battery_analysis/utils/validators/profile_validator.py`（议题2决策树）；弹框接入 `src/battery_analysis/main/ui_components/`。
4. **留痕**：`src/battery_analysis/utils/writers/info_csv_writer.py` write_info_plot_json 增加 profile_check 参数；调用点 `src/battery_analysis/utils/processors/battery_analysis.py:479` UBA_WriteCsv 传参。
5. **多 ndax 一致性检查**：`src/battery_analysis/ndax/loader.py` 批量入口实现，返回结构化结果 + 中止弹框。
6. **UI 降级**：`src/battery_analysis/main/ui_components/` 主 tab 改子功能按钮；`src/battery_analysis/ndax/converter.py` 保留原样服务按钮。
7. **结果目录**：`3_analysis results/{date}_v{ver}/` 路径生成（strResultPath 来源处，battery_analysis.py / report_coordinator.py）。

每步独立可测、可单独提交；1–2 是其余全部的地基，顺序不可换。