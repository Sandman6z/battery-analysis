# GLM (Round 3): 按用户五项裁决给出最终方案：show_countdown_notice 函数式组件（QMessageBox+button().setText，extra_button 支持跳转）、set_specification_type 返回 str|None 在 data_processor.py:312 单钩子检测两入口、文案走 _() 配置只放开关、跳转按钮直调 mw.show_config_dialog() 落在 Battery 首个 tab、旧 5 秒弹框迁移进组件并接受 OK(5) 升级，候选提取/去重/竞态全部出 v1。

# Round 3 — GLM 最终推荐方案（按用户五项拍板收敛）

先对齐裁决：①封装一层组件；②新型号判断**识别失败即弹**，不做候选提取；③跳转按钮进 v1，作为额外按钮；④倒计时竞态与去重靠后，不阻塞；⑤不谈工作量。以下是我的 FINAL 方案，所有代码位置均已对照实际仓库验证过。

---

## 一、组件封装形态：一个文件、一个函数、一个可选额外按钮

新建 `src/battery_analysis/main/ui_components/dialogs/countdown_message_box.py`（与现有 `ui_components/config_dialog/` 平级，目录结构顺理成章），只暴露一个函数：

```python
def show_countdown_notice(parent, *, title, text, timeout_seconds=3,
                          ok_text="OK", extra_button=None) -> str
```

- **实现基座：QMessageBox，不建 QDialog 子类**。Round 2 已裁定 MiniMax 的"必须自定义 QDialog"判断有误——`box.button(QW.QMessageBox.StandardButton.Ok).setText(f"{ok_text} ({n})")` 即可实现 "OK (3) → OK (2) → OK (1)"。自定义 QDialog 要重造居中、图标、布局、默认焦点，现有代码 `data_processor.py:406-434` 里那段"adjustSize + 手动居中"注释（QMessageBox 无 aboutToShow 信号）就是踩坑证据，不重踩。
- **倒计时驱动**：单个周期 `QTimer(1000ms)`，parent 挂在 box 上随其销毁；tick 中 `remaining -= 1`，>0 更新按钮文案，到 0 先 `timer.stop()` 再 `accept()`；`exec()` 返回后补一次防御性 `timer.stop()`（组件自身正确性，两行代码，不算竞态专项）。
- **extra_button 参数（为跳转按钮而生）**：形如 `("前往配置", callback)` 的二元组或 None。内部用 `box.addButton(text, QMessageBox.ButtonRole.ActionRole)` 添加；点击该按钮 → stop timer → `box.close()` → 执行 callback。**倒计时只作用于 OK 按钮**，额外按钮文案不动。返回值用字符串区分出口：`"ok"` / `"timeout"` / `"extra"`，调用方可感知用户选择。
- **居中逻辑**：照搬现有 `_show_spec_method_default_notice` 的 adjustSize + moveCenter 实现，连注释一起搬。

一个函数 + 一个可选参数，就同时满足了"封装一层"和"跳转按钮"两项裁决——不需要为跳转另做一套弹框。

## 二、触发点：单钩子覆盖两条入口，返回值改造是全场最无争议的改法

1. **`set_specification_type` 改返回 `str | None`**（`src/battery_analysis/main/business_logic/filename_parser.py:13-19`，当前隐式 return None）。范式就在隔壁：`set_specification_method`（`filename_parser.py:22-28`）已返回 bool 并被 `data_processor.py:315-317` 接住使用，照抄即可。唯一调用点是 `data_processor.py:312`，无动态调用，破坏面为零。
2. **`data_processor.py:312` 接住返回值**：返回 None → 置 `self._spec_missing_rules = True`。这是照抄现有 `_spec_method_defaulted` 标志位模式（`data_processor.py:48` 初始化、`:273-275` 的"处理完统一弹"链路），模式成熟。
3. **统一弹框点**：`_on_excel_files_processed()` 末尾（`data_processor.py:273` 一带）。NDAX 转换后与 XML 手动导入两条路径都汇合于 `_process_first_excel_file()`，**检测只写这一处，两入口天然覆盖**——这是四家三家独立验证过的结论，不再讨论。
4. **与既有 `_spec_method_defaulted` 叠加时合并为一个弹框**：型号未匹配和方法默认同时发生（新文件很常见）时，正文同时说明两件事，一个弹框解决，避免连环倒计时框。
5. **直接弹，不做任何候选提取**（用户裁决②）。正文显示**文件名本身**，不猜型号：文件名里充满 `DC2604`（批次码，`filename_parser.py:38` 的正则就是干这个的）、`mAh`、`(0.5-1)mA` 这类 token，正则提取必然把批次码当型号展示——错误的确定性比没有信息更糟。文案："未能从文件 <文件名> 中识别到已配置的电池型号"。

## 三、文案与路径配置来源：文案进代码走 i18n，配置只放两个开关

- **文案一律写在代码里走 `_()` 翻译管道**（`src/battery_analysis/i18n/`），补 locale 条目。拒绝把 message_template 放进 config——配置里的中文串绕开 `_()`，多语言下要么塞双语要么配置按语言分裂，收益为零。
- **路径以纯文本写入正文**："Configuration → Battery → Rules"（按实际菜单措辞校准）。这是静态指引，跳转能力由按钮承担（见下节），链接富文本不做——QMessageBox 里 `findChild(QLabel)` 连 `linkActivated` 依赖 Qt 内部实现，脆。
- **配置项仅两个开关**：在 `utils/config_defaults.py` 的 BatteryConfig 下加 `missing_rules_notice: {"enabled": True, "timeout_seconds": 3}`。注意本仓库配置链路是 config_defaults.py 默认值 + `config_manager.py` 的 `"BatteryConfig/..." → "battery..."` key 映射，**不存在 config_schema.py**，别改错地方。读不到配置时组件用默认值 3 秒兜底。

## 四、跳转按钮实现：复用现成的 show_config_dialog 入口，零新耦合

这是我 Round 2 砍掉、用户裁决③恢复的功能，恢复方式取**耦合最小的一条路**：

- 弹框增加额外按钮"前往配置"（i18n 文案），点击 → 弹框关闭 → 调用主窗口现成的 **`mw.show_config_dialog()`**（`src/battery_analysis/main/window_actions.py:121`）。
- 为什么这条路够用且最好：`ConfigDialog`（`src/battery_analysis/main/ui_components/config_dialog/dialog.py:40-46`）是 QTabWidget master-detail 结构，**第一个 tab 就是 Battery 页**（`_BatteryConfigPage`，内嵌 `_RulesEditor`，`rules_editor.py:16`，`battery_config_page.py:38`）。默认打开即落在用户要补 Rules 的地方——**不需要给 ConfigDialog 加 initial_tab 参数，不需要从弹框直连 _RulesEditor 内部**，四层导航问题消失。
- callback 由 data_processor 传入（它持有 `mw` 主窗口引用，`:310` 处 `mw.config_manager` 即证）。`show_config_dialog` 内部已有完整的异常兜底（服务未就绪弹 warning），直接复用。
- 保存配置后 `show_config_dialog` 会自动 `reload_config()` + `init_combobox()`（`window_actions.py:154-156` 一带），下拉框 items 重新从 rules 派生——**用户补完配置、重新加载文件即可识别**，"引导→补齐→恢复"链路的第一环成立，无需额外刷新逻辑。

## 五、与旧倒计时弹框的复用关系：迁移，并接受视觉升级

- `_show_spec_method_default_notice`（`data_processor.py:406-434`，QMessageBox + `QTimer.singleShot(5000, box.accept)`）**整体迁移**为调用 `show_countdown_notice(timeout_seconds=5)`，原约 30 行删除。用户拍板"封装一层"，迁移是封装的应有之义——不迁移等于留两段 90% 相同的代码各自腐化。
- 迁移后旧弹框 OK 按钮同样显示 `OK (5) → OK (1)`。我建议**直接接受视觉升级**：一个系统里两种倒计时弹框行为不一致才是坏 UX；且本次新需求本身就要求按钮旁秒数，保持一致最省心。
- 若某天确需旧行为，`countdown_on_button=False` 参数留作逃生口——本次不暴露此争论，默认升级。

## 六、v1 明确不做清单（范围纪律）

正则/启发式候选型号提取；文案模板配置化；Toast/状态栏/托盘替代形态；NDAX 转换完成但无 `4_test profile` XML 时的预检弹框（识别动作未发生，检测点跟随识别）；QSettings 持久化去重；批量导入的 debounce 合并弹框；倒计时进度条、按钮禁用（与"点 OK 立即关"语义冲突，Round 2 已裁定否决）。以上全部记入 backlog，其中内存去重 set（同文件名/型号一次会话只弹一次）与竞态防护按用户裁决④列为紧随 v1 的第一批后续项。

## 七、测试要点

1. 组件单测：秒数逐秒递减、到 0 自动 accept、点 OK 立即关且 timer 已停、extra_button 点击后关闭且回调执行一次、timeout_seconds=0 边界。
2. `set_specification_type` 返回值单测：命中返回型号、未命中返回 None、长型号优先（现有 sorted 逻辑不回归）。
3. 两条入口回归：NDAX 转换后自动加载、手动导入 XML，均应在识别失败时弹一次合并弹框（叠加方法默认场景验证合并文案）。
4. 迁移回归：旧 5 秒弹框行为不变（除按钮文案带秒数）。

## 八、残留风险（如实列出）

- **裁决②的直接后果**：文件名根本不含型号的文件（如 `test_data_001.xlsx`）也会弹框。这是用户拍板"识别到即弹"的代价，用文件名兜底文案 + 无候选不猜测来缓解，真实使用后若误弹频繁，再考虑收紧判定。
- NDAX 转换后无 XML 的场景（`_find_and_fill_test_profile` 中断）识别不发生、不弹框，属已知盲区，backlog。
- 批量导入多未知文件时 v1 可能连续弹多个框（去重被裁决靠后），backlog 的内存 set 就是解药。

**一句话总结：`show_countdown_notice` 函数式组件（QMessageBox + button().setText + 周期 QTimer + 可选 extra_button）；`set_specification_type` 返回 `str|None` + `_spec_missing_rules` 标志位照抄现有模式，单钩子 `data_processor.py:312` 覆盖两入口；文案走 `_()`、配置只放 enabled/timeout_seconds 于 config_defaults.py；跳转按钮直调 `mw.show_config_dialog()` 落在 Battery 首个 tab；旧弹框迁移进组件并接受 OK(5) 视觉升级；候选提取、去重、竞态、非弹框形态全部出 v1 范围。**
