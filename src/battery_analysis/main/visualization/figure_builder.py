"""
图形构建模块

提供Matplotlib图表初始化、曲线绘制、错误图表显示和坐标轴调整方法
"""

import datetime
import logging
import traceback

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from battery_analysis.main.visualization.styling import MODERN_BUTTON_STYLE
from battery_analysis.utils.constants import CN_FONT_LIST

logger = logging.getLogger(__name__)


class FigureBuilderMixin:
    """图形构建混入类，提供图表构建和绘制方法"""

    def _initialize_figure(self):
        """初始化图表设置和布局"""
        title_fontdict = {"fontsize": 15, "fontweight": "bold"}
        axis_fontdict = {"fontsize": 15}

        fig = plt.figure(figsize=(15, 6))
        try:
            if hasattr(fig.canvas.manager, "window"):
                fig.canvas.manager.window.setWindowTitle(f"Filtered {self.strPltName}")
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.warning("Unable to set chart window title: %s", str(e))

        gs = fig.add_gridspec(1, 40)
        ax = fig.add_subplot(gs[:, 5:])

        ax.axis(self.listAxis)
        x_ticks = self.listXTicks
        ax.set_xticks(x_ticks)

        y_major_locator = MultipleLocator(0.2)
        ax.yaxis.set_major_locator(y_major_locator)

        ax.set_title(f"Filtered {self.strPltName}", fontdict=title_fontdict)
        ax.set_xlabel("Charge [mAh]", fontdict=axis_fontdict)
        ax.set_ylabel("Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)

        ax.grid(linestyle="--", alpha=0.3)

        return fig, ax, title_fontdict, axis_fontdict

    def _plot_battery_curves(self, ax):
        """绘制所有电池的原始和过滤后的曲线"""
        lines_unfiltered = []
        lines_filtered = []

        for b in range(self.intBatteryNum):
            for c in range(self.intCurrentLevelNum):
                try:
                    (ul,) = ax.plot(
                        self.listPlt[c][0][b],
                        self.listPlt[c][1][b],
                        color=self.listColor[c] if c < len(self.listColor) else f"C{c}",
                        label=[f"{self.listBatteryNameSplit[b]}", "Unfiltered"],
                        visible=False,
                        linewidth=0.5,
                    )
                    lines_unfiltered.append(ul)

                    (fl,) = ax.plot(
                        self.listPlt[c][2][b],
                        self.listPlt[c][3][b],
                        color=self.listColor[c] if c < len(self.listColor) else f"C{c}",
                        label=[f"{self.listBatteryNameSplit[b]}", "Filtered"],
                        visible=True,
                        linewidth=0.5,
                    )
                    lines_filtered.append(fl)
                except (IndexError, ValueError, TypeError, AttributeError) as e:
                    logger.error(
                        "Error plotting curve for battery %s, current level %s: %s", b, c, e
                    )

        return lines_unfiltered, lines_filtered

    def _show_error_plot(
        self, title=None, main_message=None, details=None, allow_file_selection=True
    ):
        """显示详细的错误信息图表"""
        try:
            if title is None:
                title = "Data Error"
            if main_message is None:
                main_message = "Unable to load or display battery data"
            if details is None:
                details = "1. Whether the CSV file exists and is formatted correctly\n"
                details += "2. Whether the correct configuration file is selected\n"
                details += (
                    "3. Whether the file path contains Chinese characters or special characters\n"
                )
                details += "4. Whether the CSV file contains valid battery test data"

            fig, ax = plt.subplots(figsize=(12, 8))
            self.current_fig = fig

            self._apply_modern_plot_style(fig, ax)

            title_color = MODERN_BUTTON_STYLE["active_color"]
            ax.set_title(title, fontsize=18, fontweight="bold", color=title_color, pad=20)

            ax.axis("off")

            full_text = f"{main_message}\n\n"
            full_text += "Check steps:\n"
            full_text += details

            if allow_file_selection:
                full_text += "\n\nSolution:\n"
                full_text += (
                    "1. Click 'File' -> 'Open Data' in the menu bar to select a data directory\n"
                )
                full_text += "2. Or press Ctrl+O to open the file dialog\n"
                full_text += "3. Select a directory containing the Info_Image.csv file"

            if hasattr(self, "errorlog") and self.errorlog:
                full_text += f"\n\nError details: {self.errorlog!s}"

            text_color = MODERN_BUTTON_STYLE["inactive_text_color"]
            main_text_color = MODERN_BUTTON_STYLE["active_color"]

            main_text = f"{main_message}\n\n"
            ax.text(
                0.5,
                0.75,
                main_text,
                fontsize=14,
                ha="center",
                va="center",
                color=main_text_color,
                weight="bold",
                linespacing=1.4,
            )

            check_text = "Check steps:\n" + details
            ax.text(
                0.5,
                0.55,
                check_text,
                fontsize=11,
                ha="center",
                va="center",
                color=text_color,
                linespacing=1.4,
            )

            if allow_file_selection:
                solution_text = (
                    "\n\nSolution:\n"
                    + "1. Click 'File' -> 'Open Data' in the menu bar to select a data directory\n"
                    + "2. Or press Ctrl+O to open the file dialog\n"
                    + "3. Select a directory containing the Info_Image.csv file"
                )
                ax.text(
                    0.5,
                    0.35,
                    solution_text,
                    fontsize=11,
                    ha="center",
                    va="center",
                    color=MODERN_BUTTON_STYLE["hover_color"],
                    weight="bold",
                    linespacing=1.4,
                )

            if hasattr(self, "errorlog") and self.errorlog:
                error_text = f"\nError details: {self.errorlog!s}"
                ax.text(
                    0.5,
                    0.15,
                    error_text,
                    fontsize=10,
                    ha="center",
                    va="center",
                    color="#d32f2f",
                    style="italic",
                    linespacing=1.3,
                )

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fig.text(
                0.02,
                0.01,
                f"Battery Analysis Tool v1.0 | {current_time}",
                fontsize=9,
                color="#6c757d",
                alpha=0.8,
            )

            for spine in ax.spines.values():
                spine.set_color(MODERN_BUTTON_STYLE["border_color"])
                spine.set_linewidth(1.5)
                spine.set_alpha(0.8)

            menu_added = self._add_menu_bar(fig)
            if not menu_added:
                logger.warning(
                    "Unable to add menubar, will display error chart using default method"
                )

            logger.info("Displaying error information chart: %s - %s", title, main_message)
            plt.tight_layout()

            if not plt.isinteractive():
                plt.ion()

            plt.show(block=False)
            plt.pause(0.1)

            fig.canvas.draw()
            fig.canvas.flush_events()

        except (OSError, ValueError) as e:
            logger.critical("Exception while displaying error chart: %s", str(e))
            traceback.print_exc()
            logger.error(
                "\nCritical error: unable to display error information in the graphical interface"
            )
            logger.error(
                "Error details: %s - %s",
                title or "Unknown error",
                main_message or "Unable to load data",
            )

    def _cleanup_matplotlib_state(self):
        """清理Matplotlib状态，确保新的图表能正常工作"""
        logger.info("Starting to clean up Matplotlib state")
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)

        matplotlib.rcParams["font.sans-serif"] = CN_FONT_LIST
        matplotlib.rcParams["axes.unicode_minus"] = False

        # 修复 matplotlib 3.10+ backend 大小写问题（返回 'qtagg' 而非 'QtAgg'）
        if matplotlib.get_backend().lower() != "qtagg":
            logger.info(
                "Current Matplotlib backend: %s, switching to QtAgg backend",
                matplotlib.get_backend(),
            )
            matplotlib.use("QtAgg")

        logger.info("Matplotlib state cleanup complete")

    def _adjust_y_axis_range(self, ax):
        """动态调整纵轴范围，确保所有数据都能显示"""
        try:
            y_min = float("inf")
            y_max = float("-inf")

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

            if y_min != float("inf") and y_max != float("-inf"):
                y_range = y_max - y_min
                y_min = y_min - 0.1 * y_range
                y_max = y_max + 0.1 * y_range
                y_min = max(y_min, 0)

                ax.set_ylim(y_min, y_max)
                logger.info("Dynamically adjusting y-axis range: [%.4f, %.4f]", y_min, y_max)

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
                logger.info("Dynamically adjusting y-axis tick interval: %s", best_interval)
            else:
                logger.warning("Unable to calculate a valid y-axis range, using default value")
        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error adjusting y-axis range: %s", e)
