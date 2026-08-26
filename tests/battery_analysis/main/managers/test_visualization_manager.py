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
