"""Statistical result cells show statistics or No data, without sample-count labels."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from docx import Document

from battery_analysis.reports.excel_overview import ExcelOverviewMixin
from battery_analysis.reports.word_front_matter import WordFrontMatterMixin


@pytest.mark.parametrize("format_name", ["word", "excel"])
@pytest.mark.parametrize("count", [0, 1, 16])
def test_statistical_cells_do_not_display_sample_count(format_name, count):
    writer = SimpleNamespace(
        intCurrentLevelNum=1, intVoltageLevelNum=1,
        listCurrentLevel=[15], listVoltageLevel=[2.25],
    )
    stats = {key: [[300]] for key in (
        "mean", "med", "std", "mm3s", "mm2s", "mp2s", "mp3s", "min", "max",
    )}
    stats["counts"] = [[count]]
    if format_name == "word":
        table = WordFrontMatterMixin._write_statistical_results(writer, Document(), stats)
        text = table.cell(1, 1).text
    else:
        worksheet = Mock()
        fmts = {key: None for key in (
            "overview_stat_dark", "overview_stat_light", "overview_stat_light_bold", "overview_stat",
        )}
        ExcelOverviewMixin._write_overview_statistics(writer, worksheet, stats, fmts)
        text = next(call.args[2] for call in worksheet.write.call_args_list if call.args[:2] == (14, 1))
    assert "n=" not in text
    if count:
        assert text.startswith("μ: 300mAh\n")
        assert "Maximum: 300mAh" in text
    else:
        assert text == "No data"
    assert stats["counts"] == [[count]]
