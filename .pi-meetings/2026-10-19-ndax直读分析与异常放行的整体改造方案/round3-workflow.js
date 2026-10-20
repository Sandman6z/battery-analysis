const meetingDir='C:\\Users\\boe\\Documents\\EwinDT\\battery-analysis\\.pi-meetings\\2026-10-19-ndax直读分析与异常放行的整体改造方案';
const shared=`你是本项目第三轮顾问，仓库 C:/Users/boe/Documents/EwinDT/battery-analysis。必须先调用 meeting_read_index({meetingDir:${meetingDir}})，再用 meeting_read_entry 阅读黑板上 ALL Round 1、Round 2 顾问条目及所有 User Feedback 条目（包括 0005、0009、0010），不可只看摘要；此前 GLM Round 2 资源不足无有效条目，不要替其编造观点。用户新裁决优先：原有 Excel/Word/CSV/JSON/图像报告全部保留，Excel 退出分析输入/中间链；profile 不一致在点击分析前、实测档位或通道异常在点击后汇总两次确认；一次读取优先但请核实内存论据；原有 SHA256.csv 版本递增继续使用，删除 analysis_worker.py 两处同名即 rmtree，不加新 _r2 版本体系；只有全部报告成功后次版本递增，失败或取消仅清理本次运行独占创建的半成品，旧目录绝不动。检查关键实际调用链、大小写 V/v、报告写入器独立拼目录和信号无条件递增等风险，提出可交付的整体分阶段方案、数据结构与占位契约、GUI 线程边界、成功门槛/失败清理测试矩阵。清楚区分已证实代码事实与尚未有真实 NDAX 样本支持的假设。不重开用户裁决、不改源码。最终推荐需简洁明确列未决事项。用 meeting_append_entry 写中文 FULL 结论：meetingDir=${meetingDir}，speaker 为你的显示名，phase="Round 3"，summary 一句话，content 仅含顾问分析；最终答复 ONLY WROTE_ENTRY: <一句话摘要>，不贴全文。`;
const roles=[
{key:'gpt-r3',label:'收敛最终架构方案',agent:'gpt-brainstormer',name:'GPT',focus:'重点核查提交时序与现有版本机制的最小改动。'},
{key:'deepseek-r3',label:'收敛结果一致性方案',agent:'deepseek-brainstormer',name:'DeepSeek',focus:'重点核查报告写入路径、半成品所有权和成功条件。'},
{key:'minimax-r3',label:'收敛用户交互方案',agent:'minimax-brainstormer',name:'MiniMax',focus:'重点核查零伪造空位、两次确认与保留全部报告。'},
{key:'glm-r3',label:'收敛实施与测试清单',agent:'glm-brainstormer',name:'GLM',focus:'Round 2 你因资源不足未写条目，本轮请基于黑板重新参与，重点排可验收的修改清单。'}
];
return await runs.all(roles.map(r=>({key:r.key,label:r.label,agent:r.agent,task:`${shared}\n你是 ${r.name}。${r.focus} meeting_append_entry speaker 必须为 "${r.name}"。`})));
