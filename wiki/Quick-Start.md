# 中文操作指南

适用于 **v5.1.2**。主分析直接读取 NEWARE **NDAX**；不需要先转 Excel，也不再编辑 `setting.ini`。

[Wiki 首页](https://github.com/Sandman6z/battery-analysis/wiki) · [English](https://github.com/Sandman6z/battery-analysis/wiki/Quick-Start-EN) · [详细说明与规则](https://github.com/Sandman6z/battery-analysis/blob/main/docs/QUICK_START.md)

## 1. 准备数据并选择项目

建议目录结构：

```text
项目目录/
├── 1_ndax/               原始 .ndax 文件（主分析输入）
├── 2_xlsx/               可选：独立转换工具的 Excel 输出
├── 3_analysis results/   自动创建：报告与版本账本
└── 4_test profile/       可选：Test Profile XML
```

两种入口任选其一：

- **Input Path → Open**：选择包含 `.ndax` 的目录（通常是 `1_ndax`）。软件自动查找同级 `4_test profile`；多个 XML 时由你选择，取消则留空。
- **Test Profile → Open**：选择 XML，软件验证文件名和内容，并定位同级 `1_ndax`。

**Output Path 固定为输入目录同级的 `3_analysis results`，只读、不可自选。** 切换项目后重新核对路径与 Profile，等待后台扫描和校验和计算完成。

> **XML 是校验文件，不是数据源。** 无 XML 时可运行，首次按提示确认使用 NDAX 内嵌配方。XML 与内嵌档位不一致时，阅读差异并决定是否继续；继续仍以 NDAX `Step.xml` 为准，不会改用 XML 档位。

## 2. 核对自动填入的信息

| 信息 | 来源与操作 |
|------|------------|
| 样本数量 | 输入 NDAX 文件数，只读；不等于每个统计格的有效样本数 |
| 型号、厂家、构造、规格方法、批次、恒流电流 | 从首个文件名解析，运行前核对；未识别型号需先补配置 |
| 脉冲电流档位 | NDAX 内嵌 `Step.xml`，不按文件名或配置表猜测 |
| 温度类型 | NDAX 内嵌 `TestInfo.xml` 的 `StepName` 含 `Freezer`（忽略大小写）为冷冻，否则为常温；缺失/不可读时报错 |
| 三项容量 | 由「规格型号 + 规格方法」等规则带出，主窗口只读；修改见下一节 |
| 测试地点、人员、设备、环境信息 | 选择地点可带出设备信息，再核对并补齐；点 Run 时保存测试信息 |

- 同批 NDAX 的温度类型、脉冲档位及顺序必须一致，否则不能分析。
- 冷冻标称温度默认 −20°C，可编辑，**不是实测温度**；填 0°C 时运行前需确认。
- 成组方式未识别而默认 `1S1P` 时会倒计时提示，请核实，不代表原文件已声明该方式。

### 修改配置的位置

打开 **Tools → Configuration**，维护型号、厂家、人员、设备与 **Rules**；新增型号要补齐对应规则。修改容量规则后，重新选择规格/方法以刷新主窗口。

- Datasheet / Calculation Nominal Capacity 是两个独立配置参数，不是从实测或厂商 PDF 自动提取；计算使用 Calculation 容量口径。
- Required Useable Capacity 支持绝对值、百分比，以及按构造方式区分的双百分比（如 `85%|75%`）。
- 配置自动保存在 `%APPDATA%\battery-analysis\config.json`，无需手改文件。

## 3. 确认报告版本，点击 Run

1. 核对路径、表单、测试信息和 **Version**，等待校验完成，再点绿色 **Run**。
2. 若提示 Profile 差异、冷冻温度或异常，先阅读详情再决定；不要直接连续确认。
3. 成功后选择 **Open Report（打开报告）** 或 **Open Path（打开路径）**。

**软件版本与报告版本不同。** 报告版本由 NDAX 校验和和已有交付自动建议，也可手填，但必须不低于自动基线及已有最高版本，且未被使用。`4.01` 与 `4.1` 视为同一编号，换测试日期也不能复用。

> 不要删除 `SHA256.csv` 绕过检查。输入变化或从旧 Excel 流程升级后，应重新选择输入目录、等待校验和刷新。只有必需交付物检查成功才计为成功；失败/取消不增加成功次数。

### 异常提示如何处理

| 情况 | 软件行为 / 你的操作 |
|------|-------------------|
| 普通非判定格缺失 | 自动继续，完成时汇总；保留 `No data`，不补零、不插值 |
| 必需判定格缺失或可分析阶段的单文件失败 | 查看可滚动详情，两次明确确认才放行；默认停止 |
| 配方损坏、同批温度/档位不一致 | 运行前拒绝；先核对数据，不能靠异常放行绕过 |
| 整批无有效实测时间戳 | 分析失败，不猜测测试日期 |

**生成成功不等于电池合格。** 报告可能为 Pass / Fail / Incomplete；部分样本缺失后放行，仍可能基于剩余样本判为 Pass，应结合有效样本数和异常记录复核。

## 4. 查看结果与追溯

- `3_analysis results` 中自动生成报告目录（`日期_v版本`）及 Word、Result/Sample Excel、PNG/SVG 图、CSV、JSON。
- `Info_Plot.json`：查看 `anomalies` 和 `analysis_audit`，追溯输入来源、容量依据、异常确认及各格有效/预期样本数。
- 应用日志：`%LOCALAPPDATA%\BatteryAnalysis\logs`。
- 已有临时目录、报告目录或 Word 不会被覆盖；先核实旧产物，再选未使用版本。正常失败/取消只清理本次新建产物，崩溃残留不自动删除。

## 5. 可选工具与界面设置

### BatteryChartViewer

**Tools → BatteryChartViewer → File → Open**，选择包含 `Info_Image.csv` 的结果数据目录。

| 鼠标位置 | 左键拖动 | 滚轮 |
|----------|----------|------|
| 绘图区 | 双轴平移 | 以鼠标为锚缩放双轴 |
| 横轴 / 纵轴刻度区 | 仅平移对应轴 | 仅缩放对应轴 |

右键复位；**Home / Back / Forward** 导航视图。工具栏 **Pan / Zoom** 开启时暂停上述自定义手势，再点一次退出后恢复；**Save** 导出图片。主窗口 View 的字号缩放不改变图表坐标。

### NDAX Converter

**Tools → NDAX Converter（NDAX 转换器）**，选择 NDAX 目录后启动转换，Excel 保存到同级 `2_xlsx`。独立窗口不改变主分析配置，**不是分析前置步骤**。

### 设置与帮助

- **Edit → Preferences**：语言、主题、字体等，设置自动记住。
- **Help → User Manual**：打开本 GitHub Wiki（需要联网）。

## 6. 常见问题

| 问题 | 处理 |
|------|------|
| 输入目录没有数据 | 选择实际包含 `.ndax` 的目录，不是项目根目录或 `2_xlsx` |
| 型号或容量不正确 | 到 Configuration 补齐/修改 Rules，再重选规格与方法 |
| 输出目录无法创建 | 检查输入目录同级位置的写入权限；输出路径不能手选 |
| 版本冲突 / 校验和未就绪 | 等待扫描，必要时重选输入目录刷新，再选未使用且不低于最低要求的版本；不要删账本 |
| 界面显示不全 | 拉伸/最大化窗口，或在 Preferences 调小字号；小屏可滚动 |

升级前备份报告、配置和账本，并重启应用。[发布说明](https://github.com/Sandman6z/battery-analysis/blob/main/docs/RELEASE_NOTES_v5.1.2.md) · [问题反馈](https://github.com/Sandman6z/battery-analysis/issues)（请附软件版本、错误详情与日志）。
