"""
Nuitka 构建脚本 — BatteryAnalysis 应用程序

使用 Nuitka 将 Python 源码编译为独立可执行文件。
Nuitka 将 Python 编译为 C 代码再编译为原生机器码，相比 PyInstaller 的
"打包字节码+解释器"模式，具有以下优势：
- 启动更快（原生执行，无需解包）
- 运行性能有 5%~30% 提升
- 反编译保护更好（原生二进制，不可逆向为 .pyc）
- PyQt6 插件自动处理 hidden imports

已知风险与应对措施（本脚本已处理）：
1. UI 不响应/按钮无反应：
   - 通常由 Qt 插件（platforms/styles）未正确打包导致
   - 本脚本通过 --include-package-data 和显式 include-data-dir 解决
2. importlib.resources 路径问题：
   - 模板文件使用 importlib.resources.files() 定位
   - standalone 模式下 __file__ 路径正确，但 onefile 模式不兼容
   - 本脚本默认使用 standalone 模式
3. multiprocessing 递归启动：
   - launcher.py 已有 freeze_support()，Nuitka 无需额外处理
4. 动态导入（__getattr__ / importlib.import_module）：
   - Nuitka 能追踪大部分动态导入，但保险起见显式列出关键模块

用法:
    uv run python scripts/build_nuitka.py Release
    uv run python scripts/build_nuitka.py Debug
    uv run python scripts/build_nuitka.py Release --onefile   # 单文件模式（实验性）
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def _check_nuitka_env():
    """检查 Nuitka 构建环境是否就绪。"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True, text=True, timeout=30,
        )
        version_line = result.stdout.strip().split("\n")[0] if result.stdout else "unknown"
        logger.info("Nuitka 版本: %s", version_line)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.error("未找到 Nuitka。请先安装 build 依赖组:")
        logger.error("  uv pip install -e '.[build-nuitka]'")
        sys.exit(1)

    # 检查 C 编译器（Nuitka 需要）
    for compiler in ("cl", "gcc", "cc"):
        if shutil.which(compiler):
            logger.info("找到 C 编译器: %s", compiler)
            return
    logger.warning("未找到 cl/gcc/cc，Nuitka 将自动下载 MinGW64")


class NuitkaBuildConfig:
    """Nuitka 构建配置"""

    def __init__(self, build_type: str, onefile: bool = False, verbose: bool = False):
        self.project_root = Path(__file__).absolute().parent.parent
        self.build_type = build_type
        self.onefile = onefile
        self.verbose = verbose

        # 版本号
        from battery_analysis._version import __version__
        self.version = __version__

        # 目录
        self.src_path = self.project_root / "src"
        self.output_dir = self.project_root / "build" / self.build_type / "nuitka"
        self.temp_dir = self.project_root / "__nuitka_temp__"

        # 控制台模式
        self.console = build_type == "Debug"

    def get_entry_point(self) -> Path:
        """入口文件路径 — 使用 launcher.py（而非 main_window.py）

        launcher.py 是正确的入口：
        1. 先创建 QApplication 和闪屏（只依赖 PyQt6 基础库）
        2. 再导入业务模块（用户看到加载反馈）
        3. 已有 multiprocessing.freeze_support()
        """
        return self.src_path / "battery_analysis" / "main" / "launcher.py"

    def get_exe_name(self) -> str:
        """生成可执行文件名"""
        arch = "x64"
        suffix = "_debug" if self.build_type == "Debug" else ""
        mode = "_onefile" if self.onefile else ""
        return f"battery-analyzer_{self.version}_{arch}{suffix}{mode}"


class NuitkaBuilder:
    """Nuitka 构建管理器"""

    def __init__(self, config: NuitkaBuildConfig):
        self.config = config

    def clean(self):
        """清理构建目录"""
        logger.info("清理构建目录...")
        if self.config.output_dir.exists():
            shutil.rmtree(self.config.output_dir)
        if self.config.temp_dir.exists():
            shutil.rmtree(self.config.temp_dir)
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    def build_nuitka_args(self) -> list[str]:
        """构建 Nuitka 命令行参数

        关键设计决策：
        1. 使用 --standalone 而非 --onefile：
           - standalone 模式下 __file__ 指向正确的目录结构
           - 代码中大量使用 Path(__file__).parent 定位资源
           - onefile 模式下 __file__ 指向临时解压目录，资源路径会断

        2. --enable-plugin=pyqt6：
           - 自动收集 PyQt6 的 Qt 插件（platforms, styles, imageformats 等）
           - 自动处理 sip 绑定模块
           - 无需手动列出 hidden imports

        3. 显式包含数据目录：
           - templates/ — 报告模板（.docx）
           - ui/styles/ — QSS 样式表和 SVG 图标
           - locale/ — 国际化翻译文件

        4. --include-package=battery_analysis：
           - 确保 __init__.py 中的 __getattr__ 懒加载能被正确追踪
           - Nuitka 需要知道这是一个完整的包
        """
        cfg = self.config
        entry = cfg.get_entry_point()
        exe_name = cfg.get_exe_name()

        args = [
            sys.executable, "-m", "nuitka",

            # ── 基本模式 ──
            "--standalone",                          # 独立模式（保留目录结构）
            f"--output-dir={cfg.output_dir}",
            f"--output-filename={exe_name}.exe",
            "--remove-output",                       # 构建前清理旧产物

            # ── Windows 设置 ──
            f"--windows-icon-from-ico={cfg.project_root / 'config' / 'resources' / 'icons' / 'Icon_BatteryTestGUI.ico'}",
            "--windows-company-name=Ewin Hardware Group",
            "--windows-product-name=Battery Analysis",
            f"--windows-product-version={cfg.version}",
            "--windows-file-version=3.0.0",
            "--windows-file-description=Battery Test Data Analysis App",

            # ── PyQt6 插件（核心！解决 UI 不响应问题）──
            "--enable-plugin=pyqt6",

            # ── 数据文件包含 ──
            # standalone 模式下，这些会被复制到 dist/ 对应相对位置
            f"--include-data-dir={cfg.src_path / 'battery_analysis' / 'templates'}=battery_analysis/templates",
            f"--include-data-dir={cfg.src_path / 'battery_analysis' / 'ui' / 'styles'}=battery_analysis/ui/styles",
            f"--include-data-dir={cfg.project_root / 'locale'}=locale",

            # ── 编译优化 ──
            "--assume-yes-for-downloads",            # 自动下载 MinGW64（如需要）
            "--show-progress",                       # 显示编译进度
            "--show-scons",                          # 显示 SCons 构建信息（Debug 时有用）

            # ── 排除不需要的模块（Nuitka 用 --nofollow-import-to）──
            # Nuitka 的 --include-package 会拉入所有传递依赖，
            # 必须显式排除不需要的模块来缩小体积。
            "--nofollow-import-to=pytest",
            "--nofollow-import-to=pylint",
            "--nofollow-import-to=black",
            "--nofollow-import-to=astroid",
            "--nofollow-import-to=pylint_json2html",
            "--nofollow-import-to=setuptools",
            "--nofollow-import-to=pip",
            "--nofollow-import-to=pkg_resources",
            "--nofollow-import-to=IPython",
            "--nofollow-import-to=jupyter",
            "--nofollow-import-to=jupyter_client",
            "--nofollow-import-to=jupyter_core",
            "--nofollow-import-to=tkinter",
            "--nofollow-import-to=PySide6",
            "--nofollow-import-to=PySide2",
            "--nofollow-import-to=PyQt5",
            # 测试子包
            "--nofollow-import-to=matplotlib.tests",
            "--nofollow-import-to=matplotlib.testing",
            "--nofollow-import-to=matplotlib.sphinxext",
            "--nofollow-import-to=numpy.testing",
            "--nofollow-import-to=numpy.distutils",
            "--nofollow-import-to=numpy.f2py",
            "--nofollow-import-to=numpy.random._examples",
            "--nofollow-import-to=pandas.tests",
            "--nofollow-import-to=openpyxl.tests",
            # 不使用的 matplotlib 后端
            "--nofollow-import-to=matplotlib.backends.backend_qt4",
            "--nofollow-import-to=matplotlib.backends.backend_qt5",
            "--nofollow-import-to=matplotlib.backends.backend_wx",
            "--nofollow-import-to=matplotlib.backends.backend_gtk",
            "--nofollow-import-to=matplotlib.backends.backend_gtk3",
            "--nofollow-import-to=matplotlib.backends.backend_gtk4",
            "--nofollow-import-to=matplotlib.backends.backend_webagg",
            "--nofollow-import-to=matplotlib.backends.backend_nbagg",
            "--nofollow-import-to=matplotlib.backends.backend_pgf",
            # 不使用的 PyQt6 子模块
            "--nofollow-import-to=PyQt6.QtMultimedia",
            "--nofollow-import-to=PyQt6.QtMultimediaWidgets",
            "--nofollow-import-to=PyQt6.QtPositioning",
            "--nofollow-import-to=PyQt6.QtSensors",
            "--nofollow-import-to=PyQt6.QtTextToSpeech",
            "--nofollow-import-to=PyQt6.QtWebChannel",
            "--nofollow-import-to=PyQt6.QtWebSockets",
            "--nofollow-import-to=PyQt6.QtWebEngineWidgets",
            "--nofollow-import-to=PyQt6.QtWebEngineCore",
            "--nofollow-import-to=PyQt6.QtWebEngineQuick",
            "--nofollow-import-to=PyQt6.QtHelp",
            "--nofollow-import-to=PyQt6.QtSql",
            "--nofollow-import-to=PyQt6.QtQml",
            "--nofollow-import-to=PyQt6.QtQuick",
            "--nofollow-import-to=PyQt6.QtQuick3D",
            "--nofollow-import-to=PyQt6.QtQuickWidgets",
            "--nofollow-import-to=PyQt6.QtDBus",
            "--nofollow-import-to=PyQt6.QtBluetooth",
            "--nofollow-import-to=PyQt6.QtNfc",
            "--nofollow-import-to=PyQt6.QtXml",
            "--nofollow-import-to=PyQt6.QtDesigner",
            "--nofollow-import-to=PyQt6.QtSerialPort",
            "--nofollow-import-to=PyQt6.QtStateMachine",
            "--nofollow-import-to=PyQt6.QtPdf",
            "--nofollow-import-to=PyQt6.QtPdfWidgets",
            "--nofollow-import-to=PyQt6.QtRemoteObjects",
            "--nofollow-import-to=PyQt6.QtSpatialAudio",
            # pywin32 附带的无用包
            "--nofollow-import-to=pythonwin",
            "--nofollow-import-to=adodbapi",
            "--nofollow-import-to=win32com",
            "--nofollow-import-to=win32com.shell",

            # ── 入口文件 ──
            str(entry),
        ]

        # ── 控制台模式（Debug） ──
        if cfg.console:
            args.append("--windows-console-mode=attach")
        else:
            args.append("--windows-console-mode=disable")

        # ── onefile 模式（可选，实验性） ──
        if cfg.onefile:
            args.append("--onefile")
            # onefile 模式下需要额外处理资源路径
            # 此时 __file__ 指向临时目录，需要设置 NUITKA_HOME
            logger.warning("⚠ onefile 模式是实验性的，可能导致资源文件路径问题")

        # ── 详细输出 ──
        if cfg.verbose:
            args.append("--verbose")

        return args

    def build(self) -> bool:
        """执行构建"""
        cfg = self.config
        entry = cfg.get_entry_point()

        if not entry.exists():
            logger.error("入口文件不存在: %s", entry)
            return False

        logger.info("=" * 60)
        logger.info("Nuitka 构建开始")
        logger.info("  构建类型: %s", cfg.build_type)
        logger.info("  模式: %s", "onefile" if cfg.onefile else "standalone")
        logger.info("  入口: %s", entry)
        logger.info("  输出: %s", cfg.output_dir)
        logger.info("=" * 60)

        args = self.build_nuitka_args()

        if cfg.verbose:
            logger.info("Nuitka 命令:")
            for arg in args:
                logger.info("  %s", arg)

        t0 = time.time()

        # Nuitka 从项目根目录运行
        result = subprocess.run(
            args,
            cwd=cfg.project_root,
            check=False,
            encoding="utf-8",
        )

        elapsed = time.time() - t0

        if result.returncode != 0:
            logger.error("Nuitka 构建失败 (返回码: %d, 耗时: %.1fs)", result.returncode, elapsed)
            return False

        logger.info("Nuitka 构建成功 (耗时: %.1fs)", elapsed)
        return True

    def verify(self) -> bool:
        """验证构建产物"""
        cfg = self.config

        if cfg.onefile:
            exe_path = cfg.output_dir / f"{cfg.get_exe_name()}.exe"
        else:
            # Nuitka standalone 输出目录名基于入口文件名（如 launcher.dist），
            # 而不是 exe 名称。遍历查找 .dist 目录中的 .exe 文件。
            exe_path = None
            for d in cfg.output_dir.iterdir():
                if d.is_dir() and d.name.endswith(".dist"):
                    for f in d.iterdir():
                        if f.suffix == ".exe":
                            exe_path = f
                            logger.info("找到可执行文件: %s", exe_path)
                            break
                if exe_path:
                    break
            if exe_path is None:
                exe_path = cfg.output_dir / "dummy"  # 触发失败路径

        if not exe_path.exists():
            logger.error("❌ 未找到可执行文件")
            return False

        size_mb = exe_path.stat().st_size / (1024 * 1024)
        logger.info("✅ 可执行文件: %s (%.1f MB)", exe_path, size_mb)

        if not cfg.onefile:
            dist_dir = exe_path.parent

            # ── 补充 Python 包的 __init__.py 文件 ──
            # Nuitka standalone 只打包数据文件，不创建 Python 包结构，
            # 导致 importlib.resources.files() 无法找到包。
            self._ensure_package_init(cfg, dist_dir)

            # 检查 Qt 插件目录
            qt_plugin_dirs = [
                "PyQt6/Qt6/plugins/platforms",
                "PyQt6/Qt6/plugins/styles",
            ]
            for plugin_dir in qt_plugin_dirs:
                full_path = dist_dir / plugin_dir
                if full_path.exists():
                    logger.info("  ✅ Qt 插件: %s", plugin_dir)
                else:
                    logger.warning("  ⚠ 缺少 Qt 插件: %s", plugin_dir)

        return True

    @staticmethod
    def _ensure_package_init(config: NuitkaBuildConfig, dist_dir: Path):
        """在 dist 目录中为有数据文件的包创建最小 __init__.py。

        Nuitka standalone 只将数据文件复制到 dist，但不创建 Python 包结构。
        这导致 importlib.resources.files("battery_analysis") 找不到包。
        解决方案：为每个包含数据文件的目录创建空 __init__.py，
        让 Python 的导入系统将其识别为包。
        """
        # 源码中需要保留包结构的目录（有数据文件的）
        packages_with_data = [
            "battery_analysis",
            "battery_analysis/templates",
            "battery_analysis/ui",
            "battery_analysis/ui/styles",
        ]
        for pkg_rel in packages_with_data:
            pkg_dir = dist_dir / pkg_rel
            init_file = pkg_dir / "__init__.py"
            if pkg_dir.exists() and not init_file.exists():
                init_file.write_text("# Package marker for importlib.resources\n", encoding="utf-8")
                logger.info("  创建包文件: %s", init_file.relative_to(dist_dir))


    def run(self) -> bool:
        """执行完整构建流程"""
        self.clean()
        success = self.build()
        if success:
            success = self.verify()

        # 打开输出目录
        if success and not os.environ.get("CI"):
            try:
                os.startfile(self.config.output_dir)
            except OSError:
                pass

        return success


def main():
    parser = argparse.ArgumentParser(description="Nuitka 构建 BatteryAnalysis 应用程序")
    parser.add_argument(
        "build_type", choices=["Debug", "Release"], help="构建类型: Debug 或 Release",
    )
    parser.add_argument(
        "--onefile", action="store_true",
        help="单文件模式（实验性，可能导致资源路径问题）",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志信息")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    _check_nuitka_env()

    config = NuitkaBuildConfig(
        build_type=args.build_type,
        onefile=args.onefile,
        verbose=args.verbose,
    )
    builder = NuitkaBuilder(config)

    try:
        success = builder.run()
        if success:
            logger.info("✅ %s 构建完成", args.build_type)
        else:
            logger.error("❌ 构建失败")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("构建被用户中断")
        sys.exit(130)
    except (OSError, FileNotFoundError, PermissionError) as e:
        logger.error("构建出错: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
