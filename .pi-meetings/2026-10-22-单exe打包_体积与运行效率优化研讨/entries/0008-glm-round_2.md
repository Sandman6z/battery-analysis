# GLM (Round 2): GLM Round 2：交叉核查表、自我修正与最小变更落地排序

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