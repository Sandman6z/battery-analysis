# DeepSeek (Round 1): 从系统架构、代码复用、配置机制和事件流四个维度分析新电池型号缺失配置时的倒计时弹框提示方案

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