# GPT (Round 2): 交叉核查：撤回重复解包论据，先修可观测性与分析缓存，保留单 EXE 主线

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