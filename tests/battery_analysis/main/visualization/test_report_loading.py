"""Regression coverage for loading report-specific current levels and sparse curves."""

import logging
from unittest.mock import Mock

import pytest

from battery_analysis.main.visualization.data_loader import DataLoaderMixin
from battery_analysis.reports.info_csv_writer import write_info_csv, write_info_json


class ReportLoader(DataLoaderMixin):
    def __init__(self):
        self._config_service = Mock()
        self._config_service.get_config_value.side_effect = lambda key, default=None: (
            [30, 26, 15, 6, 3, 1] if key == "battery.pulseCurrents" else default
        )
        self._read_configurations()


def write_report(path, levels, charges=None, voltages=None):
    charges = charges if charges is not None else [[[10, 11, 12] for _ in levels]]
    voltages = voltages if voltages is not None else [[[3, 2.99, 2.98] for _ in levels]]
    write_info_csv(str(path), [f"Battery_{b}" for b in range(len(charges))], levels,
                   [[[] for _ in levels] for _ in charges], charges, voltages)
    write_info_json(str(path), [], current_levels=levels)


def test_report_levels_replace_startup_settings(tmp_path, caplog):
    write_report(tmp_path, [15, 13, 7.5, 3])
    loader = ReportLoader()
    assert loader.intCurrentLevelNum == 6
    loader.set_data_path(str(tmp_path))
    with caplog.at_level(logging.ERROR):
        assert loader.load_data()
    assert loader.listPulseCurrentLevel == [15, 13, 7.5, 3]
    assert loader.intCurrentLevelNum == 4
    assert loader.intBatteryNum == 1
    assert all(level[2] == [[10, 11, 12]] for level in loader.listPlt)
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_switch_report_and_reload_metadata(tmp_path):
    loader = ReportLoader()
    for levels in ([15, 13, 7.5, 3], [30, 26]):
        write_report(tmp_path, levels)
        loader.set_data_path(str(tmp_path))
        assert loader.load_data()
        assert loader.intCurrentLevelNum == len(levels)
    write_report(tmp_path, [7])
    assert loader.load_data()
    assert loader.listPulseCurrentLevel == [7]
    (tmp_path / "Info_Plot.json").unlink()
    loader.set_data_path(str(tmp_path))
    assert loader._get_pulse_current_level() == [30, 26, 15, 6, 3, 1]


@pytest.mark.parametrize("charges,voltages,expected", [
    ([[], [10, 11]], [[], [3, 2.99]], [[], [10, 11]]),
    ([[10, 10, 11]], [[3, 2.99, 2.98]], [[10, 11]]),
])
def test_filter_empty_curves_and_repeated_charge(charges, voltages, expected):
    filtered, _ = ReportLoader().filter_data(charges, voltages)
    assert filtered == expected


def test_missing_curve_does_not_hide_other_batteries(tmp_path):
    write_report(tmp_path, [15], [[[]], [[10, 11]]], [[[]], [[3, 2.99]]])
    loader = ReportLoader()
    loader.set_data_path(str(tmp_path))
    assert loader.load_data()
    assert loader.listPlt[0][2] == [[], [10, 11]]
    assert loader.intBatteryNum == 2

    from matplotlib.figure import Figure

    from battery_analysis.main.visualization.figure_builder import FigureBuilderMixin

    loader.listColor = ["#0675BE"]
    ax = Figure().subplots()
    raw_lines, filtered_lines = FigureBuilderMixin._plot_battery_curves(loader, ax)
    assert len(raw_lines) == len(filtered_lines) == 2
    assert list(filtered_lines[1].get_xdata()) == [10, 11]
    assert list(filtered_lines[1].get_ydata()) == [3, 2.99]


def test_all_empty_curves_are_not_valid_data(tmp_path):
    write_report(tmp_path, [15], [[[]]], [[[]]])
    loader = ReportLoader()
    loader.set_data_path(str(tmp_path))
    assert not loader.load_data()
