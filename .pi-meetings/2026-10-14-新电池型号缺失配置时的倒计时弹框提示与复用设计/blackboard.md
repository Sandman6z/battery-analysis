# Meeting: 新电池型号缺失配置时的倒计时弹框提示与复用设计
之前有个带倒计时的弹框，也是写好秒数，然后根据配置的时间，到时间就自动关闭，如果用户点击了OK，就立即关闭
这个弹框倒计时，是不是复用成同一段代码，由你决定
> Created: 2026-10-14T04:31:13.072Z
> Type: Brainstorming (3 rounds)

---

## GPT (Round 1): 从愿景和架构角度分析新电池型号缺失配置弹框的触发点、复用策略和用户体验设计

# Round 1 — 愿景型策略师分析

## 一、核心愿景：把"配置缺失"从被动错误变成主动引导

当前系统的电池型号识别是"隐性失败"——当 `filename_parser.set_specification_type()` 无法从文件名匹配到 `battery.rules` 中的任何规格时，下拉框只是静默地保持未选中状态。用户可能浑然不觉，直到后续分析出错才追查原因。

**我们要做的不只是加一个弹框，而是建立一条"缺失配置→用户引导→补充完成→恢复流程"的完整链路。** 弹框只是链路的第一环。

---

## 二、两个触发点分析

### 触发点 1：NDAX 转换后

当前流程（`src/battery_analysis/ndax/worker.py`）只做格式转换，不解析文件名中的电池型号。型号识别发生在转换后的 Excel 文件被导入分析时（`data_processor.py:312` 处 `filename_parser.set_specification_type`）。

**策略方向：** 在 NDAX 转换完成、用户切回分析页并加载已转换的 Excel 时，才做型号校验。此时触发点与触发点 2 合并——两条路径最终汇聚在同一处：`data_processor.py` 的 `_process_first_excel_file()` 方法中，`set_specification_type` 执行后检查是否成功匹配。

### 触发点 2：独立转换的 Excel + XML 导入识别

`filename_parser.set_specification_type()` 通过子串匹配（`if spec_type in filename`）尝试命中。如果未命中任何 `all_spec_types`，combo_box 保持 `setCurrentIndex(-1)`。

**检测逻辑：** 在 `set_specification_type` 执行后，检查 `combo_box.currentIndex() == -1` 即可判定"未识别到型号"。更精确的判定还需结合 `_apply_specification_rules()` 的结果——即使文件名匹配到了某个型号字符串，但如果该型号不在 `battery.rules` 配置中（没有对应的规则条目），同样视为"配置缺失"。

---

## 三、关于倒计时弹框复用的策略建议

### 现有基础

`data_processor.py:420-444` 已有一个倒计时弹框实现（规格方法默认值提示），核心模式是：
- `QMessageBox` + `QTimer.singleShot(5000, box.accept)`
- 居中逻辑、自动关闭

### 复用策略：提取 `CountdownMessageBox` 工具类

**建议方向：提取为独立的可复用组件**，理由如下：

1. **两个弹框场景不同但机制相同**：都是"信息提示 + OK 按钮 + N 秒倒计时自动关闭"，参数只有标题、正文、超时时长。
2. **本次需求新增了"OK 按钮旁显示倒计时秒数"**——现有实现没有这个 UI 细节。如果复用 `QTimer.singleShot` 散落在调用处，每次都要手写倒计时更新逻辑。
3. **未来可扩展**：配置路径链接（可点击跳转到配置页）等增强功能只需改一处。

**建议组件接口：**

```python
class CountdownMessageBox(QMessageBox):
    """带倒计时的提示弹框
    
    - title: 窗口标题
    - text: 提示正文（支持富文本/路径链接）
    - timeout_secs: 倒计时秒数（默认 3）
    - parent: 父窗口（用于居中）
    """
```

内部实现要点：
- 用 `QTimer(1000ms)` 每秒更新 OK 按钮文本（如 `"OK (3)"` → `"OK (2)"` → `"OK (1)"` → `"OK"`）
- 倒计时结束自动 `accept()`
- 用户点击 OK 立即 `accept()`（与现有行为一致）
- 居中逻辑提取到基类或工具方法

这样，现有的"规格方法默认值提示"也迁移到这个组件，只需改一行调用。两处共享同一段代码，后续维护成本最低。

---

## 四、用户体验设计建议

### 弹框文案设计

```
标题：电池型号配置缺失

正文：
未在系统配置中找到以下电池型号：{型号名}

请前往以下路径补充配置：
  配置 → 电池配置 → Rules

[ OK (3) ]
```

### 关键 UX 细节

1. **路径要可操作**：文案中的"电池配置"应是一个可点击的链接，点击后直接打开配置对话框并定位到 Rules 编辑页（`battery_config_page.py` + `_RulesEditor`）。光给文字路径对新用户是不够的。
2. **不阻塞主流程**：弹框关闭后，分析流程应继续——只是电池类型和规格相关字段保持空白/默认值，用户可在弹框引导下补完配置后重新加载。
3. **避免重复弹框**：同一文件名在同一会话中只弹一次。用 `_already_warned_specs: set` 做去重。
4. **倒计时 3 秒足够短**：信息型提示，不需要用户深度阅读。如果用户想看详情，点 OK 关闭后再去配置页即可。

---

## 五、架构方向总结

| 维度 | 建议 |
|------|------|
| 检测位置 | `data_processor.py` 的 `_process_first_excel_file()` 中，`set_specification_type` 执行后 |
| 判定条件 | `combo_box.currentIndex() == -1`（文件名未匹配）或匹配到的型号不在 `battery.rules` 中 |
| 弹框实现 | 提取 `CountdownMessageBox` 工具类，放在 `src/battery_analysis/main/dialogs/` |
| 现有弹框迁移 | `data_processor.py` 中的规格方法默认值提示迁移到同一组件 |
| 去重策略 | `_already_warned_specs: set[str]`，每次会话重置 |
| 配置跳转 | 弹框正文中的路径可点击，直接打开配置对话框的 Rules 页 |
| i18n | 弹框文案走 `_()` 翻译管道，与现有国际化体系一致 |

---

## 六、风险与待讨论点

1. **NDAX 转换完成时的触发时机**：是在转换完即刻检测（需要解析文件名），还是等用户切回分析页加载 Excel 时统一检测？后者更简单且复用同一段代码，但用户可能先去做了别的事。
2. **"配置缺失"与"文件名未携带型号"的区分**：如果用户手动在下拉框选了一个型号，即使文件名没匹配到，也不应弹框。所以弹框应仅在"自动识别失败且用户尚未手动选择"时触发。
3. **XML 导入路径的特殊性**：XML 导入时电池型号可能来自 XML 内容而非文件名，需要确认 XML 解析流程中型号识别的具体字段。

---

## MiniMax (Round 1): 创新交互方案、文案设计、边缘情况与非常规替代思路

# MiniMax Round 1：跳出框框的横向思考

## 一、现有倒计时机制的复用判断

**结论：不应直接复用，但应提取为共享抽象。**

现有代码（`data_processor.py:406-434`，`_show_spec_method_default_notice`）的机制是：
- 用 `QTimer.singleShot(delay_ms, box.accept)` 静默关闭
- OK 按钮文本固定不变，无视觉倒计时

**新需求的本质差异**：要求"OK 按钮旁边显示倒计时秒数"——这不是 `QMessageBox` 能做到的，因为其按钮文本是固定的，必须自定义 `QDialog`。

**建议方案**：新建 `CountdownDialog` 基类或工厂函数，接受参数：
```python
def show_countdown_dialog(parent, title, message, seconds=3, config_path=None)
```
内部用 `QTimer` 每秒更新一次 OK 按钮文本（如 "OK (3s)" → "OK (2s)" → "OK"），倒计时到 0 时自动 `accept()`。`_show_spec_method_default_notice` 可改造为调用同一工厂，传入 `show_countdown=False`（静默模式）以保持向后兼容。

---

## 二、两种触发路径的触发点精确定位

通过代码分析，两条路径的触发点分别位于：

| 路径 | 触发点 | 当前行为 |
|------|--------|----------|
| NDAX 转换后 | `ndax_tab.py:_find_and_fill_test_profile()` — 加载 `4_test profile` 目录的 XML 后 | 填充 TestProfile 路径，自动设置输入/输出路径 |
| 电池分析导入 XML | `ndax_tab.py:_check_existing_xlsx()` 或文件打开时 | 根据 xlsx 文件名解析电池型号，填充到 `comboBox_Specification_Type` |

**关键发现**：`comboBox_Specification_Type` 的 items 来源是 `config_defaults.py` 中 `rules` 字段通过 `battery_classifier.derive_specifications()` 派生。因此"该型号在 rules 中不存在"的判断逻辑只需：

```python
known_specs = derive_specifications(config_service.get("battery.rules"))
if selected_model not in known_specs.get(battery_type, []):
    show_countdown_dialog(...)
```

---

## 三、创新交互设计建议

### 1. 路径文案设计
- 不要只写静态路径，写**可点击的超链接**（`QLabel` 支持富文本 `<a href="...">`），点击后用 `QDesktopServices.openUrl` 直接打开配置文件所在目录
- 文案示例：`系统中没有 [{型号名}] 的配置信息。请 <a href="file:///{config_dir}">点击此处打开配置目录</a> 添加，或在下方填写。`（下方的"填写"可引导用户直接在 rules editor 中操作）

### 2. 非阻塞替代方案（挑战"必须弹框"的假设）
- **不弹框**：将提示降级为状态栏消息 + 左下角闪烁图标，用户可随时点击图标打开配置目录。减少对工作流的干扰。
- **只在首次出现时弹框**：用 `QSettings` 记录"本 session 已告知过该型号"，同一型号不再重复弹框，直到下次启动。
- **静默引导而非阻断**：自动将用户带到配置添加界面（如果 rules editor 对话框可复用的话）。

### 3. 倒计时 UI 的微创新
- OK 按钮文案动态变化：`"确定 (3s)" → "确定 (2s)" → "确定 (1s)" → "确定"`
- 倒计时期间按钮**不可点击**（`setEnabled(False)`），防止用户连续快速点击导致多次触发
- 进度条替代纯文字：QDialog 底部加一个细长 QProgressBar，直观显示剩余时间

---

## 四、边缘情况与边界条件

1. **连续导入多个未知型号**：若用户批量拖入多个 NDAX 文件，每个文件都触发弹框会形成"弹框轰炸"。建议加锁：检测到弹框已显示时，后续触发进入队列，等用户关闭当前弹框后再处理下一个。

2. **快速切换 tab 导致弹框消失**：若用户在 NDAX→电池分析 tab 间快速切换，弹框可能出现在错误父窗口上。确保 `parent=self.main_window` 而非当前活跃 tab。

3. **倒计时与用户点击竞态**：`QTimer` 和 `button.clicked` 信号同时到达 `accept()`。使用 `QTimer.singleShot` 而非定期 `start()` + `stop()`，避免竞态窗口。

4. **配置路径不存在**：若配置文件被删除或路径变更，弹框中的路径链接会失效。先 `os.path.exists()` 检查，失效时显示备用文案（"配置目录不存在，请从菜单 → 设置 → 打开配置"）。

5. **国际化**：倒计时数字"3"本身不需要翻译，但若按钮文案格式随语言变化（如德语"OK (3 Sek.)"），确保 `QLabel` 宽度自适应，避免倒计时数字换行导致按钮高度跳动。

6. **屏幕阅读器/无障碍**：倒计时变化时，弹出框的 `accessibleName` 应同步更新为 "确认对话框，还剩 3 秒自动关闭"，让屏幕阅读器能朗读倒计时状态。

---

## 五、非常规替代思路（"如果不弹框？"）

| 方案 | 思路 | 优势 | 劣势 |
|------|------|------|------|
| 气泡通知（Toast） | 右上角浮出不阻塞操作的提示，3 秒自动消失 | 不打断用户当前操作 | 可能被忽略 |
| 系统托盘气泡 | 程序最小化时仍可通知 | 适合后台转换场景 | 不适合前台分析场景 |
| 状态栏带操作链接 | 底部状态栏显示 "⚠️ 型号未配置 - [立即配置]" | 最不打扰，始终可见 | 视觉权重低 |
| 模态引导流程 | 检测到未知型号 → 自动打开配置 rules editor 对话框，用户填完自动继续 | 消除"用户忘记配置"的问题 | 强制用户操作，破坏流程连续性 |

**推荐**：混合方案——首次出现时弹框（同现有需求），之后转为状态栏持久提示，直到该型号被正确配置。

---

## 六、配置化设计建议

弹框文案和路径应完全配置化，避免硬编码：

```json
{
  "battery": {
    "missing_model": {
      "enabled": true,
      "countdown_seconds": 3,
      "title": "电池型号未配置",
      "message_template": "系统中没有 [{model_name}] 的配置信息，请到 {config_path} 补充。",
      "config_path_label": "config/rules"
    }
  }
}
```

这样未来修改文案无需改代码，也方便支持多语言。`config_path` 可动态从 `ConfigService` 实时读取当前配置路径，而非硬编码。

---

**总结**：现有 `_show_spec_method_default_notice` 的倒计时机制值得抽象为共享 `CountdownDialog` 基类。新弹框的核心差异是"OK 按钮旁显示倒计时数字"，这必须用自定义 QDialog 实现，而非 QMessageBox。建议同时处理边缘情况（弹框轰炸、竞态、配置路径失效）并提供配置化文案。


---

## DeepSeek (Round 1): 从系统架构、代码复用、配置机制和事件流四个维度分析新电池型号缺失配置时的倒计时弹框提示方案

# DeepSeek Round 1 分析：新电池型号缺失配置时的倒计时弹框提示与复用设计

## 一、系统架构现状

### 1.1 现有倒计时弹框实现

当前代码库中已有**一个**带自动关闭的弹框，位于：

**`src/battery_analysis/main/business_logic/data_processor.py:409-443`** — `_show_spec_method_default_notice()`

```python
SPEC_METHOD_NOTICE_TIMEOUT_MS = 5000  # 5 秒

def _show_spec_method_default_notice(self) -> None:
    box = QW.QMessageBox(self.main_window)
    box.setWindowTitle(_("Default Specification Method"))
    box.setText(_("The specification method was not found for this battery. "
                  "{method} has been selected by default. Please confirm."
                ).format(method=self.SPEC_METHOD_DEFAULT))
    box.setStandardButtons(QW.QMessageBox.StandardButton.Ok)
    box.setDefaultButton(QW.QMessageBox.StandardButton.Ok)
    # 居中逻辑...
    box.adjustSize()
    _center()
    QC.QTimer.singleShot(self.SPEC_METHOD_NOTICE_TIMEOUT_MS, box.accept)
    box.exec()
```

**关键特征**：
- 使用 `QTimer.singleShot(timeout, box.accept)` 实现自动关闭
- **没有**在 OK 按钮旁显示倒计时秒数（用户看不到剩余时间）
- 超时 5 秒，硬编码为类常量
- 纯 QMessageBox，未封装为可复用组件

### 1.2 电池型号识别的两条入口路径

#### 路径 A：NDAX 转换后自动识别

```
NdaxConverterTab._start_convert()
  → ConvertWorker.run()  (并行转换 .ndax → .xlsx)
  → _on_finished()
    → _find_and_fill_test_profile()  (自动查找 4_test profile 目录中的 XML)
      → path_manager.set_output_path() / set_input_path()
      → sigSetVersion.emit()
        → data_processor.get_xlsxinfo()  (扫描 xlsx 文件)
          → _process_first_excel_file(filename)
            → filename_parser.set_specification_type()  ← 匹配规则中的规格型号
            → filename_parser.set_specification_method()
            → 如果未匹配到方法 → _spec_method_defaulted = True
          → _show_spec_method_default_notice()  ← 仅在方法未匹配时弹框
```

**当前问题**：`filename_parser.set_specification_type()` 在文件名中找不到已知规格型号时，**静默失败**（combo box 保持未选中），没有任何提示。

#### 路径 B：手动导入 XML 识别

```
用户手动选择 XML → path_manager 检验 XML
  → set_input_path() / set_output_path()
  → sigSetVersion.emit()
    → data_processor.get_xlsxinfo()
      → 同路径 A 后半段
```

两条路径最终汇聚于 `data_processor._process_first_excel_file()`，这是检测电池型号的核心节点。

### 1.3 配置机制

电池型号规则存储在 `config.json` 的 `BatteryConfig` 节：

| 配置键 | 格式 | 用途 |
|--------|------|------|
| `BatteryConfig/Rules` | `["CR2450/1S1P/600/550/380/1.0", ...]` | 规格型号/成组方式/容量/计算容量/要求可用容量/CC电流 |
| `BatteryConfig/SpecificationTypeCoinCell` | `["CR2450", "CR2032", ...]` | 纽扣电池规格型号列表 |
| `BatteryConfig/SpecificationTypePouchCell` | `["CP503747", ...]` | 软包电池规格型号列表 |
| `BatteryConfig/SpecificationMethod` | `["1S1P", "2S1P", ...]` | 成组方式列表 |

规格型号列表实际上由 `battery_classifier.derive_specifications(rules)` 从 Rules 自动派生，规则是单一数据源。

## 二、需求分析与技术挑战

### 2.1 需求拆解

| 需求点 | 技术要求 |
|--------|----------|
| 识别新电池型号但 rules 里无配置 | 在 `set_specification_type()` 匹配失败时触发 |
| 两条路径都要弹框 | NDAX 转换后 + 手动导入 XML 后，均需检测 |
| 弹框带 3 秒倒计时 | OK 按钮旁显示 "3...2...1..." |
| 倒计时结束自动关闭 | `QTimer` 驱动 |
| 点 OK 立即关闭 | 需要正确清理 timer |
| 配置路径和文案可配置 | 弹框内容从配置读取，不硬编码 |

### 2.2 核心挑战

**挑战 1：如何判断"新电池型号不在 rules 中"？**

当前 `filename_parser.set_specification_type()` 的逻辑是遍历 `all_spec_types` 列表，在文件名中做子串匹配。如果匹配不到，函数直接返回（无返回值）。需要：

- 修改 `set_specification_type()` 返回匹配结果（bool 或匹配到的型号名）
- 或者在调用侧事后检查 combo box 是否仍为未选中状态

**推荐方案**：让 `set_specification_type()` 返回匹配到的型号名（`str | None`），调用侧根据返回值决定是否弹框。这是最小侵入性修改。

**挑战 2：如何获取文件名中的"新型号"？**

当文件名中包含一个未知型号时，我们需要提取出这个型号字符串用于提示。当前 `set_specification_type()` 只做匹配不做提取。需要一个辅助函数从文件名中提取候选型号字符串。

**推荐方案**：文件名中通常包含型号名作为子串（如 `CR2450`、`CP503747`）。可以：
1. 先尝试匹配已知型号 → 成功则正常流程
2. 匹配失败 → 用正则或启发式规则提取文件名中的型号候选（如字母+数字组合）
3. 将候选型号显示在弹框中

**挑战 3：倒计时显示在 OK 按钮旁**

标准 `QMessageBox` 的 OK 按钮不容易自定义内容。需要：
- 方案 A：创建自定义 `QDialog`，完全控制按钮布局
- 方案 B：使用 `QMessageBox.addButton()` 添加自定义按钮，用 `QTimer` 更新按钮文本
- 方案 C：在 QMessageBox 上找到 OK 按钮并修改其文本

**推荐方案 B**：用 `QMessageBox.addButton("OK (3)", ...)` + `QTimer` 每秒更新按钮文本为 `"OK (2)"` → `"OK (1)"` → 自动 accept。这是最轻量的方案。

## 三、代码复用分析

### 3.1 现有 `_show_spec_method_default_notice()` 的复用评估

| 维度 | 现有实现 | 新需求 | 复用可行性 |
|------|----------|--------|------------|
| 自动关闭机制 | `QTimer.singleShot(timeout, accept)` | 同 | ✅ 可复用 |
| 倒计时显示 | 无 | OK 按钮旁显示秒数 | ❌ 需新增 |
| 居中逻辑 | `_center()` 内联函数 | 同 | ✅ 可复用 |
| 弹框内容 | 固定文案 | 可配置路径和文案 | ❌ 需参数化 |
| 超时时间 | 5 秒 | 3 秒 | ✅ 参数化即可 |
| 按钮行为 | 仅 OK | OK + 倒计时 | ❌ 需改造 |

**结论**：现有实现**不适合作为直接复用的基础**，因为缺少倒计时显示功能，且内联在 `DataProcessor` 中未封装。

**推荐方案**：创建一个新的可复用弹框组件 `CountdownMessageBox`，放在 `main/dialogs/` 目录下，同时将 `_show_spec_method_default_notice()` 迁移为使用该组件。

### 3.2 复用设计

```python
# src/battery_analysis/main/dialogs/countdown_message_box.py

class CountdownMessageBox:
    """带倒计时的确认弹框
    
    参数：
    - parent: 父窗口
    - title: 窗口标题
    - message: 提示内容
    - timeout_sec: 倒计时秒数（默认 3）
    - config_path: 可选的配置路径提示（显示在消息中）
    """
    
    def __init__(self, parent, title, message, timeout_sec=3, config_path=None):
        ...
    
    def show(self) -> bool:
        """显示弹框，返回用户是否点击了 OK"""
        box = QW.QMessageBox(self.parent)
        box.setWindowTitle(self.title)
        box.setText(self._build_message())
        box.setStandardButtons(QW.QMessageBox.StandardButton.Ok)
        
        # 自定义 OK 按钮文本，加入倒计时
        ok_button = box.button(QW.QMessageBox.StandardButton.Ok)
        ok_button.setText(f"OK ({self.timeout_sec})")
        
        # 倒计时定时器
        remaining = self.timeout_sec
        timer = QC.QTimer()
        timer.setInterval(1000)
        
        def tick():
            nonlocal remaining
            remaining -= 1
            if remaining <= 0:
                timer.stop()
                box.accept()
            else:
                ok_button.setText(f"OK ({remaining})")
        
        timer.timeout.connect(tick)
        
        # 居中
        box.adjustSize()
        self._center_on_parent(box)
        
        timer.start()
        result = box.exec()
        timer.stop()
        return result == QW.QDialog.DialogCode.Accepted
```

## 四、事件流设计

### 4.1 新增检测点

在 `data_processor._process_first_excel_file()` 中，`filename_parser.set_specification_type()` 调用后增加检测：

```python
# data_processor.py:312 附近
matched_spec = filename_parser.set_specification_type(
    filename, all_spec_types, mw.comboBox_Specification_Type
)
if not matched_spec:
    # 从文件名提取候选型号
    candidate = self._extract_model_candidate(filename)
    self._show_missing_config_notice(candidate)
```

### 4.2 完整事件流

```
文件名解析
  → set_specification_type() 返回 None（未匹配到已知型号）
  → _extract_model_candidate(filename) 提取候选型号名
  → _show_missing_config_notice(candidate)
    → CountdownMessageBox(
        parent=mw,
        title=_("型号配置缺失"),
        message=_("系统中没有该电池的配置信息，请到以下路径补充：\n{path}\n\n型号：{model}"),
        timeout_sec=3,
        config_path=_("配置 → 电池配置 → Rules")
      ).show()
```

### 4.3 配置化方案

弹框文案和路径应从配置读取，建议在 `config.json` 中新增：

```json
{
  "BatteryConfig": {
    "MissingModelNotice": {
      "enabled": true,
      "timeout_sec": 3,
      "config_path": "配置 → 电池配置 → Rules",
      "message_template": "系统中没有该电池的配置信息，请到 {path} 补充。\n\n识别到的型号：{model}"
    }
  }
}
```

## 五、风险与依赖

### 5.1 失败模式

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 文件名中无法提取候选型号 | 中 | 弹框显示"未知型号" | 兜底显示整个文件名 |
| 型号匹配误报（文件名含无关子串） | 低 | 频繁弹框打扰用户 | 仅在 combo box 确实未选中时弹框 |
| QTimer 在对话框关闭后仍触发 | 低 | 异常日志 | exec() 返回后 stop timer |
| 配置文件中无 MissingModelNotice 节 | 中 | 启动报错 | 使用默认值兜底 |

### 5.2 扩展上限

- **倒计时精度**：`QTimer.setInterval(1000)` 在 GUI 线程中运行，极端情况下（高 CPU 负载）可能有 ±100ms 偏差，对 3 秒倒计时可接受
- **并发弹框**：如果 NDAX 批量转换后扫描多个 xlsx，每个文件都可能触发弹框。建议同一会话中只弹一次（用 `_missing_model_notice_shown` 标志位去重）
- **国际化**：弹框文案需走 `_()` 翻译函数，配置中的模板也需支持 i18n

### 5.3 依赖关系

- 新组件 `CountdownMessageBox` 无外部依赖，仅使用 PyQt6
- `filename_parser.set_specification_type()` 的返回值修改是**破坏性变更**，需检查所有调用点（当前仅 `data_processor.py:312` 一处）
- 配置 schema 需同步更新 `config_schema.py`

## 六、实施建议

### 6.1 代码复用决策

**建议创建独立的 `CountdownMessageBox` 组件**，同时：
1. 新的"型号缺失"弹框使用该组件
2. 已有的 `_show_spec_method_default_notice()` 迁移为使用该组件（可选，作为后续重构）
3. 该组件支持参数化：超时时间、消息模板、配置路径

这样实现了"一段代码，两种场景复用"的目标，且新组件向后兼容。

### 6.2 最小可行方案（MVP）

1. 创建 `countdown_message_box.py`（~60 行）
2. 修改 `filename_parser.set_specification_type()` 返回 `str | None`
3. 在 `data_processor._process_first_excel_file()` 中增加检测和弹框逻辑
4. 在 `config.json` 的 `BatteryConfig` 节新增 `MissingModelNotice` 配置
5. 用 `_missing_model_notice_shoted` 标志位防止重复弹框

### 6.3 工作量估算

| 任务 | 预估工时 |
|------|----------|
| `CountdownMessageBox` 组件 | 1h |
| `set_specification_type()` 返回值修改 + 测试 | 0.5h |
| 检测逻辑 + 弹框调用 | 1h |
| 配置化 + schema 更新 | 0.5h |
| 测试（两种入口路径） | 1h |
| **合计** | **4h** |

---

## GLM (Round 1): 基于实际代码的分析：两条入口汇合于 data_processor 单一钩子点，建议抽取共享倒计时弹框组件复用（现有弹框需升级为按钮旁显示秒数），总工作量约 1 天，最大不确定性在"新型号识别"判定逻辑。

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

---

## MiniMax (Round 2): 对三位顾问观点的质询与综合改进方案

# Round 2 — 对三位顾问的质询与我的改进方案

## 一、我们对哪些达成了真共识，哪些只是礼貌性认同？

**无争议共识（可直接执行）：**
1. 触发点统一在 `data_processor._process_first_excel_file()`，`set_specification_type()` 之后
2. 复用现有的 `CountdownMessageBox` 组件（现有弹框升级改造）
3. 去重用标志位，同一会话同型号只弹一次
4. 倒计时 3 秒，OK 按钮旁显示秒数

以上四位均同意，可以作为实施前提，不再讨论。

---

## 二、我对三位顾问的质询

### 质疑 GPT：为什么必须是弹框？为什么是 3 秒？

你提出了"建立完整链路"——我完全同意链路需要完整。但"弹框"是链路的唯一形式吗？

**核心问题**：用户正在分析数据流中被打断 3 秒，对于一个"配置缺失"这个低频事件，是否值得？你的愿景描述了"缺失配置→用户引导→补充完成→恢复流程"的链路，但弹框只解决了第一环。补完配置后，用户还需要手动重新触发扫描。

**我的反提案**：先尝试**非弹框方案**（见第三节），如果 3 个月内数据显示仍有 30%+ 的新电池型号最终因配置缺失导致分析失败，再升级为弹框。弹框是"热启动"，非弹框是"冷启动"，后者对低频事件更合适。

### 质疑 DeepSeek：返回 `str | None` 的方案有个隐藏缺陷

你建议修改 `set_specification_type()` 返回匹配到的型号名（`str | None`），调用侧根据返回值决定是否弹框。这在"已知型号匹配失败"时有效。

**但问题在于**：新电池型号**不在** `all_spec_types` 列表中（该列表从 rules 派生）。`set_specification_type()` 只会遍历已知列表做子串匹配，**永远找不到新型号**。所以返回值总是 `None`——调用侧无法区分"文件名没有型号信息"和"型号是新的但不在 rules 里"。

GLM 在 Round 1 已经指出了这个问题，但三位都没有给出清晰答案：**我们如何从文件名中提取出"CR2450"、"CP503747"这样的候选型号 token？**

### 质疑 GLM：复用是目标，但复用粒度是否正确？

你建议函数级 API：
```python
show_countdown_notice(parent, title, text, timeout_seconds, ok_text="OK", show_countdown_on_button=True)
```

**问题**：这和"提取 CountdownMessageBox 类"是两种不同粒度的复用。前者灵活但调用点分散（每个弹框都要传 6 个参数），后者封装更强但更重。

**我的立场**：采用**类级封装 + 工厂函数**，理由：
1. 弹框的"居中逻辑"和"倒计时驱动"是固定行为，不需要每次调用者重复配置
2. 可扩展性：未来可能加"不再提醒"复选框、可点击路径等，只需改组件内部
3. 现有 `_show_spec_method_default_notice()` 的调用点只需改 1 行，其余参数走默认值

**具体建议**：
```python
# main/ui_components/dialogs/countdown_notice.py
class CountdownNoticeBox(QDialog):
    """带倒计时的确认提示框"""
    
    @staticmethod
    def show(parent, title, message, timeout=3, button_text="OK"):
        """工厂方法，返回用户是否点击了确认"""
        ...
```

---

## 三、我的非弹框替代方案（坚持）

Round 1 我提出了非弹框方案，但似乎被三位视为"次选"而非并行方案。这里我正式提出两阶段升级策略：

### 阶段 1（立即上线）：状态栏 + Toast 通知（非弹框）

```
触发时机：同触发点 1 和 2
UI 形式：
  - 状态栏左侧显示 ⚠️ 图标 + "检测到未配置电池型号: {型号}，请补充配置"
  - 3 秒后自动消失（QTimer.singleShot 驱动）
  - 不阻塞主流程，分析继续但规格字段留空
```

**优点**：
- 不打断用户工作流
- 低频事件的正确响应方式
- 实现成本最低（复用现有状态栏 API）

**缺点**：
- 用户可能忽略
- 如果 3 秒内用户移除了焦点，通知会丢失

### 阶段 2（灰度升级）：弹框

如果 3 个月内数据显示用户仍频繁遇到"配置缺失→分析失败"的问题，升级为弹框。此时：
- 复用 `CountdownNoticeBox` 组件
- 统一触发点（复用代码）
- 3 秒倒计时在 OK 按钮旁

**关键问题**：如何定义"分析失败"来触发阶段 2？我建议在 config 中加一个计数器，每次检测到未配置型号且后续没有补配置时 +1，超过阈值（如 5 次）则弹出引导框。

---

## 四、对"新型号识别"判定逻辑的明确方案

三位都没有给出清晰答案。我来提：

**问题本质**：从文件名中提取形如 `CR2450`、`CP503747` 的候选型号。

**我的方案**：
```python
def extract_candidate_model(filename: str) -> str | None:
    """从文件名中提取候选电池型号"""
    # 已知型号前缀（从 config_defaults 或现有 all_spec_types 获取）
    known_prefixes = ["CR", "CP", "CL", "CGR"]  # 从 rules 派生
    # 正则：前缀 + 数字组合（允许斜杠分隔的成组信息）
    pattern = r'(CR\d{4}|CP\d{6}|CL\d+|CGR\d{4})'
    match = re.search(pattern, filename, re.IGNORECASE)
    return match.group(1) if match else None
```

**优点**：
- 不依赖 `set_specification_type()` 的已知列表
- 对任何符合格式的新型号都能捕获
- 可配置的前缀白名单，支持未来扩展

**需要确认**：实际代码中是否有其他型号前缀？建议从 `battery_classifier.py` 的 `derive_specifications()` 中自动提取前缀列表，而非硬编码。

---

## 五、综合方案：我的最终建议

### 架构决策

| 决策点 | 我的建议 | 与其他三位的分歧 |
|--------|----------|-----------------|
| 触发点 | `_process_first_excel_file()` 统一钩子 | 无分歧 |
| 组件复用粒度 | 类级封装 + 工厂函数（`CountdownNoticeBox.show()`） | 不同于 GPT（仅组件）和 GLM（函数级） |
| 是否复用现有弹框代码 | 是，但需升级 OK 按钮旁秒数 | 无分歧 |
| 弹框 vs 非弹框 | **先非弹框，灰度升级** | 与三位都不同——三位默认弹框 |
| 新型号识别 | 前缀正则提取 + 前缀白名单配置化 | 对三位"返回 None 即失败"的补充 |
| 配置路径 | 可点击链接（QLabel + linkActivated） | 与 GPT 一致 |
| 去重 | `_warned_models: set[str]` | 无分歧 |

### 实施优先级

1. **P0**：`extract_candidate_model()` — 解决"识别到新电池型号"的核心不确定性
2. **P0**：`CountdownNoticeBox` 组件（含 OK 按钮旁倒计时）
3. **P1**：状态栏通知（非弹框阶段）
4. **P2**：弹框阶段（基于灰度数据决定是否升级）
5. **P2**：配置路径可点击（QPalette 样式设置超链接样式）

### 剩余待拍板问题

1. **弹框 vs 非弹框**：三位默认弹框，我坚持非弹框先行。需要主持人和产品侧确认。
2. **前缀白名单来源**：从 `derive_specifications()` 自动派生，还是在 `config_defaults.py` 中手动维护？
3. **NDAX 转换完成时若无 XML**（GLM 提出的场景）：是否也触发提示？建议：只要能从文件名提取到候选型号就触发，无论后续 XML 是否存在。


---

## GPT (Round 2): Round 2 — 质询与融合：统一钩子点 + 共享倒计时组件 + "一键跳转 Rules"引导闭环

# GPT Round 2：质询、回应与融合改进方案

## 一、Round 1 共识盘点（四人已收敛的部分）

1. **组件复用：四人一致同意"不是零成本拷贝，而是升级抽取"**。现有 `_show_spec_method_default_notice()`（`src/battery_analysis/main/business_logic/data_processor.py:406-434`，QMessageBox + `QTimer.singleShot(5000, box.accept)`）没有按钮旁秒数显示，与新需求存在功能差距；DeepSeek、MiniMax、GLM 与我均主张抽取共享组件。这一点已无分歧，可直接拍板。
2. **统一触发点：三条分析线（我、DeepSeek、GLM）独立得出同一结论**——NDAX 转换后（`ndax_tab.py:_on_finished()` → `_find_and_fill_test_profile()` → `sigSetVersion.emit()`）与 XML/Excel 导入（`path_manager.py:173/232/260` → `sigSetVersion.emit()`）两条路最终汇入 `data_processor._process_first_excel_file()`（`data_processor.py:297`）的 `filename_parser.set_specification_type()`（`filename_parser.py:13`）。**检测与弹框只写一遍，放在钩子点**，两入口天然覆盖。
3. **去重**：同一型号同一会话只弹一次（我的 `_already_warned_specs: set` 与 DeepSeek/GLM 的标志位模式同构），不同型号各弹一次。
4. **i18n**：新增文案走 `_()` 翻译管道。
5. **最大不确定性一致被识别为"新型号识别"判定**（GLM 明确指出、DeepSeek 挑战 2 印证）：rules 是型号列表的唯一数据源（`utils/battery_classifier.py:39 derive_specifications` 从 `battery.rules` 派生下拉框 items），**不在 rules 里的型号现有代码根本"看不见"**，`set_specification_type` 只做子串匹配、匹配失败静默返回。

## 二、对三位顾问的质询与回应

### 2.1 对 GLM：钩子点结论正确，但两处需要追问

- **赞同**：`capacity_from_rules()`（`utils/pulse_currents.py:189`，未命中返回 0.0）复用为"是否在 rules 中"的判据、照抄 `_spec_method_defaulted` 标志位模式（`data_processor.py:272-275`）、照 `set_specification_method` 已返回 bool 的范式（`filename_parser.py:20`）改造 `set_specification_type` 返回 `str | None`——这三条都是"现成范式抄作业"，成本最低，我全部采纳。
- **质询 1**：GLM 建议"识别出 spec_name 后再用 `capacity_from_rules` 查 rules"，但这两个动作的数据源是同一个 `battery.rules`——识别成功即意味着在 rules 里，此检查恒为真，属于冗余。**真正的缺口在识别失败侧**：需要"从文件名提取候选型号 token"的独立逻辑。GLM 自己也指出了这一点，但实现步骤里没把它放到主位。我认为**候选提取才是 MVP 的主体工作**，不是附带项。
- **质询 2**：GLM 遗漏了"文件名未携带型号"与"识别到新型号但无配置"的区分。若文件名里根本没有型号 token（如 `test_data_001.xlsx`），弹"型号配置缺失"是误报。两类情况必须分流（见 3.2）。

### 2.2 对 DeepSeek：事件流清晰，但两处方案过度设计/欠考虑

- **赞同**：`set_specification_type()` 返回 `str | None` 是最小侵入修改；MVP 清单（组件 1h + 返回值改造 0.5h + 检测 1h + 配置 0.5h + 测试 1h）与 GLM 的 1 天估算相互印证，工作量可信。
- **质询 1（配置化过度）**：DeepSeek 和 MiniMax 都主张把**文案模板**放进 config.json（`MissingModelNotice.message_template`）。我反对：(a) 文案模板与 i18n 冲突——配置里的中文字符串走不了 `_()` 翻译管道，多语言场景下要么模板里塞双语、要么配置按语言分裂，复杂度远超收益；(b) 文案变更频率极低，改代码发版的成本与改配置重启几乎相同。**配置只存行为参数（enabled、timeout_sec），文案留在代码里走 i18n**。GLM 的 `config_defaults.py` 加节方案同理，但只放行为参数即可。
- **质询 2（候选提取启发式的风险）**：DeepSeek 建议"正则提取字母+数字组合作为候选型号"，但 `test_data_001` 里的 `data_001` 也会被误提。需要收紧规则（如首段 token 且匹配 `[A-Z]{1,4}\d{3,}` 这类型号形态、大小写不敏感比对），且**提取不到候选时宁可不弹**，避免误报轰炸。这比"兜底显示整个文件名"更符合"3 秒告知型弹框"的打扰预算。

### 2.3 对 MiniMax：边缘情况清单最有价值，但三处方案我要反驳

- **采纳**：(a) 批量导入的"弹框轰炸"问题真实存在，去重集合之外还应有"同一时刻只显示一个弹框"的串行化（GLM 的 generation 守卫模式可复用）；(b) parent 必须是 `main_window` 而非当前 tab；(c) 富文本 `<a href>` 链接、配置路径失效时的兜底文案、无障碍 `accessibleName` 同步——这些细节都对。
- **反驳 1（按钮禁用与需求矛盾）**：MiniMax 建议"倒计时期间 OK 按钮不可点击"防连击。但需求明确"OK 按钮旁显示倒计时秒数"的语义是**用户可随时点 OK 提前关闭**（与现有弹框行为一致），禁用按钮把"3 秒自动关"变成"强制看 3 秒"，是倒退。防连击用去重集合即可解决，不需要禁用。**建议否决此项**。
- **反驳 2（竞态建议自相矛盾）**：MiniMax 说"用 `QTimer.singleShot` 而非周期 start()/stop() 避免竞态"——但按钮旁秒数每秒更新**必须**用周期 timer，singleShot 做不到。正确做法是：单个周期 `QTimer`（parent 挂到 dialog，随 dialog 销毁自动清理）+ `exec()` 返回后 `stop()`（DeepSeek 的 tick 方案实际已是如此）。GLM 注释里"QMessageBox 无 aboutToShow 信号"的居中经验照搬即可。
- **反驳 3（非弹框替代方案时机未到）**：Toast/状态栏/托盘气泡的对比表做得好，但**本次需求已明确指定"倒计时 3 秒提示框"这一形态**，现在争论"要不要弹框"是重新开启已定的产品决策。MiniMax 自己的"混合方案"（首次弹框 + 之后转状态栏持久提示）非常合理，应作为 **v2 演进方向**记录在案，而不是本次实现范围。本次只做弹框 + 会话级去重，两者叠加后打扰程度已可控。

### 2.4 对我自己 Round 1 的修正

- R1 提议"配置路径可点击、点击打开配置对话框并定位到 Rules 编辑页"——经 GLM 指认，Rules 编辑入口是 `main/ui_components/config_dialog/battery_config_page.py` 的 `_RulesEditor`，**程序内跳转可实现且优于 MiniMax 的"打开配置目录"**（用户要补的是 rules 条目，不是配置文件；打开文件目录对非技术用户等于没引导）。维持并强化此方案。
- R1 未处理"NDAX 转换完成但无 `4_test profile` XML 时流程中止"（GLM 风险 2）：此场景型号识别根本未发生，按"检测点跟随识别动作"原则**不弹框**，归入 v2 的转换完成预检。

## 三、融合改进方案（提案定稿）

### 3.1 组件层：函数 API 包一个内部类（融合 MiniMax 工厂 + GLM 函数级 API + DeepSeek 类设计）

```python
# src/battery_analysis/main/dialogs/countdown_message_box.py
def show_countdown_notice(parent, title, text, timeout_sec=3,
                          ok_text="OK", show_countdown=True) -> bool
```
- 内部实现 `CountdownMessageBox(QMessageBox)`：取 `box.button(Ok)` 每秒 `setText(f"{ok_text} ({n})")`（DeepSeek 方案 B 最轻量，不需要自定义 QDialog——MiniMax"必须自定义 QDialog"的判断过强，QMessageBox 的按钮文本可以改，GLM/DeepSeek 已证明）；到 0 自动 `accept()`；点 OK 立即 `accept()`。
- 居中逻辑照搬现有 `_center()`（adjustSize + moveCenter，含"QMessageBox 无 aboutToShow"注释）。
- **现有弹框升级**：`_show_spec_method_default_notice` 迁移为调用 `show_countdown_notice(..., timeout_sec=5)`，按钮显示 `OK (5)`→`OK (1)`。**建议接受视觉升级**（与 GLM 立场一致）：一个系统里两种倒计时弹框行为不一致才是坏 UX；且需求本身就要求"现有弹框升级按钮旁秒数"。保留 `show_countdown=False` 参数作逃生口，但默认升级。
- 单测：秒数递减、到时自动关、点 OK 立即关、`show_countdown=False` 行为不变。

### 3.2 检测层：两阶段判定（本次需求真正的设计核心）

在 `_process_first_excel_file()` 中，`set_specification_type()` 改造为返回 `str | None`（照 `set_specification_method` 返回 bool 的现成范式，`filename_parser.py:20`，唯一调用点在 `data_processor.py:312`，破坏面可控）：

1. **返回了型号** → 在 rules 中（items 本就由 `derive_specifications` 从 rules 派生）→ 正常流程，不弹。
2. **返回 None** → 进入候选提取 `_extract_model_candidate(filename)`：
   - **提取到候选 token**（首段、匹配 `[A-Z]{1,4}\d{3,}` 形态）→ 判定"识别到新型号但无配置"→ 置 `_spec_missing_rules` 标志，`_on_excel_files_processed()` 末尾统一弹框（照 `_spec_method_defaulted` 的"处理完再弹"链路，`data_processor.py:272-275`），正文显示候选型号。
   - **提取不到候选** → 判定"文件名未携带型号"→ **不弹框**（下拉框留空由用户手选；用户手选过则更不应打扰——R1 风险 2 的原则）。
- 去重：`_already_warned_specs: set[str]`，候选级去重；同一时刻仅一个弹框，多型号排队串行。

### 3.3 弹框与路径呈现：提示即引导（本方案的愿景增量）

```
标题：电池型号配置缺失
正文：未在系统配置中找到电池型号：<b>{候选型号}</b>。
      请补充 Rules 配置后重新加载文件。
      [ 前往 Rules 配置 ]（富文本链接/按钮，跳转 battery_config_page._RulesEditor）
[ OK (3) ]
```
- **路径不是静态字符串而是"一键跳转"**：点击直接打开配置对话框并定位 Rules 编辑页。静态文字路径仅作链接失效时的兜底（MiniMax 边缘情况 4）。
- 更进一步（v2 记录，不在本次）：用户在 Rules 补完配置关闭配置框后自动重跑一次型号识别，形成"缺失→引导→补齐→恢复"闭环（我 R1 的链路愿景，本次先交付第一环）。
- 文案走 `_()` + locale 条目（`src/battery_analysis/i18n/`），**不入配置**；配置只加 `battery.missing_rules_notice: {enabled: true, timeout_sec: 3}`（`utils/config_defaults.py`，含 schema 同步）。

### 3.4 明确不做（本次范围裁剪）

- 不做 Toast/状态栏/托盘替代形态（v2：首次弹框+状态栏持久提示的混合方案）；
- 不做倒计时进度条、按钮禁用（与需求语义冲突/收益低）；
- 不做文案模板配置化（与 i18n 冲突）；
- 不做 NDAX 转换完成时点的预检弹框（识别动作未发生，检测点跟随识别）。

## 四、请会议拍板的三个问题

1. **现有弹框是否升级为 `OK (5)` 按钮旁倒计时**？（我+GLM：升级，保持一致性；MiniMax 保留开关；DeepSeek 未表态）
2. **"文件名未携带型号"是否弹框**？（我：不弹，仅"识别到候选型号但无配置"才弹；DeepSeek 倾向兜底显示文件名即弹）
3. **配置化边界**：只存行为参数（我的立场）还是连文案模板一起入库（DeepSeek/MiniMax）？

## 五、风险与工作量

- 风险：候选提取正则的误报/漏报（收紧形态 + 提取不到不弹 + 去重，三重缓解）；`set_specification_type` 签名变更需回归全部调用点（现仅 1 处）；批量文件排队弹框的 UX 需实测。
- 工作量（融合 GLM/DeepSeek 估算）：共享组件+迁移 ~2h；返回值改造+候选提取+检测 ~3-4h；行为参数配置+i18n ~1.5h；单测+两入口回归 ~2-3h；**合计约 1 个工作日**，不确定性集中在候选提取规则的准确率。

---

## DeepSeek (Round 2): 从共识收敛、分歧裁决、被忽视的系统风险（NDAX无XML中断、倒计时竞态、批量弹框队列）三方面质询改进，并给出最终推荐方案。

# DeepSeek Round 2：质询、收敛与系统性补漏

## 一、Round 1 共识确认

四位顾问在以下要点上已达成实质一致，无需再议：

1. **单钩子点**：两条入口（NDAX 转换后 / 手动导入 XML）最终汇合于 `data_processor._process_first_excel_file()`，在此处统一检测即可覆盖两端。GLM 的代码溯源最扎实，我完全认同。
2. **现有弹框不可直接复用**：`_show_spec_method_default_notice()` 缺少"OK 按钮旁显示秒数"的能力，需要抽取为共享组件后让旧调用点迁移。
3. **新组件参数化**：`timeout_sec`、`title`、`message`、`config_path` 等均为传入参数，不硬编码。
4. **去重**：同一会话中同一型号只弹一次。

---

## 二、分歧裁决与质询

### 分歧 1：QMessageBox 还是自定义 QDialog？

- **MiniMax** 主张"QMessageBox 按钮文本固定，必须自定义 QDialog"。
- **我（Round 1）和 GPT** 主张可在 QMessageBox 上用 `addButton()` 或 `button(Ok).setText()` 动态更新。

**裁决：MiniMax 的判断有误。** `QMessageBox.button(StandardButton.Ok)` 返回的是 `QAbstractButton*`，其 `setText()` 完全可用。PyQt6 中这不是问题。用 QMessageBox 加动态 setText 即可，不必为了一个按钮文案去新建 QDialog 子类。**推荐方案：QMessageBox + `button.setText()` + `QTimer` 每秒更新**，代码量最小、行为与现有弹框一致。

如果 MiniMax 有 PyQt6 上 `button.setText()` 不生效的实证，请在 Round 3 提出，否则按 QMessageBox 方案推进。

### 分歧 2：倒计时按钮期间是否禁用点击？

**MiniMax** 提出倒计时期间 `setEnabled(False)` 防止连续快速点击。

**我反对。** 需求原文是"如果用户点击了OK，就立即关闭"。禁用按钮违反需求。用户在倒计时 3 秒内的任何时候点 OK 都应立即 accept。快速点击不会导致多次触发——`QMessageBox.exec()` 是模态的，第一次 accept 后对话框关闭，后续点击不存在目标。

唯一需要防护的是：`QTimer.singleShot` 在 accept 之后还会触发一次。解决方案：在 `tick()` 中先 `remaining -= 1`，仅当 `remaining > 0` 时更新按钮文案，到 0 时 `stop() + accept()`；同时在 `exec()` 返回后 `timer.stop()` 做防御性清理。这是标准模式，不是竞态问题。

### 分歧 3：非弹框替代方案

**MiniMax** 提出了 Toast、状态栏、气泡通知等替代方案。

**评估**：需求明确要求"弹个框提示"，这是用户硬性需求。MiniMax 的"首次弹框 → 后续状态栏"混合方案有创意，但**超出本次范围**。建议作为后续迭代项记录，本次不做。先交付核心需求，再谈降级策略。

### 分歧 4：配置路径的显示方式

- **GPT**：可点击超链接直接打开配置对话框。
- **MiniMax**：`QLabel` 富文本 + `QDesktopServices.openUrl`。
- **我（Round 1）和 GLM**：显示文本路径即可。

**修正立场**：显示文本路径是 MVP，可点击链接是加分项。两者不矛盾——先实现纯文本，链接跳转作为后续增强。因为"打开配置对话框并定位到 Rules 页"需要额外的跨模块协调（从弹框调到 `config_dialog` 的 `_RulesEditor`），耦合风险高于收益。**MVP 阶段用纯文本路径 + 明确的菜单级指引，不做链接跳转。**

---

## 三、被忽视的系统性风险（重点质询）

### 风险 A：NDAX 转换后无 XML 的场景断路

GLM 在 Round 1 末尾提了一句但未深入：当 NDAX 转换完成后，如果 `4_test profile` 目录中没有 XML 文件，`_find_and_fill_test_profile()` 会中止后续流程，`sigSetVersion.emit()` **不会被触发**，`_process_first_excel_file()` 根本不会执行。

**这意味着：在纯 NDAX 转换场景中，如果用户只转出了 xlsx 但没有配套 XML，弹框永远不会出现。**

**质询给全体**：这个场景是否需要覆盖？如果需要，触发点就不能只放在 `_process_first_excel_file()`，还必须在 `_on_finished()` 中加一个独立的型号检测分支。这会增加复杂度，但不覆盖则存在用户盲区。

**我的建议**：本次 MVP 先不覆盖。在弹框的文案中加入兜底指引："如已完成 NDAX 转换，请将转换后的 Excel 文件导入电池分析模块以自动识别型号。"这样用户知道下一步该做什么。后续迭代再考虑在 NDAX 完成回调中增加独立检测。

### 风险 B："新型号识别"的判定逻辑——最大技术不确定性

四位顾问一致认为这是核心难点，但没有人给出完整的判定算法。

**问题本质**：`set_specification_type()` 的匹配列表（`all_spec_types`）本身就从 `battery.rules` 派生。如果型号不在 rules 中，`all_spec_types` 里根本没有它，匹配必然失败。但匹配失败的原因有两种：
1. 文件名中确实包含一个有意义的型号名（如 `CR9999`），只是 rules 里没有 → 应弹框
2. 文件名格式异常，根本不含任何型号信息（如 `test_data_2026.xlsx`）→ 不应弹框

**两种情况在 `set_specification_type()` 返回 None 时无法区分。**

**推荐判定方案（两步走）**：

**Step 1**：让 `set_specification_type()` 返回 `str | None`（GLM 提到 `set_specification_method` 已有返回 bool 的范式，改造成本低）。

**Step 2**：返回 None 时，用一个轻量的启发式函数从文件名提取候选型号：
```python
import re
_MODEL_PATTERN = re.compile(r'[A-Z]{1,4}\d{3,6}')  # 如 CR2450, CP503747, LIR2032

def extract_model_candidate(filename: str) -> str | None:
    stem = Path(filename).stem
    match = _MODEL_PATTERN.search(stem)
    return match.group(0) if match else None
```
- 如果提取到候选型号 → 弹框，文案中显示该候选
- 如果提取不到 → 不弹框（文件名确实不含型号信息）

**这个正则需要根据实际文件名格式校准**。建议在实现前先收集 20-30 个真实文件名样本验证匹配率。

### 风险 C：批量导入时的弹框队列

MiniMax 提到了"弹框轰炸"，但只说"加锁排队"，没给具体机制。

**具体方案**：不要排队（排队意味着用户要连续关闭 N 个弹框，体验更差）。改为**合并弹框**：
- 维护 `_pending_missing_models: list[str]`
- 第一个型号触发弹框时，启动一个短延迟（如 200ms）的 debounce timer
- debounce 期间收集到的所有未知型号合并为一条消息："以下电池型号在系统中无配置：CR9999、CP8888、LIR18650…请到 [路径] 补充。"
- debounce 到期后弹一个合并弹框

这样无论用户拖入多少个文件，始终只弹一次。

### 风险 D：`set_specification_type()` 返回值变更是破坏性修改

GLM 提到了这一点但没有展开。当前 `set_specification_type()` 无返回值（隐式 `None`）。改为返回 `str | None` 后，所有调用点必须兼容。

**现状**：`set_specification_type()` 当前仅在 `data_processor.py:312` 被调用一次（GLM 和我都确认了）。所以破坏性影响范围极小，但仍需确认没有动态调用（如 `getattr` 或信号槽间接调用）。

**建议**：改函数签名时同时加 type hint，在 CI 中跑一遍类型检查即可确认。

---

## 四、最终推荐方案（收敛版）

| 维度 | 决策 |
|------|------|
| 组件 | 新建 `CountdownMessageBox` 工具函数（非类），基于 `QMessageBox` + `button.setText()` |
| 触发点 | `data_processor._process_first_excel_file()` 中 `set_specification_type()` 之后 |
| 判定 | `set_specification_type()` 返回 `str \| None`；None 时用正则提取候选型号，有候选则弹框 |
| 弹框内容 | 标题 + 型号名 + 配置路径文本 + OK(N) 倒计时按钮 |
| 去重 | 去重型：`_pending_missing_models` + 200ms debounce 合并弹框 |
| 配置化 | `config.json` 新增 `BatteryConfig.MissingModelNotice` 节 |
| 旧弹框迁移 | `_show_spec_method_default_notice()` 改调共享组件（timeout=5, show_countdown=True） |
| MVP 不做 | 可点击链接跳转、NDAX 无 XML 场景、状态栏降级 |
| 工作量 | ~4-6h（含正则校准和测试） |

---

## 五、待 Round 3 拍板的问题

1. **NDAX 无 XML 场景**：本次是否需要覆盖？（我建议 MVP 不覆盖）
2. **候选型号正则**：需要真实文件名样本校准，谁来提供？
3. **debounce 合并弹框 vs 简单去重**：合并方案增加了 200ms 延迟和消息拼接逻辑，是否值得？还是简单去重（同型号不重复弹、不同型号各弹一次）就够用？
4. **旧弹框是否同步升级为显示按钮旁秒数**：GLM 建议接受（视觉一致性），GPT 建议迁移即可。需要明确。

---

## GLM (Round 2): Round 2 — 质询与收敛：QMessageBox 足以实现按钮倒计时，砍掉过度设计，收敛为 1 天可落地方案

# GLM Round 2：质询与收敛——把讨论从"能做什么"拉回"这期做什么"

先说结论：四家在**触发点（data_processor 单钩子）、组件复用（抽取共享倒计时弹框）、迁移旧弹框**三个大方向上已经一致，不必再讨论。Round 2 我逐条质询三家方案里与实际代码不符或过度设计的部分，最后给出收敛版设计和剩余待拍板项。

---

## 一、对 MiniMax 的质询（事实纠错最多，必须先厘清）

### 1.1 "QMessageBox 做不到按钮旁显示秒数，必须自定义 QDialog"——**这是错的**

QMessageBox 的标准按钮可以通过公开 API 拿到并改文本：

```python
ok_btn = box.button(QW.QMessageBox.StandardButton.Ok)
ok_btn.setText(f"OK ({remaining})")
```

`QMessageBox.button(StandardButton.Ok)` 返回的就是普通 QPushButton，每秒 `setText` 一次即可实现 "OK (3) → OK (2) → OK (1)"。DeepSeek 的方案 B/C 和我 Round 1 的方案都基于此。**自定义 QDialog 反而要重造居中、图标、布局、默认按钮焦点**——现有弹框里那段 "adjustSize + 手动居中" 的注释（`data_processor.py:430` 附近，说明 QMessageBox 无 aboutToShow 信号的原因）就是踩过坑的证据。用自定义 QDialog 等于把这些坑再踩一遍。结论：**QMessageBox + button().setText 足够，30 行以内解决**。

### 1.2 "倒计时期间按钮 setEnabled(False) 防连点"——与需求矛盾

需求是"点 OK 立即关闭 + 3 秒自动关"。禁用按钮意味着前 3 秒用户想关关不掉，比现状（现有 5 秒弹框随时可点）还差。这是为了解决一个不存在的伪问题（信息型弹框没有"连点误操作"风险）。拒绝。

### 1.3 触发点定位错了

MiniMax 说触发点在 `ndax_tab.py` 的 `_find_and_fill_test_profile()` / `_check_existing_xlsx()`。那是**路径填充层**，型号识别根本不发生在那里——GPT、DeepSeek 和我三家独立分析都确认两条入口汇合于 `data_processor._process_first_excel_file()`（`data_processor.py:312` 的 `set_specification_type` 调用处）。在 ndax_tab 弹框意味着两处写重复检测代码，且手动导入路径还得再抄一遍。此分歧可以直接裁定：**单钩子点，三家对一家**。

### 1.4 QSettings 会话级去重——引入跨启动的隐性状态

QSettings 持久化会导致"昨天弹过、今天换了新数据也不弹"的困惑，排查起来很隐蔽。内存 `set` 在进程重启时自然清零，行为可预期。**MVP 用内存 set，不做持久化**。

### 1.5 文案模板放 JSON 配置——与现有 i18n 管道打架

本项目的翻译在代码层走 `_()` 函数（现有弹框文案即如此，`data_processor.py:410-413`）。把 `message_template` 放进 config，意味着每种语言要维护一套配置文件，i18n 体系被绕开。**文案进代码走 `_()`，配置只放两个开关型字段：`enabled`、`timeout_seconds`**。

### 1.6 非弹框方案（Toast/状态栏/托盘）与各种微创新

需求白纸黑字要弹框。Toast、状态栏链接、QProgressBar、accessibleName 朗读——都是好想法，但都不是本期需求，每一个都增加测试面。务实立场：**全部记入 backlog，本期一个不做**。唯一例外：MiniMax 提的"弹框轰炸"场景（批量 NDAX 转换后多文件）是真实的，但用"同型号只弹一次"就能覆盖 95%，不需要队列锁系统。

---

## 二、对 DeepSeek 的质询

### 2.1 4 小时估计不成立，请正视自己列出的"挑战 2"

DeepSeek 一边把"如何从文件名提取未知型号"列为无现成答案的设计挑战，一边给整个 MVP 估 4 小时。这个挑战点恰恰是全场唯一有真实不确定性的地方（我在 Round 1 给检测逻辑 3-5h、总计 1 个工作日）。**估算要为不确定性留余量，而不是把最难的部分按最顺利的情况估**。

### 2.2 `_extract_model_candidate` 正则启发式提取——拒绝进 MVP，误报代价太高

文件名里充满 `DC2604`（批次码，`filename_parser.py:38` 的正则就是干这个的）、`(0.5-1)mA`（脉冲电流）、`mAh` 等字母数字 token。"字母+数字组合"的正则会把这些统统当型号候选，弹框显示"识别到新电池型号：DC2604"——**错误的确定性比没有信息更糟**，用户会真的去 rules 里加一条 DC2600 的配置。MVP 做法：弹框文案显示**文件名本身**（"无法从以下文件识别电池型号"），型号提取规则等真实用户反馈后再定。这也回应了 GPT 的风险点 2：宁可提示"识别失败"，不猜型号。

### 2.3 `set_specification_type` 返回值改造——同意，且这是全场最没争议的改法

补充一个让方案更稳的事实：`set_specification_method`（`filename_parser.py:22-28`）**已经**返回 `True/False` 表示匹配结果——改造范式就躺在隔壁，把 `set_specification_type` 的隐式 `return None` 改成显式返回匹配型号 `str | None`，调用点只有 `data_processor.py:312` 一处。DeepSeek 说这是"破坏性变更"过虑了，PySide6 里原返回 None、改成返回 str 或 None 不影响任何现有调用（无一处使用其返回值）。

### 2.4 配置挂载点对不上真实代码

DeepSeek 建议改 `config.json` + `config_schema.py`。本仓库实际配置链路是 `utils/config_defaults.py` 定义默认值 + `ConfigService` 按 json key（如 `battery.rules`，见 `config_manager.py:33` 的 `"BatteryConfig/Rules": "battery.rules"` 映射）读取。**不存在叫 config_schema.py 的文件**，配置要加在 config_defaults.py，否则改了也不生效。

### 2.5 CountdownMessageBox 伪代码的两个实现细节

- class 包装 + `.show()` 返回 bool 的面向对象 API，对"调用即弹、弹完即弃"的场景偏重，函数式 `show_countdown_notice(parent, *, title, text, ...)` 更贴现有代码风格。
- tick 里 `remaining <= 0` 时先 `timer.stop()` 再 `accept()`，且 `exec()` 返回后再补一次防御性 `timer.stop()`——你自己在风险表里列了"QTimer 在对话框关闭后仍触发"，这两行就是解法，写进组件别留给调用者。

---

## 三、对 GPT 的质询

### 3.1 可点击链接打开配置页——好愿景，坏 MVP

QMessageBox 的富文本链接要靠 `findChild(QLabel)` 拿到内部标签再连 `linkActivated`，依赖 Qt 内部实现细节，脆。而"打开应用内配置对话框并定位到 Rules 页"需要打通弹框 → 主窗口 → config_dialog → `_RulesEditor`（`main/ui_components/config_dialog/rules_editor.py:16`）四层，为一个提示框做导航系统，投入产出不成比例。**MVP：纯文本路径"设置 → 电池配置 → Rules"**（哪个菜单项进配置页就写哪条路径，文案而已）。链接跳转进 backlog。MiniMax 的 `QDesktopServices.openUrl` 打开目录方案同理搁置——rules 存在 ConfigService 里，未必有用户可直接编辑的文件路径。

### 3.2 "XML 导入时型号可能来自 XML 内容"——可以打消

代码上 XML 导入路径（`path_manager.py` 校验后 `sigSetVersion.emit()`）与 NDAX 路径汇合后，型号识别只发生在 `set_specification_type` 的**文件名**子串匹配，XML 内容不参与。这个疑虑除非需求方另有说明，否则不存在。

### 3.3 "用户手动选择型号后不应弹框"——GPT 这条是全场最有价值的补充，采纳

但实现上要注意时序：检测发生在后台文件处理回调里（`_on_excel_files_processed`），早于用户任何手动操作，所以"自动识别失败即弹"天然满足这条约束，不需要额外判断用户是否手动选过。真正要处理的是**两个标志位叠加**：型号未匹配（新）+ 方法未匹配（已有 `_spec_method_defaulted`）可能同时为 True，连续弹两个倒计时框体验很差。建议合并为一个弹框（见下节）。

---

## 四、收敛版改进方案

四家方案取交集 + 我的修正，落地设计如下：

**1. 组件**（约 40 行，含注释）
- 新文件 `src/battery_analysis/main/ui_components/dialogs/countdown_message_box.py`（与现有 `ui_components/config_dialog/` 平级，目录结构顺理成章）
- 函数式 API：`show_countdown_notice(parent, *, title, text, timeout_seconds=3, ok_text="OK", countdown_on_button=True) -> bool`
- 实现：QMessageBox + `box.button(StandardButton.Ok).setText(f"{ok_text} ({remaining})")` + `QTimer(1000ms)` tick，到 0 `accept()`；居中逻辑照搬现有实现（adjustSize + moveCenter）；`exec()` 返回后防御性 stop timer

**2. 迁移**：`_show_spec_method_default_notice`（`data_processor.py:406-434`）改为调 `show_countdown_notice(timeout_seconds=5)`，删掉原 30 行。旧弹框按钮同步显示 `OK (5)`——两处视觉一致，我认为应该接受；若坚持不动旧 UX，传 `countdown_on_button=False`，一个参数的事，留待拍板。

**3. 检测**：
- `set_specification_type` 改为返回匹配型号 `str | None`（范式照抄 `set_specification_method`，`filename_parser.py:22-28`）
- `data_processor.py:312` 接住返回值；`None` → 置 `self._spec_missing_rules = True`（照抄 `_spec_method_defaulted` 标志位模式，`data_processor.py:273-275` 的"处理完统一弹"链路现成）
- **型号缺失与方法默认同时发生 → 合并为一个弹框**，文案同时说明两件事，避免连环弹框

**4. 文案**：型号位置显示文件名兜底（不做正则提取）；路径为纯文本"设置 → 电池配置 → Rules"；全部走 `_()` + 补 locale 条目

**5. 去重**：`self._missing_rules_warned: set[str]`（以文件名/型号为 key），同 key 一次会话只弹一次，覆盖批量转换场景

**6. 配置**：`utils/config_defaults.py` 的 BatteryConfig 下加 `missing_rules_notice: {"enabled": true, "timeout_seconds": 3}`，仅此两个开关，不放文案模板

**7. 测试**：组件单测（秒数递减、到时自动关、OK 立即关、timer 清理）+ `set_specification_type` 返回值单测 + 两条入口的回归

**工作量维持 Round 1 估计：约 1 个工作日**（组件+迁移 2h、检测改造 1h、文案与判定细节 2-3h、i18n 1-2h、测试回归 2-3h）。DeepSeek 的 4h 版本不含型号判定这个真正的不确定项，不可采信。

---

## 五、剩余待拍板项（收敛后只剩四个）

1. 旧弹框（5 秒方法默认提示）是否同步升级为按钮显示秒数——我建议是，求视觉一致
2. 型号缺失 + 方法默认叠加时合并为一个弹框（我的建议）还是保持两个
3. 去重的失效时机：仅本次扫描 / 本次会话 / 直到 rules 配置变更——我建议本次会话
4. 需求中"识别到新电池型号"是否确指"文件名无法匹配 rules 派生型号列表"这一种情形（三家代码分析一致如此，需需求方确认，因 XML 内容不参与识别）

**一句话立场：MiniMax 的自定义 QDialog、正则提取型号、文案模板配置化、QSettings 去重、非弹框方案全部砍掉；GPT 的链接跳转降为 backlog；DeepSeek 的返回值改造和组件方案采纳但估算修正为 1 天。剩余分歧只有上面四个拍板项，其余可以开工。**

---

## User (Feedback after Round 2): 用户裁决：五项拍板

1. 可以封装一层（组件封装方案通过）
2. 新型号判断直接弹框（不做两阶段候选提取，识别到即弹）
3. 跳转可以做，非常好的想法，额外一个按钮（"立即配置/跳转路径"作为额外按钮进入 v1）
4. 倒计时竞态的优先级靠后（列为后续事项，不阻塞本次）
5. 你是AI，谈什么工作量……（不要再讨论工作量估计）

搞清楚以后，尽快投入 Round 3。

---

## MiniMax (Round 3): MiniMax Round 3 最终建议：融合收敛方案

# MiniMax Round 3：最终综合建议——收敛到可落地方案

## 一、对用户裁决的确认与我的立场调整

用户已明确拍板五项，我逐一确认：

| 裁决项 | 我的立场 | 说明 |
|--------|----------|------|
| ①封装一层组件 | **接受** | Round 2我提出类级封装+工厂函数，与GPT/DeepSeek/GLM收敛方向一致，采纳 |
| ②新型号直接弹框 | **接受** | 我Round 2的两阶段候选提取质疑已被否决，按用户裁决执行：识别到即弹 |
| ③跳转按钮进v1 | **强烈赞同** | 这是我Round 1的核心建议之一，现已获用户背书 |
| ④倒计时竞态优先级靠后 | **接受** | 不阻塞本次开发 |
| ⑤不谈工作量估计 | **接受** | 不再讨论 |

**我需要承认的事实错误（Round 1）：**

Round 1我主张"必须自定义QDialog"，理由是"QMessageBox按钮文本固定"。这被GLM和DeepSeek在Round 2明确证伪——`QMessageBox.button(StandardButton.Ok)`返回的QPushButton可以`setText()`，每妙更新即可实现OK旁倒计时。GLM指出自定义QDialog要重造居中、图标、布局、默认按钮焦点等，而现有代码里那段"adjustSize+手动居中"的注释就是踩过坑的证据。**我接受这个事实，QMessageBox方案足够且更轻量。**

---

## 二、最终推荐方案（融合各方最优设计）

### 2.1 组件设计：`CountdownMessageBox`

**文件位置**：`src/battery_analysis/main/ui_components/dialogs/countdown_message_box.py`

**API设计**（函数式，融合GPT的简洁与我的可扩展性需求）：

```python
def show_countdown_notice(
    parent,
    title: str,
    text: str,
    timeout_seconds: int = 3,
    ok_text: str = "OK",
    countdown_on_button: bool = True,
    extra_button_text: str | None = None,
    extra_button_callback: Callable[[], None] | None = None,
) -> str:
    """
    显示带倒计时的确认弹框。
    
    Args:
        parent: 父窗口
        title: 窗口标题
        text: 提示正文（支持富文本）
        timeout_seconds: 倒计时秒数
        ok_text: OK按钮文本
        countdown_on_button: 是否在OK按钮上显示倒计时
        extra_button_text: 额外按钮文本（如"立即配置"）
        extra_button_callback: 额外按钮点击回调
        
    Returns:
        "ok" | "extra_button" | "timeout" | "closed"
    """
```

**关键实现细节**：

1. **按钮倒计时更新**（采纳DeepSeek/GLM方案）：
   ```python
   ok_button = box.button(QW.QMessageBox.StandardButton.Ok)
   if countdown_on_button:
       ok_button.setText(f"{ok_text} ({remaining})")
   ```

2. **额外按钮处理**（用户裁决③的落地）：
   ```python
   if extra_button_text:
       extra_btn = box.addButton(extra_button_text, QW.QMessageBox.ActionRole)
       if extra_button_callback:
           box.buttonClicked.connect(lambda b: (
               extra_button_callback(),
               box.accept()
           ) if b == extra_btn else None)
   ```

3. **倒计时结束逻辑**：
   ```python
   def tick():
       nonlocal remaining
       remaining -= 1
       if remaining <= 0:
           timer.stop()
           box.accept()
       elif countdown_on_button:
           ok_button.setText(f"{ok_text} ({remaining})")
   ```

4. **返回值处理**（为跳转按钮设计）：
   ```python
   result = box.exec()
   timer.stop()
   
   clicked = box.clickedButton()
   if clicked == ok_button:
       return "ok"
   elif clicked == extra_btn:
       return "extra_button"
   elif result == QW.QDialog.Accepted:
       return "timeout"  # 倒计时到自动accept
   else:
       return "closed"
   ```

5. **居中逻辑**（照搬现有实现，GLM验证过QMessageBox无aboutToShow信号）：
   ```python
   box.adjustSize()
   geo = box.geometry()
   geo.moveCenter(parent.geometry().center())
   box.setGeometry(geo)
   ```

---

### 2.2 触发点：统一单钩子点

**位置**：`data_processor._process_first_excel_file()`，`set_specification_type()`调用之后

**流程**：
```python
# data_processor.py:312 附近
matched_spec = filename_parser.set_specification_type(
    filename, all_spec_types, mw.comboBox_Specification_Type
)
if not matched_spec:
    # 用户裁决②：直接弹框，不做候选提取
    self._spec_missing_rules = True
    self._missing_rules_filename = filename  # 记录文件名用于文案
```

**弹框触发**（在`_on_excel_files_processed()`末尾，与`_spec_method_defaulted`同一链路）：
```python
if self._spec_missing_rules:
    # 去重检查
    key = self._missing_rules_filename
    if key not in self._missing_rules_warned:
        self._missing_rules_warned.add(key)
        
        result = show_countdown_notice(
            parent=mw,
            title=_("电池型号配置缺失"),
            text=_("未在系统配置中找到电池型号 [{filename}] 的配置信息。\n"
                   "请前往以下路径补充配置：\n设置 → 电池配置 → Rules"),
            timeout_seconds=3,
            ok_text=_("确定"),
            countdown_on_button=True,
            extra_button_text=_("立即配置"),
            extra_button_callback=lambda: self._open_rules_editor(),
        )
        
        if result == "extra_button":
            # 跳转已由callback处理
            pass
```

---

### 2.3 跳转按钮实现（v1重点）

**跳转目标**：`main/ui_components/config_dialog/battery_config_page.py` 的 `_RulesEditor`（GLM确认的入口）

**实现方式**：
```python
def _open_rules_editor(self):
    """打开Rules编辑对话框"""
    from ..config_dialog.battery_config_page import BatteryConfigPage
    
    config_page = BatteryConfigPage(self.main_window)
    dialog = QW.QDialog(self.main_window)
    layout = QVBoxLayout(dialog)
    layout.addWidget(config_page)
    dialog.setWindowTitle(_("电池配置"))
    dialog.resize(800, 600)
    dialog.exec()
```

**用户体验优化**：
- 点击"立即配置"后，弹框关闭，配置对话框直接打开
- 用户在Rules编辑页补完配置后关闭对话框
- 下次加载文件时，型号识别成功，不再弹框——形成"缺失→引导→补齐→恢复"闭环

---

### 2.4 与旧弹框的复用关系

**迁移方案**（采纳GLM建议）：

`_show_spec_method_default_notice()`（`data_processor.py:406-434`）改为：
```python
def _show_spec_method_default_notice(self) -> None:
    show_countdown_notice(
        parent=self.main_window,
        title=_("Default Specification Method"),
        text=_("The specification method was not found for this battery. "
               "{method} has been selected by default. Please confirm."
               ).format(method=self.SPEC_METHOD_DEFAULT),
        timeout_seconds=5,
        ok_text=_("OK"),
        countdown_on_button=True,  # 旧弹框同步升级
    )
```

**视觉一致性**：迁移后旧弹框的OK按钮也会显示"OK (5)"→"OK (1)"，与新弹框风格统一。保留`countdown_on_button=False`参数作为逃生口，但**建议默认升级**（GLM和GPT均持此立场，视觉一致性好过两套UX）。

---

### 2.5 文案与路径配置

**硬编码文案，走i18n管道**（采纳GLM/GPT的共识，反对我Round 1的配置化方案）：

| 场景 | 标题 | 正文 | 按钮 |
|------|------|------|------|
| 新型号缺失 | 电池型号配置缺失 | 未在系统配置中找到电池型号 [{文件名}] 的配置信息。请前往以下路径补充配置：设置 → 电池配置 → Rules | 确定 (3) / 立即配置 |
| 规格方法默认（迁移后） | Default Specification Method | The specification method was not found for this battery. {method} has been selected by default. Please confirm. | OK (5) |

**路径文本**：纯文本"设置 → 电池配置 → Rules"（不做过早的可点击链接，链接跳转进v2，MVP聚焦核心功能）

**配置项**（`config_defaults.py`的BatteryConfig下，仅行为参数）：
```python
"missing_rules_notice": {
    "enabled": True,
    "timeout_seconds": 3,
}
```

---

### 2.6 去重策略

**会话级内存set**（采纳GLM的务实建议，反对我Round 1的QSettings持久化）：
```python
self._missing_rules_warned: set[str] = set()  # 在DataProcessor.__init__初始化
```

**失效时机**：进程重启即清零，每次会话独立。去重key为文件名（而非仅型号），因为同一型号文件名可能不同。

---

## 三、创新交互设计（Round 3新增）

在用户裁决框架内，我从横向思考角度补充以下交互细节：

### 3.1 倒计时视觉优化

**倒计时结束的"弹跳"效果**：
- 最后1秒时，按钮文案从"确定 (1)"变为"确定"，数字消失而非显示"确定 (0)"
- 这比显示"确定 (0)"更自然，符合用户对"倒计时结束→可点击"的预期

**实现**：
```python
def tick():
    nonlocal remaining
    remaining -= 1
    if remaining <= 0:
        timer.stop()
        ok_button.setText(ok_text)  # 恢复原始文本
        box.accept()
    else:
        ok_button.setText(f"{ok_text} ({remaining})")
```

### 3.2 批量文件的"合并提示"（可选增强）

如果用户一次拖入多个文件都触发同一提示，合并为一条：
```
未在系统配置中找到以下电池型号的配置信息：
• 文件1.xlsx
• 文件2.xlsx
• 文件3.xlsx
请前往以下路径补充配置：设置 → 电池配置 → Rules
```

**实现**：用200ms debounce timer收集同批次触发，维护`_pending_missing_files: list`，到期后合并弹框。

*注：此功能优先级低，可作为v1.1增强，不阻塞主方案。*

### 3.3 弹框层级保护

确保弹框始终显示在正确层级：
```python
# parent传main_window而非当前活跃tab，防止tab切换导致弹框"消失"
show_countdown_notice(parent=self.main_window, ...)
```

---

## 四、方案总结

| 维度 | 决策 | 依据 |
|------|------|------|
| 组件形式 | QMessageBox + button.setText() | GLM/DeepSeek验证，QMessageBox足够 |
| 组件API | 函数式show_countdown_notice() | 融合GPT简洁与我的可扩展性 |
| 触发点 | data_processor._process_first_excel_file() | 四家一致收敛 |
| 新型号判定 | set_specification_type()返回None即弹框 | 用户裁决② |
| 跳转按钮 | "立即配置"作为额外按钮进v1 | 用户裁决③ |
| 旧弹框迁移 | 同步升级为OK旁倒计时 | GLM/GPT立场，我接受 |
| 文案配置 | 硬编码走i18n，不入config | GLM/GPT共识 |
| 去重 | 会话级set，key为文件名 | GLM务实建议 |
| 倒计时竞态 | 优先级靠后 | 用户裁决④ |

---

## 五、待实现检查清单

- [ ] 新建 `countdown_message_box.py` 组件
- [ ] 改造 `set_specification_type()` 返回 `str | None`
- [ ] 在 `_process_first_excel_file()` 增加检测逻辑
- [ ] 在 `_on_excel_files_processed()` 末尾调用弹框
- [ ] 实现 `_open_rules_editor()` 跳转方法
- [ ] 迁移 `_show_spec_method_default_notice()` 到共享组件
- [ ] 配置项加 `missing_rules_notice` 到 `config_defaults.py`
- [ ] i18n添加新文案条目
- [ ] 单元测试：组件、返回值、回归两条入口

**一句话立场**：融合四家最优方案，在用户裁决框架内收敛为可立即开工的v1设计。组件轻量（QMessageBox够用）、跳转闭环（v1重点）、旧弹框统一升级（UX一致性）。

---

## GPT (Round 3): FINAL 推荐方案：共享 CountdownMessageBox 组件 + 单钩子点直接弹框 + 跳转按钮进 v1 + 合并弹框防轰炸 + 配置仅放行为参数

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

---

## DeepSeek (Round 3): 综合四方意见与用户五项拍板，给出最终落地方案：函数式API封装组件、QMessageBox+button.setText实现倒计时、无正则候选提取直接弹框显示文件名、额外"立即配置"按钮跳转Rules页、旧弹框迁移但保留计时器差异、配置仅存行为参数、内存去重。

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

---

## GLM (Round 3): 按用户五项裁决给出最终方案：show_countdown_notice 函数式组件（QMessageBox+button().setText，extra_button 支持跳转）、set_specification_type 返回 str|None 在 data_processor.py:312 单钩子检测两入口、文案走 _() 配置只放开关、跳转按钮直调 mw.show_config_dialog() 落在 Battery 首个 tab、旧 5 秒弹框迁移进组件并接受 OK(5) 升级，候选提取/去重/竞态全部出 v1。

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


---
