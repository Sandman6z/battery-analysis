## 变更摘要

将当前本地修改整理为 v5.1.0 minor 更新，继续使用 Matplotlib，不新增依赖或切换绘图库。

### Viewer 导航与交互
- 新增独立/嵌入窗口共用导航控制器：绘图区左拖双轴平移、横纵轴刻度区左拖单轴平移，滚轮按所在区域锚定缩放，右键点击复位。
- 自定义操作接入 Home/Back/Forward，避免重复历史；工具栏 Pan/Zoom 与自定义手势互斥；导航时暂停普通/KDTree 悬停与延迟回调。
- 自适应刻度、初始范围修复、释放/失焦/关闭/重复安装清理；嵌入图补工具栏、移除重复画布并修正接口说明。
- 补充范围行为测试及菜单/工具栏 16 项真实 Qt 离屏验收，实际检查 PNG/SVG/PDF、中文路径、取消及失败处理。

### 同步纳入的本地提交
- `ac701d8`：样本数量、Datasheet/Calculation Nominal Capacity、Required Useable Capacity 只读展示；来源提示与 Tab 顺序同步。

### 版本与文档
- 5.0.3 → 5.1.0；唯一版本源仍为 `_version.py`。
- 更新 CHANGELOG、README、中英文操作指南、Changelog 指南、文档首页及 MkDocs 导航，新增 v5.1.0 发布说明。
- 修正容量字段可手工编辑的过期描述；报告交付编号及账本不重置。

## 验证
- [x] `uv sync --all-extras --frozen`
- [x] `ruff check src/ tests/ scripts/`
- [x] `mypy src/`：177 源文件无错误
- [x] 全量 pytest：1256 passed（Qt offscreen，排除 tests/manual）
- [x] 源码、安装包元数据、界面封装及构建配置均为 5.1.0
- [x] 本次文档相对链接目标存在，diff 空白检查通过

## 边界
- Windows 原生文件对话框、高 DPI 桌面外观、冻结 EXE 交互与大数据性能未人工验收；PR CI 测试/构建结果以运行记录为准。
- 本地 MCP 配置与会议文件未纳入 PR。
- 本次不创建 tag 或 GitHub Release。
