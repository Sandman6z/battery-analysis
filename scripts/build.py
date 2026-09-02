"""
构建脚本模块，用于构建BatteryAnalysis应用程序。
支持Debug和Release两种构建类型，负责处理版本号管理、PyInstaller构建流程。
"""

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tomllib import TOMLDecodeError

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def _check_build_env():
    """检查构建环境：PyInstaller 已安装（缺失时输出安装指引并退出）。"""
    try:
        import PyInstaller

        logger.info("PyInstaller已安装: %s", PyInstaller.__version__)
    except ImportError:
        logger.warning("警告: 未找到PyInstaller模块。请先安装build依赖组:")
        logger.warning("  uv pip install -e '.[build]'")
        sys.exit(1)


def _build_failed(result):
    """PyInstaller 构建失败判定：返回码非零（或结果为 None）即失败。"""
    return result is None or result.returncode != 0


class BuildConfig:
    """构建配置基类"""

    def __init__(self, specified_build_type=None):
        self.project_root = Path(__file__).absolute().parent.parent
        self.temp_build_dir = self.project_root / "__temp__"

        try:
            from battery_analysis.utils.version import Version

            self.version = Version().version
            logger.info("从Version类获取的版本号: %s", self.version)
        except (
            OSError, FileNotFoundError, ImportError,
            PermissionError, KeyError, TOMLDecodeError,
        ) as e:
            logger.error("无法从Version类获取版本号: %s", e)
            sys.exit(1)

        self.console_mode = specified_build_type == "Debug"


class BuildManager(BuildConfig):
    """构建管理器"""

    def __init__(self, specified_build_type):
        super().__init__(specified_build_type)
        if specified_build_type not in ["Debug", "Release"]:
            raise ValueError(
                f"不支持的构建类型: {specified_build_type}。只支持'Debug'和'Release'"
            )
        self.build_type = specified_build_type
        self.build_path = self.temp_build_dir
        self.console = self.console_mode

        self.apps_config = self._get_apps_config()
        self.clean_build_dirs()

    def _get_apps_config(self):
        """获取应用程序配置列表"""
        return [
            {
                "name": "BatteryAnalysis",
                "main_file_path": (
                    self.project_root / "src" / "battery_analysis" / "main" / "main_window.py"
                ),
                "base_exe_name": "battery-analyzer",
                "icon_name": "Icon_BatteryAnalysis.ico",
                "hidden_imports": [
                    # 核心 PyQt6 模块
                    "PyQt6.QtCore",
                    "PyQt6.QtGui",
                    "PyQt6.QtWidgets",
                    # 应用模块
                    "battery_analysis",
                    "battery_analysis.main",
                    "battery_analysis.ui",
                    "battery_analysis.utils",
                    "battery_analysis.main.battery_chart_viewer",
                    "battery_analysis.utils.version",
                    "battery_analysis.utils.file_writer",
                    "battery_analysis.utils.processors.battery_analysis",
                    "battery_analysis.ui.ui_main_window",
                    # 第三方库
                    "openpyxl",
                    "python_calamine",
                    "xlsxwriter",
                    "docx",
                    "matplotlib.backends.backend_svg",
                    "pandas._config.localization",
                ],
            }
        ]

    def run_build(self):
        """执行完整的构建流程"""
        try:
            self.build()
            self._verify_and_clean()

            final_build_dir = self.project_root / "build" / self.build_type
            if os.environ.get("CI"):
                logger.info("CI 环境，跳过打开构建文件夹: %s", final_build_dir)
            else:
                logger.info("正在打开构建文件夹: %s", final_build_dir)
                os.startfile(final_build_dir)
        except (OSError, FileNotFoundError, PermissionError) as e:
            logger.error("构建过程中出错: %s", e)

    def clean_build_dirs(self):
        """清理构建目录和缓存"""
        logger.info("开始清理构建目录和缓存...")

        if self.temp_build_dir.exists():
            shutil.rmtree(self.temp_build_dir)

        final_build_type_dir = self.project_root / "build" / self.build_type
        if final_build_type_dir.exists():
            shutil.rmtree(final_build_type_dir)

        self.temp_build_dir.mkdir(parents=True, exist_ok=True)
        logger.info("构建目录清理完成")

    def _verify_and_clean(self):
        """验证构建产物并清理临时目录"""
        build_dir = self.project_root / "build" / self.build_type
        for app_config in self.apps_config:
            exe_path = build_dir / f"{app_config['exe_name']}.exe"
            if exe_path.exists():
                logger.info("确认: %s 已在目标目录中", exe_path)
            else:
                logger.warning("警告: %s 不存在", exe_path)

        if self.temp_build_dir.exists():
            shutil.rmtree(self.temp_build_dir)
            logger.info("已清理临时构建目录: %s", self.temp_build_dir)

    def _generate_exe_name(self, base_name, architecture):
        """生成可执行文件名"""
        suffix = "_debug" if self.build_type != "Release" else ""
        return f"{base_name}_{self.version}_{architecture}{suffix}"

    def _build_pyinstaller_args(self, app_config, temp_path, src_path, final_build_dir):
        """构建PyInstaller命令参数

        PyInstaller 从 src/ 目录运行，入口文件用绝对路径，确保依赖追踪正确。
        """
        excluded_modules = [
            # 开发/测试/构建工具
            "pytest", "pylint", "black", "astroid", "pylint_json2html",
            "setuptools", "pip", "pkg_resources",
            "IPython", "jupyter", "jupyter_client", "jupyter_core",
            # pywin32 附带的无用包
            "pythonwin", "adodbapi", "win32com", "win32com.shell",
            # matplotlib 测试/不用的后端
            "matplotlib.tests", "matplotlib.testing", "matplotlib.sphinxext",
            "matplotlib.backends.backend_qt4", "matplotlib.backends.backend_qt5",
            "matplotlib.backends.backend_wx", "matplotlib.backends.backend_gtk",
            "matplotlib.backends.backend_gtk3", "matplotlib.backends.backend_gtk4",
            "matplotlib.backends.backend_webagg", "matplotlib.backends.backend_nbagg",
            "matplotlib.backends.backend_pgf",
            # numpy 无用模块
            "numpy.testing", "numpy.distutils", "numpy.f2py",
            "numpy.random._examples",
            # pandas 不需要的模块
            "pandas.tests",
            # 其他库测试
            "openpyxl.tests",
            # GUI 框架排除（只用 PyQt6）
            "tkinter", "PySide6", "PySide2", "PyQt5",
            # 不使用的 PyQt6 子模块
            "PyQt6.QtMultimedia", "PyQt6.QtMultimediaWidgets",
            "PyQt6.QtPositioning", "PyQt6.QtSensors",
            "PyQt6.QtTextToSpeech", "PyQt6.QtWebChannel",
            "PyQt6.QtWebSockets", "PyQt6.QtWebEngineWidgets",
            "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineQuick",
            "PyQt6.QtHelp", "PyQt6.QtSql", "PyQt6.QtQml",
            "PyQt6.QtQuick", "PyQt6.QtQuick3D", "PyQt6.QtQuickWidgets",
            "PyQt6.QtDBus", "PyQt6.QtBluetooth", "PyQt6.QtNfc",
            "PyQt6.QtXml", "PyQt6.QtDesigner", "PyQt6.QtSerialPort",
            "PyQt6.QtStateMachine", "PyQt6.QtPdf", "PyQt6.QtPdfWidgets",
            "PyQt6.QtRemoteObjects", "PyQt6.QtSpatialAudio",
        ]

        icon_path = self.project_root / "config" / "resources" / "icons" / "Icon_BatteryTestGUI.ico"

        # ----- 构建命令 -----
        # 从 src/ 目录运行 PyInstaller，入口用绝对路径
        cmd_args = [
            sys.executable, "-m", "PyInstaller",
            "--log-level=INFO",
            "--hidden-import=pywintypes",
            f"--name={app_config['exe_name']}",
            f"--icon={icon_path}",
            f"--distpath={final_build_dir}",
            f"--workpath={temp_path / app_config['name']}",
            "--onedir",
        ]

        # ----- 隐藏导入 -----
        for hidden_import in app_config["hidden_imports"]:
            cmd_args.append(f"--hidden-import={hidden_import}")

        # ----- 入口文件（绝对路径，从 src/ 运行时能找到 battery_analysis 包） -----
        cmd_args.append(str(app_config["main_file_path"]))

        # ----- 数据文件 -----
        cmd_args.extend([
            "--add-data",
            f"{src_path / 'battery_analysis' / 'templates'};battery_analysis/templates",
            "--add-data",
            f"{src_path / 'battery_analysis' / 'ui' / 'styles'};battery_analysis/ui/styles",
            "--add-data",
            f"{self.project_root / 'locale'};locale",
        ])

        # ----- 排除模块 -----
        for module in excluded_modules:
            cmd_args.append(f"--exclude-module={module}")

        # ----- 控制台 / DEBUG -----
        debug_mode = self.build_type == "Debug"
        if self.console_mode or debug_mode:
            cmd_args.append("--console")
        else:
            cmd_args.append("--noconsole")

        if not debug_mode:
            cmd_args.append("--strip")

        # 确保 numpy 的 C 扩展 DLL 被正确收集
        cmd_args.append("--collect-submodules=numpy")

        return cmd_args

    def build(self):
        """构建应用程序"""
        logger.info("开始构建...")
        temp_path = self.temp_build_dir
        temp_path.mkdir(parents=True, exist_ok=True)

        final_build_dir = self.project_root / "build" / self.build_type
        final_build_dir.mkdir(parents=True, exist_ok=True)

        src_path = self.project_root / "src"
        architecture = "x64"

        for app_config in self.apps_config:
            app_config["exe_name"] = self._generate_exe_name(
                app_config["base_exe_name"], architecture
            )

            cmd_args = self._build_pyinstaller_args(
                app_config, temp_path, src_path, final_build_dir
            )

            # 从 src/ 目录运行 PyInstaller，确保依赖追踪正确
            result = subprocess.run(
                cmd_args, cwd=src_path, check=False,
                capture_output=True, encoding="utf-8",
            )
            logger.info("构建结果: %s", result.returncode)
            if result.stderr:
                logger.error("错误输出: %s", result.stderr)

            if _build_failed(result):
                logger.error(
                    "构建失败：%s（返回码 %s）",
                    app_config["name"],
                    getattr(result, "returncode", "N/A"),
                )
                sys.exit(1)

        if temp_path.exists():
            shutil.rmtree(temp_path)
        logger.info("构建完成，可执行文件位于: %s", final_build_dir)


def main():
    """主函数，处理命令行参数并执行构建流程"""
    import argparse

    parser = argparse.ArgumentParser(description="构建BatteryAnalysis应用程序")
    parser.add_argument(
        "build_type", choices=["Debug", "Release"], help="构建类型: Debug 或 Release"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志信息")

    args = parser.parse_args()
    _check_build_env()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        build_manager = BuildManager(args.build_type)
        build_manager.run_build()
        logger.info("%s 构建完成", args.build_type)
    except (OSError, FileNotFoundError, PermissionError, ValueError) as e:
        logger.error("构建失败: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
