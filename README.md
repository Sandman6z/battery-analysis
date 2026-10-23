# BOEDT Battery test GUI Tool

**当前软件版本：v5.1.0 — 图表导航恢复、轴刻度区拖动与菜单工具栏验收**

本版变更见 [CHANGELOG](CHANGELOG.md#v510--2026-10-23) 和 [v5.1.0 发布说明](docs/RELEASE_NOTES_v5.1.0.md)；v5.0.0 的 NDAX 迁移要求继续适用。

主分析直接读取 `1_ndax` 中的原始 NDAX，不再依赖先转出的 `2_xlsx`；电流档位以 NDAX 内嵌 Step.xml 为准。Excel 继续作为报告输出，独立转换功能保留。

- **[v5.0.0 完整功能变更、迁移与验证说明](docs/RELEASE_NOTES_v5.0.0.md)**
- **[版本变更记录](CHANGELOG.md)**
- **[中文操作指南](docs/QUICK_START.md)** / **[English quick start](docs/QUICK_START_EN.md)**
- **[PDF 复查、容量来源与异常策略](docs/pdf_recheck_and_anomaly_policy.md)**

升级注意：旧 XLSX 校验和需按 NDAX 输入刷新登记；手动报告版本须不低于已有最高版本且未占用。软件 `5.1.0` 与报告编号独立，已有报告和账本不自动改写。普通缺失保留 `No data` 并记录，判定必需格缺失仍需人工确认。

## BatteryChartViewer 导航

- 绘图区左键拖动平移双轴；抓横轴/纵轴刻度区域左键拖动，只平移对应轴。
- 绘图区滚轮缩放双轴；刻度区域滚轮仅缩放对应轴，以鼠标位置为锚；右键点击复位。
- 保留 Matplotlib 工具栏；Pan/Zoom 开启时自定义手势暂停，再次点击对应按钮退出模式后恢复。Home/Back/Forward 可导航自定义操作历史。
- 主窗口样本数量和三项容量派生字段只读；样本数来自输入文件，容量在 Configuration → Rules 中维护。

## NDAX 转换并发与 CPU 留核

独立转换窗口和 `convert_batch` 共用默认 worker 预算：以本进程可用逻辑核心数 C（优先 `os.process_cpu_count()`，后备 `os.cpu_count()`，最终为 1）计算 `B = max(1, min(floor(C × 75%), C − R))`，其中 C≤4 时留 1 核，否则留 2 核。实际进程数还不超过待转换文件数，Windows 最多 61 个；无待转换文件时不创建进程池。例如 1/2/4/8/16 核对应预算 1/1/3/6/12，单核无法真正留核。主分析仍按文件串行处理。

API 的 `max_workers`（`convert_batch` 及 `ConvertWorker` 的可选关键字参数）是**请求上限**，不能突破上述默认安全预算；`None` 或兼容旧调用的 `0` 表示自动，正整数可进一步降低并发，负数抛出 `ValueError`，bool/非整数抛出 `TypeError`。

**75% 是 worker 数量预算，不是全应用 CPU 百分比硬上限。** 数值库内部线程本轮未限制，其他并行任务/转换池也可叠加；因此不保证任务管理器中的 CPU 利用率≤75%。本轮不改变取消逻辑，取消仍可能等待已提交任务结束。

## 项目文档

本项目提供了以下专项文档，位于`docs/`目录下：

- **[Pylint静态代码分析使用指南](docs/README_PYLINT.md)**：介绍如何使用Pylint进行代码质量检查
- **[文档字符串编写指南](docs/DOCSTRING_GUIDE.md)**：说明项目的文档字符串编写规范

## 开发环境配置

### 环境配置流程
> uv init
> rm .\main.py #删除自动创建的无用文件
> uv venv --python 3.14
> .\.venv\Scripts\activate
> uv sync --all-extras -i https://mirrors.aliyun.com/pypi/simple/

**注意：** 开发环境请带 `--all-extras`。pytest/pylint/pyinstaller 等开发与打包工具声明在 `[project.optional-dependencies]`（dev/build extras），裸 `uv sync` 不会安装这些工具。后续同步使用 `uv sync --all-extras --frozen`（或 `make sync`），避免移除开发工具。通常无需管理员权限。

### 开发工具安装
- **Qt Designer**：设计UI界面
  - 可以通过pip安装PyQt6或PySide6获取：`pip install PyQt6`或`pip install PySide6`
  - 本项目使用 Python 3.14 和 PyQt6，请使用项目虚拟环境中的工具，不要混用全局 Python 或 PySide6 环境。

- **打包工具**：
  - 或使用pyinstaller：`uv pip install pyinstaller -i https://mirrors.aliyun.com/pypi/simple/`

## 界面与资源

当前主窗口由 `src/battery_analysis/main/ui_builder.py` 中的 `UIBuilder` 创建，不再通过 Designer 生成的 `Ui_MainWindow.setupUi()` 构建。仓库中的 `.ui` 和 `ui_main_window.py` 是历史文件，不是当前界面的修改入口。

- 应用图标：`config/resources/icons/Icon_BatteryTestGUI.ico`，同时用于 EXE 内嵌图标和运行时窗口图标。
- 样式及样式图标：`src/battery_analysis/ui/styles/`。
- 报告模板：`src/battery_analysis/templates/`。
- 翻译：`locale/`。

打包脚本通过 `--add-data` 收集这些资源。开发环境从源码目录定位，PyInstaller 环境通过 `sys._MEIPASS` 定位；不需要手动编译 `.qrc`。

## 配置文件说明

项目使用 JSON 配置文件进行管理，文件存储在 `%APPDATA%/battery-analysis/config.json`（Windows）或 `~/.config/battery-analysis/config.json`（Linux/Mac）。

首次运行时自动创建默认配置，也可通过 **Tools → Configuration** 菜单在 UI 中管理所有配置项。

## 运行方式

### 开发运行（推荐）

```bash
uv run battery-analysis
```

已激活并安装项目的虚拟环境中也可直接运行 `battery-analysis`。
开发命令和 Debug/Release EXE 都使用 `battery_analysis.main.launcher:main`：先显示闪屏，再加载主窗口，避免绕过启动器。

## 代码质量检查

项目使用Pylint进行静态代码分析，以确保代码质量和一致性。

### 运行完整代码检查

您可以使用以下命令运行整个工程的代码质量检查：

```bash
# 使用uv运行pylint脚本
uv run scripts/run_pylint.py

# 或者直接使用Python运行（确保在虚拟环境中）
python scripts/run_pylint.py
```

该脚本会执行以下操作：
- 递归查找并分析所有Python文件（包括`src`、`scripts`和`tests`目录）
- 实时显示分析结果
- 生成JSON格式的详细报告 (`pylint_report.json`)
- 生成HTML格式的可视化报告 (`pylint_report.html`)
- 生成Markdown格式的重构计划 (`refactoring_plan.md`)

### 详细使用指南

关于Pylint的详细配置和使用说明，请参考：
- **[Pylint静态代码分析使用指南](docs/README_PYLINT.md)**

## 构建与打包

打包前运行 `uv sync --all-extras --frozen` 安装开发与构建依赖。以下命令通过 uv 使用项目虚拟环境，通常无需管理员权限或手动激活环境。

### 使用构建脚本（推荐）

项目提供了自动化构建脚本，支持Debug和Release两种模式：

- Debug 构建：
  > uv run python scripts/build.py Debug

- Release 构建：
  > uv run python scripts/build.py Release

- 重复构建并保留 PyInstaller 分析缓存：
  > uv run python scripts/build.py Release --no-clean

默认构建先清理旧输出，验证 EXE 存在后清理工作目录；`--no-clean` 保留工作目录用于增量分析。构建失败保留工作目录供诊断。首次使用 `--no-clean` 仍需完成完整分析。

脚本内部使用 PyInstaller 进行打包，包含完整的 `--exclude-module`、`--hidden-import` 和资源文件配置。如需自定义打包参数，参考 `scripts/build.py` 中的 `_build_pyinstaller_args()` 方法。

## 重要注意事项

- 始终在已激活的虚拟环境中运行或打包
- 一定在虚拟环境下安装打包工具，否则无法生成各种hook，运行会各种缺失
- 打包资源从 `sys._MEIPASS` 定位；`sys.executable` 表示可执行文件位置，不能代替 onefile 的资源解包目录
- 已移除临时测试脚本：`test_config_read.py`、`test_exe.py`、`test_exe_start.py`、`test_ui_events.py`
- 如需本地检查，请直接使用上述"开发运行"命令并验证界面与配置读取是否正常
- 软件版本唯一来源是 `src/battery_analysis/_version.py`；发布同时维护 `CHANGELOG.md` 和对应发布说明，详见 [Changelog 维护指南](docs/CHANGELOG_GUIDE.md)。不要通过改软件版本绕过报告版本冲突。

## 已知问题
1. 第五页存在空白页

## 功能更新
1. Test Information UI部分已更改为使用**滚动条**进行调整，提高了可用性
2. 添加了运行进度条显示
3. 窗口大小可自由拉伸
4. 窗口支持最大化显示