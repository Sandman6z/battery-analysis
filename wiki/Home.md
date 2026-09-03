# BOEDT Battery Analysis Tool Wiki

欢迎使用 **BOEDT Battery Analysis Tool** 文档 Wiki。

本工具用于分析 NEWARE 电池测试系统导出的 **Excel 数据**，自动生成箱线图、Excel 结果表、Word 报告和 CSV 汇总。

---

## 功能特性

- 电池数据分析与可视化
- 支持多种数据格式导入
- 脉冲识别与匹配
- 批量处理与报告生成
- 自动从文件名解析测试参数（规格、批次、电流等）
- 实时校验与提示
- 多语言支持（中文/英文）
- 自动保存与恢复用户配置

---

## 快速开始

大多数情况下，你只需要 **三个步骤**：

| 步骤 | 操作 | 软件自动完成 |
|------|------|-------------|
| 1 | 选择 Test Profile（Browse 到 XML 测试配置文件） | 自动验证 XML、自动填充输入/输出路径 |
| 2 | 点击绿色 **Run** | 校验 -> 计算 -> 绘图 -> 生成报告，全程自动 |
| 3 | 完成后点击 **"打开报告"** / **"打开路径"** | 一键直达结果 |

详细指南请参阅：
- [[Quick-Start]] - 中文快速操作指南
- [[Quick-Start-EN]] - English Quick Start Guide

---

## 文档导航

| 页面 | 说明 |
|------|------|
| [[Quick-Start]] | 中文快速操作指南（三步上手） |
| [[Quick-Start-EN]] | English Quick Start Guide |

---

## 项目链接

- [GitHub 仓库](https://github.com/Sandman6z/battery-analysis)
- [问题反馈](https://github.com/Sandman6z/battery-analysis/issues)
- [文档站点](https://sandman6z.github.io/battery-analysis/)

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 提示"输入路径没有数据" | 确认 `2_xlsx` 文件夹下有 `.xlsx` 文件（排除以 `~$` 开头的临时文件） |
| 提示输出目录不存在 | 在弹窗中点"是"自动创建，或手动选择已有目录 |
| 版本号不对 | 版本号由数据内容自动决定，不要手动改；确认输入/输出路径正确 |
| 界面显示不全 | 窗口可自由拉伸、最大化；小屏会自动出现滚动条 |

---

*最后更新：2026-09-03*
