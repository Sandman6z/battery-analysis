# 会议背景与决策记录（截至 Round 1 启动）

主题：继续制定 battery-analysis 项目 NDAX 直读分析、profile 校验、异常人工放行及 Excel 边界的整体修改方案。本文件是先前用户讨论的决策摘要，并非本次顾问意见。旧会议定案可参考 `.pi-meetings/2026-10-16-ndax为主的数据管线重构_转换降级子功能_profile仅校验_中间格式选型/entries/0014-主持-final.md`；如下用户新决定覆盖其中冲突部分。

## 用户最新决定
1. NDAX 无论是否实际完成，本阶段均按可继续分析处理；若 Step.xml 有明确完成状态且显示完成，可直接通过完成性检查；若无字段，默认可放行。不再依赖“未完成”状态硬阻断。
2. 某档位找不到脉冲、某通道失败时不默认中止整批：先预检汇总全部异常，弹框问「是否停止整批」；若选继续，再弹一次明确确认；确认后保留故障通道/档位的空位，不可错位、伪造零值。应留下异常与用户决定记录。
3. 主分析全程使用 ndax：Step.xml 作为配方档位来源；NewareNDA `nda.read()` 读取 data.ndc 时序 DataFrame，派生分析所需结构。分析输入链路不得扫描/读取 2_xlsx，不经 xlsx 中间层。用户进一步明确 Excel 只存在于独立 ndax→Excel 导出功能，其他 Excel 逻辑全部移除（包括 Excel 报告；需要讨论连带影响）。
4. 无 profile 可运行，test_profile 从必填校验排除；无 profile 一次性免责声明；有 profile 只做与 ndax 档位比较。同数不同档值需明确阻断+以 ndax 为准继续按钮，默认中止；档数不一致同样给人工确认出口，不用不可验证的完成状态判断；多 ndax 配方档位不一致硬阻断（旧定案，用户尚未更改此项）。实测中位数偏差 >max(1%,0.5mA) 原为黄色告警放行留痕，需要与新“找不到脉冲”分清。
5. 校验/用户确认应发生于删除旧结果前；成功写 Info_Plot.json.profile_validation 留痕、policy_version `2026.10`，QSettings `validation/profile_disclaimer_version`；profile 留痕不能被后续写入覆盖。
6. 现有 `filter_data()` 空档位越界仍须 P0 防御；但缺脉冲可人工放行继续，不能静默丢通道。图表/Word/JSON 需要显式缺失语义和固定通道索引。

## 已核对的代码现状（供各顾问独立复核）
- `src/battery_analysis/ndax/converter.py`：`nda.read()`→按 Cycle/Step/Record 写 xlsx；`ndax/worker.py`、`main/tabs/ndax_tab.py` 为独立导出功能。
- `main/business_logic/data_processor.py`：只扫 xlsx，首文件文件名解析档位并写全局配置；`utils/file_validator.py` 强制输入目录为 2_xlsx；`main/managers/path_manager.py` 自动定位 2_xlsx。
- `utils/processors/battery_analysis.py`：scan_sorted_xlsx、read_xlsx_sheets、并行逐文件分析，Windows 失败跳过继续；`utils/processors/pulse_matcher.py` 对未匹配档位留下空列表；`utils/processors/data_utils.py` 空列表 filtered_mask[0] 越界。
- `main/workers/analysis_worker.py`：分析前删除已有同版本结果目录，后续也可能删除同名最终目录。
- `utils/writers/info_csv_writer.py`：Info_Plot.json 整体覆写，尚无 profile_validation；`main/visualization/data_loader.py` 按全局 battery.pulseCurrents 解释 Info_Image.csv，读取空行时不补占位；图表绘制按电池下标访问。
- `utils/input_validator.py` 与 `main/business_logic/validation_feedback.py` 要求 test_profile 必填。

## Round 1 交付
在代码证据基础上给出整体改造方案：端到端数据流、输入验证与异常汇总/两次确认、保留空位的数据模型、所有受影响调用链和删除/保留边界、输出落盘时机/防数据丢失、迁移和最小可验证测试；指出用户决定之间的潜在冲突或必须拍板的问题。只讨论，不改代码。顾问全文写 meeting blackboard，勿写进聊天。

## Round 1 收件（2026-10-19）
四位顾问均已写入黑板：GLM entries/0001、MiniMax entries/0002、GPT entries/0003、DeepSeek entries/0004。共识：主分析改 ndax 直读、数据缺失占位不压缩、异常汇总与二次确认、profile 可选、结果先暂存避免覆盖、Excel 仅保留独立导出；关键分歧：一次读取先算不写与二次读取预检、空位 CSV 格式、同名结果策略、完成状态是否展示、Word 报告去 Excel 引用。MiniMax 声称空输入过滤已有防御，与实际 `data_utils.filter_data` 空数组越界代码不符，下一轮应核证。Round 1 后暂停，等待用户反馈或授权 Round 2。

## Round 1 后用户反馈
见黑板 entries/0005-user-feedback_after_round_1.md。用户要求原有所有报告保留（包含 Excel 双工作簿）；profile 不一致在点击分析前处理，数据异常在点击分析后汇总处理；询问一次/两次读取效率、标记含义、旧结果定义。主持人解释后进入 Round 2。

## Round 2 收件
MiniMax entries/0006、GPT entries/0007、DeepSeek entries/0008 均完成；GLM 请求接口返回 429「余额不足或无可用资源包」，无有效 Round 2 条目，未用他人代写。三家共同修订：Excel 仅退出输入/中间层，所有报告及 Word→Excel 链接保留；一次读取、逐文件派生并释放原始 DataFrame；Info_Image.csv 固定行数、缺位空行，读端补位、原因存 JSON；结果同名自动避让、不删除旧目录；profile 提前，实测异常点击后主线程两次确认。新关键证据：report_coordinator.py/json_writer.py 与 analysis_worker.py 各自重新拼输出目录名，若只给 worker 目录加后缀，写入器会写到原旧目录；必须统一输出目标路径。仍需 Round 3 追问目录命名接口、异常记录数量一致性、Step.xml 完成状态无证据时默认放行，以及经真实 ndax 计时/内存测量。

## Round 2 后用户反馈
见黑板 entries/0009 与 entries/0010。用户指出已存在 `SHA256.csv` 主/次版本递增，要求禁止同名旧目录删除；失败或取消仅清本次半成品且版本不递增。现代码确有 `set_version()` 递增，但 `thread_end` 无条件触发，失败/取消也计次；用户要求修正。Round 3 必须沿用现有版本机制，不另造 `_r2`。

## Round 3 收件
MiniMax entries/0011、GPT entries/0012、DeepSeek entries/0013；GLM Round 3 再次 429 无条目，连续两轮不可用。主要共识：删 worker 两处同名 rmtree，碰撞安全拒绝；先统一测试日期/输出目录单一决议并下发给所有写入器，修 `V/v` 大小写和 Word docx 根目录散件；`thread_end` 保持无条件用于 UI 复位，新建仅成功发射的信号给 `set_version`；失败/取消只清本次创建的路径并不计次；一次 `nda.read()` 后逐文件派生即释放；CSV 不插 MISSING 行，空行占位读端补位，原报告种类全部保留。注意 MiniMax 0011 §1.4/阶段 6 仍推荐 `_r{n}` 后缀，与用户 0010 矛盾，不能采纳；其 V/v 在 Windows 上两个独立目录的推断也不成立，大小写分裂只在大小写敏感文件系统。DeepSeek 提出 docx 写于结果根目录且可能同名覆盖，应纳入碰撞检查与清理白名单。尚无真实 NDAX fixture，Step.xml 字段和性能数字仅为待验证假设。Round 3 后暂停，待用户确认才写 conclusion.md。

## 最终裁决与输出
见黑板 entries/0014-user-feedback_after_round_3.md：Step.xml 直接提供配方档位；实际测试日期来自 ndax 实测 Timestamp，经统一校验后只决定一次并显式传给全部写入器；内部目录小写 v，版本沿用 SHA256.csv 成功计次。此裁决和 entries/0005/0009/0010 优先于本文 Round 1 启动背景中关于删除 Excel 报告的历史记录，**Excel 报告全部保留**。用户随后明确回复「写结论」，最终方案已写入本目录 `conclusion.md`。会议阶段仅写方案，源码未修改。
