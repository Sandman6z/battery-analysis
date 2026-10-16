"""write_info_json：Info_Plot.json 写出（含裁决⑤ profile_validation 留痕）。"""

import json

from battery_analysis.utils.writers.info_csv_writer import write_info_json

TEST_INFO = [""] * 19
TEST_INFO[2] = "CF224642T"
TEST_INFO[4] = "20260917"
TEST_INFO[14] = [30, 26, 15, 6]


def _read(result_path):
    with open(result_path / "Info_Plot.json", encoding="utf-8") as f:
        return json.load(f)


def test_without_profile_validation_key_absent(tmp_path):
    write_info_json(str(tmp_path), TEST_INFO)
    assert "profile_validation" not in _read(tmp_path)


def test_with_profile_validation_written(tmp_path):
    record = {
        "result": "value_mismatch",
        "mismatch_type": "value_mismatch",
        "decision": "override_accepted",
        "policy_version": "2026.10",
    }
    write_info_json(str(tmp_path), TEST_INFO, profile_validation=record)
    data = _read(tmp_path)
    assert data["profile_validation"] == record


def test_base_metadata_still_written(tmp_path):
    write_info_json(str(tmp_path), TEST_INFO)
    data = _read(tmp_path)
    assert data["spec_type"] == "CF224642T"
    assert data["current_levels"] == [30, 26, 15, 6]
