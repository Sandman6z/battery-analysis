import csv
import zipfile
from unittest.mock import Mock, patch

import pytest
from PyQt6.QtWidgets import QMessageBox

from battery_analysis.main.managers.analysis_runner import AnalysisRunner
from battery_analysis.main.utils.file_utils import FileUtils


class TestAnalysisRunner:
    def setup_method(self):
        self.main_window = Mock()
        self.runner = AnalysisRunner(self.main_window)

    def test_init(self):
        assert self.runner.main_window == self.main_window

    def test_run_analysis(self):
        self.main_window.table_manager = Mock()
        self.main_window.table_manager.save_table = Mock()
        self.main_window.ui_manager = Mock()
        self.main_window.ui_manager.init_widgetcolor = Mock()
        with patch.object(self.runner, "_preflight_recipe", return_value=(None, {})):
            self.runner.run_analysis()
        self.main_window.table_manager.save_table.assert_called_once()
        self.main_window.ui_manager.init_widgetcolor.assert_called_once()

    @staticmethod
    def _recipe(levels):
        pulses = ''.join(f'<Pulse{i + 1} Value="-{v}"/>' for i, v in enumerate(levels))
        return f'<root><Step_Info><Step4><PulseData Count="{len(levels)}">{pulses}</PulseData></Step4></Step_Info></root>'

    def test_preflight_checks_every_channel_and_profile_values(self, tmp_path):
        source = tmp_path / "1_ndax"
        source.mkdir()
        out = tmp_path / "results"
        out.mkdir()
        for name in ("a.ndax", "b.ndax"):
            with zipfile.ZipFile(source / name, "w") as z:
                z.writestr("Step.xml", self._recipe([30, 26]))
        profile = tmp_path / "profile.xml"
        profile.write_text(self._recipe([30, 26.01]), encoding="utf-8")
        checksum = FileUtils.calc_checksum([str(p) for p in sorted(source.glob("*.ndax"))])
        with (out / "SHA256.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows([["Checksums:"], [checksum], ["Times:"], ["0"]])
        mw = self.main_window
        mw.lineEdit_InputPath.text.return_value = str(source)
        mw.lineEdit_OutputPath.text.return_value = str(out)
        mw.lineEdit_TestProfile.text.return_value = str(profile)
        mw.lineEdit_Version.text.return_value = "1.0"
        mw.sha256_checksum = checksum
        with patch("battery_analysis.main.managers.analysis_runner.QW.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes):
            files, decision = self.runner._preflight_recipe()
        assert len(files) == 2
        assert mw.listCurrentLevel == [30, 26]
        assert decision == {"result": "mismatch", "mismatch_type": "value", "decision": "continue_ndax", "policy_version": "2026.10"}

        with zipfile.ZipFile(source / "b.ndax", "w") as z:
            z.writestr("Step.xml", self._recipe([30, 25]))
        mw.sha256_checksum = FileUtils.calc_checksum([str(p) for p in sorted(source.glob("*.ndax"))])
        with pytest.raises(ValueError, match=r"Different Step\.xml"):
            self.runner._preflight_recipe()
