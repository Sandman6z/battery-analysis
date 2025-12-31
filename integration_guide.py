# -*- coding: utf-8 -*-
"""
集成指南

说明如何将新的现代化UI组件集成到现有项目中
"""

# 集成步骤

"""
一、文件结构
新的UI组件位于:
- src/battery_analysis/ui/modern_theme.py        # 现代化主题配置
- src/battery_analysis/ui/modern_chart_widget.py # 嵌入式图表控件
- src/battery_analysis/ui/modern_battery_viewer.py # 现代化主窗口
- demo_modern_ui.py                             # 演示脚本

二、集成方式

方式1: 替换现有Viewer
====================

在 visualizer_controller.py 中替换:

# 原有的创建方式
from battery_analysis.main import battery_chart_viewer
viewer = battery_chart_viewer.BatteryChartViewer(data_path=None, auto_search=False)

# 新的现代化方式
from battery_analysis.ui.modern_battery_viewer import create_modern_viewer
viewer = create_modern_viewer(data_path=data_path)

方式2: 作为选项提供
==================

在主窗口中添加切换选项:

def create_viewer(self, use_modern_ui=False):
    if use_modern_ui:
        from battery_analysis.ui.modern_battery_viewer import create_modern_viewer
        return create_modern_viewer(data_path=self.data_path)
    else:
        from battery_analysis.main import battery_chart_viewer
        return battery_chart_viewer.BatteryChartViewer(data_path=self.data_path)

方式3: 完全替换现有实现
======================

修改 main_window.py 中的 run_visualizer 方法:

def run_visualizer(self, xml_path=None):
    # ...
    try:
        # 使用现代化查看器
        from battery_analysis.ui.modern_battery_viewer import ModernBatteryViewer
        self.current_visualizer = ModernBatteryViewer(data_path=data_path)
        self.current_visualizer.show()
        
    except Exception as e:
        # 回退到原有实现
        from battery_analysis.main import battery_chart_viewer
        self.current_visualizer = battery_chart_viewer.BatteryChartViewer(data_path=data_path, auto_search=False)
        self.current_visualizer.plt_figure()

三、配置选项

可以在配置文件中添加:
[UI]
modern_interface = true  # 启用现代化界面
theme_style = modern     # 主题样式: modern, dark, light
chart_animation = true   # 启用图表动画
show_toolbar = true      # 显示工具栏
show_menubar = true      # 显示菜单栏

四、依赖要求

新的UI组件需要以下依赖:
- PyQt6 (已有)
- matplotlib (已有)
- numpy (已有)

不需要额外的依赖包。

五、兼容性

新的UI组件设计为向后兼容:
- 保持与原有 BatteryChartViewer 的数据接口兼容
- 保持原有的数据处理逻辑不变
- 可以渐进式集成，不需要一次性全部替换

六、性能考虑

现代化UI的性能优化:
- 延迟加载: 图表控件按需创建
- 内存管理: 适当释放不需要的matplotlib对象
- 渲染优化: 使用硬件加速的Qt后端
- 缓存机制: 缓存常用的图表配置

七、扩展性

新UI框架支持:
- 插件式图表类型
- 自定义主题
- 多语言支持
- 可配置的布局
- 扩展的数据分析功能

八、测试

运行测试:
python demo_modern_ui.py

这将启动演示程序，展示所有新的UI功能。

九、故障排除

常见问题及解决方案:

1. 导入错误
   - 确保所有新文件在正确的路径
   - 检查Python路径设置

2. 主题不生效
   - 确保调用了 apply_modern_theme()
   - 检查matplotlib后端设置

3. 图表不显示
   - 检查Qt应用程序是否正确初始化
   - 确认matplotlib后端为QtAgg

4. 性能问题
   - 减少同时显示的数据量
   - 调整图表刷新频率
"""

# 代码示例

"""
完整集成示例:

# 在 main_window.py 中

def __init__(self, parent=None):
    super().__init__(parent)
    # ...
    self.use_modern_ui = True  # 可配置选项
    
def run_visualizer(self, xml_path=None):
    try:
        if self.use_modern_ui:
            self._run_modern_visualizer(xml_path)
        else:
            self._run_classic_visualizer(xml_path)
    except Exception as e:
        logging.error(f"可视化器运行失败: {e}")
        # 回退到经典模式
        self._run_classic_visualizer(xml_path)

def _run_modern_visualizer(self, xml_path):
    from battery_analysis.ui.modern_battery_viewer import ModernBatteryViewer
    
    # 创建现代化查看器
    self.modern_viewer = ModernBatteryViewer(data_path=xml_path)
    
    # 连接信号
    self.modern_viewer.data_loaded.connect(self._on_modern_data_loaded)
    
    # 显示窗口
    self.modern_viewer.show()
    
    self.statusBar().showMessage("现代化界面已启动")

def _run_classic_visualizer(self, xml_path):
    from battery_analysis.main import battery_chart_viewer
    
    # 使用原有查看器
    self.classic_viewer = battery_chart_viewer.BatteryChartViewer(data_path=xml_path, auto_search=False)
    
    if self.classic_viewer.load_data():
        self.classic_viewer.plt_figure()
        self.statusBar().showMessage("经典界面已启动")
"""

print(__doc__)