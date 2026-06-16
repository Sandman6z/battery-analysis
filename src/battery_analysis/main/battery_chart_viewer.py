"""
电池数据分析图像显示模块

本模块提供了用于电池数据分析和可视化的主要功能。它能够从CSV文件读取电池数据，
进行数据过滤和处理，生成模拟数据，并创建交互式图表进行数据可视化。

主要功能：
- 从CSV文件加载电池数据
- 支持配置文件读取和自定义配置
- 实现数据过滤算法
- 生成模拟电池数据
- 创建交互式图表，支持数据点悬停、曲线切换等功能

依赖：
- matplotlib: 用于图表绘制
- csv: 用于CSV文件读取
- pathlib: 用于文件路径处理
"""

# 标准库导入
import logging
from pathlib import Path
import os

# 第三方库导入
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
import matplotlib
import matplotlib.pyplot as plt

# 使用QtAgg后端，自动检测可用的Qt绑定（包括PyQt6）
matplotlib.use('QtAgg')

from battery_analysis.utils.report_coordinator import CN_FONT_LIST
# 配置matplotlib支持中文显示
matplotlib.rcParams['font.sans-serif'] = CN_FONT_LIST
matplotlib.rcParams['axes.unicode_minus'] = False

# 开启交互模式
plt.ion()

# 配置日志
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# 混入类
from battery_analysis.main.visualization.data_loader import DataLoaderMixin
from battery_analysis.main.visualization.figure_builder import FigureBuilderMixin
from battery_analysis.main.visualization.interaction_controls import InteractionControlsMixin
from battery_analysis.main.visualization.styling import ChartStylingMixin


class BatteryChartViewer(
    DataLoaderMixin,
    FigureBuilderMixin,
    InteractionControlsMixin,
    ChartStylingMixin,
):
    """
    图表生成和数据可视化类

    负责电池数据的可视化处理，包括配置文件读取、数据加载、过滤和图表生成。
    支持从CSV文件读取实际数据或生成模拟数据，并提供交互式图表界面进行数据分析。

    属性:
        strPltName: 图表标题名称
        listColor: 图表颜色列表
        maxXaxis: X轴最大值
        listPlt: 图表数据列表
        listBatteryNameSplit: 电池名称列表
        intBatteryNum: 电池数量
        intCurrentLevelNum: 电流级别数量
        listAxis: 坐标轴范围
        listXTicks: X轴刻度值
        plot_config: 图表配置对象
    """

    class PlotConfig:
        """
        图表配置类，用于存储可配置的图表参数

        属性:
            axis_default: 默认坐标轴范围 [xmin, xmax, ymin, ymax]
            axis_special: 特殊规则下的坐标轴范围 [xmin, xmax, ymin, ymax]
        """
        def __init__(self):
            self.axis_default = [10, 600, 0, 5]
            self.axis_special = [10, 600, 1, 3]

    def __init__(self, data_path=None, auto_search=True):
        """
        初始化BatteryChartViewer类，设置默认配置并加载用户配置

        Args:
            data_path: 可选，指定要加载数据的目录路径
            auto_search: 是否自动搜索数据文件，默认为True
        """
        self.auto_search = auto_search

        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.project_root = current_dir.parent.parent
        self.path = self.project_root

        self._load_config_file()

        self.plot_config = self.PlotConfig()

        self.listColor = ['#DF7040', '#0675BE', '#EDB120',
                          '#7E2F8E', '#32CD32', '#FF4500', '#000000', '#000000']
        self.maxXaxis = self.plot_config.axis_default[1]
        self.intBatteryNum = 0
        self.loaded_data = False
        self.current_fig = None
        self.last_data_path = None
        self.last_data_timestamp = None

        self.listAxis = [self.plot_config.axis_default[0], self.maxXaxis,
                         self.plot_config.axis_default[2], self.plot_config.axis_default[3]]
        self.listXTicks = list(range(0, self.maxXaxis + 1, 100))

        self.listPlt = []
        self.listBatteryName = []
        self.listBatteryNameSplit = []
        self.strPltPath = None
        self.strInfoImageCsvPath = None

        self._read_configurations()

        if data_path is not None:
            logger.info("初始化时接收到数据路径: %s", data_path)
            self.set_data_path(data_path)
            success = self.load_data()
            if success:
                self.loaded_data = True
                logger.info("初始化数据加载成功")
            else:
                logger.warning("初始化数据加载失败")
                if auto_search:
                    self._search_for_data_files()
        else:
            logger.info("初始化时未提供数据路径，不加载数据")
            if auto_search:
                self._search_for_data_files()

    def get_axis_default(self):
        """获取默认坐标轴范围 [xmin, xmax, ymin, ymax]"""
        return self.plot_config.axis_default

    def set_axis_default(self, xmin, xmax, ymin, ymax):
        """设置默认坐标轴范围"""
        self.plot_config.axis_default = [xmin, xmax, ymin, ymax]
        if (self.listAxis[0] == self.plot_config.axis_default[0]
                and self.listAxis[2] == self.plot_config.axis_default[2]
                and self.listAxis[3] == self.plot_config.axis_default[3]):
            self.listAxis = [xmin, self.maxXaxis, ymin, ymax]

    def get_axis_special(self):
        """获取特殊规则下的坐标轴范围 [xmin, xmax, ymin, ymax]"""
        return self.plot_config.axis_special

    def set_axis_special(self, xmin, xmax, ymin, ymax):
        """设置特殊规则下的坐标轴范围"""
        self.plot_config.axis_special = [xmin, xmax, ymin, ymax]

    def get_plot_config(self):
        """获取整个图表配置对象"""
        return self.plot_config

    def plt_figure(self):
        """创建并显示电池数据图表，包含交互控件以切换数据显示"""
        try:
            logger.info("开始绘制图表")

            import matplotlib
            if matplotlib.get_backend() != 'QtAgg':
                logger.info("当前Matplotlib后端: %s, 切换到QtAgg后端", matplotlib.get_backend())
                matplotlib.use('QtAgg')

            import matplotlib.pyplot as plt

            if self.loaded_data and self.last_data_path and self.strInfoImageCsvPath:
                import datetime
                try:
                    if os.path.exists(self.strInfoImageCsvPath):
                        current_timestamp = os.path.getmtime(self.strInfoImageCsvPath)
                        if self.last_data_timestamp and current_timestamp > self.last_data_timestamp:
                            logger.info("检测到数据更新: 上次加载时间 %s, 当前文件时间 %s",
                                        datetime.datetime.fromtimestamp(self.last_data_timestamp),
                                        datetime.datetime.fromtimestamp(current_timestamp))

                            try:
                                reply = QMessageBox.question(
                                    None,
                                    "数据更新",
                                    "检测到分析结果已更新，是否重新加载最新版的图形？",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.Yes
                                )
                                if reply == QMessageBox.StandardButton.Yes:
                                    logger.info("用户选择重新加载最新数据")
                                    if not self.load_data():
                                        logger.error("重新加载数据失败")
                                    else:
                                        logger.info("重新加载数据成功")
                                else:
                                    logger.info("用户选择保持原有数据显示")
                            except Exception as msg_error:
                                logger.warning("显示更新提示框时出错: %s", msg_error)
                except Exception as check_error:
                    logger.warning("检测数据更新时出错: %s", check_error)

            if self.intBatteryNum <= 0:
                logger.error("错误: 没有有效的电池数据可供显示")
                self._show_error_plot()
                return True

            if not hasattr(self, 'listPlt') or not self.listPlt:
                logger.error("错误: 电池数据结构未初始化或为空")
                self._show_error_plot()
                return True

            if hasattr(self, 'current_fig') and self.current_fig is not None:
                try:
                    plt.close(self.current_fig)
                    self.current_fig = None
                    logger.info("已关闭之前的图表实例")
                except Exception as e:
                    logger.warning("关闭之前的图表实例时出错: %s", e)

            try:
                fig, ax, title_fontdict, axis_fontdict = self._initialize_figure()
                if fig is None or ax is None:
                    raise ValueError("无法初始化图表或坐标轴")
                self.current_fig = fig

                try:
                    self._add_menu_bar(fig)
                except Exception as menu_error:
                    logger.warning("添加菜单栏时出错: %s", menu_error)
            except (OSError, ValueError, TypeError) as init_error:
                logger.error("图表初始化失败: %s", str(init_error))
                self._show_error_plot()
                return True

            try:
                lines_unfiltered, lines_filtered = self._plot_battery_curves(ax)
                valid_data_found = bool(lines_filtered) or bool(lines_unfiltered)

                if valid_data_found:
                    logger.info("成功绘制了 %d 条过滤曲线和 %d 条原始曲线",
                                len(lines_filtered), len(lines_unfiltered))
                    self._adjust_y_axis_range(ax)
            except (OSError, ValueError, TypeError, IndexError) as plot_error:
                logger.error("绘制电池曲线时出错: %s", str(plot_error))
                lines_unfiltered, lines_filtered = [], []
                valid_data_found = False

            if not valid_data_found:
                logger.error("严重错误: 无法绘制任何电池数据曲线")
                self._show_error_plot()
                return True

            try:
                check_filter = self._add_filter_button(
                    fig, ax, lines_unfiltered, lines_filtered, title_fontdict, axis_fontdict)
                self._add_battery_selection_buttons(
                    fig, check_filter, lines_unfiltered, lines_filtered
                )
                self._add_hover_functionality(
                    fig, ax, lines_filtered, lines_unfiltered, check_filter)
                self._add_help_text(fig)
                logger.info("成功添加图表交互控件")
            except (AttributeError, TypeError, ValueError) as ui_error:
                logger.warning("添加交互控件时出错: %s", str(ui_error))

            logger.info("图表创建完成，显示CSV文件中的真实电池测试数据")

            plt.ion()
            plt.show(block=False)

            try:
                if hasattr(fig.canvas.manager, 'window'):
                    window = fig.canvas.manager.window
                    window.setWindowFlags(
                        Qt.WindowType.Window |
                        Qt.WindowType.WindowMinimizeButtonHint |
                        Qt.WindowType.WindowMaximizeButtonHint |
                        Qt.WindowType.WindowCloseButtonHint
                    )
                    window.showNormal()
                    window.show()
                    window.activateWindow()
                    window.raise_()
                    window.setWindowState(Qt.WindowState.WindowActive)

                    screen = window.screen().availableGeometry()
                    window.move(int((screen.width() - window.width()) / 2),
                                int((screen.height() - window.height()) / 2))
                    window.repaint()
                    window.update()
            except (AttributeError, TypeError, RuntimeError) as e:
                logger.warning("无法将窗口置于最前面: %s", str(e))

            plt.pause(0.5)
            fig.canvas.draw()
            fig.canvas.flush_events()
            fig.canvas.draw()
            fig.canvas.flush_events()

            logger.info("图表显示成功")
            return True

        except (OSError, ValueError, TypeError, AttributeError, RuntimeError) as e:
            logger.error("严重错误: 绘制图表时发生未预期的异常: %s", str(e))
            logger.error("错误类型: %s", type(e).__name__)
            import traceback
            traceback.print_exc()
            self._show_error_plot()
            return True


if __name__ == '__main__':
    """
    主程序入口

    创建BatteryChartViewer类实例，自动执行初始化、数据读取和图表显示操作。

    支持命令行参数：
    - 第一个参数：可选，指定数据目录路径
    """
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    try:
        from battery_analysis.ui.styles.style_manager import StyleManager
        style_manager = StyleManager()

        unified_style_path = Path(__file__).parent.parent / "ui" / "styles" / "battery_analyzer.qss"

        logger.info("尝试加载统一样式文件: %s", unified_style_path)

        if unified_style_path.exists():
            with open(unified_style_path, 'r', encoding='utf-8') as f:
                unified_style = f.read()
                app.setStyleSheet(unified_style)
                app.processEvents()
                app.style().unpolish(app)
                app.style().polish(app)
                app.update()
                logger.info("已应用统一电池分析器样式")
        else:
            logger.warning("未找到统一样式文件: %s", unified_style_path)
            try:
                style_manager = StyleManager()
                style_manager.apply_global_style(app, "modern")
                logger.info("已应用备用全局主题样式")
            except Exception as e2:
                logger.error("备用样式应用失败: %s", e2)
    except Exception as e:
        logger.error("应用样式失败: %s", e)
        try:
            style_manager = StyleManager()
            style_manager.apply_global_style(app, "modern")
            logger.info("最终备用样式已应用")
        except Exception as e3:
            logger.error("最终备用样式应用也失败: %s", e3)

    data_path = None
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
        logger.info("从命令行接收数据路径: %s", data_path)

    figure = BatteryChartViewer(data_path=data_path)
    logger.info("尝试显示图表（无论是否有数据）")
    figure.plt_figure()

    logger.info("启动Qt事件循环")
    sys.exit(app.exec())
