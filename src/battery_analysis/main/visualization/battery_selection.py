"""电池通道选择控件（图内按钮列 + Qt 复选框列表）

从 interaction_controls.py 拆出（大文件拆分重构）。
"""

import logging

from battery_analysis.main.visualization.interaction_utils import _battery_line_indices

logger = logging.getLogger(__name__)


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from battery_analysis.main.visualization.interaction_contract import (
        BatteryChoice,
        ButtonState,
        ChartInteractionHost,
    )


class BatterySelectionMixin:
    """电池选择控件（依赖 ButtonFactoryMixin 的 _create_modern_button / _battery_name_sort_key）"""

    def _add_battery_selection_buttons(
        self: ChartInteractionHost, fig, check_filter, lines_unfiltered, lines_filtered
    ):
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
        self: ChartInteractionHost,
        fig,
        rect,
        start_idx,
        end_idx,
        check_filter,
        lines_unfiltered,
        lines_filtered,
    ):
        """创建电池选择现代化按钮"""
        ax_buttons = fig.add_axes(rect)
        ax_buttons.set_xlim(0, 1)
        ax_buttons.set_ylim(0, 1)
        ax_buttons.axis("off")
        ax_buttons.invert_yaxis = False

        battery_info: list[BatteryChoice] = []
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
        index_to_state: dict[int, ButtonState] = {}

        def toggle_battery_visibility(battery_idx, button_state=None):
            try:
                logger.debug("Toggling visibility of battery %s", battery_idx)

                if battery_info[battery_idx - start_idx].get("is_none", False):
                    return

                is_filtered = (
                    self.filter_button_state["active"]
                    if hasattr(self, "filter_button_state") and self.filter_button_state is not None
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

        def make_toggle_callback(index: int):
            def on_click():
                toggle_battery_visibility(index)

            return on_click

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
                make_toggle_callback(battery["index"]),
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

    def create_battery_checkboxes(
        self: ChartInteractionHost,
        parent_widget,
        fig,
        lines_unfiltered,
        lines_filtered,
        check_filter,
    ):
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
        from PyQt6.QtWidgets import QCheckBox, QFrame, QScrollArea, QVBoxLayout, QWidget

        # 创建滚动区域
        scroll_area = QScrollArea(parent_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        battery_checkboxes = []

        # 获取电池信息并排序
        battery_info: list[BatteryChoice] = []
        for i in range(self.intBatteryNum):
            battery_info.append(
                {
                    "name": self.listBatteryNameSplit[i],
                    "index": i,
                    "initial_state": True,
                    "is_none": False,
                }
            )

        # 按电池名称数字正序排列
        battery_info.sort(key=lambda x: self._battery_name_sort_key(x["name"]))

        for battery in battery_info:
            checkbox = QCheckBox(
                battery["name"][:12] + "..." if len(battery["name"]) > 12 else battery["name"],
                content_widget,
            )
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

        logger.info(
            "Battery checkboxes created successfully (%d batteries)", len(battery_checkboxes)
        )
        return scroll_area, battery_checkboxes
