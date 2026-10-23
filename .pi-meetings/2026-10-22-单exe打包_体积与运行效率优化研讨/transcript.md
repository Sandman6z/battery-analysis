# 单EXE打包、体积与运行效率优化研讨

## 议题与协议

研究当前打包命令和方式是否适合单 EXE 分发，以及构建效率、最终体积、启动和运行效率的优化路径。三轮讨论，每轮结束须用户确认才继续。源码只读；最终 conclusion.md 须另获确认。

会议黑板 entries/ 下的原始条目是完整发言的唯一权威来源，本记录通过链接保留完整发言，不改写顾问原文。

## Round 1（已结束，等待用户确认下一轮）

- [DeepSeek 完整发言](entries/0001-deepseek-round_1.md)：实际使用 PyInstaller，重点指出启动入口偏差、依赖体积与多进程取舍。
- [GPT 完整发言](entries/0002-gpt-round_1.md)：保留 PyInstaller，优先核查缓存和入口，通过 onefile/onedir 对照决定发布路线。
- [GLM 完整发言](entries/0003-glm-round_1.md)：核查真实构建命令与现有裁剪，主张测量先行和最小改动。
- MiniMax 首次尝试失败：工具报告 Subagent timed out after 1800000ms；黑板无条目，恢复记录显示 changed tracked files: none。等待至少 5 秒后按相同任务重试 1/2；重试运行 ID：0ac794c0-3ef3-480b-a2e8-4ea0aafc2f36。

## 主持人待复核项（不是最终结论）

1. DeepSeek 将 onefile 的每个 spawn worker 都独立完整解包视为关键机制；GPT 明确指出不能未经验证如此断言。须结合 PyInstaller 版本、父子进程环境继承和官方机制核实，不先采纳该论据。
2. optimize=1 不删除 docstring；DeepSeek/GLM 部分措辞有误，GPT 已正确区分等级 1 和 2。
3. no-clean 是否真正保留分析缓存，应以实际 workpath 生命周期为准；没有手写 spec 不等于没有 PyInstaller 增量缓存。
4. 延后初始化不等于后台初始化，闪屏更早出现不等于主窗口更早可操作。
5. 文档历史体积与业务计时不作为当前版本实测基准；本轮尚未执行构建或性能测量。
6. 不应清空整个 TEMP 或删除仍运行进程的 _MEI 目录来定义冷启动；首次运行、文件系统缓存和应用缓存须分别控制。

## 用户干预与停止结果

- [用户反馈原文及执行记录](entries/0004-user-feedback_during_round_1.md)：用户要求停止 MiniMax。
- 已请求停止重试运行，随后收到工具通知 `Background task stopped: minimax-brainstormer`，确认停止。本轮不再重试。
- MiniMax（minimax-brainstormer）：本轮未响应；首次超时，重试按用户要求停止，无正式分析条目。不模拟其观点。

## 第一轮结构汇总

- GPT：保留 PyInstaller，先核查缓存和入口，再以 onefile/onedir 对照决定发布路线。
- DeepSeek：关注依赖收集、启动导入图和多进程成本；其“每 worker 完整重复解包”论据未核实，不采纳为定论。
- GLM：已有较多常规裁剪，应先建立当前版本基线，再做可回滚的最小改动。
- 共识：实际构建命令为 `uv run python scripts/build.py Release`，当前采用 PyInstaller onefile；暂不盲目迁移 Nuitka，不承诺未经测量的体积或速度收益。
- 分歧：onedir 对照实验优先级、业务导入对启动的实际贡献、多进程冻结运行的具体解包机制。
- 候选优先项：核查工作缓存是否被末尾清理；统一开发/打包入口并区分闪屏、主窗口和可操作时间；根据包内清单定位体积大头；按业务阶段测量运行吞吐和进程树内存。

## Round 2（已完成，等待用户确认第三轮）

- [第一轮后用户反馈](entries/0005-user-feedback_after_round_1.md)：用户同意 GPT、DeepSeek、GLM 三位继续第二轮；MiniMax 保持停用。
- 已并行启动三位顾问，要求先通过黑板读取全部首轮发言和用户反馈，交叉核查证据、纠正技术争议，并给出最多五项优先行动及验证条件。
- 任务边界：只读研究，不修改源码、不安装依赖、不执行完整打包、不再委派；仅通过会议工具写入发言。
- 第二轮工作流 ID：1201cc49-a178-46e5-9e14-85be5da4c6df。

### 完整发言与完成核验

三位工具回执均有 WROTE_ENTRY，黑板索引确认三条正式发言存在。

- [GPT 完整发言](entries/0006-gpt-round_2.md)：保留单 EXE 主线，先完善构建日志和产物失败契约，保留 workpath 分析缓存，分阶段验证启动与体积。
- [DeepSeek 完整发言](entries/0007-deepseek-round_2.md)：撤回每 worker 重新解包与 optimize=1 去 docstring 的错误判断，重新定位 spawn 通用代价与缓存失效根因。
- [GLM 完整发言](entries/0008-glm-round_2.md)：复核缓存被末尾删除，撤回 numpy.f2py 未排除等建议，输出最小变更清单。

### 主持人第二轮结构汇总

共识：实际锁定 PyInstaller 6.17.0；保留单 EXE 默认交付；workpath 分析状态被两处清理，no-clean 只绕过前置清理；没有手写 spec 不等于没有增量机制；optimize=1 不去 docstring；历史数据不能作为当前基线；入口切换主要是提前反馈的候选，不能保证更快可操作；暂不迁移 Nuitka。

优先建议（仍未实施）：建立可追溯基线和完整日志/缺产物失败契约；修正 workpath 留存逻辑并测重复构建；入口单因素实验；按真实归档清单选择体积优化；分别测业务阶段和 worker 数的吞吐与内存。

仍有分歧：GLM 倾向 hidden-import 逐项清理，GPT 主张只有实际成员清单变化才值得投入；GLM 对入口等价和风险较乐观，GPT 提出 QT_ACCESSIBILITY、无控制台标准流和更早 freeze_support 等需核查差异；DeepSeek 对业务重库导入闭包、strip/optimize 收益的定性仍较强，不能当实测结论。

进一步口径纠正：
- 三方不再采纳每 worker 完整解包论据，但具体当前 bootloader 环境变量和复用条件尚未完成官方在线核查；不能沿用旧版 _MEIPASS2 变量名解释 6.17.0。
- 独立启动 onefile 的准备开销不只发生在安装后首次运行；OS 缓存可改变耗时，不代表后续运行无需解包。GLM 的“仅首次解压”措辞不采用。
- 缓存问题应限于被删除的 workpath 分析缓存，不等于全局二进制缓存也被删除。
- 入口切换是否影响可操作时间仍需测量，既不保证更快，也不预先断言完全不变。
- strip 的对象包含二进制符号，不能笼统写成对二进制无效；Windows 实际收益与风险待 A/B。
- 相同字节数不是缓存正确性的充分条件；验收需功能/资源一致和变更后正确失效，不能以字节数相等替代。

## 下一步

第二轮已结束，暂停等待用户决定是否进入第三轮。MiniMax 保持停用。未启动 Round 3，未生成 conclusion.md；第三轮结束后仍须用户另行确认才写最终结论。
