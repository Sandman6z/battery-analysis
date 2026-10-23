# BOEDT Battery Analysis Tool · 用户手册

适用于 **v5.1.2**。直接分析 NEWARE 原始 **NDAX**，生成图表、Excel、Word、CSV 和 JSON。

**[中文操作指南](https://github.com/Sandman6z/battery-analysis/wiki/Quick-Start)** · **[English User Guide](https://github.com/Sandman6z/battery-analysis/wiki/Quick-Start-EN)**

## 三步开始

| 步骤 | 操作 | 注意 |
|------|------|------|
| 1. 选数据 | **Input Path → Open** 选择 `1_ndax`；也可从 **Test Profile → Open** 选择 XML 带出路径 | XML 选填；主分析不读取 `2_xlsx` |
| 2. 核对并运行 | 等待扫描，核对自动带出的电池/测试信息与报告版本，点击 **Run** | 输出固定为同级 `3_analysis results`；异常提示需先阅读 |
| 3. 查结果 | 完成后点 **Open Report / Open Path** | 生成成功不等于合格；同时检查判定、有效样本数与异常 |

## 与旧流程的关键区别

- **不必先转 Excel**：脉冲档位以 NDAX 内嵌 `Step.xml` 为准，外部 XML 仅做校验。
- **温度来自 NDAX**：读取内嵌 `TestInfo.xml` 的 `StepName`，不再依据外部 XML 文件名；同批温度/档位必须一致。
- **只读派生字段**：样本数来自输入文件；三项容量通过 **Tools → Configuration → Rules** 维护，修改后重选规格/方法刷新。
- **报告版本独立于软件版本**：可手填未使用且不低于最低要求的版本，不能覆盖旧报告；不要删除 `SHA256.csv` 绕过检查。
- **缺失分级处理**：普通缺失保留 `No data` 并汇总；必需判定格缺失/单文件分析失败需两次确认；损坏配方不能放行。

## 按任务查找

| 你要做什么 | 入口 |
|------------|------|
| 首次运行、切换项目、核对输入 | [操作指南 §1–3](https://github.com/Sandman6z/battery-analysis/wiki/Quick-Start#1-准备数据并选择项目) |
| 新增型号/厂家、修改容量规则 | **Tools → Configuration**；[字段来源与配置](https://github.com/Sandman6z/battery-analysis/wiki/Quick-Start#2-核对自动填入的信息) |
| 理解异常、查报告与日志 | [运行与结果追溯](https://github.com/Sandman6z/battery-analysis/wiki/Quick-Start#3-确认报告版本点击-run) |
| 看交互曲线 | **Tools → BatteryChartViewer → File → Open**，选含 `Info_Image.csv` 的目录 |
| 只导出原始 Excel | **Tools → NDAX Converter**，输出同级 `2_xlsx`，不是主分析前置步骤 |
| 调整语言/主题/字号 | **Edit → Preferences** |

## 项目与详细说明

- [GitHub 仓库](https://github.com/Sandman6z/battery-analysis) · [下载发布版本](https://github.com/Sandman6z/battery-analysis/releases) · [问题反馈](https://github.com/Sandman6z/battery-analysis/issues)
- [中文详细说明](https://github.com/Sandman6z/battery-analysis/blob/main/docs/QUICK_START.md) · [English detailed guide](https://github.com/Sandman6z/battery-analysis/blob/main/docs/QUICK_START_EN.md)
- [版本与迁移说明](https://github.com/Sandman6z/battery-analysis/blob/main/CHANGELOG.md) · [容量与异常判定边界](https://github.com/Sandman6z/battery-analysis/blob/main/docs/pdf_recheck_and_anomaly_policy.md)

升级前备份报告、配置及账本，并重启应用。具体步骤、错误处理和图表手势请查看上方中英文操作指南。
