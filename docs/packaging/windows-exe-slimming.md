# Windows EXE 精简完整台账（v5.1.4）

## 范围与证据口径

本记录覆盖从 v5.1.3 之后开始的全部 EXE 精简，不只覆盖 Styler 最后一轮。发布保留既有分析算法、容量口径、报告交付版本与账本；非应用入口的可选库能力边界明确列出。

- 起点：v5.1.3 / `02daa47`；早期两次本地提交 `f6fec4e`（AVIF）、`9543a66`（objectify / Qt PDF）与后续未提交优化一并纳入发布 PR。
- 历史真实候选：84,075,964 → **73,687,890 字节**，减少 **10,388,074 字节 / 12.35558%**。十进制 84.0760 → 73.6879 MB，不是 MiB。
- 本页历史体积来自同一应用版本 5.1.3 的独立候选，不能直接当作 v5.1.4 云端附件大小。干净发布工作区重建的结果见 [本版说明](../RELEASE_NOTES_v5.1.4.md)。
- 本轮 9 项调整：7 个新增显式模块排除项、QtGui 插件过滤、Matplotlib 示例资源过滤。其余 65 个排除项在精简前已存在，下面完整列出，但不虚构它们在本轮的单独收益。
- 机器可读、完整逐项名单见 [JSON 台账](windows-exe-slimming-v5.1.4.json)；历史 build/size-check 路径为本地诊断来源，默认被 Git 忽略，不是要求读者在远端下载这些临时目录。关键清单与结果已持久化在本目录。

## 各轮真实 EXE 测量

| 调整 | 对照（字节） | 候选（字节） | 独立减少（字节） |
|---|---:|---:|---:|
| Pillow AVIF 编解码器 | 84,075,964 | 79,744,083 | 4,331,881 |
| lxml.objectify | 79,744,083 | 78,707,466 | 1,036,617 |
| Qt PDF 图片读取插件 | 78,707,466 | 75,836,871 | 2,870,595 |
| Jinja2 模板引擎 | 75,837,491 | 75,534,080 | 303,411 |
| lxml.html | 75,534,080 | 75,186,656 | 347,424 |
| lxml.sax | 75,186,656 | 75,132,273 | 54,383 |
| Matplotlib 示例数据 | 75,132,273 | 74,720,380 | 411,893 |
| SQLite 标准库与原生运行库 | 74,720,380 | 73,806,185 | 914,195 |
| Pandas Styler 残留支线 | 73,806,185 | 73,687,890 | 118,295 |

**620 字节差异说明**：Jinja2 轮重新构建对照从 75,836,871 增至 75,837,491 字节，保留负载/代码均相同；本轮真实独立收益为 303,411，而非直接跨历史产物相减的 302,791 字节。9 轮独立收益合计 10,388,694 字节，扣除此 620 字节重建差异，才是首尾净减少 10,388,074 字节。归档压缩条目估算不冒充 EXE 实测。

## 全部被移除模块与资源（精确名单）

原始 EXE 对最终历史候选的直接归档复核：共 **45 个 Python 模块、39 个文件条目**退出；无新增模块/文件，保留代码与 DLL/资源内容不变，base_library 解包内容相同。AVIF 首轮 base_library.zip 仅 ZIP 条目顺序变化，不是标准库代码删除。

### 1. Pillow AVIF 编解码器

不再提供 AVIF 图片读写；应用支持的图表和 Office 图片格式不使用 AVIF。

移除的 Python 模块：

```text
PIL.AvifImagePlugin
```

移除的文件条目：

```text
PIL/_avif.cp314-win_amd64.pyd
```

### 2. lxml.objectify

不提供 lxml 对象化 XML API；Word/openpyxl 所需 etree 保留。

移除的文件条目：

```text
lxml/objectify.cp314-win_amd64.pyd
```

### 3. Qt PDF 图片读取插件

QImageReader 不再将 PDF 作为图片读取；不是删除 Matplotlib 的 PDF 导出。

移除的文件条目：

```text
PyQt6/Qt6/bin/Qt6Pdf.dll
PyQt6/Qt6/plugins/imageformats/qpdf.dll
```

### 4. Jinja2 模板引擎

不提供 Pandas Styler/Jinja2 模板能力；应用报告使用专用 XlsxWriter/python-docx writer。

移除的 Python 模块：

```text
jinja2
jinja2._identifier
jinja2.async_utils
jinja2.bccache
jinja2.compiler
jinja2.constants
jinja2.debug
jinja2.defaults
jinja2.environment
jinja2.exceptions
jinja2.ext
jinja2.filters
jinja2.idtracking
jinja2.lexer
jinja2.loaders
jinja2.nodes
jinja2.optimizer
jinja2.parser
jinja2.runtime
jinja2.sandbox
jinja2.tests
jinja2.utils
jinja2.visitor
```

### 5. lxml.html

不提供 lxml HTML 清洗、解析与 diff 工具；optparse 因唯一调用方 _diffcommand 消失自然退出，不是直接排除标准库。

移除的 Python 模块：

```text
lxml.html
lxml.html.ElementSoup
lxml.html._diffcommand
lxml.html._html5builder
lxml.html._setmixin
lxml.html.builder
lxml.html.clean
lxml.html.defs
lxml.html.formfill
lxml.html.html5parser
lxml.html.soupparser
lxml.html.usedoctest
optparse
```

移除的文件条目：

```text
lxml/html/_difflib.cp314-win_amd64.pyd
lxml/html/diff.cp314-win_amd64.pyd
```

### 6. lxml.sax

只去掉 lxml SAX 适配层，标准库 xml.sax 和 etree PullParser 保留。

移除的文件条目：

```text
lxml/sax.cp314-win_amd64.pyd
```

### 7. Matplotlib 示例数据

不提供示例程序数据；字体、styles、图标、matplotlibrc、后端和 Windows wheel DLL/加载顺序文件保留。

移除的文件条目：

```text
matplotlib/mpl-data/sample_data/Minduka_Present_Blue_Pack.png
matplotlib/mpl-data/sample_data/README.txt
matplotlib/mpl-data/sample_data/Stocks.csv
matplotlib/mpl-data/sample_data/axes_grid/bivariate_normal.npy
matplotlib/mpl-data/sample_data/data_x_x2_x3.csv
matplotlib/mpl-data/sample_data/eeg.dat
matplotlib/mpl-data/sample_data/embedding_in_wx3.xrc
matplotlib/mpl-data/sample_data/goog.npz
matplotlib/mpl-data/sample_data/grace_hopper.jpg
matplotlib/mpl-data/sample_data/jacksboro_fault_dem.npz
matplotlib/mpl-data/sample_data/logo2.png
matplotlib/mpl-data/sample_data/membrane.dat
matplotlib/mpl-data/sample_data/msft.csv
matplotlib/mpl-data/sample_data/s1045.ima.gz
matplotlib/mpl-data/sample_data/topobathy.npz
```

### 8. SQLite 标准库与原生运行库

不提供 SQLite/基于它的 Pandas SQL 连接；保留 pandas.io.sql 和应用 Excel/NDAX/报告路径，未来 SQL/缓存功能需恢复依赖。

移除的 Python 模块：

```text
sqlite3
sqlite3.__main__
sqlite3.dbapi2
sqlite3.dump
```

移除的文件条目：

```text
_sqlite3.pyd
sqlite3.dll
```

### 9. Pandas Styler 残留支线

入口仅显式排除 pandas.io.formats.style；style_render、MarkupSafe、模板自然退出。普通 DataFrame ExcelFormatter、XlsxWriter/openpyxl writer 保留。

移除的 Python 模块：

```text
markupsafe
markupsafe._native
pandas.io.formats.style
pandas.io.formats.style_render
```

移除的文件条目：

```text
markupsafe-3.0.3.dist-info/INSTALLER
markupsafe-3.0.3.dist-info/METADATA
markupsafe-3.0.3.dist-info/RECORD
markupsafe-3.0.3.dist-info/REQUESTED
markupsafe-3.0.3.dist-info/WHEEL
markupsafe-3.0.3.dist-info/licenses/LICENSE.txt
markupsafe-3.0.3.dist-info/top_level.txt
markupsafe/_speedups.cp314-win_amd64.pyd
pandas/io/formats/templates/html.tpl
pandas/io/formats/templates/html_style.tpl
pandas/io/formats/templates/html_table.tpl
pandas/io/formats/templates/latex.tpl
pandas/io/formats/templates/latex_longtable.tpl
pandas/io/formats/templates/latex_table.tpl
pandas/io/formats/templates/string.tpl
```

## 现行完整显式排除清单（72 项，含既有 65 项）

以下逐字对应 scripts/build.py 的 excluded_modules。旧项不等于本轮新删项；父包排除也覆盖其子模块。未列出的自然孤立模块/资源以上面的真实归档清单为准。

```python
excluded_modules = [
            # 开发/测试/构建工具
            "pytest", "pylint", "black", "astroid", "pylint_json2html",
            "setuptools", "pip", "pkg_resources",
            "IPython", "jupyter", "jupyter_client", "jupyter_core",
            # pywin32 附带的无用包
            "pythonwin", "adodbapi", "win32com", "win32com.shell",
            # matplotlib 测试/不用的后端
            "matplotlib.tests", "matplotlib.testing", "matplotlib.sphinxext",
            "matplotlib.backends.backend_qt4", "matplotlib.backends.backend_qt5",
            "matplotlib.backends.backend_wx", "matplotlib.backends.backend_gtk",
            "matplotlib.backends.backend_gtk3", "matplotlib.backends.backend_gtk4",
            "matplotlib.backends.backend_webagg", "matplotlib.backends.backend_nbagg",
            "matplotlib.backends.backend_pgf",
            # numpy 无用模块
            "numpy.testing", "numpy.distutils", "numpy.f2py",
            "numpy.random._examples",
            # pandas 不需要的模块
            "pandas.tests",
            # SQLite 仅用于 Pandas SQL 支线，现有 Excel/报告/NDAX 路径不使用它。
            "sqlite3",
            # Jinja2 仅供 Pandas Styler 模板；应用报告使用 XlsxWriter/python-docx。
            "jinja2",
            # Styler 模板支线不参与普通 DataFrame 的 Excel 导出或应用报告。
            "pandas.io.formats.style",
            # 其他库测试
            "openpyxl.tests",
            # Pillow 自动收集的 AVIF 编解码器不属于图表导出或 Office 报告支持的格式。
            "PIL.AvifImagePlugin",
            # lxml 钩子会收集 objectify；文档处理只需 etree，保留其原生库。
            "lxml.objectify",
            # lxml 钩子全量收集的 HTML 工具不参与 Excel/Word/NDAX 路径；保留 etree。
            "lxml.html",
            # 只排除未使用的 lxml SAX 适配层，标准库 xml.sax 和 etree 均保留。
            "lxml.sax",
            # GUI 框架排除（只用 PyQt6）
            "tkinter", "PySide6", "PySide2", "PyQt5",
            # 不使用的 PyQt6 子模块
            "PyQt6.QtMultimedia", "PyQt6.QtMultimediaWidgets",
            "PyQt6.QtPositioning", "PyQt6.QtSensors",
            "PyQt6.QtTextToSpeech", "PyQt6.QtWebChannel",
            "PyQt6.QtWebSockets", "PyQt6.QtWebEngineWidgets",
            "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineQuick",
            "PyQt6.QtHelp", "PyQt6.QtSql", "PyQt6.QtQml",
            "PyQt6.QtQuick", "PyQt6.QtQuick3D", "PyQt6.QtQuickWidgets",
            "PyQt6.QtDBus", "PyQt6.QtBluetooth", "PyQt6.QtNfc",
            "PyQt6.QtXml", "PyQt6.QtDesigner", "PyQt6.QtSerialPort",
            "PyQt6.QtStateMachine", "PyQt6.QtPdf", "PyQt6.QtPdfWidgets",
            "PyQt6.QtRemoteObjects", "PyQt6.QtSpatialAudio",
        ]
```

新增显式项仅：`PIL.AvifImagePlugin`、`lxml.objectify`、`lxml.html`、`lxml.sax`、`jinja2`、`sqlite3`、`pandas.io.formats.style`。

## 既有排除项的能力边界

这 65 项在开始本轮精简前已存在；这里补齐其功能含义，不将其算作本版新删除功能，也不保证每个排除名在当前依赖版本中都实际存在或原本会被收集。

- **开发、测试、构建与交互环境**：pytest / pylint / black / astroid / pylint_json2html、setuptools / pip / pkg_resources、IPython / Jupyter 不随 EXE 提供。EXE 不是 IDE、Notebook、包安装器或开发测试环境；源码开发依赖与 uv.lock 未因此删包。
- **pywin32 附带组件**：pythonwin、adodbapi、win32com（含 shell）不提供 PythonWin IDE、ADO 数据库及 COM 自动化接口。应用直接生成 Office 文件，不依赖启动外部 Word/Excel 的 COM；pywintypes 等实际运行依赖继续保留。
- **Matplotlib 专用测试、文档及非应用后端**：tests / testing / sphinxext 与清单中的 Qt4/Qt5 旧入口、wx、GTK、WebAgg/Notebook、PGF 后端不打包。现有 PyQt6/QtAgg 图表、Agg 渲染、SVG 输出与交互工具栏保留；不额外承诺 wx/GTK/浏览器/Notebook/TeX 专用集成。
- **NumPy 与表格库的开发内容**：numpy.testing / distutils / f2py / random._examples、pandas.tests、openpyxl.tests 不作为 EXE 的测试、Fortran 编译或示例环境提供。注意 pandas.tests 不等于实际运行必须保留的 pandas.testing。
- **其他 GUI 框架**：tkinter、PySide6、PySide2、PyQt5 不收集；应用使用 PyQt6，不提供替换绑定或 Tk UI。
- **未使用的 PyQt6 Python API**：完整名称见上面的 27 项 Qt 子模块清单，涵盖多媒体/空间音频、定位/传感器、语音合成、WebChannel/WebSocket/WebEngine、Help/SQL、QML/Quick/Quick3D、DBus/蓝牙/NFC、Qt XML/Designer/串口/状态机、PDF Widgets 与远程对象。EXE 不作为这些 Qt API 的通用开发运行环境；不能据此删除其余插件需要的原生共享依赖（例如 Qt6Network.dll）。

## 压缩、优化和钩子策略

- 沿用 PyInstaller `--onefile` 与默认归档 zlib 压缩，未引入额外压缩器或修改压缩级别，不能把已有压缩策略再算作本轮新收益。
- 沿用 `--optimize=1`：删除 Python assert 语句、关闭 __debug__，**保留 docstrings**；不是 optimize=2。发布验证脚本的关键业务校验显式抛异常，不依赖冻结后可能移除的 assert。
- 明确使用 `--noupx`，**不启用 UPX，不使用 --strip**；v5.1.1 的 Python/Qt DLL 加载安全修复保持生效，原生 DLL 保持原样。
- 不替换 NumPy/Pandas；完整携带 numpy.libs（包括重命名 MSVC DLL）和 NumPy 元数据。
- scripts/pyinstaller_hooks/hook-PyQt6.QtGui.py 沿用官方 add_qt6_dependencies，只过滤 qpdf.dll，Qt6Pdf.dll 因依赖消失自然退出。
- scripts/pyinstaller_hooks/hook-matplotlib.py 沿用官方数据与 Windows delvewheel DLL/加载顺序收集；collect_data_files("matplotlib", subdir="mpl-data", excludes=["sample_data"]) 仅过滤 15 个示例文件。

## 保留、不误删与未来恢复条件

- 保留 PyQt6 Core/Gui/Widgets、Qt6Network.dll（触摸插件原生依赖）、软件渲染库、兼容 DLL、完整应用图标/主题、Qt 翻译及字体，不按当前机器环境裁剪硬件支持。
- 保留 matplotlib 字体、styles、后端、工具栏资源、matplotlibrc；不删除字体、时区/pytz 数据，也不按本地默认语言删翻译。
- 保留 lxml.etree、lxml._elementpath、et_xmlfile、Pillow、openpyxl、python_calamine、XlsxWriter、python-docx，兼顾 openpyxl 的非 lxml 回退路径。
- 保留 pandas.testing：实测阻断会令 import pandas 失败，不能因 testing 名称删除。保留 pandas.io.formats.excel、普通 ExcelFormatter、CSS 工具和两种 Excel writer；_XlsxStyler 不是这里排除的模板 Styler。
- 保留 pydoc、multiprocessing、compression.zstd 等共享依赖；未实施 lxml.builder、lxml.isoschematron、doctest 等后续候选删除，估算不记为已完成。
- AVIF、Qt PDF-as-image、lxml objectify/HTML/SAX 适配层、Jinja2/Styler/MarkupSafe、SQLite 不是当前应用入口；不承诺这些公共库扩展 API 仍可用。若未来加入对应功能，应恢复入口排除项及原生库、模板/资源并重新验证。
- Matplotlib PDF 导出与 Qt PDF 图片读取是不同能力；后者被裁剪，不应笼统写成“移除了应用 PDF 功能”。

## 已验证与未验证

- 历史最终精简候选：全量 1284 tests passed；归档 CArchive/PYZ/base_library 比对；验证 probe 不改变应用负载；当前对照/候选重新生成清单相同；实际 EXE --smoke-test 退出 0；受保护文件哈希不变。
- 业务覆盖标准/多脉冲 × Pass/Fail，Excel 单元格/数值格式/样式、Word 段落/表格/图片数量、PNG/SVG/JPG/TIF/WEBP 图表、Qt 图片/ICO/SVG 图标像素、合成 NDAX Step.xml 配方。
- 另覆盖 openpyxl/calamine 读取、Pandas 聚合、XlsxWriter/openpyxl 普通 DataFrame 双 writer 回读、Office 嵌图、etree XML/PullParser、标准 SAX、包内字体/styles/图标。
- 独立应用子进程和冻结 probe 在导入前阻断不应使用的支线，记录连被业务捕获的导入/示例数据读取尝试；SQLite 和 Styler 最终零尝试。开发测试插件可以依赖 Jinja2/MarkupSafe，不对整个 pytest 环境粗暴阻断。
- 源码 Qt 仍有 PDF reader，冻结包只允许这一个格式差异；报告/图片/图标按内容比较。历史日期和 DPI 改变时重跑当前对照，不靠静默归一化掩盖差异。
- 以上历史 1284 包括本地尚未提交的 UI 测试；发布 PR 不包含这些 UI/翻译改动，干净 v5.1.4 的测试数量和产物见本版发布说明。
- 未覆盖全部生产 NDAX 大文件、硬件/显卡/驱动、所有用户数据组合、新版用户实际试用和人工 Office 视觉验收，不能宣称全场景无回归。
- 首次 Styler 构建曾发生进程初始化失败 0xC0000142，保留诊断、同排除项重试成功；只有最终成功构建/验证计入结论。

## 维护位置与复现

- 构建入口：scripts/build.py；钩子：scripts/pyinstaller_hooks/；回归：tests/test_build_scripts.py。
- Windows 标准构建：`uv run python scripts/build.py Release`；注意该命令会清理当前工作区 build/Release，复核历史产物应使用独立工作区，不能覆盖用户旧 Release。
- CI：Ruff → pytest → 构建 → 冻结 --smoke-test；只有 tag 触发的构建成功后才运行 Release 上传。提交/tag 推送成功不等于远端附件已发布。
- v5.1.4 使用 annotated tag，tag 正文附上本台账全文（包含现行 72 项排除与 9 轮精确移除清单），并同时提供常规发布说明。
