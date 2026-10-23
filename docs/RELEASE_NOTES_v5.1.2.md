# v5.1.2 发布说明

## 本次更新

本版更新操作文档与帮助入口，不改变 NDAX 分析算法、容量规则、报告交付编号或已有 `SHA256.csv` 账本。

- **GitHub Wiki**：重写首页及中英文操作页，按「选数据 → 核对信息 → Run → 查看结果」组织，补齐字段来源、配置位置、版本限制、异常处理、结果追溯及可选工具。
- **操作逻辑说明**：明确 NDAX 为主分析输入、外部 XML 仅校验、输出固定为同级 `3_analysis results`；容量在 Configuration → Rules 中维护，修改后重选规格/方法刷新。
- **Help → User Manual**：统一打开 [GitHub Wiki](https://github.com/Sandman6z/battery-analysis/wiki)，不再查找本地 PDF 或跳转到旧文档站操作页。浏览器启动失败时显示警告及网址，便于手动访问。
- **中英文详细指南**：补充 Profile 档位不一致时的确认逻辑，删除手选输出目录的过时提示。

[中文操作指南](https://github.com/Sandman6z/battery-analysis/wiki/Quick-Start) · [English User Guide](https://github.com/Sandman6z/battery-analysis/wiki/Quick-Start-EN)

## 使用与升级

- Wiki 已在线更新；现有软件也可直接用浏览器查阅。
- 新的 Help 入口需使用包含本次修改的构建；仅更新 Wiki 不会改变已安装 EXE。
- 软件版本 `5.1.2` 与报告版本独立，不重置报告编号或成功次数。升级前备份配置、报告和账本，并重启应用。
- [v5.1.1 的 Windows 启动修复](RELEASE_NOTES_v5.1.1.md)、[v5.1.0 的图表操作](RELEASE_NOTES_v5.1.0.md)和 [v5.0.0 的 NDAX 迁移要求](RELEASE_NOTES_v5.0.0.md)继续适用。

## 验证与发布边界

- 帮助管理器、对话框管理器及中英文界面相关测试 **27 项通过**，覆盖 Wiki 地址、浏览器返回失败、异常提示和旧入口转发。
- 加上单一版本源、界面版本封装与动态版本配置测试，本轮相关测试共 **32 项通过**。
- 已检查 Wiki 页面目标及章节链接，操作指南已在线发布；v5.1.2 版本标注随本次主仓库提交更新，待同步到线上 Wiki。
- 未执行全量回归、Windows EXE 重新构建、冻结程序启动/业务验收或 GitHub Release 发布；本说明不代表新 EXE 已可下载。
