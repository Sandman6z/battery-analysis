# GPT (Round 2): 纠正互相矛盾的导航断言，以刻度区命中控制器最小修复 Matplotlib

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