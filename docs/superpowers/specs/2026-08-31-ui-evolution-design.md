# UI 演进设计：主题系统 + 布局重构 + i18n 架构

> 上游：`docs/superpowers/specs/2026-08-18-tech-stack-modernization-roadmap-design.md`
> 上游：`docs/superpowers/specs/2026-05-15-borderless-ui-design.md`（现有暖米色主题）
> 状态：**待批准**

## 目标

解决三个 UI 层面的系统性问题：

1. **主题系统割裂**：`StyleManager` 和 `ThemeManager` 各管各的，切换非 Dark 主题丢失所有 QSS 样式，暗色主题是粗糙的内联回退
2. **布局浪费空间**：Designer 生成的 3 列布局右侧 Run 按钮列空间浪费，信息层级不清晰，图表区默认隐藏
3. **i18n 架构不统一**：两套翻译系统并存，语言切换后 UI 文本不刷新

## 范围决策

| 决策点 | 结论 |
|---|---|
| UI 构建方式 | 主窗口从 Qt Designer `.ui` 转为**纯代码构建**（`QFormLayout`/`QGridLayout`/`QVBoxLayout`） |
| 布局策略 | **单列扁平化**，不分 Tab，所有内容垂直排列 |
| Run 按钮位置 | 从右侧移至**顶部操作栏**，释放右侧空间 |
| 图表区 | **默认可见**（空状态显示引导文字），不再隐藏 |
| 主题 | 设计令牌（Token）化，支持**亮/暗两套主题**切换 |
| i18n | 统一到自定义 `_()` 系统，实现 `refresh_texts()` 刷新机制；**不新增语言** |
| 对话框 | 简单对话框可保留 Designer，主窗口必须转代码 |

## A1 主题系统 — 风险 S

### 1.1 设计令牌（Design Tokens）

将当前 873 行 QSS 中的硬编码颜色值抽取为结构化令牌集：

**颜色令牌分类**：

| 分类 | 令牌示例 | 亮色值 | 暗色值 |
|---|---|---|---|
| 背景 | `bg_primary` | `#f5f0e8` | `#1e1e1e` |
| 背景 | `bg_card` | `#faf7f2` | `#2a2a2a` |
| 背景 | `bg_input` | `#ede9e3` | `#333333` |
| 文字 | `text_primary` | `#3d3229` | `#e0e0e0` |
| 文字 | `text_secondary` | `#8a7a6a` | `#a0a0a0` |
| 强调 | `accent_green` | `#27ae60` | `#2ecc71` |
| 强调 | `accent_blue` | `#3498db` | `#5dade2` |
| 强调 | `accent_red` | `#e74c3c` | `#ec7063` |
| 边框 | `border_default` | `#d5c8b6` | `#3a3a3a` |
| 边框 | `border_focus` | `#27ae60` | `#2ecc71` |
| 状态 | `hover_input` | `#e5e0d8` | `#3d3d3d` |
| 状态 | `focus_input` | `#ffffff` | `#404040` |

**实现**：Python `dict` 定义令牌集，QSS 模板用 `{token_name}` 占位符，加载时 `str.format()` 渲染为实际值。

### 1.2 ThemeEngine

合并 `StyleManager` + `ThemeManager` 为统一的 `ThemeEngine`：

- 持有当前主题令牌集 + 渲染后的 QSS 字符串
- `set_theme("light" | "dark")` 接口
- 切换流程：更新令牌 → 重新渲染 QSS → `app.setStyleSheet(new_qss)`
- 所有对话框/弹窗从 `ThemeEngine` 获取样式，不再硬编码内联

### 1.3 补全缺失样式

- `QToolTip` 样式（当前未定义）
- `QScrollBar:horizontal` 样式（当前只有垂直）
- 移除 Run 按钮 Designer 内联样式冲突（`ui_main_window.py` 中的 `setStyleSheet` 覆盖 QSS）
- 统一对话框样式（移除硬编码内联）

### 1.4 验收

- 亮/暗主题切换即时生效，无残留样式
- 所有控件在两套主题下视觉一致
- 无内联样式与 QSS 冲突

## A2 主窗口代码化 + 布局重构 — 风险 M

### 2.1 布局结构

```
┌──────────────────────────────────────────────────┐
│  [版本 v2.x] [报告人: ___]          [运行分析 ▶]  │ ← 顶部操作栏
├──────────────────────────────────────────────────┤
│  测试配置                                          │
│  ├─ 测试地点 / 测试人员 / 测试类型                   │
│  └─ 输入路径 / 输出路径                              │
├──────────────────────────────────────────────────┤
│  电池参数                                          │
│  ├─ 电池型号 / 结构方式 / 规格 / 制造商              │
│  └─ 批次日期 / 样品数量 / 温度 / 容量                │
├──────────────────────────────────────────────────┤
│  设备信息                                          │
│  └─ 12 行 × 3 列 信息表格                           │
├──────────────────────────────────────────────────┤
│  图表区域（默认可见，空状态显示引导文字）                │
│  └─ 控制面板（左）+ 图表容器（右）                    │
├──────────────────────────────────────────────────┤
│  [进度条 ████████░░░░]                             │ ← 底部状态栏
└──────────────────────────────────────────────────┘
```

### 2.2 现有布局映射

| 现有组件 | 新位置 | 变化 |
|---|---|---|
| `frame_RunButton`（右侧 Run 按钮列） | 顶部操作栏 | 按钮+版本+报告人移至顶部，释放右侧空间 |
| `groupBox_TestConfig` | "测试配置" 区域 | 扁平化：用 `QLabel` 标题 + 底部绿色装饰线替代 QGroupBox 边框（延续 borderless-ui 风格） |
| `groupBox_Path` | "测试配置" 区域底部 | 与测试配置合并 |
| `groupBox_BatteryConfig` | "电池参数" 区域 | 独立分组 |
| `groupBox_TestInformation` | "设备信息" 区域 | 信息表格 |
| `chart_area_widget`（默认隐藏） | "图表区域" | **默认可见**，空状态显示居中引导文字"运行分析后此处显示图表" |
| 进度条 | 底部状态栏 | 始终可见 |

### 2.3 布局管理器选择

| 区域 | 管理器 | 理由 |
|---|---|---|
| 整体页面 | `QVBoxLayout` | 垂直堆叠各区域 |
| 顶部操作栏 | `QHBoxLayout` | 版本+报告人左，Run 按钮右 |
| 测试配置区 | `QFormLayout` | 标签+输入框自动对齐 |
| 电池参数区 | `QGridLayout` | 2 行 × 4 列网格布局 |
| 设备信息区 | `QTableWidget` | 保持现有表格 |
| 图表区 | `QHBoxLayout` | 控制面板左，图表容器右 |
| 底部状态栏 | `QHBoxLayout` | 进度条横贯 |

### 2.4 Main 类改造

- 移除 `Ui_MainWindow` 混入，`Main(QMainWindow)` 独立
- 删除 `ui_main_window.py`（Designer 生成代码）
- 删除 `ui_battery_analysis.ui`（Designer 源文件）
- `setupUi()` 改为 `_build_ui()` 纯代码构建
- 所有文本用 `_()` 包裹（为 A3 做准备）

### 2.5 验收

- 主窗口与现有功能完全等价
- 所有控件可访问、可操作
- 图表区默认可见
- Run 按钮在顶部始终可见
- 无 Designer 依赖

## A3 i18n 架构修复 — 风险 S

### 3.1 统一到 `_()` 系统

- 移除对 `QCoreApplication.translate()` / `retranslateUi()` 的依赖（A2 转代码后自然消失）
- 所有 UI 文本统一用 `_()` 函数

### 3.2 refresh_texts() 回调机制

```python
class LanguageManager:
    def __init__(self):
        self._listeners: list[Callable] = []

    def register(self, callback: Callable):
        self._listeners.append(callback)

    def set_locale(self, locale: str):
        # ... 加载翻译文件 ...
        for cb in self._listeners:
            cb()
```

每个 UI 组件实现 `refresh_texts()`：

```python
class Main(QMainWindow):
    def __init__(self):
        language_manager.register(self.refresh_texts)

    def refresh_texts(self):
        self.setWindowTitle(_("电池分析工具"))
        self.btn_run.setText(_("运行分析"))
        self.group_config.setTitle(_("测试配置"))
        # ... 所有可翻译文本
```

### 3.3 对话框适配

所有对话框（Preferences、DataErrorRecovery 等）也需要：
- 文本用 `_()` 包裹
- 注册 `refresh_texts()` 回调

### 3.4 验收

- 切换语言后所有 UI 文本即时刷新（不只是状态栏）
- 无 `QCoreApplication.translate()` 调用残留
- 无 `retranslateUi()` 调用残留
- 现有 en/zh_CN 翻译文件正常使用

## 分阶段实施

| 阶段 | 分支 | 关键交付 | 前置依赖 |
|---|---|---|---|
| A1 主题系统 | `feat/ui-theme-engine` | ThemeEngine、亮/暗令牌、QSS 模板、补全样式 | 无 |
| A2 主窗口代码化 | `feat/ui-main-window-code` | Main 类重写、布局重构、Designer 文件删除 | A1 |
| A3 i18n 架构 | `feat/ui-i18n-refresh` | refresh_texts()、所有组件适配 | A2 |

**节奏**：每阶段先补回归测试 → 本地 pytest 全绿 + pylint 通过 → 提交到分支 → PR → CI → 用户手动合并。

## 范围边界（明确不做）

- ❌ 新增语言翻译文件（只修架构）
- ❌ 对话框转代码（保留 Designer，除非有样式冲突）
- ❌ 工具栏实现（QSS 中有样式但实际未创建，本次不新增功能）
- ❌ 打包/CI 改动
- ❌ pyqtgraph/QtCharts 迁移
