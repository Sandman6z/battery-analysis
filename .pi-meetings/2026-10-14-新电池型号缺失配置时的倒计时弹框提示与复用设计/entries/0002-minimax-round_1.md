# MiniMax (Round 1): 创新交互方案、文案设计、边缘情况与非常规替代思路

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
