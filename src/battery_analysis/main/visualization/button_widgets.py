"""matplotlib 图内按钮构件（现代化按钮 / 切换按钮组）

从 interaction_controls.py 拆出（大文件拆分重构）。
"""

import logging

from matplotlib.patches import FancyBboxPatch

from battery_analysis.main.visualization.styling import MODERN_BUTTON_STYLE

logger = logging.getLogger(__name__)


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from battery_analysis.main.visualization.interaction_contract import ChartInteractionHost


class ButtonFactoryMixin:
    """提供图内按钮的创建与状态管理（依赖 ChartStylingMixin 的 _update_button_style）"""

    def _get_button_pad(self: ChartInteractionHost, width, height):
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

    def _battery_name_sort_key(self: ChartInteractionHost, name):
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
        self: ChartInteractionHost,
        ax,
        x,
        y,
        width,
        height,
        text,
        callback,
        is_toggle=False,
        initial_state=False,
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

    def _create_modern_toggle_group(
        self: ChartInteractionHost, ax, x, y, width, height, buttons_config
    ):
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
