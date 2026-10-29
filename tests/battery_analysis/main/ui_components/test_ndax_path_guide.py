"""Regression checks for the one-time NDAX folder introduction."""

import pytest
from PyQt6 import QtCore as QC
from PyQt6 import QtTest
from PyQt6 import QtWidgets as QW

from battery_analysis.i18n import get_current_locale, set_locale
from battery_analysis.main.ui_builder import UIBuilder
from battery_analysis.main.ui_components.ndax_path_guide import (
    GUIDE_SETTING_KEY,
    show_ndax_path_guide,
)


@pytest.fixture(scope="session")
def qapp():
    return QW.QApplication.instance() or QW.QApplication([])


@pytest.fixture
def guide_window(qapp, tmp_path):
    locale = get_current_locale()
    set_locale("en")
    window = QW.QMainWindow()
    UIBuilder(window).build_ui()
    window.show()
    qapp.processEvents()
    settings = QC.QSettings(str(tmp_path / "guide.ini"), QC.QSettings.Format.IniFormat)
    yield window, settings
    window.close()
    window.deleteLater()
    qapp.processEvents()
    set_locale(locale)


def test_dismissal_is_remembered_without_opening_folder(guide_window, qapp):
    window, settings = guide_window
    clicks = []
    window.pushButton_InputPath.clicked.connect(lambda: clicks.append(True))
    guide = show_ndax_path_guide(window.centralWidget(), window.pushButton_InputPath, settings)
    assert guide is not None
    assert not settings.value(GUIDE_SETTING_KEY, False, type=bool)
    assert not guide.mask().contains(guide.spotlight.center())
    guide.done_button.click()
    assert not guide.isVisible()
    assert clicks == []
    reloaded = QC.QSettings(settings.fileName(), QC.QSettings.Format.IniFormat)
    assert (
        show_ndax_path_guide(window.centralWidget(), window.pushButton_InputPath, reloaded) is None
    )


def test_real_open_button_still_works_and_dismisses_before_its_action(guide_window):
    window, settings = guide_window
    guide = show_ndax_path_guide(window.centralWidget(), window.pushButton_InputPath, settings)
    results = []
    window.pushButton_InputPath.clicked.connect(
        lambda: results.append((guide.isVisible(), settings.value(GUIDE_SETTING_KEY, type=bool)))
    )
    QtTest.QTest.mouseClick(window.pushButton_InputPath, QC.Qt.MouseButton.LeftButton)
    assert results == [(False, True)]


def test_escape_dismisses(guide_window, qapp):
    window, settings = guide_window
    guide = show_ndax_path_guide(window.centralWidget(), window.pushButton_InputPath, settings)
    qapp.processEvents()
    QtTest.QTest.keyClick(guide.done_button, QC.Qt.Key.Key_Escape)
    assert not guide.isVisible()
    assert settings.value(GUIDE_SETTING_KEY, type=bool)


@pytest.mark.parametrize("locale", ["en", "zh_CN"])
@pytest.mark.parametrize("size", [(720, 600), (1100, 800)])
def test_highlight_tracks_button_and_card_stays_inside_window(guide_window, qapp, locale, size):
    window, settings = guide_window
    set_locale(locale)
    guide = show_ndax_path_guide(window.centralWidget(), window.pushButton_InputPath, settings)
    window.resize(*size)
    qapp.processEvents()
    target = window.pushButton_InputPath
    assert guide.spotlight.topLeft() == target.mapTo(window.centralWidget(), QC.QPoint())
    assert guide.spotlight.topLeft() + guide.mapToGlobal(QC.QPoint()) == target.mapToGlobal(
        QC.QPoint()
    )
    assert guide.spotlight.size() == target.size()
    assert guide.rect().contains(guide.card.geometry())
    assert not guide.card.geometry().intersects(guide.spotlight)
    assert "Excel" in guide.description.text()
    assert guide.done_button.text() == ("知道了" if locale == "zh_CN" else "Got it")
    # Simply showing (or abandoning) the guide must not mark it complete.
    assert not settings.value(GUIDE_SETTING_KEY, False, type=bool)


def test_hidden_window_does_not_consume_introduction(guide_window):
    window, settings = guide_window
    window.hide()
    assert (
        show_ndax_path_guide(window.centralWidget(), window.pushButton_InputPath, settings) is None
    )
    assert not settings.contains(GUIDE_SETTING_KEY)
