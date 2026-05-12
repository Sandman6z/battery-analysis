# 启动速度优化设计

## 问题
电池分析应用（PyQt6）启动时间长，用户在点击后需要等待数秒才能看到窗口，期间无任何反馈。

## 方案

### 1. 闪屏 (Splash Screen)
- 在 `main()` 中最早期创建 `QSplashScreen`，显示应用 Logo + "Loading..." 文字
- 使用 `QApplication.processEvents()` 确保闪屏在大量 import 期间保持刷新
- 主窗口显示完成后，用 `splash.finish(window)` 关闭闪屏

### 2. 窗口优先 + 延迟初始化
- `Main.__init__()` 中仅执行必要的核心初始化，省略非关键 UI 设置
- 使用 `QTimer.singleShot(0, self._lazy_init)` 在主事件循环启动后延迟执行
- 延迟内容：
  - `setup_accessibility()` — 无障碍属性
  - `setup_tooltips()` — 工具提示
  - `init_combobox()` — 下拉框填充（节省几百毫秒）
  - `init_table()` — 表格填充
  - 菜单快捷键设置

### 3. 懒导入优化
- `main_window.py` 顶部的模块级 import 移入函数内部
- 尤其针对 `ui_main_window`（92KB）和 `resources_rc`

### 风险
- 延迟初始化期间用户可能操作未就绪的控件 → 添加 guard 检查
- 闪屏不会显著缩短实际加载时间，但能改善感知体验

## 验收标准
- 从双击到看到窗口主框架 < 2 秒
- 闪屏 < 1 秒内显示
- 所有功能完整可用
