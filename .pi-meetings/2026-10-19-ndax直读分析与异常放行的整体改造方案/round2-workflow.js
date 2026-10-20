const meetingDir='C:\\Users\\boe\\Documents\\EwinDT\\battery-analysis\\.pi-meetings\\2026-10-19-ndax直读分析与异常放行的整体改造方案';
const shared=`你参与 battery-analysis 项目“NDAX直读分析与异常放行的整体改造方案”Round 2。先调用 meeting_read_index({meetingDir:${meetingDir}})，再用 meeting_read_entry 逐一读完 Round 1 四位顾问的全文以及 User Feedback after Round 1（0005）；不要假设已看到其他顾问内容，不要从任务正文推断上一轮具体观点。随后针对其他方案的证据弱点交叉质询，提出改进与清晰单选。重点：用户最新反馈优先——保留所有原有报告种类，包括 Excel 报告，Excel 仅退出分析输入和中间层；profile 不一致在运行前确认、点击分析后才能汇总实测异常并两次确认；给出一次读取与两次读取的性能/内存选择、内部缺失空位最小兼容协议、同名已有报告安全处理方式。核查代码证据；特别注意不得直接从后台线程弹 Qt 对话框、不得假称 Step.xml 一定有完成状态、不能误删报告输出。只讨论，不改代码。将完整中文意见调用 meeting_append_entry 写到 meetingDir=${meetingDir}，speaker 用你的显示名，phase="Round 2"，summary 一句话，content 只能含分析；最终答复只能是 WROTE_ENTRY: <一句话摘要>，不得贴全文。`;
const roles=[
{key:'gpt-r2',label:'质询架构及性能取舍',agent:'gpt-brainstormer',name:'GPT',focus:'重点辩一次读取 vs 二次读取的时间/内存、点击运行后的决策时序。'},
{key:'deepseek-r2',label:'质询数据不变量',agent:'deepseek-brainstormer',name:'DeepSeek',focus:'重点辩占位协议及全套报告完整性、异常汇总正确性。'},
{key:'minimax-r2',label:'修订报告交互方案',agent:'minimax-brainstormer',name:'MiniMax',focus:'上一轮建议删 Word/Excel 报告、认为 P0 已有防御，与用户新决定及代码可能矛盾；请诚实复核后给出修订。'},
{key:'glm-r2',label:'质询落地删改清单',agent:'glm-brainstormer',name:'GLM',focus:'重点辩 Excel 报告保留时需改的调用链、同名结果防覆盖、两次确认可实现性。'}
];
return await runs.all(roles.map(r=>({key:r.key,label:r.label,agent:r.agent,task:`${shared}\n你是 ${r.name}。${r.focus} meeting_append_entry 的 speaker 必须为 "${r.name}"。`})));
