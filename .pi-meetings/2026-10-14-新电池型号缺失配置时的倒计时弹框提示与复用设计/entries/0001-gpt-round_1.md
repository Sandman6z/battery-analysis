# GPT (Round 1): 从愿景和架构角度分析新电池型号缺失配置弹框的触发点、复用策略和用户体验设计

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