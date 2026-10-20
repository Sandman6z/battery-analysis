# Round 1 议题背景（主持人提供）

## 背景取证事实（已完成的调查结论，供引用）

1. **报告崩溃 bug**：分析软件从【文件名】解析脉冲档位（30/26/15/6，来自陈旧 Remark），按该档位数遍历画曲线，但实测数据是 60/30/15/6，26mA 档无数据 → `src/battery_analysis/utils/processors/data_utils.py:42` `filtered_mask[0]=True` 越界 IndexError，报告写到曲线阶段崩（figure_builder 对全部 16 只电池报 level 1 空）。
2. **ndax 本质是 ZIP**：内嵌 `Step.xml`（实际执行配方，`<PulseData>` 含真实档位=权威）、`TestInfo.xml`（SN/开始时间/电流量程）、`data.ndc`（二进制原始时序，NewareNDA 库 `nda.read` 可解析成 DataFrame）。文件名来自陈旧 Remark，不可信。
3. **5 项目全量核验零例外**：4 个项目 profile xml ↔ ndax/xlsx 实测档位逐档一致（BattData_ndax 9/9、BattData_normal 32/32、lowTemp、PouchBatt 均与 xlsx 实测吻合）；唯一不一致是 CF224642T（桌面 profile 是 2024 年 CP224642A 旧模板，只改了文件名）——恰是崩溃项目。
4. profile 与 ndax Step.xml 的结构差异（profile 多 `Whole_Prt` 整机保护/记录配置，Step.xml 多单工步 `Limit` 截止条件）经 41 个 ndax 核验为序列化路径差异，**良性**，不参与数据分析。
5. **现管线**：主UI『ndax转excel』tab → `src/battery_analysis/ndax/converter.py`（NewareNDA，xlsxwriter 分 Record/Step/Cycle 三表、百万行分表 Record_2/3）→ `2_xlsx/` → `data_processor.py`（从文件名解析档位 ~340-349 行 + 读 xlsx 取数）→ `3_analysis results/{date}_v{ver}` → 报告（Word/图表）。报告阶段既有的空档位防御缺口（filter_data 越界）尚未修。
   相关文件：`main/tabs/ndax_tab.py`、`main/business_logic/data_processor.py`、`utils/writers/info_csv_writer.py`、`utils/writers/plot_writer.py`、`utils/processors/data_utils.py`、`main/visualization/figure_builder.py`、`main/visualization/data_loader.py`（`read_xlsx_sheets`、Info_Plot.json）。
6. PDF `BatteryQualityRequirements_v2.3` §7.1.1 定义各容量档脉冲电流（软包<1200mAh→30/26/15/6，1200-2000mAh→60/30/15/6，2000-3000→100/60/30/15/6 等），config 有 `BatteryConfig/Rules` 与 `SpecificationTypePouchCell` 查表机制（CF224642T 不在 Rules 中）。
7. 代码中档位来源现有三处：文件名解析（优先）、config 查表兜底（`lookup_pulse_currents`）、数据实测（可从 data.ndc Status=Pulse 分组或 xlsx Record 统计）。

## 用户提案（本次议题，评估对象）

- **A. ndax 为主**：把主UI上第一个『ndax转excel』功能去掉主位，降级为子功能——和 batteryChartViewer 一样，在它上面放一个按钮，点开才有这个功能。
- **B. 界面上不再通过 xml profile 带出数据**，改通过 ndax 识别，依然能识别到其他所有数据（这部分需重新识别）。
- **C. profile xml 仍自动查找，但只做验证**：验证其脉冲电流与 ndax 是否一致，一致→继续，不一致→报错。允许用户不提供 xml：没有 xml 时弹框提示、允许继续、只依靠 ndax 分析，并声明一次。
- **D. 中间格式选型**：具体分析用 excel 还是现成转换 ndax 后把 excel/csv 放临时文件夹——按最高效率、最不易出错的方式选型；数据处理分析后结果写入 3_analysis results 对应版本文件夹，再生成报告。

## 每位顾问 Round 1 必答的五个问题

1. 逐条评估提案 A–D 的合理性、风险、遗漏（各自专业视角）。
2. **中间格式给出明确单选建议**（xlsx / csv / parquet / 内存 DataFrame 直传 / 混合），多维度论证：效率、出错面、可审计性、重复分析成本、既有代码改动量。
3. 列出『通过 ndax 识别其他所有数据』的**重新识别清单**（Step.xml/TestInfo.xml/data.ndc 各能给什么；原来从 profile/文件名来的是什么；哪些给不了）。
4. profile 验证策略边界情况：不一致报错 vs 告警放行？无 xml 弹框声明一次够不够？多 ndax 文件间档位不一致怎么办？
5. 报告阶段空档位防御（filter_data 越界）**是否仍需兜底**——给出明确意见。
