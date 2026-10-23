# DeepSeek (Round 2): 撤回首轮"每worker重新解压"与"optimize=1去docstring"两处错误，强化no-clean失效根因，并按收益机制/成本/风险重排五项优先级。

# DeepSeek · Round 2 机制交叉复核

> 纪律：只读源码，无任何实测数字。能定位到文件与行号的为事实；机制以 PyInstaller 长期稳定行为为准，凡无法在本工作树本地核对的官方细节一律标「待核实」，不当作事实。

## 一、首轮自身观点的保留 / 修正 / 反驳

### 1.1 撤回（首轮核心论据错误）：onefile 下「每个 spawn worker 重新解压」

首轮原话（见 0001-deepseek-round_1.md 第 3 条与张力矩阵）：「每个 worker 重跑 bootloader→重新解压/重导入 numpy/pandas/NewareNDA」「转换场景内存/启动放大 N 倍」。**「重新解压」这一半撤回。**

实际机制（PyInstaller onefile，本仓库锁 `pyinstaller>=6.10,<7.0`，该机制自 3.x 起长期存在，远早于 6.x）：

- 父进程 bootloader 把归档解包到 `%TEMP%\_MEIxxxx`，随后把该解包目录通过**环境变量传给子进程**（确切变量名 `_MEIPASS2` 待以已安装版本 bootloader 源码核对）；
- Windows 下 `multiprocessing` spawn 重新执行 exe 时，子进程 bootloader 检测到该变量即**复用父进程解包目录，不再重新解包**。

因此：GPT 的质疑正确，我首轮论断被证伪大半。结论变更如下——

- 保留的一半：「每个 worker 各自重导入 numpy/pandas/NewareNDA」成立，但其性质是 **spawn + ProcessPoolExecutor 的进程内存语义**，onefile 与 onedir 下**完全等价**，不是 onefile 特有的放大。
- 推论：**onefile↔spawn 的「结构性冲突」被大幅削弱**。onedir 的正当理由是冷启动解包与分发形态（GPT 框架），**不是** NDAX 批量转换吞吐。这直接改变优先级：转换场景的问题应重新定位为「每 worker 独立加载重库的内存放大 + spawn 启动开销」，而非「onefile 解包」。

### 1.2 撤回（措辞错误）：`--optimize=1` 「去 docstring」

Python `-O`（optimize=1）只移除 assert 并置 `__debug__=False`，**不移除 docstring**；docstring 移除是 `-OO`（level 2）。`scripts/build.py:258` 注释「去除 docstrings 和 assert 语句」本身错误。**GPT 正确，GLM 与我错误。**

推论：当前 `--optimize=1`（build.py:259）对体积的收益≈0（依赖库内 assert 稀少），别指望它缩体积；不建议为此升到 `--optimize=2`（删 docstring 有反射风险，收益极小）。

### 1.3 补充：`--strip` 在 Windows 上近零收益且官方不推荐

`scripts/build.py:256` Release 才加 `--strip`。PyInstaller `--strip` 帮助原文为「Apply a symbol-table strip to the executable and shared libs (not recommended for Windows)」（待以实际版本 `--help` 核对）。Windows PE 通常无同语义符号表，效果近零，还可能降低可调试性。**这是候选移除项**（单变量验证），而非「体积优化杠杆」。

### 1.4 强化：`--no-clean` 不保留增量缓存的根因在「每次构建末尾删 workpath」

首轮我归因为「无 .spec 即全量重打」，不够准确。修正：

- PyInstaller 的增量分析缓存（`Analysis-*.toc` 等）保存在 `--workpath`（`scripts/build.py:223` = `__temp__/BatteryAnalysis`）下，**与是否有 .spec 无关**；
- 真正使缓存失效的是 build.py 在每次成功构建末尾**无条件删除 workpath**：
  - `build()` 末尾 `shutil.rmtree(temp_path)`（`scripts/build.py:313`）；
  - `_verify_and_clean()` 再 `shutil.rmtree(self.temp_build_dir)`（`scripts/build.py:162`）。
- 因此 `--no-clean`（build.py:83 只跳过前置清理，见 build.py:79-84）对「重复构建提速」基本无效——**GPT 判断正确**。

修复方向：若需开发期增量，让 workpath/Analysis 缓存在两次构建间存活，或把缓存目录与一次性临时产物分离。纯构建脚本改动，收益=重复构建时间（可测量）。

### 1.5 修正：入口改 launcher 的收益=感知性启动（splash 更早），非可交互提前

已核实：`main_window.py:22-24` 的模块级 import 链（`window_init.py:11-18` → `managers/initialization_manager.py` 12 个 step）只含 PyQt6 + 纯 Python 业务模块；`main/initialization/`、`main/managers/`、`main/ui_components/` 顶层**均无** matplotlib/pandas/numpy/NewareNDA 导入（grep 证实）。重库由 `battery_chart_viewer.py:25-26`、readers 等**延迟**加载。

因此入口切换只把「纯 Python import 图」挪到 splash 之后，**不改变 time-to-interactive**；收益是感知性（splash 更早出现）+ 双入口一致性。首轮「更晚重导入」措辞应更正为「更晚重导纯 Python 模块图」。与主持人待复核项 #4 一致：闪屏更早≠主窗口更早可操作（`main_window.py:79` 的 `QTimer.singleShot(0, _deferred_init)` 仍在主线程同步执行，见 window_init.py:30-47）。

### 1.6 修正：显式 `get_context("spawn")` 是死代码

首轮引用 `utils/resource_manager.py:96` 的 `multiprocessing.get_context("spawn")`；核实该函数与 `get_optimal_process_count` 在 src 中**无任何调用点**（grep 仅命中定义处）。实际并行路径是 `ndax/converter.py:229` 与 `ndax/worker.py:92` 的 `ProcessPoolExecutor`（Windows 默认即 spawn）。结论（spawn 生效）不变，但证据引用应更正为 ProcessPoolExecutor 默认行为。

### 1.7 保留不变的事实（首轮已验证，仍成立）

- 构建=PyInstaller onefile（`scripts/build.py:224`），入口=main_window.py（`scripts/build.py:107-110`）。
- `_version=5.0.2`（`src/battery_analysis/_version.py:9`）vs 现存产物 `4.0.1` 不一致。
- matplotlib 双后端硬需求（`application_initializer.py` QtAgg / `plot_writer.py` Agg）。
- 三 Excel 引擎语义不同，去重空间有限。
- config/ 未打包且仓库无 config.json（无功能影响）。
- `multiprocessing.freeze_support()` 已在 `main_window.py:117` 与 `launcher.py:55`（符合 PyInstaller multiprocessing 配方）。

## 二、逐条回应主持人待复核项

1. **spawn 解包** → 见 1.1，撤回「重新解压」。
2. **optimize=1** → 见 1.2，GPT 正确。
3. **no-clean** → 见 1.4，根因是末尾删 workpath，与是否有 spec 无关。
4. **延迟≠后台** → 同意；`QTimer.singleShot(0)` 仍主线程同步执行，splash 早≠可交互早。
5. **历史体积/计时** → 同意；CHANGELOG 的 78MB 与 ndax 20.8s 均为历史文档数字，不得作当前基线。
6. **冷启动定义** → 同意；onefile 每次启动解包到**新的唯一 `_MEIxxxx`** 目录，热启动仍会重新写盘（仅源 exe 字节可能被 OS 缓存）。基准须分离：首次/重复运行、OS 文件缓存、应用缓存（如 matplotlib font cache）；不要清空整个 TEMP 或删除运行中进程的 _MEI 来模拟冷启动（会破坏子进程复用机制并污染测量）。

## 三、影响优先级的关键结论变更

- P0 从「onedir 评估」调整为「**建立当前版本可追溯基线 + 测量**」（体积清单 / 冷热启动 / NDAX 峰值 RSS 三件套）。
- onefile 的 NDAX 转换代价被证伪大半；真正风险是「每 worker 独立内存（numpy/pandas/NewareNDA × N）」+ spawn 启动开销，与 onefile 无关，应单独测。
- 体积侧现有 flag（optimize=1 / strip）已近无效；真正杠杆 = UPX（环境依赖、AV 风险）与按清单定向裁剪，必须先测量后动手。

## 四、Top 5 建议（按 收益机制 / 成本 / 风险 排序，附单变量实验）

### 1. P0 建立可追溯基线 + 三件套测量
- 收益机制：后续一切决策（体积/启动/转换）的事实基础；成本：低；风险：低。
- 做法：重新构建 Release（确认 `_version=5.0.2` 生效），记录 Python/PyInstaller/Qt/UPX 版本、锁文件、提交、产物哈希与字节数；`pyi-archive_viewer -l` 列出 PYZ/CArchive 成员按大小排序（找 top-10 贡献者）；冷/热启动分别计时到 splash/主窗口/可交互（复用 window_init.py:52 的 elapsed 日志 + 外部打点），分离首启/复启/OS 缓存/应用缓存；NDAX 固定 fixture 测吞吐 + 进程树峰值 RSS（psutil），扫 worker 数。
- 单变量：每次只改一个维度。

### 2. P1 修构建缓存：让 workpath/Analysis 缓存在两次构建间存活
- 收益机制：直接削减重复构建时间（当前每次末尾删 workpath 使 PyInstaller 增量分析失效）；成本：低（改 build.py 清理时机）；风险：低（.toc 以源文件 mtime 天然失效，防陈旧污染）。
- 单变量：同源两次构建（首次 clean vs 第二次保留 workpath），记录总时长与 PyInstaller 分阶段耗时，验证 .toc 是否命中；删除 build.py:313/162 对 workpath 的无条件 rmtree（改为仅删一次性临时产物，正式发布仍保留显式 clean 路径）。

### 3. P1 统一入口 main_window → launcher
- 收益机制：splash 更早的**感知性**启动 + 消除双入口认知/维护负担；成本：低；风险：低-中（需回归 launcher 委托链 + 冻结态资源路径）。
- 单变量：仅切入口，其余参数不变；测 splash 出现时刻与主窗口可交互时刻，对比 main_window 入口；跑冻结冒烟（i18n/style_manager 的 `_MEIPASS` 资源，见 i18n/__init__.py:20-22、style_manager.py:23-24）。
- 注意：**不宣称**它缩短可交互时间（见 1.5）。

### 4. P2 体积单变量实验（在 P0 清单之后）
- 收益机制：体积；成本：低-中；风险：UPX 有 AV 误报/冷启动变慢，裁剪有动态 import 缺失风险——全部单变量 + 回归。
- 做法：(a) 移除 `--strip`（Windows 官方不推荐，近零收益）；(b) UPX 开/关 A/B（记录体积、冷启动、AV 扫描结果）；(c) 按清单定向裁剪（mpl-data 字体、Qt 插件、NewareNDA 实际体积）。
- 注意：`--optimize=1` 已近无效，不要为此升 `--optimize=2`。

### 5. P2 转换运行时：测 per-worker 内存放大与 spawn 开销拐点
- 收益机制：NDAX 批量转换的峰值 RSS 与吞吐；成本：低（仅测量+调参）；风险：低。
- 单变量：worker 数扫描（1 / 2 / 预算值 / 61 上限，见 concurrency_policy.py:41）；测 `xlsxwriter.Workbook(constant_memory=True)` 降内存 vs 写速；测文件数少时 spawn 开销 vs 单进程串行收益拐点。
- 可选（运行效率、与体积无关）：预置 `MPLCONFIGDIR` / 预热 matplotlib font cache，单变量验证首帧图时间。

## 五、待核实（无实测不编数字，禁止当事实）

- `_MEIPASS2` 确切变量名与复用条件，以已安装 PyInstaller 版本 bootloader 源码为准（机制本身——子进程复用父进程解包目录——为长期稳定行为）。
- `--strip` 在 Windows 上的确切帮助原文与实际对 PE 的影响（需同机 A/B）。
- 当前 exe 实际字节数与 top 体积贡献者（未实测）。
- NDAX 转换峰值 RSS 与 spawn 拐点（未实测）。
- UPX 对 Qt/numpy DLL 的压缩率与 AV 结果（未实测）。

## 六、残余风险

- 若未来激活 `resource_manager.get_processing_context` 死代码或更换 start method，需重验 _MEI 复用是否仍成立。
- 删除 workpath rmtree 后需确保 CI 干净构建路径仍显式存在。
- 入口切换后 launcher 委托链与 `config_utils.py:205-217` 的可执行目录相对路径语义在 onedir/只读安装目录下不同，需冒烟。
