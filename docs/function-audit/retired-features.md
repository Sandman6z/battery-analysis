# 遗留功能退役记录

## 本轮结果

在用户明确要求“一并处理遗留和用不到的功能”后，沿生产调用链、菜单、信号、服务注册、模块导出、构建脚本和测试核对，不再仅因旧代码有测试就保留。

| 指标 | 本轮前 | 本轮后 |
|---|---:|---:|
| `src` Python 文件 | 177 | 165 |
| 函数/方法（含嵌套） | 1080 | 985 |
| 当前阈值下近似函数候选 | 23 对 | 4 对 |
| 初始化步骤 | 12 | 11 |
| 共享服务/控制器节点 | 7 | 5 |
| 启动时创建的命令 | 6 | 1 |

共移除 12 个生产 Python 文件和 1 个历史 Designer UI 文件；另清理存活模块中的无用方法、异常类型、菜单动作及连接。函数索引和候选已重新生成。没有测量真实任务的速度/内存/包体积，不以文件数或行数替代性能证据。

## 已删除的功能链

### 1. 旧验证服务与控制器

删除：

- `main/services/validation_service.py`
- `main/controllers/validation_controller.py`
- `Services.validation` / `Services.validation_controller` 字段与构造
- services/controllers 的导出，以及 SignalConnector 的旧连接
- 对应旧测试

原因：实际分析使用 ValidationManager → InputValidator；旧服务的 TestInfo 索引、化学体系分类、浮点容量范围与当前契约不匹配；控制器仍检查 xlsx/csv。无当前分析入口调用，不能保留一条看似可用、实际规则错误的验证通道。

保留：InputValidator、ValidationManager、NDAX 运行预检、后台读取保护。

### 2. 五个不执行业务的占位命令和 Presenter

删除：

- `CalculateBatteryCommand`、`AnalyzeDataCommand`、`ExportReportCommand`、`GenerateReportCommand`、`BatchProcessingCommand`
- `commands/data_commands.py`、`commands/report_commands.py` 和旧导出
- `presenters/main_presenter.py` 与 `PresentersInitializationStep`
- 无读取方的 `_commands` 注册字典与旧主窗口命令属性

这些命令最终仅调用 Presenter 输出日志/Ready，或标记“开发中”，并没有真正计算或导出。Presenter 的状态副本、另一套必填/Barcode 校验也无生产调用方。

保留真正的 `RunAnalysisCommand`，运行按钮和 Analyze Data 菜单仍走同一个 AnalysisRunner；实际分析、绘图、Excel/Word/CSV/JSON 输出均未删除。

配套修复：CommandManagerInitializationStep 仅依赖 analysis_runner；LanguageInitializationStep 不再依赖已删除的 presenter，仍进行语言连接及真实环境信息初始化。

### 3. 十个未展示且无有效处理器的菜单动作

删除 QAction 构造、快捷键/工具提示、类型声明：

- New、Open、Save、Save As
- Undo、Redo
- Export Report、Calculate Battery、Generate Report、Batch Processing

不是关闭现有报告功能：它们原本就不在可见菜单中；报告仍随真实分析流程生成。可见的 Analyze Data、NDAX Converter、图表查看器、配置、首选项、主题、剪切/复制/粘贴、帮助、退出等入口保留。

### 4. 旧 Designer 界面及无人使用的 UI 抽象

删除：

- `ui/ui_main_window.py`
- `ui/resources/ui_battery_analysis.ui`
- `ui/frameworks/pyqt6_ui_framework.py`（含其 MessageBoxType）
- VS Code 的旧 Pyuic6 生成任务
- `scripts/build.py` 中对旧生成界面的 hidden import
- 仅验证上述旧封装的测试（混合测试文件中仅移除旧封装相关用例）

证据：真实 Main 构造直接使用 UIBuilder 和 BatteryAnalysisTab；没有生产代码导入旧生成界面或 UI 框架。README 的界面修改说明已同步。`build/` 内历史产物/旧 spec 未修改；新构建由更新后的脚本生成。

### 5. 旧资源调度器

删除 `utils/resource_manager.py` 及其测试。该模块没有生产调用方，当前 NDAX 转换已使用 `concurrency_policy.get_conversion_worker_count`。

保留当前并发预算和 Windows 进程数上限；未删除仍被环境信息/日志使用的 psutil 依赖。

### 6. 旧通用 Excel 摘要与校验链

删除：

- `analysis/excel_processor.py`
- `main/business_logic/excel_validator.py`
- 上述模块对应测试
- 已无调用的 `scan_sorted_xlsx`

这条“智能表头扫描 → 通用摘要/宽松 Excel 校验”链仅剩内部互相引用和测试，不在当前 NDAX 生产入口中。保留仍使用的 `utils/readers/xlsx_reader.py`、NDAX→XLSX 转换、Excel 报告写入器、文件校验器及可视化读取功能；没有把项目中的所有 Excel 支持都删除。

### 7. 旧逐格数值统计

删除 `utils/numeric_utils.py` 及其独立测试，生产代码已不调用它，实际统计集中在 `reports.statistics_utils`。

保留批量统计的随机对照测试：改用逐格 NumPy 参考值直接核对，不为了测试旧函数而保留另一套生产实现。空 cell 为 0、单样本标准差为 0、样本标准差 ddof=1 等约定保持不变。

### 8. 空壳方法与断开的重复对话框

删除：

- `ConfigManager.save_user_settings`、`UIManager.load_user_settings` 及后者的启动调用
- `LanguageManager.load_preferences`（语言实际通过 QSettings 加载）
- `MenuManager.update_menu_texts`
- `WindowSetup.setup_menu_shortcuts`（只输出已迁移日志）、`WindowSetup.init_widgetcolor`
- `WindowTextsMixin._refresh_dialogs` 及调用（原来没有刷新任何对话框）
- `SignalConnector._on_config_loaded` 及其空信号连接
- `DialogManager.handle_data_error_recovery` 与空 `_open_data_directory_dialog`
- ApplicationInitializer 的空构造函数

旧 DialogManager 恢复对话框没有调用方，还引用不存在的主窗口重选方法；当前 VisualizationManager 使用的 `DataErrorRecoveryDialog` 保留。真实的语言/主题偏好保存、配置 JSON 保存、字段错误清理与菜单快捷键实现均保留。

### 9. 未使用的异常类型和旧辅助函数

移除未被抛出/捕获的 DataException、FileNotFoundException、FileFormatException、AnalysisException、ValidationException、ServiceException、InitializationException，以及从未使用/抛出的 ConfigParseError。

保留实际使用的 BaseAppException、ConfigException、BatteryAnalysisException，错误码和字符串格式有回归测试。

另删除无调用的 safe_int_convert 和已被向量化匹配替代的 b_is_in_range；当前浮点配置解析与脉冲匹配没有改算法。

## 特别保留的内容

- 装饰器注册的配置迁移：普通静态搜索看不到调用，但运行时由迁移表执行，不能删。
- Qt 槽、接口抽象方法：不能只因没有直接函数调用就判定无用。
- 当前错误恢复对话框、运行前检查、后台解析保护、版本防覆盖、实际报告输出。
- 仍有职责的兼容入口（例如 report_coordinator 与 file_writer 导出）：未因文件名旧就整体删除。
- 历史 CHANGELOG、docs/plans、docs/specs 作为历史记录保留，不批量改写；当前 README、审查索引与构建配置已更新。

## 验证结果

1. 本轮前完整自动化测试：1363 passed。
2. 本轮后完整自动化测试：**1316 passed**，没有忽略新增失败；旧功能测试同步删除、命令测试重写，并新增 `tests/test_retired_features.py` 的 10 项回归。
3. 回归覆盖真实 QAction 不再创建、Analyze Data 真正调用分析、转换/配置菜单可用、服务节点正确、命令/语言不依赖 Presenter、11 步初始化、有效控制器信号、构建导入及实际异常格式。
4. Ruff 检查通过；`git diff --check` 通过；VS Code tasks.json 可正常解析。
5. 使用临时 APPDATA/LOCALAPPDATA 和临时 IniFormat QSettings 目录执行真实 launcher 的 offscreen `--smoke-test`，退出码 0。启动条件为延迟初始化完成且配置菜单启用。
6. 冒烟运行仍显示 Qt 字体目录缺失警告，以及空配置下默认电流/电压等级警告；这些未被隐藏或当作本轮清理已解决的问题。

## 兼容性与未验证范围

这是应用内部 API 的主动退役，不是无行为变化的纯重构。仓库外脚本若直接导入已删除的旧类/函数，或访问旧命令、服务、QAction 属性，会需要迁移；没有为每个死入口再保留一个兼容空壳。当前应用中的有效用户入口已通过回归和启动冒烟。

未进行冻结 EXE 构建、真实硬件/大批量数据性能、人工逐菜单交互验证。没有自动提交，也没有改写工作区原有 NDAX 引导及翻译改动。不保证静态盘点能证明全项目绝无遗留；下一优先级仍是报告准备工作、配置生命周期和重复读取/计算的数据流核查。
