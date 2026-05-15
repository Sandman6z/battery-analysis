# Borderless UI 无边框样式设计

## 概述

移除电池分析应用中所有 UI 组件的可见边框，改用背景色、圆角、间距和分隔线来区分布局层次。同时将底色改为护眼的暖米色系。

## 色彩方案

| 角色 | 颜色 | 用途 |
|---|---|---|
| 主背景 | `#f5f0e8` | QMainWindow / QWidget 底色 |
| 卡片/容器 | `#faf7f2` | 替代原白色卡片区域 |
| 输入框背景 | `#ede9e3` | QLineEdit / QComboBox / QSpinBox |
| 输入框悬停 | `#e5e0d8` | hover 状态 |
| 输入框聚焦 | `#ffffff` | focus 状态 + 2px #27ae60 边框 |
| 分隔线 | `#e0d8cc` | divider |
| 标题装饰线 | `#27ae60` | 绿色标题底线 |
| 文字主色 | `#3d3229` | 正文 |
| 文字辅助 | `#8a7a6a` | 标签/说明 |

## 改动范围（全部组件）

### QFrame
- 移除 `border` 和 `frameShadow`
- 背景设为透明

### QGroupBox
- 移除 `border`
- title 改为底部 2px `#27ae60` 装饰线（通过 `QGroupBox::title` 伪元素实现）
- 背景透明

### QLineEdit
- `border: none`
- `background: #ede9e3; border-radius: 8px`
- hover: `background: #e5e0d8`
- focus: `background: #ffffff; border: 2px solid #27ae60`

### QComboBox
- `border: none`
- `background: #ede9e3; border-radius: 8px`
- hover/focus 同 QLineEdit

### QSpinBox
- 同理，无边框 + 圆角背景

### QPushButton
- 保持现有色彩（绿色运行按钮等），但统一圆角到 8px

### QTableWidget
- 移除外部 `border`，保留内部 gridline

### 内联样式清理
- `ui_main_window.py` 中所有绿色 `#4CAF50` 边框的 setStyleSheet 移除
- 由 QSS 统一管理

## 设计原则

- **无边框**：所有可见 border 移除
- **层次靠背景色**：卡片 = `#faf7f2`，输入区域 = `#ede9e3`
- **圆角统一**：8px
- **分隔线轻量**：功能区之间用 1px `#e0d8cc` 分隔线
- **标题装饰**：GroupBox 标题改为底部 2px 绿色线

## 视觉结构

```
背景 (#f5f0e8)
  └─ 暖白卡片 (background: #faf7f2, border-radius: 10px)
       ├─ 标题栏 (底部 2px #27ae60 装饰线)
       ├─ 输入行 (背景 #ede9e3, 8px 圆角)
       ├─ 分隔线 (#e0d8cc)
       └─ 输入行
```

## 文件修改

1. `src/battery_analysis/ui/styles/battery_analyzer.qss` — 主要 QSS 重写
2. `src/battery_analysis/ui/ui_main_window.py` — 移除内联 setStyleSheet
3. `src/battery_analysis/ui/styles/style_manager.py` — 主题变量更新
4. `src/battery_analysis/main/ui_components/theme_manager.py` — 深色主题备用样式适配
5. `src/battery_analysis/main/ui_components/window_setup.py` — 背景色同步

## 验证

- 启动应用检查所有组件显示正常
- 切换主题（深色模式）检查兼容性
- 验证输入框 focus/hover 状态样式
