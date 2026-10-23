# Main 类瘦身设计

## 背景

`main_window.py` 的 `Main` 类有 702 行、55+ 方法，其中 ~38 个是纯委托或死代码。这导致：
- 间接层增加理解成本
- 新增功能时需要在 Main 上加方法
- Main 类职责边界模糊

## 三维分析框架

### 维度一：PyQt6 信号/槽机制

Qt 信号连接规则：`signal.connect(callable)` 需要一个可调用引用。

**关键时序**：所有信号连接发生在 `connect_widget()` 阶段（priority=90），此时全部 manager 已在 phase 1-3 初始化完毕。引用链 `self.main_window.xxx_manager.method` 在连接时安全。

### 维度二：Python 运行效率

```python
self.main_window.get_version()                    # 1次属性查找 + 1次调用
self.main_window.version_manager.get_version()    # 2次属性查找 + 1次调用
# 差异 ~50ns，UI 事件驱动操作可忽略
```

效率不是决定因素，代码清晰度才是。

### 维度三：代码上下文

- 38 个纯委托方法的调用者全部是内部代码（Qt 信号连接 + 其他 manager）
- 调用者都在 deferred_init 之后才执行
- 无外部 API 契约约束

## 最终方案

| 类别 | 数量 | 说明 |
|------|------|------|
| 保留 | 16 | 有逻辑 + 剪贴板封装 |
| 删除 | 48 | 纯委托 + 死代码 |

**预期**：702 行 → ~230 行，64 方法 → 16

---

## 保留的13个方法

| 方法 | 行数 | 保留理由 |
|------|------|---------|
| `_deferred_init` | 80 | 4阶段初始化管线协调，不可拆 |
| `_get_component` | 8 | 懒加载+缓存模式，避免重复从容器获取 |
| `_get_service` | 2 | 组件获取快捷方式 |
| `_get_controller` | 2 | 组件获取快捷方式 |
| `on_preferences_applied` | 27 | 协调 config 重载 + theme 应用 + UI 刷新 + combo 恢复 |
| `reload_configuration` | 15 | 协调 config 重载 + UI 刷新 + 错误处理 |
| `refresh_texts` | 80 | 语言切换全量刷新，协调30+控件的 setText |
| `show_config_dialog` | 20 | 创建对话框 + 保存状态 + 重载配置 + 恢复 combo |
| `refresh_ui` | 12 | UI 局部刷新（statusbar + combo 重选） |
| `connect_widget` | 5 | 信号连接入口，Qt 要求在 Main 上 |
| `_load_application_icon` | 18 | 图标搜索 + fallback，有实际逻辑 |
| `_on_language_changed` | 5 | language_manager.register 回调入口，有 setWindowTitle 逻辑 |
| `resizeEvent` | 15 | QTimer 去抖（150ms），Qt 事件重写必须在 Main |
| `copy_selected_text` | 3 | Qt 剪贴板封装，菜单信号目标（非 manager 委托） |
| `paste_text` | 3 | 同上 |
| `cut_selected_text` | 3 | 同上 |

---

## 删除的38个方法（按 PR 分组）

### PR-A: 版本与数据处理（3个方法，3个文件）

删除：
- `get_version()` → `self.version_manager.get_version()`
- `set_version()` → `self.version_manager.set_version()`
- `get_xlsxinfo()` → `self.data_processor.get_xlsxinfo()`

调用者更新：
| 文件 | 原调用 | 新调用 |
|------|--------|--------|
| `signal_connector.py:75` | `main_controller.analysis_completed.connect(self.main_window.set_version)` | `.connect(self.main_window.version_manager.set_version)` |
| `ui_manager.py:578` | `self.main_window.lineEdit_InputPath.textChanged.connect(self.main_window.get_xlsxinfo)` | `.connect(self.main_window.data_processor.get_xlsxinfo)` |
| `ui_manager.py:583` | `self.main_window.sigSetVersion.connect(self.main_window.get_version)` | `.connect(self.main_window.version_manager.get_version)` |
| `main_window.py:123` | `self.get_version()` | `self.version_manager.get_version()` |

### PR-B: 路径选择（3个方法，2个文件）

删除：
- `select_inputpath()` → `self.path_manager.select_inputpath()`
- `select_outputpath()` → `self.path_manager.select_outputpath()`
- `select_testprofile()` → `self.test_profile_manager.select_testprofile()`

调用者更新：
| 文件 | 原调用 | 新调用 |
|------|--------|--------|
| `ui_manager.py:579` | `self.main_window.pushButton_TestProfile.clicked.connect(self.main_window.select_testprofile)` | `.connect(self.main_window.test_profile_manager.select_testprofile)` |
| `ui_manager.py:580` | `self.main_window.pushButton_InputPath.clicked.connect(self.main_window.select_inputpath)` | `.connect(self.main_window.path_manager.select_inputpath)` |
| `ui_manager.py:581` | `self.main_window.pushButton_OutputPath.clicked.connect(self.main_window.select_outputpath)` | `.connect(self.main_window.path_manager.select_outputpath)` |

### PR-C: 验证（6个方法，3个文件）

删除：
- `validate_version()` → `self.validation_manager.validate_version()`
- `validate_input_path()` → `self.validation_manager.validate_input_path()`
- `validate_required_fields()` → `self.validation_manager.validate_required_fields()`
- `check_batterytype()` → `self.validation_manager.check_batterytype()`
- `check_specification()` → `self.validation_manager.check_specification()`
- `checkinput()` → `self.validation_manager.checkinput()`

调用者更新：
| 文件 | 原调用 | 新调用 |
|------|--------|--------|
| `ui_manager.py:361` | `.connect(self.main_window.validate_version)` | `.connect(self.main_window.validation_manager.validate_version)` |
| `ui_manager.py:364-366` | `.connect(self.main_window.validate_input_path)` | `.connect(self.main_window.validation_manager.validate_input_path)` |
| `ui_manager.py:376` | `.connect(self.main_window.validate_required_fields)` | `.connect(self.main_window.validation_manager.validate_required_fields)` |
| `ui_manager.py:560-562` | `.connect(self.main_window.check_batterytype)` | `.connect(self.main_window.validation_manager.check_batterytype)` |
| `ui_manager.py:563-568` | `.connect(self.main_window.check_specification)` | `.connect(self.main_window.validation_manager.check_specification)` |
| `analysis_runner.py:66` | `self.main_window.checkinput()` | `self.main_window.validation_manager.checkinput()` |

### PR-D: 可视化（2个方法，5个文件）

删除：
- `run_visualizer()` → `self.visualization_manager.run_visualizer()`
- `show_visualizer_error()` → `self.visualization_manager.show_visualizer_error()`

保留：`show_chart_area`、`hide_chart_area`、`get_chart_container`、`get_chart_control_panel`（有实际逻辑）

调用者更新：
| 文件 | 原调用 | 新调用 |
|------|--------|--------|
| `signal_connector.py:79` | `main_controller.start_visualizer.connect(self.main_window.run_visualizer)` | `.connect(self.main_window.visualization_manager.run_visualizer)` |
| `menu_manager.py:158` | `self.main_window.actionBatteryChartViewer.triggered.connect(self.main_window.run_visualizer)` | `.connect(self.main_window.visualization_manager.run_visualizer)` |
| `dialog_manager.py:272` | `self.main_window.run_visualizer(xml_path=None)` | `self.main_window.visualization_manager.run_visualizer(xml_path=None)` |
| `data_error_dialog.py:114` | `self.main_window.run_visualizer(xml_path=None)` | `self.main_window.visualization_manager.run_visualizer(xml_path=None)` |
| `data_error_dialog.py:161` | `self.main_window.run_visualizer(xml_path=directory)` | `self.main_window.visualization_manager.run_visualizer(xml_path=directory)` |

### PR-E: 命令执行（6个方法，2个文件）

删除：
- `calculate_battery()` → `self.calculate_battery_command.execute()`
- `analyze_data()` → `self.analyze_data_command.execute()`
- `generate_report()` → `self.generate_report_command.execute()`
- `export_report()` → `self.export_report_command.execute()`
- `batch_processing()` → `self.batch_processing_command.execute()`
- `run()` → `self.run_analysis_command.execute()`

调用者更新：
| 文件 | 原调用 | 新调用 |
|------|--------|--------|
| `menu_manager.py:155` | `.connect(self.main_window.calculate_battery)` | `.connect(self.main_window.calculate_battery_command.execute)` |
| `menu_manager.py:157` | `.connect(self.main_window.analyze_data)` | `.connect(self.main_window.analyze_data_command.execute)` |
| `menu_manager.py:159` | `.connect(self.main_window.generate_report)` | `.connect(self.main_window.generate_report_command.execute)` |
| `menu_manager.py:160` | `.connect(self.main_window.batch_processing)` | `.connect(self.main_window.batch_processing_command.execute)` |
| `menu_manager.py:178` | `.connect(self.main_window.export_report)` | `.connect(self.main_window.export_report_command.execute)` |
| `main_window.py:315` | `self.pushButton_Run.clicked.connect(self.run)` | `self.pushButton_Run.clicked.connect(self.run_analysis_command.execute)` |

### PR-F: 杂项委托 + 死代码（28个方法，4个文件）

删除：
- `set_table()` → `self.table_manager.set_table()`
- `save_table()` → `self.table_manager.save_table()`
- `init_widgetcolor()` → `self.ui_manager.init_widgetcolor()`
- `toggle_statusbar()` → `self.menu_manager.toggle_statusbar()`
- `toggle_statusbar_safe()` → `self.menu_manager.toggle_statusbar_safe()`
- `setup_menu_shortcuts()` → `self.menu_manager.setup_menu_shortcuts()`
- `show_user_manual()` → `self.help_manager.show_user_manual()`
- `show_online_help()` → `self.dialog_manager.show_online_help()`
- `handle_exit()` → `self.dialog_manager.handle_exit()`
- `handle_about()` → `self.dialog_manager.handle_about()`
- `show_preferences()` → `self.dialog_manager.show_preferences()`
- `save_settings()` → 删除（只显示 statusbar 消息，无实际功能，死代码）
- `set_theme()` → `self.theme_manager.set_theme()`
- `_initialize_environment_info()` → `self.environment_manager.initialize_environment_info()`
- `_ensure_env_info_keys()` → `self.environment_manager.ensure_env_info_keys()`
- `_open_report()` → `self.report_manager.open_report()`
- `_open_report_path()` → `self.report_manager.open_report_path()`
- `_show_analysis_complete_dialog()` → `self.report_manager.show_analysis_complete_dialog()`
- `rename_pltPath()` → `self.config_manager.rename_pltPath()`
- `update_config()` → `self.config_manager.update_config()`
- `on_temperature_type_changed()` → `self.temperature_handler.on_temperature_type_changed()`
- `get_config()` → `self.config_manager.get_config()`
- `init_window()` → `self.ui_manager.init_window()`
- `init_widget()` → `self.ui_manager.init_widget()`
- `show_chart_area()` → 删除（死代码，定义但未被调用）
- `hide_chart_area()` → 删除（死代码，定义但未被调用）
- `get_chart_container()` → 删除（死代码，定义但未被调用）
- `get_chart_control_panel()` → 删除（死代码，定义但未被调用）

调用者更新：
| 文件 | 原调用 | 新调用 |
|------|--------|--------|
| `ui_manager.py:569-571` | `.connect(self.main_window.set_table)` | `.connect(self.main_window.table_manager.set_table)` |
| `ui_manager.py:574-576` | `.connect(self.main_window.on_temperature_type_changed)` | `.connect(self.main_window.temperature_handler.on_temperature_type_changed)` |
| `analysis_runner.py:44` | `self.main_window.save_table()` | `self.main_window.table_manager.save_table()` |
| `analysis_runner.py:45` | `self.main_window.init_widgetcolor()` | `self.main_window.ui_manager.init_widgetcolor()` |
| `signal_connector.py:77` | `main_controller.path_renamed.connect(self.main_window.rename_pltPath)` | `.connect(self.main_window.config_manager.rename_pltPath)` |
| `menu_manager.py:134-137` | `.connect(self.main_window.handle_exit/handle_about/show_user_manual/show_online_help)` | `.connect(self.main_window.dialog_manager.handle_exit)` 等 |
| `menu_manager.py:140-142` | `.connect(self.main_window.copy_selected_text/paste_text/cut_selected_text)` | **保留**（有实际逻辑，非 manager 委托） |
| `menu_manager.py:145` | `.connect(self.main_window.show_preferences)` | `.connect(self.main_window.dialog_manager.show_preferences)` |
| `menu_manager.py:150` | `.connect(self.main_window.toggle_statusbar_safe)` | `.connect(self.main_window.menu_manager.toggle_statusbar_safe)` |
| `menu_manager.py:177` | `.connect(self.main_window.save_settings)` | 删除连接 + 删除方法（死代码） |
| `menu_manager.py:187,191` | `lambda: self.main_window.set_theme("light/dark")` | `lambda: self.main_window.theme_manager.set_theme("light/dark")` |
| `main_window.py:183` | `self.ui_manager.init_window()` | 不变（已在 ui_manager 上调用） |

---

## 实施策略

每个 PR 独立分支，独立测试，独立合并：
1. 创建分支
2. 删除委托方法
3. 更新所有调用者（信号连接 + 直接调用）
4. 运行测试确认通过
5. 提交 + 合并

### 风险控制

- 每个 PR 影响的文件数 ≤ 5，改动量可控
- 信号连接的更新是机械替换，出错概率低
- 保留的方法不改动，不影响已有逻辑
- 测试覆盖已有 613+ 个，能有效捕获回归
- 所有 manager 在 phase 1-3 初始化，信号连接在 phase 4，引用链安全

### 预期结果

- Main 类从 702 行 → ~250 行
- 方法数从 55+ → 18
- 每个保留的方法都有实际逻辑或 Qt API 封装，无纯转发
