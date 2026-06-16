"""
图形构建模块

提供Matplotlib图表初始化、曲线绘制、错误图表显示和坐标轴调整方法
"""

import logging
import traceback
import datetime

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from battery_analysis.main.visualization.styling import MODERN_BUTTON_STYLE
from battery_analysis.utils.report_coordinator import CN_FONT_LIST

logger = logging.getLogger(__name__)


class FigureBuilderMixin:
    """图形构建混入类，提供图表构建和绘制方法"""

    def _initialize_figure(self):
        """初始化图表设置和布局"""
        title_fontdict = {'fontsize': 15, 'fontweight': 'bold'}
        axis_fontdict = {'fontsize': 15}

        fig = plt.figure(figsize=(15, 6))
        try:
            if hasattr(fig.canvas.manager, 'window'):
                fig.canvas.manager.window.setWindowTitle(
                    f"Filtered {self.strPltName}")
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.warning("无法设置图表窗口标题: %s", str(e))

        gs = fig.add_gridspec(1, 40)
        ax = fig.add_subplot(gs[:, 5:])

        ax.axis(self.listAxis)
        x_ticks = self.listXTicks
        ax.set_xticks(x_ticks)

        y_major_locator = MultipleLocator(0.2)
        ax.yaxis.set_major_locator(y_major_locator)

        ax.set_title(f"Filtered {self.strPltName}", fontdict=title_fontdict)
        ax.set_xlabel("Charge [mAh]", fontdict=axis_fontdict)
        ax.set_ylabel(
            "Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)

        ax.grid(linestyle="--", alpha=0.3)

        return fig, ax, title_fontdict, axis_fontdict

    def _plot_battery_curves(self, ax):
        """绘制所有电池的原始和过滤后的曲线"""
        lines_unfiltered = []
        lines_filtered = []

        for b in range(self.intBatteryNum):
            for c in range(self.intCurrentLevelNum):
                try:
                    ul, = ax.plot(
                        self.listPlt[c][0][b],
                        self.listPlt[c][1][b],
                        color=self.listColor[c] if c < len(
                            self.listColor) else f'C{c}',
                        label=[f'{self.listBatteryNameSplit[b]}',
                               'Unfiltered'],
                        visible=False,
                        linewidth=0.5
                    )
                    lines_unfiltered.append(ul)

                    fl, = ax.plot(
                        self.listPlt[c][2][b],
                        self.listPlt[c][3][b],
                        color=self.listColor[c] if c < len(
                            self.listColor) else f'C{c}',
                        label=[f'{self.listBatteryNameSplit[b]}', 'Filtered'],
                        visible=True,
                        linewidth=0.5
                    )
                    lines_filtered.append(fl)
                except (IndexError, ValueError, TypeError, AttributeError) as e:
                    logger.error("绘制电池 %s, 电流级别 %s 的曲线时出错: %s", b, c, e)

        return lines_unfiltered, lines_filtered

    def _show_error_plot(self, title=None, main_message=None, details=None, allow_file_selection=True):
        """显示详细的错误信息图表"""
        try:
            if title is None:
                title = "数据错误"
            if main_message is None:
                main_message = "无法加载或显示电池数据"
            if details is None:
                details = "1. csv文件是否存在且格式正确\n"
                details += "2. 配置文件是否正确选择\n"
                details += "3. 文件路径是否包含中文字符或特殊字符\n"
                details += "4. csv文件是否包含有效的电池测试数据"

            fig, ax = plt.subplots(figsize=(12, 8))
            self.current_fig = fig

            self._apply_modern_plot_style(fig, ax)

            title_color = MODERN_BUTTON_STYLE['active_color']
            ax.set_title(title, fontsize=18, fontweight='bold',
                         color=title_color, pad=20)

            ax.axis('off')

            full_text = f"{main_message}\n\n"
            full_text += "检查步骤:\n"
            full_text += details

            if allow_file_selection:
                full_text += "\n\n解决方案:\n"
                full_text += "1. 点击菜单栏'File' -> 'Open Data'选择数据目录\n"
                full_text += "2. 或按Ctrl+O键打开文件对话框\n"
                full_text += "3. 选择包含Info_Image.csv文件的目录"

            if hasattr(self, 'errorlog') and self.errorlog:
                full_text += f"\n\n错误详情: {str(self.errorlog)}"

            text_color = MODERN_BUTTON_STYLE['inactive_text_color']
            main_text_color = MODERN_BUTTON_STYLE['active_color']

            main_text = f"{main_message}\n\n"
            ax.text(0.5, 0.75, main_text, fontsize=14, ha='center', va='center',
                    color=main_text_color, weight='bold', linespacing=1.4)

            check_text = "检查步骤:\n" + details
            ax.text(0.5, 0.55, check_text, fontsize=11, ha='center', va='center',
                    color=text_color, linespacing=1.4)

            if allow_file_selection:
                solution_text = "\n\n解决方案:\n" + "1. 点击菜单栏'File' -> 'Open Data'选择数据目录\n" + \
                               "2. 或按Ctrl+O键打开文件对话框\n" + "3. 选择包含Info_Image.csv文件的目录"
                ax.text(0.5, 0.35, solution_text, fontsize=11, ha='center', va='center',
                        color=MODERN_BUTTON_STYLE['hover_color'], weight='bold', linespacing=1.4)

            if hasattr(self, 'errorlog') and self.errorlog:
                error_text = f"\n错误详情: {str(self.errorlog)}"
                ax.text(0.5, 0.15, error_text, fontsize=10, ha='center', va='center',
                        color='#d32f2f', style='italic', linespacing=1.3)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fig.text(0.02, 0.01, f"Battery Analysis Tool v1.0 | {current_time}",
                     fontsize=9, color='#6c757d', alpha=0.8)

            for spine in ax.spines.values():
                spine.set_color(MODERN_BUTTON_STYLE['border_color'])
                spine.set_linewidth(1.5)
                spine.set_alpha(0.8)

            menu_added = self._add_menu_bar(fig)
            if not menu_added:
                logger.warning("无法添加菜单栏，将使用默认方式显示错误图表")

            logger.info("显示错误信息图表: %s - %s", title, main_message)
            plt.tight_layout()

            if not plt.isinteractive():
                plt.ion()

            plt.show(block=False)
            plt.pause(0.1)

            fig.canvas.draw()
            fig.canvas.flush_events()

        except (OSError, ValueError) as e:
            logger.critical("显示错误图表时发生异常: %s", str(e))
            traceback.print_exc()
            logger.error("\n严重错误: 无法显示图形界面的错误信息")
            logger.error("错误详情: %s - %s", title or '未知错误', main_message or '无法加载数据')

    def _cleanup_matplotlib_state(self):
        """清理Matplotlib状态，确保新的图表能正常工作"""
        logger.info("开始清理Matplotlib状态")
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)

        matplotlib.rcParams['font.sans-serif'] = CN_FONT_LIST
        matplotlib.rcParams['axes.unicode_minus'] = False

        if matplotlib.get_backend() != 'QtAgg':
            logger.info("当前Matplotlib后端: %s, 切换到QtAgg后端", matplotlib.get_backend())
            matplotlib.use('QtAgg')

        logger.info("Matplotlib状态清理完成")

    def _adjust_y_axis_range(self, ax):
        """动态调整纵轴范围，确保所有数据都能显示"""
        try:
            y_min = float('inf')
            y_max = float('-inf')

            for b in range(self.intBatteryNum):
                for c in range(self.intCurrentLevelNum):
                    try:
                        if c < len(self.listPlt) and b < len(self.listPlt[c][1]):
                            voltage_data = self.listPlt[c][1][b]
                            if voltage_data:
                                current_min = min(voltage_data)
                                current_max = max(voltage_data)
                                y_min = min(y_min, current_min)
                                y_max = max(y_max, current_max)

                        if c < len(self.listPlt) and b < len(self.listPlt[c][3]):
                            filtered_voltage_data = self.listPlt[c][3][b]
                            if filtered_voltage_data:
                                current_min = min(filtered_voltage_data)
                                current_max = max(filtered_voltage_data)
                                y_min = min(y_min, current_min)
                                y_max = max(y_max, current_max)
                    except (IndexError, ValueError, TypeError):
                        continue

            if y_min != float('inf') and y_max != float('-inf'):
                y_range = y_max - y_min
                y_min = y_min - 0.1 * y_range
                y_max = y_max + 0.1 * y_range
                y_min = max(y_min, 0)

                ax.set_ylim(y_min, y_max)
                logger.info("动态调整纵轴范围: [%.4f, %.4f]", y_min, y_max)

                y_range_actual = y_max - y_min
                target_ticks = 15
                optimal_interval = y_range_actual / target_ticks

                if y_range_actual < 5:
                    intervals = [0.1, 0.2, 0.5]
                elif y_range_actual < 20:
                    intervals = [0.5, 1.0, 2.0]
                else:
                    intervals = [1.0, 2.0, 5.0, 10.0]

                best_interval = min(intervals, key=lambda x: abs(x - optimal_interval))

                y_major_locator = MultipleLocator(best_interval)
                ax.yaxis.set_major_locator(y_major_locator)
                logger.info("动态调整Y轴刻度间隔: %s", best_interval)
            else:
                logger.warning("无法计算有效的纵轴范围，使用默认值")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("调整纵轴范围时出错: %s", e)
