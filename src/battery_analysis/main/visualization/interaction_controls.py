"""
交互控件模块

提供现代化按钮、菜单栏、过滤切换、电池选择、悬停等功能
"""

import datetime
import logging
import traceback

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from battery_analysis.main.visualization.styling import MODERN_BUTTON_STYLE
from battery_analysis.utils.version import Version

logger = logging.getLogger(__name__)


def _battery_line_indices(battery_index, current_level_num):
    """返回属于指定电池的所有曲线索引。

    曲线按电池主序构建（figure_builder 中 line = b*current_level + c），
    因此电池 b 的曲线索引区间为 [b*level, (b+1)*level)。
    """
    start = battery_index * current_level_num
    return range(start, start + current_level_num)


def _select_hover_lines(check_filter, lines_filtered, lines_unfiltered):
    """根据过滤按钮状态选择悬停应扫描的曲线集合。

    修复：check_filter 实为过滤按钮状态 dict（含 'active' 键），
    旧代码对其调用 .get_status() 必抛 AttributeError，导致悬停永远扫描 Filtered 曲线。
    """
    filtered = True
    if check_filter is not None and isinstance(check_filter, dict):
        filtered = check_filter.get("active", True)
    return lines_filtered if filtered else lines_unfiltered


class InteractionControlsMixin:
    """交互控件混入类，提供按钮、菜单、悬停等交互功能"""

    def _get_button_pad(self, width, height):
        """计算 FancyBboxPatch 的圆角 pad（transAxes 分数单位）。

        matplotlib 的 FancyBboxPatch 在 transform=ax.transAxes 下，boxstyle 的
        pad 单位是 axes 分数（不是像素）。若 pad 固定取 4/100=0.04，而电池按钮
        高度只有 0.95/32≈0.03（32 个电池时），每个按钮 patch 会向外扩张 pad，
        视觉高度膨胀到按钮高度的 3.7 倍，导致 hover 高亮覆盖 3~4 个按钮、视觉
        边界与点击命中区域错位。

        这里让 pad 随按钮尺寸动态取小值：
        - 不超过按钮最小尺寸的 15%（保证补偿后矩形仍为正）
        - 上限 0.02（避免大按钮圆角过大）
        """
        return min(0.02, min(width, height) * 0.15)

    def _battery_name_sort_key(self, name):
        """解析电池名称的数字排序键，用于按钮正序（从小到大）排列。

        名称形如 '8-8'（或 '8_8'、'Battery-5'），取前两个数字段构成排序元组，
        使 5-1 排在最上、8-8 排在最后。无法解析的名称返回无穷大排到末尾。
        """
        try:
            parts = str(name).replace("-", "_").split("_")
            return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
        except (ValueError, IndexError, TypeError):
            return (float("inf"), 0)

    def _create_modern_button(
        self, ax, x, y, width, height, text, callback, is_toggle=False, initial_state=False
    ):
        """创建现代化按钮"""
        try:
            pad = self._get_button_pad(width, height)
            # 矩形内缩 pad 以补偿 boxstyle 的向外扩张，使视觉范围恰好等于
            # 逻辑范围 [x, x+width]×[y, y+height]，与点击命中检测保持一致。
            button_bg = FancyBboxPatch(
                (x + pad, y + pad),
                width - 2 * pad,
                height - 2 * pad,
                boxstyle=f"round,pad={pad}",
                facecolor=MODERN_BUTTON_STYLE["inactive_color"],
                edgecolor=MODERN_BUTTON_STYLE["border_color"],
                linewidth=MODERN_BUTTON_STYLE["border_width"],
                alpha=0.95,
                transform=ax.transAxes,
            )
            ax.add_patch(button_bg)

            button_text = ax.text(
                x + width / 2,
                y + height / 2,
                text,
                ha="center",
                va="center",
                fontsize=MODERN_BUTTON_STYLE["font_size"],
                color=MODERN_BUTTON_STYLE["inactive_text_color"],
                weight=MODERN_BUTTON_STYLE["font_weight"] if is_toggle else "normal",
                transform=ax.transAxes,
            )

            state = {
                "active": initial_state,
                "bg": button_bg,
                "text": button_text,
                "hover": False,
                "pad": pad,
            }

            self._update_button_style(state)

            def on_button_hover(event):
                if event.inaxes != ax:
                    if state["hover"]:
                        state["hover"] = False
                        self._update_button_style(state)
                    return

                is_in_button = x <= event.xdata <= x + width and y <= event.ydata <= y + height

                if is_in_button and not state["hover"]:
                    state["hover"] = True
                    self._update_button_style(state, hover=True)
                    ax.figure.canvas.draw_idle()
                elif not is_in_button and state["hover"]:
                    state["hover"] = False
                    self._update_button_style(state)
                    ax.figure.canvas.draw_idle()

            def on_button_click(event):
                if event.inaxes != ax:
                    return

                if x <= event.xdata <= x + width and y <= event.ydata <= y + height:
                    if is_toggle:
                        state["active"] = not state["active"]
                        self._update_button_style(state)
                    else:
                        self._update_button_style(state, pressed=True)
                        self._reset_button_after_delay(state, delay=0.1)

                    try:
                        callback()
                    except (TypeError, ValueError, AttributeError) as e:
                        logger.error("Error executing button callback: %s", e)

                    ax.figure.canvas.draw_idle()

            ax.figure.canvas.mpl_connect("motion_notify_event", on_button_hover)
            ax.figure.canvas.mpl_connect("button_press_event", on_button_click)

            return state

        except (ValueError, TypeError, AttributeError) as e:
            logger.error("Error creating modern button: %s", e)
            return None

    def _create_modern_toggle_group(self, ax, x, y, width, height, buttons_config):
        """创建现代化切换按钮组"""
        try:
            button_states = []
            button_width = width / len(buttons_config)

            for i, config in enumerate(buttons_config):
                btn_x = x + i * button_width
                btn_state = self._create_modern_button(
                    ax,
                    btn_x,
                    y,
                    button_width - 0.005,
                    height,
                    config["text"],
                    config["callback"],
                    is_toggle=True,
                    initial_state=config.get("initial", False),
                )
                if btn_state:
                    button_states.append(btn_state)

            return button_states

        except (ValueError, TypeError, AttributeError) as e:
            logger.error("Error creating modern toggle button group: %s", e)
            return []

    def _add_filter_button(
        self, fig, ax, lines_unfiltered, lines_filtered, title_fontdict, axis_fontdict
    ):
        """添加过滤/未过滤数据切换按钮"""
        try:
            ax_filter = fig.add_axes([0.001, 0.92, 0.12, 0.05])
            ax_filter.set_xlim(0, 1)
            ax_filter.set_ylim(0, 1)
            ax_filter.axis("off")

            is_filtered = {"value": True}
            button_state_ref = {"button_state": None}

            def toggle_filter_mode():
                try:
                    is_filtered["value"] = not is_filtered["value"]

                    if button_state_ref and isinstance(button_state_ref, dict):
                        button_state = button_state_ref.get("button_state")
                        if (
                            button_state
                            and isinstance(button_state, dict)
                            and "text" in button_state
                        ):
                            new_text = "[Filtered]" if is_filtered["value"] else "[All Data]"
                            button_state["text"].set_text(new_text)

                    if is_filtered["value"]:
                        fig.canvas.manager.window.setWindowTitle(f"Filtered {self.strPltName}")
                        ax.set_title(f"Filtered {self.strPltName}", fontdict=title_fontdict)
                        ax.set_ylabel("Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)

                        for i in range(min(len(lines_unfiltered), len(lines_filtered))):
                            battery_index = i // self.intCurrentLevelNum
                            battery_visible = any(
                                lines_unfiltered[j].get_visible()
                                for j in _battery_line_indices(
                                    battery_index, self.intCurrentLevelNum
                                )
                                if j < len(lines_unfiltered)
                            )
                            lines_filtered[i].set_visible(battery_visible)
                            lines_unfiltered[i].set_visible(False)
                    else:
                        fig.canvas.manager.window.setWindowTitle(f"Unfiltered {self.strPltName}")
                        ax.set_title(f"Unfiltered {self.strPltName}", fontdict=title_fontdict)
                        ax.set_ylabel("Unfiltered Battery Load Voltage [V]", fontdict=axis_fontdict)

                        for i in range(min(len(lines_filtered), len(lines_unfiltered))):
                            battery_index = i // self.intCurrentLevelNum
                            battery_visible = any(
                                lines_filtered[j].get_visible()
                                for j in _battery_line_indices(
                                    battery_index, self.intCurrentLevelNum
                                )
                                if j < len(lines_filtered)
                            )
                            lines_unfiltered[i].set_visible(battery_visible)
                            lines_filtered[i].set_visible(False)

                    fig.canvas.draw_idle()
                except (AttributeError, TypeError, ValueError, IndexError) as e:
                    logger.error("Error toggling filter mode: %s", e)

            button_text = "[Filtered]" if is_filtered["value"] else "[All Data]"
            button_state = self._create_modern_button(
                ax_filter,
                0.02,
                0.15,
                0.96,
                0.7,
                button_text,
                toggle_filter_mode,
                is_toggle=True,
                initial_state=True,
            )

            button_state_ref["button_state"] = button_state
            self.filter_button_state = button_state

            logger.info("Modern filter button added successfully")

        except (ValueError, TypeError, AttributeError) as e:
            logger.error("Error creating filter button: %s", e)

        return button_state_ref["button_state"]

    def _add_battery_selection_buttons(self, fig, check_filter, lines_unfiltered, lines_filtered):
        """添加电池选择现代化按钮"""
        button_states_line1 = None
        button_states_line2 = None

        if self.intBatteryNum > 32:
            button_states_line1 = self._create_battery_check_buttons(
                fig,
                [0.001, 0.005, 0.04, 0.029 * 32],
                0,
                32,
                check_filter,
                lines_unfiltered,
                lines_filtered,
            )
            button_states_line2 = self._create_battery_check_buttons(
                fig,
                [0.041, 0.005, 0.04, 0.029 * 32],
                32,
                64,
                check_filter,
                lines_unfiltered,
                lines_filtered,
            )
        else:
            button_states_line1 = self._create_battery_check_buttons(
                fig,
                [0.001, 0.005, 0.04, 0.029 * 32],
                0,
                32,
                check_filter,
                lines_unfiltered,
                lines_filtered,
            )

            ax_empty = fig.add_axes([0.041, 0.005, 0.04, 0.029 * 32])
            ax_empty.set_xlim(0, 1)
            ax_empty.set_ylim(0, 1)
            ax_empty.axis("off")
            ax_empty.text(
                0.5,
                0.5,
                "Empty",
                ha="center",
                va="center",
                fontsize=8,
                alpha=0.5,
                transform=ax_empty.transAxes,
            )
            button_states_line2 = []

        self.battery_button_states = {"line1": button_states_line1, "line2": button_states_line2}

        logger.info("Modern battery selection buttons added successfully")
        return button_states_line1, button_states_line2

    def _create_battery_check_buttons(
        self, fig, rect, start_idx, end_idx, check_filter, lines_unfiltered, lines_filtered
    ):
        """创建电池选择现代化按钮"""
        ax_buttons = fig.add_axes(rect)
        ax_buttons.set_xlim(0, 1)
        ax_buttons.set_ylim(0, 1)
        ax_buttons.axis("off")
        ax_buttons.invert_yaxis = False

        self.battery_button_states = []

        battery_info = []
        for i in range(start_idx, end_idx):
            if i < self.intBatteryNum:
                battery_info.append(
                    {
                        "name": self.listBatteryNameSplit[i],
                        "index": i,
                        "initial_state": True,
                        "is_none": False,
                    }
                )
            else:
                battery_info.append(
                    {
                        "name": f"Battery {start_idx + 1}",
                        "index": i,
                        "initial_state": False,
                        "is_none": True,
                    }
                )

        battery_info.sort(key=lambda x: x["index"])

        num_valid_batteries = min(self.intBatteryNum - start_idx, end_idx - start_idx)
        if num_valid_batteries > 0:
            total_height = 0.95
            button_height = total_height / num_valid_batteries
            button_width = 0.96
        else:
            button_height = 0.1
            button_width = 0.96

        button_states = []
        # 电池索引 → 按钮 state 映射，供 toggle 回调按索引查找对应按钮状态。
        # 避免 lambda 晚绑定捕获循环变量 button_state（所有回调曾指向最后一个
        # 按钮的 state，导致点击任意电池都会连带切换排序后的末位按钮）。
        index_to_state = {}

        def toggle_battery_visibility(battery_idx, button_state=None):
            try:
                logger.debug("Toggling visibility of battery %s", battery_idx)

                if battery_info[battery_idx - start_idx].get("is_none", False):
                    return

                is_filtered = (
                    self.filter_button_state["active"]
                    if hasattr(self, "filter_button_state")
                    else True
                )

                battery_index = battery_info[battery_idx - start_idx]["index"]

                current_lines = lines_filtered if is_filtered else lines_unfiltered
                line_indices = _battery_line_indices(battery_index, self.intCurrentLevelNum)

                battery_visible = any(
                    current_lines[i].get_visible() for i in line_indices if i < len(current_lines)
                )

                new_visibility = not battery_visible

                updated = False
                for i in line_indices:
                    if i < len(current_lines):
                        current_lines[i].set_visible(new_visibility)
                        updated = True

                other_lines = lines_unfiltered if is_filtered else lines_filtered
                for i in line_indices:
                    if i < len(other_lines):
                        other_lines[i].set_visible(new_visibility)

                if button_state is None:
                    button_state = index_to_state.get(battery_idx)
                if button_state is None:
                    return
                button_state["active"] = new_visibility
                self._update_button_style(button_state)

                if updated:
                    fig.canvas.draw_idle()
            except (AttributeError, TypeError, ValueError, IndexError) as e:
                logger.error("Error selecting battery: %s", e)

        valid_batteries = [battery for battery in battery_info if not battery["is_none"]]
        # 按电池名称数字正序排列（如 5-1 在最上、8-8 在最下）。
        # 仅改变按钮显示顺序，battery['index'] 仍绑定真实通道的曲线数据。
        valid_batteries.sort(key=lambda x: self._battery_name_sort_key(x["name"]))
        num_valid = len(valid_batteries)

        for i, battery in enumerate(valid_batteries):
            # matplotlib axes 的 y 轴自下而上：y_pos 越大越靠上。
            # 反转 i 使正序（5-1 顶、8-8 底）在视觉上从上到下排列。
            y_pos = (num_valid - 1 - i) * button_height

            button_state = self._create_modern_button(
                ax_buttons,
                0.02,
                y_pos,
                button_width,
                button_height,
                battery["name"][:12] + "..." if len(battery["name"]) > 12 else battery["name"],
                lambda idx=battery["index"]: toggle_battery_visibility(idx),
                is_toggle=True,
                initial_state=battery["initial_state"],
            )

            if button_state:
                index_to_state[battery["index"]] = button_state
                button_states.append((battery["index"], button_state))

        logger.info(
            "Modern battery selection button group created successfully (%s-%s)", start_idx, end_idx
        )
        return button_states

    def _add_help_text(self, fig):
        """添加帮助文本到图表右上角"""
        try:
            fig.text(
                0.98, 0.85, "Tip: Hover over a data point to view details", fontsize=7, ha="right"
            )
            fig.text(
                0.98,
                0.78,
                "Shortcuts: Scroll to zoom, drag to pan, right-click to reset view",
                fontsize=7,
                ha="right",
            )
            logger.info("Help text added successfully")
        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("Error adding help text: %s", e)

    def _add_hover_functionality(self, fig, ax, lines_filtered, lines_unfiltered, check_filter):
        """添加鼠标悬停功能，显示数据点信息"""
        try:
            annot = ax.annotate(
                "",
                xy=(0, 0),
                xytext=(10, 10),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.7),
                arrowprops=dict(arrowstyle="->"),
            )
            annot.set_visible(False)

            def on_hover(event):
                if event.inaxes == ax:
                    current_lines = _select_hover_lines(
                        check_filter, lines_filtered, lines_unfiltered
                    )

                    min_dist = float("inf")
                    closest_point = None
                    closest_line_label = None

                    for line in current_lines:
                        if line.get_visible():
                            try:
                                x_data = line.get_xdata()
                                y_data = line.get_ydata()
                                line_label = line.get_label()

                                for i, (x, y) in enumerate(zip(x_data, y_data)):
                                    dist = ((x - event.xdata) ** 2 + (y - event.ydata) ** 2) ** 0.5
                                    if dist < min_dist and dist < 0.05 * (
                                        self.maxXaxis - self.listAxis[0]
                                    ):
                                        min_dist = dist
                                        closest_point = (x, y, i)
                                        closest_line_label = line_label
                            except (AttributeError, TypeError, ValueError, IndexError):
                                continue

                    if closest_point:
                        x, y, idx = closest_point
                        annot.xy = (x, y)

                        label_text = ""
                        if isinstance(closest_line_label, list) and len(closest_line_label) > 0:
                            label_text = f"{closest_line_label[0]}"
                            if len(closest_line_label) > 1:
                                label_text += f" ({closest_line_label[1]})"
                        else:
                            label_text = str(closest_line_label)

                        annot.set_text(
                            f"{label_text}\nPoint {idx}:\nCharge: {x:.2f} mAh\nVoltage: {y:.4f} V"
                        )
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                    else:
                        if annot.get_visible():
                            annot.set_visible(False)
                            fig.canvas.draw_idle()

            fig.canvas.mpl_connect("motion_notify_event", on_hover)

        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("Error adding hover functionality: %s", e)

    def _add_file_operation_buttons(self, fig):
        """添加文件操作按钮区域（打开文件和退出按钮）"""
        try:
            ax_file = fig.add_axes([0.001, 0.90, 0.17, 0.062])
            ax_file.set_xlim(0, 1)
            ax_file.set_ylim(0, 1)
            ax_file.axis("off")

            buttons_config = [
                {"text": "Open", "callback": lambda: self._open_file_dialog(), "initial": False},
                {"text": "Exit", "callback": lambda: self._close_viewer(), "initial": False},
            ]

            self.file_button_states = self._create_modern_toggle_group(
                ax_file, 0.02, 0.15, 0.96, 0.7, buttons_config
            )

            logger.info("Modern file operation button area added successfully")
        except (ValueError, TypeError, AttributeError) as e:
            logger.error("Error creating file operation buttons: %s", e)

    def _add_menu_bar(self, fig):
        """为图表添加菜单栏（统一使用PyQt6）"""
        try:
            logger.info("Starting to add PyQt6 menubar")

            manager = fig.canvas.manager
            if not manager or not hasattr(manager, "window"):
                logger.warning(
                    "Unable to obtain matplotlib window manager, skipping menubar addition"
                )
                return False

            if hasattr(manager.window, "menuBar"):
                self._apply_window_modern_style(manager.window)

                menubar = manager.window.menuBar()
                self._apply_menubar_style(menubar)

                file_menu = menubar.addMenu("File")
                self._apply_menu_style(file_menu)

                open_action = file_menu.addAction("Open")
                open_action.setProperty("menu_action", "open")

                def on_open_clicked():
                    logger.info("Open menu item clicked")
                    self._open_file_dialog()

                open_action.triggered.connect(on_open_clicked)

                file_menu.addSeparator()

                exit_action = file_menu.addAction("Exit")
                exit_action.setProperty("menu_action", "exit")

                def on_exit_clicked():
                    logger.info("Exit menu item clicked, closing visualizer window")
                    if self.current_fig is not None:
                        plt.close(self.current_fig)
                        self.current_fig = None
                        logger.info("Visualizer window closed")
                    else:
                        logger.warning("No visualizer window is currently open")

                exit_action.triggered.connect(on_exit_clicked)

                help_menu = menubar.addMenu("Help")
                self._apply_menu_style(help_menu)

                about_action = help_menu.addAction("About")
                about_action.setProperty("menu_action", "about")

                def on_about_clicked():
                    logger.info("About menu item clicked")
                    self._show_about_dialog()

                about_action.triggered.connect(on_about_clicked)
                logger.info("PyQt6 menubar added successfully")
            else:
                raise RuntimeError("Window does not support a menu bar")

        except ImportError as e:
            raise ImportError(
                f"PyQt6 dependency missing: {e}. Please ensure PyQt6 is installed correctly"
            )
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            logger.error("Failed to add menubar: %s", e)
            raise RuntimeError(f"Menu bar initialization failed: {e}") from e

    def _open_file_dialog(self):
        """打开文件对话框，允许用户选择数据文件"""
        logger.info("=== _open_file_dialog method started ===")
        try:
            logger.info("Attempting to open file dialog to select data directory")

            data_dir = None

            logger.info("Attempting to use Qt file dialog")
            try:
                data_dir = QFileDialog.getExistingDirectory(
                    None,
                    "Select Data Directory",
                    self.strPltPath or ".",
                    QFileDialog.Option.ShowDirsOnly,
                )
                logger.info("Qt file dialog succeeded, return value: %s", data_dir)
            except (ImportError, AttributeError, TypeError, RuntimeError) as qt_error:
                logger.error("Qt file dialog failed: %s", qt_error)

            if data_dir:
                logger.info("User selected data directory: %s", data_dir)
                self.set_data_path(data_dir)
                success = self.load_data()
                if success:
                    logger.info("Data loaded successfully, redrawing chart")
                    self._cleanup_matplotlib_state()
                    if self.current_fig is not None:
                        plt.close(self.current_fig)
                        self.current_fig = None
                    self.plt_figure()
                else:
                    logger.error("Data loading failed, cannot display chart")
        except (AttributeError, TypeError, ValueError, OSError, RuntimeError) as e:
            logger.error("Error opening file dialog: %s", str(e))
            traceback.print_exc()

    def _show_about_dialog(self):
        """显示About对话框"""
        try:
            try:
                current_time = datetime.datetime.now().strftime("%Y")
            except (ImportError, OSError, ValueError) as e:
                logger.warning("Failed to get current year: %s", e)
                current_time = "2024"

            try:
                version_obj = Version()
                version_info = f"v{version_obj.version}"
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning("Unable to get version info, using default version: %s", e)
                version_info = "v2.0.0"

            about_text = f"""Battery Analysis Tool
Version: {version_info}

Battery test data visualization and analysis application
Supports importing multiple data formats and generating charts

Features:
• Import data from CSV files
• Interactive chart display and operation
• Toggle between filtered and unfiltered data
• Battery selection and channel control
• Hover to show detailed information

Developer: Ewin Battery Analysis Team
Copyright: © {current_time} MIT License

Thank you for using Battery Analysis Tool!"""

            msg_box = QMessageBox()
            msg_box.setWindowTitle("About")
            msg_box.setText(about_text)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()

            logger.info("About dialog displayed")
        except (AttributeError, TypeError, ValueError, OSError, RuntimeError) as e:
            logger.error("Failed to display About dialog: %s", e)
            try:
                version_obj = Version()
                fallback_version = f"v{version_obj.version}"
            except (ImportError, AttributeError, TypeError):
                fallback_version = "v2.1.2"

    def _close_viewer(self):
        """关闭viewer窗口"""
        try:
            logger.info("File operation button: Exit clicked, closing visualizer window")
            if self.current_fig is not None:
                plt.close(self.current_fig)
                self.current_fig = None
                logger.info("Visualizer window closed")
            else:
                logger.warning("No visualizer window is currently open")
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.error("Error closing viewer window: %s", e)

    def create_filter_checkbox(self, parent_widget, fig, ax, lines_unfiltered, lines_filtered, title_fontdict, axis_fontdict):
        """创建过滤切换 QCheckBox（Qt 控件版本）

        Args:
            parent_widget: 父 QWidget
            fig: matplotlib Figure 对象
            ax: matplotlib Axes 对象
            lines_unfiltered: 未过滤曲线列表
            lines_filtered: 过滤后曲线列表
            title_fontdict: 标题字体配置
            axis_fontdict: 坐标轴字体配置

        Returns:
            QCheckBox: 过滤切换复选框
        """
        from PyQt6.QtWidgets import QCheckBox

        checkbox = QCheckBox("Show Filtered Data", parent_widget)
        checkbox.setChecked(True)
        checkbox.setObjectName("filter_checkbox")

        def on_filter_toggled(checked):
            try:
                if checked:
                    if hasattr(fig.canvas.manager, "window"):
                        fig.canvas.manager.window.setWindowTitle(f"Filtered {self.strPltName}")
                    ax.set_title(f"Filtered {self.strPltName}", fontdict=title_fontdict)
                    ax.set_ylabel("Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)

                    for i in range(min(len(lines_unfiltered), len(lines_filtered))):
                        battery_index = i // self.intCurrentLevelNum
                        battery_visible = any(
                            lines_unfiltered[j].get_visible()
                            for j in _battery_line_indices(battery_index, self.intCurrentLevelNum)
                            if j < len(lines_unfiltered)
                        )
                        lines_filtered[i].set_visible(battery_visible)
                        lines_unfiltered[i].set_visible(False)
                else:
                    if hasattr(fig.canvas.manager, "window"):
                        fig.canvas.manager.window.setWindowTitle(f"Unfiltered {self.strPltName}")
                    ax.set_title(f"Unfiltered {self.strPltName}", fontdict=title_fontdict)
                    ax.set_ylabel("Unfiltered Battery Load Voltage [V]", fontdict=axis_fontdict)

                    for i in range(min(len(lines_filtered), len(lines_unfiltered))):
                        battery_index = i // self.intCurrentLevelNum
                        battery_visible = any(
                            lines_filtered[j].get_visible()
                            for j in _battery_line_indices(battery_index, self.intCurrentLevelNum)
                            if j < len(lines_filtered)
                        )
                        lines_unfiltered[i].set_visible(battery_visible)
                        lines_filtered[i].set_visible(False)

                fig.canvas.draw_idle()
            except (AttributeError, TypeError, ValueError, IndexError) as e:
                logger.error("Error toggling filter mode: %s", e)

        checkbox.toggled.connect(on_filter_toggled)

        # 保存引用以便后续访问
        self.filter_checkbox = checkbox
        self.filter_button_state = {"active": True}  # 兼容旧代码

        logger.info("Filter checkbox created successfully")
        return checkbox

    def create_battery_checkboxes(self, parent_widget, fig, lines_unfiltered, lines_filtered, check_filter):
        """创建电池选择 QCheckBox 列表（Qt 控件版本）

        Args:
            parent_widget: 父 QWidget
            fig: matplotlib Figure 对象
            lines_unfiltered: 未过滤曲线列表
            lines_filtered: 过滤后曲线列表
            check_filter: 过滤按钮状态（兼容旧代码）

        Returns:
            list: (battery_index, checkbox) 元组列表
        """
        from PyQt6.QtWidgets import QCheckBox, QVBoxLayout, QScrollArea, QWidget

        # 创建滚动区域
        scroll_area = QScrollArea(parent_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QW.QFrame.Shape.NoFrame)

        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        battery_checkboxes = []

        # 获取电池信息并排序
        battery_info = []
        for i in range(self.intBatteryNum):
            battery_info.append({
                "name": self.listBatteryNameSplit[i],
                "index": i,
                "initial_state": True,
            })

        # 按电池名称数字正序排列
        battery_info.sort(key=lambda x: self._battery_name_sort_key(x["name"]))

        for battery in battery_info:
            checkbox = QCheckBox(battery["name"][:12] + "..." if len(battery["name"]) > 12 else battery["name"], content_widget)
            checkbox.setChecked(battery["initial_state"])
            checkbox.setObjectName(f"battery_checkbox_{battery['index']}")

            def on_battery_toggled(checked, idx=battery["index"]):
                try:
                    # 确定当前应该操作哪组曲线
                    is_filtered = True
                    if hasattr(self, "filter_checkbox"):
                        is_filtered = self.filter_checkbox.isChecked()
                    elif check_filter is not None and isinstance(check_filter, dict):
                        is_filtered = check_filter.get("active", True)

                    current_lines = lines_filtered if is_filtered else lines_unfiltered
                    other_lines = lines_unfiltered if is_filtered else lines_filtered

                    line_indices = _battery_line_indices(idx, self.intCurrentLevelNum)

                    # 设置曲线可见性
                    for i in line_indices:
                        if i < len(current_lines):
                            current_lines[i].set_visible(checked)
                        if i < len(other_lines):
                            other_lines[i].set_visible(checked)

                    fig.canvas.draw_idle()
                except (AttributeError, TypeError, ValueError, IndexError) as e:
                    logger.error("Error selecting battery: %s", e)

            checkbox.toggled.connect(on_battery_toggled)
            layout.addWidget(checkbox)
            battery_checkboxes.append((battery["index"], checkbox))

        # 添加弹性空间
        layout.addStretch()

        scroll_area.setWidget(content_widget)

        # 保存引用
        self.battery_checkboxes = battery_checkboxes

        logger.info("Battery checkboxes created successfully (%d batteries)", len(battery_checkboxes))
        return scroll_area, battery_checkboxes

    def __del__(self):
        """析构函数，确保在对象销毁时释放所有资源"""
        try:
            if hasattr(self, "current_fig") and self.current_fig is not None:
                plt.close(self.current_fig)
                self.current_fig = None
                logger.info("Destructor: closing chart window")

            if hasattr(self, "_cleanup_matplotlib_state"):
                self._cleanup_matplotlib_state()
                logger.info("Destructor: cleaning up Matplotlib state")

            if hasattr(self, "listPlt"):
                try:
                    for c in range(len(self.listPlt)):
                        if len(self.listPlt[c]) >= 4:
                            self.listPlt[c][0].clear()
                            self.listPlt[c][1].clear()
                            self.listPlt[c][2].clear()
                            self.listPlt[c][3].clear()
                    logger.info("Destructor: releasing data resources")
                except Exception as e:
                    logger.error("Destructor: error releasing data resources: %s", e)

            logger.info("BatteryChartViewer object destroyed, resources released")
        except Exception as e:
            logger.error("Destructor execution exception: %s", e)
