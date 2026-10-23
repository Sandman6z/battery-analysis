"""All report formats serialize the same submitted TestInfo battery type."""

import json

import pytest

from battery_analysis.reports.word_report_writer import WordReportWriter
from battery_analysis.utils.battery_classifier import battery_type_code
from battery_analysis.utils.json_writer import JsonWriter
from battery_analysis.utils.report_coordinator import ReportCoordinator


@pytest.mark.parametrize("label,code", [
    ("Coin Cell", "CoinCell"), ("Pouch Cell", "PouchCell"),
    ("Button Cell", "ButtonCell"), ("Cylindrical", "Cylindrical"),
    ("Prismatic", "Prismatic"), ("PouchCell", "PouchCell"),
])
def test_type_serialization(label, code):
    assert battery_type_code(label) == code


@pytest.mark.parametrize("value", ["", "CP5022121", "unknown"])
def test_unknown_type_is_not_silently_coin(value):
    with pytest.raises(ValueError, match="Unknown battery type"):
        battery_type_code(value)


@pytest.mark.parametrize("label,model,expected", [
    ("Pouch Cell", "CP5022121", "PouchCell"),
    ("Coin Cell", "CR2450", "CoinCell"),
    ("Pouch Cell", "CUSTOM_NEW_MODEL", "PouchCell"),
])
def test_json_and_word_use_same_type_snapshot(tmp_path, label, model, expected):
    info = [""] * 19
    info[0], info[2], info[4], info[7] = label, model, "Example", "Room"
    info[14], info[15], info[16] = [30], [2.25], "1.0"
    battery = [[[100]], ["BTS83_18_1_1"], ["2025-06-10 10:00:00", "2025-06-10 11:00:00"]]
    writer = JsonWriter(str(tmp_path), info, battery, result_dir=str(tmp_path))
    result = json.loads(next(tmp_path.glob("*.json")).read_text(encoding="utf-8"))
    assert result["batteryType"] == expected
    assert writer.dictJson["batteryType"] == expected

    coordinator = ReportCoordinator.__new__(ReportCoordinator)
    coordinator.listTestInfo = info
    coordinator.intCurrentLevelNum = 1
    coordinator.listCurrentLevel = [30]
    coordinator.listColorName = ["red"]
    coordinator._build_replacements()
    word = WordReportWriter.__new__(WordReportWriter)
    word.listTestInfo = info
    word.intCurrentLevelNum = 1
    word.listCurrentLevel = [30]
    word._init_replace_placeholders()
    assert coordinator.listTestInfoForReplace[6] == expected
    assert word.listTestInfoForReplace[6] == expected
