# v5.1.3 发布说明

## 版本判断

本次升级为 **5.1.3 补丁版**：主要是内部职责整理、图标打包路径及界面对齐修复，没有新增用户功能，也未有意改变分析算法、容量规则或报告格式。本次 tag 同时包含此前已提交但未打 tag 的 [v5.1.2 操作指南与帮助入口更新](RELEASE_NOTES_v5.1.2.md)。

## 本次更新

- **分析与报告分层**：分析计算代码迁至 `battery_analysis.analysis`，CSV/Excel/Word/图表输出代码迁至 `battery_analysis.reports`；`TestInfo` 改为 `battery_analysis.domain.test_info`，服务容器改为 `battery_analysis.main.services.service_container`。同步业务调用、测试、基准脚本和冻结构建隐式导入。
- **包内图标**：应用图标移至 `src/battery_analysis/resources/icons`，纳入 setuptools 包数据；运行时统一解析源码、wheel 和 PyInstaller 资源路径，构建脚本同步 EXE 图标及资源收集路径。
- **界面对齐**：调整 Report Ver. 和 Tester Location 行的左侧边距，并增加布局回归断言。
- **仓库清理**：移除本地会议记录、独立路线图前端及空壳目录；设计与计划归档至 `docs/specs` 和 `docs/plans`，更新工程结构说明、测试说明与文档站导航。

## 使用与升级

- 用户操作流程不变，[v5.1.2 中英文操作指南](RELEASE_NOTES_v5.1.2.md)仍适用；NDAX 主输入、Step.xml 定档和异常人工确认策略继续沿用。
- 软件版本 `5.1.3` 与报告交付版本独立，不重置报告编号、已有报告或 `SHA256.csv` 账本。升级前备份配置、报告及账本，并重启应用。
- 二次开发需同步内部 Python 导入路径：旧 `utils.processors`、`utils.writers`、`domain.entities.test_info` 和 `main.services.service_container.container` 路径不再保留。不支持将新旧源码目录混合覆盖运行，建议完整替换安装。
- [v5.1.1 Windows 启动修复](RELEASE_NOTES_v5.1.1.md)、[v5.1.0 图表交互](RELEASE_NOTES_v5.1.0.md)与 [v5.0.0 NDAX 迁移要求](RELEASE_NOTES_v5.0.0.md)继续适用。

## 本地验证

2026-10-23 在 Windows / Python 3.14 项目环境执行：

- `uv sync --all-extras --frozen`：通过，动态包元数据由 5.1.2 更新为 **5.1.3**，无需更改依赖锁文件。
- `uv run ruff check src/ tests/ scripts/`：通过。
- `uv run mypy src/`：通过，检查 **176** 个源文件，沿用现有类型检查配置。
- `QT_QPA_PLATFORM=offscreen` 下运行全量 pytest：**1267 passed, 9 skipped**；跳过项不计为通过。

## 发布边界

- 本地未重新执行完整 Windows EXE 构建、冻结程序人工操作验收、真实大批次 NDAX 性能测试或外部 Word/Excel 人工验收。
- 推送 `v5.1.3` tag 会触发现有 GitHub Actions：检查与测试 → EXE 构建 → 冻结程序 `--smoke-test` → GitHub Release 与附件上传。
- 提交、tag 与推送成功不等于远端构建和 Release 已成功，下载前须确认对应工作流结果；本说明不预先宣称新 EXE 已可下载。
