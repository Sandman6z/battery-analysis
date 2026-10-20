# 会议记录：新电池型号缺失配置时的倒计时弹框提示与复用设计

日期：2026-10-14 · 参与者：GPT、DeepSeek、MiniMax、GLM（3 轮）+ 用户裁决

## 议题
识别到新电池型号但系统 rules 无配置时，NDAX 转换后与电池分析功能导入 XML 识别型号后两个入口都弹倒计时 3 秒提示框（OK 按钮旁显示倒计时秒数，提示补充配置路径）；与既有倒计时弹框是否复用同一段代码由讨论决定。

## Round 1（初始分析，entries 0001–0004）
- **GPT**：触发点统一策略、CountdownMessageBox 复用组件、配置路径可点击跳转等 UX 细节。
- **DeepSeek**：可复用 CountdownMessageBox 组件、修改 `set_specification_type()` 返回值、在 `_process_first_excel_file()` 增加检测点。
- **MiniMax**：抽象 CountdownDialog 基类、路径可点击化、提出非弹框替代混合方案。
- **GLM**（基于实际代码）：两入口汇合于 `data_processor` 单一钩子点；现有弹框需升级加"按钮旁秒数"；最大不确定性是"新型号识别"判定逻辑。

## Round 2（质询与改进，entries 0005–0008）
- **GPT**：共识=共享倒计时组件+单钩子点；否决文案模板入库；提出两阶段新型号检测（候选提取不到不弹）+"立即配置"跳转闭环。
- **DeepSeek**：指出被忽视风险——NDAX 无 XML 中断、倒计时竞态、批量弹框队列。
- **MiniMax**：质询弹框必要性，提出两阶段灰度升级。
- **GLM**：纠错 MiniMax（不必自定义 QDialog、触发点误定位）；否决正则提取型号与文案模板配置化；修正工作量口径为 1 天；收敛设计=QMessageBox+button().setText 共享组件、单钩子点、合并弹框、内存去重；链接跳转降 backlog。

## 用户裁决（entry 0009）
1. 封装一层组件 ✔
2. 新型号判断直接弹框（不做两阶段候选提取）✔
3. 跳转按钮要做，作为额外按钮进 v1 ✔
4. 倒计时竞态优先级靠后 ✔
5. 不再讨论工作量估计 ✔

## Round 3（最终综合，entries 0010–0013）
- **GPT**：共享 CountdownMessageBox + 单钩子点直接弹框 + "立即配置"跳转按钮进 v1 + 型号缺失与方法默认合并弹框防轰炸 + 配置仅放行为参数不碰文案。
- **DeepSeek**：函数式 API 封装组件、QMessageBox+button.setText 倒计时、直接弹框显示文件名、"前往配置"按钮跳 Rules 页、旧弹框迁移保留逃生开关、行为参数配置+内存去重。
- **MiniMax**：封装 CountdownMessageBox、统一触发点、v1 含跳转按钮、旧弹框同步升级。
- **GLM**：`show_countdown_notice` 函数式组件（QMessageBox+button().setText，extra_button 支持跳转）、`set_specification_type` 返回 str|None 在 `data_processor.py:312` 单钩子检测两入口、文案走 `_()` 且配置只放开关、跳转按钮直调 `mw.show_config_dialog()` 落在 Battery 首个 tab、旧 5 秒弹框迁移进组件并升级为 OK(5) 样式、候选提取/去重/竞态全部出 v1。

## 最终共识（Round 3 收敛）
| 维度 | 结论 |
|---|---|
| 组件 | 封装一层共享倒计时组件（QMessageBox + button().setText，函数式 API），新旧弹框统一 |
| 触发点 | `data_processor.py:312` 单钩子点，`set_specification_type()` 返回 str|None，一处覆盖 NDAX/XML 两入口 |
| 检测逻辑 | 识别到即直接弹框（显示识别文件名/型号），不做正则候选提取 |
| 跳转按钮 | 额外按钮"立即配置/前往配置"，直调 `mw.show_config_dialog()`，进 v1 |
| 文案与配置 | 文案走 `_()` 国际化，配置文件仅放行为参数（秒数、开关），文案模板不入库 |
| 旧弹框 | 迁移进共享组件，接受 OK(5) 升级样式 |
| 出 v1 | 候选提取、弹框队列/去重、倒计时竞态（后续事项） |
