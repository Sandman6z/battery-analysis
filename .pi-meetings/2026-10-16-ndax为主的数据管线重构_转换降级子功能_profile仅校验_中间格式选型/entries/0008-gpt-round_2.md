# GPT (Round 2): GPT Round 2 辩论

# GPT Round 2 辩论（四议题收敛）

> 开场声明：**议题1我改判**。Round 1 我站「xlsx 落 2_xlsx 缓存」，本轮在性能账重算后倒向 DataFrame 直传。立场变更的理由放在议题1内，不回避。

---

## 议题1：中间格式 —— 单选【内存 DataFrame 直传 + 会话内指纹缓存】

**结论**：单选 DataFrame 直传。xlsx 退出主链路，降级为审计副本（新数据集首次分析落一份）与「ndax转excel」子功能的导出格式；混合方案的 manifest 思想保留，「缓存」语义废弃。

### 对 xlsx 阵营的最强论证：xlsx 当数据契约会真实伤害这个项目

1. **脆弱映射是主链路必经之路**。`src/battery_analysis/ndax/converter.py:33` `XLSX_MAX_ROWS = 1_048_576` 分表 Record_2/3 + `src/battery_analysis/utils/readers/xlsx_reader.py:12` `read_xlsx_sheets` 拼接，是已验证的脆弱映射。16 文件 × 百万行 = 每次批量都在掷骰子，且一旦拼接错位，错误数据会静默流进报告。
2. **性能账算不平，"重复分析免重转"是幻觉**（这是我改判的直接原因）：`nda.read` 重解析 ~1s/文件 = 16s/批；而 xlsx 写+读 5-10s/文件中读回约占一半（2-4s/文件 ≈ 32-64s/批）。**缓存命中比重解析还慢**，写 xlsx 的 3-6s/文件是纯沉没成本。重复分析是高频操作，每一次都被 xlsx 税抽血。
3. **Windows 特有伤害**：百万行 xlsx 被 Excel/资源管理器预览占用时写入失败（文件锁）；杀毒软件实时扫描拖慢写入；单文件数十 MB × 16 的磁盘与备份负担。

### 诚实自评：DataFrame 阵营的真弱点

无落盘审计、崩溃后无凭据排查、批量中途失败全量重跑。这些是真的，但解法不是"把 xlsx 当数据契约"，而是审计副本 + 会话缓存（见下）。

### 混合方案诚实评估：「主链路 DataFrame 直传 + manifest 控制的 xlsx 落盘缓存兼审计」

- **当缓存：不成立**。读路径按数字永远不划算，却要完整保留分表写 + 拼接读两套脆弱代码——纯负资产。
- **当审计副本：成立**，但砍掉"缓存"语义后它只写不读，本质是"随报告归档的转换快照"，与已裁决的「ndax转excel」子功能共用同一导出代码即可，不构成第二条数据通道。
- **可保留的部分**：manifest（数据集指纹 = 路径 + 文件名集 + mtime + size）不驱动 xlsx，改驱动 ①会话内 DataFrame 缓存（改参数重跑零重转，彻底解决高频重复分析）②审计副本仅在新数据集首次分析时落盘一次。

### 用户新提案（临时文件夹 + 3_analysis results/{date}_v{ver}/）的采纳与修正

- 持久结果 → `3_analysis results/{date}_v{ver}/`：**采纳**。
- 中间产物 → 临时文件夹：**采纳但修正一处**——审计副本不进临时目录。审计件要随报告可追溯，应放 `3_analysis results/{date}_v{ver}/0_convert/`；临时目录只放可再生的调试 dump（按需）。

**最终单选：内存 DataFrame 直传（+ 会话内指纹缓存）**。无新依赖（pyarrow 不需要、pickle 不用）、脆弱映射整体退役出主链路、重复分析最快（会话内 0s / 跨会话 16s）、Windows 文件锁问题消失。

---

## 议题2：profile 不一致 —— 两层决策树

**结论（决策树）**：

```
输入 profile xml + ndax Step.xml PulseData
├─ 无 xml → 弹框声明一次 → 放行（已裁决，留痕见议题4）
├─ 层1 设定值层比对（0 容差：档数 与 逐档值）
│   └─ 不一致（含 CF224642T: 30/26/15/6 vs 60/30/15/6）→ 阻断
│      弹窗给逐档对照表 + 按钮【以 ndax 档位为准继续（记录差异）】
│      默认焦点 =【中止】→ 显式放行后留痕
└─ 层2 实测层比对（Step.xml PulseData vs 实测电流中位数，容差 max(1%, 0.5mA)）
    └─ 超差 → 黄色告警横幅 + 继续分析 → 留痕 warning（不阻断）
```

- **层1 采用 GLM 的 0 容差 + 阻断 + 显式放行**。关键理由：CF224642T 是档数相同、档**值**差异（30/26/15/6 vs 60/30/15/6）——若按我 R1"值差异仅告警"，这个崩溃 case 会被放过去，验证器就白建了。我修正自己 R1 的分层阈值：**档数不同与值不同同属设定值层、同为 0 容差阻断**，差异类型只影响留痕里的 `mismatch_type`。
- **层2 容差采纳 GLM 的 max(1%, 0.5mA)**（中位数比对），比 pulse_matcher 的 ±5% 严。两者职责不同：±5% 是匹配契约，max(1%, 0.5mA) 是体检告警阈值，漂移早发现；层2 不阻断（BTS 电流输出有物理公差）。
- **放行按钮文案**：【以 ndax 档位为准继续（记录差异）】（i18n key：`validation.override_continue`），默认焦点在【中止】，防手快。
- **放行留痕**：写 Info_Plot.json，字段 schema 见议题4（同一字段承载，不散落别处）。

---

## 议题3：多 ndax 档位不一致 —— MVP 检测+阻断+剔除，二期留并集接口

**结论**：MVP = 批内两两比对 Step.xml PulseData → 不一致弹框列出差异文件 →【剔除异常文件继续】/【中止】。**不做并集、不做自动分组**。

### 对并集方案（含我 R1 自我修正）

下游 `listCurrentLevel` 是单一列表——`src/battery_analysis/main/visualization/data_loader.py`（intCurrentLevelNum）、`src/battery_analysis/main/visualization/figure_builder.py`、`src/battery_analysis/utils/writers/plot_writer.py`、`src/battery_analysis/utils/writers/info_csv_writer.py`（Info_Image.csv posi 列）、`src/battery_analysis/main/business_logic/data_processor.py`（listTestInfo[14]）全链路按"统一档位集"假设写死。并集 = 全链路改造：档位索引→档位键重构 + N/A 渲染（图上缺口线段会误导读图）+ 报告版式回归。**诚实估 3-5 人日**（编码 2-3 + 版式/视觉回归 1-2）。触发场景却罕见（操作员中途改配方），且真发生时"剔除/分批"几乎总能覆盖。ROI 不成立，二期再议。

### 对 DeepSeek「基准 + 三选」

"以第一个为准"是危险默认——第一个文件凭什么是基准？"自动分组"= 一次操作出两份报告 + UI 状态分叉，一期不值，用户手动分两次跑即可。三选里两选都是坑，MVP 只留安全的两选。

### 对 GLM「纯检测 + 中止」

无放行路径太硬。真实场景"16 个里 1 个档位不同，剔掉继续"是刚需，纯中止会逼用户手动移文件。补【剔除异常文件继续】就是完整 MVP。

### 二期接口

Step.xml 解析时天然产出 `levels_by_file` 映射，数据层保留在解析结果元数据里（不进 listCurrentLevel）；若混档需求真出现，并集改造立专项。MVP 工作量 ≈ **0.5-1 人日**（解析层比对 + 弹框 + 剔除）。

---

## 议题4：无 xml 声明持久化 —— Info_Plot.json 为主，QSettings 免打扰，黄三角常驻

**结论**：主方案 = Info_Plot.json `profile_validation` 字段（审计）+ QSettings 指纹键（免重复弹框）；可叠加 = MiniMax 的黄三角常驻（成本近零、视觉持续提醒，好点子）。**撤回我 R1 的项目级 NO_PROFILE_DISCLAIMER.txt**：目的 (a)(b) 均被上述组合覆盖，报告目录多一个游离文本反而破坏 `{date}_v{ver}` 目录整洁。诚实说：我 R1 低估了 Info_Plot.json 已是 BatteryChartViewer 元数据入口（`src/battery_analysis/main/visualization/data_loader.py:105`）这一事实——那里才是可追溯的自然落点。

### 具体设计

```json
"profile_validation": {
  "result": "no_profile | ok | mismatch_overridden | measured_warning",
  "profile_levels": [30, 26, 15, 6],
  "ndax_levels": [60, 30, 15, 6],
  "mismatch_type": "count | values | none",
  "decision": "use_ndax | abort | remove_files",
  "policy_version": "2026.10",
  "ack_time": "2026-10-16T10:00:00"
}
```

- **QSettings 键**：`validation/policy_version = "2026.10"`（策略升级后重新弹）；`validation/no_profile_ack/<dataset_fingerprint>`（fingerprint = sha1(目录 + 排序文件名 + size + mtime)，同一数据集不重复弹，换数据集重弹）。
- **黄三角**：主窗状态栏常驻，点击展开差异详情，用户确认后消失——Info_Plot.json 留痕永久。
- **职责一句话**：QSettings 只管"别烦我"，Info_Plot.json 只管"可追溯"，二者不互相备份（换机器/归档场景 QSettings 不可见，它绝不能当审计）。

---

## 实施顺序 + 改动文件清单

**P0（独立先行，半天）**
- `src/battery_analysis/utils/processors/data_utils.py` — filter_data 循环头空档位防御（`if not charge_data: append([]); continue`）
- `src/battery_analysis/utils/processors/charge_calculator.py` — 上游空位列表返回空
- `tests/test_battery_analysis_pandas.py` — 补空档位 case

**P1（议题2+4，同一 Info_Plot.json schema，一次交付）**
- 新增 `src/battery_analysis/utils/validators/profile_validator.py` — profile 读取 + 两层比对（纯函数，可单测）
- `src/battery_analysis/utils/processors/battery_analysis.py:479` — Info_Plot.json 写 `profile_validation` 字段
- `src/battery_analysis/main/business_logic/data_processor.py` — 档位权威切 Step.xml + 调验证器 + 层1 阻断钩子
- `src/battery_analysis/main/workers/analysis_worker.py` — 阻断/放行流转
- `src/battery_analysis/main/window_init.py` / `window_actions.py` — QSettings 键 + 黄三角状态栏

**P2（议题1，DataFrame 直传）**
- `src/battery_analysis/ndax/converter.py` — 新增 `parse_ndax() -> DataFrame` + 会话指纹缓存；`convert_one()` 降级为导出包装器（子功能/审计副本共用）
- `src/battery_analysis/utils/processors/battery_analysis.py:282` — 入口接受 DataFrame，`read_xlsx_sheets` 调用移出主链路
- `src/battery_analysis/utils/readers/xlsx_reader.py` — 保留，仅供"导入旧 xlsx"兼容路径
- `src/battery_analysis/main/business_logic/data_processor.py` — 透传 DataFrame

**P3（议题3 MVP）**
- `src/battery_analysis/ndax/converter.py`（或 validators 下新增 `batch_consistency.py`）— `levels_by_file` 比对
- `src/battery_analysis/main/workers/analysis_worker.py` — 剔除/中止弹框流转

**P4（已裁决，独立收尾）**
- `src/battery_analysis/main/tabs/ndax_tab.py` — 「ndax转excel」降级为子功能按钮

**不动**：`filename_parser.py` 其余调用点、`pulse_currents.py`、`quality_requirements.py`、`file_validator.py`（2_xlsx 校验留给兼容路径）。
