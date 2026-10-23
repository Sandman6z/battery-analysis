# GPT (Round 1): 保留 PyInstaller，先建立可测双发布路线，而不是为单文件换技术栈

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