"""Startup/empty-chart regressions with real offscreen Qt canvases."""

import logging
from types import SimpleNamespace
from unittest.mock import Mock

import matplotlib.pyplot as plt
import pytest
from PyQt6.QtWidgets import QApplication, QWidget

from battery_analysis.main.battery_chart_viewer import BatteryChartViewer
from battery_analysis.main.factories.battery_chart_viewer_wrapper import BatteryChartViewerWrapper
from battery_analysis.utils.writers.info_csv_writer import write_info_csv, write_info_json


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def wrapper(qapp, monkeypatch):
    # Do not read/write the user's persistent configuration during GUI tests.
    config = Mock()
    config.get_config_value.side_effect = lambda key, default=None: default
    monkeypatch.setattr(
        BatteryChartViewer,
        "_load_config_file",
        lambda self: setattr(self, "_config_service", config),
    )
    monkeypatch.setattr(plt, "pause", lambda *args: None)
    instance = BatteryChartViewerWrapper()
    yield instance
    plt.close("all")
    qapp.processEvents()


def test_no_path_shows_neutral_chart_without_loading(wrapper, monkeypatch, caplog):
    load_data = Mock(wraps=wrapper._viewer.load_data)
    monkeypatch.setattr(wrapper._viewer, "load_data", load_data)
    with caplog.at_level(logging.INFO):
        assert wrapper.show_figure()
    load_data.assert_not_called()
    fig = wrapper._viewer.current_fig
    assert fig.axes[0].get_title() == "No Data"
    assert "Info_Image.csv" in " ".join(text.get_text() for text in fig.axes[0].texts)
    assert not [record for record in caplog.records if record.levelno >= logging.WARNING]
    menubar = fig.canvas.manager.window.menuBar()
    assert [action.text() for action in menubar.actions()] == ["File", "Help"]


@pytest.mark.parametrize("contents", [None, "", "bad,data\n", "\xff\xfe"])
def test_attempted_load_failure_still_shows_data_error(wrapper, tmp_path, contents, caplog):
    if contents is not None:
        (tmp_path / "Info_Image.csv").write_bytes(contents.encode("latin-1"))
    with caplog.at_level(logging.ERROR):
        assert wrapper.show_figure(data_path=str(tmp_path))
    assert wrapper._viewer.data_load_attempted
    assert not wrapper._viewer.loaded_data
    assert wrapper._viewer.current_fig.axes[0].get_title() == "Data Error"
    assert any(record.levelno >= logging.ERROR for record in caplog.records)


def test_requested_xml_without_results_is_not_startup_empty(wrapper, tmp_path):
    assert wrapper.show_figure(xml_path=str(tmp_path / "missing.xml"))
    assert wrapper._viewer.data_load_attempted
    assert wrapper._viewer.current_fig.axes[0].get_title() == "Data Error"


def test_valid_data_still_plots_after_failed_load(wrapper, tmp_path):
    assert not wrapper.load_data(str(tmp_path))
    write_info_csv(
        str(tmp_path), ["Battery_1"], [15], [[[]]], [[[10, 11, 12]]], [[[3, 2.99, 2.98]]]
    )
    write_info_json(str(tmp_path), [], current_levels=[15])
    assert wrapper.show_figure(data_path=str(tmp_path))
    viewer = wrapper._viewer
    assert viewer.loaded_data
    assert viewer.intBatteryNum == 1
    assert len(viewer.current_fig.axes[0].lines) == 2
    assert viewer.current_fig.axes[0].get_title().startswith("Filtered ")
    (tmp_path / "Info_Image.csv").unlink()
    assert not viewer.load_data()
    assert viewer.data_load_attempted
    assert not viewer.loaded_data
    assert viewer.intBatteryNum == 0


def test_empty_chart_open_menu_loads_selected_data(wrapper, tmp_path, monkeypatch):
    write_info_csv(
        str(tmp_path), ["Battery_1"], [15], [[[]]], [[[10, 11, 12]]], [[[3, 2.99, 2.98]]]
    )
    write_info_json(str(tmp_path), [], current_levels=[15])
    monkeypatch.setattr(
        "battery_analysis.main.visualization.viewer_controls.QFileDialog.getExistingDirectory",
        lambda *args: str(tmp_path),
    )
    assert wrapper.show_figure()
    empty_fig = wrapper._viewer.current_fig
    file_menu = empty_fig.canvas.manager.window.menuBar().actions()[0].menu()
    file_menu.actions()[0].trigger()
    viewer = wrapper._viewer
    assert viewer.loaded_data
    assert viewer.data_load_attempted
    assert viewer.current_fig is not empty_fig
    assert len(viewer.current_fig.axes[0].lines) == 2


def test_menu_creation_exception_does_not_break_empty_plot(wrapper, monkeypatch, caplog):
    from matplotlib.backends.backend_qt import MainWindow

    monkeypatch.setattr(MainWindow, "menuBar", Mock(side_effect=RuntimeError("Qt menu failed")))
    with caplog.at_level(logging.WARNING):
        assert wrapper.show_figure()
    assert wrapper._viewer.current_fig.axes[0].get_title() == "No Data"
    assert any("Qt menu failed" in record.message for record in caplog.records)
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


@pytest.mark.parametrize("attempt_load", [False, True])
def test_embedded_empty_and_failed_load_are_distinct(wrapper, tmp_path, attempt_load, caplog):
    parent = QWidget()
    with caplog.at_level(logging.INFO):
        result = wrapper.embed_to_widget(parent, data_path=str(tmp_path) if attempt_load else None)
    assert result is not None
    fig, canvas, filter_checkbox, scroll_area, checkboxes = result
    assert fig.axes[0].get_title() == ("Data Error" if attempt_load else "No Data")
    assert parent.layout().indexOf(canvas) >= 0
    assert (filter_checkbox, scroll_area, checkboxes) == (None, None, [])
    if not attempt_load:
        assert not [record for record in caplog.records if record.levelno >= logging.WARNING]
    parent.close()


def test_add_menu_bar_returns_true_on_success(wrapper):
    fig = plt.figure()
    assert wrapper._viewer._add_menu_bar(fig) is True
    assert [action.text() for action in fig.canvas.manager.window.menuBar().actions()] == [
        "File",
        "Help",
    ]


def test_add_menu_bar_returns_false_without_window(wrapper):
    fig = SimpleNamespace(canvas=SimpleNamespace(manager=None))
    assert wrapper._viewer._add_menu_bar(fig) is False


@pytest.mark.parametrize("attempt_load", [False, True])
@pytest.mark.parametrize("menu_result", [False, RuntimeError("menu unavailable")])
def test_menu_failure_keeps_empty_or_error_chart_visible(
    wrapper, tmp_path, monkeypatch, caplog, attempt_load, menu_result
):
    menu = (
        Mock(side_effect=menu_result)
        if isinstance(menu_result, Exception)
        else Mock(return_value=menu_result)
    )
    monkeypatch.setattr(wrapper._viewer, "_add_menu_bar", menu)
    with caplog.at_level(logging.WARNING):
        assert wrapper.show_figure(data_path=str(tmp_path) if attempt_load else None)
    fig = wrapper._viewer.current_fig
    assert fig is not None
    assert fig.axes[0].get_title() == ("Data Error" if attempt_load else "No Data")
    assert plt.fignum_exists(fig.number)
    assert any("menubar" in record.message.lower() for record in caplog.records)
    assert not any("Error displaying chart" in record.message for record in caplog.records)
