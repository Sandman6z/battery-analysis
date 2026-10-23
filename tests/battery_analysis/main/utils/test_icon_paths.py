"""Application icons must resolve from the package, not the working directory."""

from pathlib import Path
from unittest.mock import Mock

from battery_analysis.main.utils import file_utils
from battery_analysis.main.utils.file_utils import FileUtils


def test_packaged_icon_exists_without_project_root(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    paths = FileUtils.get_icon_paths(None, None)

    assert paths[0].is_file()
    assert paths[0].name == "Icon_BatteryTestGUI.ico"
    assert paths[0].parent.name == "icons"


def test_icon_path_uses_frozen_package_location(monkeypatch, tmp_path):
    package = tmp_path / "_MEIPASS" / "battery_analysis"
    icon = package / "resources" / "icons" / "Icon_BatteryTestGUI.ico"
    icon.parent.mkdir(parents=True)
    icon.touch()
    monkeypatch.setattr(file_utils, "__file__", str(package / "main" / "utils" / "file_utils.py"))

    assert FileUtils.get_icon_paths(None, None)[0] == icon


def test_icon_fallbacks_use_new_resource_layout(tmp_path):
    relative = Path("battery_analysis/resources/icons/Icon_BatteryTestGUI.ico")
    detector = Mock()
    detector.get_resource_path.return_value = tmp_path / "frozen" / relative

    paths = FileUtils.get_icon_paths(detector, tmp_path)

    detector.get_resource_path.assert_called_once_with(relative.as_posix())
    assert tmp_path / "frozen" / relative in paths
    assert tmp_path / relative in paths
    assert tmp_path / "src" / relative in paths
