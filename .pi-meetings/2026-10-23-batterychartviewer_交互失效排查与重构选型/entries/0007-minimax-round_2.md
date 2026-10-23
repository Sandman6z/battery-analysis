# MiniMax (Round 2): MiniMax / Round 2：更正第一轮过强断言（单轴、垂直 RangeSlider、从未实现、拖轴差异不大、视图重置），并给出 Matplotlib 优先的轴区拖动落地方案与 PyQtGraph 逐项绘图能力对照

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
