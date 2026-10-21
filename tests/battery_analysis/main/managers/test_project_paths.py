"""Both input selectors must resolve one project without retaining stale paths."""

from unittest.mock import Mock, patch

import pytest
from PyQt6 import QtWidgets as QW

from battery_analysis.i18n import get_current_locale, set_locale
from battery_analysis.main.main_window import Main
from battery_analysis.main.managers.path_manager import PathManager
from battery_analysis.main.managers.test_profile_manager import TestProfileManager
from battery_analysis.main.ui_components.ui_manager import UIManager


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QW.QApplication.instance() or QW.QApplication([])
    yield app


@pytest.fixture(autouse=True)
def english_locale():
    previous = get_current_locale()
    assert set_locale("en")
    yield
    assert set_locale(previous)


@pytest.fixture
def window(tmp_path):
    with patch.object(Main, "_deferred_init", lambda self: None):
        window = Main()
    window.current_directory = str(tmp_path)
    window.path_manager = PathManager(window)
    window.test_profile_manager = TestProfileManager(window)
    yield window
    window.close()
    window.deleteLater()


def make_project(root, profiles=()):
    source = root / "1_ndax"
    source.mkdir(parents=True)
    (source / "sample.ndax").touch()
    for name in profiles:
        folder = root / "4_test profile"
        folder.mkdir(exist_ok=True)
        (folder / name).write_text("<root />", encoding="utf-8")
    return source


def choose_ndax(window, source):
    with patch.object(QW.QFileDialog, "getExistingDirectory", return_value=str(source)):
        window.path_manager.select_inputpath()


def choose_xml(window, profile):
    with patch.object(QW.QFileDialog, "getOpenFileName", return_value=(str(profile), "")):
        window.test_profile_manager.select_testprofile()


def assert_project(window, root, profile=""):
    assert window.lineEdit_InputPath.text() == str(root / "1_ndax")
    assert window.lineEdit_OutputPath.text() == str(root / "3_analysis results")
    assert (root / "3_analysis results").is_dir()
    assert window.lineEdit_TestProfile.text() == str(profile)
    assert window.current_directory == str(root)


@pytest.mark.parametrize("entry", ["ndax", "xml"])
def test_either_selector_resolves_project_before_refresh(window, tmp_path, entry):
    source = make_project(tmp_path, ["test.XML"])
    profile = tmp_path / "4_test profile" / "test.XML"
    refreshed = []
    window.sigSetVersion.connect(lambda: refreshed.append((
        window.lineEdit_InputPath.text(), window.lineEdit_OutputPath.text(),
        window.lineEdit_TestProfile.text(),
    )))
    if entry == "ndax":
        choose_ndax(window, source)
    else:
        choose_xml(window, profile)
    assert_project(window, tmp_path, profile)
    assert refreshed == [(str(source), str(tmp_path / "3_analysis results"), str(profile))]


def test_switching_project_without_profile_clears_old_profile(window, tmp_path):
    first = tmp_path / "first"
    choose_ndax(window, make_project(first, ["test.xml"]))
    second = tmp_path / "second"
    source = make_project(second)
    with patch.object(QW.QMessageBox, "question") as question:
        choose_ndax(window, source)
    assert_project(window, second)
    assert window.statusBar_BatteryAnalysis.currentMessage() == (
        "No sibling Test Profile was found (optional). Analysis will use the recipe embedded in the NDAX files."
    )
    question.assert_not_called()  # Existing first-run acknowledgement remains in AnalysisRunner.


@pytest.mark.parametrize("accept", [True, False])
def test_multiple_profiles_require_selection(window, tmp_path, accept):
    source = make_project(tmp_path, ["first.xml", "second.xml"])
    with patch.object(QW.QInputDialog, "getItem", return_value=("second.xml", accept)) as picker:
        choose_ndax(window, source)
    picker.assert_called_once()
    assert picker.call_args.args[1:3] == (
        "Select Test Profile",
        "Multiple XML files were found. Select a Test Profile for validation, or cancel to leave it empty:",
    )
    assert_project(window, tmp_path, tmp_path / "4_test profile" / "second.xml" if accept else "")


def test_invalid_automatic_profile_is_left_empty(window, tmp_path):
    source = make_project(tmp_path, ["broken.xml"])
    (tmp_path / "4_test profile" / "broken.xml").write_text("invalid xml")
    window.lineEdit_TestProfile.setText("old profile")
    with patch.object(QW.QMessageBox, "warning") as warning:
        choose_ndax(window, source)
    warning.assert_called_once()
    assert_project(window, tmp_path)


def test_xml_without_sibling_ndax_does_not_keep_previous_input(window, tmp_path):
    choose_ndax(window, make_project(tmp_path / "first"))
    other = tmp_path / "other"
    profile_dir = other / "4_test profile"
    profile_dir.mkdir(parents=True)
    profile = profile_dir / "test.xml"
    profile.write_text("<root />")
    with patch.object(QW.QMessageBox, "warning") as warning:
        choose_xml(window, profile)
    warning.assert_called_once()
    assert warning.call_args.args[1:] == (
        "Input Directory Not Found",
        f"The sibling NDAX directory was not found:\n{other / '1_ndax'}\nPlease check the project directory structure.",
    )
    assert window.lineEdit_InputPath.text() == ""
    assert window.lineEdit_TestProfile.text() == str(profile)
    assert window.lineEdit_OutputPath.text() == str(other / "3_analysis results")


def test_cancelling_either_selector_preserves_project(window, tmp_path):
    choose_ndax(window, make_project(tmp_path, ["test.xml"]))
    choose_ndax(window, "")
    choose_xml(window, "")
    assert_project(window, tmp_path, tmp_path / "4_test profile" / "test.xml")


def test_output_is_automatic_and_profile_is_really_optional(window):
    window.validation_manager = Mock()
    manager = UIManager(window)
    manager.init_lineedit()
    assert window.lineEdit_TestProfile.text() == ""
    assert window.lineEdit_TestProfile.placeholderText()
    assert window.lineEdit_OutputPath.isReadOnly()
    assert window.findChild(QW.QPushButton, "pushButton_OutputPath") is None
    assert not hasattr(window.path_manager, "select_outputpath")
    manager.setup_accessibility()
    manager.setup_tooltips()
    assert window.lineEdit_OutputPath.accessibleName()
    assert "3_analysis results" in window.lineEdit_OutputPath.toolTip()
