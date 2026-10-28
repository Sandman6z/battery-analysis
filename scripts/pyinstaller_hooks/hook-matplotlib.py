"""沿用官方数据及 wheel DLL 收集规则，仅跳过应用未使用的示例数据。"""

from PyInstaller.compat import is_win
from PyInstaller.utils.hooks import (
    check_requirement,
    collect_data_files,
    collect_delvewheel_libs_directory,
)

# excludes 相对于 subdir；保留字体、styles、matplotlibrc 和工具栏图标。
datas = collect_data_files("matplotlib", subdir="mpl-data", excludes=["sample_data"])
binaries = []

# 与官方钩子相同：Windows wheel 的 DLL 和加载顺序文件不能随示例数据删除。
if is_win and check_requirement("matplotlib >= 3.7.0"):
    delvewheel_datas, delvewheel_binaries = collect_delvewheel_libs_directory("matplotlib")
    datas += delvewheel_datas
    binaries += delvewheel_binaries
