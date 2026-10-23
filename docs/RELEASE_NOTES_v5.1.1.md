# v5.1.1 发布说明

## 升级建议

请使用 **v5.1.1** 替代存在启动问题的 v5.1.0 云端 EXE。

- [正式 Release](https://github.com/Sandman6z/battery-analysis/releases/tag/v5.1.1)
- [下载 Windows x64 EXE](https://github.com/Sandman6z/battery-analysis/releases/download/v5.1.1/battery-analyzer_5.1.1_x64.exe)

本次为 Windows 打包修复，不改变 NDAX 分析、容量计算、报告交付编号或已有账本；[v5.1.0 的图表交互说明](RELEASE_NOTES_v5.1.0.md)及 [v5.0.0 的迁移要求](RELEASE_NOTES_v5.0.0.md)继续适用。

## 原因与修复

1. **Python DLL 加载失败**：旧云端构建日志确认对 `python314.dll` 先执行 `strip`、再执行 UPX 压缩；本机能复现正式附件的加载错误。现已移除 `--strip`，固定使用 `--noupx`，不再随构建机器上的工具改变 DLL 处理方式。未分别进行单变量实验，不将 strip 或 UPX 中任一个认定为唯一触发因素。
2. **NumPy DLL 漏收**：解决 Python DLL 加载后，冻结程序启动检查发现 NumPy 原生扩展缺少一个重命名的 MSVC DLL。现已完整携带 `numpy.libs`，补齐依赖扫描遗漏。
3. **CI 缺少冻结程序启动验证**：原流程只验证源码测试、EXE 生成与上传。现于发布前实际启动 EXE，只有主窗口延迟初始化完成后，`--smoke-test` 才正常退出；异常、初始化未完成或超过 90 秒均阻断发布。失败产物保留供诊断，不代表允许发布。

## 验证结果

- 修复后的自动回归 **1260 项通过**，Ruff 检查通过，Mypy 检查 **177 个源文件通过**。
- [正式 tag 发布流水线](https://github.com/Sandman6z/battery-analysis/actions/runs/39911397167)的测试、构建、冻结程序启动检查与附件发布均成功。
- 从正式 Release 下载附件，SHA256 与 GitHub 提供的摘要一致：

  ```text
  ac602aa55f57e22c2ddda9d09b19c6e33f9511f0c4d5433335d947b6e8110f7d
  ```

- 正式附件在本机真实 Windows 窗口环境连续三次完成初始化并正常退出，耗时 **5.18 / 4.71 / 4.48 秒**；这些数字为该机器的观察值，不是性能承诺。
- 不带测试参数启动时显示 `Battery Analyzer v5.1.1` 主窗口，正常关闭、退出码为 0；日志确认延迟初始化完成，ERROR／CRITICAL 均为 0。

## 本地与云端共用的检查入口

```bash
uv sync --all-extras --frozen
uv run python scripts/build.py Release
```

然后运行构建所得 EXE，例如在 PowerShell 中：

```powershell
& .\build\Release\battery-analyzer_5.1.1_x64.exe --smoke-test
```

`--smoke-test` 是启动验收入口，初始化完成后自动退出，不是正常使用模式。CI 使用外部超时及退出码判定结果；手动运行时也应确认进程确实结束，而非仅确认文件或进程存在。正常使用直接打开 EXE，不加该参数。

## 验证边界

启动、初始化和关闭通过不等于所有业务功能均完成冻结程序验收。本次未对正式 EXE 做完整数据分析、报告导出、不同 Windows 版本、高 DPI、杀毒软件环境或大数据性能验收。未来原生依赖或构建环境变化仍可能引入新问题，发布前启动检查必须保留。
