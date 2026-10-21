"""可视化管理器测试——当前仅验证 matplotlib 延迟导入"""

import subprocess
import sys


def test_matplotlib_import_is_deferred():
    """visualization_manager 顶层不再 import matplotlib"""
    code = (
        "import sys;"
        "from battery_analysis.main.managers.visualization_manager import VisualizationManager;"
        "assert 'matplotlib' not in sys.modules"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_automatic_visualizer_uses_exact_delivered_directory(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import Mock

    from battery_analysis.main.managers.visualization_manager import VisualizationManager

    result_dir = tmp_path / "A" / "20241019_v1.0"
    result_dir.mkdir(parents=True)
    (result_dir / "Info_Image.csv").write_text("data")
    window = SimpleNamespace(lineEdit_TestProfile=Mock(), visualizer_factory=Mock(), statusBar_BatteryAnalysis=Mock())
    window.lineEdit_TestProfile.text.return_value = "B/new-profile.xml"
    visualizer = window.visualizer_factory.create_visualizer.return_value
    visualizer.show_figure.return_value = True
    manager = VisualizationManager(window)
    monkeypatch.setattr(manager, "_cleanup_matplotlib_resources", Mock())
    manager.run_visualizer(data_path=str(result_dir))
    window.lineEdit_TestProfile.text.assert_not_called()
    visualizer.show_figure.assert_called_once_with(data_path=str(result_dir))


def test_manual_visualizer_keeps_current_ui_profile(monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import Mock

    from battery_analysis.main.managers.visualization_manager import VisualizationManager

    window = SimpleNamespace(lineEdit_TestProfile=Mock(), statusBar_BatteryAnalysis=Mock())
    window.lineEdit_TestProfile.text.return_value = "B/current-profile.xml"
    manager = VisualizationManager(window)
    launch = Mock()
    monkeypatch.setattr(manager, "_run_visualizer_standalone", launch)
    manager.run_visualizer(False)  # QAction.triggered(bool)
    launch.assert_called_once_with("B/current-profile.xml")
