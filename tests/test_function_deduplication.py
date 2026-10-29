"""Behavioral regression checks for the function deduplication pass."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from battery_analysis.main.business_logic.data_processor import DataProcessor
from battery_analysis.main.business_logic.version_manager import VersionManager
from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.main.initialization.steps.basic_attributes_step import (
    BasicAttributesInitializationStep,
)
from battery_analysis.main.initialization.steps.environment_initialization_step import (
    EnvironmentInitializationStep,
)
from battery_analysis.main.initialization.steps.services_initialization_step import (
    ServicesInitializationStep,
)
from battery_analysis.main.initialization.steps.styles_initialization_step import (
    StylesInitializationStep,
)
from battery_analysis.main.initialization.steps.ui_setup_step import UISetupStep
from battery_analysis.main.ui_components.menu_manager import MenuManager
from battery_analysis.main.ui_components.window_setup import WindowSetup
from battery_analysis.main.workers.task_runner import TaskManager
from battery_analysis.reports.word_front_matter import WordFrontMatterMixin
from battery_analysis.reports.word_report_writer import WordReportWriter
from battery_analysis.utils.constants import COLOR_NAME
from battery_analysis.utils.report_coordinator import ReportCoordinator, build_word_replacements


@pytest.mark.parametrize("fails", [False, True])
@pytest.mark.parametrize("with_callbacks", [False, True])
def test_shared_dispatch_connects_before_start_and_releases_task(fails, with_callbacks):
    pool = Mock()
    pool.start.side_effect = lambda runner: runner.run()
    done, error = Mock(), Mock()
    progress = Mock()

    def task(value, *, factor, progress_callback):
        progress_callback(50, "half")
        if fails:
            raise ValueError("bad task")
        return value * factor

    with patch(
        "battery_analysis.main.workers.task_runner.QC.QThreadPool.globalInstance",
        return_value=pool,
    ):
        manager = TaskManager()
        runner = manager.run_async(
            task, done if with_callbacks else None, error if with_callbacks else None,
            3, factor=4, progress_callback=progress,
        )
    pool.start.assert_called_once_with(runner)
    assert manager.active_count == 0
    progress.assert_called_once_with(50, "half")
    if with_callbacks and fails:
        error.assert_called_once_with("bad task")
        done.assert_not_called()
    elif with_callbacks:
        done.assert_called_once_with(12)
        error.assert_not_called()
    else:
        done.assert_not_called()
        error.assert_not_called()


@pytest.mark.parametrize("owner", [DataProcessor, VersionManager])
def test_business_dispatch_remains_a_compatible_entry(owner):
    instance = owner.__new__(owner)
    instance._task_manager = Mock()
    task, done, error = Mock(), Mock(), Mock()
    result = instance._run_async(task, done, error, "input", flag=True)
    instance._task_manager.run_async.assert_called_once_with(
        task, done, error, "input", flag=True
    )
    assert result is instance._task_manager.run_async.return_value


@pytest.mark.parametrize("step_class", [
    BasicAttributesInitializationStep, EnvironmentInitializationStep,
    ServicesInitializationStep, StylesInitializationStep, UISetupStep,
])
def test_unconditional_initialization_uses_base_policy(step_class):
    assert step_class.can_execute is InitializationStep.can_execute
    assert step_class().can_execute(SimpleNamespace()) is True


@pytest.mark.parametrize("component", [MenuManager, WindowSetup])
@pytest.mark.parametrize("checked", [True, False, None])
@pytest.mark.parametrize("visible", [True, False])
def test_statusbar_entry_points_keep_checked_and_fallback_behavior(component, checked, visible):
    bar = Mock()
    bar.isVisible.return_value = visible
    window = SimpleNamespace(statusBar_BatteryAnalysis=bar)
    if checked is not None:
        window.actionShow_Statusbar = Mock()
        window.actionShow_Statusbar.isChecked.return_value = checked
    component(window).toggle_statusbar_safe()
    bar.setVisible.assert_called_once_with(checked if checked is not None else not visible)


@pytest.mark.parametrize("component", [MenuManager, WindowSetup])
def test_statusbar_absent_is_safe(component):
    component(SimpleNamespace()).toggle_statusbar_safe()


@pytest.mark.parametrize("levels", [[], [100], [100, 200, 300]])
def test_word_and_legacy_replacements_share_order_and_values(levels):
    info = [f"field-{i}" for i in range(19)]
    info[0] = "Pouch Cell"
    legacy = ReportCoordinator.__new__(ReportCoordinator)
    word = WordReportWriter.__new__(WordReportWriter)
    for owner in (legacy, word):
        owner.listTestInfo = info
        owner.listCurrentLevel = levels
        owner.intCurrentLevelNum = len(levels)
    legacy.listColorName = COLOR_NAME
    legacy._build_replacements()
    word._init_replace_placeholders()
    assert legacy.listTextToReplace == word.listTextToReplace == [
        "TypeA", "TypeB", "TypeC", "TypeD", "TypeE", "TypeF", "TypeG",
        "StrA", "StrB", "StrC", "StrD", "StrF",
    ]
    assert legacy.listImageToReplace == word.listImageToReplace
    assert len(word.listImageToReplace) == 21
    assert word.listImageToReplace[-1] == "<<Title_UseableCapacityOverCutoffVoltage9>>"
    assert legacy.listTestInfoForReplace == word.listTestInfoForReplace
    assert word.listTestInfoForReplace[:6] == [info[i] for i in (2, 3, 4, 5, 7, 11)]
    assert word.listTestInfoForReplace[7:11] == [None] * 4
    assert word.listTestInfoForReplace[-1] == ", ".join(
        f"{COLOR_NAME[i]}{value}mA" for i, value in enumerate(levels)
    )
    assert legacy.listTestInfoForReplace is not word.listTestInfoForReplace


def test_replacements_preserve_custom_colors_and_reject_missing_colors():
    info = [""] * 19
    info[0] = "Pouch Cell"
    assert build_word_replacements(info, [100], ["custom"])[2][-1] == "custom100mA"
    with pytest.raises(IndexError):
        build_word_replacements(info, [100], [])


@pytest.mark.parametrize(("value", "expected"), [
    ("server", "server"), (["a", 2], "a, 2"), (("a", "b"), "a, b"),
    (None, "fallback"), (123, "fallback"),
])
def test_remaining_equipment_reader_retains_format_and_fallback(value, expected):
    writer = WordFrontMatterMixin()
    writer._equipment_info = {"software": {"version": value}}
    assert writer._get_equip_value("software.version", "fallback") == expected
    assert writer._get_equip_value("missing.path", "fallback") == "fallback"
