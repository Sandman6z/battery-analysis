"""真实 Qt 画布上派发鼠标事件，验证导航范围及轴向不变量。"""

from types import SimpleNamespace
from unittest.mock import Mock

import matplotlib

matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.backend_bases import CloseEvent, MouseEvent
from matplotlib.ticker import AutoLocator
from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QApplication

from battery_analysis.main.visualization.filter_controls import FilterControlsMixin
from battery_analysis.main.visualization.hover_controls import HoverControlsMixin
from battery_analysis.main.visualization.navigation_controls import (
    install_navigation,
    navigation_active,
)


@pytest.fixture
def chart():
    app = QApplication.instance() or QApplication([])
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set(xlim=(10, 110), ylim=(2, 4))
    ax.plot([10, 110], [2, 4])
    fig.canvas.draw()
    nav = install_navigation(fig, ax)
    yield fig, ax, nav
    nav.disconnect()
    plt.close(fig)
    app.processEvents()


def dispatch(fig, name, point, button=None, step=0):
    event = MouseEvent(name, fig.canvas, *point, button=button, step=step)
    fig.canvas.callbacks.process(name, event)
    return event


def tick_point(fig, ax, direction):
    axis = ax.xaxis if direction == "x" else ax.yaxis
    boxes = [
        label.get_window_extent(fig.canvas.get_renderer())
        for label in axis.get_ticklabels() if label.get_visible() and label.get_text()
    ]
    bbox = boxes[len(boxes) // 2]
    return (bbox.x0 + bbox.x1) / 2, (bbox.y0 + bbox.y1) / 2


@pytest.mark.parametrize("direction", ["x", "y", "both"])
def test_drag_changes_only_target_axis_and_preserves_span(chart, direction):
    fig, ax, nav = chart
    point = tick_point(fig, ax, direction) if direction != "both" else ax.bbox.get_points().mean(axis=0)
    if direction != "both":
        assert MouseEvent("button_press_event", fig.canvas, *point).inaxes is None
    assert nav.region(MouseEvent("button_press_event", fig.canvas, *point)) == direction
    before = (ax.get_xlim(), ax.get_ylim())
    dispatch(fig, "button_press_event", point, button=1)
    assert navigation_active(fig.canvas)
    dispatch(fig, "motion_notify_event", (point[0] + 40, point[1] + 30), button=1)
    dispatch(fig, "button_release_event", (point[0] + 40, point[1] + 30), button=1)
    after = (ax.get_xlim(), ax.get_ylim())
    for index, axis in enumerate(("x", "y")):
        assert np.diff(after[index]) == pytest.approx(np.diff(before[index]))
        if direction in (axis, "both"):
            assert after[index][0] < before[index][0]
        else:
            assert after[index] == before[index]
    assert not navigation_active(fig.canvas)


@pytest.mark.parametrize("direction", ["x", "y", "both"])
def test_scroll_zooms_target_axis_around_mouse(chart, direction):
    fig, ax, nav = chart
    point = tick_point(fig, ax, direction) if direction != "both" else ax.bbox.get_points().mean(axis=0)
    event = MouseEvent("scroll_event", fig.canvas, *point, step=1)
    anchor = ax.transData.inverted().transform((event.x, event.y))
    before = (ax.get_xlim(), ax.get_ylim())
    fig.canvas.callbacks.process("scroll_event", event)
    after = (ax.get_xlim(), ax.get_ylim())
    for index, axis in enumerate(("x", "y")):
        if direction in (axis, "both"):
            expected = anchor[index] + (np.array(before[index]) - anchor[index]) / 1.2
            assert after[index] == pytest.approx(expected)
        else:
            assert after[index] == before[index]


def test_right_click_resets_and_history_can_go_back(chart):
    fig, ax, nav = chart
    point = ax.bbox.get_points().mean(axis=0)
    dispatch(fig, "scroll_event", point, step=1)
    zoomed = (ax.get_xlim(), ax.get_ylim())
    dispatch(fig, "button_press_event", point, button=3)
    assert (ax.get_xlim(), ax.get_ylim()) == nav.initial_limits
    fig.canvas.toolbar.back()
    assert ax.get_xlim() == pytest.approx(zoomed[0])
    assert ax.get_ylim() == pytest.approx(zoomed[1])


def test_repeated_scrolls_have_no_duplicate_history_entries(chart):
    fig, ax, nav = chart
    point = ax.bbox.get_points().mean(axis=0)
    dispatch(fig, "scroll_event", point, step=1)
    first = ax.get_xlim()
    dispatch(fig, "scroll_event", point, step=1)
    fig.canvas.toolbar.back()
    assert ax.get_xlim() == pytest.approx(first)
    fig.canvas.toolbar.back()
    assert ax.get_xlim() == pytest.approx(nav.initial_limits[0])


def test_toolbar_mode_blocks_custom_gestures(chart):
    fig, ax, nav = chart
    fig.canvas.toolbar.pan()
    before = (ax.get_xlim(), ax.get_ylim())
    point = tick_point(fig, ax, "x")
    dispatch(fig, "button_press_event", point, button=1)
    dispatch(fig, "motion_notify_event", (point[0] + 40, point[1]), button=1)
    dispatch(fig, "button_release_event", point, button=1)
    dispatch(fig, "scroll_event", point, step=1)
    dispatch(fig, "button_press_event", point, button=3)
    assert (ax.get_xlim(), ax.get_ylim()) == before
    assert nav.drag is None
    fig.canvas.toolbar.pan()


def test_auxiliary_axes_do_not_navigate(chart):
    fig, ax, nav = chart
    button_ax = fig.add_axes([0.01, 0.01, 0.08, 0.08])
    fig.canvas.draw()
    before = (ax.get_xlim(), ax.get_ylim())
    point = button_ax.bbox.get_points().mean(axis=0)
    dispatch(fig, "scroll_event", point, step=1)
    dispatch(fig, "button_press_event", point, button=1)
    assert nav.drag is None
    assert (ax.get_xlim(), ax.get_ylim()) == before


def test_drag_outside_release_and_focus_loss_clear_state(chart):
    fig, ax, nav = chart
    point = tick_point(fig, ax, "y")
    dispatch(fig, "button_press_event", point, button=1)
    dispatch(fig, "motion_notify_event", (-20, -20), button=1)
    dispatch(fig, "button_release_event", (-20, -20), button=1)
    assert nav.drag is None
    assert not fig.canvas.widgetlock.locked()
    dispatch(fig, "button_press_event", point, button=1)
    nav.eventFilter(fig.canvas, QEvent(QEvent.Type.FocusOut))
    assert nav.drag is None
    assert not fig.canvas.widgetlock.locked()


def test_reinstall_disconnects_old_callbacks_and_close_releases_lock(chart):
    fig, ax, old = chart
    nav = install_navigation(fig, ax)
    assert not old.cids
    point = tick_point(fig, ax, "x")
    before = ax.get_xlim()
    dispatch(fig, "scroll_event", point, step=1)
    assert np.diff(ax.get_xlim()) == pytest.approx(np.diff(before) / 1.2)
    dispatch(fig, "button_press_event", point, button=1)
    CloseEvent("close_event", fig.canvas)._process()
    assert nav.drag is None
    assert not nav.cids
    assert not fig.canvas.widgetlock.locked()


@pytest.mark.parametrize("method", ["_add_hover_functionality", "_add_hover_functionality_kdtree"])
def test_hover_does_not_scan_while_dragging_or_toolbar_active(chart, monkeypatch, method):
    fig, ax, nav = chart
    host = HoverControlsMixin()
    host.maxXaxis = 110
    host.listAxis = [10, 110, 2, 4]
    getattr(host, method)(fig, ax, ax.lines, [], {"active": True})
    scan = Mock()
    monkeypatch.setattr(
        "battery_analysis.main.visualization.hover_controls._find_nearest_point_linear", scan
    )
    point = ax.bbox.get_points().mean(axis=0)
    dispatch(fig, "button_press_event", point, button=1)
    dispatch(fig, "motion_notify_event", (point[0] + 10, point[1] + 10), button=1)
    scan.assert_not_called()
    dispatch(fig, "button_release_event", point, button=1)
    fig.canvas.toolbar.pan()
    dispatch(fig, "motion_notify_event", point)
    scan.assert_not_called()
    fig.canvas.toolbar.pan()


def test_filter_visibility_change_preserves_navigated_limits(chart):
    fig, ax, nav = chart
    raw = ax.plot([10, 110], [3, 3], visible=False)[0]
    filtered = ax.lines[0]
    dispatch(fig, "scroll_event", ax.bbox.get_points().mean(axis=0), step=1)
    limits = (ax.get_xlim(), ax.get_ylim())
    host = SimpleNamespace(strPltName="Test", intCurrentLevelNum=1)
    FilterControlsMixin._apply_filter_mode(host, fig, ax, False, [raw], [filtered], {}, {})
    assert (ax.get_xlim(), ax.get_ylim()) == limits
    assert raw.get_visible() and not filtered.get_visible()


def test_scroll_preserves_inverted_axis(chart):
    fig, ax, nav = chart
    ax.invert_xaxis()
    dispatch(fig, "scroll_event", ax.bbox.get_points().mean(axis=0), step=1)
    assert ax.get_xlim()[0] > ax.get_xlim()[1]
    assert np.diff(ax.get_xlim()) == pytest.approx([-100 / 1.2])
