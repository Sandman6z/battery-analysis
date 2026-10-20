# GLM (Round 1): 基于实际代码的分析：两条入口汇合于 data_processor 单一钩子点，建议抽取共享倒计时弹框组件复用（现有弹框需升级为按钮旁显示秒数），总工作量约 1 天，最大不确定性在"新型号识别"判定逻辑。

# Round 1 — 务实落地分析：新电池型号缺失 rules 配置的倒计时弹框

我已浏览过仓库实际代码（PyQt6 应用，`src/battery_analysis/`），以下分析基于真实代码结构，不是凭空设想。

## 一、关键事实：两条入口最终汇合同一个钩子点

**入口 A（NDAX 转换后）**：`src/battery_analysis/main/tabs/ndax_tab.py` 的 `_on_finished()`（转换完成回调）末尾调用 `_find_and_fill_test_profile()`，后者设置 TestProfile/输入输出路径并 `mw.sigSetVersion.emit()`。

**入口 B（独立 Excel + 导入 XML）**：用户手动选 XML → `src/battery_analysis/main/managers/path_manager.py` 校验后同样 `sigSetVersion.emit()`（`path_manager.py:173/232/260`）。

两条路都汇入电池分析的数据流：`data_processor.get_xlsxinfo()` → 后台扫描/解析 Excel → `_on_excel_files_processed()`（`src/battery_analysis/main/business_logic/data_processor.py:232`）→ `_process_first_excel_file()`（`data_processor.py:297`）→ `filename_parser.set_specification_type()` 从文件名识别型号（`src/battery_analysis/main/business_logic/filename_parser.py:13`）。

**务实结论：不需要在两处分别弹框。在 `_process_first_excel_file` 识别型号后做一次 rules 匹配检查，即可同时覆盖两个场景**，逻辑只写一遍。

## 二、现有倒计时弹框的真实形态与复用可行性

现有弹框是 `_show_spec_method_default_notice()`（`data_processor.py:406-434`）：QMessageBox + `QTimer.singleShot(SPEC_METHOD_NOTICE_TIMEOUT_MS=5000, box.accept)`，5 秒自动关、点 OK 立即关、居中于主窗口。

**关键差距：它并没有在 OK 按钮旁显示剩余秒数**——新需求明确要求"OK 按钮旁边显示倒计时秒数"。所以"复用"不是零成本拷贝，而是把现有方法升级抽取为共享组件。

**复用方案（推荐做）**：
- 新建 `src/battery_analysis/ui/dialogs/countdown_message_box.py`（或放 `main/ui_components/dialogs/`），提供函数级 API：
  `show_countdown_notice(parent, title, text, timeout_seconds, ok_text="OK", show_countdown_on_button=True)`
- 实现要点：`QTimer` 每 1 秒 tick，更新 `box.button(Ok).setText(f"{ok_text} ({n})")`，倒数到 0 调 `box.accept()`；保留现有居中逻辑（adjustSize + moveCenter，注释里已说明 QMessageBox 无 aboutToShow 信号的原因，直接照搬）。
- 迁移现有调用点 `_show_spec_method_default_notice` 改为调共享组件（timeout=5），两个调用点只差文案和秒数。
- 成本：共享组件约 1 小时，迁移 + 回归约 1 小时。**两段代码 90% 相同，不复用才是浪费**。唯一需要拍板的：升级后旧弹框的 OK 按钮也会显示 `OK (5)` 倒数——建议接受（视觉一致性更好），若不想动旧 UX 可加开关参数。

## 三、具体实现步骤

1. **共享倒计时弹框组件**（见上节）。秒数建议走配置（见步骤 4），默认 3 秒。

2. **缺配置检测逻辑**（核心工作量所在）：
   - 在 `_process_first_excel_file()` 识别出 `spec_name` 后，调 `capacity_from_rules(rules, spec_name)`（`src/battery_analysis/utils/pulse_currents.py:189`，未命中返回 0.0）判断该型号是否在 `BatteryConfig/Rules` 中。
   - 未命中 → 置 `_spec_missing_rules = True`（完全照抄现有 `_spec_method_defaulted` 标志位模式，`data_processor.py:272-275` 已有成熟的"处理完再弹框"链路），在 `_on_excel_files_processed()` 末尾弹倒计时框。
   - **必须诚实指出的坑**：`set_specification_type` 的匹配目标列表本身就是从 rules 派生的（`utils/battery_classifier.py:39` `derive_specifications`，单一数据源 `battery.rules`，见 `config_manager.py:33/111`）。**新型号不在 rules 里时，型号下拉框根本匹配不上**，`currentText()` 可能是空或残留旧值。所以"识别到新电池型号"需要一个独立的文件名型号提取逻辑（比如从文件名里抽出形如 CR2450/CP305050 的型号 token 再对 rules 查找），这是本次需求里唯一有设计含量的点，建议会上明确"识别"的准确定义。

3. **去重**：一次扫描可能有多个文件、同一型号只弹一次；不同型号各自弹。参考现有 generation 守卫模式防过期弹框。

4. **文案与路径配置化**：
   - 在 `utils/config_defaults.py` 的 BatteryConfig 下加 `missing_rules_notice: {enabled, timeout_s, message}`，message 含 `{rules_path}` 占位符。
   - 路径指向 rules 编辑入口（`main/ui_components/config_dialog/battery_config_page.py` 的 `_RulesEditor`）或配置文件实际位置。
   - i18n：新增文案走 `_()` 并补 locale 条目（`src/battery_analysis/i18n/`）。

5. **测试**：`tests/` 下补共享弹框组件的单测（秒数递减、到时自动关、OK 立即关）+ 型号检测逻辑的纯函数单测。

## 四、工作量评估

| 项 | 估计 |
|---|---|
| 共享倒计时弹框 + 迁移旧调用点 | ~2h |
| 缺配置检测 + 文件名型号提取 | ~3-5h（不确定性集中在此） |
| 配置项 + i18n 文案 | ~2h |
| 单测 + 回归 | ~2-3h |
| **合计** | **约 1 个工作日** |

## 五、风险与待拍板问题

1. **"识别到新电池型号"的定义**（最大不确定性）：rules 是型号列表的唯一数据源，不在 rules 里的型号现有代码"看不见"。需要定文件名提取规则，或改 `set_specification_type` 返回匹配状态（类似 `set_specification_method` 已返回 bool 的做法，`filename_parser.py:20`——这是现成的范式，改造成本低）。
2. NDAX 转换完成后若无 `4_test profile` XML，`_find_and_fill_test_profile` 会中止流程，型号识别不会发生——这种场景要不要弹框，需明确。
3. 弹框升级对旧场景（规格方法默认提示）的视觉影响：OK → OK(5)。
4. 线程安全无忧：弹框在主线程回调里触发，与现有 `_show_spec_method_default_notice` 同一模式。

**一句话立场：复用共享倒计时组件（推荐）、单钩子点覆盖两条入口、总工作量约 1 天；唯一需要会上认真讨论的是"新型号识别"的判定逻辑，其余都是照现有模式抄作业。**