# Plan: 修复 matplotlib 字体链以支持 emoji

## Context

`application_initializer.py:205` 报 warning:
```
Glyph 128269 (\N{LEFT-POINTING MAGNIFYING GLASS}) missing from font(s) SimHei.
```

原因是 matplotlib 字体链中没有包含支持 emoji 的字体。目前 Qt 界面（通过 `font.setFamilies(["Segoe UI", "Segoe UI Emoji", ...])`）已有 emoji 支持，但 matplotlib 渲染路径没有。

## 方案

在 matplotlib 的 `font.sans-serif` 字体列表中添加各平台的 emoji 字体：

- `Segoe UI Emoji` — Windows
- `Apple Color Emoji` — macOS
- `Noto Color Emoji` — Linux

放在中文字体之后、DejaVu Sans 之前。matplotlib 3.4+ 的 `font.fallback` 机制会自动在缺失字形时尝试后续字体。

## 修改文件（5 处）

所有文件都使用相同的 font.sans-serif 配置，统一添加 emoji 字体：

1. `src/battery_analysis/utils/plot_utils.py:12-14`
   - 模块级配置，最早加载

2. `src/battery_analysis/main/battery_chart_viewer.py:36-37`
   - 模块级配置

3. `src/battery_analysis/utils/file_writer.py:20`
   - 模块级配置

4. `src/battery_analysis/main/visualization/figure_builder.py:185`
   - `_cleanup_matplotlib_state()` 中的重置

5. `src/battery_analysis/main/controllers/visualizer_controller.py:353`
   - `_reconfigure_matplotlib()` 中的重置

### 变动内容

将每处：
```python
['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial', 'Times New Roman']
```

改为：
```python
['SimHei', 'Microsoft YaHei', 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', 'Arial', 'Times New Roman']
```

## 验证

1. 启动应用，检查原 warning 是否消失
2. 检查 UI 中带 emoji 的按钮（🔍📊📁❌）是否正常显示
3. 使用 `python -W error::UserWarning main.py` 确认没有任何 Glyph 相关 warning
