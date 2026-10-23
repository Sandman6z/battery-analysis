# MiniMax (Round 1): MiniMax / Round 1：交互代码盘点、matplotlib 能力边界与"交互意图层"选型建议

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
