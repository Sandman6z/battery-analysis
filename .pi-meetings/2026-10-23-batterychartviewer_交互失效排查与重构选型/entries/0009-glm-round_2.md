# GLM (Round 2): GLM / Round 2：修正过滤切换误判、核实工具栏与抓轴手势边界、分阶段最小修复清单

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