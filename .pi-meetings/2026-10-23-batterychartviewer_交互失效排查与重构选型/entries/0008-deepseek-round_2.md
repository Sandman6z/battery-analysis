# DeepSeek (Round 2): DeepSeek / Round 2：勘误三处事实、核验轴带拖动与工具栏单轴的语义差异，给出行为级测试

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
