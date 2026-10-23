"""Regression checks for the compact main window and larger UI fonts."""

import os
from pathlib import Path

import pytest
from PyQt6 import QtGui as QG
from PyQt6 import QtWidgets as QW

from battery_analysis.i18n import get_current_locale, set_locale
from battery_analysis.main.ui_builder import UIBuilder
from battery_analysis.ui.styles.style_manager import get_theme_engine


@pytest.fixture(scope="session")
def qapp():
    app = QW.QApplication.instance() or QW.QApplication([])
    # Windows offscreen Qt does not discover system fonts automatically.
    if app.platformName() == "offscreen" and os.name == "nt":
        font_dir = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
        for filename in ("msyh.ttc", "segoeui.ttf"):
            assert QG.QFontDatabase.addApplicationFont(str(font_dir / filename)) >= 0
    return app


@pytest.fixture
def compact_window(qapp):
    previous_locale = get_current_locale()
    previous_style = qapp.styleSheet()
    engine = get_theme_engine()
    previous_theme = engine.get_theme_preference()
    set_locale("en")
    window = QW.QMainWindow()
    builder = UIBuilder(window)
    builder.build_ui()
    builder.create_actions()
    builder.create_menus()
    yield window
    window.close()
    window.deleteLater()
    engine.set_theme(previous_theme)
    qapp.setStyleSheet(previous_style)
    set_locale(previous_locale)


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_reporter_width_stays_twice_version_width(compact_window, qapp, theme):
    window = compact_window
    # The real application applies its theme after building the widgets.
    get_theme_engine().set_theme(theme)
    window.show()
    qapp.processEvents()
    assert window.width() == 720
    assert window.minimumWidth() == 720
    assert window.lineEdit_Version.width() == 100
    assert window.comboBox_ReportedBy.width() == 200
    assert window.comboBox_ReportedBy.x() > window.label_ReportedBy.x()
    assert window.comboBox_ReportedBy.geometry().right() < window.pushButton_Run.x()

    window.resize(1100, 750)
    qapp.processEvents()
    assert window.comboBox_ReportedBy.width() == 2 * window.lineEdit_Version.width()


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_main_labels_share_left_edge(compact_window, qapp, theme):
    get_theme_engine().set_theme(theme)
    compact_window.show()
    qapp.processEvents()
    for width in (720, 1100):
        compact_window.resize(width, 750)
        qapp.processEvents()
        labels = (
            compact_window.label_Version,
            compact_window.label_TesterLocation,
            compact_window.label_TestProfile,
        )
        left_edges = [label.mapTo(compact_window, label.rect().topLeft()).x() for label in labels]
        assert len(set(left_edges)) == 1, left_edges


def test_compact_layout_has_no_horizontal_overflow(compact_window, qapp):
    get_theme_engine().set_theme("light")
    compact_window.show()
    qapp.processEvents()
    scroll = compact_window.centralWidget().findChildren(QW.QScrollArea)[0]
    assert scroll.horizontalScrollBar().maximum() == 0
    for label in compact_window.centralWidget().findChildren(QW.QLabel):
        assert label.width() >= label.minimumSizeHint().width(), label.objectName()
    assert compact_window.label_Version.font().pixelSize() == 13
    assert compact_window.pushButton_Run.font().pixelSize() == 22
    assert compact_window.groupBox_BatteryConfig.font().pointSize() == 11
