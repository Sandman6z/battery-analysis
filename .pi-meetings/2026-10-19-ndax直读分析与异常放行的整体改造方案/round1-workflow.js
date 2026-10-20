const meetingDir = 'C:\\Users\\boe\\Documents\\EwinDT\\battery-analysis\\.pi-meetings\\2026-10-19-ndax直读分析与异常放行的整体改造方案';
const shared = `会议主题：NDAX直读分析与异常放行的整体改造方案。工作目录 C:/Users/boe/Documents/EwinDT/battery-analysis。首先完整阅读 ${meetingDir}/transcript.md 的用户决定与代码索引，并独立核查关键代码；Round 1 没有任何先前顾问条目，不需要读取 meeting index。只提方案、不修改源码或其他会议文件。请给出端到端实施阶段、影响文件/调用链、异常预检汇总+两次确认、缺档/坏通道的固定索引空位和报告处理、Excel仅保留独立ndax→Excel导出功能的删改边界、输出不覆盖旧结果的安全机制、测试矩阵及需用户拍板的分歧。不要重开用户已经决定的事项；发现互相冲突之处如实指出。必须用 meeting_append_entry 写入 FULL 中文分析：meetingDir=${meetingDir}；phase="Round 1"；speaker 使用你的显示名；summary 一句话；content 仅含顾问分析。最终答复只能是 WROTE_ENTRY: <一句话摘要>，不能把全文贴到聊天。`;
const roles = [
  {key:'gpt-r1', label:'提出架构与迁移路径', agent:'gpt-brainstormer', name:'GPT', emphasis:'偏战略：分析入口重塑、迁移步骤、产品交互与边界。'},
  {key:'deepseek-r1', label:'梳理数据不变量', agent:'deepseek-brainstormer', name:'DeepSeek', emphasis:'偏系统：NDAX真实数据模型、通道/档位不变量、失败恢复及一致性。'},
  {key:'minimax-r1', label:'探索异常呈现方案', agent:'minimax-brainstormer', name:'MiniMax', emphasis:'偏创造：可理解的二次确认、缺失图表显式表达、旧报告兼容。'},
  {key:'glm-r1', label:'盘点代码改造清单', agent:'glm-brainstormer', name:'GLM', emphasis:'偏落地：定位代码文件、接口变动、Excel删除边界、最小测试。'}
];
return await runs.all(roles.map(r => ({key:r.key,label:r.label,agent:r.agent,task:`${shared}\n你是 ${r.name}。${r.emphasis} meeting_append_entry 的 speaker 必须为 "${r.name}"。`})));
