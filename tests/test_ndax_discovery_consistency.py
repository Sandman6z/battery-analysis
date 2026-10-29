"""Conversion preview and analysis must discover the same NDAX files."""

from pathlib import Path

import pytest

from battery_analysis.ndax.converter import _get_ndax_files, get_ndax_files
from battery_analysis.utils.file_finder import scan_sorted_ndax


def test_analysis_and_conversion_share_selection_and_natural_order(tmp_path):
    for name in ("channel_10.ndax", "channel_2.NDAX", "channel_1.NdAx", "notes.csv"):
        (tmp_path / name).write_bytes(b"placeholder")
    (tmp_path / "directory.ndax").mkdir()
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "channel_3.ndax").write_bytes(b"placeholder")
    expected = ["channel_1.NdAx", "channel_2.NDAX", "channel_10.ndax"]
    analysis = scan_sorted_ndax(str(tmp_path))
    assert [Path(path).name for path in analysis] == expected
    assert get_ndax_files(tmp_path) == expected
    assert _get_ndax_files(tmp_path) == [Path(path) for path in analysis]
    assert all(isinstance(path, str) for path in analysis)
    assert all(isinstance(path, Path) for path in _get_ndax_files(tmp_path))


def test_empty_directory_is_empty_for_both_entry_points(tmp_path):
    assert scan_sorted_ndax(str(tmp_path)) == []
    assert get_ndax_files(tmp_path) == []


def test_legacy_conversion_missing_directory_contract_is_preserved(tmp_path):
    missing = tmp_path / "missing"
    assert get_ndax_files(missing) == []
    with pytest.raises(FileNotFoundError):
        scan_sorted_ndax(str(missing))
