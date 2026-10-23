# GLM (Round 1): 务实核查：实际打包命令、启动路径与最小改动优化清单

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