# Meeting: BatteryChartViewer 交互失效排查与重构选型
> Created: 2026-10-23T01:05:01.830Z
> Type: Brainstorming (3 rounds)

---

## GPT (Round 1): 从入口与能力契约定位交互缺口：先恢复导航链路，再以指标决定替换

## 一、结论与证据等级

**战略判断：优先保留 Matplotlib 修复交互契约，不宜把当前问题直接归因为库的局限并全面重写。** 当前源码明确具有曲线、过滤、电池选择、悬停能力，却没有与帮助文字相匹配的自定义滚轮缩放、直接拖动、右键复位实现。独立窗口与嵌入窗口不是同一条导航链路，不能拿嵌入模式缺 toolbar 解释主入口的一切现象。

本轮仅只读检查仓库；没有运行 GUI、pytest、构建或安装工具，没有查历史提交。因此能证明“当前代码有什么”，不能证明“哪个历史提交删除了功能”，也不能确认用户实际看到的工具栏状态。

## 二、实际入口与链路

### 已证实：当前主菜单走独立窗口，不走嵌入模式

1. `src/battery_analysis/main/ui_components/menu_manager.py:156` 将 `actionBatteryChartViewer.triggered` 连接到 `visualization_manager.run_visualizer`。
2. `src/battery_analysis/main/managers/visualization_manager.py:38-62` 明确选择独立窗口路径；`:64-88` 创建 `battery_chart` visualizer，再调用 `show_figure(data_path=...)` 或 `show_figure(xml_path=...)`。
3. `src/battery_analysis/main/factories/visualizer_factory.py:31-33,51-69` 注册并构造 `BatteryChartViewerWrapper`；wrapper 在 `battery_chart_viewer_wrapper.py:33-35` 创建 viewer，在 `:208-238` 最终调用 `self._viewer.plt_figure()`。
4. `src/battery_analysis/main/battery_chart_viewer.py:263-315` 初始化 Figure、绘制曲线；`:317-329` 添加过滤、电池选择、悬停、帮助文字；`:335-350` 执行非阻塞显示及 canvas 绘制。
5. 独立 Figure 由 `src/battery_analysis/main/visualization/figure_builder.py:24-35` 的 `plt.figure()` 创建，QtAgg 后端由 `battery_chart_viewer.py:31-32,200-208` 设置/校验。这条路径可以依赖 Matplotlib FigureManager 自动创建的标准工具栏，不能因为业务代码没显式导入 NavigationToolbar 就断言独立窗口没有工具栏。

### 已证实：嵌入路径是独立实现，导航装配缺口明确

`battery_chart_viewer.py:435-476` 直接创建 `Figure` 和 `FigureCanvasQTAgg`；`:541-550` 安装 Qt 选择控件和悬停；`:561-580` 保存引用、只向布局添加 canvas，并返回五元组 `(fig, canvas, filter_checkbox, scroll_area, battery_checkboxes)`。没有构建 NavigationToolbar。`:442` 的三元组 `(fig, canvas, toolbar)` 文档已与实际返回值脱节。

对 `src` 的检索没有发现 NavigationToolbar 类的实例化，也没有发现 `scroll_event`、`button_release_event`、`xlim_changed`、`ylim_changed` 注册。QSS 的 `src/battery_analysis/ui/styles/battery_analyzer.qss:678-679` 虽有 NavigationToolbar 样式，但样式不是功能实现。当前仓库可见调用关系里，嵌入方法主要由 wrapper 提供，主菜单未使用它。

## 三、交互能力现状清单

| 能力 | 当前证据 | 判断 |
|---|---|---|
| 曲线绘制、初始坐标范围 | `figure_builder.py:35-40,55-86` | 已存在 |
| 过滤/原始曲线切换 | `filter_controls.py:22-57,59-125` | 已存在，主要修改可见性和标题后 draw_idle |
| 电池选择 | `battery_chart_viewer.py:321-323,541-543` | 两种窗口均有装配入口；本轮未逐项 GUI 验证 |
| 悬停 | `hover_controls.py:119,335` 连接 motion_notify_event；独立/嵌入分别安装普通与 KDTree 版本 | 已存在，不等价于平移 |
| 图内按钮点击 | `button_widgets.py:118-141` | 已存在，只处理按钮区域，不是主图导航 |
| 滚轮缩放 | 帮助文字有承诺，源码检索无 scroll_event 处理 | 业务自定义实现当前缺失 |
| 不启用工具栏即直接拖动平移 | 无相应 press/move/release 导航状态机 | 自定义实现当前缺失；标准 toolbar 的 Pan 模式另论 |
| 右键复位 | `viewer_controls.py:35-39` 有帮助文字，未发现对应复位处理 | 提示与实现脱节 |
| 框选缩放、工具栏平移/Home | 独立模式使用 pyplot/QtAgg 默认 manager；业务不显式安装导航 | 依赖运行时 toolbar，需 GUI 确认 |
| 横轴/纵轴单独拉动 | 未见轴区域 hit-test 或轴向约束 controller | 若指“直接拖刻度/轴带”则当前未实现；若指标准 Pan/Zoom 的 x/y 约束，则需启用相应模式验证 |

`viewer_controls.py:27-39` 原样显示“Scroll to zoom, drag to pan, right-click to reset view”。这是最强的“用户预期仍在、应用事件实现没有对应装配”的证据。不能把一段提示文字当作功能仍然存在。

## 四、为何不工作：区分原因、疑点与非原因

### 已证实的结构性原因

- 自定义滚轮、直接拖动、右键复位没有注册链路；`InteractionControlsMixin` 目前只汇总按钮、过滤、电池选择、hover、菜单等 mixin（`interaction_controls.py:24-43`），没有导航 mixin。就当前快照而言，想要这些手势不能只调整样式或重绘。
- 嵌入模式只创建 canvas，没有显式导航工具栏，因此不能期待它自动具备独立 FigureManager 的标准 toolbar 导航。
- 主窗口菜单的 Zoom 不是图表 Zoom：`menu_manager.py:167-170,204-224` 的 zoom_in/out/reset_zoom 修改主窗口字体，完全不调用图表坐标范围。这是“缩放入口看起来仍在但作用对象不同”的具体脱节点。

### 已证实的重绘与状态行为

- 过滤切换主要 `set_visible` 后 `draw_idle`（`filter_controls.py:37-57`），没有每次把 xlim/ylim 重置。因此不能把普通过滤切换重绘说成导航被清零的已证实原因。
- `_adjust_y_axis_range` 读取原始和过滤数据并设置 ylim（`figure_builder.py:299-348`），由两个创建路径在初次绘曲线后调用。它不是 motion 事件里的持续 autoscale。
- 重新打开独立 viewer 会 `plt.close('all')`（`visualization_manager.py:68,97-103`）；`plt_figure()` 也会关闭旧 current_fig 后重建（`battery_chart_viewer.py:255-265`）。打开新目录则清理 Matplotlib 状态、关闭并重画（`viewer_controls.py:158-166`）。所以“重新打开/载入后视野丢失”有代码依据，和“同一窗口拖动完全失效”是不同问题。

### 推断与待验证

- 独立窗口的标准 Pan/Zoom 很可能仍可通过工具栏恢复使用；其可见性、模式、焦点及运行时 rcParams 尚未实测。源码未见隐藏/删除工具栏的调用，不应先宣称样式把它隐藏了。
- “以前可以直接拉 X/Y，现在不行”可能是历史自定义逻辑未接回，也可能是用户从某种工具栏模式切换到普通模式。没有版本历史和 GUI 证据，不能选择其中一种作为确定事实。
- KDTree hover 在原始数据坐标空间用距离，而不是屏幕像素距离（`hover_controls.py:151-156,189-196,311-325`）；放大后命中体验可能不稳定。它值得优化，但不是滚轮处理器缺失的解释。
- hover 回调没有显示的导航模式仲裁，移动时更新注释可能增加导航绘制负担；需要性能测量后再判断影响大小，不应直接说它吞掉了导航事件。

## 五、Matplotlib 是否有能力、恢复边界是什么

Matplotlib 的 QtAgg canvas 支持鼠标事件和坐标范围修改；标准 NavigationToolbar 支持平移、框选缩放与历史视图。其通常还支持导航中用 x/y 按键约束轴向，但具体版本、焦点和使用方式必须在本项目环境实测。`pyproject.toml:29` 允许 `matplotlib>=3.8.0,<4.0.0`，跨度较宽。

“无模式滚轮缩放”“直接拖刻度改变单轴”“右键恢复”并非应默认假定的标准 Matplotlib 交互契约，但可以通过 controller 实现。**默认没有某个产品手势，不等于绘图库不支持实现这个手势。** 当前证据足以支持恢复可行，不足以保证大数据量下满足所有延迟指标。

## 六、建议的修复与架构路线：先建立契约，再精确补链路

### 第一步：最小恢复，不引入新绘图库

1. 明确手势：滚轮以鼠标位置为锚缩放；主绘图区左拖平移；X/Y 轴带拖动只改变对应轴；复位恢复“加载数据后的合理视野”，而不是意外回到硬编码默认。明确右键是否未来要给上下文菜单使用。
2. 独立窗口先诊断 manager.toolbar 是否存在、可见、处于什么 mode；嵌入模式显式选择安装标准 toolbar，或安装自定义统一 controller。不要对两个入口盲目做同一个修补。
3. 两种创建路径在同一位置调用交互安装方法。先保留标准 toolbar 作为可发现的兜底，避免只留下不可见手势。
4. 如果自定义 controller 与 toolbar 共存，必须定义互斥状态，不能在 toolbar Pan/Zoom 活跃时又执行第二套拖动。
5. 保存 callback ids、定时器与状态，close 时统一 disconnect；避免重复安装事件。把主坐标轴与图内按钮辅助 Axes 清楚区分，防止手势在按钮区生效。

### 第二步：针对重复构建做局部重构

- 当前 `_initialize_figure` 与 `embed_to_widget` 有重复的轴布局、刻度、标题和绘图流程（`figure_builder.py:24-52` 对比 `battery_chart_viewer.py:494-520`），易出现“一边恢复、一边遗漏”。抽成共享构建过程，但保留独立/嵌入宿主差异。
- 分离三份状态：数据/可见性、视野/导航历史、宿主窗口资源。用单一交互 controller 管理 view limits 与模式，而不是继续把状态散到额外 mixin 属性里。
- 过滤、选择仅更新 Artist；数据变更才触发明确的 fit/reset 策略。统一 `draw_idle` 合并刷新，只有真实瓶颈再考虑 blit、降采样。
- hover 使用显示空间距离或相对轴尺度，并在导航中暂停；可见性变化时管理索引失效。避免先增加复杂缓存，再发现交互契约不清。

## 七、何时才值得换库

| 路线 | 合理采用条件 | 成本/风险 |
|---|---|---|
| 保留 Matplotlib | 现有 CSV 静态分析为主、需要高质量导出、修复后可达到响应指标 | 最低迁移成本；需要自己定义轴拖动/滚轮交互 |
| PyQtGraph | 核心是 Qt 桌面高频曲线、多通道/大样本，基准显示 Matplotlib 导航延迟无法接受 | Qt 融合较自然；仍需重做交互细节、标注、导出和回归，不是换包即完成 |
| Plotly + QtWebEngine | 产品明确需要浏览器式交互、Web 共享/报告，且接受浏览器运行时 | 打包体积、WebEngine 部署、Python-JS 状态同步成本明显；当前纯 Qt 桌面不宜只为恢复拖动而引入 |

决策不按“库新旧”，而按真实数据基准：加载时间、导航 p95 延迟、可见曲线数/点数、内存、中文显示、导出一致性、离线打包。可先给出产品候选目标（例如拖动反馈 p95 <50ms），但本轮没有测量，不能把候选值说成现状。先完成小修复和同数据基准，再决定是否做限定范围原型，不做空泛全量重写。

## 八、测试缺口与最小验收

已检查的 `tests/battery_analysis/main/test_battery_chart_viewer.py:1-180` 使用真实 offscreen Qt canvas，但聚焦空图、失败载入、菜单和恢复加载；其中 `:119-134` 验证嵌入空/错误图，没有导航验收。`tests/battery_analysis/main/visualization/test_interaction_controls.py:1-40` 只测试电池索引与过滤曲线选择。检索相关测试没有发现图表 scroll/pan/axis-lock 行为断言；`tests/.../ui_components/test_menu_manager.py` 的 Zoom 测试不能替代图表范围断言。

建议后续自动化：对两种入口构造有效小数据，发 scroll/press/move/release 事件，断言 xlim/ylim 的变化和轴向不变量；验证轴外和按钮区不导航、复位、过滤后视野保留、重复安装不倍增、关闭再开事件不过期。GUI 手工验收必须覆盖工具栏显示与模式、焦点、X/Y 约束、坐标轴带拖动、右键、DPI 和长数据导航。offscreen 测试不能证明用户实际手感或工具栏图标可见。

## 九、残余风险与本轮边界

未运行 GUI/测试，未核对用户机器上的 Matplotlib 版本和 rcParams；不能确定标准工具栏是否真的消失，也不能给出历史回归提交。未对整个仓库所有测试逐文件阅读。当前最有把握的方向是“业务手势承诺与实现缺口 + 两种宿主导航装配不一致”，而不是“Matplotlib 无法实现缩放拖动”。

```acceptance-report
{
  "criteriaSatisfied": [{"id":"criterion-1","status":"satisfied","evidence":"完成当前入口、两种宿主、事件绑定、帮助文字、重绘状态与测试的只读检查，并按事实/推断/GUI待验分类提出恢复与替换条件。"}],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [],
  "validationOutput": ["通过 read/grep/find 静态检查；未运行 GUI、pytest 或构建。"],
  "residualRisks": ["运行时标准工具栏可见性、导航模式、版本差异与真实交互性能尚未 GUI 验证。", "没有历史提交证据，无法确认功能消失的具体时间和引入提交。"],
  "noStagedFiles": true,
  "diffSummary": "未修改源码、配置或提交；仅追加会议分析。",
  "reviewFindings": ["主要发现：帮助文字承诺的滚轮/直接拖动/右键复位无对应自定义事件实现；嵌入路径无 NavigationToolbar 装配。"],
  "manualNotes": "本轮为静态架构分析，引用均指当前仓库路径与行号；没有执行可破坏性操作，未检查 git 暂存区状态。"
}
```

---

## DeepSeek (Round 1): 系统分析：缩放/拖动/单轴拉动消失的故障链与恢复路径

# DeepSeek（系统分析）Round 1：缩放/拖动/横纵轴单独拉动为何消失

## 一、结论速览

1. **自定义缩放/拖动/单轴拉动代码在当前源码中不存在**（已证实，全仓 grep）。全 `src/` 只有 4 处 `mpl_connect`，全部是悬停与图内按钮，没有任何 `scroll_event` / `button_release_event` / `key_press_event` / 工具栏实例化。
2. **缩放与拖动目前只能靠 matplotlib 默认工具栏**，而该工具栏只在「独立窗口模式」(`plt.figure()+plt.show(block=False)`) 下由 QtAgg 后端自动创建；「嵌入模式」(`embed_to_widget`) 裸建 `Figure+FigureCanvasQTAgg`，**完全没有工具栏、没有导航回调**。
3. **"横轴纵轴单独拉动"从来不是 matplotlib 默认的可见按钮**：默认 `NavigationToolbar2` 只有 Home/Back/Forward/Pan-Zoom/Zoom-rect/Subplots/Save，单轴约束靠 pan/zoom 模式下按键盘 `x`/`y`（隐藏快捷键，依赖 canvas 键盘焦点）。源码中没有任何"可见的单轴拖动按钮/轴命中拖动"实现。
4. **帮助文案与实现脱节**：`viewer_controls.py:36` 写着 "Scroll to zoom, drag to pan, right-click to reset view"，但 "right-click to reset" 并非 matplotlib 默认行为——这是"曾存在自定义 button_press 处理器、后被移除"的最强旁证。
5. **结论**：这不是 matplotlib 能力局限，而是**工程实现缺口**——自定义交互代码在多次重构（拆分大文件 + p4 嵌入/回退）中丢失，且嵌入模式从设计上就没有导航。功能**可以恢复**，matplotlib 原生能力足够，无需换库即可满足；换库（pyqtgraph）是"彻底重构"的备选项而非前提。

---

## 二、证据分级

### 2.1 已证实（文件 + 行号 + 源码级证据）

**A. 当前没有任何自定义缩放/拖动/单轴代码**

- 全 `src/` `mpl_connect` 仅 4 处，均为悬停/按钮：
  - `battery_analysis/main/visualization/hover_controls.py:119` — `motion_notify_event`（线性悬停）
  - `battery_analysis/main/visualization/hover_controls.py:335` — `motion_notify_event`（KDTree 悬停）
  - `battery_analysis/main/visualization/button_widgets.py:140` — `motion_notify_event`（按钮 hover）
  - `battery_analysis/main/visualization/button_widgets.py:141` — `button_press_event`（按钮 click）
- 全 `src/` grep `scroll_event` / `button_release_event` / `key_press_event` / `NavigationToolbar2` / `zoom_rect` / `start_pan`：**0 命中**（仅 QSS 里的样式选择器，见下）。
- 唯一的坐标范围改动是 `figure_builder.py` 的初始 `ax.axis(self.listAxis)` 与 `_adjust_y_axis_range`（:294 起，自动 y 范围 + `MultipleLocator` 刻度），**没有交互式 set_xlim/set_ylim**。

**B. 独立窗口模式依赖 QtAgg 自动创建工具栏（因此"缩放/拖动"理论上仍在）**

- 入口：`main/managers/visualization_manager.py:39 run_visualizer → :64 _run_visualizer_standalone → visualizer.show_figure()`。
- `main/factories/battery_chart_viewer_wrapper.py:208 show_figure → :239 self._viewer.plt_figure()`。
- `main/battery_chart_viewer.py:188 plt_figure` → `:252 _initialize_figure`（`plt.figure(figsize=(15,6))`）→ `:319 plt.show(block=False)` → `:330 fig.canvas.draw()`。
- 模块级 `battery_chart_viewer.py:33 matplotlib.use("QtAgg")` + `:42 plt.ion()`。
- 已核对本地 matplotlib **3.10.7**（`uv.lock:546-547`）后端源码：`matplotlib/backends/backend_qt.py:570 FigureManagerQT.__init__` 中 `:596-597 if self.toolbar: self.window.addToolBar(self.toolbar)`；`:1080 FigureManagerQT._toolbar2_class = NavigationToolbar2QT`。即 `plt.figure()` 一创建就带上完整 `NavigationToolbar2QT`（Home/Back/Forward/Pan-Zoom/Zoom-rect/Subplots/Save）。
- 因此独立窗口下：滚轮缩放、pan 按钮拖动**应当可用**（待 GUI 复现确认，见 2.3）。

**C. 嵌入模式没有工具栏、没有导航**

- `main/battery_chart_viewer.py:435 embed_to_widget`：`:445 fig = Figure(figsize=(15,6))` + `:446 canvas = FigureCanvasQTAgg(fig)`，随后直接 `:499 左右 add_subplot`、`:547 _add_hover_functionality_kdtree`，**全程无 toolbar、无 scroll/pan 事件绑定**。
- 该模式当前生产路径未接线：grep 确认 `embed_to_widget` 只被 `battery_chart_viewer_wrapper.py:195` 与测试 `tests/.../test_battery_chart_viewer.py` 调用；`visualization_manager` 走的是 `show_figure`（独立窗口）。**嵌入模式属"半成品/死路径"**。

**D. 帮助文案承诺了不存在的功能**

- `viewer_controls.py:31` "Hover over a data point to view details"（存在，悬停已实现）；`:36` "Scroll to zoom, drag to pan, right-click to reset view"。
- "right-click to reset" 非默认行为；`button_press_event` 处理器（button_widgets.py:141）只处理图内按钮点击，不处理右键重置视图。→ 文案是旧交互的残留。

**E. QSS 有 NavigationToolbar 样式但源码不实例化**

- `battery_analyzer.qss:678-679 QToolBar[objectName="NavigationToolbar"]` 样式存在；`viewer_controls.py` 只创建菜单栏（`_add_menu_bar`，`fig.canvas.manager.window.menuBar()`），从不创建 toolbar。
- 注意区分：`docs/superpowers/specs/2026-08-31-ui-evolution-design.md:204` "工具栏实现（QSS 中有样式但实际未创建）" 指的是**主窗口**工具栏，与图表工具栏不是同一物，但同样印证"样式先行、实现缺席"的工程状态。

**F. 依赖面**

- `pyproject.toml:27-39` 依赖无 `scipy`、无 `pyqtgraph`；`requires-python = ">=3.14"`（`:13`）。`uv.lock` 锁定 matplotlib 3.10.7、numpy 2.3.5、PyQt6。
- 后果：`hover_controls.py _build_kdtree_index` 中 `from scipy.spatial import cKDTree` 恒 ImportError → 悬停永远走线性扫描（`refactor-findings.md #22` 已记录并修复回退，但**性能优化的 KDTree 路径实际从未生效**）。

### 2.2 推断（合理但需 git 历史核实）

**G. 旧版很可能存在自定义缩放/拖动/单轴处理器，后在重构中丢失**

- 旁证 1：`viewer_controls.py:36` "right-click to reset view" 是自定义 `button_press_event(button==3→重置)` 才有的说法，现在无对应代码。
- 旁证 2：git reflog（`.git/logs/HEAD`）显示两次大改动：
  - `refactor-findings.md` 记录 "split-large-files" 把 `interaction_controls.py`（原 1136 行）拆成 6 个子 Mixin，声称"行为不变"——但拆分边界是否包含缩放/拖动代码已无法从现状反推。
  - `feat/p4-chart-embed` 系列（`62689cb 图表嵌入主窗口（双模式支持）`、`fc79628 假按钮替换为 Qt 控件`、`31aa7cc KDTree hover 优化`），随后 `b7abe03 revert(p4): 恢复图表独立窗口模式`——"嵌入→回退独立窗口"的往返中，交互代码最可能被丢。
- **约束声明**：我没有 shell 工具，无法跑 `git log -p`/`git diff` 精确定位"哪次提交删了哪几行"。旧版是否真有"轴拖动"需由具备 git 权限者核对 `battery_chart_viewer.py` / `interaction_controls.py` 的历史版本。我以下结论不依赖"旧版必然有"，只依赖"现状必然无"。

**H. "横轴纵轴单独拉动"最可能的三种解释**（按概率排序）
1. 旧版自定义"抓轴拖动缩放"或"单轴缩放按钮"——现无代码（需 git 核实）。
2. matplotlib 默认 pan/zoom 模式下的键盘 `x`/`y` 单轴约束——**功能仍在但隐藏、无按钮、依赖焦点**，用户以为"没了"。
3. 嵌入模式下根本无 toolbar，用户把嵌入期截图当基准——嵌入路径本来就无。

### 2.3 待 GUI/打包验证（我无法在无显示环境确认）

1. **独立窗口实际是否有 toolbar 且 zoom/pan 可用**：需在真实 Windows + 3.14 + matplotlib 3.10.7 上点开 `BatteryChartViewer` 目测 toolbar 是否存在、滚轮/pan 是否生效、按 `x`/`y` 是否单轴锁定。
2. **键盘焦点**：`plt_figure` 在 `plt.show(block=False)` 后 `:322-327 window.activateWindow(); raise_(); setWindowState(WindowActive)` 可能把焦点从 canvas 抢到 window，导致 `x`/`y` 键与 `h/r`（home）快捷键不响应。`FigureManagerQT.__init__` 本身 `self.canvas.setFocus()`，但后置 activate 的净效果需实测。
3. **打包 exe 的后端完整性**：`scripts/build.py:116` 只 hidden-import `matplotlib.backends.backend_svg`，`:183-188` exclude 了 qt4/qt5/wx/gtk/webagg/nbagg/pgf，**未显式 hidden-import `backend_qtagg`**。若 PyInstaller 未自动追踪 `matplotlib.use("QtAgg")` 的动态导入，打包版可能出现"无 Qt 窗口/无工具栏"（此时现象会从"交互消失"升级为"窗口异常"）。需在 exe 上验证 `import matplotlib.backends.backend_qtagg` 是否可用。

---

## 三、故障链（证据驱动的因果链）

**链 1：嵌入模式 = 交互真空**
`embed_to_widget`（battery_chart_viewer.py:435）裸建 Figure+Canvas → 无 toolbar、无 scroll/pan handler → 任何通过 embed 路径展示的图表天然不可缩放/拖动/单轴。

**链 2：独立窗口 = 只有默认工具栏，且文案误导**
`plt_figure`（:188）→ QtAgg 自动 toolbar（backend_qt.py:596-597）→ 缩放/拖动**名义上可用**；但"单轴单独拉动"无可见入口，只能 `x`/`y` 键（隐藏），而帮助文案（viewer_controls.py:36）又承诺了"right-click reset"这个并不存在的行为 → 用户感知为"功能消失/不好用"。

**链 3：重构丢码**
拆分大文件（声称行为不变）+ p4 嵌入/回退往返 → 若旧版有自定义 `button_press`（右键重置、抓轴拖动），拆分/回退中未被搬回 → 现状只剩 hover+按钮。此链为推断，需 git 历史坐实（见 2.2-G）。

**链 4：回调生命周期（悬停/按钮，非缩放直接原因但影响交互可靠性）**
每次 `plt_figure` 先 `plt.close(self.current_fig)`（:268 附近）再 `_initialize_figure` 新建 fig → 所有 `mpl_connect` 回调绑定在新 canvas 上（悬停/按钮每次都重新注册），旧回调随旧 canvas 一起销毁 → **无泄漏，但也没有任何缩放/拖动回调可复用**。`_open_file_dialog`（viewer_controls.py）重载数据时 `_cleanup_matplotlib_state() + plt.close + plt_figure()` 全量重建，同样只重建 hover/按钮，不重建导航。

**链 5：KDTree 悬停优化形同虚设**
scipy 缺失（pyproject.toml 无依赖）→ `_build_kdtree_index` 恒 `(None,None)` → `_add_hover_functionality_kdtree` 每次悬停回退线性扫描（refactor-findings #22 已修复回退逻辑，但 KDTree 从未生效）。这不是缩放问题，但说明"交互层有大量未兑现承诺"，与主题同源。

---

## 四、能否恢复 / 是否 matplotlib 局限

**能否恢复：能。** 三条路径按成本递增：

1. **零新依赖、最小改动（推荐先做）**：显式实例化并持有 `NavigationToolbar2QT`，并把它同时用于独立窗口与 embed 模式。
   - 独立窗口：`plt_figure` 里 `fig.canvas.manager.toolbar` 已存在，只需验证/保活，别在 `_cleanup_matplotlib_state` 后误关。
   - embed 模式：在 `embed_to_widget` 里 `from matplotlib.backends.backend_qtagg import NavigationToolbar2QT; toolbar = NavigationToolbar2QT(canvas, parent_widget)` 并加入布局，一次补齐 zoom/pan/home/save。
2. **补齐单轴拖动（用户真正想要的功能）**：在 canvas 上补 `scroll_event`（滚轮缩放，读 `event.key`/修饰键做 x/y 单轴）、`button_press/release/motion`（拖动平移，按命中轴或 `x`/`y` 键约束单轴）、`key_press_event`（`x`/`y` 锁定 + 右键重置）。这些全部是标准 matplotlib 事件 API，**不是库局限**。工作量约一个 100–150 行 mixin + 单测。
3. **换库重构（pyqtgraph 等）**：见第五节。

**是否 matplotlib 局限：基本不是。** matplotlib 完整支持缩放（滚轮+框选）、平移（pan）、单轴约束（`x`/`y` 键、或自定义 handler 里只改 xlim/ylim）。真正的局限是：①默认工具栏不提供"可见的单轴拖动按钮"（需自定义或快捷键）；②本项目"图内按钮 axes 与主 axes 混用 + 无显式 toolbar 管理 + embed 无 toolbar + 重构丢码"是工程缺口，不是库能力天花板。唯一算"库固有"的：单轴拖动若要"鼠标直接抓轴上拖"这种 OriginLab 式交互，matplotlib 无开箱组件，需自写命中检测（这可以算半条局限）。

---

## 五、重构优化与替代库

**目标约束**：现有 PyQt6 主窗口 + 独立图表窗口，Python 3.14，打包单 exe（体积敏感，见 2026-10-22 会议结论：Qt/matplotlib/numpy/pandas 是体积大头）。换库必须评估"体积/打包/迁移成本/中文与出版级渲染"。

| 方案 | 缩放/平移/单轴 | 迁移成本 | 打包体积 | 结论 |
|---|---|---|---|---|
| **保留 matplotlib + 显式 toolbar + 自定义单轴 handler** | 全支持，需补代码 | 低（100–150 行 + 测试） | 不变 | **首选** |
| **pyqtgraph** | ViewBox 原生缩放/平移/按轴锁定（`mouseEnabled`、`setMouseEnabled(x=…)` 可做单轴；或 `ViewBox.setXLink`） | 高（全部曲线/按钮/hover 重写） | 中（纯 Qt，体积小于 matplotlib+QtAgg？需实测） | 若决定彻底重做可视化层再选 |
| **QtCharts（PyQt6 自带）** | 基本缩放（QChartView rubberband），单轴拖动需自实现 | 高 | 低（复用 Qt6） | 许可/功能有限，不建议 |
| **Plotly/Bokeh（WebView）** | 交互强，但引入 Web 运行时 | 高 | 明显增大 + 需 QWebEngine | 不建议（与单 exe、离屏报告目标冲突） |

**要点**：
- 换 pyqtgraph 能解决"性能"（曲线多、百万点级，见 2026-10-19 会议对百万行的量级估计）与"单轴 ViewBox 原生"两点，但**不能自动解决"横轴纵轴单独拉动"**——pyqtgraph 的默认行为也是双轴同步缩放，单轴要显式配置（ViewBox 支持 `mouseEnabled`/`aspectLocked`/轴独立，比 matplotlib 更顺手，但仍是代码活）。所以"换库=功能自动回来"是错误预期。
- 若追求 OriginLab 式"抓轴拖缩放"：pyqtgraph 有 `AxisItem` 但也没有开箱"拖轴缩放"；两个库都需自写，差异不大。
- 架构建议（与换库无关）：把"导航交互"抽成独立 `NavigationMixin`（与现有 `InteractionControlsMixin` 平级），避免再被 hover/按钮重构连带丢失；用显式 `canvas.mpl_connect(...)` 返回的 `cid` 记录并在重建/析构时 `mpl_disconnect`，消除回调生命周期隐患。

---

## 六、测试建议（可落地、可验证）

1. **静态回归锁（最便宜）**：测试断言 viewer 类存在导航方法（若决定恢复），例如 `hasattr(viewer, "_add_navigation")`；以及 grep 级断言"存在 ≥1 个 scroll_event 连接"——把"交互能力"变成可回归契约，防止再次被重构抹掉。
2. **独立窗口 toolbar 冒烟（offscreen Qt，复用现有 `test_battery_chart_viewer.py` 的 qapp fixture）**：`show_figure()` 后断言 `fig.canvas.manager.toolbar is not None`、`isinstance(toolbar, NavigationToolbar2QT)`、`toolbar.mode` 可切换。
3. **单轴缩放逻辑单测**：直接构造 `scroll_event`/`button_press_event`（可用 `mpl.backend_bases.MouseEvent` 或 mock）派发给 handler，断言只改 xlim 或只改 ylim、另一轴不变。
4. **嵌入模式回归**：`embed_to_widget(parent)` 后断言 canvas 存在且（恢复后）layout 中包含 toolbar；当前状态下先记录"无 toolbar"为已知缺口。
5. **打包验证**：在 exe 里 `import matplotlib.backends.backend_qtagg` 冒烟 + 手动点开 viewer 看 toolbar；确认 `scripts/build.py` 是否需要补 `--hidden-import=matplotlib.backends.backend_qtagg`。
6. **焦点验证**：真实 GUI 下按 `x`/`y` 能否单轴锁定（确认 `window.activateWindow()` 是否抢焦点）。

---

## 七、风险与待办（给后续轮次/执行方）

- **必须 git 历史核实**（我无 shell）：定位"拆分大文件"和"p4 嵌入/回退"两次改动是否删除了自定义缩放/轴拖动处理器，旧版文件路径与行号。这是回答"代码是否还在"的最终依据，目前只能证"现状无"。
- **待 GUI 复现**：独立窗口 toolbar 是否存在/可用、`x`/`y` 键是否响应、exe 后端是否完整（三者任何一项为否，都会改变修复方案）。
- **低风险先做**：修正 `viewer_controls.py:36` 误导文案 + 显式创建/持有 toolbar + 补 `backend_qtagg` hidden-import；再评估是否自写单轴拖动。
- **勿过度投入**：在未确认"旧版确有自定义单轴拖动"前，不建议直接启动 pyqtgraph 全量重写；先以 matplotlib 补 toolbar + 单轴 handler 恢复能力，性价比最高。

---

## MiniMax (Round 1): MiniMax / Round 1：交互代码盘点、matplotlib 能力边界与"交互意图层"选型建议

# MiniMax / Round 1：BatteryChartViewer 交互（缩放/拖动/轴拉动）失效排查与选型

> 方法说明：本轮全部结论来自**本仓库当前代码**与**本机 .venv 内 matplotlib 3.10.7 源码**（行号已标注）。本会话无 web 工具，因此未引用任何外部网页/库宣传材料；凡涉及"实际运行表现"的结论一律标注为【待 GUI 验证】。本轮未修改任何源码/配置。

---

## 0. 一句话结论

**不是 Matplotlib "做不到"，而是项目从来没有实现过这套交互，只是被动继承 matplotlib 默认工具栏的默认行为**——而默认行为在 3.10 里既不含滚轮缩放、也不含"单轴拖动"，且在独立窗口与嵌入窗口两种模式下表现完全不同；同时图内的固定刻度（`FixedLocator`）会把"缩放生效"这件事在视觉上抹掉，于是用户感知为"功能都没了"。

---

## 1. 已证实事实（代码级，可复核）

### 1.1 入口链路（当前生产路径 = 独立窗口）

| 环节 | 位置 |
|---|---|
| 菜单动作 | `src/battery_analysis/ui/ui_main_window.py:1347`、`src/battery_analysis/main/ui_builder.py:154`（Tools → BatteryChartViewer） |
| 信号连接 | `src/battery_analysis/main/ui_components/menu_manager.py:156` → `main_window.visualization_manager.run_visualizer` |
| 运行管理器 | `src/battery_analysis/main/managers/visualization_manager.py:74-95`（`run_visualizer` → `_run_visualizer_standalone`，注释即写"独立窗口模式"） |
| 工厂/包装 | `src/battery_analysis/main/factories/visualizer_factory.py:33`、`src/battery_analysis/main/factories/battery_chart_viewer_wrapper.py:208-262`（`show_figure` → `_viewer.plt_figure()`） |
| 画图主流程 | `src/battery_analysis/main/battery_chart_viewer.py:186`（`plt_figure`）→ `figure_builder.py:29`（`plt.figure(figsize=(15,6))`）→ `battery_chart_viewer.py:318-320`（`plt.show(block=False)`） |

### 1.2 全仓事件绑定只有 3 处，且**没有一处是导航/缩放**

- `src/battery_analysis/main/visualization/button_widgets.py:140-141`：`mpl_connect("motion_notify_event"/"button_press_event")` —— 图内按钮 hover/点击
- `src/battery_analysis/main/visualization/hover_controls.py:119`、`:335`：`mpl_connect("motion_notify_event")` —— 悬停数据提示（线性扫描 / KDTree）

全仓 `grep -i "zoom|pan|scroll|NavigationToolbar|mpl_connect|on_scroll|on_press|on_motion"`（`src/`）结果里，与"缩放/平移"相关的只有：

- `src/battery_analysis/main/ui_components/menu_manager.py:168-170, 205-222`：`actionZoom_In/actionZoom_Out/actionReset_Zoom` —— 这是**主窗口界面缩放**（`menu_manager.py:222` 注释"重置界面缩放"），与图表坐标轴无关；`locale/*/messages.po:314-321` 的 "Zoom In/Zoom Out/Reset Zoom" 也是这个语义。
- `src/battery_analysis/main/visualization/viewer_controls.py:36`：**只是一行帮助文案** `"Shortcuts: Scroll to zoom, drag to pan, right-click to reset view"`。

**结论（已证实）：仓库中不存在任何坐标轴缩放/拖动/轴拉动的事件处理代码，也不存在 `NavigationToolbar` 的实例化。**

### 1.3 图内菜单栏只有 File / Help，没有 View/导航入口

`src/battery_analysis/main/visualization/viewer_controls.py:69-136`（`_add_menu_bar`）只创建了 `File`（Open/Exit）与 `Help`（About）两个菜单；`tests/battery_analysis/main/test_battery_chart_viewer.py:126-131` 也断言菜单栏恰好是 `["File", "Help"]`——**说明这是被测试固化的现状，不是偶发**。用户没有任何"视图/缩放"的可发现入口。

### 1.4 matplotlib 3.10.7 侧的真实能力边界（本地源码，行号可复核）

- `.venv/Lib/site-packages/matplotlib/backend_bases.py:2608-2646` `FigureManagerBase.__init__`：`rcParams['toolbar'] == 'toolbar2'` 时创建 `self._toolbar2_class(self.canvas)`（Qt 即 `NavigationToolbar2QT`）；`rcParams` 可选值见 `rcsetup.py:281-286`：`'none' | 'toolbar2' | 'toolmanager'`。
- `.venv/Lib/site-packages/matplotlib/backends/backend_qt.py:570-600` `FigureManagerQT.__init__`：`if self.toolbar: self.window.addToolBar(self.toolbar)` → **独立窗口（pyplot 路径）顶部理论上有一条 matplotlib 自带工具栏**（Pan/Zoom/Home/Back/Forward/Save）。
- `.venv/Lib/site-packages/matplotlib/backend_bases.py:2825-2842` `NavigationToolbar2.__init__`：只连接 `button_press_event / button_release_event / motion_notify_event`。**全库 grep `mouse_scroll` 零命中**，即 3.10 的 toolbar2 模式下 **matplotlib 没有任何滚轮缩放处理**。
- 滚轮缩放只存在于 `.venv/Lib/site-packages/matplotlib/backend_tools.py:643-705` `ZoomPanBase.enable()/scroll_zoom()`：只有在 **toolmanager 模式**下启用 Pan/Zoom 工具时才 `mpl_connect('scroll_event', ...)`。
- `.venv/Lib/site-packages/matplotlib/backend_bases.py:3023-3040`（`pan()`）、`:3084-3096`（`zoom()`）：**必须先进入 PAN/ZOOM 模式**（点工具栏按钮或按快捷键）才会响应拖拽。
- `.venv/Lib/site-packages/matplotlib/backend_bases.py:2380-2440` `key_press_handler`：`'p'/'o'/'h'` 等快捷键**要求 `canvas.toolbar` 非 None**（`:2402-2403`）。嵌入模式画布没有 toolbar → 快捷键也无效。
- `.venv/Lib/site-packages/matplotlib/axes/_base.py:738-739`：`Axes` 默认 `set_navigate(True)`，导航本身没有被禁用。

### 1.5 嵌入模式（`embed_to_widget`）是"零导航"的裸画布

- `src/battery_analysis/main/battery_chart_viewer.py:435-470`：`Figure(figsize=(15,6))` + `FigureCanvasQTAgg(fig)`，**不走 pyplot、无 manager、无 toolbar**。
- `src/battery_analysis/main/factories/battery_chart_viewer_wrapper.py:169-196`：包装层提供 `embed_to_widget`。
- **但全仓 grep 显示 `embed_to_widget` 的调用方只有测试**（`tests/battery_analysis/main/test_battery_chart_viewer.py:125`），生产路径未使用（`run_visualizer` 明确走 standalone）。
  → 结论：**当前版本不存在"嵌入后失去缩放"的线上场景**；但一旦将来启用嵌入（`docs/CHANGELOG.md:231` 提到过"图表嵌入主窗口"方向），交互会 100% 消失，因为裸 `FigureCanvasQTAgg` 上没有任何导航能力。

### 1.6 会让"缩放看起来没生效"的两处实现细节（重要）

1. **固定刻度**：`src/battery_analysis/main/visualization/figure_builder.py:38-39`
   ```python
   x_ticks = self.listXTicks          # list(range(0, maxXaxis+1, 100))
   ax.set_xticks(x_ticks)
   ```
   → `matplotlib/axis.py:2156-2170` `_set_tick_locations` 使用 `FixedLocator`，**缩放后刻度不会随视窗重排**，用户会看到"放大后还是 0/100/200…"，主观判定为缩放无效。
2. **`axis()` 覆盖 x 起点**：`figure_builder.py:37` 先 `ax.axis(self.listAxis)`（配置 xmin=10, xmax=600），随后 `set_xticks` 内部 `axis.set_view_interval(min(ticks), max(ticks))`（`axis.py:2158-2160`）把 X 视图强行撑回 **0..600** —— 配置里的 xmin=10 被静默覆盖（**推断，需运行确认**）。同时 `Axes.set_xlim` 会关闭该轴 autoscale，因此后续任何 `autoscale()/relim()` 也不再生效。

### 1.7 测试缺口（已证实）

`tests/battery_analysis/main/test_battery_chart_viewer.py` 共 9 个用例，全部是"启动/空图/错误图/菜单"回归；**没有任何一条断言坐标轴范围、缩放、平移或工具栏存在性**。因此交互行为目前 0 覆盖、0 保护。

---

## 2. "为什么感觉功能都没了"——按可能性排序的解释（含证据强度）

| # | 解释 | 证据 | 强度 |
|---|---|---|---|
| 1 | **从未实现过**：用户记忆中的"缩放/拖动"其实是 matplotlib 默认工具栏的 Pan/Zoom/Home 按钮 + 老版本习惯，项目从未把它产品化（无菜单入口、无帮助、无测试） | 1.2 / 1.3 全仓无实现 | **已证实** |
| 2 | **滚轮缩放在 mpl 3.10 默认根本不存在**（帮助文案是假的） | 1.4（`mouse_scroll` 零命中；scroll 只在 toolmanager 模式） | **已证实（代码级）** |
| 3 | **平移/框选缩放必须先"激活模式"**（点工具栏按钮或按 p/o），用户若只拖拽图表区域不会有任何反应 | 1.4（`pan()/zoom()` 需 mode 激活） | **已证实（代码级）**，运行表现待验证 |
| 4 | **固定刻度把缩放效果"抹平"**，看起来像没生效 | 1.6-1 | **已证实（代码级）**，视觉程度待验证 |
| 5 | 独立窗口顶部**其实有** matplotlib 工具栏，但项目自绘了 File/Help 菜单与 QSS 样式，工具栏显得"外来且无人指引"；用户不知道要点它 | 1.4（`addToolBar`）+ 1.3（无引导） | **推断**；需 GUI 验证工具栏是否真的可见（尤其 `_cleanup_matplotlib_state()` 里 `rcParams.update(rcParamsDefault)`，`figure_builder.py:281-286`，会重置为默认 `toolbar2`） |
| 6 | "横轴纵轴单独拉动"**从来不是 matplotlib 的功能**（matplotlib 的 pan 是 X/Y 联动，`Axes.set_navigate` 无 per-axis 平移），即使装上工具栏也不会有 | 1.4 / `backend_bases.py:3063-3080` `drag_pan` 对同一 axes 同时改 x/y | **已证实** |
| 7 | 用户记忆的旧形态可能在 **v4.0.1 独立版**（`build/Release/battery-analyzer_4.0.1_x64.exe`）或更早的脚本里，本轮无 shell 权限跑 `git log/diff`，**未能核对历史** | — | **待验证**（见 §7） |

---

## 3. "能否恢复"——分层方案（成本递增，建议按序做）

### P0（~50 行，零架构改动）：让 matplotlib 自带能力"可见可用"
1. 在 `viewer_controls.py:_add_menu_bar` 增加 **View 菜单**：Pan / Zoom / Zoom-to-rect / Home(Reset) / Back / Forward，**直接转发到 `fig.canvas.manager.toolbar`**（`toolbar.pan()/.zoom()/.home()/.back()/.forward()`，API 见 `backend_bases.py:2857-3040`）。独立窗口下 `manager.toolbar` 必然存在（`backend_bases.py:2628-2635`）。
2. 隐藏 matplotlib 默认工具栏（`manager.toolbar.hide()`）以统一视觉，改由项目 View 菜单 + 工具提示承载（避免中英混排）。**注意**：`tests/.../test_battery_chart_viewer.py:126` 断言菜单栏内容，需同步更新测试。
3. 修正 `viewer_controls.py:36` 的**虚假帮助文案**（当前承诺的滚轮缩放/右键复位在 mpl 3.10 默认不存在），改为与实现一致并纳入 i18n。

### P1（~30 行）：自研滚轮缩放 + 单轴语义
- 复刻 `backend_tools.py:675-705` `scroll_zoom` 的思路（`ax._set_view_from_bbox([x, y, scale])`），但**扩展修饰键**：`滚轮=双轴缩放 / Ctrl+滚轮=仅X / Shift+滚轮=仅Y`——这正是用户"横轴纵轴单独拉动"的诉求在 Matplotlib 里最接近的实现。
- **单轴拖动平移**：`mpl_connect("button_press_event"/"motion_notify_event")` 自研，按住 Ctrl/Shift 时只改 xlim 或只改 ylim（`ax.set_xlim`/`set_ylim`），绕开 matplotlib 的双轴联动 pan。
- 触摸板/高精度滚轮需做阈值处理（`backend_tools.py` 用 `scrollthresh=.5s` 合并连续滚动）。

### P2（~80 行）："轴把手/区间选择器"语义
- 横轴：直接用 `matplotlib.widgets.RangeSlider`（原生水平区间选择，官方 API）。
- 纵轴：matplotlib 无原生垂直 RangeSlider，需自研（`RectangleSelector` + 轴坐标变换，或自绘 Slider）。
- 这是"拉动轴改变可视区间"最正统的实现，也是 matplotlib 内"横轴纵轴单独拉动"唯一靠谱的落地方式。

### P3：把交互从渲染器里抽出来（**本轮的核心建议，见 §4**）
- 引入 **ChartNavigator（交互意图层）**：只描述语义（`zoom_in/out/reset/zoom_to_rect/pan_start/pan_move/pan_end/x_only/y_only/set_x_range/set_y_range`），不触碰任何 artist。
- 两种后端：`MatplotlibNavigator`（mpl 实现）与未来的 `PyQtGraphNavigator`。
- 好处：交互语义、快捷键、手势、帮助文案、单元测试**全部脱离渲染器**；未来换库时交互行为与验收标准不变；今天就能把"缩放/平移/单轴"变成**可测的纯状态转换**（视图状态 = (xlim, ylim)）。

### P4：结构性修复（与交互无关但强烈建议同批做）
- `figure_builder.py:37-39`：`ax.axis(self.listAxis)` + 固定 `set_xticks` → 改为显式 `set_xlim/set_ylim` + **默认 AutoLocator**（缩放后刻度自适应），并保留 `maxXaxis` 作为初始范围。
- 事件 cid 管理：`button_widgets.py:140-141`、`hover_controls.py:119,335` 的 `mpl_connect` 返回值**从未保存/断开**；每次 `plt_figure` 新建 figure 都会重复注册，`_cleanup_matplotlib_state()` 也没做 `mpl_disconnect`。建议引入 `ChartEventRegistry`，随 figure 关闭统一回收。

---

## 4. 横向创新视角：把"交互"从"渲染"里切出来

**核心洞察**：当前架构把"用户想看哪一段数据"（意图）与"用哪个绘图库画"（渲染）**耦合在 matplotlib 的默认工具栏里**。这造成三个后果：
1. 交互能力不可发现、不可本地化、不可测试（现在连一句帮助文案都是硬编码英文 + 内容不实）；
2. 想换库就得连交互一起重写，迁移成本被放大；
3. 用户的核心诉求（**单轴独立缩放/拖动**）恰好是 matplotlib 的能力短板（pan 双轴联动、无 per-axis 缩放、3.10 无滚轮缩放），无论怎么"用好默认工具栏"都补不上。

**建议的新分层**（渲染器无关）：

```
ChartInteractionIntent  ← 纯数据/纯状态：{intent: zoom_rect|pan|zoom_axis|reset, axis: x|y|both, ...}
        │
        ├── MatplotlibNavigator   （mpl_connect + Axes.set_xlim/ylim + NavigationToolbar 复用）
        └── PyQtGraphNavigator    （ViewBox.setMouseEnabled(x=?,y=?) / setMouseMode / setLimits）
                    ↑
        ChartNavigator（统一语义、快捷键、手势、帮助文案、i18n）
                    ↑
        Viewer UI（View 菜单 / 工具条 / 状态提示 / 单轴锁定指示）
```

这样做的额外红利（横向价值）：
- **"横轴纵轴单独拉动"变成一个开关**：`axis_lock = 'x' | 'y' | 'both'`，UI 上就是一个"轴锁定"按钮，而不是三套手势。
- **交互可回归测试**：用离屏 `FigureCanvasQTAgg` + 合成 `MouseEvent/KeyEvent`，断言 Navigator 输出的是"意图"或"目标 (xlim, ylim)"，测试不依赖真实窗口（补上 §1.7 的空白）。
- **交互与导出解耦**：报告链路（`src/battery_analysis/utils/writers/plot_writer.py` 用 `backend_agg` 出 PNG/SVG）完全不依赖交互层，换库时报告不受影响。

---

## 5. 替代库比较（结论基于项目现状，不基于库的宣传语）

| 维度 | Matplotlib（现状） | PyQtGraph | Plotly |
|---|---|---|---|
| 交互语义完整度 | 需自研滚轮/单轴；pan 双轴联动 | **原生按轴平移/缩放**（`ViewBox.setMouseEnabled(x,y)`、`setMouseMode(PanMode)`）、无限画布、框选缩放 | **最强**（缩放框、拖拽平移、hover、双轴锁定 `fixedrange`、轴范围 API 完整） |
| 与本项目栈的契合 | ✅ 已在栈内；报告导出 `plot_writer.py` 依赖 mpl Agg | ✅ 原生 Qt，与 PyQt6 主程序同栈 | ❌ 渲染走浏览器/WebView，桌面需额外 QtWebEngine |
| 现有代码迁移代价 | 0 | **高**：`figure_builder.py` / `hover_controls.py` / `filter_controls.py` / `battery_selection.py` / `button_widgets.py` 全部是 mpl 惯用法（`FancyBboxPatch`+`transAxes` 的图内按钮、`annotate` 悬停、`fig.add_axes` 叠加轴）需重写 | **很高**：同上 + 渲染模型更换 + 静态导出需 kaleido（额外依赖） |
| 性能（本项目数据量：`档位数×电池数×2` 条曲线，见 `data_loader.py:303-336`，可达数百~上千条） | 千级 line 重绘偏慢（尤其 hover 线性扫描 `hover_controls.py:104-118`） | **数量级优势**（GPU/增量绘制） | 中（浏览器渲染，需数据序列化） |
| 打包/内网部署（Windows + PyInstaller/Nuitka，`scripts/build.py`） | ✅ 现状 | ⚠️ 新增依赖，PyInstaller 可支持但需验证 | ❌ QtWebEngine 体积/依赖/离线风险高 |
| 与报告链路一致性（PNG/SVG → Word/Excel 报告） | ✅ 同一套样式与导出 | ❌ 报告仍需 mpl，两套渲染 | ❌ 同上，且样式难统一 |

**选型结论（我的横向建议）**：
- **不建议整体迁移到 Plotly**：对本项目（内网 Windows 桌面 + PyQt6 + 已有 mpl 报告链路 + 打包流程）是最差匹配，收益（交互）远小于代价（依赖、部署、体积、风格割裂）。
- **PyQtGraph 是唯一值得认真评估的替代**，但**它的价值不是"更好看"，而是原生支持按轴独立平移/缩放**——正好命中用户诉求。但迁移成本被现有"matplotlib 惯用法式 UI"放大，因此**前提是先做 §4 的交互意图层**，让"换渲染器"变成可替换的一件事而不是重写。
- **务实路径**：P0+P1（~100 行）先把 80% 的诉求在 matplotlib 内补齐（菜单化 pan/zoom/reset + 滚轮缩放 + Ctrl/Shift 单轴），用 1~2 天换回用户体感；把 PyQtGraph 作为"渲染器后端 B"的试点（可只做一个只读诊断页），等交互意图层稳定后再决定是否迁移主图。

---

## 6. 重构优化清单（针对本模块，按性价比排序）

1. **修帮助文案**（`viewer_controls.py:36`）——当前描述的功能在 mpl 3.10 默认下**不存在**，属于会误导用户的文档级缺陷；成本 1 行。
2. **补 View 菜单**（`viewer_controls.py:_add_menu_bar`）转发 `manager.toolbar`；同步改 `tests/.../test_battery_chart_viewer.py:126` 的菜单断言。
3. **固定刻度 → 自适应**（`figure_builder.py:38-39`）——缩放后刻度不动是"缩放看起来失效"的直接原因。
4. **`ax.axis()` → 显式 `set_xlim/set_ylim`**（`figure_builder.py:37`），避免被 `set_xticks` 的 `set_view_interval` 覆盖 xmin。
5. **事件 cid 生命周期**：`mpl_connect` 结果统一登记/注销（`button_widgets.py:140-141`、`hover_controls.py:119,335`）。
6. **交互测试补齐**：离屏 canvas + 合成事件，断言 (xlim, ylim) 变化；这批测试同时是未来换库的"行为契约"。
7. **hover 性能**：`_find_nearest_point_linear` 在数百条曲线上每次 mousemove 全扫（`hover_controls.py:104-118`），叠加 `scipy` 未在依赖中（`docs/refactor-findings.md:33` 记录 KDTree 恒不可用）——建议要么加 `scipy` 依赖，要么做抽样/降频；这与"拖动是否跟手"直接相关。
8. **i18n**：`viewer_controls.py` 的所有菜单/提示均为硬编码英文，而主程序有完整 `_()` 体系（`main/ui_builder.py`）——交互入口产品化时应统一。

---

## 7. 待验证清单（诚实标注；本轮无法静态确认）

1. 【待 GUI 验证】独立窗口顶部是否真的渲染出 matplotlib `NavigationToolbar2QT` 工具栏（预期：有，因为 `backend_qt.py:596` `addToolBar` 且 `rcParams['toolbar']` 默认 `toolbar2`，且 `figure_builder.py:281-286` 每次重置为默认）；工具栏 Pan/Zoom 按钮点击后拖拽是否真的生效。
2. 【待 GUI 验证】画布获得焦点时 `'p' / 'o' / 'h'` 是否生效（依赖 `canvas.toolbar` 非 None + `backend_bases.py:2430-2436`）。
3. 【待 GUI 验证】滚轮在独立窗口是否**完全无反应**（预期如此，因 `mouse_scroll` 在 3.10 零命中）。
4. 【待 GUI 验证】缩放后 X 刻度是否仍固定在 0/100/200…（`FixedLocator` 预期不变）。
5. 【待 GUI 验证】`ax.axis(listAxis)` 设的 xmin=10 是否被 `set_xticks` 覆盖回 0（静态推断，需打印 `ax.get_xlim()` 确认）。
6. 【待历史核对】用户记忆中的旧交互（"横轴纵轴单独拉动"）在 v4.0.1（`build/Release/battery-analyzer_4.0.1_x64.exe`）或更早提交中的真实形态——本轮无 shell/git 权限，未能执行 `git log -S` / diff 比对，**不能断言"代码被删了"**，只能断言"当前代码里没有"。
7. 【待验证】独立窗口与"将来可能的嵌入模式"两条路径的交互差异是否需要用同一套 Navigator 覆盖（我建议覆盖，但需产品确认是否还会启用嵌入）。

---

## 8. 给下一轮的具体问题

- 是否同意"**不迁移库也能满足 80% 诉求**"（P0+P1 ≈ 100 行），把 PyQtGraph 降级为"后端 B 试点"而非替代？
- `axis_lock`（单轴锁定）应放在 Viewer UI 还是放进 ChartNavigator（我倾向 Navigator 持有状态、UI 只做切换）？
- 交互意图层是否单独成包（如 `main/visualization/navigation/`），以便未来同时服务 matplotlib / pyqtgraph？
- 固定刻度是彻底改为 AutoLocator，还是保留 `maxXaxis` 步长语义但允许缩放时重算？


---

## GLM (Round 1): 缩放拖动失效排查：代码已证实无自研实现，疑点集中在工具栏缺失与视图重置

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

---

## User (Feedback after Round 1): 优先修复 Matplotlib，同时比较 PyQtGraph 与 Matplotlib 的绘图丰富度和易用性；轴拖动明确指抓住横纵轴刻度区域拖动。

用户第二轮反馈：

> 首先可以先修复matplotlib，其次看下pyqtgraph绘图功能和matplot比哪个更丰富，更好用
> 其次，我的拉动，是抓住横轴/纵轴刻度区域拖动，你理解的没错

方向约束：优先考虑修复现有 Matplotlib；并行比较 PyQtGraph 与 Matplotlib 的绘图功能丰富度及易用性。轴拖动需求已澄清为直接抓住横轴/纵轴刻度区域拖动，不只是工具栏模式下的键盘单轴约束。本条保存用户原意，不代表已经选定拖动时平移还是缩放的具体数学语义。

---

## GPT (Round 2): 纠正互相矛盾的导航断言，以刻度区命中控制器最小修复 Matplotlib

## 一、按已澄清需求收敛

已阅读全部四份 Round 1 和 User Feedback。用户选择的是“先修复 Matplotlib，同时比较 PyQtGraph 的丰富度和易用性”；“抓住横轴/纵轴刻度区域拖动”已经明确，不能再用工具栏里的 x/y 快捷键、Ctrl/Shift 滚轮或 RangeSlider 替代交付。反馈尚未确定拖动表示平移还是缩放，下面给出明确区分的建议契约，而不是冒充用户已选定数学语义。

本轮只读源码及本地 Matplotlib 源码，不修改项目、不安装依赖、不提交。工具不提供 shell/web，未运行 GUI、测试、git 历史或性能基准。以下“事实”指静态源码事实；设计是建议；官方链接供核对，不表示本轮访问过网页。PyQtGraph 未发现于本地虚拟环境，因此不能声称本轮验证了其默认轴区拖动行为。

## 二、必须纠正的第一轮矛盾

### 1. “从来没实现”与“重构丢码”都超出当前证据

MiniMax 的“项目从来没有实现过、已证实”，与 DeepSeek 的“重构中丢失”均应撤回确定语气。当前 `src` 的 `mpl_connect` 检索只有 `visualization/hover_controls.py:119,335` 和 `visualization/button_widgets.py:140-141` 四处，能证明当前业务没有这些自定义导航绑定，不能证明任何历史版本的存在或不存在。帮助文字 `visualization/viewer_controls.py:35-39` 是实现不匹配的证据，不是删除历史的证据。GLM 的“自始至终零测试”同理应限定为当前已检查测试。

### 2. 过滤/选择并不每次重建 Figure，“任何重绘必然复位”不成立

GLM 将初始化流程误当成普通交互回调：
- `src/battery_analysis/main/visualization/filter_controls.py:24-58` 的 `_apply_filter_mode` 修改标题、标签和曲线可见性，最后 `draw_idle()`。
- `src/battery_analysis/main/visualization/battery_selection.py:137-184` 的 `toggle_battery_visibility` 修改曲线/按钮状态并 `draw_idle()`。
- `figure_builder.py:24-52` 是建图初始化；`ax.axis(self.listAxis)` 不会因任意 `draw_idle()` 自动再次执行。

因此“不停重置视野是当前失效主因”没有这条调用链支持，不能据此安排补丁。重新载入/重新建图丢视野是另一回事。GLM 提议用 `set_xbound/set_ybound` 避免覆盖也不成立：它们仍然设定边界；避免复位应改变调用时机/状态策略，而不是更换 setter 名称。

### 3. Matplotlib 支持单轴约束，但这不是刻度区拖动

MiniMax 说“pan 必然双轴联动、没有单轴功能”不准确。本地 `.venv/Lib/site-packages/matplotlib/axes/_base.py:4374-4383` 明确把 `key == 'x'` 转为 `dy=0`、`key == 'y'` 转为 `dx=0`；`backend_bases.py:3063-3069` 将 `event.key` 传给 `ax.drag_pan`。这能推翻“不支持单轴约束”，但不能当成用户需求已完成。

GLM 的“缩放状态下拖动 spine 可免费改 limit”没有给出刻度区命中证据，应撤回默认可用承诺。标准导航的模式、绘图区命中，与轴外刻度区域的命中不是同一件事。

### 4. 默认 toolbar2 不能被当成滚轮缩放已接好

DeepSeek 一处说独立窗口“滚轮缩放应当可用”，另一处又承认需要补 `scroll_event`，应统一为后者。本地 `backend_bases.py:2825-2844` 的 `NavigationToolbar2.__init__` 绑定 press/release/motion，没有滚轮绑定。不能由 QtAgg 自动工具栏存在推出无模式滚轮缩放存在。

工具栏本身也不是“必然有”：`backend_bases.py:2628-2640` 根据 `rcParams['toolbar']` 和后端类条件创建，否则为 None。独立入口通常有 toolbar 是合理预期，不是本轮 GUI 事实。修复时先读实际 manager/toolbar，不能重复创建第二个 toolbar。

### 5. 固定刻度不等于缩放被取消

`figure_builder.py:37-42` 和 `battery_chart_viewer.py:500-507` 确实设置固定 X 刻度和固定步长 Y locator。固定刻度会导致放大后刻度偏稀或缩小时偏密，不会把已经变化的 xlim/ylim 自动恢复，更不会让曲线几何缩放消失。MiniMax 的“固定刻度把缩放抹平、直接原因”应降为可读性问题。初始化 `set_xticks` 可能扩展视图范围，可单独验收，不能当作持续导航失败证据。

另外，“Matplotlib 没有垂直 RangeSlider”不准确：本地 `widgets.py:595,663` 的 RangeSlider 支持 horizontal/vertical。即便支持，它也不是本次刻度区拖动诉求，不宜作为首选替代。

### 6. PyQtGraph 与性能断言也需去宣传化

“PyQtGraph 没有开箱轴区拖动”不应凭印象下结论：官方 AxisItem 源码提供轴鼠标交互相关方法，应核对目标版本 `mouseDragEvent`、`wheelEvent` 与 linked ViewBox 的转发、轴向限制关系：
https://pyqtgraph.readthedocs.io/en/latest/_modules/pyqtgraph/graphicsItems/AxisItem.html

本轮未联网、未安装该库，不能声称已经核实目标版本源码或实际行为。反过来，`ViewBox.setMouseEnabled(x,y)` 的存在也不能直接证明其默认手势与用户想要的刻度区行为完全一致。

第一轮的“数量级优势”“万点 hover 不卡”、固定工期、固定补丁行数、包体积增量都没有本项目测量支撑，不用于决策。未在依赖声明中列 scipy 也不能证明任何用户环境里“恒 ImportError”或历史上“从未生效”；最多指出干净安装环境的可选优化依赖风险。

## 三、最小可靠控制器：只为当前 Matplotlib 服务

### 1. 先固定交互契约，平移和缩放分开

建议默认：
- 横轴刻度区域左拖：仅 X 平移，X 跨度不变，Y 完全不变。
- 纵轴刻度区域左拖：仅 Y 平移，Y 跨度不变，X 完全不变。
- 主绘图区左拖：双轴平移；仅在没有 toolbar 模式时启用。
- 缩放采用滚轮：绘图区双轴、X 刻度区仅 X、Y 刻度区仅 Y，锚点分别为鼠标投影位置。
- 提供明确的“复位视图”按钮；右键复位若保留帮助契约，则只对没有形成拖动的右键点击执行。不要让右键拖动同时承担缩放和复位。

若产品确认“拉刻度”实际期待缩放，则增加一个明确可发现的“轴拖动：平移/缩放”选项，复用同一命中/生命周期，不把一种数学操作称为另一种。默认左拖平移是本人的设计建议，非用户原话。

### 2. 命中检测必须使用显示坐标，而不是只检查 event.inaxes

刻度文本通常位于主 Axes patch 外，`event.inaxes is ax` 很可能为假，`event.xdata/ydata` 也可能为 None。这正是“看似写了拖动但抓刻度无反应”的典型设计陷阱。

最小做法：控制器只持有主 `ax`，不扫描所有辅助按钮 Axes。完成首次 draw 后，根据 `ax.bbox`、可见 tick label 的 `get_window_extent(renderer)`，形成底部 X 带和左侧 Y 带：沿轴方向限制在主图跨度内，垂直轴方向覆盖刻度线、刻度文字及少量容差。整个 Axis 的 tightbbox 可能包含轴标题，应显式决定是否排除标题，而非误让大块空白可拖。辅助按钮区优先排除；角部 X/Y 带重叠设为不启动，避免靠顺序随机抢轴。

区域随 draw/resize 更新；容差基于当前 renderer 的点到显示单位转换，不硬编码 Qt 逻辑像素与 Matplotlib display 像素比例。实际高 DPI 对齐仍须 GUI 验证。

### 3. 单一拖动状态机与确定数学

状态只需 idle/dragging；按下时记录轴向、模式、鼠标显示坐标、起始 xlim/ylim、主轴 bbox 及冻结变换。整个手势冻结这些参考值，不在每次 motion 上叠加前一次结果。

对于当前线性轴，起始 X 范围 `[a,b]`，水平像素移动 `dx`，图宽 W：
- 平移：`delta = dx / W * (b-a)`，新范围 `[a-delta,b-delta]`；因此跨度不变，内容随鼠标移动。Y 用 dy/H 类推。
- 缩放：选择锚点 c 和正倍率 s，新范围 `[c+(a-c)*s, c+(b-c)*s]`；锚点不变、跨度改变。滚轮向上建议 s<1。若以后提供拖动缩放，可用有界指数倍率并明确拖动方向。

采用鼠标显示坐标加冻结逆变换求锚点，不能依赖轴外 `xdata/ydata`。保留反向轴的端点顺序，拒绝 NaN/Inf 和过小范围。当前版本先声明只支持线性坐标；未来对数轴需在尺度变换空间完成相同计算，不能直接用线性公式承诺通用支持。

移动距离未超过小阈值不算拖动，避免点击引起细小视野变化。每次有效更新只调用相应 setter 和 `draw_idle()`。拖动时暂停 hover/注释扫描；释放后恢复。

### 4. 可靠性比“几十行”重要

- toolbar Pan/Zoom 活跃或 canvas widgetlock 已被他者占有时，自定义控制器不启动；自身开始拖动后持有锁，避免两套逻辑同时改 limits。不要依赖回调注册顺序“吞事件”。
- press 后锁定目标轴，移动到轴外仍继续；不能在 motion 时要求仍命中刻度带。画布内可使用 canvas 的鼠标抓取能力，Qt 画布外释放/失焦则需要验证 Qt 的 grab/release 与取消处理，不能假设 mpl 回调一定送达。
- release、窗口失焦、关闭、重建、异常统一结束/取消并释放锁，避免卡住。Esc 可回滚起始范围；失焦至少结束手势。
- 控制器由 viewer 强引用；保存 callback ids，安装幂等，销毁时 disconnect。Matplotlib 对实例方法回调的弱引用是需要保活的原因之一。不能仅凭“建了新 figure”断言必然泄漏或绝无泄漏。
- 自定义导航前后按一次手势记录历史：有标准 toolbar 时接入其 `push_current()`，不在每个 motion 压栈；复位基线在初始范围和刻度设置完成后捕获。数据载入新建基线，过滤/电池显隐保留当前视野。
- 两条建图路径安装同一个 Matplotlib 控制器即可；`battery_chart_viewer.py:541-580` 的嵌入路径当前装配选择/hover 后只把 canvas 加入布局，若保留该 API，可补同样导航及可发现工具栏，但不要为此扩大为宿主重构工程。

官方接口参考（本轮未联网）：
https://matplotlib.org/stable/users/explain/figure/event_handling.html
https://matplotlib.org/stable/api/backend_bases_api.html
https://matplotlib.org/stable/api/transformations.html

## 四、绘图丰富度与“好用”应拆为三种评价

| 维度 | Matplotlib | PyQtGraph | 当前决策含义 |
|---|---|---|---|
| 通用统计/科研绘图丰富度 | 现成图型、布局、坐标投影、刻度/注释/出版式样广，适合静态分析与报告 | 重点是 Qt 科学可视化；曲线、散点、图像、ROI 等很实用，不等于通用图型完全覆盖 mpl | 当前已有曲线和报告体系，Matplotlib 更适合作为通用绘图基础 |
| 交互工具丰富度 | 标准导航、widgets、事件/变换接口完整，但本需求需自行装配 | ViewBox、轴联动、ROI/区域选择、图像工具更贴近交互桌面工作流 | 若未来产品主线成为交互诊断仪表，PyQtGraph 值得原型 |
| 终端用户易用性 | 默认工具栏模式和隐藏快捷键不够直接，但定制后能提供刻度区拖动与清晰提示 | Qt 交互工作流较自然，但默认菜单/鼠标语义仍需产品化 | 用户不应承担库差异，最终用任务完成率和误操作评价 |
| 开发易用性 | 当前已集成，Artist、导出和样式可复用；精细交互要管理命中/回调/变换 | Qt 开发者更易接入实时数据、范围联动和交互对象；现有 mpl Artist/hover/图内按钮不能原封不动迁移 | “新页面好开发”与“现有页面迁移省事”不是同一结论 |
| 静态导出与一致性 | 适合精细控制和已有报告样式复用 | 有导出支持，不能说无报告能力；字体、线型、矢量输出及报告一致性需验证 | 用实际报告样张对比，不凭库标签下结论 |
| 大数据交互性能 | 可能受曲线数量、重绘、hover 扫描影响，可尝试降采样/暂停 hover 等优化 | 针对科学交互显示有相应能力，但不保证本项目任意场景更快，也不是所有绘制都自动走 GPU | 同数据、同可见曲线数、同功能测导航延迟/内存后再选 |
| 部署 | 已在项目依赖中 | 需验证 Python/PyQt/NumPy 支持矩阵和打包；报告继续依赖 mpl 时，新增库不等于缩包 | 不承诺性能倍数、包体积或固定工期 |

PyQtGraph 官方能力索引供核对：
https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/viewbox.html
https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/axisitem.html
https://pyqtgraph.readthedocs.io/en/latest/user_guide/exporting.html
Matplotlib 图型参考：https://matplotlib.org/stable/plot_types/index.html

综合建议：论通用绘图与精细成图，优先 Matplotlib；论 Qt 科学交互组件和持续更新工作流，重点评估 PyQtGraph；论本次修复可达性，没有证据证明必须换库。

## 五、不提前建设双后端框架，验收先于迁移

拒绝第一轮“先建设渲染器无关意图层 + 两种 Navigator 才能换库”的前置条件。现在只需一个 Matplotlib 控制器，加少量可独立测试的范围计算函数与交互契约。保留清晰边界不是立即实施插件体系；若未来原型证明必须换库，再按真实差异抽象接口。

最小验收应测试行为而不是 grep 到处理器或 hasattr：
1. 在主 Axes 外、tick label 显示坐标处发事件，X/Y 拖动分别只改对应轴，平移跨度不变。
2. 缩放改变跨度并保持锚点；不把缩放与平移混为一个断言。
3. 拖出刻度带后继续，释放/失焦后停止，角部/按钮区不启动。
4. toolbar 模式与自定义拖动互斥；hover 在拖动时不扫描/更新；一次手势只增加一次有效历史。
5. 过滤/选择保留 limits；复位恢复初始基线；重建/重复安装无双倍响应，关闭后不残留状态。
6. 两个入口的离屏范围测试通过后，再在真实 Windows 和打包版验证高 DPI、窗口外释放、工具栏可见性和实际手感。

残余风险：本轮没有 GUI、打包、历史与性能运行证据；用户尚未选择轴拖动的平移/缩放默认语义；PyQtGraph 目标版本的 AxisItem 默认行为未本地验证。下一步应由实施阶段确认手势契约并执行最小修复和回归；并行咨询本身不应改源码。资料已足够支撑当前方向，不继续扩散选型。

---

## MiniMax (Round 2): MiniMax / Round 2：更正第一轮过强断言（单轴、垂直 RangeSlider、从未实现、拖轴差异不大、视图重置），并给出 Matplotlib 优先的轴区拖动落地方案与 PyQtGraph 逐项绘图能力对照

# MiniMax / Round 2：更正与收敛——轴区拖动的真实能力边界、逐项绘图丰富度对照、Matplotlib 优先落地方案

## 0. 本轮方法与工具限制（先声明，避免把推测当事实）

- 本轮仍然**只读**分析：未修改源码、未安装依赖、未运行 GUI/pytest、未提交。
- 本会话**没有 shell、没有 web/检索工具**。因此：
  - 所有 matplotlib 侧结论均来自**本机 `.venv/Lib/site-packages/matplotlib` 3.10.7 源码**（可复核的路径+行号）；
  - 所有 **pyqtgraph 侧结论均为模型知识，本机未安装 pyqtgraph（`.venv/Lib/site-packages` 目录清单中不存在 `pyqtgraph`，同目录也没有 `scipy`），无法给出行号级证据**，一律标注「模型知识·未核实」，并给出核实步骤；
  - 官方文档链接为记忆中入口，**本轮未联网核对**，标注「未核实」；
  - 未测量的性能倍数、工期、包体积一律不写成事实。
- 已复核的仓库事实（与第一轮一致）：`src/` 内 `mpl_connect` 仅 4 处——`visualization/button_widgets.py:140-141`、`visualization/hover_controls.py:119` 与 `:335`，**全部是悬停与图内按钮，无任何导航/缩放/轴区事件**（复跑 grep 结果）。这是「现状无实现」的事实。

---

## 1. 对第一轮结论的更正（逐条，含证据等级）

### 更正 A：「Matplotlib 不支持单轴」是过强断言 —— **已证伪**

- 第一轮 `MiniMax / Round 1` §2 第 6 条称「matplotlib 的 pan 是 X/Y 联动，`Axes.set_navigate` 无 per-axis 平移」，该表述不成立。
- 事实（本地源码）：
  - `.venv/Lib/site-packages/matplotlib/axes/_base.py:4383-4385`：`format_deltas()` 中 `elif key == 'x': dy = 0` / `elif key == 'y': dx = 0` → **按住 x/y 键时平移只作用于单轴**；
  - `.venv/Lib/site-packages/matplotlib/backend_bases.py:3128-3136`：`drag_zoom()` 中 `if key == "x": y1, y2 = ax.bbox.intervaly` / `elif key == "y": x1, x2 = ax.bbox.intervalx` → **框选缩放同样支持单轴约束**；
  - `backend_bases.py:3023`（`pan()`）、`:3084`（`zoom()`）：两个手势都需先进入 PAN/ZOOM 模式，这一点第一轮说得对。
- 修正后的准确表述：**matplotlib 支持「单轴平移 + 单轴框选缩放」，但入口是隐藏快捷键（需工具栏处于 Pan/Zoom 模式 + 画布持有键盘焦点），不是用户所说的「抓住轴刻度区域直接拖动」。**

### 更正 B：「matplotlib 无原生垂直 RangeSlider，需自研」是过强断言 —— **已证伪**

- 第一轮 `MiniMax / Round 1` §3 P2 称「纵轴：matplotlib 无原生垂直 RangeSlider，需自研（RectangleSelector + 轴坐标变换，或自绘 Slider）」。本地 3.10.7 源码不支持该说法：
  - `matplotlib/widgets.py:623`（`RangeSlider.__init__(..., orientation="horizontal")`）、`:663-664` 文档明写 `orientation : {'horizontal', 'vertical'}`、`:258-266` `SliderBase` 显式 `_api.check_in_list(['horizontal', 'vertical'], orientation=orientation)`、`:275-277` 垂直分支切到 `ax.yaxis`；
  - 垂直分支的绘制与命中逻辑齐备：`:713-715`（轨道矩形）、`:754-756`（标签）、`:804-805`（选区多边形）、`:851-852`、`:938-940`（handle 跟随）；
  - 另有 `matplotlib/widgets.py:2478-2479` `SpanSelector(..., direction : {"horizontal", "vertical"})`、`:2558`、`:2598-2611` 垂直分支同样原生可用。
- 修正后的准确表述：**matplotlib 3.10.7 同时原生提供水平/垂直的 `RangeSlider` 与 `SpanSelector`；纵轴区间选择不需要自研控件，只需放置与几何配置。**

### 更正 C：「项目从未实现过这套交互」属未证推断 —— 应表述为「现状无实现」

- 「现状无实现」是可核事实（见 §0）。但「从未实现过」「用户记忆来自 matplotlib 默认工具栏」是推断，第一轮把它写成了结论（`MiniMax / Round 1` §2 表第 1 行标「已证实」、`DeepSeek / Round 1` §三链 3「重构丢码」）。
- 本轮可读到 `.git/logs/HEAD`（**纯文本，可读**），其中包含 `62689cb… feat(p4): 图表嵌入主窗口（双模式支持）` 与 `b7abe03… revert(p4): 恢复图表独立窗口模式`，说明**交互宿主形态在历史上确实发生过变更**（独立窗口 ↔ 嵌入窗口）；但 `.git/objects` 已打包、无 shell 无法解包做 diff，因此**「历史上是否存在过自定义轴拖动代码」依然无法判定**。
- 修正后的准确表述：**「当前 HEAD 无任何自定义导航/缩放/轴拖动实现（事实）」；「历史上是否存在过并被删除」为未决问题；既不能说从未实现，也不能断言被重构删除。**（此条同时约束 DeepSeek 的「重构丢码」链与 GLM 的「v3.1.0 清理是否波及图表窗口」假设：两者都是假设，不是结论。）

### 更正 D：「两库在『抓轴拖动』上差异不大、都需自写」方向可疑 —— **matplotlib 侧已证伪，pyqtgraph 侧待核实**

- **matplotlib 侧（本地事实）**：
  - `matplotlib/axis.py` 中 grep `def mouse` **零命中**（仅有 `:1337 get_tightbbox`）→ **Axis（刻度、标签、轴脊）没有任何鼠标事件处理**；
  - `matplotlib/axes/_base.py:2685-2689` `Axes.in_axes()` = `self.patch.contains(mouseevent)[0]`，即**只有 axes 绘图区内部才算命中，刻度区在 bbox 之外**；
  - `backend_bases.py:2970-3020` `_start_event_axes_interaction()` 只在 `ax.in_axes(event)` 为真时收集 axes → **工具栏的 Pan/Zoom 一律不响应轴区点击**。
  - ⇒ **在 matplotlib 中实现「抓住横纵轴刻度区域拖动」必须自写命中检测 + 手势**，这一点第一轮说对了。
- **pyqtgraph 侧（模型知识·未核实，不可当结论）**：pyqtgraph 的 `AxisItem` 是独立的 `QGraphicsItem`，**定义了 `mouseDragEvent` 与 `mouseWheelEvent`**（轴区拖拽/滚轮在框架层就有入口），轴区交互因此**不是从零自写**；其具体语义（拖轴=平移该轴？缩放该轴？滚轮是否只作用于该轴？）必须读源码确认。
- 核实步骤（本轮未执行，需后续具备 shell/网络者执行）：
  1. `pip download pyqtgraph` 或在虚拟环境安装后 `python -c "import pyqtgraph,inspect;print(inspect.getsourcefile(pyqtgraph.graphicsItems.AxisItem))"`；
  2. 在 `pyqtgraph/graphicsItems/AxisItem.py` 中 grep `def mouseDragEvent`、`def mouseWheelEvent`，读其 `linkedView()` / `setRange` / `setLimits` 调用，判断语义；
  3. 在 `pyqtgraph/graphicsItems/ViewBox.py` 中 grep `mouseDragEvent`、`mouseWheelEvent`、`setMouseEnabled`、`linkView`，确认单轴锁定与联动能力；
  4. 官方 API 入口（记忆，未核实）：`https://pyqtgraph.readthedocs.io/en/latest/api/graphicsItems/axisitem.html`、`https://pyqtgraph.readthedocs.io/en/latest/api/graphicsItems/viewbox.html`。
- 修正后的准确表述：**「抓轴拖动」在 matplotlib 侧 = 必需自研；在 pyqtgraph 侧 = 已有框架级轴区事件入口（待核实语义）。第一轮『两库差异不大』的结论在证据不足时不应成立。**

### 更正 E：「每次交互后视图都被强制重置」过强 —— **已证伪（对过滤切换而言）**

- 第一轮 `GLM / Round 1` §1.6 称「任何一次切换交互后视图必然回到初始范围」。
- 本地事实：全仓 `set_xlim|set_ylim|relim|autoscale` 命中全部落在**布局辅助 axes**（`battery_selection.py:64-65,96-97`、`filter_controls.py:74-75`、`viewer_controls.py:48-49`）与**唯一的建图期 Y 轴自适应** `visualization/figure_builder.py:330`；`_adjust_y_axis_range` 的调用点只有 `battery_chart_viewer.py:290`（独立窗口建图）与 `:527`（嵌入建图）。
- ⇒ **过滤/电池按钮切换（`set_visible` + `draw_idle`）不会重置视野**；只有「重建 figure」（重新打开/载入数据，`plt.close` + 重建）会重置 Y 范围。`figure_builder.py:37 ax.axis(self.listAxis)` 只在建图时执行一次。
- 修正后的准确表述：**「视图丢失」是「重建 figure 时重置」，不是「每次交互都重置」；用户抱怨的『拖了没用』更可能是『根本没有可拖的手势 + 工具栏不可发现』，而不是『拖完被弹回』。**

### 更正 F：GLM 的「补丁 A：防御性挂 NavigationToolbar2QT」对独立窗口近乎无效

- 本地事实：`.venv/.../matplotlib/backends/backend_qt.py:596-597` `if self.toolbar: self.window.addToolBar(self.toolbar)`，`:685` `class NavigationToolbar2QT(NavigationToolbar2, QtWidgets.QToolBar)`，`:1080` `FigureManagerQT._toolbar2_class = NavigationToolbar2QT`；仓库侧 `visualization/figure_builder.py:284` 每次清理都 `rcParams.update(rcParamsDefault)`，**没有任何地方把 `rcParams['toolbar']` 设为 `'none'`**（全仓 grep 仅 QSS 注释 `ui/styles/battery_analyzer.qss:678-679`）。
- ⇒ 独立窗口（pyplot 路径）**按 matplotlib 默认行为本就有工具栏**；「防御性再挂一个」只会造成双工具栏，**不解决用户要的东西**（轴区直接拖动）。
- 真正有缺口的是：①**嵌入路径**（`main/battery_chart_viewer.py:435+` 裸 `Figure`+`FigureCanvasQTAgg`，无 toolbar，且 `:442` 的 docstring 仍宣称返回 `toolbar`，属文档漂移）；②**手势本身**（滚轮缩放、轴区拖动）需要自研；③**可发现性**（`visualization/viewer_controls.py:36` 的帮助文案承诺「Scroll to zoom, drag to pan, right-click to reset view」，而这三条在 mpl 3.10 默认下都不成立——文案是缺陷本身）。

---

## 2. 主责项：PyQtGraph vs Matplotlib —— 绘图丰富度与易用性逐项对照

**标注规则**：`原生` = 库直接提供该能力；`扩展` = 库内相邻能力组合/插件式组件可达；`自定义` = 需自己写。
**证据等级**：`M` = 本机 matplotlib 3.10.7 源码已核实（带路径行号）；`P` = pyqtgraph 模型知识，本机未安装、**未核实**；`R` = 需运行验证。

| # | 维度 | Matplotlib 3.10.7（已核实，除注明） | PyQtGraph（模型知识·未核实） | 谁更丰富 / 谁更好用 |
|---|---|---|---|---|
| 1 | 曲线 | **原生**：`ax.plot`/`Line2D`，样式、对数轴、多轴（twinx）齐全（`M`） | **原生**：`PlotDataItem`/`PlotCurveItem`，`setData(connect='finite')` 增量更新、`setClipToView`、`setDownsampling(auto=True, mode='peak')`（`P`） | 丰富度：matplotlib（类型学、对数、公式排版、坐标轴科学格式化）胜；**实时/大数据跟手度：pyqtgraph 胜**（机制优势，是否成为瓶颈需实测） |
| 2 | 散点 | **原生**：`ax.scatter`（marker/size/color 映射、alpha 集合）（`M`） | **原生**：`ScatterPlotItem`（`P`） | 打平；matplotlib 静态出图更精细 |
| 3 | 误差条 | **原生**：`ax.errorbar`（含 `capsize`、`errorevery`）、`fill_between` 置信带（`M`） | **原生**：`ErrorBarItem`（`P`） | 打平 |
| 4 | 统计与科学图 | **原生**：箱线/小提琴/直方/等高线/极坐标/3D（`mplot3d`），数学公式（`mathtext`）、LaTeX 挂载（`M`） | **部分原生**：`BarGraphItem`、`HistogramLUTItem`；**箱线/小提琴/等高线/3D 需自定义或第三方**（`P`） | **matplotlib 明显更丰富**（这是 pyqtgraph 的短板，不能因「实时交互强」而忽略） |
| 5 | 图像与热图 | **原生**：`imshow`、`pcolormesh`、`contourf`、`colorbar`（`M`） | **原生**：`ImageItem` + `ColorMap` + `HistogramLUTItem`（对比度/亮度 LUT，交互性强）（`P`） | 静态热图 matplotlib 强（色标/等高线/插值）；**交互式图像 LUT 调整 pyqtgraph 强** |
| 6 | ROI（选区/局部放大） | **扩展**：需显式启用 `matplotlib/widgets.py` 的 `SpanSelector`（`:2478` 支持 `direction='vertical'`）、`RectangleSelector`、`EllipseSelector`、`LassoSelector`、`PolygonSelector`、`Cursor`（`:1880`）（`M`） | **原生强项**：`ROI`/`LinearRegionItem`（可拖、可缩放、带手柄、可发信号）（`P`） | **ROI 与局部放大：pyqtgraph 明显更好用**（可拖拽手柄 + 事件回调是它的设计中心）；matplotlib 是「能用但要自己拼装」 |
| 7 | 多图联动 | **扩展**：`plt.subplots(sharex/sharey=True)`、`ax.sharex(other)` 属静态共享；**跨图同步视图栈（back/forward）无内建**，需自写 `xlim_changed` 广播（`M`） | **原生**：`ViewBox.linkView/setXLink/setYLink`、`MultiViewBox`（`P`） | **pyqtgraph 更省事**；matplotlib 需自写 ~几十行 |
| 8 | 实时更新 | **扩展**：`artist.set_data()` + `canvas.draw_idle()`；高效 blit 需自写 `copy_from_bbox/restore_region`；`matplotlib.animation`（`M`） | **原生**：`setData` 增量 + `clipToView` + 自动降采样（`P`） | **pyqtgraph 更强**，尤其点数大时 |
| 9 | 中文标注 | **原生**：`Text/annotate`；**但依赖字体配置**：仓库已做 `main/battery_chart_viewer.py:38-39` 与 `visualization/figure_builder.py:286-287`（`CN_FONT_LIST`、`axes.unicode_minus=False`）；矢量输出时字体需可嵌入（`M`） | **原生**：走 Qt 字体（`QGraphicsTextItem`），中文由系统字体直接支持、无嵌入坑；**但无 mathtext/LaTeX**（`P`） | 中文**桌面显示 pyqtgraph 更省心**；**出版级排版/公式 matplotlib 更强** |
| 10 | 矢量与报告导出 | **原生且成体系**：`backends/backend_svg.py`、`backend_pdf.py`、`backend_ps.py`、`backend_agg.py` 均在本机（`M`）；仓库报告链路已用它（`utils/writers/plot_utils.py`、`utils/report_coordinator.py`） | **扩展**：有 `pyqtgraph.exporters`（SVG/图像），**PDF/EPS 等出版格式缺失或依赖额外件**（`P`） | **matplotlib 明显胜**（且换库会直接打断现有报告链路） |
| 11 | Qt 集成 | **扩展**：有 `backends/backend_qtagg.py`（本机存在，`M`），可 `FigureCanvasQTAgg` 嵌入 Qt，但窗口/字体/DPI/事件协调由项目自己做 | **原生**：`GraphicsView/GraphicsLayoutWidget`，就是 Qt 控件（`P`） | **pyqtgraph 更原生**；matplotlib 是「能塞进 Qt 的外来渲染器」 |
| 12 | 交互可发现性 | **扩展**：默认 `NavigationToolbar2` 有 Home/Back/Forward/Pan/Zoom/Save（`backend_bases.py:2857` 起、`backend_qt.py:685`），**但轴区无任何交互**（`axis.py` 无 mouse 方法、`_base.py:2685-2689`），且滚轮缩放不在 toolbar2 中 | **扩展**：交互丰富但**默认无工具栏**，按钮/提示要自己造；轴区有事件入口（`P`，待核实） | **两者都不满足「用户抓住刻度区就拖」**：matplotlib 需自写手势，pyqtgraph 需自写工具栏/提示；**体验差异主要在自写成本，而非有无** |

**对照结论（可辩护的部分）**
1. **「谁更丰富」要分两层**：*静态/科学/出版* → **matplotlib 明显更丰富**（统计图、公式、PDF/PS/SVG、中文+公式排版）；*交互几何与实时数据流* → **pyqtgraph 更丰富**（ROI 手柄、跨图 linkView、增量更新+自动降采样、Qt 原生）。
2. **「谁更好用」取决于本项目的具体功能面**：本项目要的是「大量电池曲线 + 过滤切换 + 悬停读数 + 报告出图」，**报告链路与统计/出版能力是硬需求 → matplotlib 侧优势权重更高**；而 pyqtgraph 的优势恰好落在「实时大数据流 + ROI 精细操作」，本项目当前**没有证据表明**这两项是瓶颈（第一轮引用的「百万行」是外部会议估计，非本项目实测）。
3. **交互能力不是「换库自动获得」**：两库都需要自写「工具栏/可发现性/中文化/状态同步」，差别是**起点不同**：matplotlib 起点是「成熟渲染 + 成熟 widget 库（垂直 RangeSlider/SpanSelector 已有）+ 无轴区手势」；pyqtgraph 起点是「轴区与 ViewBox 交互框架已在 + 静态科学图能力缺」。
4. **若确实要评估 pyqtgraph，最小可行试点不是重写主图**，而是做一个**只读诊断页**（同一份数据，两套渲染并排 + 交互一致性对拍），用真实数据量测「hover/拖动延迟、内存、报告出图一致性」，再决定是否值得迁移。

---

## 3. 用户澄清后的需求落地：Matplotlib 中实现「抓住横纵轴刻度区域拖动」

用户已明确：**拖的是横轴/纵轴刻度区域本身**（不是工具栏模式下按 x/y 键）。用户**未**指定拖动后的数学语义（平移该轴？缩放该轴？），因此方案必须把语义做成可切换，而不是替用户决定。

### 方案 A（推荐主路径）：自研「轴区命中 + 轴把手」手势，matplotlib 必需自写
- **命中检测（自写，matplotlib 侧无原生）**：在 `button_press_event` 中，用 `ax.xaxis.get_tightbbox(renderer)` / `ax.yaxis.get_tightbbox(renderer)`（`axis.py:1337` 提供 `get_tightbbox`）取轴区外框，判断事件点是否落在轴区（并排除本仓已有的图内按钮 axes：`battery_selection.py:63`、`filter_controls.py:73`、`viewer_controls.py:47` 这些 `add_axes` 辅助轴）。
- **手势语义（三选一，用可见开关而非隐藏快捷键）**：
  - `平移该轴`：拖动 Δ → 只改 `ax.set_xlim(x0-Δx, x1-Δx)`；
  - `缩放该轴`：以按下点为锚，`new = anchor + (old-anchor)/k`；
  - `双轴联动平移`（默认，兼容性最好）。
- **可发现性（关键，matplotlib 已给零件）**：`matplotlib/backend_tools.py:29-38` `Cursors.RESIZE_HORIZONTAL / RESIZE_VERTICAL` → 鼠标进入轴区时 `canvas.set_cursor(...)`，配合 `viewer_controls.py` 的 View 菜单与中文提示，弥补「无工具栏提示」的短板。
- **复用现成 widget 的取巧做法**：把「轴把手」做成 `RangeSlider`（横轴，`orientation='horizontal'`）与 `RangeSlider`（纵轴，`orientation='vertical'`，**3.10.7 原生支持，见更正 B**），放在与轴刻度重叠的独立 axes 里，视觉上就是「抓住轴拖」，且完全用现成、成熟、可测的控件——**代价是它是「区间选择」语义而非「连续拖动平移」语义**，需产品确认是否接受。
- 结论：**「抓轴拖动」在 matplotlib 是可控的自研量（命中检测 + 状态机，约百行级），不应因「Matplotlib 做不到」而否定。**

### 方案 B（不推荐现在做）：换成 pyqtgraph
理由不是「matplotlib 做不到」，而是「若未来**实测证明**实时大数据流或 ROI 精细操作成为瓶颈，再把渲染层换成 pyqtgraph 才划算」；届时也应保留本方案 A 的**交互意图层**，让迁移只换渲染器。

---

## 4. 改进方案（Matplotlib 优先，收敛为可执行阶段）

### P0 先把「假承诺」变成「真能力」与「真文案」（低风险、立刻可见）
1. 修 `visualization/viewer_controls.py:36` 的虚假帮助文案：当前承诺的滚轮缩放/拖动平移/右键复位在 mpl 3.10 默认下均不存在；改为与实现一致，或在实现后改成中文真实文案（项目已有 `_()` 体系，见 `main/ui_builder.py`）。
2. 补 **View 菜单**（Pan / Zoom / Reset(Home) / Back / Forward），直接转发 `fig.canvas.manager.toolbar`（`backend_bases.py:2857 home()`、`:3023 pan()`、`:3084 zoom()`），并按需隐藏默认工具栏以统一视觉；**同步更新 `tests/battery_analysis/main/test_battery_chart_viewer.py`（当前断言菜单恰为 `["File","Help"]`）**。
3. 独立窗口无需防御性再挂 `NavigationToolbar2QT`（见更正 F）；**嵌入路径**（`main/battery_chart_viewer.py:435+`）若将来启用，需显式 `NavigationToolbar2QT(canvas, parent)` 并把 `:442` docstring 的 `toolbar` 承诺对齐实现。

### P1 实现用户点名的手势（核心）
4. 新增独立 Mixin（与 `visualization/interaction_controls.py` 平级，避免再被拆分重构抹掉），职责三件事：**①轴区命中与轴把手拖动；②滚轮缩放（可复用 `backend_tools.py` 的 `scroll_zoom` 思路）；③右键/快捷键复位**。
5. 引入极简 **视口状态对象**（`xlim, ylim, axis_lock, mode`）+ **事件 cid 登记/注销**（现有 `mpl_connect` 返回值从未保存，见 `button_widgets.py:140-141`、`hover_controls.py:119,335`）。
6. **明确「视图所有权」策略**：数据变更（重载/换目录）→ 重新 fit；仅过滤/电池选择 → **保留用户视野**（事实依据：当前切换路径不重置 xlim/ylim，见更正 E）。

### P2 让视图状态与视觉反馈自洽（消除「缩放看起来没生效」）
7. `visualization/figure_builder.py:37-39`：`ax.axis(self.listAxis)` + 固定 `set_xticks(listXTicks)` 会让刻度不随视窗重排（`FixedLocator`），主观上像「缩放无效」；建议改为显式 `set_xlim/set_ylim` + 自适应刻度（或保留步长语义但允许缩放时重算），并注意 `set_xticks` 内部 `set_view_interval` 可能覆盖配置的 xmin（**推断，需运行打印 `ax.get_xlim()` 验证**）。
8. `figure_builder.py:330` 的建图期 Y 轴自适应与用户交互后的 Y 视野要分工（数据 fit vs 用户视野）。

### P3 测试与回归护栏（第一轮一致且必要）
9. 离屏 Qt 断言：**轴区拖动后仅 xlim 变化**（ylim 不变）、**滚轮缩放锚点在鼠标位置**、**复位恢复初始视野**、**过滤切换后视野保留**、**重复安装不导致事件倍增**、**按钮区/辅助 axes 不触发导航**、**嵌入模式 toolbar 存在性**。
10. 把手势行为固化为**纯函数契约**（输入：意图 + 当前视口 → 输出：目标视口），使未来换渲染器时行为可对拍。

### P4（可选，暂缓）真正的渲染器抽象
11. 若未来确有换库需求，再抽 `ChartNavigator`（意图层）+ `MatplotlibNavigator`；**在此之前不要为了「以后可能要换」而先做抽象**（YAGNI），但 P1 的状态对象设计要预留可移植性（不直接依赖 mpl 内部 API，只依赖 `set_xlim/set_ylim/get_xlim/get_ylim`）。

---

## 5. 事实 / 推断 / 待运行验证 三分清单

**事实（本地源码可复核）**
- 现状无任何自定义缩放/拖动/轴拖实现（`mpl_connect` 仅 4 处：hover 与按钮）。
- matplotlib 3.10.7 支持单轴平移（`axes/_base.py:4383-4385`）与单轴框选缩放（`backend_bases.py:3128-3136`）。
- matplotlib 3.10.7 原生支持垂直 `RangeSlider`（`widgets.py:623,663-664,713,754,804,851,938`）与垂直 `SpanSelector`（`widgets.py:2478-2479`）。
- matplotlib 的 `Axis` 无任何鼠标处理（`axis.py` grep `def mouse` 零命中）；`Axes.in_axes()` 以 patch 判定（`axes/_base.py:2685-2689`）→ 轴区点击不进入 Pan/Zoom。
- 独立窗口工具栏由 `backends/backend_qt.py:596-597,1080` 自动创建，仓库未禁用（`figure_builder.py:284` 重置为默认 rcParams）。
- 全仓无「交互时重设 xlim/ylim」的代码；唯一 `set_ylim` 在建图期 `figure_builder.py:330`。
- 本机环境：matplotlib 3.10.7 / PyQt6 6.10.0 / numpy 2.3.5 / pandas 2.3.3；**无 scipy、无 pyqtgraph**。

**推断（需运行或读源码确认）**
- `set_xticks` 覆盖 `ax.axis()` 配置的 xmin（静态推断）。
- 用户所说「抓住刻度区拖动」更可能是平移或缩放某轴（两种语义都合理，方案必须可切换，不能替用户定死）。
- pyqtgraph 的 `AxisItem.mouseDragEvent/mouseWheelEvent` 存在且作用于轴区（模型知识，未核实）。

**待运行/GUI/源码核实**
- 独立窗口运行时是否真的渲染出工具栏、按钮是否可见可点、焦点是否让 `x/y` 快捷键生效（需真实 Windows GUI）。
- 打包 exe 中 `matplotlib.backends.backend_qtagg` 及其 toolbar 子模块是否完整（`scripts/build.py` 的 exclude 列表未排除 qtagg，但隐式导入收集需实测）。
- pyqtgraph 轴区事件的真实语义与联动能力（按 §1 更正 D 的 4 步核实）。
- 数据规模是否真的构成交互瓶颈（**本轮无任何性能实测，不给倍数**）。

---

## 6. 结论（收敛）

1. **先修 Matplotlib 的方向成立**，但理由要改写：不是因为「matplotlib 做不到」，而是因为①静态/科学/报告能力与现有链路都在 matplotlib；②轴区拖动在 matplotlib 需要自写**约百行级**的手势，而工具栏、垂直 RangeSlider、SpanSelector、光标样式等零件都已具备；③换库会同时打断报告链路与统计图能力，而 pyqtgraph 的强项（实时大数据流、ROI 手柄、跨图 linkView）**当前没有实测证据表明是瓶颈**。
2. **第一轮三处过强断言需更正**：单轴（matplotlib 支持，只是入口隐藏）、垂直 RangeSlider（原生支持）、从未实现（只能断言「现状无实现」，历史未决）；另需更正「两库拖轴差异不大」（matplotlib 侧已证为纯自研）与「每次交互都重置视野」（实际只在重建 figure 时重置）。
3. **可立即落地的顺序**：P0 文案+View 菜单 → P1 轴区拖动手势+滚轮+复位+状态对象 → P2 刻度自适应与视图所有权 → P3 离屏契约测试；P4 渲染器抽象推迟到有实测证据时。
4. **PyQtGraph 的评估方式**：不是「直接换库」，而是先做**只读诊断页**（同数据双渲染 + 交互对拍 + 报告出图一致性），用实测数据决定是否值得付出迁移成本。


---

## DeepSeek (Round 2): DeepSeek / Round 2：勘误三处事实、核验轴带拖动与工具栏单轴的语义差异，给出行为级测试

# DeepSeek / Round 2：勘误 + 轴带拖动语义核验 + 行为测试设计

## 0. 方法与限制声明（事实前提）

- 本轮只读仓库 + 本地 `.venv/Lib/site-packages/matplotlib/3.10.7` 源码（行号可复核）。matplotlib 版本由 `uv.lock:546-567` 锁定为 3.10.7。
- 本 worker 无 shell、无 web、无 GUI 显示环境：**未运行 pytest、未启动窗口、未跑 `git log -S`**。所有"运行表现"类结论继续标注【待 GUI 验证】，不把源码推断冒充实测。
- 以下行号均为 `.venv/Lib/site-packages/matplotlib/...` 或 `src/battery_analysis/...` 的真实路径。

---

## 1. 事实勘误（对第一轮三方结论的交叉复核）

### 1.1 纠正 GLM §1.6 的事实错误：过滤/电池切换**不会**重建 figure，也不会重置视图

GLM 第一轮 §1.6 断言："过滤切换 `_apply_filter_mode`、电池按钮等交互会重建 figure……任何一次切换交互后视图必然回到初始范围"，并给出行号 `battery_chart_viewer.py:309-316`、`:252-260`。**这条是事实错误**，我把两段真实代码对照如下：

- `filter_controls.py:30-58` `_apply_filter_mode` 的实际动作只有四件：`manager.window.setWindowTitle`、`ax.set_title`、`ax.set_ylabel`、逐条 `line.set_visible(...)`，最后 `fig.canvas.draw_idle()`。**没有** `ax.axis()`、没有 `plt.close`、没有 `set_xlim/set_ylim`。
- `battery_selection.py` 的 `toggle_battery_visibility` 同理：只 `line.set_visible` + `draw_idle()`，不重建 figure、不动坐标范围。
- figure 真正被重建只发生在 `plt_figure()` **重新进入**时：`battery_chart_viewer.py:252-260` 先 `plt.close(self.current_fig)` 再 `_initialize_figure()`。触发源是 File→Open 载入新数据（`viewer_controls.py:161-166` 调 `_cleanup_matplotlib_state()` + `plt.close` + `self.plt_figure()`）或从主菜单重新启动查看器（`visualization_manager.py:64-88` 每次都 `plt.close("all")`）。

结论：**"缩放后切一下过滤就被弹回初始视图"这个症状在过滤/电池切换路径上不成立**。GPT 第一轮在这点上是对的（"过滤切换主要 set_visible 后 draw_idle，没有每次把 xlim/ylim 重置"）。GLM 把"重新打开查看器会清视图"和"同一窗口内切换过滤"两件事混为一谈。

### 1.2 纠正 GLM §1.6 的另一处事实错误：`ax.axis(listAxis)` 不是"每次重绘都执行"

GLM 称"每次绘制/重绘都会执行 `ax.axis(self.listAxis)`（figure_builder.py:37、battery_chart_viewer.py:500）"。实际上 `ax.axis(self.listAxis)` 只在**创建 figure 时执行一次**：

- 独立窗口：`figure_builder.py:37`（`_initialize_figure` 内，紧随 `plt.figure` 之后）。
- 嵌入模式：`battery_chart_viewer.py:500`（`embed_to_widget` 内，紧随 `add_subplot` 之后）。

`draw_idle()` 只触发重绘，不会重跑这两行。因此"视图被强制钉回初始范围"只发生在"重新创建 figure"时，不是"每次重绘"时。

### 1.3 收回我自己第一轮的说法：默认工具栏**没有**滚轮缩放

我第一轮 §2.1-B 写过"独立窗口下：滚轮缩放、pan 按钮拖动应当可用"。**滚轮缩放这一半是错的，现收回**。源码证据：

- `backend_bases.py:2832-2837` `NavigationToolbar2.__init__` 只 `mpl_connect` 了三个事件：`button_press_event`（→ `_zoom_pan_handler`）、`button_release_event`（→ `_zoom_pan_handler`）、`motion_notify_event`（→ `mouse_move`）。**没有任何 `scroll_event` 连接**。
- 滚轮缩放只存在于 **toolmanager 模式**：`backend_tools.py:656-658` `ZoomPanBase.enable()` 才 `mpl_connect('scroll_event', self.scroll_zoom)`，而 `scroll_zoom`（`backend_tools.py:675-705`）才是滚轮缩放实现。
- 项目跑在 toolbar2 模式：`matplotlibrc:107` 默认 `toolbar: toolbar2`，`rcsetup.py:281-284` 可选值仅 `none|toolbar2|toolmanager`，仓库未改 `rcParams['toolbar']`（`_cleanup_matplotlib_state` 每次都 `rcParams.update(rcParamsDefault)`，见 `figure_builder.py:281-284`，等于回到 toolbar2）。

结论：MiniMax 第一轮"滚轮缩放在 mpl 3.10 默认不存在"是**正确**的；`viewer_controls.py:36` 帮助文案 "Scroll to zoom" 是虚假承诺，`drag to pan` 需先进入 Pan 模式才成立，"right-click to reset" 无任何对应实现。三者都不该再被当作"现状功能"。

### 1.4 核实 MiniMax §1.6 的"xmin=10 被 set_xticks 覆盖"——从"推断"升级为"源码级事实"

MiniMax 把"`ax.axis()` 设的 xmin=10 被 `set_xticks` 覆盖回 0"标为【推断，需运行确认】。我读完 `axis.py` 后确认它**成立**，且是确定行为：

- `ax.axis([10,600,0,5])` → `set_xlim(10,600)` 用 `ignore=True` 精确设定 xlim=[10,600]。
- 随后 `figure_builder.py:38` `ax.set_xticks(self.listXTicks)`（`listXTicks = range(0,601,100)`，见 `battery_chart_viewer.py:133`）→ `axis.py:2172 set_ticks` → `axis.py:2154 _set_tick_locations` → `axis.py:2163 axis.set_view_interval(min(ticks), max(ticks))` **默认 `ignore=False`**。
- `axis.py:2352-2362` `_make_getset_interval` 的 setter：`ignore=False` 时"只扩不缩"，取 `min(0,600,10)=0` → xlim 被**扩张回 [0,600]**。

所以项目配置的 `xmin=10` 从未真正生效，初始 X 视图恒为 [0,600]。这是**初始视图**的细微 bug，与缩放/拖动失效无关，但修交互时应一并处理（见 §3.6）。注意：`set_ticks` 的 docstring（`axis.py:2209-2215`）明确说"view limits 会被扩到包含所有 ticks"，这是有意的设计，不是 matplotlib 的异常。

---

## 2. 用户诉求的核心差异：标准工具栏"单轴约束" ≠ "抓住刻度带拖动"

用户反馈（0005）已澄清：要的是**抓住横轴/纵轴刻度区域直接拖动**。这必须与第一轮多位顾问提到的"工具栏 x/y 键单轴约束"严格区分——**两者是不同手势，恢复默认工具栏不满足诉求**。

### 2.1 标准工具栏的单轴约束是"键盘修饰键 + 拖动"，不是抓轴带

- Pan 模式：`backend_bases.py:3043 press_pan` → `:3063 drag_pan` → `axes/_base.py:4431 Axes.drag_pan` → `:4369-4410 _get_pan_points` → `:4377-4392 format_deltas`：`key=='x'` 时 `dy=0`（只平移 X），`key=='y'` 时 `dx=0`（只平移 Y）。即**进入 Pan 模式后按住 x/y 键拖动**才单轴。
- Zoom 模式：`backend_bases.py:3100 press_zoom` → `:3126 drag_zoom` 用 `key=='x'/'y'` 把另一轴强制铺满 bbox，实现单轴框选缩放。
- 这些全部依赖：①先点工具栏进入 Pan/Zoom 模式；②画布持有键盘焦点；③用户知道按住 x/y 键。没有任何"抓刻度区拖动"的命中逻辑。

### 2.2 关键坐标事实：`event.inaxes` 只覆盖数据 patch，不含刻度带

这一点直接决定 hit-test 方案，第一轮无人点出：

- `axes/_base.py:2685-2689`：`Axes.in_axes(mouseevent)` 返回 `self.patch.contains(mouseevent)[0]`——patch 是**数据区矩形**，不含刻度标签带。所以鼠标落在刻度标签带（数据区之外）时，`event.inaxes` 是 **None**。
- 推论 A：**轴带命中检测不能依赖 `event.inaxes`**，必须自己遍历 `fig.get_axes()` + 用 `ax.bbox`（含刻度标签的完整 axes 包围盒）判断落点，再细分落在哪个带。
- 推论 B：工具栏 pan/zoom 的触发过滤 `_start_event_axes_interaction`（`backend_bases.py:2970-2978`）同样靠 `ax.in_axes(event)`，**因此工具栏在刻度带区域根本不会触发**。这天然形成"数据区内=工具栏/悬停，数据区外刻度带=自定义轴带手势"的物理互斥基础（见 §3.4）。

---

## 3. 轴带拖动设计方案（行为级，供评审，不改码）

### 3.1 hit-test（命中检测）

- 对 `fig.get_axes()` 逐个：先判 `event.x/event.y`（display 像素）是否落在 `ax.bbox` 内（`ax.get_window_extent(renderer)` 或 `ax.bbox`），不在则跳过。
- 数据矩形四角：`ax.transData.transform((xlim0, ylim0))`、`ax.transData.transform((xlim1, ylim1))`。本项目是线性轴，四角即数据区边（更精确含 margin 可用 `ax.patch.get_window_extent(renderer)`）。
- 带划分（display 像素）：
  - **x 轴带** = `ax.bbox.y0 <= y < data_bottom`（下缘刻度带），水平跨度对齐数据区宽度。
  - **y 轴带** = `ax.bbox.x0 <= x < data_left`（左缘刻度带）。
  - 顶部 strip（标题区）默认**不**当 x 轴带，避免与标题/工具栏语义打架；若确需顶部刻度带可改用 `ax.xaxis.get_tightbbox(renderer)` 精确限定。
- 命中优先级：数据 patch（透传，交给 pan/zoom/悬停）→ y 轴带 → x 轴带 → 未命中透传。

### 3.2 坐标变换（默认"拖动=平移"语义）

反馈 0005 明确"不代表已经选定拖动时平移还是缩放的具体数学语义"，故此处给出平移为主、缩放备选，**默认平移**：

- 按下记录 `press_x/press_y`、`xlim0/ylim0`、`data_width_px/data_height_px`。
- x 轴带：`dx_px = x - press_x`；`scale_x = (xlim1 - xlim0) / data_width_px`；`set_xlim(xlim0 - dx_px*scale_x, xlim1 - dx_px*scale_x)`。负号表示"向右拖视图左移"，与 matplotlib `_get_pan_points` 的 `bbox.translated(-dx,-dy)`（`axes/_base.py:4396`）方向一致。
- y 轴带：`dy_px` 同理只改 ylim。
- 若产品改选"拖动=缩放"（Origin 式拉伸）：锚定对侧边，`factor = (data_width + dx_px) / data_width_px` 之类公式；需产品拍板，不作为默认。
- 线性轴适用；对数轴需经 `ax.xaxis.set_view_interval` 做数据坐标换算（本项目线性，暂不涉及）。

### 3.3 拖出画布 / 释放 / 失焦兜底

- 状态存 mixin 属性 `self._axis_drag`（含 axes 引用、axis、起始点、起始 lim、`cid_motion`、`cid_release`）。**运动与释放都读保存的状态，不读 `event.inaxes`**——仿照 `NavigationToolbar2.press_pan` 存 `self._pan_info.axes` 的做法（`backend_bases.py:3058-3074`），这正是 matplotlib 官方处理"拖出 axes 后 inaxes 变 None"的范式。
- motion 超出 bbox 时仍按实际 delta 更新（拖出继续跟手，不 clip）；或 clip 到 bbox 边缘，二选一，建议不 clip。
- 释放 `button_release_event`：`mpl_disconnect(cid_motion/cid_release)`，清 `self._axis_drag`，并调 `toolbar.push_current()`（有 toolbar 时）把本次视图写入历史，使 Home/Back/Forward 可用。
- 失焦/漏 release 兜底：连接 figure `close_event`，断开仍在活跃的 cid；或在 motion 中检测 `event.button` 已无按下即自动收尾。

### 3.4 与工具栏互斥

- 物理互斥由 §2.2 推论 B 保证：轴带在数据 patch 之外，工具栏 pan/zoom 不触发。
- 补充显式规则（可读性/防御）：轴带 handler 只在 `toolbar.mode == NONE` 时接管；若处于 PAN/ZOOM 模式则忽略轴带按下，避免与工具栏状态机竞争。轴带按下限定 `button == 1`（左键），右键留给未来上下文菜单。
- 若后续决定隐藏默认 toolbar 改自绘 View 菜单（MiniMax P0 思路），则互斥简化为"单一 NavigationMixin 持有模式状态"，不再与 NavigationToolbar2 并存。短期建议：**保留默认 toolbar 兜底 + 叠加轴带手势**，成本最低、可发现性最好。

### 3.5 close/生命周期 disconnect（现状缺口）

- 现状：`hover_controls.py:119,335`、`button_widgets.py:140-141` 的 `mpl_connect` 返回值从未保存/断开。独立窗口每次 `plt.close` 重建 figure，旧 canvas 随销毁、回调随之消失，暂不泄漏；但嵌入模式 canvas 可复用，且未来若复用 fig 会叠加 handler。
- 轴带拖动新增的 motion/release cid 必须双路径断开（release + close_event），避免引用已销毁 axes 的陈旧 handler 在后续事件里抛异常。

### 3.6 顺带修两处与"交互看起来失效"相关的实现

- `figure_builder.py:38-39` 固定 `set_xticks` 会把初始 xmin 从 10 扩回 0（§1.4），且 FixedLocator 使缩放后刻度不随视窗重排（MiniMax §1.6-1 正确）。建议改为"先 set_xlim/set_ylim 再设刻度"，或缩放交互后切回 AutoLocator。
- `viewer_controls.py:36` 帮助文案三处承诺全部与实现不符（§1.3），落地手势后重写文案并纳入 i18n。

---

## 4. 行为测试（断言数值变化/不变量，不是 grep/方法存在性）

以下 T2–T6 是"轴带手势恢复后应通过"的目标契约；T1 现在就能写，并可**直接反证 GLM 的"过滤重置视图"说**。全部用离屏 `FigureCanvasQTAgg` + 合成 `MouseEvent`（复用现有 `tests/battery_analysis/main/test_battery_chart_viewer.py` 的 qapp fixture 思路）。

- **T1 过滤切换视图保留（回归）**：建图 → `ax.set_xlim(200,400)` 模拟用户缩放 → 触发 `_apply_filter_mode`（或点击过滤按钮回调）→ 断言 `ax.get_xlim() == (200,400)` 不变，且目标 line 组可见性正确翻转。
- **T2 轴带命中分类**：合成 `button_press_event`，x 取 `data_bottom` 与 `ax.bbox.y0` 之间像素 → 断言分类为 `'x'`；y 取左侧带 → `'y'`；数据 patch 内 → 断言**不接管**（透传给 pan/zoom）。
- **T3 单轴不变量（核心）**：x 带 press → motion(+50px) → release，断言 `xlim` 两端同向平移同一 delta、`ylim` **完全不变**；y 带反之。这是"只动一根轴"的行为证明。
- **T4 拖出画布 + 释放**：x 带 press → motion 到 canvas 外坐标 → release，断言无异常、`self._axis_drag` 已清空、xlim 为最后有效值、再次 press 正常。
- **T5 工具栏互斥**：`toolbar.pan()` 后，press+drag 于数据 patch → 断言两轴都变（工具栏生效）且轴带 handler 未触发；再 press 于 x 带 → 断言仅 xlim 变（轴带生效）。
- **T6 关闭清理**：press 不 release → `plt.close(fig)`（或 emit `close_event`）→ 断言无异常、后续无残留 motion 回调触发。

---

## 5. Matplotlib vs PyQtGraph：绘图丰富度/易用性（回应反馈 0005，克制声明）

只区分"能力事实"与"迁移成本推断"，不把未测的性能倍数/工期/包体积当事实。

- **事实**：Matplotlib 的出版级渲染、中文字体（`CN_FONT_LIST`）、导出 PNG/SVG→Word/Excel（`plot_writer` 用 Agg）链路现成；pyqtgraph 需要另起一套报告导出或保留双渲染栈。
- **事实**：单轴独立拖动两者都非"零代码"。matplotlib 无开箱"抓轴带拖动"，需 §3 自写 hit-test+motion；pyqtgraph `ViewBox.setMouseEnabled(x=?, y=?)` 能锁单轴平移，但"抓刻度带拖"同样要派生的 AxisItem/SignalProxy 自定义，不是开箱即得。所以"换 pyqtgraph 单轴拖动自动就有了"是错误预期（GPT/DeepSeek 第一轮已指出，此处再次确认）。
- **推断（非实测）**：pyqtgraph 在大点数多曲线的交互流畅度通常优于 matplotlib（其定位），但本仓数据量（档位×电池×2 条曲线，数百条，`data_loader.py:303-336`）的延迟**未测**，不把"数量级优势"当既定事实。
- **推断（非实测）**：迁移成本——现有 `figure_builder/hover_controls/button_widgets/battery_selection` 全是 mpl 惯用法（`transAxes` 图内按钮、`annotate` 悬停、`fig.add_axes` 叠加轴），换 pyqtgraph 需重写整套交互，报告导出仍需保留 mpl，形成双渲染栈。

**结论**：按反馈"优先修 matplotlib"落地 §3 轴带手势，同时把视图状态契约收敛为 `(xlim, ylim)` 并用 §4 的行为测试锁定——未来若评估 pyqtgraph 后端 B，同一套行为测试不变，换库成本才能被量化而非拍脑袋。

---

## 6. 给下一轮/执行的决策点

1. 轴带拖动语义：**平移（默认）还是缩放**？反馈 0005 未定，需产品拍板（§3.2 两套公式已备）。
2. 顶部 strip 是否也作 x 轴带（会与标题区冲突），默认建议只下缘。
3. 保留默认 toolbar 兜底 + 叠加轴带手势，还是隐藏 toolbar 改自绘 View 菜单（决定互斥复杂度，§3.4）。
4. 过滤切换不重置视图是现状事实（§1.1），应写进 CHANGELOG 作为既定行为，避免后续误"修"。


---

## GLM (Round 2): GLM / Round 2：修正过滤切换误判、核实工具栏与抓轴手势边界、分阶段最小修复清单

# GLM（务实落地）— Round 2：修正我第一轮的错误结论、核对各顾问断言与用户"抓轴拖动"语义下的最小修复清单

## 0. 本轮边界声明（重要）
- 本 worker 工具集只有 read/grep/find/ls 与会议黑板工具，**没有 shell**：无法执行 `git log -S`、`git show`、pytest、GUI 运行。因此"旧版本是否存在过自定义缩放/轴拖动代码"**仍无历史证据**，维持第一轮立场：**当前无实现只能证明"现在没有"，不能推出"从未实现"或"曾被重构删除"**。DeepSeek 的"重构丢码"链（其 2.2-G）是合理假设，但不是事实，勿当结论使用。
- 所有 matplotlib 行为断言均已对照本地 `.venv/Lib/site-packages/matplotlib` 3.10.7 源码（运行验证仍缺，标注为"代码级证实/GUI 待验"）。
- 用户方向以黑板条目 0005 为准：**优先修 matplotlib；并行比较 PyQtGraph 与 Matplotlib 的绘图丰富度和易用性；"拉动"= 抓住横轴/纵轴刻度区域拖动**。本轮不改任何源码。

## 1. 主动修正：我第一轮 §1.6 "过滤切换必定重建图/重置视野"是错的

GPT 在第一轮第四节的质疑成立，我沿实际回调链重查后**收回该结论**：

- 过滤切换的真实链路：点击图内按钮 → `toggle_filter_mode`（`filter_controls.py:81`）→ `_apply_filter_mode`（`filter_controls.py:25-60`）——该函数只做三件事：改窗口标题/标题/ylabel 文本、对 lines 逐条 `set_visible`、`fig.canvas.draw_idle()`（`filter_controls.py:60`）。**不 `plt.close`、不新建 figure、不调用 `ax.axis`/`set_xlim`，视野完全不动。**
- 电池选择按钮同理：`toggle_battery_visibility`（`battery_selection.py:139-186`）只 `set_visible`（`:166,:172`）+ `draw_idle`（`:182`）；QCheckBox 版本同样（`:299-303`）。
- `_add_filter_button`/`_add_battery_selection_buttons` 在 `plt_figure` 中只执行一次（建图时），之后的点击走的是已注册的回调，不再经过 `battery_chart_viewer.py:309-316`。我第一轮把"建图时的装配代码"误读成"每次点击的路径"。
- **修正后的结论**：过滤/电池切换**不**重置视野；用户缩放后点过滤，视图应保留（代码级推断 + draw_idle 语义支持，GUI 待验）。视野强制重置只发生在三类场景：①`plt_figure` 重入（重载数据/新目录，`battery_chart_viewer.py:252-265` close 旧 fig → `figure_builder.py:37-39` 全新 figure 重新 `ax.axis(self.listAxis)`+`set_xticks`）；②重新打开 viewer（`visualization_manager` 关闭重建）；③嵌入模式 `_show_error_chart_embedded` 等重建路径。若用户主诉是"过滤一切换视野就弹回"，那与代码矛盾，GUI 实测必须优先复现这一点。

## 2. 对各顾问结论的核对结果（逐条，代码级）

### 2.1 MiniMax：两条关键断言经本地 mpl 源码复核，成立
1. **toolbar2 模式无滚轮缩放**：`NavigationToolbar2.__init__`（`backend_bases.py:2825-2841`）只连接 `button_press_event`/`button_release_event`/`motion_notify_event` 三类，全文件无 `scroll_event` 连接。滚轮缩放只存在于 toolmanager 模式的 `ZoomPanBase`。→ **帮助文案 "Scroll to zoom"（`viewer_controls.py:36`）在默认配置下是不实承诺**，且 hover 线性扫描的 on_hover 与此无关。成立。
2. **`set_xticks` 覆盖 `ax.axis()` 的 xmin + FixedLocator 抹平缩放**：`axis.py:2154-2170` `_set_tick_locations` 用 `FixedLocator(ticks)` 并对共享轴调用 `set_view_interval(min, max)`；`set_ticks` docstring 明说 "view limits ... are expanded so that all given ticks are visible"（`axis.py:2176-2177`）。本项目 `listXTicks = list(range(0, maxXaxis+1, 100))`（`battery_chart_viewer.py:136`）起点为 0，而 `listAxis[0]` 来自配置默认值（`:130-134`）——只要配置 xmin>0，视窗会被静默扩回 0；且缩放后刻度固定在 0/100/200…，放大到 10–50 区间时轴上**无任何刻度线**，用户主观即"缩放没生效"。这是全部候选解释里**唯一能同时解释"独立窗口有工具栏却觉得什么都不能用"的代码级事实**。成立。

### 2.2 三方共识复核：无自定义导航代码、独立窗口有默认工具栏
- 全仓 `mpl_connect` 仅 hover（`hover_controls.py:119,:335`）与按钮（`button_widgets.py:140-141`），无 scroll/pan/key 导航绑定——GPT/DeepSeek/MiniMax/我在第一轮一致，本轮复核无异议。
- 独立窗口工具栏：`FigureManagerQT.__init__` 在 `rcParams['toolbar']`（默认 'toolbar2'）时创建并 `window.addToolBar(self.toolbar)`（`backend_qt.py:596-597`，`_toolbar2_class = NavigationToolbar2QT` 于 `:1080`）。仓库内无禁用代码。**"独立窗口应有工具栏"是代码级强推断，GUI 待验**——这是本案头号待验证项，任何修复方案都应先确认它在用户机器上的真实状态。
- 嵌入模式（`battery_chart_viewer.py:435` 起）裸建 `Figure`+`FigureCanvasQTAgg`，无 manager、无 toolbar，且生产路径不走（仅 wrapper 转发与测试调用）。四方一致，复核无异。

### 2.3 被 Round 1 全体忽略、但直接命中用户需求的事实：默认工具栏**不支持抓刻度区域拖动**
用户已澄清"拉动 = 抓住横/纵轴刻度区域拖动"。本地源码证实：
- pan/zoom 的启动命中过滤 `_ax_filter` 要求 `ax.in_axes(event)`（`backend_bases.py:2970-2975`）——在主 axes bbox **之外**（即刻度/轴标签区域）按下不会启动任何 pan/zoom。默认工具栏做不到"抓轴"。
- 工具栏的单轴约束是"pan/zoom 模式下**按住键盘 x/y 键**拖拽"：`drag_pan` 把 `event.key` 传给 `ax.drag_pan`（`backend_bases.py:3063-3075`），`drag_zoom` 显式 `if key == "x": ...`（`:3126-3140`）。依赖 canvas 键盘焦点，且不是用户要的手势。
- **推论**：只补工具栏（我第一轮的补丁 A/B）**不足以满足用户明确表述的诉求**。用户要的"抓刻度区域拖动"必须自研 hit-test + 单轴 set_xlim/set_ylim。这改变了修复清单的构成（见 §4），也是对 MiniMax "P0 补工具栏即可"路线的修正。

### 2.4 新发现的集成隐患：hover 回调与导航并发
`on_hover`（`hover_controls.py:100-119` 线性版、`:258-335` KDTree 版）在每个 `motion_notify_event` 上运行，**不检查 `canvas.toolbar.mode`、不检查 `canvas.widgetlock`**。一旦恢复 pan/zoom 拖动，拖动重绘与悬停最近点扫描（数百条曲线线性扫描）将并发执行——拖动卡顿、注释闪现风险（推断，需运行验证）。任何导航实现都必须带"导航期间抑制 hover"的互斥逻辑，DeepSeek 建议的 NavigationMixin + cid 登记是对的，应纳入最小方案而非"以后再说"。

### 2.5 对 DeepSeek "right-click reset 是旧自定义实现残留"的表述纠偏
旁证合理，但"曾存在后被移除"仍无 git 证据（他也自认无 shell）。在本轮应统一表述为："**文案承诺了不存在的行为**，是确定的文档级缺陷；其成因（曾实现后丢失 / 一直未实现）待历史核验"。我不接受把任何一方当作定论。

## 3. 根因模型（修正版，按证据强度排序）
1. **【代码级证实】假文案 + FixedLocator 组合造成"全功能失效"的感知**：帮助文字承诺滚轮/右键复位（`viewer_controls.py:36`）而默认工具栏无滚轮（`backend_bases.py:2825-2841`）、无抓轴手势（`:2970-2975`）；缩放后刻度不重排（`axis.py:2154-2170` + `figure_builder.py:39`）让即使成功的框选缩放也"看起来无效"。
2. **【代码级强推断，GUI 待验】独立窗口默认工具栏仍在，但 pan/zoom 需先点击按钮进入模式**（`backend_bases.py:3023-3040`），无可见引导、无菜单入口（图内菜单仅 File/Help，`viewer_controls.py:_add_menu_bar`），用户不知道也不习惯。
3. **【推断，无历史证据】**旧版本可能存在过自定义手势；无法用当前仓库证实或证伪（无 shell，git 未查）。
4. **【打包环境未知】**exe 中 toolbar 子模块收集是否完整未验证（build.py 的 hidden-import 问题，DeepSeek §2.3-3 的检查清单有效）。

## 4. 最小分阶段修复清单（matplotlib 优先，含验收；行数为设计估计非承诺，不给工期）

**阶段 A：诊断 + 兜底 + 去伪（先做，全部零架构改动）**
- A1 GUI 诊断脚本/日志：`plt_figure` 后记录 `type(fig.canvas.manager.toolbar)`、`toolbar.isVisible()`、`ax.get_xlim()`。验收：一次真实运行产出日志，锁定工具栏存在性与初始 xlim（是否被扩到 0）。
- A2 `figure_builder.py:37-39`：`ax.axis(self.listAxis)` 改为显式 `set_xlim/set_ylim`；刻度改 AutoLocator（或保留初始步长但缩放时重排）。验收：offscreen 测试断言初始 xlim == listAxis 定义值（而非被扩到 0），且手动缩小视窗后刻度数量变化。
- A3 防御性工具栏兜底：`fig.canvas.manager.toolbar` 为 None 时挂 `NavigationToolbar2QT`。验收：offscreen 测试断言 toolbar 非 None、`isinstance(toolbar, NavigationToolbar2QT)`、pan/zoom 模式可切换。
- A4 修 `viewer_controls.py:36` 假文案，改为与已实现功能一致的描述并纳入 i18n。验收：文案与功能清单逐条对应（评审人核）。

**阶段 B：滚轮缩放（自研 scroll_event）**
- 实现：以鼠标位置为锚缩放，默认双轴；`Ctrl+滚轮=仅X`、`Shift+滚轮=仅Y`（语义写进帮助文案）。参考 mpl 自带 `backend_tools.py` 的 scroll_zoom 思路自写，不改全局 rcParams。与工具栏 pan/zoom 模式互斥（mode 非 NONE 时忽略或先退出模式）。
- 验收：offscreen 合成 `scroll_event`：①xlim 按期望比例变化且以鼠标数据坐标为锚；②Ctrl 时 ylim 不变，Shift 时 xlim 不变；③按钮辅助 axes（`event.inaxes` 属按钮轴）上滚动无副作用。

**阶段 C：抓刻度区域拖动（用户明确诉求，自研单轴手势）**
- 命中区域：主 axes bbox 外扩约 15–25 px 的下带（X 轴刻度区）与左带（Y 轴刻度区）；`button_press_event` 命中后，`motion_notify_event` 按屏幕位移换算数据位移，只更新 `set_xlim` 或只更新 `set_ylim`；`button_release_event` 结束。命中判定须排除图内按钮轴（fig 顶部/左侧的按钮 axes 优先消费事件，且主 axes 判定用 bbox 带宽而非 inaxes）。
- 互斥三件套（验收硬条件）：①工具栏处于 PAN/ZOOM 模式时本手势不生效；②本手势拖动中 hover 回调被抑制（导航结束恢复，注释隐藏）；③mpl_connect 返回的 cid 全部登记，figure 关闭/重建时 disconnect。
- 验收：offscreen 合成 press/motion/release：①按住 X 刻度区拖动 → 仅 xlim 变化、ylim 逐值相等；②按住 Y 刻度区 → 仅 ylim 变化；③主绘图区中央拖动不触发本手势（避免与未来 pan 冲突）；④拖动中注释不可见；⑤重复建图两次后 cid 数不翻倍。

**阶段 D：回归与验收闭环**
- 现有 `tests/battery_analysis/main/test_battery_chart_viewer.py` 的菜单断言（File/Help）保持通过；新增导航测试文件独立存放。
- 手工验收清单（真实 GUI）：工具栏可见且按钮可用、滚轮/抓轴/框选三种方式互不干扰、过滤与电池切换后视野保留（对照 §1 修正结论）、重载数据后复位到默认视野、长数据下拖动跟手（记录主观卡顿，不做性能数字承诺）。

## 5. PyQtGraph vs Matplotlib 对照（用户要求的功能丰富度/易用性比较；不给无依据的天数/体积/性能倍数）

### 5.1 现有 matplotlib 功能 → pyqtgraph 迁移对照

| 现有功能（证据位置） | matplotlib 现状 | pyqtgraph 对应 | 迁移判定 |
|---|---|---|---|
| 曲线绘制（数百条 line，按电流档配色，`figure_builder.py:_plot_battery_curves`） | 成熟 | PlotDataItem 原生，曲线多时渲染机制更优（**方向性判断，本项目未测**） | 直接平移 |
| 过滤/电池可见性切换（`filter_controls.py:25-60`、`battery_selection.py:139-186`） | set_visible + draw_idle | setVisible 等价 | 状态模型可整体平移，**不需重写** |
| 悬停注释（线性扫描 `hover_controls.py:100-119`；KDTree 版因 scipy 不在依赖恒走线性） | 自研 | SigMouseMoved 事件 + 自写最近点逻辑；内置降采样 | 逻辑重写但需求等价；scipy 缺失问题在两个库下都存在 |
| 图内自绘按钮（FancyBboxPatch+transAxes，`button_widgets.py`、`battery_selection.py` 的 axes 按钮区） | 大量自研 | **无对应物** | 若迁移应改用 Qt 控件替代图内按钮（更简单但 UI 形态变化，需用户确认） |
| 菜单栏（`viewer_controls.py:_add_menu_bar` 依赖 `fig.canvas.manager.window`） | mpl manager 耦合 | 自建 QWidget + 原生 QMenuBar | **反而解耦**，更自然 |
| 抓刻度区域拖动/滚轮单轴缩放（本方案阶段 B/C 自研） | 自研（默认无） | ViewBox `setMouseEnabled(x=,y=)` 原生按轴独立平移/缩放、无模式手势 | **pyqtgraph 最接近用户手势语义**，但仍需配置，非零代码 |
| PNG/SVG 报告导出（plot_writer 走 backend_agg） | 同库一致 | 需**保留 matplotlib 双渲染并存**，样式一致性人工校准 | 长期成本点 |
| 刻度体系（MultipleLocator(0.2)、自适应需求） | 手动 locator | 自动刻度原生 | 简化 |

### 5.2 真正需要重写的边界（诚实清单）
- **必须重写**：figure_builder 的 gridspec+按钮轴布局体系、button_widgets 自绘按钮、hover 注释逻辑、test_battery_chart_viewer 的画布/菜单断言（全部依赖 mpl canvas）。
- **必须保留 matplotlib**：报告导出链路。即迁移后是双渲染器并存，不是替换。
- **可平移**：data_loader、过滤/电池的数据与可见性状态模型、交互状态机设计（若按阶段 B/C 实现成独立 NavigationMixin，其语义层可直接映射到 ViewBox）。
- **不评估的项**：打包体积变化、迁移工期、性能提升倍数——三者在本轮均无测量依据，拒绝给数。pyqtgraph 的性能优势是普遍经验方向，但在"数百条曲线、本项目数据形态"下的真实差距必须先基准测量再进决策，这正是把迁移挡在阶段 B/C 之后的理由。

## 6. 给执行方/下一轮的关键问题
1. GUI 实测结果（阶段 A1 日志）能否确认独立窗口工具栏在用户环境存在且可用？这决定阶段 A3 是"兜底"还是"主修复"。
2. 配置中 `axis_default[0]`（xmin）实际值是多少？若 >0，`set_xticks` 扩视窗的 bug 在当前版本真实发生，A2 从"优化"升级为"缺陷修复"。
3. 图内自绘按钮形态是否允许在 pyqtgraph 试点中改为 Qt 控件？（影响 §5.2 重写边界的规模。）

## 7. 残余风险
- git 历史未经核验（无 shell），"是否曾有自定义交互"保持不可知态。
- 所有交互手感、hover 并发影响、打包 exe 工具栏状态均待真实 GUI 验证。
- 我修正后的"过滤切换不重置视野"同样基于静态阅读，若用户实测与此矛盾，应优先怀疑存在未读到的重入路径（如某处触发 plt_figure 重入），届时以运行日志为准。

---
