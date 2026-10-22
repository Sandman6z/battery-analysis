"""过滤/未过滤切换控件（图内按钮 + Qt 复选框两种形态）

从 interaction_controls.py 拆出（大文件拆分重构）。
"""

import logging

from battery_analysis.main.visualization.interaction_utils import _battery_line_indices

logger = logging.getLogger(__name__)


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from battery_analysis.main.visualization.interaction_contract import (
        ButtonState,
        ChartInteractionHost,
    )


class FilterControlsMixin:
    """过滤切换控件（依赖 ButtonFactoryMixin 的 _create_modern_button）"""

    def _apply_filter_mode(
        self: ChartInteractionHost,
        fig,
        ax,
        show_filtered,
        lines_unfiltered,
        lines_filtered,
        title_fontdict,
        axis_fontdict,
    ):
        """应用过滤/未过滤状态（matplotlib 按钮与 QCheckBox 两种控件共用）

        Args:
            show_filtered: True 显示过滤后曲线，False 显示未过滤曲线
        """
        prefix = "Filtered" if show_filtered else "Unfiltered"
        manager = getattr(fig.canvas, "manager", None)
        if manager is not None and hasattr(manager, "window"):
            manager.window.setWindowTitle(f"{prefix} {self.strPltName}")
        ax.set_title(f"{prefix} {self.strPltName}", fontdict=title_fontdict)
        ax.set_ylabel(f"{prefix} Battery Load Voltage [V]", fontdict=axis_fontdict)

        # 可见性来源组（按其电池分组决定谁可见）与目标组
        source = lines_unfiltered if show_filtered else lines_filtered
        target = lines_filtered if show_filtered else lines_unfiltered
        for i in range(min(len(source), len(target))):
            battery_index = i // self.intCurrentLevelNum
            battery_visible = any(
                source[j].get_visible()
                for j in _battery_line_indices(battery_index, self.intCurrentLevelNum)
                if j < len(source)
            )
            target[i].set_visible(battery_visible)
            source[i].set_visible(False)

        fig.canvas.draw_idle()

    def _add_filter_button(
        self: ChartInteractionHost,
        fig,
        ax,
        lines_unfiltered,
        lines_filtered,
        title_fontdict,
        axis_fontdict,
    ):
        """添加过滤/未过滤数据切换按钮"""
        try:
            ax_filter = fig.add_axes([0.001, 0.92, 0.12, 0.05])
            ax_filter.set_xlim(0, 1)
            ax_filter.set_ylim(0, 1)
            ax_filter.axis("off")

            is_filtered = {"value": True}
            button_state_ref: dict[str, ButtonState | None] = {"button_state": None}

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

                    self._apply_filter_mode(
                        fig,
                        ax,
                        is_filtered["value"],
                        lines_unfiltered,
                        lines_filtered,
                        title_fontdict,
                        axis_fontdict,
                    )
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
        self: ChartInteractionHost,
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
                # 与 hover/电池选择共享的过滤状态（此前漏更新，导致悬停永远扫 Filtered 曲线）
                self.filter_button_state["active"] = checked
                self._apply_filter_mode(
                    fig,
                    ax,
                    checked,
                    lines_unfiltered,
                    lines_filtered,
                    title_fontdict,
                    axis_fontdict,
                )
            except (AttributeError, TypeError, ValueError, IndexError) as e:
                logger.error("Error toggling filter mode: %s", e)

        checkbox.toggled.connect(on_filter_toggled)

        # 保存引用以便后续访问
        self.filter_checkbox = checkbox
        self.filter_button_state = {"active": True}  # 兼容旧代码

        logger.info("Filter checkbox created successfully")
        return checkbox
