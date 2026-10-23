# Meeting: 单EXE打包、体积与运行效率优化研讨
如何优化exe的运行效率
> Created: 2026-10-22T05:43:28.569Z
> Type: Brainstorming (3 rounds)

---

## DeepSeek (Round 1): 系统视角：实际打包走PyInstaller而非Nuitka，入口选择绕过了launcher的闪屏优先设计，onefile与spawn多进程存在结构性冲突。

# 系统视角 · 单exe打包与运行效率（Round 1）

> 范围：只读研究工作树。所有速度/体积数字均**未实测**，标注为待实测；能定位到文件与行号的均为**事实**；机制性结论为**推断**，已标注。

## TL;DR（结构化结论）

1. **实际构建是 PyInstaller，不是 Nuitka**。`docs/NUITKA_BUILD.md` 只是文档，Makefile/`scripts/build.py` 全链路走 PyInstaller（`--onefile`）。文档与实现存在双轨偏差。
2. **打包入口选错导致"闪屏优先"设计失效**：入口是 `main_window.py`，其顶层 import 三个 Mixin → `window_init` → `InitializationManager` → 12 个 step → 大量 controller/manager/ui_components。模块级导入在 `main()`（及 splash）之前就展开；而 `launcher.py` 的"先 splash 再 import 主模块"的最轻量启动路径被绕过。
3. **onefile 与 spawn 多进程是结构性冲突**：NDAX 转换用 `ProcessPoolExecutor`（spawn），onefile 下每个 worker 重跑 bootloader→重新解压/重导入 numpy/pandas/NewareNDA，worker 数越大代价越高。这是本项目"打包方式↔运行效率"最尖锐的相互制约点。
4. **体积大头在第三方二进制（Qt/matplotlib/pandas/numpy），`--optimize=1`/`--strip` 只作用于字节码与符号，对总体积贡献有限**。matplotlib 需同时保留 QtAgg（交互）与 Agg（离屏报告）两套后端，无法靠砍后端省太多。
5. **现存构建产物与源码版本不一致**：`build/Release/battery-analyzer_4.0.1_x64.exe`，而 `src/battery_analysis/_version.py:9` 为 `5.0.2`——产物陈旧，不能作为体积/启动的可靠基准，需重新构建后测量。

---

## 一、当前构建命令与事实基线

### 事实：真实构建入口

- `Makefile:25` → `build: uv run python scripts/build.py Release`（Debug 对应 `scripts/build.py Debug`，`Makefile:28`）。
- `scripts/build.py:196` → `--onefile`；`scripts/build.py:250` → `--optimize=1`；`scripts/build.py:242` → Release 才 `--strip`；`scripts/build.py:256` → 无 UPX 时 `--noupx`；`scripts/build.py:262` → `--copy-metadata=numpy`。
- 入口文件：`scripts/build.py:107-110`（`apps_config.main_file_path`）→ `src/battery_analysis/main/main_window.py`，随后 `cmd_args.append(str(app_config["main_file_path"]))`。
- 输出名：`scripts/build.py:157` → `battery-analyzer_{version}_x64.exe`（`base_exe_name="battery-analyzer"`）。
- 打包工具链来源：`pyproject.toml` `[project.optional-dependencies].build = ["pyinstaller>=6.10.0,<7.0.0"]`。

### 事实：文档与实现的偏差

- `docs/NUITKA_BUILD.md` 全文给的是 Nuitka 命令；但 Makefile 无任何 nuitka target，`scripts/` 无 nuitka 脚本。**Nuitka 未接入实际构建**（推断：文档为历史遗留/备选方案）。
- `docs/NUITKA_BUILD.md` 的 Nuitka 命令含 `--include-data-dir=config=config`，但实际 `scripts/build.py:205-215` 的 `--add-data` 只有三类：`templates`、`ui/styles`、`locale`，**未打包 `config/`**。由于 `config/` 目录里只有 `resources/icons/Icon_BatteryTestGUI.ico`（构建期 `--icon` 已内嵌），且 `config_utils.py:104` 的 `find_config_file("config.json")` 在仓库里无 `config.json`，运行时回退到 `utils/config_defaults.py` 的 `DEFAULT_CONFIG`——因此**不打包 config/ 目前无功能影响**（事实+推断）。

### 事实：版本不一致

- `src/battery_analysis/_version.py:9`：`__version__ = "5.0.2"`。
- `build/Release/` 现存 `battery-analyzer_4.0.1_x64.exe`。
- 结论：现有 exe 为旧版本产物，**体积/启动数字不能引用它**，需以 `5.0.2` 重新构建后实测。

---

## 二、构建依赖图（事实 + 推断）

### 运行时第三方依赖（`pyproject.toml` dependencies）

PyQt6、matplotlib、numpy、pandas、NewareNDA、openpyxl、python-calamine、xlsxwriter、python-docx、psutil、pywin32。

### 体积/复杂度关键角色（推断排序，未实测）

1. **PyQt6**（最大候选）：QtCore/QtGui/QtWidgets 三套 DLL + `platforms/`、`imageformats/`、`styles/` 等插件目录。`scripts/build.py:168-190` 已排除不用的 Qt 子模块（Multimedia/WebEngine/Qml/DBus/Bluetooth 等），但 Qt 本体仍是大头。
2. **matplotlib**：双后端要求——
   - 交互：`main/application_initializer.py:127` `matplotlib.use("QtAgg")`；`main/battery_chart_viewer.py:457` `from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg`。
   - 离屏报告：`utils/report_coordinator.py:37` `matplotlib.use("Agg")`；`utils/writers/plot_writer.py:11` `backend_agg.FigureCanvasAgg`。
   - 两套后端 + `mpl-data`（字体/数据文件）都需收集。
3. **pandas + numpy**：pandas 额外拉 dateutil/pytz/tzdata 等；numpy 的 C 扩展 DLL 由 PyInstaller 追踪 + `--copy-metadata=numpy`（`scripts/build.py:262`，注释解释了为何不用 `--collect-submodules=numpy`）。
4. **NewareNDA**（`ndax/converter.py:14`、`ndax/reader.py:10`）：设备二进制库，体积与结构未知，需 `pyi-archive_viewer` 确认。
5. **三套 Excel 引擎**：calamine（读，`utils/readers/xlsx_reader.py:18` `engine="calamine"`）、openpyxl（依赖项，`launcher.py:16-21` 还专门过滤其样式警告，说明在用）、xlsxwriter（写，`utils/writers/excel_report_writer.py:17`、`ndax/converter.py:17`）。功能有重叠但语义不同，去重空间有限。

### 模块级导入图（事实：启动期展开范围）

`main_window.py:22-24` 顶层 import `window_actions` / `window_init` / `window_texts` →
- `window_init.py:12` → `ApplicationInitializer`；`window_init.py:13-19` → `InitializationManager`；
- `InitializationManager`（`managers/initialization_manager.py:12+`）→ 12 个 step → controller/manager/service/presenter 全图；
- `window_actions.py:11` → `ui_components.config_dialog.ConfigDialog`。

这些在 `main_window.py` 作为脚本执行时，**先于 `if __name__ == "__main__": main()`** 完成导入，因此**早于 QApplication 与 splash**。

---

## 三、收集范围分析

### 事实：显式收集

- `--hidden-import` 清单（`scripts/build.py:112-133`）：PyQt6 三件套、`battery_analysis*` 若干、`openpyxl`、`python_calamine`、`xlsxwriter`、`docx`、`matplotlib.backends.backend_svg`、`pandas._config.localization`。
- `--add-data`（`scripts/build.py:205-215`）：`templates/*.docx`（2 个）、`ui/styles/*`、`locale/*`（en、zh_CN 的 `messages.po`）。
- 入口为 `main_window.py`，PyInstaller 静态追踪从它出发 + 隐藏导入补漏。

### 事实：排除清单（`scripts/build.py:168-190`）

排除了 pytest/pylint/black/astroid、setuptools/pip/pkg_resources、IPython/jupyter、pythonwin/adodbapi/win32com、matplotlib 多数非用后端（qt4/qt5/wx/gtk/webagg/nbagg/pgf 等）、numpy.testing/distutils/f2py、pandas.tests、tkinter/PySide/PyQt5、PyQt6 大量未用子模块。

### 事实/推断：遗留物

- `ui/resources/ui_battery_analysis.ui` 与 `ui/ui_main_window.py`（pyuic6 生成，约 1465 行）是 Designer 遗留，现改用 `UIBuilder`（`main_window.py:63` 注释"替代 Designer 生成的 setupUi"）。
  - `.ui` 文件**未进 `--add-data`**，不占体积（事实）。
  - `ui_main_window.py` 无源码引用（grep 仅自身注释 + build 的 hidden import），但 `scripts/build.py:120` 显式 `--hidden-import=battery_analysis.ui.ui_main_window`，会被编入 PYZ。纯文本 pyc，体积可忽略，属**死代码/可清理项**（推断：清理收益极小，仅整洁性）。
- `battery_analysis/ui/` 目录**无 `__init__.py`**（PEP420 命名空间包）。PyInstaller 对命名空间包的隐藏导入需注意，目前靠 `--hidden-import=battery_analysis.ui` 兜底（事实）。

---

## 四、资源体积构成（事实结构 + 推断权重，不编数字）

- **二进制 DLL（Qt/numpy/pandas/NewareNDA/calamine 的 Rust 扩展）**：推断为体积主体，`--optimize=1`/`--strip` 不作用于它们。
- **matplotlib `mpl-data`**：字体（DejaVu 等）+ 数据文件，推断为第二大项之一。
- **字节码 PYZ**：`--optimize=1` 去 docstring/assert，`--strip` 去符号（仅对二进制有效）；对纯 .pyc 贡献有限（推断）。
- **数据文件**：2 个 `.docx` 模板 + `ui/styles`（qss + 2 个 svg）+ 2 个 `.po`——体积小（事实：文件个数少）。
- **UPX 未强制**：取决于本机是否安装 UPX（`scripts/build.py:256` `--noupx` 条件）。构建环境若无 UPX 则默认不压缩（事实：`_check_build_env` 仅检测并提示）。

---

## 五、解包与加载机制对启动的影响

### 事实：onefile 解压机制

PyInstaller `--onefile` 冷启动：bootloader 把 bundle 解压到 `%TEMP%\_MEIxxxx`，再在其中运行解释器/加载 DLL，进程退出时清理。**首屏时间包含一次解压 I/O**（推断：第二次启动受 OS 文件缓存，通常更快，待实测冷/热差）。

### 事实：spawn 多进程放大 onefile 成本

- `ndax/converter.py:229`、`ndax/worker.py:92`：`ProcessPoolExecutor`。
- `utils/resource_manager.py:96`：`multiprocessing.get_context("spawn")`。
- `concurrency_policy.py`：75% CPU 预算、Windows 上限 61（`:41`）。
- `main_window.py:117`、`launcher.py:55`：均已 `multiprocessing.freeze_support()`（防递归启动）。

推断：spawn 下每个 worker 重新执行 exe → **每个进程重复一次解压/映射 + 重新 import numpy/pandas/NewareNDA**。批量 NDAX 转换时，内存≈基座 + N×（解释器+库），启动 I/O 放大 N 倍。**文件数少时，池子进程 spawn 开销可能超过转换本身收益**（待实测最优 worker 数与文件数阈值）。

### 事实：启动链路与闪屏

- `launcher.py:21-25` 只 import PyQt6 基础三类即建 QApplication+splash；`launcher.py:78-82` 才 import `main_window`。
- 但 **PyInstaller 入口是 `main_window.py`**（`scripts/build.py`），直接脚本执行会先展开第二节的模块级导入图，**绕过了 launcher 的闪屏优先设计**（事实+推断）。这是可验证的启动优化点：把打包入口改为 `launcher.py`。

### 事实：延迟初始化已存在

- `main_window.py:74-79`：先 `self.show()` 再 `QTimer.singleShot(0, self._deferred_init)`。
- `window_init.py:30-47`：`_deferred_init` 计时并分 4 阶段（环境→核心服务→UI→启动完成），有 `elapsed` 日志。
- matplotlib 在 `ApplicationInitializer.initialize()`（`application_initializer.py:183` 调 `_setup_matplotlib`）才 `import matplotlib`，即**后于窗口显示**（事实：不阻塞首屏，但仍在启动会话内）。

---

## 六、缓存与重复打包

### 事实

- 无 `.spec` 文件（find 无结果，`.gitignore` 也忽略 `*.spec`），每次构建即时生成参数，**无 spec 缓存**。
- `scripts/build.py` 每次 `clean_build_dirs()`（`:135-143`）删 `__temp__` 与 `build/{type}`；`--no-clean` 可跳过清理（`:63-72`）以加速重复构建。
- `pyproject.toml [tool.uv] cache-keys` 把 `pyproject.toml` 与 `src/battery_analysis/_version.py` 纳入缓存键（`:128`），版本号变更会失效可编辑包元数据缓存（事实）。

### 推断

- 重复构建的耗时大头是 PyInstaller 重新追踪 + 重写 archive，`--no-clean` 只能省目录清理；真正的缓存收益来自 UPX（若启用）与 C 扩展复用（无）。**没有 spec 意味着每次排除/收集规则都靠代码生成，规则变更即全量重打**。

---

## 七、优化间的相互制约（张力矩阵）

| 优化 | 收益机制 | 风险/反作用 |
|---|---|---|
| `--onefile` | 单文件分发便利 | 冷启动解压；与 spawn 多进程叠加 → 每 worker 重解压重导入，转换场景内存/启动放大 N 倍 |
| UPX 压缩 | 明显缩小 exe（若启用） | 运行时解压抵消启动收益；压缩的 DLL 常触发杀软误报；对已压缩的 DLL/图标无效 |
| `--optimize=1`/`--strip` | 去 docstring/assert、去符号，略缩体积 | 只动字节码/符号，二进制大头不变；strip 降低崩溃栈可读性 |
| 扩大 `--exclude-module` | 砍未用模块/后端 | 动态 import 缺失风险（matplotlib 后端大小写、pandas 可选依赖），`--collect-submodules=numpy` 会覆盖 exclude（build.py 注释已警示） |
| 砍 matplotlib 后端 | 省 mpl-data/后端体积 | 双后端（QtAgg 交互 + Agg 离屏报告）都是硬需求，砍不动 |
| 三 Excel 引擎去重 | 省一库体积 | calamine 只读、xlsxwriter 只写、openpyxl 通用，语义不同；砍 openpyxl 需确认无写路径依赖（launcher 过滤其警告说明在用） |
| `.po` 改 `.mo` | 略快翻译加载 | 需加编译步骤；en/zh_CN 两份极小，收益可忽略 |
| 入口改 `launcher.py` | 更早 splash、更晚重导入 | 需重验 `main_window.main(app, splash)` 的委托链路在打包态正常 |
| `--onedir` 替代 `--onefile` | 免解压、worker 共享基座、启动快 | 失去单文件，需 zip/安装器分发 |

**核心判断**：本项目"体积优化"与"启动/运行效率优化"在 onefile+spawn 组合点上**直接对立**。若目标场景包含批量 NDAX 转换（多进程），应优先评估 `--onedir` 或限制 worker 数，其次才是 UPX 体积压榨。

---

## 八、运行效率建议（具体、可验证）

1. **把 PyInstaller 入口改为 `launcher.py`**：恢复"先 splash 再 import 主模块"设计，推迟 `main_window` 及其 12-step 导入图到 splash 之后。验证：对比入口切换前后首屏可见时间（基准方法见下）。
2. **NDAX 转换进程模型实测调优**：`converter.py:105-108` 逐行 `ws.write_row`（Python 循环）是写瓶颈之一；可测 `xlsxwriter.Workbook(constant_memory=True)` 降内存（代价：可能略降写速）。worker 数已有 75% 预算+61 上限，但需实测"文件数少时 spawn 开销 vs 收益"的拐点。
3. **matplotlib 字体缓存**：首帧图慢常来自冷建 font cache。可预置 `MPLCONFIGDIR` 到可写目录或在安装/首次启动预热，避免每台机器首次图慢（事实：`application_initializer.py:123-133` 只设 rcParams，未处理 cache 目录）。
4. **读路径保持 calamine**：`xlsx_reader.py` 已用 Rust calamine 引擎，是最快 xlsx 读路径之一，勿回退 openpyxl 读。
5. **onefile 温度目录失败模式**：确认 `%TEMP%` 空间与写权限（磁盘满/企业策略只读会导致 bootloader 解压失败，属已知 onefile 失败模式，待实测确认本机环境）。

---

## 九、可复现基准方法（不预设任何数字）

### 体积

1. 重新构建 `uv run python scripts/build.py Release`（确认 `_version.py=5.0.2` 生效）。
2. `pyi-archive_viewer -l build/Release/battery-analyzer_5.0.2_x64.exe`（列出 PYZ/CArchive 成员及大小），找 TOP 贡献者；或改用 `--onedir` 构建后直接 `du`/资源管理器看各子目录占比。
3. 对比 UPX 前后体积与 exe 哈希；记录 `_check_build_env` 是否检测到 UPX。

### 启动时间

- 冷启动：重启（或清 OS 缓存）+ 清 `%TEMP%\_MEI*`，测到窗口可见；热启动：连续第二次。多次取中位数。
- 打点：`launcher.py`/`window_init.py:45-47` 已有 `elapsed` 日志，可直接复用作"后置初始化耗时"；首屏需外部计时（`Measure-Command` 只测到进程退出，不适用 GUI 常驻；建议 wrapper 记录 `process start` 到首条日志/窗口句柄出现）。
- 变量隔离：入口 `main_window.py` vs `launcher.py`；`--onefile` vs `--onedir`；有/无 UPX。

### 转换吞吐与内存

- 固定 N 个 `.ndax` fixture，跑 `time` 脚本 + `psutil` 采样峰值 RSS（含全部子进程之和）。
- 扫描 worker 数（1 / 2 / 预算值 / 上限），画出 吞吐×峰值内存×启动时间 曲线，定位 onefile 下 spawn 的规模拐点。

---

## 十、事实 / 推断 / 待实测 汇总

- **事实**：构建=PyInstaller（`scripts/build.py`，Makefile 驱动）；入口=main_window.py；onefile/optimize=1/strip/条件 UPX；排除清单与 add-data 清单；`_version=5.0.2` vs 产物 4.0.1 不一致；matplotlib 双后端；calamine/openpyxl/xlsxwriter 三引擎；NDAX 用 spawn ProcessPoolExecutor + freeze_support；launcher 闪屏优先设计被入口选择绕过；config/ 未打包且仓库无 config.json。
- **推断**：体积大头=Qt/matplotlib/pandas/numpy 二进制；onefile+spawn 导致内存/启动放大 N 倍；UPX 体积↔启动/AV 权衡；optimize/strip 收益边际。
- **待实测**：exe 实际体积与各组件占比；冷/热启动差；NDAX 转换吞吐与峰值 RSS（随 worker 数、onefile/onedir、UPX 变化）；UPX 对 Qt DLL 压缩率与 AV 结果；`%TEMP%` 只读/空间不足的失败复现。


---

## GPT (Round 1): 保留 PyInstaller，先建立可测双发布路线，而不是为单文件换技术栈

## 一、结论与判断边界

建议保留 Python/PyQt6 + PyInstaller 作为近期主线，不因“一个 exe”就迁移 GUI、数据分析库或编译器；把**单文件便携版**和**日常高频使用版（onedir ZIP，必要时再包安装器）**视为同一应用的两个发布配置。先用同源对照实验决定默认形态，而不是先承诺单文件最小、最快。

单文件对无需 Python 环境、拷走即用的 Windows 用户有价值；但该项目有 Qt、NumPy、pandas、Matplotlib 和多种 Office 文件读写原生依赖，单文件只是交付容器，不会消除这些依赖。PyInstaller onefile 的一般机制是在运行前准备/解包内部资源，故“下载包小”“启动快”“运行快”“安装后占用小”应分别衡量，不能相互代替。该机制属于工具原理，不是本项目性能实测结论。

**本轮实测事实仅限工具只读检查当前工作树的内容与目录，未运行应用、构建、测试或计时，未安装依赖。无任何启动时长、exe 字节数、压缩率或吞吐提升的实测数据。** 以下分为已观察代码事实、代码推断、待验证方案。当前 `build/Release/` 可见 `battery-analyzer_4.0.1_x64.exe`，但尚不能证明它对应当前源码、锁文件、UPX 状态和构建机器，不将其当作有效基线。

## 二、当前命令、技术栈与发布链证据

1. 开发任务入口：`Makefile:33-37` 的 Release/Debug 分别执行 `uv run python scripts/build.py Release` 和 `uv run python scripts/build.py Debug`。脚本 CLI 另支持 `--no-clean`、`--verbose`（`scripts/build.py:317-341`）。本轮仅阅读这些命令，没有执行。
2. 技术栈不作假定：`pyproject.toml:13` 要求 Python >=3.14；`:27-39` 明列 NewareNDA、Matplotlib、NumPy、openpyxl、pandas、psutil、PyQt6、python-calamine、python-docx、pywin32、xlsxwriter；`:50-51` 的构建 extra 是 PyInstaller >=6.10,<7。实际构建链明显 Windows 化：使用 `.exe`、`os.startfile`、Windows 资源路径分隔符与 CI windows-latest，不能仅凭元数据里的 OS Independent 判定已有跨平台交付能力。
3. PyInstaller 使用当前 `sys.executable -m PyInstaller`，入口为 `src/battery_analysis/main/main_window.py`（`scripts/build.py:89-93,214-225,232`），从 `src/` 作为 cwd 运行（`:295-299`）。默认且不可从 CLI 切换 `--onefile`；Release `--noconsole --strip`，Debug `--console`；两者都有 `--optimize=1`（`:248-259`）。UPX 是否启用取决于 PATH，未发现时才加 `--noupx`（`:261-263`）。版本取自 Version，架构名称硬编码 x64（`:51-54,283`），不是构建前实际架构校验。
4. 已做裁剪：`scripts/build.py:175-209` 排除测试、开发工具、其他 GUI 框架、部分 Matplotlib 后端和许多 Qt 模块；`:96-117` 显式 hidden imports 包含 Office 读写和 SVG 后端；`:235-242` 带入模板、样式、locale，`:269` 复制 NumPy 元数据。因此“不加区分地 collect-all”不宜作为优化动作，反而可能抵消已有裁剪。
5. CI：`.github/workflows/ci-cd.yaml:24-32` 设置 uv 缓存并 `uv sync --all-extras --frozen`；`:43-48` 可选安装 UPX 5.0.0 后构建；`:145-155` 发布时只选取 `build/Release/*.exe`，找不到 exe 甚至 `exit 0`。引入 ZIP/安装器不能只改 PyInstaller 参数，还必须改发布选择与产物存在性检查。
6. 两个入口目前不一致：`pyproject.toml:121-122` 的安装命令入口是 `battery_analysis.main.launcher:main`；该 launcher 在 `src/battery_analysis/main/launcher.py:54-93` 中先 `freeze_support()`、设置 Qt 环境、创建闪屏，再导入 main_window；而 exe 直接分析并运行 main_window，已在模块顶部导入三个 mixin（`main_window.py:22-24`），再于 `:115-129` 创建闪屏。两条路径均有 freeze_support，但初始化顺序和配置并不完全等价。启动优化不能只验证 uv 下的 launcher，就宣称 exe 同样收益。

## 三、优先级路线：先修构建可观测性，再争体积和分发形态

### P0：建立可信基线和失败契约，成本低、收益基础性

- 保存实际 Python/PyInstaller/Qt/UPX 版本、锁文件标识、提交与工作树状态、完整参数、构建日志、产物清单和哈希。UPX 现在是环境自适应且 CI 安装允许失败，因此相同源码不保证相同压缩路径；产品发布应明确选择压缩配置，失败时明确记录降级，而不是默默变化。
- 现有 `--no-clean` 不应直接宣传为有效增量：`scripts/build.py:79-84` 仅跳过前置清理，但成功构建末尾 `:312-313` 仍删除临时目录，且 `_verify_and_clean():160-162` 也会删除。**代码推断：常规成功构建之间没有保留此 workpath 的分析缓存，no-clean 不能保证重复构建提速。** 先区分 work/cache、最终输出和可丢弃临时目录，开发增量保留 cache，正式发布允许受控 clean。这比先换编译器迁移更直接。
- `_verify_and_clean()` 对缺失 exe 只 warning（`:154-158`）；`run_build()` 捕获部分文件系统异常后只记录（`:134-135`）；CI 无 exe 也可成功退出。应形成“预期清单不存在即失败”的契约，并保存诊断目录而不是无条件删除。
- `tests/test_build_scripts.py:1-58` 已覆盖 PyInstaller 非零返回值传播，但没有覆盖真实冻结后的资源、GUI 启动、缺失产物和缓存留存；源码测试不能替代 frozen smoke test。

### P1：统一入口 + PyInstaller 双模式试验，成本低至中

- 将轻量 launcher 定为候选唯一入口，令开发、exe、冻结进程路径对齐；先复核其 Qt 环境设置与 warning handler 行为，再做回归，不把它当作无风险改名。`main_window.py:79` 已用 `QTimer.singleShot(0, self._deferred_init)` 延后业务初始化；`window_init.py:30-49` 实际同步调用初始化流水线。**代码推断：延后执行不等于在后台线程执行，窗口先可见也不代表已可交互。** 测量必须拆分闪屏、主窗、可操作三个时间点。
- 新增 onedir 作为实验发布配置，先用完整目录 ZIP 分发，保留 onefile 便携版。PyInstaller 模式切换本身成本较低，但当前产物检查、命名与发布逻辑以单 exe 为前提，所以交付链迁移成本是低至中，而非“只换一个参数”。
- 资源已有兼容基础：`src/battery_analysis/i18n/__init__.py:20-22` 和 `ui/styles/style_manager.py:23-24` 使用 `_MEIPASS` 找资源，适合优先验证 onedir。但 `main/controllers/file_controller.py:49-51` 使用 exe 所在目录，`utils/config_utils.py:205-217` 存在冻结/可执行文件相对候选路径，必须核验用户数据写入位置；安装到只读 Program Files 与便携目录的权限语义不同。
- 仅当用户确实需要桌面快捷方式、卸载、企业部署、更新生命周期时，再在 onedir 外包安装器。**安装器也可以是单个下载 exe，但不等于每次启动重新解包的单文件应用**，这是可同时满足“单个下载文件”和“重复启动效率”的重要折中。成本中等：新增安装、卸载、签名、用户数据保留测试，不先上复杂自动更新。

### P2：基于清单做裁剪和压缩选择，避免牺牲功能

- 用 onedir 文件清单按 Qt 插件、科学计算 DLL、Matplotlib 数据、解释器、模板/语言包分桶，按实际字节贡献排序，不凭依赖名称猜最大的组件。优先删除明确冗余，不先删除业务格式支持。
- `pyproject.toml:27-39` 中多个 Excel/Word 库不能直接认定重复：可能分别服务读取兼容性、快速读表、公式与样式、导出。按功能调用与样本结果建立矩阵后，才讨论合并实现或“高级可选组件”。把功能改成 optional dependency 也不会自动缩小冻结包，必须同步改变导入和打包配置；离线用户缺功能的支持成本可能高于省下的下载体积。
- UPX 做开/关 A/B，不以更小 exe 作为唯一标准。需要核对冷启动、临时磁盘量、安全软件扫描、DLL 兼容性、构建时长。Release 的 `--strip` 在 Windows 二进制生态里也不应视为无代价默认值，应单独验证可用工具、兼容与调试损失。
- 注释声称 `--optimize=1` 去除 docstring（`scripts/build.py:258-259`），但 Python 优化等级 1 不去除 docstring；不能把注释当作已实现收益。等级 2 才涉及 docstring 删除，也不能未经功能回归就升级；去掉 assert 还涉及运行语义，不是免费加速。
- 若基础包仍过大，再评估 pywin32 使用范围（已看到 win32api/win32con 直接调用，如 `main/services/file_service.py:222-223,343-344`）；不可只因包名大就剔除，也不能认为 build 环境安装 dev 依赖就必定把它们全部塞进 exe。精简 build 环境主要提升环境可控性与准备效率，最终体积仍由依赖图和 hooks 决定。

### P3：编译器或框架迁移暂不作为主线，成本高、收益未证

- Nuitka 可作为独立候选实验，而不是已证明的更小/更快方案。项目的原生数组计算与 Qt 绘制不能因 Python 源码编译就自动更快，还会引入 C 编译工具链、Qt 插件/原生 DLL、Python 3.14 与冻结 multiprocessing 的兼容验证。若需要 onefile，其交付机制代价仍须实际测量。
- 不建议近期切到 Web/Electron/Tauri 或重写分析层来解决分发体积：这会移动而不是消灭 Python 数据处理依赖，且是 UI/协议/资源/测试体系迁移。只有产品出现浏览器协作、远端重计算等新的需求时，才重新计算这类投资。
- 发布形态优先级：**保留 onefile → 增加 onedir ZIP 对照 → 根据真实日用场景选择默认 → 有部署需求再包安装器 → 明确瓶颈后才比较编译器**。

## 四、运行效率的简要边界

onefile 改 onedir 主要针对启动准备与交付生命周期，不承诺加快表格解析、NDAX 转换、绘图或报告生成。运行效率应单独优化算法、IO、数据复制、渲染与并发。

仓库已经有 NDAX 进程池（`src/battery_analysis/ndax/worker.py:92`、`ndax/converter.py:229`），并存在按 CPU 留余量的统一 worker budget（`utils/concurrency_policy.py:35-41`），因此不是简单“再加进程”就一定快。大样本应观察 worker 总 RSS、任务序列化、磁盘并发和 UI 响应；不得未经证据断言每个子进程都会完整独立解包 onefile，也不得把 Python GIL 当作所有业务阶段的唯一瓶颈。启动阶段继续优先查重依赖导入/初始化链，而非仅调整压缩参数。

## 五、建议后续验证实验（本轮均未执行）

1. **固定来源**：同一源码、Python 架构、uv.lock 和构建工具版本；先记录当前基线。保持机器、电源策略、测试文件与安全软件策略一致。
2. **最小对照矩阵**：onefile/onedir × UPX 开/关，先保持相同入口和依赖；再独立比较 main_window 与 launcher，避免多个因素同时改变而无法归因。strip/optimize 作为后续单因素实验，不一次展开所有组合。
3. **构建效率**：分别记录首次 clean 与连续增量构建总时长、PyInstaller 分阶段时长、缓存命中与保留目录。验证 `--no-clean` 在改动前后是否真保留工作目录；PR 若无需验证单文件容器，可评估较轻发布模式 smoke，正式标签仍验证最终 onefile，不能以减少质量门禁来假造提速。
4. **用户体验**：从进程创建到闪屏、主窗口、核心操作可用分别计时，区分冷/热与首次/重复运行，重复采样报告中位数及波动；同时记录发行压缩包大小、解包后的占用、运行临时目录峰值、进程树峰值 RSS。分别报告，不给单一“体积”结论。
5. **冻结功能矩阵**：无开发环境的 Windows 干净机器，中文/空格路径、标准用户、只读安装目录，验证启动、语言/主题/模板、XLSX 各引擎导入、NDAX 进程池、绘图与 SVG、Excel/Word 报告、退出清理和第二次运行。对杀软兼容保留正常保护，不建议靠长期排除扫描解决产品问题。
6. **运行性能**：固定小/中/大样本，独立记录读取、转换、计算、绘图、报告阶段吞吐与总内存，验证结果一致。只有某阶段变快且输出正确，才归因对应优化。

## 六、尚缺证据与决策门槛

缺少：当前 exe 的可追溯构建信息与真实大小分解；实际 uv.lock 对应的环境安装版本与 hooks 行为；用户对“单个下载文件”“免安装”“首次启动”“重复启动”的优先级；目标机器硬盘/安全软件/权限分布；各读写库不可替代能力矩阵；冷/热启动基线和业务阶段 CPU/IO/内存画像；签名证书与企业部署要求。

在这些证据补齐前，不宣布 onefile 不适合、不承诺 onedir 必然省总磁盘、更不承诺任何百分比收益。近期决策门槛是：同功能、同输出、同安全策略下，是否显著改善用户最在意的指标且不增加不可接受的安装/维护成本。策略核心是把“方便下载”和“高效运行”解耦，而不是让一个 exe 同时承担所有目标。

## 研究验收记录

```acceptance-report
{
  "criteriaSatisfied": [{"id": "criterion-1", "status": "satisfied", "evidence": "已只读检查构建脚本、依赖、双入口、CI、资源路径及构建测试，以路径/行号给出双发布路线、优先级、实验和残余风险。"}],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [],
  "validationOutput": ["仅使用只读文件与目录工具核验当前工作树；未运行构建、应用、测试或依赖安装。"],
  "residualRisks": ["没有项目性能实测或当前 exe 的可追溯元数据，所有收益仍待对照实验。", "onedir/安装器迁移涉及发布筛选、资源路径、写权限和冻结多进程回归。"],
  "noStagedFiles": true,
  "diffSummary": "未修改项目源码；唯一持久写入为本次会议黑板条目。",
  "reviewFindings": ["发现 no-clean 后仍删除 workpath、开发与冻结入口不同、缺失发布产物可仅警告等需优先验证的风险。"],
  "manualNotes": "本轮为静态研究，未检查 git 暂存状态；noStagedFiles 表示本代理未暂存任何文件，并非断言工作树原本无暂存内容。"
}
```

---

## GLM (Round 1): 务实核查：实际打包命令、启动路径与最小改动优化清单

# GLM（务实实施视角）Round 1：实际打包命令与 exe 优化逐项核查

## 一、实际构建入口与命令（已知，有证据）

**唯一真实打包链路**（三处互相印证）：
1. Makefile `build` 目标 → `uv run python scripts/build.py Release`（Makefile:23-24）
2. CI 完全一致：`.github/workflows/ci-cd.yaml:48` → `uv run python scripts/build.py Release`
3. `scripts/build.py` 内部拼装 PyInstaller 命令（`_build_pyinstaller_args`，build.py:180-266），`subprocess` 以 `cwd=src` 运行（build.py:297-301）

**实际生效的 PyInstaller 参数清单**（build.py:180-266，逐项核对）：
- 入口文件：`src/battery_analysis/main/main_window.py`（build.py:66-68）——注意不是 `launcher.py`
- `--onefile` + Release 时 `--noconsole`（Debug 为 `--console`）
- `--strip`（非 Debug，build.py:264）
- `--optimize=1`（build.py:267，去 docstrings/assert）
- UPX：仅当 PATH 中有 upx 才启用，否则 `--noupx`（build.py:270-271）
- `--copy-metadata=numpy`（build.py:276-277），刻意**不用** `--collect-submodules=numpy` 以免冲掉 exclude
- 6 个 hidden imports（build.py:69-97：PyQt6 三件套、应用模块、openpyxl/python_calamine/xlsxwriter/docx/matplotlib svg 后端/pandas localization）+ `--hidden-import=pywintypes`（build.py:186）
- 约 45 个 `--exclude-module`（build.py:154-178：测试/构建工具、pywin32 冗余包、matplotlib 非用后端、tkinter/PySide/PyQt5、20+ 个不用的 PyQt6 子模块）
- 3 组 add-data：templates/*.docx、ui/styles、locale（build.py:240-247）
- 产物命名 `battery-analyzer_{version}_x64.exe`，输出 `build/Release/`

**产物现状**：`build/Release/battery-analyzer_4.0.1_x64.exe` 存在于当前工作树，但我无 shell 工具，**当前实际体积未测**（待验证）。历史记录：CHANGELOG v3.2.0 "onefile 后 183MB → 78MB（-57%）"（CHANGELOG.md:128）。

## 二、关键判断：低垂果实基本已被摘完

排除清单、onefile、strip、optimize=1、numpy 元数据精细处理、启动延迟初始化——这些"标准优化"项目里**已经全部存在**。任何人提案"加 exclude、上 UPX、换打包器"之前，必须先承认现状已相当优化。

## 三、发现的具体问题点（本轮主要贡献）

### 发现 1：打包入口与设计入口不一致（推断，待验证）
- `pyproject.toml [project.scripts]` 的入口是 `battery_analysis.main.launcher:main`（pyproject.toml:130-131），launcher.py 的设计意图是"最小化入口、业务模块导入前先显示闪屏"（launcher.py:1-9, 54-80）。
- 但 PyInstaller 打包的入口是 `main_window.py`（build.py:66-68），其模块级 import 直接拉入 window_init/window_actions/window_texts 三个 Mixin（main_window.py:20-22），进而拉入 i18n、application_initializer、log_manager 等（window_init.py:11-22）。launcher.py 的"尽早闪屏"在 exe 中**未生效**，exe 的闪屏来自 main_window.py:91 的 `_create_splash_screen`，在整条模块链 import 完之后才出现。
- 影响评估（推断）：pandas/matplotlib 均不在启动链的模块级 import（grep 全 src 证实：matplotlib 只在 battery_chart_viewer.py:25-26、figure_builder.py:11-13 等子模块；pandas 只在 ndax/reader.py、xlsx_reader.py 等子模块），所以启动瓶颈主要是 PyQt6 本体 + onefile 自解压，而非业务模块。但统一入口仍是低风险的一致性修复——改 build.py:66 的入口路径 + 回归验证即可，不改业务代码。

### 发现 2：hidden imports 可能存在冗余（待验证）
- `battery_analysis.main.battery_chart_viewer` 等显式 hidden import（build.py:79-84）可能 PyInstaller 本可自动追踪；`pandas._config.localization` 这类逐个列出说明维护者曾踩坑，但也可能部分已不再需要。**逐个删减 + 启动回归**是零代码改动、可单变量验证的实验。

### 发现 3：Python 3.14 兼容性风险（已知事实，影响待验证）
- `.python-version` = 3.14，`requires-python >= 3.14`（pyproject.toml:15），但 ruff/mypy 目标还是 py313（pyproject.toml tool.ruff/tool.mypy）。PyInstaller 对最新 Python 的钩子兼容历来滞后，若升级 PyInstaller 或换 Python 补丁版本，需重新验证打包。pyinstaller 约束为 `>=6.10.0,<7.0.0`（pyproject.toml:36-37）。

### 发现 4：已知运行热点（与打包正交，避免混淆议题）
- 核心计算已向量化且有基准脚本 `scripts/benchmark_p2.py`（头部注释记录 2026-08-21 实测：match_pulse_levels 0.0090s、charge batch 0.0015s，验收目标 10-100 倍已达成）。
- ndax 全量 9 文件端到端 20.8s、峰值内存 192MB、**串行**读取（docs/ndax_rework_risk_report.md:17, 60）——这是当前最大的运行时热点，但它是数据分析管线问题，不是打包问题，不建议混入本轮。

## 四、其他路线简要比较（不推荐盲换）

- **Nuitka**：`docs/NUITKA_BUILD.md` 已有 300+ 行完整指南，但从未接入 CI/Makefile，属于搁置的备选。切换成本 = C 编译器环境 + 显著更长的构建时间 + 全量回归，且当前"启动慢/体积大"未证明源于解释执行。**不建议现在换**，除非基线测量证明 PyInstaller 路线到达天花板。
- **UPX**：脚本已内置可选支持（build.py:270-271），但 CHANGELOG.md:484 记录过"禁用 UPX 压缩以解决构建问题"的历史事故。收益（体积）与风险（杀软误报、启动时解压更慢）需同机 A/B 实测，不是无脑开关。
- **--onedir**：曾用过又改回 onefile（CHANGELOG.md:178-179，资源路径已兼容 `sys._MEIPASS`，见 i18n/__init__.py:21-22、style_manager.py:23-24、config_utils.py:204-206）。onedir 能消除 onefile 冷启动解压代价，但牺牲单文件分发形态——这是产品决策不是技术决策。
- **--optimize=2**：当前是 optimize=1。升到 2 会删 docstrings，风险是运行时反射/introspection 代码可能崩，需全量回归才知道，收益通常很小，优先级最低。

## 五、最小改动优化清单（按风险从低到高，每项独立可回滚）

1. **P0 测量先行（零改动）**：记录三项基线——(a) exe 实际字节数；(b) 冷启动（首次解压）与热启动到主窗口可交互的耗时，现有日志 `Background initialization completed in %dms`（window_init.py:52）可直接利用；(c) 用 `pyi-archive_viewer` 列出 onefile 内部成员按大小排序，找出 top-10 体积贡献者（推断 PyQt6 的 Qt6*.dll、matplotlib、pandas 是大头，**未验证，不许引用具体数字**）。没有基线，后面所有讨论都是空转。
2. **P1 入口统一**：build.py:66 入口改为 launcher.py 或显式决策维持现状并写注释，消除两套启动路径的认知负担。改完跑启动冒烟（闪屏→主窗口→打开文件→画图→导出报告）。
3. **P1 hidden import 逐项瘦身**：一次只删一个，构建后启动冒烟，通过才保留删除。纯配置改动，git 单行 diff 可回滚。
4. **P2 补充 exclude 候选**：如 numpy.testing 已排除但 `numpy.f2py`/`numpy.doc` 等，同样单变量验证。前提是先有 P0 的 archive 清单，不盲猜。
5. **P3（仅当 P0 证明必要）**：UPX A/B、optimize=2、onedir 对比、Nuitka 试点。全部需要独立分支 + CI 完整构建验证。

## 六、回归检查与基准实验设计

**回归清单**（每次打包配置改动后必须跑）：
- `uv run pytest`（历史基线 891 passed，见 docs/RELEASE_NOTES_v5.0.0.md:176）
- 打包后 exe 手工冒烟：启动闪屏出现、主窗口渲染、导入一个真实数据文件、图表绘制、导出 Excel/Word 报告、切换语言（locale 打包依赖 add-data，i18n 最易坏）
- 检查启动日志毫秒数不劣化超过阈值（阈值待 P0 定）

**基准实验设计（单变量原则）**：
- 同一台机器、同一 Python/PyInstaller 版本、同一 commit，仅改一个参数构建一次
- 体积指标：exe 字节数 + archive 内 top 成员清单
- 启动指标：冷启动 = 清空 %TEMP% 后首启；热启动 = 二次启动；各测 3 次取中位数，用现有日志时间戳而非秒表
- 运行指标：benchmark_p2.py 可复跑（数值计算），ndax 端到端用 docs 中 9 文件基准（20.8s 基线）
- 任何实验结果先记录在黑板/文档，不得直接写进 CHANGELOG 数字

## 七、已知 / 推断 / 待验证汇总

- **已知（文件证据）**：完整命令参数、入口文件、exclude/hidden 清单、onefile 历史 78MB（v3.2.0）、launcher 与打包入口分叉、启动延迟初始化架构、pandas/matplotlib 延迟导入。
- **推断**：启动瓶颈主要是 PyQt6 + onefile 解压而非业务 import；hidden imports 存在冗余；体积大头是 Qt DLL。
- **待验证**：当前 4.0.1 exe 实际体积；冷/热启动耗时；archive 内 top-10 成员；各 hidden import 是否真必要；Python 3.14 + PyInstaller 当前组合在 CI 上的实际表现。

---

## User (Feedback during Round 1): 用户要求停止 MiniMax，主持人已请求停止其重试，不再继续本轮重试。

用户反馈：minimax的停掉吧。

执行记录：主持人已对 MiniMax 重试运行 0ac794c0-3ef3-480b-a2e8-4ea0aafc2f36 调用 stop，工具返回 Stop requested。本轮不再重试 MiniMax，也不将本次反馈视为进入第二轮的许可。后续轮次是否恢复 MiniMax 需用户确认。

---

## User (Feedback after Round 1): 用户同意仅由 GPT、DeepSeek、GLM 进入第二轮，交叉核查问题并排序优化优先级。

主持人询问：是否让 GPT、DeepSeek、GLM 三位继续第二轮，重点交叉核查构建缓存、入口、体积与业务运行瓶颈，并排出优化优先级？

用户回复：可以。

第二轮继续只读研究，不实施代码修改；MiniMax 保持停用。各顾问应读取第一轮所有发言、用户反馈以及 transcript.md 中主持人待复核项，针对证据进行交叉质疑和完善。本次同意不包含自动启动第三轮或写最终 conclusion.md。

---

## GPT (Round 2): 交叉核查：撤回重复解包论据，先修可观测性与分析缓存，保留单 EXE 主线

## 一、修订方向与证据边界

已读取黑板全部三份 Round 1、两份用户反馈，以及 transcript.md 的六项待复核项。本轮仅只读源码和当前虚拟环境内的 PyInstaller 官方包源码；没有运行应用、测试、构建、安装或性能测量。所有收益都是待验证假设。

**修订我自己的首轮建议：单 EXE 便携版继续作为既定交付约束；onedir 先只是定位解包开销的实验对照，不默认新增第二条正式发布线，更不以安装器代替用户诉求。** 只有测量显示无法满足体验目标，再请用户决策是否接受其他形态。首轮“低垂果实已基本摘完”也说早了：分析缓存被主动删除、成功契约和日志可观测性，仍是明确的低成本问题。

## 二、有证据的修正／认可／反驳表

下表路径均相对仓库根目录；事实、推断和待验证分别标明。

| 首轮判断 | 复核结论 | 证据及限制 |
|---|---|---|
| 三方：当前实际走 PyInstaller onefile，而非 Nuitka | **认可，代码事实** | `Makefile:33-37`、`.github/workflows/ci-cd.yaml:46-48` 调用构建脚本；`scripts/build.py:217-224` 拼装 `sys.executable -m PyInstaller` 和 `--onefile`。不能用历史 Nuitka 指南解释当前行为。 |
| DeepSeek：每个 spawn worker 都完整独立解包，构成 onefile 与多进程的结构性冲突 | **反驳其已被证明的地位，撤出决策依据** | `ndax/worker.py:92` 与 `ndax/converter.py:229` 的确新建进程池，但两处没有显式传入 `ResourceManager.get_processing_context()`；`utils/resource_manager.py:96` 存在 spawn helper，不能据此声称进程池接入该 helper。Windows spawn 与每 worker 都新建完整解包目录不是同一命题。PyInstaller 6 系列有父子进程识别及继承解包路径的机制；本轮无法在线核对 bootloader C 源码，故不将具体路径复用行为写成已核实事实。必须用运行时 `_MEIPASS`、进程树及目录写入观察核验，而非先下“IO 放大 N 倍”的结论。 |
| 三方：已有 freeze_support，冻结多进程问题已基本解决 | **只认可防递归分流，不等于无额外启动成本** | 本地 `.venv/Lib/site-packages/PyInstaller/hooks/rthooks/pyi_rth_multiprocessing.py:24-54` 将 worker 参数分流到 `spawn_main()` 后退出；它生效之前，入口顶部导入已经发生。`main_window.py:22-24` 导入 mixin，`freeze_support()` 到 `:117` 才执行。`launcher.py:21-23` 仍先导入 Qt，`:55` 才分流。因此“换 launcher”也不等于 worker 完全免 GUI 库导入。此处有进一步精简 worker 启动路径的候选机会，但不在本轮提出重写。 |
| DeepSeek：无手写 spec 就没有增量缓存，no-clean 主要省删除 | **反驳原理，认可当前脚本实际上丢失分析缓存** | `scripts/build.py:223` 将 workpath 放在 `__temp__/BatteryAnalysis`；`:312-313` 成功后删掉整个临时根目录，`:161-162` 又清一次；`--no-clean` 只跳过 `:80-84` 的前置清理。官方本地源码 `PyInstaller/building/datastruct.py:158,169-185,209` 明确按 workpath 内 TOC 读写重建状态，完全不依赖是否人工维护 spec。准确表述应是“当前成功构建之间不保留这套 workpath 分析状态”。 |
| 我首轮：缓存被清理，应优先处理 | **认可，但收窄范围** | 不是“所有 PyInstaller 缓存都被删”。本地 `PyInstaller/building/utils.py:119-130,174-180` 另用 `CONF['cachedir']` 保存 strip/UPX 等二进制处理缓存；构建脚本没有证据表明也删了它。保留 workpath 能否显著降低总构建时间，仍需计时，不能承诺跳过重新压包。 |
| DeepSeek／GLM：optimize=1 去 docstring；strip 不作用于二进制大头 | **纠正** | `scripts/build.py:258-259` 的注释错误：优化等级 1 去 assert、使 `__debug__` 为假，等级 2 才另去 docstring。strip 的对象恰恰是可处理的二进制符号，不能说“不作用于 DLL 大头”；但发行 DLL 是否有可去符号及 Windows 上兼容性，需具体检查。不要把这两个参数当已证明的体积／速度收益。 |
| 三方：切 launcher 可恢复更早闪屏 | **认可顺序事实，不认可“入口选错”“低风险”“必然更快”** | `scripts/build.py:91-93` 指向 main_window；`launcher.py:78-81` 是先创建闪屏再导入主窗口。它改变的是业务导入相对闪屏的顺序，不改变 onefile bootloader 的先行准备成本；是否缩短主窗可用时间尚未知。另 `launcher.py:59` 设置 QT_ACCESSIBILITY，当前主窗口直接入口没有相同设置，所以不是等价替换。 |
| GLM：pandas/matplotlib 在子模块，所以启动瓶颈主要是 Qt／解包而不是业务 import | **推论不成立，结论暂缓** | 位于子模块不等于延迟导入：`window_init.py:13-19` 顶层导入初始化管理器，后者 `managers/initialization_manager.py:10-46` 顶层导入全部步骤，步骤如 `steps/handlers_initialization_step.py:5-13` 又导入业务管理器。与此同时确有真实懒导入，例如 `main/factories/battery_chart_viewer_wrapper.py:30-31` 在方法内导入 viewer。两类都存在，不能靠 grep 到模块名就确定完整入口的传递闭包和耗时。DeepSeek 所称 matplotlib 一定在窗口显示后才首次导入也缺完整闭包证明。 |
| 三方：已延后初始化，已有日志可衡量启动 | **认可已有延后执行，反驳后台化和完整启动计时解释** | `main_window.py:79` 为 `QTimer.singleShot(0, ...)`；`window_init.py:39-47` 在回调中同步准备、执行流水线并计时。日志中的 Background 是名字，不是线程证据；该计时不含 bootloader、顶部导入、构造窗体的前段时间，也不单独证明 GUI 能接收操作。 |
| GLM：优先逐项删 hidden import，属于零代码瘦身 | **降级，先查 archive 差异** | `scripts/build.py:96-117` 包含显式 hidden imports；如果某模块已经由依赖图或 hook 收集，删除重复声明通常不会删除包内模块，不应期待体积收益；如果确实删除了它，又可能破坏低频动态功能。一次完整构建只换一行仍有实验成本，且仅启动冒烟不足验证报告、SVG、语言与 NDAX。先依据成员清单挑能改变实际收集结果的大项。 |
| DeepSeek：过滤 openpyxl 警告说明存在必需读写路径；两后端必需所以 mpl-data 砍不动 | **均属证据跳跃** | `launcher.py:12-19` 是警告过滤，不证明当下调用路径必须依赖 openpyxl。QtAgg 与 Agg 的用途证据可保留，但不能将后端 Python 模块与独立完整数据资源包混为一谈，更不能由此否定字体／资源清单级分析。当前也没有证据支持删除这些资源。 |
| GPT：发布成功契约应先修 | **认可并补充可观测性问题** | `scripts/build.py:154-158` 缺 exe 只 warning，`:134-135` 捕获文件系统异常后不重新抛出；CI `.github/workflows/ci-cd.yaml:148-150` 无 exe 仍 `exit 0`。另外构建输出 `scripts/build.py:297-302` 被整体 capture，只转发 stderr 且按 error 级别处理；stdout 没有转发，默认 WARNING 又隐藏部分 info。应先确保保存完整真实日志，才能讨论分析／压包耗时及缓存命中。 |

### 入口回归的新增风险提示

`launcher.py:70` 和 `main_window.py:156` 的 Qt 消息处理器都直接调用 `sys.stderr.write()`；Release 使用 `--noconsole`（`scripts/build.py:248-254`）。无控制台冻结程序中标准流可能为 None 是 PyInstaller 官方文档描述的兼容点；本轮未执行冻结程序，故只列为**需验证的已有风险**，不宣布必现崩溃。入口统一不能掩盖此差异，应包含 Qt warning 路径冒烟，而不只是看到闪屏就通过。

## 三、机制资料、版本与无法验证之处

实际锁文件 `uv.lock:837-838` 是 **PyInstaller 6.17.0**，本地 `.venv/Lib/site-packages/PyInstaller/__init__.py:19` 也为 6.17.0；这比泛泛以 `>=6.10,<7` 推断机制更有用，但不证明旧 exe 当时由它构建。两处本地官方 Python 源码已直接核查：

- TOC 增量状态：https://github.com/pyinstaller/pyinstaller/blob/v6.17.0/PyInstaller/building/datastruct.py
- 二进制处理缓存、CFG/Qt 插件自动 UPX 禁用：https://github.com/pyinstaller/pyinstaller/blob/v6.17.0/PyInstaller/building/utils.py ，本地对应 `:147-155` 还证明“启用 UPX”不等于全部 Qt 文件都会压缩。
- freeze_support runtime hook：https://github.com/pyinstaller/pyinstaller/blob/v6.17.0/PyInstaller/hooks/rthooks/pyi_rth_multiprocessing.py

下列是应采用的官方机制核对入口，**当前工具没有 web 或 fetch 能力，未在线打开，不冒充在线查证**：

- 6.17.0 bootloader 环境继承与 `_PYI_APPLICATION_HOME_DIR`／`_PYI_PARENT_PROCESS_LEVEL`：https://pyinstaller.org/en/v6.17.0/advanced-topics.html#environment-variables-used-by-frozen-applications
- 冻结多进程及 windowed 标准流：https://pyinstaller.org/en/v6.17.0/common-issues-and-pitfalls.html
- Python 3.14 优化等级：https://docs.python.org/3.14/using/cmdline.html#cmdoption-O 与 https://docs.python.org/3.14/using/cmdline.html#cmdoption-OO

因此，本轮能直接坐实 TOC 缓存与 freeze_support 分流；bootloader 的确切路径复用仍由主持人补官方资料或交给最小实验裁决。不能让一个尚未核实的机制成为改交付形态的主要理由。

## 四、最多五项优先行动及最小验证实验（均未执行）

1. **P0：先建立可追溯且失败明确的当前 onefile 基线。** 固定锁文件、Python 架构、PyInstaller/hooks/UPX 版本和源码状态，保留完整构建日志、参数、exe 哈希与成员清单。最小验证：对脚本模拟 PyInstaller 返回 0 但没有预期 exe，以及文件系统异常，确认最终必须非零；正常冻结产物跑一个真实 XLSX 导入、绘图、Excel/Word 导出、一次 NDAX 转换。历史 4.0.1 exe、78MB、20.8s、891 passed 均不作为当前性能或质量基线。
2. **P1：恢复开发增量所需 workpath，正式 onefile 交付不变。** 保留分析状态与“清空正式输出”分开，失败诊断也保留。最小验证：相同源码连续构建两次，再改一个纯 Python 文件构建一次，记录 TOC 存在、Analysis/PYZ/PKG/EXE 各阶段日志与耗时；当前清理策略作为控制组。此项只针对构建效率，不承诺 exe 体积或运行吞吐提升。
3. **P1：分阶段测启动，再决定是否统一 launcher。** 最小 A/B 只改变入口，固定 onefile、UPX、依赖；从进程创建分别记录闪屏、主窗绘制、核心操作成功时间，同时检查 Qt 消息处理器、QT_ACCESSIBILITY 行为以及 worker 是否误建 GUI。先将问题定义为入口一致性及用户反馈改进，不承诺实际 ready time 下降。只有实测确认重导入显著时，再讨论更早 freeze_support 等小改动。
4. **P2：按 archive 实际贡献选择一个瘦身／压缩实验。** 先按压缩／解包字节区分 Qt、科学计算库、Matplotlib 数据和业务资源，再选最大的明确非必需成员，或单独做 UPX 开关 A/B；不要先删所有 hidden import、Excel 引擎或追求 optimize=2。验收要求成员差异、产物字节、启动体验及相应功能回归同时成立。UPX 引发的安全软件和兼容风险须记录，不能靠关闭防护证明更快。
5. **P2：用小规模冻结 NDAX 实验裁决多进程机制，再决定是否需要 onedir 对照。** 同一小／大文件集，先测 onefile 下 1、2、预算 worker；记录进程树、父子 `_MEIPASS`、实际创建的 `_MEI` 目录及写入量、转换时间和进程树总内存，校验输出一致。若怀疑解包成本，再只增做一个同依赖 onedir 诊断构建，不直接发布或改成安装版。进程总 RSS 可能重复计算共享页，要明确它是口径一致的观测指标，不是精确物理内存占用。

所有启动实验均不清空整个 TEMP、不删除仍运行的 `_MEI`。普通 onefile 每次新启动仍有准备过程，第二次运行并不等于“完全不解包”；应分别注明应用首次配置／字体缓存、OS 文件缓存和重复运行条件。现有日志只作为后段初始化指标，用外部窗口／操作观测补足启动前段。

## 五、结论与残余风险

近期路线是：**单 EXE 主线不变 → 可靠产物与日志 → 留住分析缓存 → 独立验证入口与启动分段 → 按清单做一个高价值瘦身实验 → 用冻结多进程实测裁决争议。** 不把 onedir、安装器、Nuitka 当成预定终点，也不因为参数已经很多就认定优化空间耗尽。

尚缺：当前源码的可追溯冻结产物、在线 bootloader 机制核实、传递导入画像、真实用户机器的防护／存储条件及性能门槛。任何明显提速、压缩率和“最大运行热点”的排名都仍不足以支持决策。

```acceptance-report
{
  "criteriaSatisfied": [{"id":"criterion-1","status":"satisfied","evidence":"读取全部首轮发言、用户反馈及主持人待复核项，结合当前构建、入口、CI 和本地 PyInstaller 6.17.0 官方源码提供修正表与五项最小实验。"}],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [],
  "validationOutput": ["只读文件核验完成；未运行构建、应用、测试或性能测量；唯一持久写入为会议黑板。"],
  "residualRisks": ["没有 web/fetch，bootloader 环境继承的官方在线说明未直接核实。", "无当前冻结版本性能数据，入口改动、UPX、缓存和多进程收益均待实验。"],
  "noStagedFiles": true,
  "diffSummary": "未修改项目源码，仅追加本次会议分析。",
  "reviewFindings": ["分析 workpath 在成功后被删除；无 spec 不等于无增量机制。", "逐 worker 完整解包和业务导入非瓶颈均证据不足。", "缺失 exe 可仅警告、发布无 exe 可成功退出，且构建 stdout 未转发。"],
  "manualNotes": "官方本地包源码版本与 uv.lock 均为 6.17.0；性能结论未实测。noStagedFiles 仅表示本代理未暂存文件，未检查原有 git 暂存区。"
}
```

---

## DeepSeek (Round 2): 撤回首轮"每worker重新解压"与"optimize=1去docstring"两处错误，强化no-clean失效根因，并按收益机制/成本/风险重排五项优先级。

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


---

## GLM (Round 2): GLM Round 2：交叉核查表、自我修正与最小变更落地排序

# GLM（务实实施视角）Round 2：交叉核查与落地排序

> 方法：先读黑板全部 Round 1 条目、用户反馈与 transcript 主持人待复核项，再逐项用当前工作树源码复核。本轮零构建、零安装、零改动，唯一写入为本条目。以下所有"文件:行号"均来自本轮实读；历史文档数字明确标注为历史，不作为当前基线。

## TL;DR

1. **GPT 对 `--no-clean` 的质疑本轮逐行证实**：`scripts/build.py` 在成功构建尾部**无条件**删除 workpath（`__temp__/BatteryAnalysis`），`--no-clean` 实际不保留任何 PyInstaller 分析缓存。这是五项清单里收益/成本比最高的修复。
2. **DeepSeek 的"每个 spawn worker 重新解包"论据需要修正**：PyInstaller 6.17.0（uv.lock:837-838 锁定）引导器自 v4.3 起通过环境变量让 multiprocessing 子进程复用父进程的解压目录，不再重复解包（外部可靠来源，本机无法复核 C 引导器源码，已标注）；但 spawn 语义下的**重复导入** numpy/pandas/NewareNDA 仍然存在，且这一点与 onedir/onefile 无关。**该修正显著削弱"onefile↔spawn 结构性冲突"，onedir 的决策权重从"多进程放大"转移回"仅首次解压"。**
3. **修正我自己的两处 Round 1 错误**：(a) 我转述了 build.py 的错误注释"optimize=1 去 docstrings"——优化等级 1 只去 assert，不去 docstring（GPT 正确）；(b) 我建议"补充 exclude：numpy.f2py 等"——numpy.f2py/`numpy.distutils`/`numpy.random._examples` **已在现行排除清单中**（build.py `_build_pyinstaller_args` 的 excluded_modules），该建议作废。
4. 入口统一（launcher.py）、ui_main_window.py 死代码清理、hidden-import 逐项瘦身——方向均获源码证实，但收益预期要收窄：入口切换不减少任何导入工作量，只把闪屏提前（感知收益）；死代码清理体积收益可忽略。
5. 当前不存在任何可信的性能/体积基线：`build/Release/battery-analyzer_4.0.1_x64.exe` 是陈旧产物（`_version.py:9` 为 5.0.2），CHANGELOG 78MB 是 v3.2.0 历史（CHANGELOG.md:128），benchmark_p2.py 头部数字是 2026-08-21 历史。测量先行仍是 P0。

## 一、交叉核查表（观点 / 证据 / 认可或修正 / 决策影响）

| # | 观点（出处） | 本轮核查证据 | 结论 | 决策影响 |
|---|---|---|---|---|
| 1 | **GPT**："no-clean 不保留 workpath 缓存，成功构建末尾仍删临时目录" | `build.py` `build()` 尾部：`if temp_path.exists(): shutil.rmtree(temp_path)` 无条件执行；随后 `_verify_and_clean()` 又对 `temp_build_dir` 再删一次；workpath 固定为 `__temp__/{name}`（`--workpath` 参数），`--no-clean` 只跳过开头的 `clean_build_dirs()` | **认可，逐行证实** | 修复=把末尾删除改为受 `no_clean` 控制，开发构建即可获得 PyInstaller 分析缓存复用；零业务代码改动，`__temp__/` 已在 .gitignore:4 |
| 2 | **DeepSeek**："onefile 下每个 spawn worker 重新解压/重新导入，I/O 与内存放大 N 倍" | 打包链为 PyInstaller 6.17.0（uv.lock 锁定）。官方文档/变更记录：v4.3 起引导器向 multiprocessing spawn 子进程传递父进程解压目录，子进程**不再重复解包**（本机 wheel 只含编译后引导器，C 源码无法复核——**标注为可靠外部来源引用，未经本地验证**）。重复导入 numpy/pandas 仍会发生（spawn 语义），但 onedir 下同样如此 | **部分修正** | "结构性冲突"降级为"spawn 通用代价"；onedir 对 NDAX 批量转换的收益被高估，其真实收益=免除**首次**解压。是否上 onedir 应由首启/热启对照数据决定（清单第 5 项一次性验证） |
| 3 | **GPT**："optimize=1 不删 docstring，build.py 注释有误" | build.py 注释原文："Python 字节码优化：去除 docstrings 和 assert 语句，减小体积并略微提速"。Python 语义：`-O`（=1）只去 assert；去 docstring 需 `-OO`（=2） | **认可；并修正我 Round 1 的重复错误** | optimize=1→2 的实际体积收益比注释暗示的更小，且删 docstring 影响 introspection/reflection，维持 P3，不作为候选动作 |
| 4 | **三方共识**："打包入口应统一为 launcher.py" | 事实成立：build.py `main_file_path` = main_window.py；launcher.py 的 `main()` 先建 QApplication+splash（仅依赖 PyQt6 基类）再 `from ...main_window import main`；main_window.py:22-24 顶层 import 三个 Mixin 拉起整个初始化模块图；pyproject [project.scripts] 亦指向 launcher | **方向认可，收益预期收窄** | 入口切换**不减少导入总量**，只是把 splash 显示点提前；onefile 下 splash 出现时间还受解压时长下限约束。"更早可见"≠"更早可操作"（transcript 待复核项 4 正确：`QTimer.singleShot(0, _deferred_init)` 仍在 GUI 线程串行执行）。验收必须用三点计时 |
| 5 | **DeepSeek**："ui_main_window.py 为 Designer 遗留死代码" | 本轮 grep `ui_main_window` 全 src 零引用（文件存在于 src/battery_analysis/ui/，内容自不含引用）；唯一引用是 build.py hidden-import 清单里的 `battery_analysis.ui.ui_main_window` | **认可** | 删文件+删 hidden-import 两行即可；PYZ 内 pyc 体积收益可忽略，属整洁性清理，可与第 4 项同批验证，不单列优先级 |
| 6 | **GLM Round 1 P2**："补充 exclude：numpy.f2py/numpy.doc" | excluded_modules 已含 `numpy.testing`、`numpy.distutils`、`numpy.f2py`、`numpy.random._examples` | **撤回我的建议（numpy.f2py 部分作废）** | 后续任何新增 exclude 必须先有 `pyi-archive_viewer` 清单证据，不凭库名猜 |
| 7 | **DeepSeek**："体积大头在 Qt/matplotlib/pandas/numpy 二进制" | 结构上成立（排除清单已最大化、--optimize/--strip 不作用于二进制），但**无任何当前实测数字**；4.0.1 产物陈旧、78MB 为 v3.2.0 历史 | **认可为待测推断，不引用数字** | 体积优化的一切具体动作（新 exclude、UPX、后端裁剪）都以第 2 项的 archive 清单为前置条件 |
| 8 | **GPT**："CI 无 exe 也可成功退出；发布链以单 exe 为前提" | ci-cd.yaml:148-150：`if (-not $exeFiles) { exit 0 }`；:43-44 UPX 安装标注 optional，失败静默降级为 `--noupx`（build.py `--noupx` 条件） | **认可** | 若路线二上 onedir，发布筛选与存在性契约需同步改；UPX 是否启用目前取决于构建机 PATH，同源码不保证同压缩路径——产品发布前应显式固定 |
| 9 | **主持人待复核项 3**："没有手写 spec 不等于没有增量缓存" | PyInstaller 无 spec 时每次生成临时 spec 并写入 workpath；workpath 中的分析/TOC 缓存本可复用，但本项目把 workpath 每次删光（见第 1 行）——即"缓存机制存在，被脚本主动丢弃" | **认可并定位根因** | 修复路径明确（第 1 项），无需引入手写 spec |
| 10 | **DeepSeek/GLM**："launcher 入口切换是低风险改动" | 本轮补核：launcher.main 与 main_window.__main__ 块的警告过滤（sipPyTypeDict、dataChanged）、qInstallMessageHandler、freeze_support 均等价齐备；`main_window.main(app, splash)` 委托签名兼容 | **认可，风险确实低** | 但必须跑冻结态冒烟（不能把 uv 下的冒烟当冻结回归，也不能把冒烟当完整功能回归） |

## 二、最小变更优先清单（≤5 项，均独立可回滚）

**P1 · 保留 PyInstaller 分析缓存**
- 改动：`scripts/build.py`——`build()` 尾部的 `shutil.rmtree(temp_path)` 与 `_verify_and_clean()` 里的删除，改为仅在非 `--no-clean` 时执行（约 5 行）。
- 成本/风险：极低；`__temp__/` 已被 .gitignore:4 覆盖，无脏工作树风险；仅开发迭代受益，正式构建行为不变。
- 验收：同一 commit 连续两次 `build.py Release --no-clean`，第二次 PyInstaller 日志出现分析缓存复用、总时长下降，且两次产物字节数一致。

**P1 · 测量先行：建立 5.0.2 基线（零代码）**
- 改动：无。动作：a) `pyi-archive_viewer -l` 列 onefile 成员按大小排序取 top-10；b) 三点计时——进程创建→splash 可见→主窗口可见→日志 `Background initialization completed in %dms`（window_init.py 已有该日志），冷/热各 3 次取中位数；不删除运行中进程的 _MEI 目录、不清整个 TEMP。
- 成本/风险：无代码风险；唯一成本是构建一次 5.0.2。
- 验收：清单与计时记录进黑板/文档，显式标注取代 4.0.1 旧产物与 CHANGELOG 历史数字；此后所有体积/启动动作以此为对照。

**P2 · 统一入口为 launcher.py**
- 改动：`scripts/build.py` 的 `main_file_path` 改为 `src/battery_analysis/main/launcher.py`（1 行），或显式注释决策维持现状。
- 成本/风险：低；本轮已核验 launcher 与 main_window 两套入口的警告过滤/freeze_support/委托签名等价。剩余风险集中在冻结态行为，需真机冒烟。
- 验收：exe 冒烟链（splash→主窗→打开数据文件→绘图→导出 Excel/Word→切换语言）通过，且基线三点计时中 splash 时间点提前；"可交互时间"不劣化。

**P2 · hidden-import 死代码清理与逐项瘦身**
- 改动：删 `src/battery_analysis/ui/ui_main_window.py` + build.py hidden-import 对应行；随后每次只多验证一个（如 `battery_analysis.main.battery_chart_viewer` 是否本可自动追踪）。
- 成本/风险：每项 1 次构建+冒烟；单行 diff 可回滚；验证不过的恢复。
- 验收：删除项构建成功、冻结冒烟通过；不通过的项恢复并记录"必要"结论，形成 hidden-import 必要性台账。
- **禁止项**：不做"盲删 hidden imports"——逐个验证是本项的硬性约束。

**P3 · spawn 子进程行为一次性验证（为 onedir 决策供证据）**
- 改动：无。动作：5.0.2 exe 批量 NDAX 转换时观察 %TEMP% 是否出现多个 _MEI 目录（验证第 2 行的外部结论），并测 worker=1/2/预算值 的吞吐与进程树峰值 RSS。
- 成本/风险：无代码风险。
- 验收：确认"子进程是否重复解包"的真伪与 worker 数拐点，据此决定是否值得为多进程场景上 onedir——在此之前 onedir 不立项。

## 三、两条路线

**路线 A：单 EXE 约束不可放宽（默认路线）**
- 保持 PyInstaller 6.17.0 onefile 不动，执行上述 P1→P3。
- 体积空间来源（按确定性排序）：archive 清单驱动的新 exclude → UPX A/B（CHANGELOG.md:484 有禁用 UPX 的历史事故，必须同机 A/B + 杀软实测后才能定，且 CI 的 optional 安装要改为显式固定）→ optimize=2（P3，需反射/内省全量回归，收益小）。
- 明确天花板：Qt6/matplotlib/pandas/numpy/NewareNDA 的二进制与数据文件构成体积下限，--strip/--optimize 对其无效；启动时间下限 = 解压 + 解释器 + PyQt6 导入，入口优化只影响感知段。
- 不换 Nuitka：文档存在（docs/NUITKA_BUILD.md）但从未接入 Makefile/CI，Python 3.14 + Nuitka 兼容性未证，收益未证，不符合"收益驱动"原则。

**路线 B：约束可放宽（仅在第 5 项数据支持时启动）**
- 在 build.py 增加 onedir 模式参数，ZIP 分发作为第二发布配置，保留 onefile 便携版双轨。
- 预期收益修正后重新表述：免除**首次**解压（热启动本就受 OS 缓存），而非 DeepSeek 所述的"消除 N×解压"——后者已被外部机制修正。
- 连带改动：CI 发布筛选（ci-cd.yaml:148-150）与"缺产物 exit 0"的失败契约；`file_controller.py` 用 `os.path.dirname(sys.executable)` 定位项目根、`config_utils.py` 生产路径含 exe 同级目录与 `~/.battery_analysis`，onedir 下需验证用户数据写入位置语义。
- 决策门槛：同功能同输出下，首启/多进程内存指标显著改善且发布链迁移成本可接受；否则维持路线 A。

## 四、已知 / 推断 / 外部引用 / 待实测 汇总

- **已知（本轮实读源码）**：PyInstaller 6.17.0（uv.lock）；workpath 无条件删除两处；optimize=1 注释错误；numpy.f2py 已排除；入口=main_window.py 且顶层 Mixin 导入链存在；launcher 委托签名兼容；ui_main_window 零引用；ui/ 无 __init__.py（PEP420，hidden-import `battery_analysis.ui` 兜底——**不动它**）；`__temp__/` 已 gitignore；CI 缺 exe exit 0；版本 5.0.2 vs 产物 4.0.1 不一致；`_MEIPASS` 兼容路径在 i18n/style_manager/config_utils/environment_utils 均有处理，onedir 迁移有基础。
- **推断（结构成立、无数字）**：体积大头为 Qt 等二进制；入口切换只提前 splash；hidden-import 多数可能可自动追踪。
- **外部引用（可靠来源，本机未验证）**：PyInstaller ≥4.3 引导器让 multiprocessing spawn 子进程复用父进程解压目录（官方文档/变更记录；本机 wheel 仅含编译引导器，无法复核 C 源码）。
- **待实测**：当前 exe 体积与 archive 构成；冷/热启动三点计时；spawn 子进程解包行为验证；UPX A/B；重复构建缓存收益。
- **纪律确认**：未盲删 hidden imports；冒烟测试不当作完整功能回归；未编造任何当前性能数字；历史文档数字均已标注出处与年代。

---
