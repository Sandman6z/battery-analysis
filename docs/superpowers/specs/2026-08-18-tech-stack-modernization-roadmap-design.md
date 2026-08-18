# 技术栈现代化路线图设计：性能提升、依赖清理与架构收敛

## 背景与目标

BOEDT Battery test GUI Tool（PyQt6 + pandas/matplotlib，~32k 行 Python，v2.14.0）经历多年迭代后，存在三类问题：

1. **过时 / 停止维护的依赖**：`xlrd==1.2.0` 已停更（2020）却被用于读 `.xlsx`；i18n 手写 `.po` 解析器含 `eval()` 代码注入风险；matplotlib 参数名已随新版弃用。
2. **性能瓶颈**：pandas 向量化被放弃后进入纯 Python 三重循环；主线程同步执行重活（Excel 解析、SHA-256、同步等待进程池）；图表 hover 为 O(总点数) 线性扫描并伴随全图重绘。
3. **架构冗余与确定性 bug**：三套并发模型并存、双事件总线、仪式性 Command/Presenter 空壳、服务容器非真正 DI；多处运行时必抛异常被裸 `except` 吞掉。

**目标**：产出一份分阶段的现代化路线图（评估 + 规划，不实施），按"先修 bug → 再换库 → 最后架构收敛"的顺序，每阶段独立分支 + PR 交付，重点缓解三个实际痛点——**启动慢、大数据处理慢、图表交互卡**。

## 需求澄清结论

| 决策点 | 结论 |
|---|---|
| 项目定位 | 两者兼顾（内部使用 + 对外分发），优先稳定与可验证，框架级改动谨慎 |
| 产出形态 | 评估 + 路线图（只规划，不实施） |
| 痛点优先级 | 启动慢、大数据处理慢、图表交互卡（报告生成/排版未列为痛点） |
| 图表演进方向 | **matplotlib 嵌入 `FigureCanvasQTAgg`** + 按钮改 Qt 控件 + KDTree hover（不迁 pyqtgraph，避免双栈） |
| 打包形态 | **暂不涉及**（onedir/安装器不在本路线图内） |
| 换语言 | 明确不推荐（Rust/Tauri 重写收益低风险高，32k 行 Python 重写代价不可接受） |
| 交付流程 | **每阶段独立分支 + 测试通过后 PR 合入 main** |

## 现状评估

### 一、过时 / 停止维护的依赖

| # | 问题 | 位置 | 建议替代 |
|---|---|---|---|
| 1 | `xlrd==1.2.0` 已停更（2020），却用 `open_workbook` 读 `.xlsx`（非 `.xls`）；回退路径"更慢更脆弱"纯属负资产 | `pyproject.toml:36`、`xlsx_reader.py:35`、`battery_analysis.py:25,349` | 移除 xlrd；日期提取改 calamine 读前 20 行 |
| 2 | openpyxl 纯 Python 读大文件慢，且同一文件被解析 3 遍 | `xlsx_reader.py:14-16` | `pandas engine='calamine'`（Rust，读 xlsx 快 5-10 倍）+ 一次 `sheet_name=[0,1,2]` |
| 3 | 手写 `.po` 解析器 + 手写复数公式编译，用 `eval()` 编译 .po 文件公式——损坏/恶意翻译文件可代码注入；多行 msgstr 漏译 | `i18n/translator.py:15-95,135-229` | `gettext.GNUTranslations` 或 polib/babel |
| 4 | matplotlib `boxplot(labels=)` 已弃用（3.9+ 改名 `tick_labels=`）；backend 判断 `'QtAgg'` 与 3.10 返回 `'qtagg'` 大小写不匹配恒为真 | `plot_writer.py:77`、`battery_chart_viewer.py:177`、`figure_builder.py:189` | `tick_labels=`；backend 判断改小写 |

### 二、框架级决策问题

| # | 问题 | 位置 | 建议 |
|---|---|---|---|
| 5 | **matplotlib 未嵌入主窗口**：用 pyplot 全局状态弹独立顶层窗口（`plt.figure()`/`plt.show(block=False)`），QSS 里 `FigureCanvasQTAgg` 样式是死代码；"按钮"全是 `FancyBboxPatch` + `ax.text` 假按钮，交互靠手写坐标命中检测（已多次因 pad/DPI 错位出 bug） | `battery_chart_viewer.py`、`figure_builder.py`、`interaction_controls.py` | 嵌入 `FigureCanvasQTAgg` + 按钮改 Qt 控件 |
| 6 | **三套并发模型并存**：QRunnable（`AnalysisWorker`）、`QThread`+`moveToThread`（含已弃用 `BackgroundWorker`、`QThread.terminate()`）、`concurrent.futures`；`QThreadPool` 初始化"并行"实为死代码（每优先级组恒 1 步骤） | `data_processor.py`、`workers/task_runner.py`、`business_logic/background_worker.py`、`initialization_orchestrator.py:116-160` | 统一到 `TaskRunner`+`TaskManager`，去 `terminate()` |
| 7 | **服务容器非真正 DI**：字段型 dataclass + 恒等 `_name_map` + `getattr` 字符串取服务，`register()` 废弃却留空签名；**双事件总线**（`services/event_bus.py` vs `utils/domain_events.py`）；**Command/Presenter 多为仪式性空实现**；UIBridge 字符串拼接 `getattr` 查控件且 Manager 仍直接访问 `main_window.comboBox_X`，迁移半途而废 | `container.py`、`event_bus.py`、`report_commands.py`、`main_presenter.py`、`app_context.py` | 收敛：删空壳，或真正 DI |

### 三、性能瓶颈

| # | 问题 | 位置 | 对症 |
|---|---|---|---|
| 8 | pandas 列 `.tolist()` 降级回 Python list 后进入纯 Python 三重嵌套循环（脉冲匹配、电荷计算、统计），向量化被放弃 | `battery_analysis.py:299-304`、`pulse_matcher.py:74-101`、`charge_calculator.py:74-86`、`statistics_utils.py:10-72` | **大数据处理慢** |
| 9 | 主线程同步执行重活：扫描后逐文件 `pd.read_excel`（冻结 UI）、SHA-256 哈希全部文件、`ProcessPoolExecutor` 同步等待 | `data_processor.py:166,411-421`、`version_manager.py:54` | **启动慢 + 图表卡** |
| 10 | hover 最近点 O(总点数) 线性扫描 + 每次 mousemove 全图 `draw_idle()` 重绘风暴；每按钮挂常驻 mousemove 回调 | `interaction_controls.py:397-448` | **图表交互卡** |
| 11 | `ProcessPoolExecutor` 提交绑定方法（`self` 不可 pickle），Windows spawn 下实际失效并被 `except` 静默吞掉 | `data_processor.py:138-145,411-418` | **大数据处理慢** |
| 12 | `psutil.cpu_percent(interval=1)` 阻塞主线程 1 秒 | `resource_manager.py:43` | 启动慢 |
| 13 | `resizeColumnsToContents()` 在 `resizeEvent` 中高频触发 | `main_window.py:542-547` | 图表卡 |
| 14 | `data_loader.py` 先 `list(csvreader)` 全量读入再 `seek(0)` 二次遍历（双倍 I/O） | `data_loader.py:198-226` | 图表卡 |

### 四、确定性 bug

| # | 问题 | 位置 |
|---|---|---|
| 15 | `QMessageBox.error()` 在 PyQt6 中不存在（只有 information/warning/critical）→ 必抛 AttributeError 被裸 except 吞掉 | `data_processor.py:439` |
| 16 | 电池按钮"索引→曲线"映射错误：曲线按电池主序构建，切换逻辑按电流档主序索引，多电流档时点一个电池切换 3 个不同电池的曲线 | `interaction_controls.py:187-188,321-322` vs `figure_builder.py:61-62` |
| 17 | 悬停永远用 Filtered 数据：`check_filter` 实为 dict，对其调 `.get_status()` 必抛异常，被 except 吞掉后固定回退 `lines_filtered` | `interaction_controls.py:399-405` |
| 18 | 报告"Filtered 图"画的其实是原始数据（`[0]/[1]`），过滤后数据 `[2]/[3]` 已算却未用 | `plot_writer.py:105,142-145` |
| 19 | `data_utils` 缺 `import logging`，fallback 分支触发 NameError | `utils/processors/data_utils.py` |
| 20 | Gitee token 拼进 remote URL 后又被 `git remote -v` 打印 → 凭据泄漏到 CI 日志 | `.github/workflows/sync-to-gitee.yaml:62,65` |
| 21 | 构建失败被吞掉、CI 仍报绿：`build.py` 用 `check=False` 且忽略 returncode | `scripts/build.py:242,249,435` |
| 22 | "第五页空白页"（README 已知问题）：Overview 大表插入锚点在封面页 + `intStepOut` 段落计数启发式，配合模板固定分页符/写死 TOC 页码 | `word_report_writer.py:502-520`（线索，暂列 backlog） |

### 五、构建 / 发布 / CI

| # | 问题 | 位置 |
|---|---|---|
| 23 | CI 不用 `uv sync --frozen`（锁文件形同虚设）；`uv add flake8` 会改写 pyproject.toml/uv.lock | `.github/workflows/ci-cd.yaml:30-47` |
| 24 | release 上传用 github-script `fs.readFile` 把整个 exe 读进 Node 内存，慢且易 OOM | `ci-cd.yaml:148-166` |
| 25 | 版本升级 + CHANGELOG 完全手工，`generate_changelog.py` 未接 CI；README 多处文档漂移 | `_version.py`、`README.md:113-137` |
| 26 | `--onefile` + UPX 对 PyQt6+matplotlib+pandas 非最优（启动解压慢、AV 误报高）；Nuitka 文档与实现脱节 | `scripts/build.py:349,388-398`（**本路线图暂不涉及**） |

## 现代化路线图

### 设计原则

1. **阶段独立**：每阶段可单独交付、回归、发版，阶段间无硬依赖。
2. **先止血后优化**：确定性 bug（错误数据 > 慢）永远排在性能优化前。
3. **测试门槛**：每项改动前先补回归测试，涉及性能的建立基准。
4. **范围锁定**：打包形态、换语言、pyqtgraph 迁移明确不在本路线图内。

### 阶段总览

| 阶段 | 主题 | 对症痛点 | 风险 |
|---|---|---|---|
| P0 | 止血：确定性 bug + 可观测性 | 全部的基础 | 低 |
| P1 | 数据读加速 | 大数据处理慢 | 低-中 |
| P2 | 核心算法向量化 | 大数据处理慢（核心） | 中 |
| P3 | 主线程解阻塞 | 启动慢 + 图表卡 | 中 |
| P4 | 图表演进：Qt 嵌入 | 图表交互卡（核心） | 中-高 |
| P5 | 架构收敛 | 长期可维护 | 高 |

### P0 — 止血（修复确定性 bug + 可观测性）

**目标**：消除确定会触发的运行时错误、数据错误、凭据泄漏与 CI 假绿。

- `QMessageBox.error()` → `QMessageBox.critical()`（#15）
- 电池按钮"索引→曲线"映射统一为电池主序（#16）
- 图表悬停修复：维护真实过滤状态，替换对 dict 调 `.get_status()`（#17）
- 报告 Filtered 图改用过滤后数据 `[2]/[3]`（#18）
- `data_utils` 补 `import logging`（#19）
- Gitee 同步改 `http.extraheader` 传递凭据，不打印带凭据 remote（#20）
- `build.py` 检查 PyInstaller returncode，失败 `sys.exit(1)`（#21）
- 启动/图表路径裸 `except` 改 `logger.exception`，区分可恢复/致命（#4 可观测性）

**验收**：每项有回归测试；CI 全绿。

### P1 — 数据读加速

**目标**：大文件读取提速 5-10 倍。

- 移除 `xlrd==1.2.0`：日期提取改 pandas/calamine 读前 20 行；删除 xlrd 回退路径；移除模块级 import（#1）
- openpyxl → calamine：`xlsx_reader` 一次 `sheet_name=[0,1,2]` 读三表；预览/校验加 `nrows`（#2）
- `excel_utils.num2letter` 改用 `xlsxwriter.utility.xl_col_to_name`，去掉 openpyxl 耦合
- `data_loader` 去掉 `list(csvreader)` + `seek(0)` 双读（#14）

**验收**：大文件读取基准提升 5-10 倍；`xlrd` 从依赖移除；calamine 类型差异过回归。

### P2 — 核心算法向量化

**目标**：大数据量下核心计算提速 10-100 倍。

- `battery_analysis` 保持 numpy 数组，不再 `.tolist()` 降级（#8）
- `pulse_matcher` 一次性 `np.asarray * 1000` + 广播比较（替代三重嵌套循环）
- `charge_calculator` 用 `np.searchsorted` 批量定位 + `to_dict`/`to_numpy` 预转换
- 统计量 2D numpy 批量 `mean/std`
- 消除 `ProcessPoolExecutor` 假并行：改模块级可 pickle 函数，或改后台线程 + pandas 批量（#11）

**验收**：几万行 record 基准提速 10-100 倍；脉冲边界回归。

### P3 — 主线程解阻塞

**目标**：消除 UI 冻结，改善启动与交互响应。

- 扫描后 Excel 解析、SHA-256 校验和、`analyze_data` 全部移入后台 worker（#9）
- 移除 `progress_dialog`/`theme_manager`/`launcher` 的 `processEvents()`（防重入）
- `cpu_percent(interval=1)` → 非阻塞采样（#12）
- `resizeColumnsToContents` 首次/数据变化才调用 + 去抖（#13）

**验收**：大文件扫描/报告生成时 UI 不冻结；操作可中断、可回退。

### P4 — 图表演进（Qt 嵌入）

**目标**：图表交互流畅，告别假按钮/游离窗口/跨线程问题。

- pyplot 独立窗口 → `FigureCanvasQTAgg` 嵌入主窗口；按钮改 Qt 控件（QCheckBox 列表放左侧面板）（#5）
- hover 最近点改 KDTree 预建索引 + mousemove 节流（#10）
- `threading.Timer` 改 `QTimer.singleShot`；修 backend 大小写；图表窗口生命周期统一管理（消除 `plt.close('all')` 全局副作用）
- 报告生成脱离全局 pyplot/backend 切换：`Figure` + `FigureCanvasAgg` 后台线程出图

**验收**：查看器嵌入主窗口；96 线悬停流畅；QSS `FigureCanvasQTAgg` 样式生效；图表回归测试。

### P5 — 架构收敛

**目标**：消除并发/依赖/事件多重实现与仪式性抽象，消除 eval 注入风险。

- 并发模型统一到 `TaskRunner`+`TaskManager`，删 `BackgroundWorker`/`AnalysisWorker`/`QThread.terminate()`（#6）
- 服务容器删 `_name_map`/`register` 死代码（或引入轻量 DI）；双事件总线统一（#7）
- 删 Command/Presenter 空壳，Manager 直接承接；UIBridge 迁移完成或回退
- i18n 手写 `.po` 解析 + `eval()` → `gettext.GNUTranslations`/polib（#3）
- 启动延迟导入 pandas/matplotlib；配置默认值移到 JSON 资源

**验收**：并发/依赖/事件单一实现；启动更快；pylint 全绿。

## 交付流程

- **分支规范**：每阶段从 `main` 拉独立功能分支：
  `feat/p0-bugfixes` · `feat/p1-read-acceleration` · `feat/p2-vectorization` · `feat/p3-unblock-ui` · `feat/p4-chart-embed` · `feat/p5-architecture`
- **阶段内节奏**：每项改动**先补回归测试**（TDD）→ 本地 `pytest` 全绿 + `pylint` 通过 → 提交到阶段分支
- **PR 门槛**：push 分支 → 创建 PR → CI（flake8 + pytest + 构建）作为合并门槛 → 审查通过后合入 `main`
- **审查方式**：可结合 code-review 技能做变更审查（自审 / Claude 协助 / 两者）
- **节奏**：一个阶段合并后立即开始下一阶段分支，不跨阶段累积变更

## 范围边界（明确不做）

- ❌ 打包形态（onedir/安装器）——已定暂不涉及
- ❌ 换语言（Rust/Tauri 等）——收益低风险高
- ❌ pyqtgraph/QtCharts 迁移——已定 matplotlib 嵌入
- 📌 **backlog 注明**：第五页空白页（#22）——已定位线索（Overview 表插入锚点在封面页 + 段落计数启发式），P0/P4 触及 `report_coordinator`/`word_report_writer` 时顺手修或单列阶段

## 测试与验收策略

- **TDD 门槛**：每项改动先写/补回归测试再改，P0 的 bug 修复必须有对应测试锁定
- **基准测试**：为 xlsx 读取（P1）、核心计算（P2）、hover（P4）各建立 benchmark，前后对比验收
- **回归重点**：calamine 类型差异、脉冲边界、电池按钮映射、多电流档切换
- **CI 门槛**：flake8 + pytest + 构建（现有 ci-cd.yaml），作为 PR 合并条件
- **已知风险**：P4 需重写 `plt_figure` 与 `InteractionControlsMixin`，工作量中等；P5 的 DI 化改造影响面大，若风险超预期可降级为"删除死代码"而非全面 DI
