# DeepSeek (Round 3): 综合四方意见与用户五项拍板，给出最终落地方案：函数式API封装组件、QMessageBox+button.setText实现倒计时、无正则候选提取直接弹框显示文件名、额外"立即配置"按钮跳转Rules页、旧弹框迁移但保留计时器差异、配置仅存行为参数、内存去重。

# DeepSeek Round 3 最终综合建议

## 一、用户拍板确认（五项，全部纳入方案）

| # | 用户裁决 | 本方案对应决策 |
|---|----------|--------------|
| ① | 封装一层组件 | 函数式 API + 内部类（融合 GPT/GLM/MiniMax 三方最优） |
| ② | 新型号判断直接弹框，不做两阶段候选提取 | `set_specification_type()` 返回 None → 直接弹框，显示文件名而非猜测型号 |
| ③ | 跳转按钮要做，进 v1 | 弹框底部新增"前往配置"按钮，点击跳转 battery_config_page 的 Rules 编辑页 |
| ④ | 倒计时竞态优先级靠后 | 不阻塞开发，仅在组件内做基础防御（tick 中先检查 remaining） |
| ⑤ | 不讨论工作量估计 | 不再出现工时数字 |

---

## 二、最终方案——六层设计

### 第 1 层：共享组件设计

**新建文件**：`src/battery_analysis/main/ui_components/dialogs/countdown_message_box.py`

**API 形态**（函数式，融合 GLM 的轻量 + MiniMax 的可扩展性）：

```python
def show_countdown_notice(
    parent: QWidget,
    *,
    title: str,
    text: str,
    timeout_sec: int = 3,
    ok_text: str = "OK",
    show_countdown: bool = True,
    extra_buttons: list[QAbstractButton] | None = None,
) -> tuple[int, QAbstractButton | None]
    """
    返回值：(standardButton, clickedExtraButton)
    - 用户点 OK 或倒计时到 0：返回 (QMessageBox.Ok, None)
    - 用户点额外按钮：返回 (0, clickedButton)
    """
```

**实现要点**：
- 内部用 `QMessageBox` + `box.button(StandardButton.Ok).setText(f"OK (3)")` 每秒更新（GLM 已证明可行，MiniMax 的"必须自定义 QDialog"判断被全体否决）。
- `extra_buttons` 参数支持添加额外按钮（用于"前往配置"），`box.addButton(btn, ButtonRole.ActionRole)`。
- 倒计时到 0 调 `box.accept()`；用户点 OK 立即 accept。
- tick 中防御：`remaining -= 1`，仅 `remaining > 0` 更新文案，否则 `timer.stop() + accept()`。`exec()` 返回后防御性 `timer.stop()`。
- 居中逻辑照搬现有 `_center()`（adjustSize + moveCenter，QMessageBox 无 aboutToShow 信号的已知限制）。
- 组件约 50-60 行，含 docstring。

**为什么不自定义 QDialog**：QMessageBox.button().setText() 完全可用；自定义 QDialog 要重造居中、图标、布局、默认焦点，现有代码的居中注释（data_processor.py:430 附近）就是踩坑证据。

### 第 2 层：检测与触发点

**触发点**：`data_processor._process_first_excel_file()`，`filename_parser.set_specification_type()` 调用后（`data_processor.py:312`），两入口天然覆盖。

**判定逻辑**（用户拍板②：不做正则候选提取，直接弹框）：

```python
# data_processor.py:312 附近
matched_spec = filename_parser.set_specification_type(
    filename, all_spec_types, mw.comboBox_Specification_Type
)
# matched_spec 为 str（匹配到的型号）或 None（未匹配）
if matched_spec is None:
    if filename not in self._missing_rules_warned:
        self._missing_rules_warned.add(filename)
        self._spec_missing_rules = True
        self._pending_missing_filename = filename
```

`set_specification_type()` 返回值改造（照 `set_specification_method` 在 `filename_parser.py:22-28` 已返回 bool 的范式）：
- 当前：隐式返回 None，调用处无返回值使用
- 改造后：返回 `str | None`，返回匹配到的型号名或 None
- 破坏面极小：调用点仅 `data_processor.py:312` 一处（GLM、DeepSeek、GPT 三方独立确认）

**为什么不提取候选型号**：用户明确裁决"直接弹框"。正则启发式提取存在误报风险（批次码 DC2604、脉冲电流值等均含字母+数字组合），误报带来的"错误确定性"比不提示更糟。用文件名代替型号名，诚实告知"以下文件未能识别型号"，后续用户自行确认。

### 第 3 层：弹框文案与跳转按钮

**弹框呈现**：

```
标题：电池型号配置缺失

正文：以下文件未能匹配到已有的电池型号配置：
      {filename}
      
      请在"设置 → 电池配置 → Rules"中补充对应型号配置后重新加载文件。

按钮区：[ 前往配置 ]   [ OK (3) ]
```

**"前往配置"按钮实现**（用户拍板③）：
- 通过 `extra_buttons` 参数传入一个 QPushButton("前往配置")
- 点击后：关闭弹框 → 打开应用内配置对话框 → 定位到 Rules 编辑页
- 跳转路径：`main_window.show_config_dialog()` → 切到 battery_config_page → `_RulesEditor`
- 需要从弹框调用到主窗口的配置页，通过 `parent` 链（parent 即 main_window）或信号槽中转，避免硬耦合

**文案 i18n**：全部走 `_()` 翻译管道，不放配置文件（GLM 已指出与 i18n 冲突）。locale 条目补入 `src/battery_analysis/i18n/`。

### 第 4 层：旧弹框迁移

现有 `_show_spec_method_default_notice()`（`data_processor.py:406-434`）迁移为调用 `show_countdown_notice()`：

```python
# 改造前：30 行内联代码
# 改造后：
show_countdown_notice(
    self.main_window,
    title=_("Default Specification Method"),
    text=_("...{method}...").format(method=self.SPEC_METHOD_DEFAULT),
    timeout_sec=5,
    show_countdown=True,   # 升级后按钮旁也显示秒数
)
```

**旧弹框按钮是否升级为显示秒数**：GLM 和 GPT 均建议升级（视觉一致性），本方案采纳。show_countdown=True 为默认值，迁移只需改一行调用。若坚持保留旧 UX，传 `show_countdown=False` 即可——一个参数的逃生口。

### 第 5 层：去重与批量场景

**去重策略**：`self._missing_rules_warned: set[str]`（key 为文件名），内存级去重，进程重启自然清零。

**批量文件场景**（NDAX 一次转换多个 xlsx）：
- 同一文件名不重复弹（set 去重）
- 不同文件名各弹一次（用户可快速点 OK 跳过）
- 倒计时竞态（如需进一步合并弹框）列为后续优化，本次不阻塞

**与方法默认叠加的场景**：
- 型号缺失（`_spec_missing_rules=True`）+ 方法默认（`_spec_method_defaulted=True`）同时触发
- 优先弹型号缺失（更紧急），方法默认的弹框在型号缺失弹框关闭后再弹（如果两者都触发）
- 或合并为一个弹框同时说明两件事（文案模板："型号未匹配且规格方法已使用默认值"）。推荐后者，减少弹框次数，但实现复杂度略高，可在 v1 中先串行弹、v2 合并

### 第 6 层：配置与行为参数

在 `utils/config_defaults.py` 的 BatteryConfig 下新增：

```python
"missing_rules_notice": {
    "enabled": True,
    "timeout_seconds": 3,
}
```

仅两个行为开关。不放文案模板（与 i18n 冲突）、不放型号前缀白名单（用户已裁决不做候选提取）。GLM 指出真实配置链路是 `config_defaults.py` + `ConfigService`（通过 `config_manager.py:33` 的 key 映射），不是 `config_schema.py`，此处严格遵循现有机制。

---

## 三、与 Round 1-2 各方分歧的最终裁决

| 分歧点 | 裁决 | 依据 |
|--------|------|------|
| QMessageBox vs 自定义 QDialog | **QMessageBox + button.setText()** | GLM 实证 + 三方一致 + 代码库现有居中坑证据 |
| 候选型号提取（正则启发式） | **不做，直接显示文件名** | 用户拍板② + 误报代价高于漏报 |
| 链接跳转 | **做，额外按钮进 v1** | 用户拍板③ |
| 按钮倒计时期间是否禁用 | **不禁用，随时可点 OK** | 与需求"点 OK 立即关闭"一致（GPT/DeepSeek/GLM 三方一致） |
| 配置化边界 | **仅行为参数（enabled, timeout）** | 与 i18n 管道一致（GLM/GPT 一致） |
| 旧弹框是否升级按钮秒数 | **升级，show_countdown=True** | 视觉一致性（GLM/GPT 一致），保留关闭开关 |
| 去重机制 | **内存 set，非 QSettings** | 行为可预期，无跨启动隐性状态 |
| 非弹框替代方案 | **本次不做，记入 backlog** | 需求明确要求弹框，Toast/状态栏为 v2 演进 |
| NDAX 无 XML 场景 | **本次不覆盖** | 检测点跟随识别动作，识别未发生则不弹 |
| 触发点位置 | **data_processor 单钩子点** | 三家独立分析一致（GPT/GLM/DeepSeek），一处代码覆盖两入口 |

---

## 四、待实现文件清单

| 文件 | 改动 |
|------|------|
| `main/ui_components/dialogs/countdown_message_box.py` | **新建**，共享倒计时弹框组件 |
| `main/business_logic/data_processor.py` | ① `_process_first_excel_file` 中 `set_specification_type` 返回值接住 + 检测弹框；② `_show_spec_method_default_notice` 迁移为调共享组件；③ `_on_excel_files_processed` 末尾统一弹框链路；④ 新增 `_missing_rules_warned: set` |
| `main/business_logic/filename_parser.py` | `set_specification_type()` 返回值改为 `str \| None`（照 `set_specification_method` 范式） |
| `utils/config_defaults.py` | BatteryConfig 下新增 `missing_rules_notice: {enabled, timeout_seconds}` |
| `i18n/` | 补新文案的 locale 条目 |
| `tests/` | 组件单测 + 返回值单测 + 两条入口回归 |

---

## 五、系统性风险提醒（供实现时参考）

1. **QTimer 清理**：tick 中 `remaining <= 0` 时先 `timer.stop()` 再 `accept()`；`exec()` 返回后补一次 `timer.stop()` 防御。这是 DeepSeek/GPT 两轮都强调的防御点。
2. **parent 必须是 main_window**：不是当前 tab。MiniMax 在 Round 2 正确指出了快速切换 tab 导致弹框 parent 错误的风险。
3. **`set_specification_type` 返回值改造**：调用点仅一处（data_processor.py:312），但改签名时需确认无动态调用（getattr 等），GLM 建议跑一遍类型检查。
4. **按钮宽高跳动**：倒计时数字从 "OK (3)" 变 "OK (2)" 时按钮宽度可能微变。setMinimumWidth 预留空间或用等宽数字格式（如右对齐固定宽度），MiniMax 的这个细节提醒值得采纳。