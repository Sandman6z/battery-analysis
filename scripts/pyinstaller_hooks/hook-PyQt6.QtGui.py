"""沿用官方 QtGui 收集规则，仅跳过应用未使用的 PDF 图片读取插件。"""

from pathlib import Path

from PyInstaller.utils.hooks.qt import add_qt6_dependencies

hiddenimports, binaries, datas = add_qt6_dependencies(__file__)

# qpdf 用于将 PDF 读为图片，与 Matplotlib 的图表导出无关。
binaries = [entry for entry in binaries if Path(entry[0]).name.lower() != "qpdf.dll"]
