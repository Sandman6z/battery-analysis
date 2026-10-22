"""交互 Mixin 对最终查看器的结构化要求，不引入运行时循环依赖。"""

from collections.abc import Callable
from typing import Any, Protocol, TypedDict


class BatteryChoice(TypedDict):
    name: str
    index: int
    initial_state: bool
    is_none: bool

from matplotlib.figure import Figure
from PyQt6.QtWidgets import QCheckBox

# Matplotlib 的按钮状态同时持有 artist、回调状态和尺寸。
ButtonState = dict[str, Any]


class ChartInteractionHost(Protocol):
    """由 BatteryChartViewer 的数据、绘图、样式和交互组件共同实现。"""

    intBatteryNum: int
    intCurrentLevelNum: int
    listBatteryNameSplit: list[str]
    listAxis: list[float]
    maxXaxis: float
    strPltName: str
    strPltPath: str
    current_fig: Figure | None
    battery_button_states: dict[str, list[tuple[int, ButtonState]]]
    battery_checkboxes: list[tuple[int, QCheckBox]]
    file_button_states: list[ButtonState] | None
    filter_button_state: ButtonState | None
    filter_checkbox: QCheckBox
    _kdtree_cache: dict

    def _get_button_pad(self, width: float, height: float) -> float: ...
    def _battery_name_sort_key(self, name: str) -> tuple[float, float]: ...
    def _create_modern_button(
        self, ax, x, y, width, height, text, callback: Callable[[], object],
        is_toggle: bool = False, initial_state: bool = False,
    ) -> ButtonState | None: ...
    def _create_modern_toggle_group(
        self, ax, x, y, width, height, buttons_config,
    ) -> list[ButtonState] | None: ...
    def _create_battery_check_buttons(
        self, fig, rect, start_idx, end_idx, check_filter, lines_unfiltered, lines_filtered,
    ) -> list[tuple[int, ButtonState]]: ...
    def _apply_filter_mode(
        self, fig, ax, show_filtered, lines_unfiltered, lines_filtered,
        title_fontdict, axis_fontdict,
    ) -> None: ...
    def _add_hover_functionality(
        self, fig, ax, lines_filtered, lines_unfiltered, check_filter,
    ) -> None: ...
    def _build_kdtree_index(self, lines): ...
    def _find_nearest_point_kdtree(self, kdtree, points_data, x, y, max_dist): ...
    def _update_button_style(self, state, pressed=False, hover=False) -> None: ...
    def _reset_button_after_delay(self, state, delay=0.1) -> None: ...
    def _apply_window_modern_style(self, window) -> None: ...
    def _apply_menubar_style(self, menubar) -> None: ...
    def _apply_menu_style(self, menu) -> None: ...
    def _cleanup_matplotlib_state(self) -> None: ...
    def _open_file_dialog(self) -> None: ...
    def _show_about_dialog(self) -> None: ...
    def _close_viewer(self) -> None: ...
    def set_data_path(self, path: str) -> None: ...
    def load_data(self) -> bool: ...
    def plt_figure(self) -> bool: ...
