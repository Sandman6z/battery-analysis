# 大文件拆分重构 — 问题与优化发现汇总

> 分支：`refactor/split-large-files`
> 规则：**本阶段只做拆分（行为不变）**。拆分过程中发现的可疑点、潜在 bug、可优化项，
> 全部记录到下面的清单里，等所有拆分完成、测试全绿之后，再逐条修复。
> 每条记录：编号 / 位置 / 问题描述 / 严重度 / 状态（open / fixed）。

## 状态总览

| # | 位置 | 问题 | 严重度 | 状态 |
|---|------|------|--------|------|
| 1 | `main/factories/battery_chart_viewer_wrapper.py` `embed_to_widget` 与 `show_figure` | 两方法中「XML路径 → 定位 analysis results 目录 → 找最新子目录 → 找 Info_Image.csv → load_data」这一整段约 80 行逻辑**几乎完全重复**，且 `embed_to_widget` 版本缺少 `show_figure` 里的几处兜底（父目录不存在检查、无子目录时直接在根目录找 csv、找不到时遍历其他子目录）。两份实现已经**行为不一致** | 高 | fixed |
| 2 | `main/factories/battery_chart_viewer_wrapper.py` 两方法内 | 方法体内 `import os`（模块顶部已 import os），冗余 import | 低 | fixed |
| 3 | `main/factories/battery_chart_viewer_wrapper.py` `embed_to_widget` / `show_figure` | 捕获 `(ImportError, TypeError, ValueError, OSError)` 而内部对 analysis results 的处理用了宽泛 `except Exception`，异常策略不统一；且导入错误被当成运行时错误吞掉 | 低 | open |
| 4 | `main/factories/visualizer_factory.py` `create_visualizer` | 捕获 `ImportError` 等但 `visualizer_class(**kwargs)` 抛出的其它异常（如 KeyError）会直接穿透，错误处理不完整 | 低 | open |
| 5 | `main/visualization/viewer_controls.py` `_add_menu_bar` | 第一个 `except ImportError as e: raise ImportError(...)` 之后紧跟 `except (ImportError, AttributeError, ...) as e:` —— 后者的 `ImportError` 分支**永远不可达**（dead code），异常分类自相矛盾 | 中 | fixed |
| 6 | `main/visualization/hover_controls.py` `_add_hover_functionality`（线性 O(n) 扫描）vs `_add_hover_functionality_kdtree`（KDTree 加速） | 同一悬停功能两套并行实现，约 67 行 + 144 行；kdtree 版失败时回退到线性版。长期只应保留一套（KDTree 版），或抽出共享的坐标换算/标注更新逻辑（已抽出 4 个模块级共享函数） | 中 | fixed |
| 7 | `main/visualization/filter_controls.py` `_add_filter_button` 与 `create_filter_checkbox` | 「过滤/未过滤切换」的可见性联动逻辑两份（matplotlib 按钮形态 86 行 + QCheckBox 形态 66 行），切换规则若改动需同步改两处，易漂移 | 中 | fixed（抽出共享 `_apply_filter_mode`；并修复 checkbox 路径漏更新 `filter_button_state["active"]` 导致悬停永远扫 Filtered 曲线） |
| 8 | `main/visualization/viewer_controls.py` `_open_file_dialog` | 日志与异常处理过度（方法内 10+ 条 logger 调试日志），Qt 对话框失败后仅打日志、`data_dir` 为 None 时无用户可见提示 | 低 | open |
| 9 | `main/visualization/*.py`（本次拆分产物） | 拆分后 `ButtonFactoryMixin`/`FilterControlsMixin` 等子 Mixin 之间通过 `self` 隐式耦合（子 Mixin 单独使用会 AttributeError），且各文件无 `TYPE_CHECKING` 依赖声明，IDE 无法静态看出依赖关系 | 低 | open |
| 10 | `utils/writers/excel_report_writer.py` `write` | 两个 workbook（`wbResult`/`wbSample`）创建后无 `try/finally` 保护，中间任一步抛异常都会**不关闭工作簿**，产生损坏/空的 xlsx 文件；应改用 with 语句或 try/finally | 中 | fixed |
| 11 | `utils/writers/excel_report_writer.py` `write` | `wsOverview is None` / `wsResult is None` 检查：`xlsxwriter.Workbook.add_worksheet` 失败时抛的是 `WorksheetNameContainsInvalidCharsException` 等异常，几乎不会返回 None，这两段防御代码实际不可达 | 低 | open |
| 12 | `utils/writers/word_report_writer.py` `write` | 结尾用 `logging.info(...)`（root logger）而非模块级 `logger`，与全文件其他日志调用不一致 | 低 | open |
| 13 | `utils/writers/word_report_writer.py` `__init__` | `__init__` 133 行，承担了过多职责（路径计算、图片占位符列表生成、电池类型匹配、替换字符串数组构造）；且函数内局部 import `from battery_analysis.utils.constants import COLOR_NAME` | 低 | open |
| 14 | `main/window_actions.py` `show_config_dialog` | 对话框接受后 `combo = getattr(self, f"comboBox_{name}")` **无默认值**：控件名与 `saved` 字典键不一致或控件未创建时直接 AttributeError，且发生在配置已保存之后（保存成功但恢复现场崩溃） | 中 | fixed |
| 15 | `main/window_init.py` `_deferred_init`（103 行）、`main/window_texts.py` `refresh_texts`（79 行） | 两个长函数：前者含阶段 1-4 初始化管线 + 内联阶段注释，后者为集中式文本刷新，均未拆子步骤；改动任一阶段都需整体阅读 | 中 | fixed（`_deferred_init` 拆为 `_prepare_application` / `_run_initialization_pipeline` / `_complete_launch_phase` 三步；`refresh_texts` 改为 `_GROUP_TITLE_TEXTS` / `_WIDGET_TEXTS` 数据表驱动，27 条目与旧实现双向 diff 一致。注意：进度对话框刷新必须内联在 `refresh_texts` 内——测试夹具为 MagicMock，经 self 调子方法只会落到自动 Mock 上） |
| 16 | `main/window_init.py` / `main/window_actions.py` | 函数内局部 import 共 9 处（`_deferred_init` 内 6 处、`show_config_dialog`/`reload_configuration` 内 3 处），用于规避循环导入；拆分后本可上移到模块顶，属拆分遗留的可清理项 | 低 | open |
| 17 | `main/window_actions.py` `set_theme`/`toggle_statusbar` 前 | 分节注释写着「报告相关方法」，但其下方法实际是主题/状态栏开关（原文件沿袭下来的错标注释，搬移时一并带过来） | 低 | open |
| 18 | `main/window_actions.py` `reload_configuration` / `on_preferences_applied` 等 | 多处 `hasattr(self, "config_manager")` 形式的守卫：依赖缺失时**静默跳过**初始化/刷新，无任何日志，故障表现为“配置没生效”但日志无痕 | 低 | open |
| 19 | `main/business_logic/validation_manager.py` `__init__` | `main_window=None` 有默认值，但几乎所有方法（`validate_version`、`checkinput`…）都直接 `self.main_window.xxx` —— 传 None 时不会在构造期报错，而是到第一次校验时 AttributeError；应去掉默认值或在构造期断言 | 中 | fixed |
| 20 | `main/business_logic/validation_feedback.py` `checkinput`（173 行）、`_apply_field_errors`（79 行） | 本次拆出的两个最长函数：checkinput 内含完整的“取值→逐字段校验→高亮→汇总”线性流程，未拆子步骤；_apply_field_errors 里字段类型分支（单选/文本/表格）重复着色代码 | 中 | fixed（checkinput 拆为 `_report_field_validation_failure` / `_check_legacy_fields`（_LEGACY_FIELD_CHECKS 数据表驱动）/ `_finalize_check_result` 三段；15 组控件取值 + 验证器失败路径与旧实现逐字段样式/状态栏文本等价验证通过；文件 421→298 行） |
| 21 | `main/business_logic/validation_manager.py` `self.logger = logging.getLogger(__name__)` | logger 名硬编码为当前模块名，拆分后 mixin 方法的日志全部记在 `validation_manager` 名下，无法从日志区分具体子模块（同理适用于此前拆出的 window_*/interaction_*） | 低 | open |
| 22 | `main/visualization/hover_controls.py` | `pyproject.toml` 依赖里**没有 scipy**，`_build_kdtree_index` 恒 ImportError 返回 `(None, None)`；而 `_add_hover_functionality_kdtree` 拿到空索引后 `_find_nearest_point_kdtree` 恒返回 None，**并不会真的回退到线性扫描**（日志 “falling back to linear search” 是谎报），导致 `embed_to_widget` 路径的悬停提示完全失效 | 高 | fixed（索引为 None 时真正回退到 `_find_nearest_point_linear`，并加 unavailable 标记避免每次悬停重建） |

## 详细记录

### #1 + #2 — battery_chart_viewer_wrapper 加载逻辑去重（已修复）

**改动**：抽出两个私有方法，两处调用共用一套实现。

- `_load_data_at(data_path, success_msg)` — 统一的「set_data_path → load_data → 置 loaded_data → 打日志」四步，替代原来 4 份重复的内联代码。
- `_load_data_from_xml_path(xml_path)` — 完整的 XML → analysis results → 最新子目录 → Info_Image.csv 定位链，以原本更完整的 `show_figure` 版本为准（含三处兜底：父目录不存在检查、无子目录时直接在根目录找 csv、最新目录没有 csv 时遍历其他子目录）。

**行为差异说明**：`embed_to_widget` 现在获得了 `show_figure` 的全部兜底分支（此前缺失），即行为向更完整的一方**对齐**；`show_figure` 行为不变。两者日志话术保持原样，便于与历史日志比对。`_load_data_at` 的 `success_msg` 参数沿用原三条不同文案，未合并文案。

**连带**：方法体内的重复 `import os` 随替换一并消失（#2），模块顶部的 `import os` 保留。
