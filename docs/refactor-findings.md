# 大文件拆分重构 — 问题与优化发现汇总

> 分支：`refactor/split-large-files`
> 规则：**本阶段只做拆分（行为不变）**。拆分过程中发现的可疑点、潜在 bug、可优化项，
> 全部记录到下面的清单里，等所有拆分完成、测试全绿之后，再逐条修复。
> 每条记录：编号 / 位置 / 问题描述 / 严重度 / 状态（open / fixed）。

## 状态总览

| # | 位置 | 问题 | 严重度 | 状态 |
|---|------|------|--------|------|
| 1 | `main/factories/battery_chart_viewer_wrapper.py` `embed_to_widget` 与 `show_figure` | 两方法中「XML路径 → 定位 analysis results 目录 → 找最新子目录 → 找 Info_Image.csv → load_data」这一整段约 80 行逻辑**几乎完全重复**，且 `embed_to_widget` 版本缺少 `show_figure` 里的几处兜底（父目录不存在检查、无子目录时直接在根目录找 csv、找不到时遍历其他子目录）。两份实现已经**行为不一致** | 高 | open |
| 2 | `main/factories/battery_chart_viewer_wrapper.py` 两方法内 | 方法体内 `import os`（模块顶部已 import os），冗余 import | 低 | open |
| 3 | `main/factories/battery_chart_viewer_wrapper.py` `embed_to_widget` / `show_figure` | 捕获 `(ImportError, TypeError, ValueError, OSError)` 而内部对 analysis results 的处理用了宽泛 `except Exception`，异常策略不统一；且导入错误被当成运行时错误吞掉 | 低 | open |
| 4 | `main/factories/visualizer_factory.py` `create_visualizer` | 捕获 `ImportError` 等但 `visualizer_class(**kwargs)` 抛出的其它异常（如 KeyError）会直接穿透，错误处理不完整 | 低 | open |
| 5 | `main/visualization/viewer_controls.py` `_add_menu_bar` | 第一个 `except ImportError as e: raise ImportError(...)` 之后紧跟 `except (ImportError, AttributeError, ...) as e:` —— 后者的 `ImportError` 分支**永远不可达**（dead code），异常分类自相矛盾 | 中 | open |
| 6 | `main/visualization/hover_controls.py` `_add_hover_functionality`（线性 O(n) 扫描）vs `_add_hover_functionality_kdtree`（KDTree 加速） | 同一悬停功能两套并行实现，约 67 行 + 144 行；kdtree 版失败时回退到线性版。长期只应保留一套（KDTree 版），或抽出共享的坐标换算/标注更新逻辑 | 中 | open |
| 7 | `main/visualization/filter_controls.py` `_add_filter_button` 与 `create_filter_checkbox` | 「过滤/未过滤切换」的可见性联动逻辑两份（matplotlib 按钮形态 86 行 + QCheckBox 形态 66 行），切换规则若改动需同步改两处，易漂移 | 中 | open |
| 8 | `main/visualization/viewer_controls.py` `_open_file_dialog` | 日志与异常处理过度（方法内 10+ 条 logger 调试日志），Qt 对话框失败后仅打日志、`data_dir` 为 None 时无用户可见提示 | 低 | open |
| 9 | `main/visualization/*.py`（本次拆分产物） | 拆分后 `ButtonFactoryMixin`/`FilterControlsMixin` 等子 Mixin 之间通过 `self` 隐式耦合（子 Mixin 单独使用会 AttributeError），且各文件无 `TYPE_CHECKING` 依赖声明，IDE 无法静态看出依赖关系 | 低 | open |

## 详细记录
