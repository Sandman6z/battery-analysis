# GPT (Round 1): 从入口与能力契约定位交互缺口：先恢复导航链路，再以指标决定替换

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