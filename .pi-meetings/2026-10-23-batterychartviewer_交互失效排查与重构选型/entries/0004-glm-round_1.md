# GLM (Round 1): 缩放拖动失效排查：代码已证实无自研实现，疑点集中在工具栏缺失与视图重置

# GLM（务实落地）— Round 1：BatteryChartViewer 缩放/拖动失效排查

## 0. 排查方法与边界声明
- 仅静态阅读仓库代码 + grep 全仓检索，未修改任何文件，未安装工具，未全量建图谱，未启动其他子代理。
- **本 worker 没有可用的 shell 工具，无法执行 `git log -S 'NavigationToolbar2QT'` 等命令**；`.git/objects` 已打包（zlib 压缩），grep 对 packed object 的命中不可信。因此"缩放功能是否曾被代码删除"**只能标记为待验证**，下面给出可执行的验证命令。
- 无法启动 GUI，一切交互行为结论需桌面验证，已逐条标注。

## 1. 已证实事实（有路径+行号）

### 1.1 代码库中不存在任何自定义缩放/拖动实现
- 全仓 grep：`SpanSelector` / `RectangleSelector` / `matplotlib.widgets` **零命中**（src/ 与 tests/ 均无）。
- 全部 `mpl_connect` 事件只有 3 类：hover 的 `motion_notify_event`（`src/battery_analysis/main/visualization/hover_controls.py:119`、`:335`）、自绘按钮的 `motion_notify_event`+`button_press_event`（`button_widgets.py:140-141`）。**没有任何 pan/zoom/滚轮/按键绑定的自研代码**。
- `set_xlim/set_ylim` 命中均为布局用途（按钮轴 `battery_selection.py:64,96`、`filter_controls.py:74`、`viewer_controls.py:48`）或纵轴自适应 `_adjust_y_axis_range`（`figure_builder.py:299-330`），不是缩放功能。

### 1.2 全仓无 NavigationToolbar2QT 实例化
- `NavigationToolbar` 全仓仅 3 处：QSS 样式 `src/battery_analysis/ui/styles/battery_analyzer.qss:678-679`（只是美化，不隐藏：padding 6px、圆角，无 height:0）、`battery_chart_viewer.py:442` 的 docstring、`battery_analyzer.qss:830` 的 `FigureCanvasQTAgg` 样式。**没有任何 Python 代码创建 matplotlib 工具栏。**
- 无 `rcParams["toolbar"]`、无 matplotlibrc 文件禁用工具栏（全仓 grep 证实）。

### 1.3 两种渲染模式的本质差异（关键）
- **嵌入模式** `embed_to_widget`（`battery_chart_viewer.py:435-585`）：裸建 `Figure` + `FigureCanvasQTAgg`（`:457-462`、`:490`），直接塞进 parent 的 QVBoxLayout——**这种模式下缩放/拖动从来就没有**，因为没有工具栏、没有等价事件绑定。这是"没做"，不是"做不了"。但注意：**当前生产代码没有任何调用方调用 `wrapper.embed_to_widget`**（全仓 grep 仅 wrapper 自身 `factories/battery_chart_viewer_wrapper.py:169-195` 转发 + 测试 `tests/battery_analysis/main/test_battery_chart_viewer.py:125` 调用），所以嵌入模式目前不是用户看到的主路径。
- **独立窗口模式（实际生产入口）**：菜单 `ui_components/menu_manager.py:156`（action 创建于 `ui_builder.py:154`）→ `visualization_manager.py:39 run_visualizer` → `:64 _run_visualizer_standalone` → `factories/battery_chart_viewer_wrapper.py:208 show_figure` → `battery_chart_viewer.py:188 plt_figure` → `plt.figure(figsize=(15,6))`（`figure_builder.py:29`）+ `plt.ion()`/`plt.show(block=False)`（`battery_chart_viewer.py:318-319`）。
- ** pyplot + QtAgg 的 FigureManager 默认自带 NavigationToolbar2QT**，且本仓没有任何代码禁用它。推论：独立窗口的工具栏**理论上应该还在**——这与"缩放消失"的症状矛盾，是本案最大疑点（见 §2）。

### 1.4 测试覆盖现状
- `tests/battery_analysis/main/test_battery_chart_viewer.py`（141+ 行）覆盖：空图/加载失败/数据错误/菜单栏/File-Open 重载/嵌入模式区分，**没有任何一条断言缩放、拖动、工具栏存在性**。
- `test_menu_manager.py:65-71` 的 `zoom_in/zoom_out/reset_zoom` 测的是**主窗口字体缩放**（`menu_manager.py:205-225`，只改 `QFont.pointSize`），与图表缩放完全无关——不要被名字误导。
- 结论：**缩放功能自始至终零测试覆盖**，回归无从拦截。

### 1.5 CHANGELOG 线索
- `CHANGELOG.md:189`（v3.1.0 破坏性变更）："**移除顶部 toolbar**：菜单栏已有相同功能，工具栏冗余"。上下文（v3.1.0 节）指主窗口工具栏 + "纯代码构建主窗口 UI"。**无法从现有代码确证那次清理是否连带删掉了图表查看器的工具栏代码**（需要 git 历史，见 §4）。
- `CHANGELOG.md:449`（更早）："refactor(ui): 将缩放功能移至menu_manager" —— 从 test_menu_manager 可证实这指的也是主窗口字体缩放，不是图表缩放。

### 1.6 视图会被强制重置的代码（体验层面的强候选）
- 每次绘制/重绘都会执行 `ax.axis(self.listAxis)`（`figure_builder.py:37` 独立模式、`battery_chart_viewer.py:500` 嵌入模式），`listAxis` 在 `battery_chart_viewer.py:130-134` 初始化、`:174` 与 `data_loader.py:206-209` 重设，等价于每次都把 xlim/ylim 钉回 `[xmin, maxXaxis, ymin, ymax]`。
- 过滤切换 `_apply_filter_mode`、电池按钮等交互会重建 figure（`battery_chart_viewer.py:309-316` 多个 `_add_*` 调用，旧 fig 在 `:252-260` 被 `plt.close`）。**即使用户成功缩放，任何一次切换交互后视图必然回到初始范围**——用户主观感受即"拖了没用/被弹回去"。

## 2. 推断（按可能性排序，均需 GUI/历史验证）
1. **"缩放消失"最可能是"从未以显式代码存在 + 视图重置让残存工具栏显得失效"的组合**：独立窗口若工具栏仍在，则症状应是"能缩放但一切换就被重置"；若独立窗口工具栏也彻底不见了，则必须怀疑打包环节——`build.py:182-188` 排除了大量 matplotlib 后端（qt4/qt5/wx/gtk/webagg/nbagg/pgf），**未排除 backend_qtagg，理论上打包完整**，但 PyInstaller 对 `matplotlib.backends.backend_qtagg` 的 toolbar 子模块隐式导入收集是已知雷区，需在打包版 exe 里实测。
2. 若用户对比的是"旧版本 exe vs 新版本 exe"，v3.1.0 的 toolbar 清理是唯一有据可查的删除动作（CHANGELOG.md:189），是否波及图表窗口待 git 确证。
3. `battery_chart_viewer.py:195-199, 449-453` 反复修 matplotlib 3.10+ backend 大小写问题，说明近期动过 backend 相关代码，回归窗口期在此附近。

## 3. 是否为 Matplotlib 局限？
- **不是**。pyplot/QtAgg 独立窗口原生支持：框选缩放（zoom rect）、pan 拖动、Home/Back/Forward、zoom/pan 的 x-only/y-only 模式（工具栏按钮 + 键盘修饰键）、缩放状态下拖动单个轴 spine 也可改 limit。这些都随 NavigationToolbar2QT 免费获得。
- matplotlib 真正的局限只有一点：**没有"不进工具栏模式、直接用鼠标手势拖单条轴"的默认行为**——如果"横轴纵轴单独拉动"指的是这个手势且旧版确实有过，那它必然曾是自定义实现（但全仓 grep 不到任何痕迹，我倾向它从来就是工具栏行为，此点标记为待 GUI 验证）。
- 嵌入模式没工具栏是"没接"，加 `NavigationToolbar2QT(canvas, parent)` 十几行就能补齐。

## 4. 待验证清单（按优先级，含可执行命令）
1. **git 历史**：`git log --oneline -S 'NavigationToolbar2QT' -- src/`、`git log --oneline -S 'SpanSelector' -- src/`、`git show v3.1.0 --stat`（对照 CHANGELOG.md:189）。本 worker 无 shell 无法执行。
2. **GUI 实测（源码运行）**：菜单 → BatteryChartViewer，检查独立窗口底部是否有工具栏；有则试 zoom/pan 并立刻切换一次过滤按钮，验证 §1.6 的"视图重置"症状。
3. **GUI 实测（打包 exe）**：同上，验证 build.py 打包是否丢 toolbar 模块。
4. 问用户两个关键问题：症状出现前后的版本号？"消失"指按钮不见了，还是点了没效果/被弹回？

## 5. 最小恢复补丁方案（不实际改码，供评审）
- **补丁 A（首选，~15 行）**：在 `viewer_controls.py:65 _add_menu_bar` 或 `battery_chart_viewer.py:318 plt.show` 之前加防御性检查：`toolbar = fig.canvas.manager.toolbar`；若为 None，则 `from matplotlib.backends.backend_qtagg import NavigationToolbar2QT`，`window.addToolBar(Qt.ToolBarArea.TopToolBarArea, NavigationToolbar2QT(canvas, window, True))`。恢复独立窗口缩放/拖动，零新依赖。
- **补丁 B（~10 行）**：视图重置问题——`figure_builder.py:37` 的 `ax.axis(self.listAxis)` 改为仅首次绘制设置（或改用 `ax.set_xbound/set_ybound` 不清 user navigation），并定义明确策略：交互后切换过滤时**保留用户视图**或**显式复位**（二选一，写进 CHANGELOG）。
- **补丁 C（可选，~10 行）**：`battery_chart_viewer.py:462` 嵌入模式在 layout 里 `layout.addWidget(NavigationToolbar2QT(canvas, parent_widget))` 放在 canvas 之上，为未来嵌入场景兜底。
- **配套测试（offscreen，仿 test_battery_chart_viewer.py 的 qapp fixture）**：`assert fig.canvas.manager.toolbar is not None`；缩放后模拟 `toolbar.zoom()` + `canvas.button_press_event` 再断言 `ax.get_xlim()` 变化；切过滤后按选定策略断言 xlim。

## 6. 分阶段重构建议
- **阶段 0（半天）**：§4 验证清单跑完，锁定根因是"工具栏缺失"还是"视图重置"或两者。
- **阶段 1（1-2 天）**：补丁 A+B + 测试 + CHANGELOG。收益/成本比最高，先交付。
- **阶段 2（2-3 天，可选）**：把 `current_fig` 视图状态管理收敛到 figure_builder 一处，消除 figure_builder 与 battery_chart_viewer 两份近似重复的绘制路径（wrapper 注释 `factories/battery_chart_viewer_wrapper.py:56` 已自认两份重复）。
- **阶段 3（不建议现在做）**：换库。理由见 §7。

## 7. 替代库对比（务实视角）
| 方案 | 缩放/拖动/轴单独拉 | 迁移成本 | 结论 |
|---|---|---|---|
| matplotlib + NavigationToolbar（补丁 A/B） | 全部满足（含 x/y-only） | ~2 天 | **推荐，先走这条** |
| pyqtgraph | ViewBox 原生，性能最佳（万点级 hover 不卡） | 重写 hover/KDTree/按钮/过滤全链路，2-3 周 + 回归 1187 项 | 数据量确实现性能瓶颈时再做 |
| QtCharts (PyQt6 自带) | rubberBand 缩放+轴拖动原生 | 同上量级，且中文样式体系要重接 | 无明显优势 |
| plotly/Web | 功能最全 | 打包体积 +~100MB、离线依赖、打包雷区 | 不推荐 |

核心判断：**当前病根不是库的能力，是工具栏没接/视图被重置 + 零测试**。换库解决不了零测试问题，先修后议。

## 8. 残余风险与诚实声明
- git 历史未经核验（无 shell 工具），"是否曾被删除"结论可能被 `git log -S` 推翻。
- 所有"独立窗口工具栏应该还在"的判断基于 matplotlib 默认行为推理，未实机启动验证。
- 用户实际看到的入口可能是打包 exe 或旧版本，与本仓 HEAD 行为可能不一致。
- `plt.ion()` 全局开启（`battery_chart_viewer.py:42`）与主窗口事件循环的交互未深查，若 GUI 实测发现 hover 与 pan 事件冲突，需回到 `hover_controls.py:258` 的 on_hover 节流逻辑复查。