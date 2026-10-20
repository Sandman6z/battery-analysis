# Round 2 上下文（主持人整理，必读）

## 已定裁决（不再讨论）

1. **档位权威 = ndax Step.xml PulseData**；主UI第一tab『ndax转excel』降级为子功能按钮（同 batteryChartViewer 模式）。文件名降为参考。
2. **profile xml 仅做验证**：自动查找，脉冲档位一致→继续，不一致→报错；允许无 xml（弹框声明一次、放行）。
3. **容量缺口不成立**（裁决）：容量来自 config Battery Rules（capacity_from_rules，规则第3段），从来不是从数据文件读的；且重构后容量查表降级为交叉校验，主路径直接读 Step.xml。
4. **制造商/成组方式等非分析字段**（裁决）：UI 人工配置即可，不进重构范围，filename_parser 其余调用点不动。
5. **filter_data 空档位防御必修**，P0 前置（Round 1 四票全票）。修法：data_utils.py filter_data 循环头 `if not charge_data: append([]); continue`；上游 L2（ChargeCalculator 空位列表返回空）同修。
6. **多 ndax 间档位一致性检查要做**（Round 1 四票全票识别为关键边界），但处理策略未收敛。

## Round 1 四家立场速览

| 顾问 | 中间格式 | 不一致处理 | 多ndax不一致 | 无xml声明持久化 |
|---|---|---|---|---|
| MiniMax | 内存DataFrame+parquet可选缓存 | 四级告警矩阵(子集/超集/不相交/相等) | 并集+告警 | 首弹+黄三角常驻 |
| GLM | xlsx落项目缓存2_xlsx/+manifest(mtime+size) | 阻断+[以ndax为准继续]按钮，默认焦点中止；设定值层容差0，实测层max(1%,0.5mA)中位数 | 批内检查，禁止静默取并集；第一期只做检测+中止 | QSettings存策略版本号字符串(如"2026.10") |
| DeepSeek | 内存DataFrame直传（xlsx按需导出） | 硬阻断无放行；设定值0容差/实测±5% | 基准文件+弹框三选（以第一个为准/分组/中止） | 会话级弹一次+写Info_Plot.json |
| GPT | xlsx落2_xlsx缓存（审计刚需+重复分析免重转） | 分层：档数不同→阻断；值差异→告警可放行 | 取并集，缺失档位画N/A+告警 | 项目级NO_PROFILE_DISCLAIMER.txt+QSettings |

## Round 2 对辩议题（只辩这4个，其余已裁决）

### 议题1：中间格式（2:2平票，必须收敛）
平票双方：GLM/GPT=xlsx缓存；DeepSeek/MiniMax=内存DataFrame直传。
补充事实供辩论：
- converter.py 现状 XLSX_MAX_ROWS=1_048_576 分表 Record_2/3，read_xlsx_sheets 拼接——这段是已验证的脆弱映射
- 重复分析（改参数重跑）是高频操作；nda.read 解析 ~1s/文件，16文件批量≈16s+；xlsx 写+读 每文件 5-10s
- 用户新提案：中间格式放临时文件夹；结果写 3_analysis results/{date}_v{ver}/ 后生成报告
- 项目约束：不引入新依赖（pyarrow 未装）；Windows 环境
要求：双方各自给出"对方方案哪里会真实伤害到这个项目"的最强论证，然后各退一步评估混合方案是否成立（如：主链路DataFrame直传 + manifest控制的xlsx落盘缓存兼审计）。最终必须单选。

### 议题2：profile不一致时的处理深度
四家四方案。要求收敛为一个分层决策树，明确：哪一层阻断、哪一层放行、放行按钮文案、放行是否留痕（写Info_Plot.json哪个字段）。
已知输入：CF224642T 案例=设定值层不一致（profile 30/26/15/6 vs Step.xml 60/30/15/6）——这正是触发崩溃的case，验证器存在的全部意义就是拦住它。

### 议题3：多ndax间档位不一致的MVP边界
GPT/MiniMax 并集方案 vs DeepSeek 基准+分组 vs GLM 禁止并集只检测+中止。
关键约束：下游 listCurrentLevel 是单一列表（data_loader/intCurrentLevelNum/figure_builder/plot_writer 全链路假设统一档位），并集方案意味着下游全链路改造。
要求：明确第一期(MVP)做什么、留接口给二期；给出"并集改造"的真实工作量估计。

### 议题4：无xml声明持久化（四家四方案）
QSettings版本号 vs 项目级txt vs Info_Plot.json vs 黄三角常驻。
约束：声明的目的是(a)用户知情(b)报告可追溯。可组合。
要求：选主方案+可叠加项，给出QSettings键名/文件名/JSON字段名的具体设计。

## 输出要求
- 每议题一节，先结论后论证
- 语言精炼，不要重复Round 1已说过的背景
- 最后给"实施顺序+改动文件清单"（精确到文件路径）
