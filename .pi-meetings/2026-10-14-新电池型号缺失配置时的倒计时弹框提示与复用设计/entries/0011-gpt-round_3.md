# GPT (Round 3): FINAL 推荐方案：共享 CountdownMessageBox 组件 + 单钩子点直接弹框 + 跳转按钮进 v1 + 合并弹框防轰炸 + 配置仅放行为参数

# Round 3 — 最终综合建议（愿景型策略师）

## 前言：用户已拍板五项决策

1. ✅ 封装一层组件（共享 CountdownMessageBox）
2. ✅ 新型号判断**直接弹框**（不做两阶段候选提取，`set_specification_type()` 返回 None 即弹）
3. ✅ 跳转按钮要做（"立即配置"作为额外按钮进 v1）
4. ⏳ 倒计时竞态优先级靠后（不阻塞本次）
5. 🚫 不再讨论工作量估计

以下方案严格遵循这五项裁决，综合四家三轮讨论的最佳想法，给出可直接执行的最终设计。

---

## 一、组件设计：CountdownMessageBox

### 1.1 定位与接口

新建 `src/battery_analysis/main/ui_components/dialogs/countdown_message_box.py`，提供函数式 API：

```python
def show_countdown_notice(
    parent: QWidget,
    *,
    title: str,
    text: str,
    timeout_seconds: int = 3,
    ok_text: str = "OK",
    countdown_on_button: bool = True,
    extra_buttons: list[tuple[str, callable]] | None = None,
) -> str | None
```

- 返回值：被点击按钮的文本（用户点哪个按钮返回哪个字符串），倒计时自动关闭返回 `None`
- `extra_buttons`：可选的额外按钮列表，每项为 `(按钮文本, 点击回调)`；用于 v1 的"立即配置"跳转按钮

### 1.2 实现要点

- **底层用 `QMessageBox`**，不用自定义 QDialog。四家三轮讨论已达成共识：`box.button(StandardButton.Ok).setText()` 完全可改按钮文本，PyQt6 下已验证（GLM R2 质询 MiniMax 的"必须自定义 QDialog"为误判，DeepSeek R2 裁决确认）
- 倒计时驱动：`QTimer(1000ms)` 每秒 tick，更新 `ok_button.setText(f"{ok_text} ({remaining})")`，到 0 时 `timer.stop()` + `box.accept()`
- `exec()` 返回后防御性 `timer.stop()`（DeepSeek R2 指出的 QTimer 清理保障）
- 居中逻辑照搬现有 `_center()` 实现（`adjustSize` + `moveCenter`，含"QMessageBox 无 aboutToShow 信号"的已知 workaround）
- **按钮不设 `setEnabled(False)`**（用户裁决：倒计时期间可随时点 OK 立即关闭，与需求一致；GLM R2 和 DeepSeek R2 均反对 MiniMax 的禁用提案）

### 1.3 迁移现有弹框

`data_processor._show_spec_method_default_notice()`（`data_processor.py:406-434`）迁移为调用 `show_countdown_notice(timeout_seconds=5)`，删掉原有 30 行内联代码。旧弹框 OK 按钮同步升级为显示 `OK (5)` 倒数——**视觉一致性**：一个系统里两种倒计时弹框行为不一致才是坏 UX（GLM R2 + GPT R2 共同立场）。如需保留旧行为，传 `countdown_on_button=False` 即可。

---

## 二、触发点与检测逻辑

### 2.1 单钩子点（四家共识，无需再议）

两条入口最终汇合于 `data_processor._process_first_excel_file()`（`data_processor.py:297`）中的 `filename_parser.set_specification_type()` 调用处（`data_processor.py:312`）：

- **入口 A（NDAX 转换后）**：`ndax_tab._on_finished()` → `_find_and_fill_test_profile()` → `sigSetVersion.emit()` → `data_processor.get_xlsxinfo()` → `_process_first_excel_file()`
- **入口 B（手动导入 XML/Excel）**：`path_manager` 校验 → `sigSetVersion.emit()` → 同上

检测逻辑只写一遍，两个入口天然覆盖。

### 2.2 新型号判定（用户裁决：直接弹框）

用户明确拍板"新型号判断直接弹框"，不做两阶段候选提取。方案简化为：

1. **改造 `set_specification_type()` 返回 `str | None`**（照抄 `set_specification_method` 返回 `True/False` 的现成范式，`filename_parser.py:20-28`；唯一调用点在 `data_processor.py:312`，破坏面可控）
2. **返回 `None` → 直接置标志位** `self._spec_missing_rules = True`，照抄现有 `_spec_method_defaulted` 的"处理完统一弹"链路（`data_processor.py:272-275`）
3. **弹框文案中显示文件名**（GLM R2 的务实建议：文件名兜底，不猜测型号。正则提取候选型号被 GLM 和 DeepSeek 均质疑误报风险——如 `DC2604` 批次码会被误提为型号。用户裁决不做候选提取，文件名即是最安全的展示内容）

### 2.3 型号缺失 + 方法默认的合并弹框

当型号未匹配（`_spec_missing_rules = True`）与方法未匹配（`_spec_method_defaulted = True`）同时发生时，**合并为一个弹框**（GLM R2 提案），文案同时说明两件事。避免连环弹两个倒计时框轰炸用户。合并逻辑放在 `_on_excel_files_processed()` 末尾的弹框触发处，优先级：型号缺失文案优先展示，方法默认信息作为补充段落。

### 2.4 NDAX 转换后无 XML 的场景

当 `4_test profile` 目录无 XML 时，`_find_and_fill_test_profile()` 中止流程，`_process_first_excel_file()` 不执行。**本次不覆盖**（DeepSeek R2 建议），在弹框文案中加入兜底指引即可。后续迭代再考虑在 `_on_finished()` 中增加独立预检。

---

## 三、文案与路径配置

### 3.1 弹框文案（i18n，不入配置）

```
标题：_("电池型号配置缺失")
正文：_("未在系统配置中找到电池型号。\n\n文件：{filename}\n\n请前往以下路径补充 Rules 配置：\n设置 → 电池配置 → Rules")

合并弹框（型号+方法同时缺失）：
正文：_("未在系统配置中找到电池型号。\n\n文件：{filename}\n\n规格方法未匹配，已使用默认值：{method}\n\n请前往以下路径补充配置：\n设置 → 电池配置 → Rules")
```

文案走 `_()` 翻译管道 + 补 `src/battery_analysis/i18n/` locale 条目。**不入 JSON 配置**——文案模板入库与 i18n 冲突（GLM R2、GPT R2 均指出：配置里的中文字符串走不了 `_()`，多语言场景下要么模板塞双语要么配置按语言分裂，复杂度远超收益；文案变更频率极低，改代码发版成本与改配置重启几乎相同）。

### 3.2 配置只放行为参数

在 `utils/config_defaults.py` 的 BatteryConfig 下新增：

```python
"missing_rules_notice": {
    "enabled": True,
    "timeout_seconds": 3,
}
```

仅此两个字段。`enabled` 方便运维关闭弹框，`timeout_seconds` 支持调整倒计时。未来如需"不再提醒"复选框等扩展，也只加行为开关，不碰文案。

---

## 四、跳转按钮（用户裁决：进 v1）

### 4.1 设计

在 OK 按钮旁增加一个额外按钮 **"立即配置"**，点击后：

1. 关闭弹框
2. 打开应用内配置对话框，定位到 `battery_config_page.py` 的 `_RulesEditor`（Rules 编辑页）

### 4.2 实现路径

通过 `CountdownMessageBox` 的 `extra_buttons` 参数传入：

```python
show_countdown_notice(
    parent=self.main_window,
    title=_("电池型号配置缺失"),
    text=_(...),
    timeout_seconds=3,
    extra_buttons=[(_("立即配置"), self._open_rules_editor)]
)
```

- `_open_rules_editor()` 是 `DataProcessor` 的新方法，负责打开配置对话框并切换到 Rules 页
- 跨模块调用链：弹框回调 → `DataProcessor._open_rules_editor()` → 主窗口的配置对话框 API → `battery_config_page._RulesEditor`
- **链接失效兜底**（MiniMax R1 边缘情况 4）：如果配置对话框打开失败（如配置文件被删），catch 异常后弹一条轻量提示"配置页面不可用，请从菜单 → 设置 → 电池配置进入"
- QMessageBox 的 `addButton(text, ButtonRole.ActionRole)` 支持添加额外按钮，不需要自定义 QDialog

### 4.3 不做的降级方案

- 不做 `QLabel` 富文本 `<a href>` 链接（GLM R2 指出依赖 Qt 内部实现细节，脆）
- 不做 `QDesktopServices.openUrl` 打开配置文件目录（DeepSeek R2 指出 rules 存在 ConfigService 里未必有用户可直接编辑的文件路径）
- 程序内跳转是最佳方案，用户裁决确认

---

## 五、去重与批量弹框

### 5.1 去重策略

- `self._missing_rules_warned: set[str]`（以文件名为 key），内存级，进程重启自动清零（GLM R2 反对 QSettings 持久化："昨天弹过、今天换数据也不弹"的隐性状态难以排查）
- 同一文件名在同一会话中只弹一次
- 不同文件名各自弹（即使型号相同——因为型号提取被裁决为不做，文件名是唯一 key）

### 5.2 批量导入防轰炸

当用户批量拖入多个 NDAX 文件时，多个未知型号可能在短时间内触发弹框。方案：

- **简单去重**（同上，已覆盖大部分场景）
- **型号缺失 + 方法默认合并弹框**（已覆盖叠加场景）
- **串行化**：同一时刻仅一个弹框（QMessageBox 本身是模态的，exec() 阻塞直到关闭，天然串行）
- **debounce 合并弹框**：记录 `pending_missing_files`，第一个弹框关闭后检查是否有新的待弹项，有则立即弹下一个。这是 DeepSeek R2 的 200ms debounce 方案的简化版——不需要 debounce timer，因为模态 exec() 天然保证前一个弹完再弹下一个

---

## 六、与旧弹框的复用关系（最终结论）

| 维度 | 现有弹框（方法默认提示） | 新弹框（型号配置缺失） |
|------|------------------------|----------------------|
| 组件 | 迁移后统一使用 `show_countdown_notice()` | 同左 |
| 倒计时秒数 | 5 秒（保持不变） | 3 秒 |
| OK 按钮旁显示秒数 | 升级后显示 `OK (5)` | 显示 `OK (3)` |
| 额外按钮 | 无 | "立即配置"按钮 |
| 触发点 | `_spec_method_defaulted` 标志位 | `_spec_missing_rules` 标志位 |
| 合并场景 | 两标志位同时为 True 时合并为一个弹框 | 同左 |

**复用关系：同一组件，不同调用参数。** 共享倒计时机制、居中逻辑、timer 清理；差异化 title/text/timeout/extra_buttons。这是三轮讨论的最佳实践结晶——不重建、不零拷贝、封装一层。

---

## 七、明确不做（范围裁剪）

| 项目 | 原因 | 记录位置 |
|------|------|---------|
| 非弹框替代方案（Toast/状态栏/托盘） | 需求明确指定弹框形态 | v2 backlog |
| 倒计时进度条 | 增加测试面，收益低 | backlog |
| 按钮倒计时期间禁用 | 与需求"点 OK 立即关闭"矛盾 | 不做 |
| 文案模板配置化 | 与 i18n 管道冲突 | 不做 |
| QSettings 持久化去重 | 隐性状态难排查 | 不做 |
| 候选型号正则提取 | 误报风险高，用户裁决不做 | 不做 |
| NDAX 无 XML 场景预检 | 检测点跟随识别动作 | v2 backlog |
| 倒计时竞态完美处理 | 用户裁决优先级靠后 | 后续事项 |
| 配置路径富文本链接 | 依赖 Qt 内部细节 | v2 backlog |

---

## 八、实施要点清单

1. 新建 `countdown_message_box.py`（~40-50 行，含 extra_buttons 支持）
2. 改造 `filename_parser.set_specification_type()` 返回 `str | None`
3. `data_processor.py`：`_process_first_excel_file()` 接收返回值，`None` 时置 `_spec_missing_rules` 标志
4. `data_processor.py`：`_on_excel_files_processed()` 末尾合并弹框逻辑（型号缺失 + 方法默认）
5. `data_processor.py`：新增 `_open_rules_editor()` 方法，实现跳转配置对话框 Rules 页
6. 迁移 `_show_spec_method_default_notice()` 调用共享组件
7. `utils/config_defaults.py` 加 `missing_rules_notice` 配置节
8. `src/battery_analysis/i18n/` 补 locale 条目
9. 单测：组件行为（秒数递减/到时自动关/OK 立即关/timer 清理/extra_buttons）+ 返回值改造 + 两条入口回归