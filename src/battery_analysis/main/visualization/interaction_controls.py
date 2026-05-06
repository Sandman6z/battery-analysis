"""
交互控件模块

提供现代化按钮、菜单栏、过滤切换、电池选择、悬停等功能
"""

import logging
import traceback
import datetime
import threading

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from battery_analysis.main.visualization.styling import MODERN_BUTTON_STYLE
from battery_analysis.utils.version import Version

logger = logging.getLogger(__name__)


class InteractionControlsMixin:
    """交互控件混入类，提供按钮、菜单、悬停等交互功能"""

    def _create_modern_button(self, ax, x, y, width, height, text, callback,
                              is_toggle=False, initial_state=False):
        """创建现代化按钮"""
        try:
            button_bg = FancyBboxPatch(
                (x, y), width, height,
                boxstyle=f"round,pad={MODERN_BUTTON_STYLE['padding']/100}",
                facecolor=MODERN_BUTTON_STYLE['inactive_color'],
                edgecolor=MODERN_BUTTON_STYLE['border_color'],
                linewidth=MODERN_BUTTON_STYLE['border_width'],
                alpha=0.95,
                transform=ax.transAxes
            )
            ax.add_patch(button_bg)

            button_text = ax.text(
                x + width/2, y + height/2, text,
                ha='center', va='center',
                fontsize=MODERN_BUTTON_STYLE['font_size'],
                color=MODERN_BUTTON_STYLE['inactive_text_color'],
                weight=MODERN_BUTTON_STYLE['font_weight'] if is_toggle else 'normal',
                transform=ax.transAxes
            )

            state = {'active': initial_state, 'bg': button_bg, 'text': button_text, 'hover': False}

            self._update_button_style(state)

            def on_button_hover(event):
                if event.inaxes != ax:
                    if state['hover']:
                        state['hover'] = False
                        self._update_button_style(state)
                    return

                is_in_button = (x <= event.xdata <= x + width and
                                y <= event.ydata <= y + height)

                if is_in_button and not state['hover']:
                    state['hover'] = True
                    self._update_button_style(state, hover=True)
                    ax.figure.canvas.draw_idle()
                elif not is_in_button and state['hover']:
                    state['hover'] = False
                    self._update_button_style(state)
                    ax.figure.canvas.draw_idle()

            def on_button_click(event):
                if event.inaxes != ax:
                    return

                if (x <= event.xdata <= x + width and
                    y <= event.ydata <= y + height):

                    if is_toggle:
                        state['active'] = not state['active']
                        self._update_button_style(state)
                    else:
                        self._update_button_style(state, pressed=True)
                        self._reset_button_after_delay(state, delay=0.1)

                    try:
                        callback()
                    except (TypeError, ValueError, AttributeError) as e:
                        logger.error("按钮回调执行出错: %s", e)

                    ax.figure.canvas.draw_idle()

            ax.figure.canvas.mpl_connect('motion_notify_event', on_button_hover)
            ax.figure.canvas.mpl_connect('button_press_event', on_button_click)

            return state

        except (ValueError, TypeError, AttributeError) as e:
            logger.error("创建现代化按钮时出错: %s", e)
            return None

    def _create_modern_toggle_group(self, ax, x, y, width, height, buttons_config):
        """创建现代化切换按钮组"""
        try:
            button_states = []
            button_width = width / len(buttons_config)

            for i, config in enumerate(buttons_config):
                btn_x = x + i * button_width
                btn_state = self._create_modern_button(
                    ax, btn_x, y, button_width - 0.005, height,
                    config['text'], config['callback'],
                    is_toggle=True, initial_state=config.get('initial', False)
                )
                if btn_state:
                    button_states.append(btn_state)

            return button_states

        except (ValueError, TypeError, AttributeError) as e:
            logger.error("创建现代化切换按钮组时出错: %s", e)
            return []

    def _add_filter_button(self, fig, ax, lines_unfiltered, lines_filtered,
                           title_fontdict, axis_fontdict):
        """添加过滤/未过滤数据切换按钮"""
        try:
            ax_filter = fig.add_axes([0.001, 0.92, 0.12, 0.05])
            ax_filter.set_xlim(0, 1)
            ax_filter.set_ylim(0, 1)
            ax_filter.axis('off')

            is_filtered = {'value': True}
            button_state_ref = {'button_state': None}

            def toggle_filter_mode():
                try:
                    is_filtered['value'] = not is_filtered['value']

                    if button_state_ref and isinstance(button_state_ref, dict):
                        button_state = button_state_ref.get('button_state')
                        if button_state and isinstance(button_state, dict) and 'text' in button_state:
                            new_text = "🔍 Filtered" if is_filtered['value'] else "📊 All Data"
                            button_state['text'].set_text(new_text)

                    if is_filtered['value']:
                        fig.canvas.manager.window.setWindowTitle(
                            f"Filtered {self.strPltName}")
                        ax.set_title(
                            f"Filtered {self.strPltName}", fontdict=title_fontdict)
                        ax.set_ylabel(
                            "Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)

                        for i in range(min(len(lines_unfiltered), len(lines_filtered))):
                            battery_index = i % self.intBatteryNum
                            battery_visible = any(lines_unfiltered[battery_index + j * self.intBatteryNum].get_visible()
                                                  for j in range(self.intCurrentLevelNum))
                            lines_filtered[i].set_visible(battery_visible)
                            lines_unfiltered[i].set_visible(False)
                    else:
                        fig.canvas.manager.window.setWindowTitle(
                            f"Unfiltered {self.strPltName}")
                        ax.set_title(
                            f"Unfiltered {self.strPltName}", fontdict=title_fontdict)
                        ax.set_ylabel(
                            "Unfiltered Battery Load Voltage [V]", fontdict=axis_fontdict)

                        for i in range(min(len(lines_filtered), len(lines_unfiltered))):
                            battery_index = i % self.intBatteryNum
                            battery_visible = any(lines_filtered[battery_index + j * self.intBatteryNum].get_visible()
                                                  for j in range(self.intCurrentLevelNum))
                            lines_unfiltered[i].set_visible(battery_visible)
                            lines_filtered[i].set_visible(False)

                    fig.canvas.draw_idle()
                except (AttributeError, TypeError, ValueError, IndexError) as e:
                    logger.error("执行过滤切换时出错: %s", e)

            button_text = "🔍 Filtered" if is_filtered['value'] else "📊 All Data"
            button_state = self._create_modern_button(
                ax_filter, 0.02, 0.15, 0.96, 0.7,
                button_text, toggle_filter_mode,
                is_toggle=True, initial_state=True
            )

            button_state_ref['button_state'] = button_state
            self.filter_button_state = button_state

            logger.info("成功添加现代化过滤按钮")

        except (ValueError, TypeError, AttributeError) as e:
            logger.error("创建过滤按钮时出错: %s", e)

        return button_state_ref['button_state']

    def _add_battery_selection_buttons(self, fig, check_filter, lines_unfiltered, lines_filtered):
        """添加电池选择现代化按钮"""
        button_states_line1 = None
        button_states_line2 = None

        if self.intBatteryNum > 32:
            button_states_line1 = self._create_battery_check_buttons(
                fig, [0.001, 0.005, 0.04, 0.029*32], 0, 32,
                check_filter, lines_unfiltered, lines_filtered
            )
            button_states_line2 = self._create_battery_check_buttons(
                fig, [0.041, 0.005, 0.04, 0.029*32], 32, 64,
                check_filter, lines_unfiltered, lines_filtered
            )
        else:
            button_states_line1 = self._create_battery_check_buttons(
                fig, [0.001, 0.005, 0.04, 0.029*32], 0, 32,
                check_filter, lines_unfiltered, lines_filtered
            )

            ax_empty = fig.add_axes([0.041, 0.005, 0.04, 0.029*32])
            ax_empty.set_xlim(0, 1)
            ax_empty.set_ylim(0, 1)
            ax_empty.axis('off')
            ax_empty.text(0.5, 0.5, 'Empty', ha='center', va='center',
                          fontsize=8, alpha=0.5, transform=ax_empty.transAxes)
            button_states_line2 = []

        self.battery_button_states = {
            'line1': button_states_line1,
            'line2': button_states_line2
        }

        logger.info("成功添加现代化电池选择按钮")
        return button_states_line1, button_states_line2

    def _create_battery_check_buttons(self, fig, rect, start_idx, end_idx,
                                      check_filter, lines_unfiltered, lines_filtered):
        """创建电池选择现代化按钮"""
        ax_buttons = fig.add_axes(rect)
        ax_buttons.set_xlim(0, 1)
        ax_buttons.set_ylim(0, 1)
        ax_buttons.axis('off')
        ax_buttons.invert_yaxis = False

        self.battery_button_states = []

        battery_info = []
        for i in range(start_idx, end_idx):
            if i < self.intBatteryNum:
                battery_info.append({
                    'name': self.listBatteryNameSplit[i],
                    'index': i,
                    'initial_state': True,
                    'is_none': False
                })
            else:
                battery_info.append({
                    'name': f"Battery {start_idx + 1}",
                    'index': i,
                    'initial_state': False,
                    'is_none': True
                })

        battery_info.sort(key=lambda x: x['index'])

        num_valid_batteries = min(self.intBatteryNum - start_idx, end_idx - start_idx)
        if num_valid_batteries > 0:
            total_height = 0.95
            button_height = total_height / num_valid_batteries
            button_width = 0.96
        else:
            button_height = 0.1
            button_width = 0.96

        button_states = []

        def toggle_battery_visibility(battery_idx, button_state):
            try:
                logger.debug("切换电池 %s 的可见性", battery_idx)

                if battery_info[battery_idx - start_idx].get('is_none', False):
                    return

                is_filtered = self.filter_button_state['active'] if hasattr(self, 'filter_button_state') else True

                battery_index = battery_info[battery_idx - start_idx]['index']

                current_lines = lines_filtered if is_filtered else lines_unfiltered
                battery_visible = False
                for i in range(len(current_lines)):
                    if i % self.intBatteryNum == battery_index:
                        battery_visible = current_lines[i].get_visible()
                        break

                new_visibility = not battery_visible

                updated = False
                for i in range(len(current_lines)):
                    if i % self.intBatteryNum == battery_index:
                        current_lines[i].set_visible(new_visibility)
                        updated = True

                other_lines = lines_unfiltered if is_filtered else lines_filtered
                for i in range(len(other_lines)):
                    if i % self.intBatteryNum == battery_index:
                        other_lines[i].set_visible(new_visibility)

                button_state['active'] = new_visibility
                self._update_button_style(button_state)

                if updated:
                    fig.canvas.draw_idle()
            except (AttributeError, TypeError, ValueError, IndexError) as e:
                logger.error("执行电池选择时出错: %s", e)

        valid_batteries = [battery for battery in battery_info if not battery['is_none']]
        num_valid = len(valid_batteries)

        for i, battery in enumerate(valid_batteries):
            y_pos = i * button_height

            button_state = self._create_modern_button(
                ax_buttons, 0.02, y_pos, button_width, button_height,
                battery['name'][:12] + '...' if len(battery['name']) > 12 else battery['name'],
                lambda idx=battery['index']: toggle_battery_visibility(idx, button_state),
                is_toggle=True,
                initial_state=battery['initial_state']
            )

            if button_state:
                button_states.append((battery['index'], button_state))

        logger.info("成功创建现代化电池选择按钮组 (%s-%s)", start_idx, end_idx)
        return button_states

    def _add_help_text(self, fig):
        """添加帮助文本到图表右上角"""
        try:
            fig.text(0.98, 0.85, "提示: 将鼠标悬停在数据点上查看详细信息", fontsize=7, ha='right')
            fig.text(0.98, 0.78, "快捷键: 滚轮缩放, 鼠标拖拽平移, 右键重置视图", fontsize=7, ha='right')
            logger.info("成功添加帮助文本")
        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("添加帮助文本时出错: %s", e)

    def _add_hover_functionality(self, fig, ax, lines_filtered, lines_unfiltered, check_filter):
        """添加鼠标悬停功能，显示数据点信息"""
        try:
            annot = ax.annotate(
                '', xy=(0, 0), xytext=(10, 10),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->')
            )
            annot.set_visible(False)

            def on_hover(event):
                if event.inaxes == ax:
                    if check_filter is not None:
                        try:
                            current_lines = lines_filtered if check_filter.get_status()[0] else lines_unfiltered
                        except (AttributeError, IndexError):
                            current_lines = lines_filtered
                    else:
                        current_lines = lines_filtered

                    min_dist = float('inf')
                    closest_point = None
                    closest_line_label = None

                    for line in current_lines:
                        if line.get_visible():
                            try:
                                x_data = line.get_xdata()
                                y_data = line.get_ydata()
                                line_label = line.get_label()

                                for i, (x, y) in enumerate(zip(x_data, y_data)):
                                    dist = ((x - event.xdata)**2 +
                                            (y - event.ydata) ** 2)**0.5
                                    if (dist < min_dist
                                            and dist < 0.05 * (self.maxXaxis - self.listAxis[0])):
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
                            f"{label_text}\n点 {idx}:\nCharge: {x:.2f} mAh\nVoltage: {y:.4f} V")
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                    else:
                        if annot.get_visible():
                            annot.set_visible(False)
                            fig.canvas.draw_idle()

            fig.canvas.mpl_connect('motion_notify_event', on_hover)

        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("添加悬停功能时出错: %s", e)

    def _add_file_operation_buttons(self, fig):
        """添加文件操作按钮区域（打开文件和退出按钮）"""
        try:
            ax_file = fig.add_axes([0.001, 0.90, 0.17, 0.062])
            ax_file.set_xlim(0, 1)
            ax_file.set_ylim(0, 1)
            ax_file.axis('off')

            buttons_config = [
                {
                    'text': '📁 Open',
                    'callback': lambda: self._open_file_dialog(),
                    'initial': False
                },
                {
                    'text': '❌ Exit',
                    'callback': lambda: self._close_viewer(),
                    'initial': False
                }
            ]

            self.file_button_states = self._create_modern_toggle_group(
                ax_file, 0.02, 0.15, 0.96, 0.7, buttons_config
            )

            logger.info("成功添加现代化文件操作按钮区域")
        except (ValueError, TypeError, AttributeError) as e:
            logger.error("创建文件操作按钮时出错: %s", e)

    def _add_menu_bar(self, fig):
        """为图表添加菜单栏（统一使用PyQt6）"""
        try:
            logger.info("开始添加PyQt6菜单栏")

            manager = fig.canvas.manager
            if not manager or not hasattr(manager, 'window'):
                logger.warning("无法获取matplotlib窗口管理器，跳过菜单栏添加")
                return False

            if hasattr(manager.window, 'menuBar'):
                self._apply_window_modern_style(manager.window)

                menubar = manager.window.menuBar()
                self._apply_menubar_style(menubar)

                file_menu = menubar.addMenu('File')
                self._apply_menu_style(file_menu)

                open_action = file_menu.addAction('Open')
                open_action.setProperty('menu_action', 'open')

                def on_open_clicked():
                    logger.info("Open菜单项被点击")
                    self._open_file_dialog()

                open_action.triggered.connect(on_open_clicked)

                file_menu.addSeparator()

                exit_action = file_menu.addAction('Exit')
                exit_action.setProperty('menu_action', 'exit')

                def on_exit_clicked():
                    logger.info("Exit菜单项被点击，关闭visualizer窗口")
                    if self.current_fig is not None:
                        plt.close(self.current_fig)
                        self.current_fig = None
                        logger.info("已关闭visualizer窗口")
                    else:
                        logger.warning("当前没有打开的visualizer窗口")

                exit_action.triggered.connect(on_exit_clicked)

                help_menu = menubar.addMenu('Help')
                self._apply_menu_style(help_menu)

                about_action = help_menu.addAction('About')
                about_action.setProperty('menu_action', 'about')

                def on_about_clicked():
                    logger.info("About菜单项被点击")
                    self._show_about_dialog()

                about_action.triggered.connect(on_about_clicked)
                logger.info("成功添加PyQt6菜单栏")
            else:
                raise RuntimeError("窗口不支持菜单栏")

        except ImportError as e:
            raise ImportError(f"PyQt6依赖缺失: {e}. 请确保已正确安装PyQt6")
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            logger.error("添加菜单栏失败: %s", e)
            raise RuntimeError(f"菜单栏初始化失败: {e}") from e

    def _open_file_dialog(self):
        """打开文件对话框，允许用户选择数据文件"""
        logger.info("=== _open_file_dialog方法开始执行 ===")
        try:
            logger.info("尝试打开文件对话框，选择数据目录")

            data_dir = None

            logger.info("尝试使用Qt文件对话框")
            try:
                data_dir = QFileDialog.getExistingDirectory(
                    None,
                    "选择数据目录",
                    self.strPltPath or ".",
                    QFileDialog.Option.ShowDirsOnly
                )
                logger.info("使用Qt文件对话框成功，返回值: %s", data_dir)
            except (ImportError, AttributeError, TypeError, RuntimeError) as qt_error:
                logger.error("Qt文件对话框失败: %s", qt_error)

            if data_dir:
                logger.info("用户选择的数据目录: %s", data_dir)
                self.set_data_path(data_dir)
                success = self.load_data()
                if success:
                    logger.info("数据加载成功，重新绘制图表")
                    self._cleanup_matplotlib_state()
                    if self.current_fig is not None:
                        plt.close(self.current_fig)
                        self.current_fig = None
                    self.plt_figure()
                else:
                    logger.error("数据加载失败，无法显示图表")
        except (AttributeError, TypeError, ValueError, OSError, RuntimeError) as e:
            logger.error("打开文件对话框时出错: %s", str(e))
            traceback.print_exc()

    def _show_about_dialog(self):
        """显示About对话框"""
        try:
            try:
                current_time = datetime.datetime.now().strftime("%Y")
            except (ImportError, OSError, ValueError) as e:
                logger.warning("获取当前年份失败: %s", e)
                current_time = "2024"

            try:
                version_obj = Version()
                version_info = f"v{version_obj.version}"
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning("无法获取版本信息，使用默认版本: %s", e)
                version_info = "v2.0.0"

            about_text = f"""Battery Analysis Tool
版本: {version_info}

电池测试数据可视化分析应用
支持多种数据格式导入与图表生成

功能特点:
• 支持CSV文件数据导入
• 交互式图表显示和操作
• 数据过滤和未过滤切换
• 电池选择和通道控制
• 悬停显示详细信息

开发者: Ewin电池分析团队
版权: © {current_time} MIT License

感谢使用Battery Analysis Tool!"""

            msg_box = QMessageBox()
            msg_box.setWindowTitle("About")
            msg_box.setText(about_text)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()

            logger.info("About对话框显示完成")
        except (AttributeError, TypeError, ValueError, OSError, RuntimeError) as e:
            logger.error("显示About对话框失败: %s", e)
            try:
                version_obj = Version()
                fallback_version = f"v{version_obj.version}"
            except (ImportError, AttributeError, TypeError):
                fallback_version = "v2.1.2"
            print(f"Battery Analysis Tool {fallback_version}\n开发者: Ewin电池分析团队")

    def _close_viewer(self):
        """关闭viewer窗口"""
        try:
            logger.info("文件操作按钮：Exit被点击，关闭visualizer窗口")
            if self.current_fig is not None:
                plt.close(self.current_fig)
                self.current_fig = None
                logger.info("已关闭visualizer窗口")
            else:
                logger.warning("当前没有打开的visualizer窗口")
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.error("关闭viewer窗口时出错: %s", e)

    def __del__(self):
        """析构函数，确保在对象销毁时释放所有资源"""
        try:
            if hasattr(self, 'current_fig') and self.current_fig is not None:
                plt.close(self.current_fig)
                self.current_fig = None
                logger.info("析构函数：关闭图表窗口")

            if hasattr(self, '_cleanup_matplotlib_state'):
                self._cleanup_matplotlib_state()
                logger.info("析构函数：清理Matplotlib状态")

            if hasattr(self, 'listPlt'):
                try:
                    for c in range(len(self.listPlt)):
                        if len(self.listPlt[c]) >= 4:
                            self.listPlt[c][0].clear()
                            self.listPlt[c][1].clear()
                            self.listPlt[c][2].clear()
                            self.listPlt[c][3].clear()
                    logger.info("析构函数：释放数据资源")
                except Exception as e:
                    logger.error("析构函数：释放数据资源时出错: %s", e)

            logger.info("BatteryChartViewer对象已销毁，资源已释放")
        except Exception as e:
            logger.error("析构函数执行异常: %s", e)
