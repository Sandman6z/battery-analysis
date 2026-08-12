---
name: English Default, Settings Polish, and Framework Cleanup
description: 默认语言切换为英文（保留 i18n）、配置对话框改为逐条化主从布局（master-detail）、删除未接入的 clean-architecture 死骨架
---

# English Default + Settings Polish + Framework Cleanup

## 背景

当前应用存在三个独立问题，本次一并解决：

1. **默认语言**：`initialize_default_locale()` 与 `LanguageManager._initialize_settings()` 都调用 `detect_system_locale()`，在中文系统上应用默认显示中文；但大量 `_("key", "Chinese-fallback")` 调用把第二个参数当作 gettext context 传入，而 .po 文件没有任何 `msgctxt` 条目，导致这些位置直接显示原始 key（如 `confirm_exit_title`）。
2. **配置对话框**：`ConfigDialog` 使用顶部 `QTabWidget` 分 3 页（Battery / Test / Equipment），其中电池页堆叠 8 个区域，形成"大对话框"；docstring 声称的"左侧分类列表、右侧编辑器"（master-detail）从未实现。`_BatteryConfigPage` 与 `_TestConfigPage` 存在重复的 `_fill_list`/`_read_list` 方法。
3. **框架残留**：`application/`、`infrastructure/`、`domain/{services,repositories}`、`domain/entities/`（除 `test_info.py`）构成一套从未接入主应用的 clean-architecture 骨架，配套 15 个测试。另有 `LanguageHandler`、`I18nService`、`visualizer_controller`、`ApplicationService` 等死代码。

## 改动目标

1. **默认英文，保留 i18n**：默认锁定 `en`，不再自动跟随系统语言；`_()` 调用规范化为 `msgid = 英文文本`；重建 en/zh_CN 的 .po；全库硬编码中文（界面 + 日志）转英文。docstring/注释不改。
2. **设置/配置调优**：保持"菜单 → Configuration/Preferences"两个入口不变；`Configuration` 改为 master-detail 布局解决大对话框问题；所有配置项逐条化（row-based）；Rules 用表格编辑；Specifications 从 Rules 派生且只读；Preferences 对话框清理并迁出 `i18n/` 包。
3. **框架清理**：删除未接入的 clean-architecture 死骨架及其测试，删除 i18n 三层代理中的死链（LanguageHandler / I18nService），删除 `visualizer_controller` 与 `ApplicationService`；配置访问统一走 `ConfigService`。
4. **风险控制**：删除前做 import-graph 审计与全量测试基线；明确放弃 clean-architecture 迁移基础（仅保留 `test_info.py` 实体）。

## 决策记录

| # | 决策 | 理由 |
|---|------|------|
| D1 | 默认语言锁定 `en`；`detect_system_locale()` 保留但不作为默认入口 | 保留 i18n 框架，以后有空再优化多语言 |
| D2 | `_()` 参数语义修正为 `_("英文 msgid")`，消除 key-based 与 context-abuse | .po 无 msgctxt，传 context 必然 fallback 到 key |
| D3 | `en.po` 做成 identity（msgstr = msgid），`zh_CN.po` 保留中文译文 | 默认 en 时零翻译开销；中文仍可用 |
| D4 | `Language` tab 保留在 Preferences 中 | 保留 i18n 能力，用户可手动切换 |
| D5 | 配置对话框改 master-detail：左导航 + 右 `QStackedWidget` | 修复"大对话框"，兑现 docstring 声明的意图 |
| D6 | 所有配置项逐条化：列表类用 row-based 编辑，Rules 用 `QTableWidget` | 用户 Q2 要求"逐条化" |
| D7 | 解锁 Construction Methods / Specification Methods / Pulse Currents / Cut-off Voltages / Manufacturers；仅 Battery Types 只读 | 事实核查发现这些键被 ui_manager/data_processor/data_loader 消费，是活跃配置 |
| D8 | Specifications 从 Rules 派生且只读 | 吸收既有 rules-to-specs 设计（`docs/superpowers/specs/2026-06-18-rules-to-specs-design.md`） |
| D9 | 删除未接入的 clean-architecture 骨架；保留 `test_info.py` | 6 个活跃文件消费 `test_info.py` |
| D10 | 配置路径/重载通过 `ConfigService`；`config_parser.py` 保留 | `config_parser` 被 `battery_config_initialization_step.py` 活跃使用 |

## 实现设计

### 第 1 节：英文化

**默认语言锁定 en**

- `src/battery_analysis/i18n/__init__.py` — `initialize_default_locale()`：不再调用 `detect_system_locale()`，直接 `set_locale("en")`。
- `src/battery_analysis/i18n/language_manager.py` — `_initialize_settings()`：无保存偏好时默认 `"en"`。
- `src/battery_analysis/i18n/locale_utils.py` — 保留 `detect_system_locale`/`resolve_locale_code`（仍被 i18n 内部与测试使用），不再作为默认入口。

**`_()` 调用规范化**

全库把 `_("key", "中文/英文 fallback")` 改为 `_("英文文本")`（msgid 即英文）。受影响文件：`dialog_manager.py`、`menu_manager.py`、`preferences_dialog.py`、`config_dialog.py`、`main_window.py` 及其余所有双参调用点。

**重建 .po**

- `locale/en/LC_MESSAGES/messages.po` — msgid = 英文文本，msgstr = 同英文（identity）。
- `locale/zh_CN/LC_MESSAGES/messages.po` — msgid = 英文文本，msgstr = 中文译文。
- `SimplePOTranslator` 解析逻辑不改。

**硬编码中文 → 英文**（界面 + 日志，不含 docstring/注释）

- `src/battery_analysis/main/application_initializer.py` — 崩溃/启动错误对话框标题与文案（"应用程序错误"、"很抱歉，应用程序遇到了一个问题"）改用 `_()`。
- `src/battery_analysis/main/battery_chart_viewer.py:196-197` — "数据更新" 消息框。
- `src/battery_analysis/main/ui_components/dialog_manager.py` — `show_user_manual`/`show_online_help` 内联中文字符串、错误恢复对话框。
- `src/battery_analysis/main/ui/language_handler.py:86` — `"状态:就绪"`（该文件本身将删除，见第 3 节，消息迁入 `main_window`）。
- 全库 `logger.*` 中文消息 → 英文。

**测试**

- 更新 `tests/battery_analysis/i18n/test_i18n.py` 以匹配默认 `en` 与新翻译契约。

### 第 2 节：设置/配置

**入口不变**：菜单 `Configuration`（ConfigDialog）与 `Preferences`（PreferencesDialog）两个入口保持。

**Configuration → master-detail 布局**

`src/battery_analysis/main/ui_components/config_dialog.py`：

- 顶部 `QTabWidget` 改为左侧分类导航（Battery / Test / Equipment）+ 右侧 `QStackedWidget`，兑现 docstring 的 master-detail 意图。
- 窗口尺寸控制：收起为常规对话框尺寸（约 700×560），不再需要 960×720。

**电池页逐条化**

- 分组：**Test Data Dictionary**（Battery Types 只读、Rules、Specifications 只读派生、Manufacturers、Construction Methods、Specification Methods）+ **Test Parameters**（Pulse Currents、Cut-off Voltages）。
- 列表类（Manufacturers / Construction Methods / Specification Methods / Pulse Currents / Cut-off Voltages）沿用 row-based `QListWidget` + 增删按钮（现有 `_fill_list`/`_read_list` 模式）。
- **Rules**：大文本框改为 `QTableWidget`，列：`Specification | Pack | Capacity | Voltage | Method | Note`，逐条可编辑，提供增删行。
- **Specifications**：从 Rules 派生（复用 `derive_specifications` 分类逻辑：CR → Coin Cell，CP/CF → Pouch Cell，容量兜底阈值 800），只读展示，移除编辑按钮。
- **Battery Types**：只读（类型是固定枚举）。

**去重**：`_BatteryConfigPage` 与 `_TestConfigPage` 的 `_fill_list`/`_read_list` 合并到共享基类或模块级辅助函数。

**数据层**

- `src/battery_analysis/utils/config_defaults.py` — `specifications` 硬编码默认值改为 `{}`（由 rules 派生）；修正 `CP305050` 规则容量 `20 → 2000`（既有 rules-to-specs 设计指出）。
- `src/battery_analysis/utils/config_schema.py` — 已确认 `specifications: Dict[str, List[str]] = field(default_factory=dict)`，无需改动。
- `collect_data()` 保存时由 rules 计算 specifications 并写回。

**Preferences 清理**

- 主题/字体选项与 `main_window` 现有设置共用同一 key（消除双份配置）。
- 删除 auto-save 相关选项（无消费者）。
- `src/battery_analysis/i18n/preferences_dialog.py` → 迁入 `src/battery_analysis/main/ui_components/`（其 `IConfigPathProvider` 接口与 `config_path_provider.py` 合并），更新 `dialog_manager.py` 等导入。

### 第 3 节：框架清理

**删除 clean-architecture 死骨架**

- 删除 `src/battery_analysis/application/usecases/*`（3 文件）、`src/battery_analysis/infrastructure/*`（2 文件）、`src/battery_analysis/domain/services/battery_analysis_service.py`、`src/battery_analysis/domain/repositories/*`（4 文件）、`src/battery_analysis/domain/entities/{battery,configuration,test_profile,test_result}.py`。
- **保留** `src/battery_analysis/domain/entities/test_info.py`（6 个活跃文件使用）。

**删除配套测试（15 个）**

- `tests/battery_analysis/domain/entities/{test_battery,test_configuration,test_test_profile,test_test_result}.py`
- `tests/battery_analysis/domain/repositories/{test_battery_repository,test_configuration_repository,test_test_profile_repository,test_test_result_repository}.py`
- `tests/battery_analysis/domain/services/test_battery_analysis_service.py`
- `tests/battery_analysis/application/usecases/{test_analyze_data_use_case,test_calculate_battery_use_case,test_generate_report_use_case}.py`
- `tests/battery_analysis/infrastructure/repositories/test_battery_repository_impl.py`
- `tests/battery_analysis/infrastructure/services/test_battery_analysis_service_impl.py`
- `tests/battery_analysis/main/services/test_application_service.py`
- `tests/manual/test_cache_mechanism.py`（已损坏，导入路径不存在）

**删除 i18n 死链**

- 删除 `src/battery_analysis/main/ui/language_handler.py`（LanguageHandler）——其 `_on_language_changed` 的窗口标题/状态栏更新逻辑合并进 `main_window._on_language_changed`；`language_initialization_step.py` 移除对它的实例化。
- 删除 `src/battery_analysis/main/services/i18n_service.py`（I18nService，从未被导入）。

**删除其他死代码**

- 删除 `src/battery_analysis/main/controllers/visualizer_controller.py`（container.py 实例化但从未调用），同步更新 `container.py` 与 `controllers/__init__.py`。
- 删除 `src/battery_analysis/main/services/application_service.py`（仅测试引用）。

**配置访问统一**

- `main_window` 中绕过 `ConfigService` 直接使用 `config_utils`/`QSettings` 的路径读取与重载逻辑改为经 `ConfigService`（见 `src/battery_analysis/main/services/config_service.py`）。
- `config_manager.py` 的 `_INI_TO_JSON_KEY` 映射保留（INI 兼容层仍被消费）。

### 第 4 节：风险控制与验证

1. **删除前基线**：运行全量测试，确认当前绿。
2. **import-graph 审计**：删除每个文件前确认无活跃引用（`grep` 全库 import / 引用）。
3. **删除后验证**：再次全量测试 + 手动冒烟（启动、打开 Configuration、编辑 Rules 刷新 Specifications、切换语言、保存配置）。
4. **明确放弃**：本次删除后项目不再保留 clean-architecture 迁移基础；仅 `test_info.py` 实体保留。

## 文件改动清单

**新增**
- `docs/superpowers/specs/2026-08-12-english-default-settings-framework-design.md`（本文件）

**修改**
- `src/battery_analysis/i18n/__init__.py`、`language_manager.py`、`translator.py`（如需）
- `src/battery_analysis/main/ui_components/config_dialog.py`（master-detail + 逐条化）
- `src/battery_analysis/main/ui_components/dialog_manager.py`、`menu_manager.py`、`ui_manager.py`（如有）
- `src/battery_analysis/main/main_window.py`、`application_initializer.py`、`battery_chart_viewer.py`
- `src/battery_analysis/main/initialization/steps/language_initialization_step.py`
- `src/battery_analysis/main/services/config_service.py`
- `src/battery_analysis/main/controllers/container.py`、`controllers/__init__.py`
- `src/battery_analysis/utils/config_defaults.py`
- `locale/en/LC_MESSAGES/messages.po`、`locale/zh_CN/LC_MESSAGES/messages.po`
- `tests/battery_analysis/i18n/test_i18n.py`
- 其余 `_("key", "fallback")` 双参调用点

**迁移**
- `src/battery_analysis/i18n/preferences_dialog.py` → `src/battery_analysis/main/ui_components/preferences_dialog.py`（含 `IConfigPathProvider` 合并）

**删除**
- `src/battery_analysis/application/`、`infrastructure/`、`domain/services/`、`domain/repositories/`、`domain/entities/{battery,configuration,test_profile,test_result}.py`
- `src/battery_analysis/main/ui/language_handler.py`、`main/services/i18n_service.py`、`main/services/application_service.py`、`main/controllers/visualizer_controller.py`
- 15 个配套测试文件

## 已知问题（本次不处理）

- 初始化管线（12 类 step 管线）复杂度
- 服务定位器（container.py）式依赖注入
- 数据流中的魔法值/硬编码业务常量
- `config_service.py` 中硬编码的 Windows 路径约定

## 未改动

- `config.json` 结构、key 命名与 schema
- `SimplePOTranslator` / gettext 解析逻辑
- 日志框架
- docstring 与代码注释（保持中文）
