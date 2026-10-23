"""Viewer 菜单与原生 Qt 工具栏的行为验收，不仅检查信号连接。"""

import xml.etree.ElementTree as ET
from unittest.mock import Mock

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.backend_bases import MouseEvent
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (
    QApplication,
    QDialogButtonBox,
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
)

from battery_analysis.main.battery_chart_viewer import BatteryChartViewer
from battery_analysis.main.factories.battery_chart_viewer_wrapper import BatteryChartViewerWrapper
from battery_analysis.reports.info_csv_writer import write_info_csv, write_info_json


@pytest.fixture
def viewer(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Mock()
    config.get_config_value.side_effect = lambda key, default=None: default
    monkeypatch.setattr(
        BatteryChartViewer, "_load_config_file",
        lambda self: setattr(self, "_config_service", config),
    )
    monkeypatch.setattr(plt, "pause", lambda *args: None)
    write_info_csv(
        str(tmp_path), ["Battery_1"], [15], [[[]]], [[[10, 11, 12]]], [[[3, 2.99, 2.98]]]
    )
    write_info_json(str(tmp_path), [], current_levels=[15])
    wrapper = BatteryChartViewerWrapper()
    assert wrapper.show_figure(data_path=str(tmp_path))
    instance = wrapper._viewer
    yield instance
    for widget in app.topLevelWidgets():
        if widget.objectName() == "SubplotTool" or widget.windowTitle() == "Figure options":
            widget.close()
    plt.close("all")
    app.processEvents()


def menu_action(viewer, menu, text):
    menubar = viewer.current_fig.canvas.manager.window.menuBar()
    submenu = next(action.menu() for action in menubar.actions() if action.text() == menu)
    return next(action for action in submenu.actions() if action.text() == text)


def mouse(fig, name, point, button=None, step=0):
    event = MouseEvent(name, fig.canvas, *point, button=button, step=step)
    fig.canvas.callbacks.process(name, event)


def limits(ax):
    return np.array([ax.get_xlim(), ax.get_ylim()])


def test_all_expected_toolbar_actions_are_present_and_enabled(viewer):
    toolbar = viewer.current_fig.canvas.toolbar
    expected = {"home", "back", "forward", "pan", "zoom", "configure_subplots", "edit_parameters", "save_figure"}
    assert expected <= toolbar._actions.keys()
    for name in expected - {"back", "forward"}:
        assert toolbar._actions[name].isEnabled()
    assert not toolbar._actions["back"].isEnabled()
    assert not toolbar._actions["forward"].isEnabled()


def test_home_back_forward_actions_restore_custom_navigation(viewer):
    fig = viewer.current_fig
    ax = fig.axes[0]
    actions = fig.canvas.toolbar._actions
    initial = limits(ax)
    center = ax.bbox.get_points().mean(axis=0)
    mouse(fig, "scroll_event", center, step=1)
    zoomed = limits(ax)
    assert actions["back"].isEnabled()
    actions["back"].trigger()
    assert limits(ax) == pytest.approx(initial)
    assert actions["forward"].isEnabled()
    actions["forward"].trigger()
    assert limits(ax) == pytest.approx(zoomed)
    actions["home"].trigger()
    assert limits(ax) == pytest.approx(initial)


def test_pan_action_performs_native_drag_and_exits_cleanly(viewer):
    fig = viewer.current_fig
    ax = fig.axes[0]
    action = fig.canvas.toolbar._actions["pan"]
    before = limits(ax)
    start = ax.bbox.get_points().mean(axis=0)
    end = start + np.array([40, 25])
    action.trigger()
    assert action.isChecked()
    mouse(fig, "button_press_event", start, button=1)
    mouse(fig, "motion_notify_event", end, button=1)
    mouse(fig, "button_release_event", end, button=1)
    after = limits(ax)
    assert (after[:, 0] < before[:, 0]).all()
    assert np.diff(after) == pytest.approx(np.diff(before))
    assert fig.canvas._battery_navigation.drag is None
    action.trigger()
    assert not action.isChecked()
    assert not fig.canvas.widgetlock.locked()
    mouse(fig, "scroll_event", start, step=1)
    assert np.abs(np.diff(limits(ax))) == pytest.approx(np.abs(np.diff(after)) / 1.2)


def test_zoom_action_performs_native_rectangle_zoom(viewer):
    fig = viewer.current_fig
    ax = fig.axes[0]
    actions = fig.canvas.toolbar._actions
    before = limits(ax)
    bbox = ax.bbox
    start = (bbox.x0 + bbox.width * .2, bbox.y0 + bbox.height * .2)
    end = (bbox.x0 + bbox.width * .8, bbox.y0 + bbox.height * .8)
    actions["zoom"].trigger()
    assert actions["zoom"].isChecked()
    mouse(fig, "button_press_event", start, button=1)
    mouse(fig, "motion_notify_event", end, button=1)
    mouse(fig, "button_release_event", end, button=1)
    assert (np.abs(np.diff(limits(ax))) < np.abs(np.diff(before))).all()
    actions["home"].trigger()
    assert limits(ax) == pytest.approx(before)
    actions["zoom"].trigger()
    assert not actions["zoom"].isChecked()
    assert not fig.canvas.widgetlock.locked()


def test_subplot_dialog_edits_resets_exports_and_closes(viewer):
    fig = viewer.current_fig
    toolbar = fig.canvas.toolbar
    before = fig.axes[0].get_position().bounds
    toolbar._actions["configure_subplots"].trigger()
    dialog = toolbar._subplot_dialog
    assert dialog.isVisible()
    old_left = dialog._spinboxes["left"].value()
    dialog._spinboxes["left"].setValue(old_left + .04)
    assert fig.subplotpars.left == pytest.approx(old_left + .04)
    assert fig.axes[0].get_position().x0 > before[0]
    buttons = {button.text(): button for button in dialog.findChildren(QPushButton)}
    buttons["Export values"].click()
    exported = dialog._export_values_dialog
    assert exported.isVisible()
    assert "left=" in exported.findChild(QPlainTextEdit).toPlainText()
    exported.close()
    buttons["Tight layout"].click()
    assert 0 <= fig.subplotpars.left < fig.subplotpars.right <= 1
    buttons["Reset"].click()
    assert fig.subplotpars.left == pytest.approx(old_left)
    buttons["Close"].click()
    assert not dialog.isVisible()
    toolbar._actions["configure_subplots"].trigger()
    assert toolbar._subplot_dialog.isVisible()
    plt.close(fig)
    assert not dialog.isVisible()


def test_customize_dialog_applies_axis_and_curve_changes(viewer, monkeypatch):
    fig = viewer.current_fig
    toolbar = fig.canvas.toolbar
    ax = fig.axes[0]
    # Viewer 的按钮也使用辅助 Axes；在真实选择框中接受默认主图。
    selected = []
    original_select = QInputDialog.getItem

    def select_axes(parent, title, label, items, *args):
        selected.extend(items)
        QTimer.singleShot(0, lambda: QApplication.activeModalWidget().accept())
        return original_select(parent, title, label, items, *args)

    monkeypatch.setattr(QInputDialog, "getItem", select_axes)
    toolbar._actions["edit_parameters"].trigger()
    assert selected[0] == ax.get_title()
    dialog = toolbar._fedit_dialog
    assert dialog.isVisible()
    general = dialog.formwidget.widgetlist[0]
    fields = {
        (label, index): field
        for index, ((label, _), field) in enumerate(zip(general.data, general.widgets))
    }
    fields[("Title", 0)].setText("Edited battery chart")
    # 首个 Min/Max 是 X 轴。
    x_min = next(field for (label, index), field in fields.items() if label == "Min")
    x_max = next(field for (label, index), field in fields.items() if label == "Max")
    x_min.setText("20")
    x_max.setText("300")
    curves = dialog.formwidget.widgetlist[1].widgetlist[0]
    width = next(field for (label, _), field in zip(curves.data, curves.widgets) if label == "Width")
    width.setText("2.5")
    dialog.bbox.button(QDialogButtonBox.StandardButton.Apply).click()
    assert ax.get_title() == "Edited battery chart"
    assert ax.get_xlim() == pytest.approx((20, 300))
    assert ax.lines[0].get_linewidth() == pytest.approx(2.5)
    dialog.bbox.button(QDialogButtonBox.StandardButton.Ok).click()
    assert not dialog.isVisible()


def test_customize_axis_selection_cancel_keeps_chart_unchanged(viewer, monkeypatch):
    fig = viewer.current_fig
    toolbar = fig.canvas.toolbar
    before = limits(fig.axes[0])
    monkeypatch.setattr(QInputDialog, "getItem", lambda *args: ("", False))
    toolbar._actions["edit_parameters"].trigger()
    assert not hasattr(toolbar, "_fedit_dialog")
    assert limits(fig.axes[0]) == pytest.approx(before)


@pytest.mark.parametrize("extension", ["png", "svg", "pdf"])
def test_save_action_writes_readable_output(viewer, tmp_path, monkeypatch, extension):
    path = tmp_path / f"battery-chart.{extension}"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: (str(path), ""))
    viewer.current_fig.canvas.toolbar._actions["save_figure"].trigger()
    assert path.stat().st_size > 100
    if extension == "png":
        image = QImage(str(path))
        assert not image.isNull()
        assert image.width() > 0 and image.height() > 0
    elif extension == "svg":
        root = ET.parse(path).getroot()
        assert root.tag.endswith("svg")
        assert root.findall(".//{http://www.w3.org/2000/svg}path")
    else:
        assert path.read_bytes().startswith(b"%PDF-")


def test_save_action_uses_real_qt_file_dialog(viewer, tmp_path, monkeypatch):
    path = tmp_path / "电池图表.png"
    original_save_dialog = QFileDialog.getSaveFileName
    observed = []

    def choose_file(*args, **kwargs):
        # 离屏环境只使用 Qt 对话框，不弹出宿主 Windows 的原生文件窗口。
        kwargs["options"] = QFileDialog.Option.DontUseNativeDialog

        def accept_file():
            dialog = QApplication.activeModalWidget()
            observed.append(type(dialog))
            dialog.selectFile(str(path))
            dialog.accept()

        QTimer.singleShot(0, accept_file)
        return original_save_dialog(*args, **kwargs)

    monkeypatch.setattr(QFileDialog, "getSaveFileName", choose_file)
    viewer.current_fig.canvas.toolbar._actions["save_figure"].trigger()
    assert observed == [QFileDialog]
    assert not QImage(str(path)).isNull()


def test_save_action_cancel_and_write_failure_are_handled(viewer, tmp_path, monkeypatch):
    action = viewer.current_fig.canvas.toolbar._actions["save_figure"]
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("", ""))
    save = Mock(wraps=viewer.current_fig.savefig)
    monkeypatch.setattr(viewer.current_fig, "savefig", save)
    action.trigger()
    save.assert_not_called()
    path = tmp_path / "missing-parent" / "chart.png"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: (str(path), ""))
    error = Mock()
    monkeypatch.setattr(QMessageBox, "critical", error)
    action.trigger()
    error.assert_called_once()
    assert not path.exists()


def test_about_action_opens_real_message_box_and_accepts(viewer, monkeypatch):
    original_exec = QMessageBox.exec
    observed = []

    def accept_message(box):
        observed.append((box.windowTitle(), box.text(), box.standardButtons()))
        QTimer.singleShot(0, box.accept)
        return original_exec(box)

    monkeypatch.setattr(QMessageBox, "exec", accept_message)
    fig = viewer.current_fig
    menu_action(viewer, "Help", "About").trigger()
    assert len(observed) == 1
    assert observed[0][0] == "About"
    assert "Battery Analysis Tool" in observed[0][1]
    assert "Version:" in observed[0][1]
    assert observed[0][2] == QMessageBox.StandardButton.Ok
    assert viewer.current_fig is fig and plt.fignum_exists(fig.number)


def test_exit_action_closes_figure_and_disconnects_navigation(viewer):
    fig = viewer.current_fig
    nav = fig.canvas._battery_navigation
    menu_action(viewer, "File", "Exit").trigger()
    assert viewer.current_fig is None
    assert not plt.fignum_exists(fig.number)
    assert not nav.cids


def test_open_action_cancel_keeps_existing_chart(viewer, monkeypatch):
    fig = viewer.current_fig
    before = limits(fig.axes[0])
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args: "")
    menu_action(viewer, "File", "Open").trigger()
    assert viewer.current_fig is fig
    assert limits(fig.axes[0]) == pytest.approx(before)


def test_open_action_invalid_data_keeps_window_and_warns(viewer, tmp_path, monkeypatch):
    fig = viewer.current_fig
    empty = tmp_path / "empty-data"
    empty.mkdir()
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args: str(empty))
    warning = Mock()
    monkeypatch.setattr(QMessageBox, "warning", warning)
    menu_action(viewer, "File", "Open").trigger()
    warning.assert_called_once()
    assert viewer.current_fig is fig and plt.fignum_exists(fig.number)
