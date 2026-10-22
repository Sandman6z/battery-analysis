"""类型检查发现的真实边界问题，使用真实 Qt 控件回归。"""

from types import SimpleNamespace

import pytest
from PyQt6 import QtCore as QC
from PyQt6 import QtGui as QG
from PyQt6 import QtWidgets as QW

from battery_analysis.domain.entities.test_info import TestInfo as BatteryTestInfo
from battery_analysis.main.handlers.temperature_handler import TemperatureHandler
from battery_analysis.main.main_window import Main
from battery_analysis.main.ndax_converter_window import NdaxConverterWindow
from battery_analysis.main.ui_components.menu_manager import MenuManager
from battery_analysis.ui.frameworks.pyqt6_ui_framework import PyQt6UIFramework


@pytest.fixture(scope="session")
def application():
    return QW.QApplication.instance() or QW.QApplication([])


def test_progress_dialog_uses_window_modality(application):
    parent = QW.QWidget()
    dialog = PyQt6UIFramework().create_progress_dialog(parent)

    assert dialog.parentWidget() is parent
    assert dialog.windowModality() == QC.Qt.WindowModality.WindowModal
    dialog.close()
    parent.close()


@pytest.mark.parametrize("checked", [False, True])
def test_statusbar_delegates_to_real_menu_manager(application, checked):
    statusbar = QW.QStatusBar()
    action = QG.QAction()
    action.setCheckable(True)
    action.setChecked(checked)
    window = SimpleNamespace(
        statusBar_BatteryAnalysis=statusbar,
        actionShow_Statusbar=action,
    )
    window.menu_manager = MenuManager(window)

    Main.toggle_statusbar(window)

    assert statusbar.isHidden() is not checked
    statusbar.close()


def test_test_info_normalizes_tuple_levels_to_lists():
    values = [""] * 19
    values[14] = (1.0, 5.0)
    values[15] = (2.0, 2.25)

    info = BatteryTestInfo.from_list(values)

    assert info.current_levels == [1.0, 5.0]
    assert info.voltage_levels == [2.0, 2.25]
    assert isinstance(info.current_levels, list)
    assert isinstance(info.voltage_levels, list)


@pytest.mark.parametrize("window_class", [Main, NdaxConverterWindow])
def test_close_event_tolerates_missing_event(window_class):
    window_class.closeEvent(SimpleNamespace(), None)


def test_temperature_value_requires_a_window():
    with pytest.raises(RuntimeError, match="requires a main window"):
        TemperatureHandler().get_temperature_value()
