# v5.1.4 发布说明

## 版本与范围

本次是 **5.1.4 补丁版**，集中交付 v5.1.3 之后的全部 Windows EXE 精简，并将原来只在本地临时目录中的审计结论纳入版本控制。不是只记录最后一轮 Styler，也不修改分析算法、容量判定、NDAX 主输入、异常人工确认规则、报告交付版本或历史账本。

- [全部精简与功能边界台账](packaging/windows-exe-slimming.md)
- [机器可读的完整清单与测量证据](packaging/windows-exe-slimming-v5.1.4.json)

## 全部 9 项精简

1. **Pillow AVIF**：排除 `PIL.AvifImagePlugin`，原生 `_avif` 编解码器自然退出。
2. **lxml.objectify**：移除对象化 XML 原生扩展，保留 `lxml.etree` 和 Office 所需 XML 能力。
3. **Qt PDF 图片读取**：QtGui 钩子仅过滤 `qpdf.dll`，`Qt6Pdf.dll` 随之退出；不是移除 Matplotlib 的 PDF 导出。
4. **Jinja2**：移除 23 个专用模板模块；应用报告使用 XlsxWriter/python-docx，不经 Pandas Styler 模板。
5. **lxml.html**：移除 12 个 HTML 模块、两个 HTML diff 原生扩展；`optparse` 因其唯一调用方退出而自然消失，没有直接排除这个标准库模块。
6. **lxml.sax**：仅移除 lxml SAX 适配层，保留标准库 `xml.sax`、etree XML/PullParser。
7. **Matplotlib sample_data**：仅移除 15 个示例文件；字体、styles、图标、后端及 Windows wheel DLL/加载顺序文件保留。
8. **SQLite**：移除 `sqlite3` 四个 Python 模块、`_sqlite3.pyd`、`sqlite3.dll`；保留 Pandas 及 `pandas.io.sql`，当前 UI 没有 SQL 入口。
9. **Pandas Styler 残留**：只新增 `pandas.io.formats.style` 排除，`style_render`、MarkupSafe 原生/纯 Python 模块及元数据、7 个模板自然退出；普通 DataFrame 的 ExcelFormatter 与两种 Excel writer 保留。

台账逐项列明全部 **45 个退出的 Python 模块、39 个文件条目**，并记录现行 **72 个显式排除项（65 个既有、7 个新增）**。上述两组计数分别来自实际归档差异和构建配置，不能混为一谈；旧排除项没有虚构本轮独立收益。

## 体积与压缩口径

- 历史同版本 5.1.3 候选：**84,075,964 → 73,687,890 字节**，首尾减少 **10,388,074 字节 / 12.35558%**（十进制约 84.0760 → 73.6879 MB）。
- 9 项独立实测收益与首尾值相差 620 字节，来自 Jinja2 轮重新构建对照的增长；台账明确列出，不把重建漂移算作删除收益。
- 干净 v5.1.4 发布工作区本地重建：**73,667,621 字节**。不混入未提交的 NDAX 路径提示/界面/翻译改动；版本、源码及构建路径与历史候选不同，不能把额外差值全部归因于精简。云端附件需以对应 CI 产物为准。
- 沿用 `--onefile`、PyInstaller 默认 zlib、`--optimize=1`（去 assert、保留 docstrings）。**不使用 UPX、strip 或 optimize=2**，不替换 NumPy/Pandas，不裁剪兼容 DLL、字体、翻译或时区数据。

## 本地验证

- 全仓 Ruff 检查通过；Mypy 按既有配置检查 **176 个源文件**通过。
- 干净发布工作区全量 pytest：**1276 passed**（手动测试未收集）。新版本源码/冻结报告、图片与图标一致；SQLite 和 Styler 支线导入尝试均为零，普通 DataFrame 两种 Excel writer 通过，验证 probe 未改变应用负载。结构化结果记录在 JSON 台账的 `release_validation` 字段，不以历史工作区的 1284 项通过冒充干净发布版测试结果。
- v5.1.4 真实 EXE 已重新构建，`--smoke-test` 退出码为 **0**。本地产物 SHA-256：`f8c9eabf55558f2ad97f836ef29236b7f58431b282b67cd45df7654146b340dd`；该哈希不冒充云端独立构建附件的哈希。
- 历史最终精简候选已通过全部 1284 项测试、原始/最终归档的直接复核、逐轮对照、当前基准/候选报告与图片图标比较；此历史工作区包含未提交的 UI 测试，不混入本发布 PR。
- 核心覆盖标准/多脉冲 × Pass/Fail、Excel 单元格/数值格式/样式、Word 段落/表格/图片数量、PNG/SVG/JPG/TIF/WEBP、Qt ICO/SVG 像素、合成 NDAX 配方、openpyxl/calamine 读取、XlsxWriter/openpyxl 普通 DataFrame 双 writer 回读、XML/SAX 与包内字体/styles。
- 应用子进程/冻结 probe 对 SQLite、Styler/MarkupSafe 导入和 Matplotlib 示例数据访问安装防线，连被业务捕获的尝试也记录。验证 probe 不得补入或改变发行包的应用负载；发行 EXE 本身不含这些验证钩子。

## 升级与能力边界

- 当前应用操作、Excel/Word/CSV/JSON 报告、图表、界面主题与 Matplotlib 样式继续保留；软件版本与报告编号独立，不重置历史报告或 `SHA256.csv`。
- 打包环境不再提供 AVIF、Qt PDF-as-image、lxml objectify/HTML/SAX 适配层、Jinja2/Styler/MarkupSafe、SQLite 这些非应用入口的可选库能力，不承诺所有第三方库扩展 API 都保持可用。未来增加对应入口时须恢复依赖及模板/原生资源，并重新构建验证。
- 不删除 `pandas.testing`、`et_xmlfile`、`Qt6Network.dll`、`numpy.libs`、软件渲染与硬件兼容 DLL。未实施 lxml.builder、isoschematron、doctest 等审计候选删除。
- 未覆盖全部生产 NDAX 大文件、所有硬件/显卡/驱动及用户数据组合、新版用户实际试用或人工 Office 视觉验收，不能声称全场景无回归。

## 发布方式

本版通过独立发布分支 PR 合并到 `main`，不直接推送本地未提交 UI/翻译工作。在合并提交上创建 `v5.1.4` **annotated tag**，tag 正文收录本说明及完整精简台账（包括全部现行排除与精确移除名单）。

推送 tag 会触发现有 CI：Ruff / pytest → Windows EXE 构建 → 冻结启动检查 → GitHub Release 与附件上传。PR 合并、tag 推送、远端构建与附件发布是不同阶段，须按实际结果分别确认，不因 tag 已存在就宣称附件可下载。
