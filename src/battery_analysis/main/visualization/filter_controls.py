"""过滤/未过滤切换控件（图内按钮 + Qt 复选框两种形态）

从 interaction_controls.py 拆出（大文件拆分重构）。
"""

import logging

from battery_analysis.main.visualization.interaction_utils import _battery_line_indices

logger = logging.getLogger(__name__)


class FilterControlsMixin:
    """过滤切换控件（依赖 ButtonFactoryMixin 的 _create_modern_button）"""

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

    def create_filter_checkbox(
        self,
        parent_widget,
        fig,
        ax,
        lines_unfiltered,
        lines_filtered,
        title_fontdict,
        axis_fontdict,
    ):
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
