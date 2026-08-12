# English Default + Settings Polish + Framework Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 默认语言锁定为英文（保留 i18n）、配置对话框改为主从（master-detail）逐条化布局并派生只读 Specifications、删除未接入的 clean-architecture 死骨架与死代码。

**Architecture:** 三个独立阶段，各自以「测试全绿 + 提交」为检查点。
- **Phase 1 英文化**：默认 `en`；`_()` 调用规范化为 `_("英文 msgid")`；脚本重建 en/zh_CN .po；硬编码中文（界面 + 日志）转英文。
- **Phase 2 设置/配置**：新建 `battery_classifier` 工具；`ConfigDialog` 改为左导航 + 右 `QStackedWidget`；Rules 改 6 列 `QTableWidget`；Specifications 派生只读；`_ListEditor` 消除重复的 `_fill_list/_read_list`；`PreferencesDialog` 迁出 `i18n/` 包并合并 `IConfigPathProvider`；main_window 配置重载走 `ConfigService`。
- **Phase 3 框架清理**：删除 `application/`、`infrastructure/`、`domain/{services,repositories}`、4 个 domain 实体（保留 `test_info.py`）、`LanguageHandler`、`I18nService`、`ApplicationService`、`VisualizerController` 及其配套测试，同步更新 `container.py`/`controllers/__init__.py`。

**Tech Stack:** Python 3.13, PyQt6, gettext/SimplePOTranslator, pytest, JsonConfigManager。

**Working state:** 当前分支 `feat/setting-config`，工作区有大量未提交改动（i18n、config_dialog、tests 等）。每个任务只 add 自己触及的文件，不要 `git add -A`。

---

## Phase 1 — 英文化（English Default）

### Task 1.1: 默认语言锁定 en — `i18n/__init__.py`

**Files:**
- Modify: `src/battery_analysis/i18n/__init__.py:132-146`（`initialize_default_locale`）
- Modify: `tests/battery_analysis/i18n/test_i18n.py:353-370`（`TestModuleFunctionsInitializeDefaultLocale`）

- [ ] **Step 1: 改写测试——默认必须是英文，不再跟随系统**

把 `TestModuleFunctionsInitializeDefaultLocale` 整个类替换为：

```python
class TestModuleFunctionsInitializeDefaultLocale:
    """__init__.initialize_default_locale — 默认锁定英文"""

    def test_initializes_to_english(self):
        from battery_analysis.i18n import initialize_default_locale
        with patch("battery_analysis.i18n.set_locale", return_value=True) as mock_set:
            assert initialize_default_locale() is True
            mock_set.assert_called_once_with("en")

    def test_returns_false_when_english_unavailable(self):
        from battery_analysis.i18n import initialize_default_locale
        with patch("battery_analysis.i18n.set_locale", return_value=False) as mock_set:
            assert initialize_default_locale() is False
            mock_set.assert_called_once_with("en")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/battery_analysis/i18n/test_i18n.py::TestModuleFunctionsInitializeDefaultLocale -v`
Expected: FAIL —— 现有实现会调用 `detect_system_locale()`，mock 断言 `set_locale("en")` 失败。

- [ ] **Step 3: 最小实现——直接 `set_locale("en")`**

替换 `src/battery_analysis/i18n/__init__.py` 的 `initialize_default_locale`：

```python
def initialize_default_locale() -> bool:
    """Initialize with English (the application default)."""
    return set_locale("en")
```

同时把模块顶部 auto-initialize 处保留不变（仍会调用 `initialize_default_locale()` → `en`）。`detect_system_locale()` 函数保留（仍被 `language_manager.reset_to_default` 与测试使用），不再作为默认入口。

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/battery_analysis/i18n/test_i18n.py -v`
Expected: 全部通过。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/i18n/__init__.py tests/battery_analysis/i18n/test_i18n.py
git commit -m "feat: lock default locale to English in i18n init"
```

---

### Task 1.2: 默认语言锁定 en — `LanguageManager._initialize_settings`

**Files:**
- Modify: `src/battery_analysis/i18n/language_manager.py:61-76`（`_initialize_settings`）
- Modify: `tests/battery_analysis/i18n/test_i18n.py`（`TestLanguageManager`）

- [ ] **Step 1: 加测试——无已存偏好时默认 en**

在 `TestLanguageManager` 类末尾追加：

```python
def test_default_locale_is_english_when_no_saved(self):
    from battery_analysis.i18n.language_manager import LanguageManager
    lm = LanguageManager()
    lm.settings = MagicMock()
    lm.settings.value.return_value = ""
    with patch.object(lm, "set_locale", return_value=True) as mock_set:
        lm._initialize_settings()
    mock_set.assert_called_once_with("en")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/battery_analysis/i18n/test_i18n.py::TestLanguageManager::test_default_locale_is_english_when_no_saved -v`
Expected: FAIL —— 现有实现调用 `detect_system_locale()` 而非 `"en"`。

- [ ] **Step 3: 最小实现**

把 `_initialize_settings` 中 `if not saved_locale:` 分支替换为：

```python
        if not saved_locale:
            # 默认语言固定为英文（不跟随系统语言）
            saved_locale = "en"
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/battery_analysis/i18n/test_i18n.py -v`
Expected: 全部通过（`reset_to_default` 仍用 `detect_system_locale`，测试不受影响）。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/i18n/language_manager.py tests/battery_analysis/i18n/test_i18n.py
git commit -m "feat: default LanguageManager locale to English"
```

---

### Task 1.3: `_()` 调用规范化（上）——menu_manager / theme_manager / progress_dialog / validation_manager

**Files:**
- Modify: `src/battery_analysis/main/ui_components/menu_manager.py`
- Modify: `src/battery_analysis/main/ui_components/theme_manager.py`
- Modify: `src/battery_analysis/main/ui_components/progress_dialog.py`
- Modify: `src/battery_analysis/main/business_logic/validation_manager.py`

**背景**：`_("key", "fallback")` 把第二参数当 gettext context 传入，而 .po 无 `msgctxt`，必然显示 key。所有双参调用统一改为 `_("英文文本")`，msgid 即显示文本。

- [ ] **Step 1: 改写 menu_manager.py**

把 `setup_menu_shortcuts` 里的工具提示按下表替换（`_("old", "...")` → `_("New English")`）：

```python
_("tooltip_new", "新建项目")        → _("New Project")
_("tooltip_open", "打开项目")       → _("Open Project")
_("tooltip_save", "保存设置")       → _("Save Settings")
_("tooltip_save_as", "另存为")      → _("Save As")
_("tooltip_exit", "退出应用")       → _("Exit")
_("tooltip_undo", "撤销操作")       → _("Undo")
_("tooltip_redo", "重做操作")       → _("Redo")
_("tooltip_cut", "剪切选中内容")     → _("Cut")
_("tooltip_copy", "复制选中内容")    → _("Copy")
_("tooltip_paste", "粘贴内容")      → _("Paste")
_("tooltip_zoom_in", "放大界面")    → _("Zoom In")
_("tooltip_zoom_out", "缩小界面")   → _("Zoom Out")
_("tooltip_reset_zoom", "重置界面缩放") → _("Reset Zoom")
_("tooltip_show_toolbar", "显示/隐藏工具栏") → _("Show/Hide Toolbar")
_("tooltip_show_statusbar", "显示/隐藏状态栏") → _("Show/Hide Status Bar")
_("tooltip_calculate_battery", "计算电池参数") → _("Calculate Battery Parameters")
_("tooltip_analyze_data", "分析数据") → _("Analyze Data")
_("tooltip_generate_report", "生成报告") → _("Generate Report")
_("tooltip_chart_viewer", "打开电池图表查看器") → _("Open Battery Chart Viewer")
_("tooltip_batch_processing", "批量处理数据") → _("Batch Process Data")
_("tooltip_configuration", "配置管理系统数据字典") → _("Manage Data Dictionary")
_("tooltip_preferences", "首选项设置") → _("Preferences")
_("tooltip_user_manual", "打开用户手册") → _("Open User Manual")
_("tooltip_online_help", "打开在线帮助") → _("Open Online Help")
_("tooltip_about", "关于应用")      → _("About")
_("tooltip_export_report", "导出报告") → _("Export Report")
```

另外：
- 第 261 行 `update_menu_texts` 的注释示例行 `# 例如：self.main_window.actionExit.setText(_("menu_exit", "Exit"))` 删除（避免污染 msgid 提取）。
- `update_statusbar_messages` 里 `status_ready = _("status_ready", "状态:就绪")` → `status_ready = _("Ready")`。
- `setup_menu_shortcuts` 底部 `logging.error("设置菜单快捷键和工具提示失败: %s", e)` → `logging.error("Failed to set up menu shortcuts and tooltips: %s", e)`。

- [ ] **Step 2: 改写 theme_manager.py**

工具提示映射表：

```python
_("tooltip_system_default", "使用系统默认主题")  → _("Use System Default Theme")
_("tooltip_windows_11", "使用Windows 11风格主题") → _("Use Windows 11 Style Theme")
_("tooltip_windows_vista", "使用Windows Vista风格主题") → _("Use Windows Vista Style Theme")
_("tooltip_fusion", "使用跨平台Fusion主题")       → _("Use Cross-platform Fusion Theme")
_("tooltip_dark_theme", "使用深色主题，适合夜间使用") → _("Use Dark Theme for Night Use")
```

`set_theme` 里的状态栏消息（含内联中文）替换为英文：

```python
_("theme_switched_default", f"已切换到系统默认主题")  → _("Switched to System Default theme")
_("theme_switched_fusion", f"已切换到Fusion主题")     → _("Switched to Fusion theme")
_("theme_switched_dark", f"已切换到深色主题")         → _("Switched to Dark theme")
_("theme_switched_simple_dark", f"已切换到简单深色主题") → _("Switched to Simple Dark theme")
_("theme_switch_failed", f"切换主题失败: {str(e)}")   → f"Failed to switch theme: {str(e)}"
```

Windows 11 / Vista 分支的内联中文 f-string 改为英文：
- `f"已切换到Windows 11主题"` → `"Switched to Windows 11 theme"`
- `f"已切换到Fusion主题（Windows 11样式在当前平台不可用）"` → `"Switched to Fusion theme (Windows 11 style is unavailable on this platform)"`
- `f"已切换到Windows Vista主题"` → `"Switched to Windows Vista theme"`
- `f"已切换到Fusion主题（Windows Vista样式在当前平台不可用）"` → `"Switched to Fusion theme (Windows Vista style is unavailable on this platform)"`
- `self.logger.error("切换主题失败: %s", e)` → `self.logger.error("Failed to switch theme: %s", e)`

- [ ] **Step 3: 改写 progress_dialog.py**

```python
_("progress_title", "Battery Analysis Progress")    → _("Battery Analysis Progress")
_("progress_ready", "Ready to start analysis...")   → _("Ready to start analysis...")
_("cancel", "Cancel")                                → _("Cancel")
_("progress_canceled", "Task canceled...")           → _("Task canceled...")
self.setWindowTitle(f"{_("progress_title", "Battery Analysis Progress")} - {progress}%")
    → self.setWindowTitle(f"{_("Battery Analysis Progress")} - {progress}%")
```

- [ ] **Step 4: 改写 validation_manager.py**

```python
_("status_ok", "status:ok")  →  _("Ready")
```

（3 处，均出现在 `showMessage` 调用中。）

- [ ] **Step 5: 验证无残留双参调用**

Run: `grep -rn '_\s*("[^"]*"\s*,\s*"' src/battery_analysis/main/ui_components/menu_manager.py src/battery_analysis/main/ui_components/theme_manager.py src/battery_analysis/main/ui_components/progress_dialog.py src/battery_analysis/main/business_logic/validation_manager.py`
Expected: 无输出。

- [ ] **Step 6: 运行相关测试**

Run: `python -m pytest tests/battery_analysis/main/ui_components/test_menu_manager.py tests/battery_analysis/main/ui_components/test_theme_manager.py tests/battery_analysis/main/ui_components/test_progress_dialog.py -v`
Expected: 通过（这些测试用 mock main_window，不校验具体字符串）。

- [ ] **Step 7: 提交**

```bash
git add src/battery_analysis/main/ui_components/menu_manager.py src/battery_analysis/main/ui_components/theme_manager.py src/battery_analysis/main/ui_components/progress_dialog.py src/battery_analysis/main/business_logic/validation_manager.py
git commit -m "refactor(i18n): normalize _() calls to English msgids (menus, theme, progress, validation)"
```

---

### Task 1.4: `_()` 调用规范化（中）——dialog_manager / data_processor / help_manager / signal_connector / analysis_runner / main_window

**Files:**
- Modify: `src/battery_analysis/main/ui_components/dialog_manager.py`
- Modify: `src/battery_analysis/main/business_logic/data_processor.py`
- Modify: `src/battery_analysis/main/business_logic/help_manager.py`
- Modify: `src/battery_analysis/main/utils/signal_connector.py`
- Modify: `src/battery_analysis/main/managers/analysis_runner.py`
- Modify: `src/battery_analysis/main/main_window.py`

- [ ] **Step 1: 改写 dialog_manager.py**

`_()` 双参映射：

```python
_("confirm_exit_title", "确认退出")        → _("Confirm Exit")
_("confirm_exit_message", "确定要退出应用程序吗？") → _("Are you sure you want to exit the application?")
_("about_title", "About Battery Analyzer") → _("About Battery Analyzer")
_("error", "错误")                        → _("Error")
_("data_error_title", "数据加载错误 - 恢复选项") → _("Data Load Error - Recovery Options")
_("data_error_message", "无法加载电池数据，请选择如何继续:") → _("Unable to load battery data. Choose how to continue:")
_("data_error_prompt", "请选择以下恢复选项之一:") → _("Choose one of the following recovery options:")
_("data_error_retry", "重新选择数据目录")   → _("Reselect Data Directory")
_("data_error_default", "使用默认配置重新启动") → _("Restart with Default Configuration")
_("data_error_cancel", "取消操作")        → _("Cancel Operation")
_("ok", "确定")                          → _("OK")
_("cancel", "取消")                       → _("Cancel")
_("data_error_opening_dir", "正在打开数据目录选择...") → _("Opening data directory selector...")
_("data_error_restarting", "使用默认配置重新启动...") → _("Restarting with default configuration...")
_("data_error_restart_title", "重新启动")  → _("Restart")
_("data_error_restart_msg", "应用将使用默认配置重新启动。\n\n请确保您有有效的数据文件可用。") → _("The application will restart with the default configuration.\n\nPlease make sure you have valid data files available.")
_("data_error_cancelled", "操作已取消")    → _("Operation canceled")
_("data_error_cancelled_title", "取消")   → _("Canceled")
_("data_error_cancelled_msg", "操作已取消。您可以通过菜单 'File -> Open Data' 重新尝试。") → _("Operation canceled. You can retry via the 'File -> Open Data' menu.")
_("data_error_detail", f"错误详情: {error_msg}") → f"Error details: {error_msg}"
```

`show_user_manual` 里找不到手册时的内联中文改为英文：

```python
QW.QMessageBox.information(
    self.main_window,
    "用户手册",
    "未找到用户手册文件。\n\n"
    "请确保以下文件存在：\n"
    "• docs/user_manual.pdf\n"
    "• user_manual.pdf\n\n"
    "如需帮助，请联系技术支持。",
    QW.QMessageBox.StandardButton.Ok
)
```
替换为：

```python
QW.QMessageBox.information(
    self.main_window,
    "User Manual",
    "User manual file not found.\n\n"
    "Please make sure one of the following files exists:\n"
    "• docs/user_manual.pdf\n"
    "• user_manual.pdf\n\n"
    "For help, please contact technical support.",
    QW.QMessageBox.StandardButton.Ok
)
```

`show_online_help` 的内联中文改为英文：

```python
QW.QMessageBox.information(
    self.main_window,
    "Online Help",
    "Unable to open online help. Please check your network connection or contact technical support.\n\nHelp Center URL: https://example.com/battery-analyzer-help",
    QW.QMessageBox.StandardButton.Ok
)
```

`show_preferences`/`show_user_manual`/`show_online_help` 中的 `self.logger.error(...)` 中文消息改为英文：
- `"显示首选项对话框时发生错误: %s"` → `"Error showing preferences dialog: %s"`
- `"打开用户手册失败: %s"` → `"Failed to open user manual: %s"`
- `"成功打开用户手册: %s"` → `"Opened user manual: %s"`
- `"打开手册文件失败 %s: %s"` → `"Failed to open manual file %s: %s"`
- `logging.error("打开在线帮助失败: %s", e)` → `logging.error("Failed to open online help: %s", e)`

- [ ] **Step 2: 改写 data_processor.py**

```python
_("input_path_no_data", "[Error]: Input path has no data") → _("[Error]: Input path has no data")
_("status_ready", "状态:就绪")           → _("Ready")
_("warning_title", "警告")               → _("Warning")
_("input_path_not_set", "请先设置输入路径。") → _("Please set the input path first.")
_("analyzing_data", "分析数据...")       → _("Analyzing data...")
_("analysis_result", "分析结果")         → _("Analysis Result")
_("no_excel_files_found", "没有找到Excel文件。") → _("No Excel files found.")
_("error_title", "错误")                 → _("Error")
_("data_analysis_failed", "数据分析失败: {}").format(str(e)) → _("Data analysis failed: {}").format(str(e))
```

`logger` 中文消息改为英文（逐条）：

```python
self.logger.error("没有成功处理的Excel文件")           → self.logger.error("No Excel files were processed successfully")
self.logger.error("扫描Excel文件失败: %s", error_msg)  → self.logger.error("Failed to scan Excel files: %s", error_msg)
self.logger.info("获取Excel文件信息")                  → self.logger.info("Retrieving Excel file info")
self.logger.warning("没有找到Excel文件: %s", input_dir) → self.logger.warning("No Excel files found: %s", input_dir)
self.logger.warning("显示错误对话框时出错: %s", e)       → self.logger.warning("Error showing error dialog: %s", e)
self.logger.info("保存表格数据")                       → self.logger.info("Saving table data")
self.logger.info("更新配置")                           → self.logger.info("Updating configuration")
self.logger.info("开始数据分析")                       → self.logger.info("Starting data analysis")
self.logger.error("分析失败 %s: %s", result['filename'], result['error']) → self.logger.error("Analysis failed %s: %s", result['filename'], result['error'])
self.logger.info("数据分析汇总: %s", summary)          → self.logger.info("Data analysis summary: %s", summary)
self.logger.error("数据分析失败: %s", str(e))          → self.logger.error("Data analysis failed: %s", str(e))
```

- [ ] **Step 3: 改写 help_manager.py**

```python
_("error", "错误")            → _("Error")
_("warning_title", "警告")    → _("Warning")
_("failed_to_open_help", "无法打开在线帮助。") → _("Failed to open online help.")
```

- [ ] **Step 4: 改写 signal_connector.py**

```python
_("error_title", "错误")  →  _("Error")
```

- [ ] **Step 5: 改写 analysis_runner.py**

```python
_("validation_failed", "输入验证失败")     → _("Input Validation Failed")
_("input_path_empty", "输入数据路径不能为空") → _("Input data path cannot be empty")
_("output_path_empty", "输出路径不能为空")   → _("Output path cannot be empty")
_("start_failed", "启动失败")             → _("Start Failed")
_("cannot_start_analysis", "无法启动分析任务") → _("Cannot start the analysis task")
```

- [ ] **Step 6: 改写 main_window.py**

```python
logger.warning(_("app_icon_not_found", "未找到应用图标文件，使用默认图标")) → logger.warning(_("App icon not found; using default icon."))
self.signal_connector.progress_dialog.setWindowTitle(_("progress_title", "Battery Analysis Progress")) → _("Battery Analysis Progress")
self.signal_connector.progress_dialog.status_label.setText(_("progress_ready", "Ready to start analysis...")) → _("Ready to start analysis...")
```

- [ ] **Step 7: 验证无残留双参调用**

Run: `grep -rn '_\s*("[^"]*"\s*,\s*"' src/battery_analysis/main/ui_components/dialog_manager.py src/battery_analysis/main/business_logic/data_processor.py src/battery_analysis/main/business_logic/help_manager.py src/battery_analysis/main/utils/signal_connector.py src/battery_analysis/main/managers/analysis_runner.py src/battery_analysis/main/main_window.py`
Expected: 无输出。

- [ ] **Step 8: 运行相关测试**

Run: `python -m pytest tests/battery_analysis/main/ui_components/test_dialog_manager.py tests/battery_analysis/main/business_logic/test_data_processor.py tests/battery_analysis/main/managers/test_analysis_runner.py tests/battery_analysis/main/test_main_window.py -v`
Expected: 通过。

- [ ] **Step 9: 提交**

```bash
git add src/battery_analysis/main/ui_components/dialog_manager.py src/battery_analysis/main/business_logic/data_processor.py src/battery_analysis/main/business_logic/help_manager.py src/battery_analysis/main/utils/signal_connector.py src/battery_analysis/main/managers/analysis_runner.py src/battery_analysis/main/main_window.py
git commit -m "refactor(i18n): normalize _() calls to English msgids (dialogs, processors, window)"
```

---

### Task 1.5: `_()` 调用规范化（下）——ui_manager / preferences_dialog / config_dialog

**Files:**
- Modify: `src/battery_analysis/main/ui_components/ui_manager.py`
- Modify: `src/battery_analysis/i18n/preferences_dialog.py`
- Modify: `src/battery_analysis/main/ui_components/config_dialog.py`

- [ ] **Step 1: 改写 ui_manager.py**

`_()` 双参映射（accessible 名称/描述与 tooltip，全为英文 msgid）：

```python
_("access_test_config", "测试配置")            → _("Test Config")
_("access_test_config_desc", "包含测试相关配置的设置") → _("Settings related to the test configuration")
_("access_battery_config", "电池配置")          → _("Battery Config")
_("access_battery_config_desc", "包含电池相关配置的设置") → _("Settings related to the battery configuration")
_("access_run_button", "运行分析")             → _("Run Analysis")
_("access_run_button_desc", "开始电池分析任务")   → _("Start battery analysis")
_("access_test_profile_button", "选择测试文件")   → _("Select Test Profile")
_("access_test_profile_desc", "选择电池测试配置文件") → _("Select battery test profile file")
_("access_input_path_button", "选择输入路径")     → _("Select Input Path")
_("access_input_path_desc", "选择输入数据文件路径") → _("Select input data file path")
_("access_output_path_button", "选择输出路径")    → _("Select Output Path")
_("access_output_path_desc", "选择分析结果输出路径") → _("Select analysis output path")
_("access_test_info_table", "测试信息表格")       → _("Test Information Table")
_("access_test_info_table_desc", "包含测试设备和软件版本信息的表格") → _("Table containing test equipment and software version information")

_("This is test config", "测试配置组 - 包含测试相关配置的设置") → _("Test config group - settings related to the test configuration")
_("This is battery_config", "电池配置组 - 包含电池相关配置的设置") → _("Battery config group - settings related to the battery configuration")
_("This is battery_type", "选择电池类型")        → _("Select battery type")
_("This is construction_method", "选择电池构造方法") → _("Select battery construction method")
_("This is specification_type", "选择电池规格类型") → _("Select battery specification type")
_("This is specification_method", "选择电池规格方法") → _("Select battery specification method")
_("This is manufacturer", "选择电池制造商")       → _("Select battery manufacturer")
_("This is batch_date_code", "输入电池批次日期代码") → _("Enter battery batch date code")
_("This is samples_qty", "输入样品数量")         → _("Enter number of samples")
_("This is temperature_type", "选择测试温度类型")  → _("Select temperature type")
_("This is temperature_value", "输入冷冻温度值")   → _("Enter freezing temperature value")
_("This is datasheet_capacity", "输入数据手册中的标称容量") → _("Enter datasheet nominal capacity")
_("This is calculation_capacity", "输入计算得出的标称容量") → _("Enter calculated nominal capacity")
_("This is accelerated_aging", "输入加速老化天数") → _("Enter accelerated aging days")
_("This is required_capacity", "输入所需可用容量") → _("Enter required usable capacity")
_("This is tester location", "选择测试地点")      → _("Select tester location")
_("This is tested people", "选择测试人员")       → _("Select tested-by")
_("This is reported people", "选择报告人员")     → _("Select reported-by")
_("This is test profile, it's a xml file", "测试配置文件路径") → _("Test profile file path")
_("Here need to select test profile", "选择测试配置文件") → _("Select test profile file")
_("Input data file path", "输入数据文件路径")     → _("Input data file path")
_("Please select input path", "选择输入数据文件路径") → _("Select input data file path")
_("Output data file path", "输出结果文件路径")    → _("Output result file path")
_("Please select output path", "选择输出结果文件路径") → _("Select output result file path")
_("Go!", "开始运行电池分析")                    → _("Start battery analysis")
_("Here is the version", "输入版本号")           → _("Enter version number")
_("Here is test infomation table", "测试信息表格 - 包含测试设备和软件版本信息") → _("Test information table - contains test equipment and software version information")
_("progress_title", "Battery Analysis Progress") → _("Battery Analysis Progress")
_("progress_ready", "Ready to start analysis...") → _("Ready to start analysis...")
_("status_ready", "状态:就绪")                  → _("Ready")
```

- [ ] **Step 2: 改写 preferences_dialog.py**

`_()` 双参映射（这些 key 对应的英文文本本身就是新 msgid）：

```python
_("preferences_title", "Preferences")          → _("Preferences")
_("general_settings", "General Settings")      → _("General Settings")
_("auto_save", "Auto-save settings")           → _("Auto-save settings")          # Phase 2 将删除该项
_("auto_save_tooltip", "Automatically save settings when changes are made") → _("Automatically save settings when changes are made")
_("confirm_exit", "Confirm before exiting")    → _("Confirm before exiting")
_("confirm_exit_tooltip", "Show confirmation dialog when exiting the application") → _("Show confirmation dialog when exiting the application")
_("display_settings", "Display Settings")      → _("Display Settings")
_("theme", "Theme:")                           → _("Theme:")
_("theme_light", "Light")                      → _("Light")
_("theme_dark", "Dark")                        → _("Dark")
_("theme_system", "System")                    → _("System")
_("font_size", "Font Size:")                   → _("Font Size:")
_("general", "General")                        → _("General")
_("language_settings", "Language Settings")    → _("Language Settings")
_("current_language", "Current Language:")     → _("Current Language:")
_("select_language", "Select Language:")       → _("Select Language:")
_("apply_language", "Apply Language")          → _("Apply Language")
_("translation_status", "Translation Status")  → _("Translation Status")
_("translation_info", "Translation information will be displayed here.") → _("Translation information will be displayed here.")
_("language", "Language")                      → _("Language")
_("config_file_settings", "Configuration File Settings") → _("Configuration File Settings")
_("current_config_path", "Current Config Path:") → _("Current Config Path:")
_("not_loaded", "Not loaded")                  → _("Not loaded")
_("custom_config_path", "Custom Config Path:") → _("Custom Config Path:")
_("enter_config_path", "Enter custom configuration file path...") → _("Enter custom configuration file path...")
_("browse", "Browse...")                       → _("Browse...")
_("validate_config", "Validate Configuration") → _("Validate Configuration")
_("required_sections", "Required Sections in Config File") → _("Required Sections in Config File")
_("reset_to_default", "Reset to Default")      → _("Reset to Default")
_("config", "Config")                          → _("Config")
_("select_config_file", "Select Configuration File") → _("Select Configuration File")
_("please_enter_path", "Please enter a configuration file path") → _("Please enter a configuration file path")
_("file_not_exists", "File does not exist")    → _("File does not exist")
_("invalid_json", "JSON root must be an object") → _("JSON root must be an object")
_("config_valid", "Configuration file is valid!") → _("Configuration file is valid!")
_("ini_deprecated", "INI format is deprecated; consider migrating to config.json") → _("INI format is deprecated; consider migrating to config.json")
_("ok", "OK")                                  → _("OK")
_("cancel", "Cancel")                          → _("Cancel")
_("apply", "Apply")                            → _("Apply")
_("using_default", "Using default paths")      → _("Using default paths")
_("warning", "Warning")                        → _("Warning")
_("language_change_failed", "Failed to change language") → _("Failed to change language")
_("error", "Error")                            → _("Error")
_("language_change_error", "Language change error") → _("Language change error")
_("settings_apply_error", "Settings apply error") → _("Settings apply error")
_("translation_status_text", f"Translation coverage: {translated_keys}/{total_keys} keys translated") → _(f"Translation coverage: {translated_keys}/{total_keys} keys translated")
_('translation_complete', '✓ Translation is complete') → _("✓ Translation is complete")
_('translation_incomplete', '⚠ Some translations are missing') → _("⚠ Some translations are missing")
_("missing_sections", f"Missing required sections: {', '.join(missing_sections)}") → _(f"Missing required sections: {', '.join(missing_sections)}")
_("config_parse_error", f"Error parsing config: {str(e)}") → _(f"Error parsing config: {str(e)}")
```

`_apply_settings` 里的 logger 中文消息改为英文：
- `self.logger.debug(f"保存自定义配置路径: '{custom_path}'")` → `self.logger.debug(f"Saving custom config path: '{custom_path}'")`
- `self.logger.debug(f"成功保存自定义配置路径: '{custom_path}'")` → `self.logger.debug(f"Saved custom config path: '{custom_path}'")`
- `self.logger.warning(f"配置文件不存在: '{custom_path}'")` → `self.logger.warning(f"Config file does not exist: '{custom_path}'")`
- `self.logger.debug(f"已保存配置路径（文件不存在）: '{custom_path}'")` → `self.logger.debug(f"Saved config path (file does not exist): '{custom_path}'")`

- [ ] **Step 3: 改写 config_dialog.py 的 `_()` 双参（仅顶部对话框部分；页面在 Phase 2 整体重写）**

```python
_("config_dialog_title", "Configuration") → _("Configuration")
_("cat_battery", "Battery Config")        → _("Battery Config")
_("cat_test", "Test Config")              → _("Test Config")
_("cat_equipment", "Equipment")           → _("Equipment")
_("reset_defaults", "Reset Defaults")     → _("Reset Defaults")
_("save", "Save")                          → _("Save")
_("cancel", "Cancel")                      → _("Cancel")
_("confirm_reset", "Reset Defaults")       → _("Reset Defaults")
_("confirm_reset_msg", "Reset all configuration to default values? This cannot be undone.") → _("Reset all configuration to default values? This cannot be undone.")
_("error", "Error")                        → _("Error")
_("save_failed", "Failed to save configuration") → _("Failed to save configuration")
```

- [ ] **Step 4: 全库验证无残留双参调用**

Run: `grep -rn '_\s*("[^"]*"\s*,\s*"' src --include=*.py | grep -v '\.venv'`
Expected: 仅剩 `src/battery_analysis/main/ui/language_handler.py` 的 3 处（该文件在 Phase 3 删除，跳过）与 `menu_manager.py:261` 注释（Task 1.3 已删除）。若无其他输出即达标。

- [ ] **Step 5: 运行相关测试**

Run: `python -m pytest tests/battery_analysis/main/ui_components/test_ui_manager.py tests/battery_analysis/i18n/test_i18n.py -v`
Expected: 通过。

- [ ] **Step 6: 提交**

```bash
git add src/battery_analysis/main/ui_components/ui_manager.py src/battery_analysis/i18n/preferences_dialog.py src/battery_analysis/main/ui_components/config_dialog.py
git commit -m "refactor(i18n): normalize _() calls to English msgids (ui_manager, preferences, config dialog)"
```

---

### Task 1.6: 硬编码中文 → 英文（启动器 / 图表查看器 / 初始化步骤 / 其余日志）

**Files:**
- Modify: `src/battery_analysis/main/application_initializer.py`
- Modify: `src/battery_analysis/main/battery_chart_viewer.py`
- Modify: `src/battery_analysis/main/initialization/steps/language_initialization_step.py`
- Modify: 其余含中文日志的模块（按 Step 3 的 grep 结果逐个修）

- [ ] **Step 1: application_initializer.py 全部界面文案转英文**

把三处 `QMessageBox` 的窗口标题与正文替换：

```python
msg_box.setWindowTitle("应用程序错误")          → msg_box.setWindowTitle("Application Error")
error_msg = f"很抱歉，应用程序遇到了一个问题。\n\n错误信息: {str(value)}\n\n"
error_msg += "详细信息已记录到日志文件中。"
if report_path:
    error_msg += f"\n\n崩溃报告已生成: {report_path}"
error_msg += "\n\n建议您重新启动应用程序。"
    →  error_msg = f"Sorry, the application encountered a problem.\n\nError: {str(value)}\n\n"
        error_msg += "Details have been logged to the log file."
        if report_path:
            error_msg += f"\n\nCrash report generated: {report_path}"
        error_msg += "\n\nIt is recommended that you restart the application."
```

`_handle_qt_exception`（`_setup_qt_message_handler` 调用，第二处）：

```python
msg_box.setWindowTitle("应用程序错误")          → msg_box.setWindowTitle("Application Error")
error_msg = f"很抱歉，应用程序遇到了一个问题。\n\n错误信息: {str(e)}\n\n"
error_msg += "详细信息已记录到日志文件中。\n\n"
error_msg += "建议您重新启动应用程序。"
    →  error_msg = f"Sorry, the application encountered a problem.\n\nError: {str(e)}\n\n"
        error_msg += "Details have been logged to the log file.\n\n"
        error_msg += "It is recommended that you restart the application."
```

`_show_startup_error_dialog`（第三处）：

```python
msg_box.setWindowTitle("应用程序启动失败")      → msg_box.setWindowTitle("Application Failed to Start")
error_msg = f"很抱歉，应用程序无法启动。\n\n错误信息: {str(e)}\n\n"
error_msg += "详细信息已记录到日志文件中。\n\n"
error_msg += "建议您重新启动应用程序。"
    →  error_msg = f"Sorry, the application could not start.\n\nError: {str(e)}\n\n"
        error_msg += "Details have been logged to the log file.\n\n"
        error_msg += "It is recommended that you restart the application."
```

日志与 print 中文全部转英文（逐条）：
- `logger.critical("系统崩溃 - 未捕获的异常:", ...)` → `logger.critical("System crash - uncaught exception:", ...)`
- `logger.critical(f"崩溃报告已生成: {report_path}")` → `logger.critical(f"Crash report generated: {report_path}")`
- `logger.critical(f"生成崩溃报告失败: {e}")` → `logger.critical(f"Failed to generate crash report: {e}")`
- `logger.critical(f"显示错误对话框失败: {e}")` → `logger.critical(f"Failed to show error dialog: {e}")`
- `print(f"应用程序错误: {str(value)}")` → `print(f"Application error: {str(value)}")`
- `print("详细信息已记录到日志文件中。")` → `print("Details have been logged to the log file.")`
- `print(f"崩溃报告已生成: {report_path}")` → `print(f"Crash report generated: {report_path}")`
- `logger.critical("Qt事件循环中的未捕获异常:", ...)` → `logger.critical("Uncaught exception in Qt event loop:", ...)`
- `logger.critical(f"显示错误对话框失败: {dialog_error}")` → `logger.critical(f"Failed to show error dialog: {dialog_error}")`
- `logger.critical(f"显示启动错误对话框失败: {dialog_error}")` → `logger.critical(f"Failed to show startup error dialog: {dialog_error}")`
- `print(f"应用程序启动失败: {str(e)}")` → `print(f"Application failed to start: {str(e)}")`
- `print("详细信息已记录到日志文件中。")` → `print("Details have been logged to the log file.")`
- `logger.critical("应用程序初始化失败:", ...)` → `logger.critical("Application initialization failed:", ...)`
- `logger.critical("应用程序事件循环中发生未捕获异常:", ...)` → `logger.critical("Uncaught exception in application event loop:", ...)`

Qt 消息处理器里的中文（`Qt关键错误`/`Qt警告`/`Qt信息`/`Qt调试`）也转英文（它们走 logger）：

```python
logger.critical("Qt关键错误: %s (文件: %s, 行: %d)", ...)  → logger.critical("Qt critical error: %s (file: %s, line: %d)", ...)
logger.warning("Qt警告: %s (文件: %s, 行: %d)", ...)       → logger.warning("Qt warning: %s (file: %s, line: %d)", ...)
logger.debug("Qt信息: %s (文件: %s, 行: %d)", ...)          → logger.debug("Qt info: %s (file: %s, line: %d)", ...)
logger.debug("Qt调试: %s (文件: %s, 行: %d)", ...)          → logger.debug("Qt debug: %s (file: %s, line: %d)", ...)
```

- [ ] **Step 2: battery_chart_viewer.py 数据更新提示与日志转英文**

替换 189–212 行的中文：

```python
logger.info("检测到数据更新: 上次加载时间 %s, 当前文件时间 %s", ...)  → logger.info("Data update detected: last load %s, current file %s", ...)
reply = QMessageBox.question(None, "数据更新", "检测到分析结果已更新，是否重新加载最新版的图形？", Yes|No, Yes)
    → reply = QMessageBox.question(None, "Data Updated", "The analysis results have been updated. Reload the latest charts?", Yes|No, Yes)
logger.info("用户选择重新加载最新数据")      → logger.info("User chose to reload the latest data")
logger.error("重新加载数据失败")            → logger.error("Failed to reload data")
logger.info("重新加载数据成功")             → logger.info("Data reloaded successfully")
logger.info("用户选择保持原有数据显示")      → logger.info("User chose to keep the current display")
logger.warning("显示更新提示框时出错: %s", msg_error)  → logger.warning("Error showing update prompt: %s", msg_error)
logger.warning("检测数据更新时出错: %s", check_error)   → logger.warning("Error checking for data update: %s", check_error)
```

- [ ] **Step 3: 扫描全库其余运行时中文日志**

Run: `grep -rnP 'logger\.\w+\([^)]*[\x{4e00}-\x{9fff}]' src --include=*.py | grep -v '\.venv'`
以及 `grep -rnP '(print|statusBar|setWindowTitle|QMessageBox|QLabel)\([^)]*[\x{4e00}-\x{9fff}]' src --include=*.py | grep -v '\.venv'`

逐条把匹配到的**运行时字符串**（logger/print/消息框/状态栏，不含 docstring 与注释）翻译为英文。已知命中点：
- `src/battery_analysis/main/initialization/steps/language_initialization_step.py:42` — `self.logger.info("语言初始化完成")` → `"Language initialization complete"`；`:45` `self.logger.exception("语言初始化失败")` → `"Language initialization failed"`。
- `src/battery_analysis/main/services/config_service.py` — 全文 logger 中文（如 `"配置已保存到: %s"`、`"无法保存配置：未指定配置路径或配置未加载"`、`"首次运行，已创建默认配置文件: %s"`、`"配置警告: %s"`、`"配置 schema 验证失败（不影响运行）: %s"`、`"配置已迁移至 v%d"`、`"配置已加载: %s"`、`"配置文件加载失败: %s"`、`"加载配置 I/O 错误: %s"`、`"获取配置值失败: %s"` 等）→ 对应英文。
- `src/battery_analysis/main/ui_components/dialog_manager.py` 其余 logger 中文。
- 其余 grep 命中的模块。
- `src/battery_analysis/main/business_logic/validation_manager.py` 的 `validate_required_fields` 中拼接进状态消息的字段名中文（"样品数量"、"标称容量"、"计算容量"、"可用容量"）——属运行时字符串，同样转英文。
- `src/battery_analysis/main/ui_components/ui_manager.py:502` 陈旧 sentinel `("状态:就绪", "Ready")` → 改为 `("Ready", "就绪")`（Task 1.7 重建后 `"状态:就绪"` 已无生产者，且 zh_CN 译文为 `"就绪"`；此处是语言切换重译的匹配用字面量）。
- Task 1.5 质量审查确认：`ui_manager.py:292` 的 `"Not provided"` 与 `ui_manager.py:65` 的 `"status:ok"` 是**内部 sentinel**（与 visualizer_controller.py:151 / analysis_runner.py:165 比对），visualizer_controller 将在 Phase 3 删除——**决定：保持硬编码英文，不改**（避免破坏比对）。

> 注意：docstring 与注释保持中文不改（spec 明确排除）。

- [ ] **Step 3.5: 全库扫描单引号双参 `_()` 调用并规范化**

Task 1.3/1.4/1.5 的映射表只覆盖了双引号调用。单引号形态 `_('key', '中文fallback')` 同理会把 key 当 context 显示原始 key，必须一并清理。已知 4 处（`validation_manager.py:46,63,108`，其中 108 行附近有 2 处）：

Run: `grep -rn "_\s*('[^']*'\s*,\s*'" src --include=*.py | grep -v '\.venv'`

对每条命中按语义改英文 msgid。已知映射（validation_manager.py）：

```python
_('warning', '警告')                        → _('Warning')
_('version_format_invalid', '版本号格式不正确，应为 x.y.z 格式') → _('Version format is invalid. Expected x.y.z format')
_('input_path_not_exists', '输入路径不存在') → _('Input path does not exist')
_('required_fields_empty', '以下必填字段为空') → _('The following required fields are empty')
```

扫描后重新运行 grep 确认无输出。

- [ ] **Step 4: 运行测试**

Run: `python -m pytest tests/battery_analysis/main/test_main_window.py tests/battery_analysis/main/services/test_config_service.py -v`
Expected: 通过。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/main/application_initializer.py src/battery_analysis/main/battery_chart_viewer.py src/battery_analysis/main/initialization/steps/language_initialization_step.py src/battery_analysis/main/services/config_service.py
git add -u src  # 提交其余日志翻译改动（若 Step 3 改了其他文件）
git commit -m "i18n: translate hardcoded Chinese UI text and log messages to English"
```

---

### Task 1.7: 重建 en/zh_CN .po

**Files:**
- Create: `scripts/rebuild_po.py`
- Modify: `locale/en/LC_MESSAGES/messages.po`（重写）
- Modify: `locale/zh_CN/LC_MESSAGES/messages.po`（重写）

**目标**：en.po 为 identity（msgstr = msgid）；zh_CN.po 为英文 msgid → 中文译文，来源 = 既有 zh_CN.po 保留 + 下述 `CHINESE` 字典。

- [ ] **Step 0: 规范化单引号 `_()` 调用（Task 1.4 遗留）**

Task 1.4 将 `dialog_manager.py` 与 `help_manager.py` 的单引号双参调用改成了**单引号单参** `_('...')`，但 `MSGID_RE` 只匹配双引号，这些 msgid 无法被提取进目录。将 3 处改为双引号，并补入下方 `CHINESE` 字典：

- `src/battery_analysis/main/ui_components/dialog_manager.py:98` `_('Failed to show preferences dialog')` → `_("Failed to show preferences dialog")`
- `src/battery_analysis/main/ui_components/dialog_manager.py:154` `_('Cannot open user manual')` → `_("Cannot open user manual")`
- `src/battery_analysis/main/business_logic/help_manager.py:79` `_('Cannot open user manual')` → `_("Cannot open user manual")`

新增 CHINESE 条目（已列于下方字典）：
- `"Failed to show preferences dialog": "显示首选项对话框失败"`
- `"Cannot open user manual": "无法打开用户手册"`

Run: `grep -rn "_\s*('[^']*')" src --include=*.py`
Expected: 无输出（所有 `_()` 调用均为双引号单参）。

- [ ] **Step 1: 创建 `scripts/rebuild_po.py`**

```python
"""Rebuild en/zh_CN .po catalogs from source _() msgids + Chinese dict.

Usage:  python scripts/rebuild_po.py
Prereq: 源码中不得残留双参 _("key", "fallback") 调用（Task 1.3-1.5 已清理）。
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
LOCALE_DIR = ROOT / "locale"

# msgid(英文) -> 中文译文
CHINESE = {
    # ——— 来自双参 _() 的 fallback（fallback 为中文的取原值；为英文的取新译）———
    "New Project": "新建项目",
    "Open Project": "打开项目",
    "Save Settings": "保存设置",
    "Save As": "另存为",
    "Exit": "退出应用",
    "Undo": "撤销操作",
    "Redo": "重做操作",
    "Cut": "剪切选中内容",
    "Copy": "复制选中内容",
    "Paste": "粘贴内容",
    "Zoom In": "放大界面",
    "Zoom Out": "缩小界面",
    "Reset Zoom": "重置界面缩放",
    "Show/Hide Toolbar": "显示/隐藏工具栏",
    "Show/Hide Status Bar": "显示/隐藏状态栏",
    "Calculate Battery Parameters": "计算电池参数",
    "Analyze Data": "分析数据",
    "Generate Report": "生成报告",
    "Open Battery Chart Viewer": "打开电池图表查看器",
    "Batch Process Data": "批量处理数据",
    "Manage Data Dictionary": "配置管理系统数据字典",
    "Preferences": "首选项",
    "Open User Manual": "打开用户手册",
    "Open Online Help": "打开在线帮助",
    "About": "关于应用",
    "Export Report": "导出报告",
    "Ready": "就绪",
    "Use System Default Theme": "使用系统默认主题",
    "Use Windows 11 Style Theme": "使用Windows 11风格主题",
    "Use Windows Vista Style Theme": "使用Windows Vista风格主题",
    "Use Cross-platform Fusion Theme": "使用跨平台Fusion主题",
    "Use Dark Theme for Night Use": "使用深色主题，适合夜间使用",
    "Confirm Exit": "确认退出",
    "Are you sure you want to exit the application?": "确定要退出应用程序吗？",
    "About Battery Analyzer": "关于电池分析器",
    "Error": "错误",
    "Warning": "警告",
    "Data Load Error - Recovery Options": "数据加载错误 - 恢复选项",
    "Unable to load battery data. Choose how to continue:": "无法加载电池数据，请选择如何继续:",
    "Choose one of the following recovery options:": "请选择以下恢复选项之一:",
    "Reselect Data Directory": "重新选择数据目录",
    "Restart with Default Configuration": "使用默认配置重新启动",
    "Cancel Operation": "取消操作",
    "OK": "确定",
    "Cancel": "取消",
    "Opening data directory selector...": "正在打开数据目录选择...",
    "Restarting with default configuration...": "使用默认配置重新启动...",
    "Restart": "重新启动",
    "The application will restart with the default configuration.\n\nPlease make sure you have valid data files available.": "应用将使用默认配置重新启动。\n\n请确保您有有效的数据文件可用。",
    "Operation canceled": "操作已取消",
    "Canceled": "取消",
    "Operation canceled. You can retry via the 'File -> Open Data' menu.": "操作已取消。您可以通过菜单 'File -> Open Data' 重新尝试。",
    "[Error]: Input path has no data": "[Error]: 输入路径没有数据",
    "Please set the input path first.": "请先设置输入路径。",
    "Analyzing data...": "分析数据...",
    "Analysis Result": "分析结果",
    "Battery Analysis Progress": "电池分析进度",
    "Ready to start analysis...": "准备开始分析...",
    "Task canceled...": "任务已取消...",
    "No Excel files found.": "没有找到Excel文件。",
    "Data analysis failed: {}": "数据分析失败: {}",
    "Failed to open online help.": "无法打开在线帮助。",
    "App icon not found; using default icon.": "未找到应用图标文件，使用默认图标",
    "Input Validation Failed": "输入验证失败",
    "Input data path cannot be empty": "输入数据路径不能为空",
    "Output path cannot be empty": "输出路径不能为空",
    "Start Failed": "启动失败",
    "Cannot start the analysis task": "无法启动分析任务",
    "Test Config": "测试配置",
    "Battery Config": "电池配置",
    "Select Test Profile": "选择测试文件",
    "Select Input Path": "选择输入路径",
    "Select Output Path": "选择输出路径",
    "Run Analysis": "运行分析",
    "Test Information Table": "测试信息表格",
    # ——— Preferences 各项（原 fallback 为英文，补充中文）———
    "General Settings": "常规设置",
    "Auto-save settings": "自动保存设置",
    "Automatically save settings when changes are made": "更改时自动保存设置",
    "Confirm before exiting": "退出前确认",
    "Show confirmation dialog when exiting the application": "退出应用程序时显示确认对话框",
    "Display Settings": "显示设置",
    "Theme:": "主题:",
    "Light": "浅色",
    "Dark": "深色",
    "System": "跟随系统",
    "Font Size:": "字体大小:",
    "General": "常规",
    "Language Settings": "语言设置",
    "Current Language:": "当前语言:",
    "Select Language:": "选择语言:",
    "Apply Language": "应用语言",
    "Translation Status": "翻译状态",
    "Translation information will be displayed here.": "翻译信息将显示在这里。",
    "Language": "语言",
    "Configuration File Settings": "配置文件设置",
    "Current Config Path:": "当前配置路径:",
    "Not loaded": "未加载",
    "Custom Config Path:": "自定义配置路径:",
    "Enter custom configuration file path...": "输入自定义配置文件路径...",
    "Browse...": "浏览...",
    "Validate Configuration": "校验配置",
    "Required Sections in Config File": "配置文件必需部分",
    "Reset to Default": "重置为默认",
    "Config": "配置",
    "Select Configuration File": "选择配置文件",
    "Please enter a configuration file path": "请输入配置文件路径",
    "File does not exist": "文件不存在",
    "JSON root must be an object": "JSON 根必须是对象",
    "Configuration file is valid!": "配置文件有效！",
    "INI format is deprecated; consider migrating to config.json": "INI 格式已弃用，建议迁移到 config.json",
    "Apply": "应用",
    "Using default paths": "使用默认路径",
    "Failed to change language": "切换语言失败",
    "Language change error": "切换语言错误",
    "Settings apply error": "设置应用错误",
    "Failed to save configuration": "保存配置失败",
    "Failed to show preferences dialog": "显示首选项对话框失败",
    "Cannot open user manual": "无法打开用户手册",
    # ——— ui_manager 无障碍名称/描述与 tooltip（Task 1.5 引入）———
    "Start battery analysis": "开始电池分析",
    "Select battery type": "选择电池类型",
    "Select battery construction method": "选择电池构造方法",
    "Select battery specification type": "选择电池规格类型",
    "Select battery specification method": "选择电池规格方法",
    "Select battery manufacturer": "选择电池制造商",
    "Enter battery batch date code": "输入电池批次日期代码",
    "Enter number of samples": "输入样品数量",
    "Enter freezing temperature value": "输入冷冻温度值",
    "Enter datasheet nominal capacity": "输入数据手册中的标称容量",
    "Enter calculated nominal capacity": "输入计算得出的标称容量",
    "Enter accelerated aging days": "输入加速老化天数",
    "Enter required usable capacity": "输入所需可用容量",
    "Enter version number": "输入版本号",
    "Select tester location": "选择测试地点",
    "Select tested-by": "选择测试人员",
    "Select reported-by": "选择报告人员",
    "Test profile file path": "测试配置文件路径",
    "Select test profile file": "选择测试配置文件",
    "Input data file path": "输入数据文件路径",
    "Select input data file path": "选择输入数据文件路径",
    "Output result file path": "输出结果文件路径",
    "Select output result file path": "选择输出结果文件路径",
    "Settings related to the test configuration": "包含测试相关配置的设置",
    "Settings related to the battery configuration": "包含电池相关配置的设置",
    "Select battery test profile file": "选择电池测试配置文件",
    "Select analysis output path": "选择分析结果输出路径",
    "Table containing test equipment and software version information": "包含测试设备和软件版本信息的表格",
    "Test config group - settings related to the test configuration": "测试配置组 - 包含测试相关配置的设置",
    "Battery config group - settings related to the battery configuration": "电池配置组 - 包含电池相关配置的设置",
    "Test information table - contains test equipment and software version information": "测试信息表格 - 包含测试设备和软件版本信息",
    "✓ Translation is complete": "✓ 翻译完整",
    "⚠ Some translations are missing": "⚠ 部分翻译缺失",
    # ——— Config 对话框分类（Phase 2 使用）———
    "Equipment": "设备",
    "Reset Defaults": "恢复默认",
    "Save": "保存",
    "Reset all configuration to default values? This cannot be undone.": "将所有配置恢复为默认值？此操作不可撤销。",
    "Configuration": "配置",
    "Battery": "电池",
    "Test": "测试",
    "Test Data Dictionary": "测试数据字典",
    "Test Parameters": "测试参数",
    "Battery Types": "电池类型",
    "Construction Methods": "构造方式",
    "Specification Methods": "规格方式",
    "Manufacturers": "制造商",
    "Rules": "规则",
    "Specifications": "规格型号",
    "Pulse Currents": "脉冲电流",
    "Cut-off Voltages": "截止电压",
    "Tested By": "测试人员",
}

MSGID_RE = re.compile(r'_\s*\(\s*"((?:[^"\\]|\\.)*)"')


def extract_msgids(src_dir: Path) -> "list[str]":
    msgids: "list[str]" = []
    for path in sorted(src_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for m in MSGID_RE.finditer(text):
            msgid = m.group(1).replace('\\"', '"').replace("\\\\", "\\")
            if msgid and msgid not in msgids:
                msgids.append(msgid)
    return msgids


def parse_po(path: Path) -> dict:
    if not path.exists():
        return {}
    entries = {}
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n{2,}", text)
    for block in blocks:
        m = re.search(r'^msgid\s+"((?:[^"\\]|\\.)*)"\s*$', block, re.MULTILINE)
        s = re.search(r'^msgstr\s+"((?:[^"\\]|\\.)*)"\s*$', block, re.MULTILINE)
        if m and s:
            msgid = m.group(1).replace('\\"', '"').replace("\\\\", "\\")
            msgstr = s.group(1).replace('\\"', '"').replace("\\\\", "\\")
            if msgid:
                entries[msgid] = msgstr
    return entries


def _po_quote(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def render_po(lang: str, entries: list) -> str:
    lines = [
        f'# {lang} translations for Battery Analysis application',
        f'# Language: {lang}',
        'msgid ""',
        'msgstr ""',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"',
        "",
    ]
    for msgid, msgstr in entries:
        lines.append(f'msgid "{_po_quote(msgid)}"')
        lines.append(f'msgstr "{_po_quote(msgstr)}"')
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    msgids = extract_msgids(SRC_DIR)
    existing_zh = parse_po(LOCALE_DIR / "zh_CN" / "LC_MESSAGES" / "messages.po")

    en_entries = [(m, m) for m in msgids]
    zh_entries = []
    for m in msgids:
        zh_entries.append((m, CHINESE.get(m, existing_zh.get(m, m))))

    (LOCALE_DIR / "en" / "LC_MESSAGES" / "messages.po").write_text(
        render_po("en", en_entries), encoding="utf-8")
    (LOCALE_DIR / "zh_CN" / "LC_MESSAGES" / "messages.po").write_text(
        render_po("zh_CN", zh_entries), encoding="utf-8")
    print(f"Rebuilt en.po ({len(msgids)} entries) and zh_CN.po ({len(msgids)} entries)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 运行脚本并校验**

Run: `python scripts/rebuild_po.py`
Expected: 输出 `Rebuilt en.po (N entries) and zh_CN.po (N entries)`。

Run: `grep -c '^msgid' locale/en/LC_MESSAGES/messages.po`
Expected: N（与脚本输出一致），且 `.po` 中不得出现旧 key 形态的 msgid（如 `tooltip_new`、`window_title`）。

- [ ] **Step 3: 运行 i18n 测试**

Run: `python -m pytest tests/battery_analysis/i18n/test_i18n.py -v`
Expected: 全部通过。

- [ ] **Step 4: 提交**

```bash
git add scripts/rebuild_po.py locale/en/LC_MESSAGES/messages.po locale/zh_CN/LC_MESSAGES/messages.po
git commit -m "i18n: rebuild en (identity) and zh_CN catalogs from English msgids"
```

---

### Phase 1 检查点

Run: `python -m pytest tests/ -q 2>&1 | tail -20`
Expected: 全绿（或仅已知失败项，记录并继续）。

Run: `grep -rnP '[\x{4e00}-\x{9fff}]' src --include=*.py | grep -vP '^\s*#|"""|#[ ]*$' | grep -vP '(# .*|:.*"""|:.*docstring)'`
Expected: 剩余命中仅为 docstring/注释/中文注释行；运行时字符串已无中文。若仍有运行时中文，按 Task 1.6 Step 3 补齐。

---

## Phase 2 — 设置/配置（Settings Polish）

### Task 2.1: 新增 `battery_classifier` 分类工具（TDD）

**Files:**
- Create: `src/battery_analysis/utils/battery_classifier.py`
- Create: `tests/battery_analysis/utils/test_battery_classifier.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/battery_analysis/utils/test_battery_classifier.py`：

```python
"""测试电池分类工具"""

import pytest
from battery_analysis.utils.battery_classifier import (
    classify_spec,
    extract_spec_name,
    extract_capacity,
    derive_specifications,
    DEFAULT_CAPACITY_THRESHOLD,
)


class TestClassifySpec:
    def test_cr_prefix_is_coin_cell(self):
        assert classify_spec("CR2450", 600) == "Coin Cell"

    def test_cr_without_capacity_is_coin_cell(self):
        assert classify_spec("CR2450") == "Coin Cell"

    def test_cp_prefix_is_pouch_cell(self):
        assert classify_spec("CP224642A", 920) == "Pouch Cell"

    def test_cf_prefix_is_pouch_cell(self):
        assert classify_spec("CF583083", 4000) == "Pouch Cell"

    def test_lower_case_input(self):
        assert classify_spec("cr2450", 600) == "Coin Cell"
        assert classify_spec("cp305050", 2000) == "Pouch Cell"

    def test_fallback_by_capacity_above_threshold(self):
        name = "XYZ9999"
        assert classify_spec(name, DEFAULT_CAPACITY_THRESHOLD + 1) == "Pouch Cell"

    def test_fallback_by_capacity_below_threshold(self):
        name = "XYZ100"
        assert classify_spec(name, DEFAULT_CAPACITY_THRESHOLD - 1) == "Coin Cell"

    def test_fallback_zero_capacity_coin(self):
        assert classify_spec("UNKNOWN", 0) == "Coin Cell"


class TestExtractSpecName:
    def test_first_part_of_rule(self):
        assert extract_spec_name("CR2450/1S1P/600/550/380/1.0") == "CR2450"

    def test_empty_string(self):
        assert extract_spec_name("") == ""

    def test_single_part(self):
        assert extract_spec_name("CR2450") == "CR2450"


class TestExtractCapacity:
    def test_third_part_of_rule(self):
        assert extract_capacity("CR2450/1S1P/600/550/380/1.0") == 600

    def test_not_a_number(self):
        assert extract_capacity("CR2450/1S1P/abc/550/380/1.0") == 0

    def test_too_few_parts(self):
        assert extract_capacity("CR2450/1S1P") == 0


class TestDeriveSpecifications:
    def test_mixed_rules(self):
        rules = [
            "CR2450/1S1P/600/550/380/1.0",
            "CR2450D/1S1P/600/550/280/1.0",
            "CP224642A/1S1P/920/920/80%/5.0",
            "CF583083/1S1P/4000/4000/80%/5.0",
            "CP305050/1S1P/2000/2000/80%/1.0",
        ]
        result = derive_specifications(rules)
        assert "CR2450" in result["Coin Cell"]
        assert "CR2450D" in result["Coin Cell"]
        assert "CP224642A" in result["Pouch Cell"]
        assert "CF583083" in result["Pouch Cell"]
        assert "CP305050" in result["Pouch Cell"]

    def test_duplicate_specs_are_deduplicated(self):
        rules = [
            "CR2450/1S1P/600/550/380/1.0",
            "CR2450/1S2P/600/550/380/1.0",
        ]
        result = derive_specifications(rules)
        assert result["Coin Cell"].count("CR2450") == 1

    def test_empty_rules(self):
        assert derive_specifications([]) == {"Coin Cell": [], "Pouch Cell": []}
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/battery_analysis/utils/test_battery_classifier.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: 创建实现**

创建 `src/battery_analysis/utils/battery_classifier.py`：

```python
"""电池型号分类工具——根据型号名和容量判断电池类型"""

DEFAULT_CAPACITY_THRESHOLD = 800  # mAh，低于此值为 Coin Cell


def classify_spec(model_name: str, capacity: int = 0) -> str:
    """根据规格型号名和容量判定电池类型

    判定规则：
    1. CR 开头 → Coin Cell
    2. CP 或 CF 开头 → Pouch Cell
    3. 兜底：容量 >= threshold → Pouch Cell，否则 Coin Cell
    """
    upper = model_name.strip().upper()
    if upper.startswith("CR"):
        return "Coin Cell"
    if upper.startswith(("CP", "CF")):
        return "Pouch Cell"
    return "Pouch Cell" if capacity >= DEFAULT_CAPACITY_THRESHOLD else "Coin Cell"


def extract_spec_name(rule: str) -> str:
    """从规则字符串中提取规格型号名（rule 分段第 0 段）"""
    parts = rule.split("/")
    return parts[0].strip() if parts else ""


def extract_capacity(rule: str) -> int:
    """从规则字符串中提取容量（rule 分段第 2 段）"""
    parts = rule.split("/")
    if len(parts) >= 3:
        try:
            return int(parts[2])
        except ValueError:
            return 0
    return 0


def derive_specifications(rules: list) -> dict:
    """从 rules 列表自动派生 specifications 字典

    返回: {"Coin Cell": [...], "Pouch Cell": [...]}，去重、保持首次出现顺序
    """
    specs: dict = {"Coin Cell": [], "Pouch Cell": []}
    seen: set = set()
    for rule in rules:
        spec_name = extract_spec_name(rule)
        if not spec_name or spec_name in seen:
            continue
        seen.add(spec_name)
        capacity = extract_capacity(rule)
        cell_type = classify_spec(spec_name, capacity)
        specs[cell_type].append(spec_name)
    return specs
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/battery_analysis/utils/test_battery_classifier.py -v`
Expected: 全部通过。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/utils/battery_classifier.py tests/battery_analysis/utils/test_battery_classifier.py
git commit -m "feat: add battery classifier utility for spec-to-type deduction"
```

---

### Task 2.2: `PreferencesDialog` 迁出 i18n 包 + 合并 `IConfigPathProvider` + 删除 auto-save

**Files:**
- Move: `src/battery_analysis/i18n/preferences_dialog.py` → `src/battery_analysis/main/ui_components/preferences_dialog.py`
- Modify: `src/battery_analysis/main/ui_components/config_path_provider.py`
- Delete: `src/battery_analysis/i18n/config_dialog_interface.py`
- Modify: `src/battery_analysis/main/ui_components/dialog_manager.py`（import）
- Modify: `tests/battery_analysis/i18n/test_i18n.py`（`TestIConfigPathProvider` import）

- [ ] **Step 1: git mv 并改导入**

Run: `git mv src/battery_analysis/i18n/preferences_dialog.py src/battery_analysis/main/ui_components/preferences_dialog.py`

在新文件 `preferences_dialog.py` 顶部，把：

```python
from . import _, get_available_locales, set_locale, get_current_locale
from .config_dialog_interface import IConfigPathProvider
from .language_manager import get_language_manager
```

改为：

```python
from battery_analysis.i18n import _, get_available_locales, set_locale, get_current_locale
from battery_analysis.i18n.language_manager import get_language_manager
from battery_analysis.main.ui_components.config_path_provider import IConfigPathProvider
```

- [ ] **Step 2: 合并 IConfigPathProvider 进 config_path_provider.py**

把 `src/battery_analysis/i18n/config_dialog_interface.py` 的接口类移入 `src/battery_analysis/main/ui_components/config_path_provider.py` 顶部：

```python
"""配置路径提供者——main 层对 IConfigPathProvider 的实现

接口定义随 Preferences 对话框一同迁出 i18n 包，消除 i18n 对 main 的依赖反转接口。
"""

from abc import ABC, abstractmethod


class IConfigPathProvider(ABC):
    """配置路径提供者接口——由 main 层实现，注入到首选项对话框中使用"""

    @abstractmethod
    def get_config_path(self) -> str:
        """返回当前配置文件路径，不可用时返回空字符串"""
        ...
```

删除原 `from battery_analysis.i18n.config_dialog_interface import IConfigPathProvider` 这一行。

- [ ] **Step 3: 删除 config_dialog_interface.py**

Run: `git rm src/battery_analysis/i18n/config_dialog_interface.py`

- [ ] **Step 4: 更新 dialog_manager.py 导入**

```python
from battery_analysis.i18n.preferences_dialog import PreferencesDialog
```
改为：
```python
from battery_analysis.main.ui_components.preferences_dialog import PreferencesDialog
```

- [ ] **Step 5: 删除 auto-save 选项**

在 `_setup_ui` 的 `_create_general_tab` 中，删除 auto-save 相关的两段（checkbox 与 tooltip）：

```python
        # Auto-save option
        self.auto_save_checkbox = QW.QCheckBox(_("Auto-save settings"))
        self.auto_save_checkbox.setToolTip(_("Automatically save settings when changes are made"))
        general_group_layout.addWidget(self.auto_save_checkbox)
```

同步删除：
- `__init__` 里 `self.auto_save_checkbox = None`
- `_load_settings` 里 `self.auto_save_checkbox.setChecked(settings.value("general/auto_save", True, type=bool))`
- `_apply_settings` 里 `settings.setValue("general/auto_save", self.auto_save_checkbox.isChecked())`

- [ ] **Step 6: 更新 test_i18n.py 的接口测试导入**

把 `TestIConfigPathProvider` 中的三处：

```python
from battery_analysis.i18n.config_dialog_interface import IConfigPathProvider
```
改为：
```python
from battery_analysis.main.ui_components.config_path_provider import IConfigPathProvider
```

并把类 docstring 中的 `config_dialog_interface.IConfigPathProvider` 更新为 `config_path_provider.IConfigPathProvider`。

- [ ] **Step 7: 运行测试**

Run: `python -m pytest tests/battery_analysis/i18n/test_i18n.py tests/battery_analysis/main/ui_components/test_dialog_manager.py -v`
Expected: 全部通过。

- [ ] **Step 8: 提交**

```bash
git add -A src/battery_analysis/i18n src/battery_analysis/main/ui_components tests/battery_analysis/i18n/test_i18n.py
git commit -m "refactor: move PreferencesDialog out of i18n, merge IConfigPathProvider, drop auto-save"
```

---

### Task 2.3: 重写 `ConfigDialog` —— master-detail + 逐条化 + Rules 表格 + 派生只读 Specifications

**Files:**
- Modify: `src/battery_analysis/main/ui_components/config_dialog.py`（整体重写）
- Modify: `src/battery_analysis/utils/config_defaults.py`

- [ ] **Step 1: 整体重写 config_dialog.py**

用以下内容**完整替换** `src/battery_analysis/main/ui_components/config_dialog.py`：

```python
"""
配置管理对话框
提供左侧分类导航、右侧编辑器的 master-detail UI，用于管理应用的数据字典配置。
"""

import copy
import logging
from typing import Dict

from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC

from battery_analysis.i18n.language_manager import _
from battery_analysis.utils.battery_classifier import derive_specifications
from battery_analysis.utils.config_defaults import DEFAULT_CONFIG

RULE_COLUMNS = [
    "Specification", "Spec Method", "Datasheet Capacity",
    "Calculation Capacity", "Required Useable Capacity", "Coefficient",
]


class ConfigDialog(QW.QDialog):
    """配置管理主对话框（master-detail 布局）"""

    _CATEGORIES = ["Battery", "Test", "Equipment"]

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._config_service = main_window._get_service("config")
        if self._config_service is None:
            raise RuntimeError("ConfigService not available — cannot open Configuration dialog")

        # 从 ConfigService 加载当前数据（深拷贝，取消保存才写回）
        raw_data = self._config_service.get_config_value("")
        self._working_data = copy.deepcopy(raw_data) if isinstance(raw_data, dict) else {}

        self.setWindowTitle(_("Configuration"))
        self.setMinimumSize(760, 560)
        self._setup_ui()
        self._populate_data()

    def _setup_ui(self):
        layout = QW.QVBoxLayout(self)

        # 左导航 + 右堆叠（master-detail）
        splitter = QW.QSplitter(QC.Qt.Orientation.Horizontal)
        self._nav = QW.QListWidget()
        self._nav.setFixedWidth(150)
        for name in self._CATEGORIES:
            QW.QListWidgetItem(_(name), self._nav)
        self._nav.setCurrentRow(0)

        self._stack = QW.QStackedWidget()
        self._page_battery = _BatteryConfigPage(self)
        self._page_test = _TestConfigPage(self)
        self._page_equipment = _EquipmentPage(self)
        self._stack.addWidget(self._page_battery)
        self._stack.addWidget(self._page_test)
        self._stack.addWidget(self._page_equipment)
        self._nav.currentRowChanged.connect(self._stack.setCurrentIndex)

        splitter.addWidget(self._nav)
        splitter.addWidget(self._stack)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, 1)

        # 底部按钮栏
        btn_layout = QW.QHBoxLayout()
        btn_reset = QW.QPushButton(_("Reset Defaults"))
        btn_reset.clicked.connect(self._on_reset_defaults)
        btn_save = QW.QPushButton(_("Save"))
        btn_save.clicked.connect(self._on_save)
        btn_cancel = QW.QPushButton(_("Cancel"))
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _on_reset_defaults(self):
        reply = QW.QMessageBox.question(
            self, _("Reset Defaults"),
            _("Reset all configuration to default values? This cannot be undone."),
            QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
        )
        if reply == QW.QMessageBox.StandardButton.Yes:
            self._working_data = copy.deepcopy(DEFAULT_CONFIG)
            self._populate_data()

    def _on_save(self):
        try:
            self._page_battery.collect_data()
            self._page_test.collect_data()
            self._page_equipment.collect_data()
            self._config_service.replace_all_config(self._working_data)
            self._config_service.save_config()
            self.accept()
        except Exception as e:
            self.logger.error("Failed to save configuration: %s", e)
            QW.QMessageBox.critical(
                self, _("Error"),
                f"{_('Failed to save configuration')}: {e}"
            )

    def _populate_data(self):
        wd = self._working_data if isinstance(self._working_data, dict) else {}
        self._page_battery.load_data(wd.get("battery", {}))
        self._page_test.load_data(wd.get("test", {}))
        self._page_equipment.load_data(wd.get("test", {}).get("equipment", {}))


class _ListEditor(QW.QGroupBox):
    """可增删的行级列表编辑器（Manufacturers 等列表类配置使用）"""

    def __init__(self, title: str, editable: bool = True):
        super().__init__(title)
        vbox = QW.QVBoxLayout(self)
        self._lw = QW.QListWidget()
        self._lw.setAlternatingRowColors(True)
        self._lw.setMinimumHeight(110)
        if editable:
            self._lw.itemDoubleClicked.connect(lambda item: self._lw.editItem(item))
        vbox.addWidget(self._lw)
        if editable:
            btn_row = QW.QHBoxLayout()
            btn_add = QW.QPushButton("+")
            btn_add.setFixedSize(22, 22)
            btn_remove = QW.QPushButton("×")
            btn_remove.setFixedSize(22, 22)
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_remove)
            btn_row.addStretch()
            vbox.addLayout(btn_row)
            btn_add.clicked.connect(self._add_item)
            btn_remove.clicked.connect(self._remove_item)

    def _add_item(self):
        item = QW.QListWidgetItem("")
        item.setFlags(item.flags() | QC.Qt.ItemFlag.ItemIsEditable)
        self._lw.addItem(item)
        self._lw.editItem(item)

    def _remove_item(self):
        for item in self._lw.selectedItems():
            self._lw.takeItem(self._lw.row(item))

    def set_items(self, items) -> None:
        self._lw.clear()
        for value in items:
            item = QW.QListWidgetItem(str(value))
            item.setFlags(item.flags() | QC.Qt.ItemFlag.ItemIsEditable)
            self._lw.addItem(item)

    def items(self) -> list:
        return [self._lw.item(i).text().strip() for i in range(self._lw.count())
                if self._lw.item(i).text().strip()]


class _RulesEditor(QW.QGroupBox):
    """Rules 表格编辑器——每一行一条规则，6 列与 rule_parts[0..5] 对应"""

    def __init__(self, title: str = "Rules"):
        super().__init__(title)
        vbox = QW.QVBoxLayout(self)
        self._table = QW.QTableWidget(0, len(RULE_COLUMNS))
        self._table.setHorizontalHeaderLabels(RULE_COLUMNS)
        self._table.verticalHeader().hide()
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSelectionBehavior(QW.QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setMinimumHeight(150)
        vbox.addWidget(self._table)

        btn_row = QW.QHBoxLayout()
        btn_add = QW.QPushButton("+ Add Rule")
        btn_remove = QW.QPushButton("× Remove")
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_remove)
        btn_row.addStretch()
        vbox.addLayout(btn_row)
        btn_add.clicked.connect(self._add_row)
        btn_remove.clicked.connect(self._remove_rows)

    def _add_row(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        for col in range(len(RULE_COLUMNS)):
            self._table.setItem(row, col, QW.QTableWidgetItem(""))
        self._table.setCurrentCell(row, 0)
        self._table.editItem(self._table.item(row, 0))

    def _remove_rows(self):
        rows = sorted({idx.row() for idx in self._table.selectionModel().selectedRows()},
                      reverse=True)
        for row in rows:
            self._table.removeRow(row)

    def set_rules(self, rules: list) -> None:
        self._table.setRowCount(0)
        for rule in rules:
            parts = rule.split("/")
            row = self._table.rowCount()
            self._table.insertRow(row)
            for col in range(len(RULE_COLUMNS)):
                value = parts[col] if col < len(parts) else ""
                self._table.setItem(row, col, QW.QTableWidgetItem(value))

    def rules(self) -> list:
        result = []
        for row in range(self._table.rowCount()):
            parts = []
            for col in range(len(RULE_COLUMNS)):
                item = self._table.item(row, col)
                parts.append(item.text().strip() if item else "")
            if any(parts):
                result.append("/".join(parts))
        return result


class _BatteryConfigPage(QW.QWidget):
    """电池配置编辑页面（逐条化 + Specifications 派生只读）"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog

        main_layout = QW.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QW.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QW.QFrame.Shape.NoFrame)

        content = QW.QWidget()
        layout = QW.QVBoxLayout(content)

        # ── Test Data Dictionary ──
        dict_group = QW.QGroupBox(_("Test Data Dictionary"))
        dict_layout = QW.QVBoxLayout(dict_group)

        self._list_types = _ListEditor(_("Battery Types"), editable=False)
        dict_layout.addWidget(self._list_types)

        self._rules_editor = _RulesEditor(_("Rules"))
        dict_layout.addWidget(self._rules_editor)

        # Specifications（从 Rules 派生，只读展示，无增删按钮）
        self._spec_page = QW.QTabWidget()
        self._spec_coin = QW.QListWidget()
        self._spec_coin.setSelectionMode(QW.QAbstractItemView.SelectionMode.NoSelection)
        self._spec_pouch = QW.QListWidget()
        self._spec_pouch.setSelectionMode(QW.QAbstractItemView.SelectionMode.NoSelection)
        self._spec_page.addTab(self._spec_coin, "Coin Cell")
        self._spec_page.addTab(self._spec_pouch, "Pouch Cell")
        self._spec_page.setMinimumHeight(140)
        spec_group = QW.QGroupBox(_("Specifications"))
        spec_vbox = QW.QVBoxLayout(spec_group)
        spec_vbox.addWidget(self._spec_page)
        dict_layout.addWidget(spec_group)

        self._list_construction = _ListEditor(_("Construction Methods"))
        dict_layout.addWidget(self._list_construction)

        self._list_spec_method = _ListEditor(_("Specification Methods"))
        dict_layout.addWidget(self._list_spec_method)

        self._list_mfrs = _ListEditor(_("Manufacturers"))
        dict_layout.addWidget(self._list_mfrs)

        layout.addWidget(dict_group)

        # ── Test Parameters ──
        params_group = QW.QGroupBox(_("Test Parameters"))
        params_layout = QW.QVBoxLayout(params_group)

        self._list_pulse = _ListEditor(_("Pulse Currents"))
        params_layout.addWidget(self._list_pulse)

        self._list_voltage = _ListEditor(_("Cut-off Voltages"))
        params_layout.addWidget(self._list_voltage)

        layout.addWidget(params_group)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Rules 变更时自动刷新 Specifications
        model = self._rules_editor._table.model()
        model.rowsInserted.connect(self._on_rules_changed)
        model.rowsRemoved.connect(self._on_rules_changed)
        model.dataChanged.connect(self._on_rules_changed)

    def _on_rules_changed(self):
        self._refresh_specs_from_rules(self._rules_editor.rules())

    def _refresh_specs_from_rules(self, rules: list) -> None:
        self._spec_coin.clear()
        self._spec_pouch.clear()
        specs = derive_specifications(rules)
        for spec in specs.get("Coin Cell", []):
            self._spec_coin.addItem(spec)
        for spec in specs.get("Pouch Cell", []):
            self._spec_pouch.addItem(spec)

    def load_data(self, data: dict) -> None:
        rules = data.get("rules", [])
        self._list_types.set_items(data.get("types", []))
        self._list_construction.set_items(data.get("constructionMethods", []))
        self._rules_editor.set_rules(rules)
        self._refresh_specs_from_rules(rules)
        self._list_spec_method.set_items(data.get("specificationMethods", []))
        self._list_mfrs.set_items(data.get("manufacturers", []))
        self._list_pulse.set_items([str(v) for v in data.get("pulseCurrents", [])])
        self._list_voltage.set_items([str(v) for v in data.get("cutOffVoltages", [])])

    def collect_data(self) -> None:
        battery = self._dialog._working_data.setdefault("battery", {})
        battery["types"] = self._list_types.items()
        battery["constructionMethods"] = self._list_construction.items()
        rules = self._rules_editor.rules()
        battery["rules"] = rules
        # Specifications 从 Rules 自动派生，不直接读取 UI
        battery["specifications"] = derive_specifications(rules)
        battery["specificationMethods"] = self._list_spec_method.items()
        battery["manufacturers"] = self._list_mfrs.items()
        battery["pulseCurrents"] = self._parse_float_list(self._list_pulse.items())
        battery["cutOffVoltages"] = self._parse_float_list(self._list_voltage.items())

    @staticmethod
    def _parse_float_list(raw: list) -> list:
        result = []
        for v in raw:
            try:
                result.append(float(v))
            except ValueError:
                logging.getLogger(__name__).warning("Ignoring non-float value: %s", v)
        return result


class _TestConfigPage(QW.QWidget):
    """测试配置编辑页面"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog

        layout = QW.QVBoxLayout(self)
        self._list_tested_by = _ListEditor(_("Tested By"))
        layout.addWidget(self._list_tested_by)
        layout.addStretch()

    @staticmethod
    def _location_from_equipment(loc_key: str, test_equipment: str) -> str:
        parts = loc_key.split(".")
        if len(parts) != 2:
            return loc_key
        site, lab = parts
        prefix = "NEWARE Battery Testing System "
        model = test_equipment[len(prefix):].strip() if test_equipment.startswith(prefix) else test_equipment.strip()
        lab_display = lab + "." if lab == "Qual" else lab
        return f"{model} ({lab_display}), {site}"

    def load_data(self, data: dict) -> None:
        # Tester locations 从 equipment 数据自动生成
        equipment = self._dialog._working_data.get("test", {}).get("equipment", {})
        locations = []
        for loc_key, info in equipment.items():
            locations.append(self._location_from_equipment(loc_key, info.get("testEquipment", "")))
        self._dialog._working_data.setdefault("test", {})["locations"] = locations
        self._list_tested_by.set_items(data.get("testedBy", []))

    def collect_data(self) -> None:
        test = self._dialog._working_data.setdefault("test", {})
        equipment = test.get("equipment", {})
        locations = []
        for loc_key, info in equipment.items():
            locations.append(self._location_from_equipment(loc_key, info.get("testEquipment", "")))
        test["locations"] = locations
        test["testedBy"] = self._list_tested_by.items()


class _EquipmentPage(QW.QWidget):
    """设备信息编辑页面"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog
        self._data: Dict[str, dict] = {}

        layout = QW.QVBoxLayout(self)

        self._table = QW.QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["No.", "Location", "Test Equipment", "Model"])
        self._table.verticalHeader().hide()
        self._table.setColumnWidth(0, 120)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSelectionBehavior(QW.QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.doubleClicked.connect(self._on_edit_row)

        btn_row = QW.QHBoxLayout()
        btn_add = QW.QPushButton("+ Add Location")
        btn_copy = QW.QPushButton("Copy")
        btn_edit = QW.QPushButton("Edit")
        btn_remove = QW.QPushButton("× Remove")
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_copy)
        btn_row.addWidget(btn_edit)
        btn_row.addWidget(btn_remove)
        btn_row.addStretch()

        btn_add.clicked.connect(self._on_add_location)
        btn_copy.clicked.connect(self._on_copy_location)
        btn_edit.clicked.connect(self._on_edit_selected)
        btn_remove.clicked.connect(self._on_remove_location)

        layout.addWidget(self._table)
        layout.addLayout(btn_row)

    def load_data(self, data: dict) -> None:
        self._data = data if isinstance(data, dict) else {}
        self._refresh_table()

    def _refresh_table(self) -> None:
        self._table.setRowCount(0)
        for i, (loc_key, info) in enumerate(self._data.items()):
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QW.QTableWidgetItem(str(i + 1)))
            self._table.setItem(row, 1, QW.QTableWidgetItem(loc_key))
            self._table.setItem(row, 2, QW.QTableWidgetItem(info.get("testEquipment", "")))
            self._table.setItem(row, 3, QW.QTableWidgetItem(info.get("testUnits", {}).get("model", "")))

    def _on_edit_row(self, index):
        self._edit_location(index.row())

    def _on_edit_selected(self):
        rows = self._table.selectionModel().selectedRows()
        if rows:
            self._edit_location(rows[0].row())

    def _edit_location(self, row: int):
        loc_key = self._table.item(row, 1).text()
        info = self._data.get(loc_key, {})
        dialog = _EquipmentEditDialog(loc_key, info, self)
        if dialog.exec():
            new_key, new_info = dialog.get_data()
            if new_key != loc_key:
                del self._data[loc_key]
            self._data[new_key] = new_info
            self._refresh_table()

    def _on_add_location(self):
        dialog = _EquipmentEditDialog("", {}, self)
        if dialog.exec():
            key, info = dialog.get_data()
            if key and key not in self._data:
                self._data[key] = info
                self._refresh_table()

    def _on_copy_location(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        loc_key = self._table.item(row, 1).text()
        info = self._data.get(loc_key)
        if info is None:
            return
        new_key = loc_key + " (Copy)"
        suffix = 1
        while new_key in self._data:
            suffix += 1
            new_key = f"{loc_key} (Copy {suffix})"
        self._data[new_key] = copy.deepcopy(info)
        self._refresh_table()

    def _on_remove_location(self):
        rows = self._table.selectionModel().selectedRows()
        for index in sorted(rows, reverse=True):
            loc_key = self._table.item(index.row(), 1).text()
            self._data.pop(loc_key, None)
        self._refresh_table()

    def collect_data(self) -> None:
        self._dialog._working_data.setdefault("test", {})["equipment"] = self._data


class _EquipmentEditDialog(QW.QDialog):
    """设备信息编辑对话框"""

    def __init__(self, loc_key: str, data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Equipment Info" if loc_key else "Add Equipment Info")
        self.setMinimumWidth(500)

        layout = QW.QVBoxLayout(self)
        form = QW.QFormLayout()

        self._edit_key = QW.QLineEdit(loc_key)
        form.addRow("Location Key:", self._edit_key)

        self._edit_equipment = QW.QLineEdit(data.get("testEquipment", ""))
        form.addRow("Test Equipment:", self._edit_equipment)

        sv = data.get("softwareVersions", {})
        self._edit_sv_server = QW.QLineEdit(sv.get("btsServer", ""))
        self._edit_sv_client = QW.QLineEdit(sv.get("btsClient", ""))
        self._edit_sv_da = QW.QLineEdit(sv.get("btsda", ""))
        form.addRow("BTS Server:", self._edit_sv_server)
        form.addRow("BTS Client:", self._edit_sv_client)
        form.addRow("BTSDA:", self._edit_sv_da)

        mm = data.get("middleMachines", {})
        self._edit_mm_model = QW.QLineEdit(mm.get("model", ""))
        self._edit_mm_hw = QW.QLineEdit(mm.get("hardwareVersion", ""))
        self._edit_mm_sn = QW.QLineEdit(mm.get("serialNumber", ""))
        self._edit_mm_fw = QW.QLineEdit(mm.get("firmwareVersion", ""))
        self._edit_mm_dt = QW.QLineEdit(mm.get("deviceType", ""))
        form.addRow("MM Model:", self._edit_mm_model)
        form.addRow("MM HW Ver:", self._edit_mm_hw)
        form.addRow("MM S/N:", self._edit_mm_sn)
        form.addRow("MM FW Ver:", self._edit_mm_fw)
        form.addRow("MM Device Type:", self._edit_mm_dt)

        tu = data.get("testUnits", {})
        self._edit_tu_model = QW.QLineEdit(tu.get("model", ""))
        self._edit_tu_hw = QW.QLineEdit(tu.get("hardwareVersion", ""))
        self._edit_tu_fw = QW.QLineEdit(tu.get("firmwareVersion", ""))
        form.addRow("TU Model:", self._edit_tu_model)
        form.addRow("TU HW Ver:", self._edit_tu_hw)
        form.addRow("TU FW Ver:", self._edit_tu_fw)

        layout.addLayout(form)

        btn_layout = QW.QHBoxLayout()
        btn_ok = QW.QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QW.QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def get_data(self) -> tuple:
        key = self._edit_key.text().strip()
        info = {
            "testEquipment": self._edit_equipment.text().strip(),
            "softwareVersions": {
                "btsServer": self._edit_sv_server.text().strip(),
                "btsClient": self._edit_sv_client.text().strip(),
                "btsda": self._edit_sv_da.text().strip(),
            },
            "middleMachines": {
                "model": self._edit_mm_model.text().strip(),
                "hardwareVersion": self._edit_mm_hw.text().strip(),
                "serialNumber": self._edit_mm_sn.text().strip(),
                "firmwareVersion": self._edit_mm_fw.text().strip(),
                "deviceType": self._edit_mm_dt.text().strip(),
            },
            "testUnits": {
                "model": self._edit_tu_model.text().strip(),
                "hardwareVersion": self._edit_tu_hw.text().strip(),
                "firmwareVersion": self._edit_tu_fw.text().strip(),
            },
        }
        return key, info
```

> 说明：`_ListEditor` 同时被 Battery 页与 Test 页复用，消除了原来两处重复的 `_fill_list`/`_read_list`/`_make_list_group`/`_make_list_widget`。

- [ ] **Step 2: 更新 config_defaults.py 默认值**

在 `src/battery_analysis/utils/config_defaults.py` 中：

把 `specifications` 硬编码字典替换为空字典：

```python
        "specifications": {
            "Coin Cell": ["CR2450", "CR2450YP", "CR2450PH", "CR2450D", "CR2450HE1", "CR2450HE4"],
            "Pouch Cell": ["CP224642A", "CF583083", "CP305050"]
        },
```
替换为：
```python
        "specifications": {},  # 从 rules 自动派生，启动时由配置对话框填充
```

把 rules 里 `CP305050` 的容量从 20 修正为 2000：

```python
            "CP305050/1S1P/20/20/80%/1.0"
```
替换为：
```python
            "CP305050/1S1P/2000/2000/80%/1.0"
```

- [ ] **Step 3: 语法与导入检查**

Run: `python -c "import ast; ast.parse(open('src/battery_analysis/main/ui_components/config_dialog.py', encoding='utf-8').read())"`
Expected: 无输出（解析成功）。

Run: `python -c "import battery_analysis.main.ui_components.config_dialog"`
Expected: 可导入（若提示缺少 `battery_classifier`，说明 Task 2.1 未完成）。

- [ ] **Step 4: 运行相关测试**

Run: `python -m pytest tests/battery_analysis/utils/test_battery_classifier.py tests/battery_analysis/utils/test_config_utils.py tests/battery_analysis/main/ui_components/test_main_config_manager.py -v`
Expected: 通过。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/main/ui_components/config_dialog.py src/battery_analysis/utils/config_defaults.py
git commit -m "refactor: master-detail config dialog, row-based rules editor, derived read-only specs"
```

---

### Task 2.4: main_window 配置重载走 ConfigService + 状态栏英文

**Files:**
- Modify: `src/battery_analysis/main/main_window.py`（`on_preferences_applied`/`reload_configuration`/`show_config_dialog`/`save_settings`）

- [ ] **Step 1: 改写 `on_preferences_applied`**

把当前实现：

```python
    def on_preferences_applied(self) -> None:
        try:
            from battery_analysis.utils.config_utils import (
                clear_config_cache, set_custom_config_path, clear_custom_config_path,
            )
            from PyQt6.QtCore import QSettings
            clear_config_cache()
            custom_path = QSettings().value("config/custom_config_path", "", type=str)
            if custom_path:
                set_custom_config_path(custom_path)
            else:
                clear_custom_config_path()
            self.reload_configuration()
        except (OSError, ValueError, ImportError) as e:
            self.logger.error("应用首选项后处理时发生错误: %s", e)
```

替换为：

```python
    def on_preferences_applied(self) -> None:
        try:
            # 配置路径/重载统一经 ConfigService；仅需丢弃 config_utils 的路径缓存，
            # 让 ConfigService 重新解析（含 QSettings 里的自定义路径）
            from battery_analysis.utils.config_utils import clear_config_cache
            clear_config_cache()
            svc = self._get_service("config")
            if svc is not None:
                svc.reload_config()
            if hasattr(self, 'config_manager'):
                self.config_manager.reload_config()
            if hasattr(self, 'ui_manager'):
                self.ui_manager.init_combobox()
            self.refresh_ui()
        except Exception as e:
            self.logger.error("Preferences apply post-processing failed: %s", e)
```

- [ ] **Step 2: 改写 `reload_configuration`**

```python
    def reload_configuration(self) -> None:
        try:
            from battery_analysis.utils.config_utils import clear_config_cache
            clear_config_cache()
            svc = self._get_service("config")
            if svc is not None:
                svc.reload_config()
            if hasattr(self, 'config_manager'):
                self.config_manager.reload_config()
            if hasattr(self, 'ui_manager'):
                self.ui_manager.init_combobox()
            self.refresh_ui()
        except Exception as e:
            self.logger.error("Failed to reload configuration: %s", e)
            if hasattr(self, 'statusBar_BatteryAnalysis'):
                self.statusBar_BatteryAnalysis.showMessage(f"Configuration reload failed: {str(e)}")
```

> `MainConfigManager.reload_config`（config_manager.py:145）与 `ConfigService.reload_config`（config_service.py:190）均已存在，两者职责不同：前者刷新 INI 兼容层读取缓存，后者重载 JSON 主配置。顺序：先清 config_utils 路径缓存 → JSON 重载 → INI 兼容层重载 → 下拉框/UI 刷新。

- [ ] **Step 3: `show_config_dialog` 与 `save_settings` 状态栏英文**

```python
self.statusBar_BatteryAnalysis.showMessage("配置已保存")  →  self.statusBar_BatteryAnalysis.showMessage("Configuration saved")
self.statusBar_BatteryAnalysis.showMessage("设置已保存")   →  self.statusBar_BatteryAnalysis.showMessage("Settings saved")
```

- [ ] **Step 4: 运行测试**

Run: `python -m pytest tests/battery_analysis/main/test_main_window.py -v`
Expected: 通过。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/main/main_window.py
git commit -m "refactor: route config reload through ConfigService; English status messages"
```

---

### Phase 2 检查点

Run: `python -m pytest tests/ -q 2>&1 | tail -20`
Expected: 全绿（或仅已知失败项）。

手动冒烟（Windows 桌面）：
1. 启动应用 → `菜单 → Configuration`，确认左侧导航 + 右侧页面切换。
2. Battery 页新增/删除一条 Rule → Specifications 两个 tab 自动刷新。
3. 修改 Manufacturers/Pulse Currents 等并 Save → 重开对话框数据仍在。
4. `Preferences` 打开正常（Language 可切换），无 auto-save 复选框。

---

## Phase 3 — 框架清理（Framework Cleanup）

> 前提：删除每个文件前用 `grep -rn "模块名" src tests --include=*.py` 确认无活跃引用。下面每个任务的引用已预先核实。

### Task 3.1: 删除 clean-architecture 死骨架源码

**Files:**
- Delete: `src/battery_analysis/application/usecases/{analyze_data_use_case,calculate_battery_use_case,generate_report_use_case}.py`
- Delete: `src/battery_analysis/infrastructure/repositories/battery_repository_impl.py`
- Delete: `src/battery_analysis/infrastructure/services/battery_analysis_service_impl.py`
- Delete: `src/battery_analysis/domain/services/battery_analysis_service.py`
- Delete: `src/battery_analysis/domain/repositories/{battery_repository,configuration_repository,test_profile_repository,test_result_repository}.py`
- Delete: `src/battery_analysis/domain/entities/{battery,configuration,test_profile,test_result}.py`
- **保留**：`src/battery_analysis/domain/entities/test_info.py`（6 个活跃文件使用）

- [ ] **Step 1: 确认引用面**

Run: `grep -rn "analyze_data_use_case\|calculate_battery_use_case\|generate_report_use_case\|battery_repository_impl\|battery_analysis_service_impl\|domain.services\|domain.repositories\|domain.entities.battery\|domain.entities.configuration\|domain.entities.test_profile\|domain.entities.test_result" src tests --include=*.py`
Expected: 命中仅在被删文件自身、待删测试，或指向 `domain.entities.test_info`。

- [ ] **Step 2: 删除文件**

Run: `git rm src/battery_analysis/application/usecases/analyze_data_use_case.py src/battery_analysis/application/usecases/calculate_battery_use_case.py src/battery_analysis/application/usecases/generate_report_use_case.py src/battery_analysis/infrastructure/repositories/battery_repository_impl.py src/battery_analysis/infrastructure/services/battery_analysis_service_impl.py src/battery_analysis/domain/services/battery_analysis_service.py src/battery_analysis/domain/repositories/battery_repository.py src/battery_analysis/domain/repositories/configuration_repository.py src/battery_analysis/domain/repositories/test_profile_repository.py src/battery_analysis/domain/repositories/test_result_repository.py src/battery_analysis/domain/entities/battery.py src/battery_analysis/domain/entities/configuration.py src/battery_analysis/domain/entities/test_profile.py src/battery_analysis/domain/entities/test_result.py`

若 `application/`、`infrastructure/`、`domain/services/`、`domain/repositories/` 目录已空，用 `rmdir` 删除（保留 `domain/entities/test_info.py` 所在目录）。

- [ ] **Step 3: 删除配套测试**

Run:
```bash
git rm tests/battery_analysis/domain/entities/test_battery.py tests/battery_analysis/domain/entities/test_configuration.py tests/battery_analysis/domain/entities/test_test_profile.py tests/battery_analysis/domain/entities/test_test_result.py
git rm tests/battery_analysis/domain/repositories/test_battery_repository.py tests/battery_analysis/domain/repositories/test_configuration_repository.py tests/battery_analysis/domain/repositories/test_test_profile_repository.py tests/battery_analysis/domain/repositories/test_test_result_repository.py
git rm tests/battery_analysis/domain/services/test_battery_analysis_service.py
git rm tests/battery_analysis/application/usecases/test_analyze_data_use_case.py tests/battery_analysis/application/usecases/test_calculate_battery_use_case.py tests/battery_analysis/application/usecases/test_generate_report_use_case.py
git rm tests/battery_analysis/infrastructure/repositories/test_battery_repository_impl.py tests/battery_analysis/infrastructure/services/test_battery_analysis_service_impl.py
git rm tests/manual/test_cache_mechanism.py
```

- [ ] **Step 4: 运行全量测试确认无回归**

Run: `python -m pytest tests/ -q 2>&1 | tail -20`
Expected: 通过（不再引用被删模块）。

- [ ] **Step 5: 提交**

```bash
git add -A src tests
git commit -m "refactor: remove unintegrated clean-architecture skeleton and its tests (keep test_info)"
```

---

### Task 3.2: 删除 i18n / 应用层死代码

**Files:**
- Delete: `src/battery_analysis/main/services/i18n_service.py`
- Delete: `src/battery_analysis/main/services/application_service.py`
- Delete: `src/battery_analysis/main/controllers/visualizer_controller.py`
- Modify: `src/battery_analysis/main/services/service_container/container.py`
- Modify: `src/battery_analysis/main/controllers/__init__.py`
- Delete: `tests/battery_analysis/main/services/test_i18n_service.py`
- Delete: `tests/battery_analysis/main/services/test_application_service.py`
- Delete: `tests/battery_analysis/main/controllers/test_visualizer_controller.py`

- [ ] **Step 1: 确认引用面**

Run: `grep -rn "i18n_service\|application_service\|visualizer_controller" src tests --include=*.py | grep -v '\.venv'`
Expected: 命中仅在被删文件、`container.py`、`controllers/__init__.py`、待删测试。

- [ ] **Step 2: 删除源文件与测试**

```bash
git rm src/battery_analysis/main/services/i18n_service.py src/battery_analysis/main/services/application_service.py src/battery_analysis/main/controllers/visualizer_controller.py
git rm tests/battery_analysis/main/services/test_i18n_service.py tests/battery_analysis/main/services/test_application_service.py tests/battery_analysis/main/controllers/test_visualizer_controller.py
```

- [ ] **Step 3: 更新 container.py**

在 `src/battery_analysis/main/services/service_container/container.py`：
- 删除 `Services` dataclass 中的 `visualizer_controller: Any = None` 行。
- 删除 `_name_map` 中的 `"visualizer_controller": "visualizer_controller",` 行。
- 删除 `_initialize_services` 第 3 段中的 import 与实例化：

```python
        from battery_analysis.main.controllers.visualizer_controller import VisualizerController
```
和
```python
        self._impl.visualizer_controller = VisualizerController()
```

（`application` 字段与 `i18n` 相关代码本就只存在于被删的 `application_service.py` 中，`Services.application` 字段保留不动——它不产生实例化。）

- [ ] **Step 4: 更新 controllers/__init__.py**

删除 `from .visualizer_controller import VisualizerController` 一行。

- [ ] **Step 5: 运行测试**

Run: `python -m pytest tests/battery_analysis/main/services/test_service_container.py tests/battery_analysis/main/controllers -v`
Expected: 通过。

- [ ] **Step 6: 提交**

```bash
git add -A src/battery_analysis/main/services src/battery_analysis/main/controllers tests/battery_analysis/main
git commit -m "refactor: remove dead i18n/application/visualizer services and update container"
```

---

### Task 3.3: 删除 `LanguageHandler` 并合并语言切换逻辑

**Files:**
- Delete: `src/battery_analysis/main/ui/language_handler.py`（连同空的 `main/ui/` 目录）
- Modify: `src/battery_analysis/main/initialization/steps/language_initialization_step.py`

**背景**：`main_window._on_language_changed`（main_window.py:269-275）已实现 LanguageHandler 的全部职责（窗口标题、`_update_ui_texts`、`_update_statusbar_messages`、`_refresh_dialogs`）。`language_initialization_step._connect_language_signals` 已把 `language_changed` 信号连接到 `main_window._on_language_changed`。因此 LanguageHandler 是纯冗余。

- [ ] **Step 1: 移除实例化**

在 `src/battery_analysis/main/initialization/steps/language_initialization_step.py`：

删除导入：
```python
from battery_analysis.main.ui.language_handler import LanguageHandler
```

删除 `execute` 中的：
```python
            # 初始化语言处理器
            main_window.language_handler = LanguageHandler(main_window)
```

保留 `_connect_language_signals`（它连接 `language_manager.language_changed` → `main_window._on_language_changed`）与 `_initialize_environment_info` 调用。

`execute` 里的 logger 中文改为英文：
- `self.logger.info("语言初始化完成")` → `self.logger.info("Language initialization complete")`
- `self.logger.exception("语言初始化失败")` → `self.logger.exception("Language initialization failed")`

- [ ] **Step 2: 删除文件与目录**

Run: `git rm src/battery_analysis/main/ui/language_handler.py`
Run: `rmdir src/battery_analysis/main/ui`（目录已空时；若有 `__pycache__` 一并删除）

- [ ] **Step 3: 确认无残留引用**

Run: `grep -rn "language_handler\|main.ui.language_handler" src tests --include=*.py`
Expected: 无输出。

- [ ] **Step 4: 运行测试**

Run: `python -m pytest tests/battery_analysis/main -q 2>&1 | tail -10`
Expected: 通过。

- [ ] **Step 5: 提交**

```bash
git add -A src/battery_analysis/main
git commit -m "refactor: remove redundant LanguageHandler; language switch handled by main window"
```

---

### Phase 3 检查点（最终验证）

- [ ] **Step 1: 全量测试**

Run: `python -m pytest tests/ -q 2>&1 | tail -25`
Expected: 全绿。

- [ ] **Step 2: 无死代码引用**

Run: `grep -rn "application_service\|i18n_service\|visualizer_controller\|LanguageHandler\|analyze_data_use_case\|battery_repository_impl\|domain.repositories\|domain.services" src tests --include=*.py`
Expected: 无输出。

- [ ] **Step 3: 应用可启动**

Run: `python -c "from battery_analysis.main.launcher import main; import inspect; print('launcher ok')"`
Expected: 打印 `launcher ok`（不真正启动 GUI）。

- [ ] **Step 4: 手动冒烟**

1. 启动应用，界面与日志为英文。
2. 打开 `Preferences`，切到 `中文(简体)`，界面语言切换生效；重启后回到英文（因为默认锁定 en）。
3. 打开 `Configuration`，master-detail 正常工作，Rules/Specifications 联动。
4. 运行一次数据导入/分析，确认业务链路正常。

---

## 自审记录

- **Spec 覆盖**：Phase 1 覆盖 spec §1 全部（默认 en、`_()` 规范化、.po 重建、硬编码中文/日志英文）；Phase 2 覆盖 spec §2 全部（master-detail、逐条化、Rules 表格、Specs 派生只读、解锁列表项、Preferences 清理与迁移、去重、config_service 路径统一、`config_defaults` 修正）；Phase 3 覆盖 spec §3 全部（死骨架、15+3 测试、死服务、LanguageHandler、container/controllers 同步）与 §4 验证。
- **无占位符**：每个代码步骤均含完整代码或完整映射表。
- **类型/签名一致性**：`_ListEditor.set_items/items`、`_RulesEditor.set_rules/rules`、`derive_specifications`、`IConfigPathProvider.get_config_path` 在各任务间保持一致；`preferences_dialog` 迁移后 import 路径与测试一致。
