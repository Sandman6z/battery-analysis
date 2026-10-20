const base = "C:/Users/boe/Documents/EwinDT/battery-analysis/.pi-meetings/2026-10-16-ndax为主的数据管线重构_转换降级子功能_profile仅校验_中间格式选型";
const mk = (agent, first, stance) => ({
  agent,
  task: `会议 Round 2 对辩。先读 ${base}/round2-context.md（已定裁决、四家Round1立场速览、4个对辩议题，务必全读）。你是${first}。你Round 1的立场：${stance}。针对4个议题与另外三家辩论并收敛；议题1中间格式2:2平票必须给出你方最强论证、诚实评估混合方案后做出单选（注意：pyarrow未装、不引入新依赖、Windows、16文件批量、重复分析高频）。完成后用 meeting_append_entry 写入同一目录（speaker: ${first.split(' ')[0]}, phase: "Round 2", title: "${first} Round 2 辩论"），content 为你的完整辩论文本（Markdown）。`,
});
return [
  mk("gpt-brainstormer", "GPT愿景战略家", "xlsx落2_xlsx缓存；分层不一致处理；多ndax取并集缺失档位画N/A；项目级NO_PROFILE_DISCLAIMER.txt"),
  mk("deepseek-brainstormer", "DeepSeek数据流契约专家", "内存DataFrame直传(xlsx按需导出)；硬阻断无放行；基准文件+弹框三选；会话级声明+写Info_Plot.json"),
  mk("minimax-brainstormer", "MiniMax横向创意顾问", "DataFrame直传+parquet可选缓存；四级告警矩阵；并集+告警；首弹+黄三角常驻"),
  mk("glm-brainstormer", "GLM务实实现者", "xlsx落项目级2_xlsx缓存+manifest(mtime+size)；阻断+[以ndax为准继续]按钮+设定值层0容差实测层max(1%,0.5mA)；批内检查禁止静默取并集第一期只检测+中止；QSettings存策略版本号"),
];
