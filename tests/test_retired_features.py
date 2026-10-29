"""Regression gates for removing disconnected/placeholder feature chains."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow

from battery_analysis.main.initialization.steps.command_manager_initialization_step import (
    CommandManagerInitializationStep,
)
from battery_analysis.main.initialization.steps.language_initialization_step import (
    LanguageInitializationStep,
)
from battery_analysis.main.managers.command_manager import CommandManager
from battery_analysis.main.managers.initialization_manager import InitializationManager
from battery_analysis.main.services import service_container
from battery_analysis.main.ui_builder import UIBuilder
from battery_analysis.main.ui_components.menu_manager import MenuManager
from battery_analysis.main.utils.signal_connector import SignalConnector
from battery_analysis.utils.exceptions import BatteryAnalysisException, ConfigException
from scripts.build import BuildManager

RETIRED_ACTIONS = {
    "actionNew", "actionOpen", "actionSave", "actionSave_As", "actionExport_Report",
    "actionUndo", "actionRedo", "actionCalculate_Battery", "actionGenerate_Report",
    "actionBatch_Processing",
}


@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def menu_window(application):
    window = QMainWindow()
    builder = UIBuilder(window)
    builder.create_actions()
    builder.create_menus()
    window.analysis_runner = Mock()
    CommandManager(window)
    for name in (
        "dialog_manager", "help_manager", "visualization_manager", "theme_manager",
        "copy_selected_text", "paste_text", "cut_selected_text", "show_ndax_converter",
        "show_config_dialog",
    ):
        setattr(window, name, Mock())
    window.menu_manager = MenuManager(window)
    window.menu_manager.setup_menu_shortcuts()
    window.menu_manager.connect_menu_actions()
    yield window
    window.close()


def test_retired_actions_are_not_constructed_or_given_shortcuts(menu_window):
    created = {action.objectName() for action in menu_window.findChildren(QAction)}
    assert not created.intersection(RETIRED_ACTIONS)
    for name in RETIRED_ACTIONS:
        assert not hasattr(menu_window, name)


def test_analysis_menu_still_runs_the_real_analysis(menu_window):
    menu_window.actionAnalyze_Data.trigger()
    menu_window.analysis_runner.run_analysis.assert_called_once_with()


def test_converter_and_configuration_menus_remain_available(menu_window):
    menu_window.actionNdaxConverter.trigger()
    menu_window.show_ndax_converter.assert_called_once()
    # Config is disabled until the existing initialization pipeline enables it.
    menu_window.actionConfiguration.setEnabled(True)
    menu_window.actionConfiguration.trigger()
    menu_window.show_config_dialog.assert_called_once()


def test_services_create_only_live_nodes_and_keep_controller_dependencies(application, monkeypatch):
    container = service_container.ServiceContainer()
    monkeypatch.setattr(service_container, "_global_container", container)
    expected = {"config", "environment", "file", "main_controller", "file_controller"}
    assert set(service_container.Services.__dataclass_fields__) == expected
    for name in expected:
        assert container.get(name) is not None
    assert container.get("validation") is None
    assert container.get("validation_controller") is None
    assert container.get("nonexistent") is None


def test_command_initialization_depends_only_on_analysis_runner():
    step = CommandManagerInitializationStep()
    assert not step.can_execute(SimpleNamespace())
    window = SimpleNamespace(analysis_runner=Mock())
    assert step.can_execute(window)
    assert step.execute(window)
    assert window.run_analysis_command.execute()
    window.analysis_runner.run_analysis.assert_called_once_with()


def test_language_initialization_is_not_skipped_without_presenter(monkeypatch):
    language = SimpleNamespace(language_changed=Mock())
    monkeypatch.setattr(
        "battery_analysis.main.initialization.steps.language_initialization_step.get_language_manager",
        lambda: language,
    )
    window = SimpleNamespace(
        _on_language_changed=Mock(),
        _initialize_environment_info=Mock(),
        _ensure_env_info_keys=Mock(),
    )
    step = LanguageInitializationStep()
    assert step.can_execute(window)
    assert step.execute(window)
    language.language_changed.connect.assert_called_once_with(window._on_language_changed)
    window._initialize_environment_info.assert_called_once_with()
    window._ensure_env_info_keys.assert_called_once_with()


def test_initialization_pipeline_contains_live_steps_only():
    manager = InitializationManager(SimpleNamespace())
    assert manager.get_total_steps() == 11
    assert manager._orchestrator.get_step("presenters") is None
    assert manager._orchestrator.get_step("command_manager") is not None
    assert manager._orchestrator.get_step("language") is not None


def test_signal_connector_requests_only_live_controllers():
    requested = []
    window = SimpleNamespace(_get_controller=lambda name: requested.append(name))
    SignalConnector(window).connect_controllers()
    assert requested == ["main_controller", "file_controller"]


def test_packaging_does_not_force_import_of_retired_ui():
    manager = BuildManager.__new__(BuildManager)
    manager.project_root = Path(__file__).resolve().parents[1]
    for app in manager._get_apps_config():
        assert "battery_analysis.ui.ui_main_window" not in app["hidden_imports"]
        assert "battery_analysis.main.battery_chart_viewer" in app["hidden_imports"]


def test_remaining_exception_contracts_are_unchanged():
    assert str(ConfigException("invalid")) == "[500] Configuration error: invalid"
    error = BatteryAnalysisException("read failed", 400)
    assert error.message == "read failed"
    assert error.error_code == 400
    assert str(error) == "[400] read failed"
