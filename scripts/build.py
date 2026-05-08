"""
构建脚本模块，用于构建BatteryAnalysis和ImageMaker应用程序。
支持Debug和Release两种构建类型，负责处理版本号管理、文件复制和PyInstaller构建流程。
"""
import sys
import os
import shutil
import configparser
import subprocess
import logging
from pathlib import Path

# 从tomllib导入TOMLDecodeError用于异常处理
from tomllib import TOMLDecodeError

# 配置日志记录
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入Version类，统一版本管理
# 添加sys.path以确保可以导入battery_analysis模块
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
try:
    from battery_analysis.utils.version import Version
except ImportError as e:
    logger.error("无法导入Version类: %s", e)
    sys.exit(1)

# 检查PyInstaller是否已安装，如果未安装则提示用户安装build依赖
try:
    import PyInstaller
    logger.info("PyInstaller已安装: %s", PyInstaller.__version__)
except ImportError:
    logger.warning("警告: 未找到PyInstaller模块。请先安装build依赖组:")
    logger.warning("  uv pip install -e '.[build]'")
    logger.warning("或")
    logger.warning("  pip install -e '.[build]'")
    sys.exit(1)

# 添加项目根目录到Python路径，确保能正确导入模块
script_dir = Path(__file__).absolute().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))


class CaseSensitiveConfigParser(configparser.ConfigParser):
    """大小写敏感的配置解析器"""

    def optionxform(self, option_str):
        return option_str


class BuildConfig:
    """构建配置基类"""

    def __init__(self, specified_build_type=None):
        # 项目根目录是scripts的上一级目录
        self.project_root = Path(__file__).absolute().parent.parent
        self.temp_build_dir = self.project_root / "__temp__"

        # 使用Version类获取版本号（版本号中心化管理）
        try:
            self.version = Version().version
            logger.info("从Version类获取的版本号: %s", self.version)
        except (FileNotFoundError, ImportError, IOError, PermissionError, KeyError, TOMLDecodeError) as e:
            logger.error("无法从Version类获取版本号: %s", e)
            sys.exit(1)

        # 根据构建类型决定是否显示控制台窗口
        # Debug构建默认显示控制台窗口，Release构建默认不显示控制台窗口
        self.console_mode = specified_build_type == "Debug"
        # 补充说明：Release模式下，specified_build_type != "Debug"，因此self.console_mode也为False
        # 这样就自动实现了Release模式不显示控制台的功能，无需额外编写Release模式的逻辑


class BuildManager(BuildConfig):
    """构建管理器"""

    def __init__(self, specified_build_type):
        super().__init__(specified_build_type)
        # 只支持Debug和Release两种构建类型
        if specified_build_type not in ['Debug', 'Release']:
            raise ValueError(
                f"不支持的构建类型: {specified_build_type}。只支持'Debug'和'Release'，或请检查大小写")
        self.build_type = specified_build_type
        self.build_path = self.temp_build_dir
        
        # 统一Debug环境处理：设置DEBUG环境变量，使version.py能检测到Debug环境
        if self.build_type == "Debug":
            os.environ["DEBUG"] = "true"
            logger.info("设置DEBUG环境变量为'true'，表示Debug构建环境")
        self.console = self.console_mode

        # 定义共享的应用程序配置列表：统一管理BatteryAnalysis和BatteryChartViewer参数
        self.apps_config = self._get_apps_config()

        # 清理构建目录和缓存
        self.clean_build_dirs()

    def _get_apps_config(self):
        """获取应用程序配置列表

        Returns:
            list: 应用程序配置列表
        """
        build_path = Path(self.build_path)

        # 定义共同的隐藏导入
        common_spec_hidden_imports = [
            "matplotlib.backends.backend_svg", "docx"]

        return [
            {
                "name": "BatteryAnalysis",
                "display_name": "BatteryTest-DataConverter",
                "build_dir": build_path / "Build_BatteryAnalysis",
                "main_file_path": self.project_root / "src" / "battery_analysis" / "main" / "main_window.py",
                "main_file": '["main_window.py"]',
                "base_exe_name": "battery-analyzer",
                "icon_name": "Icon_BatteryAnalysis.ico",
                "spec_hidden_imports": common_spec_hidden_imports + [
                    "battery_analysis", "battery_analysis.main",
                    "battery_analysis.ui", "battery_analysis.utils",
                    "battery_analysis.main.battery_chart_viewer"
                ],
                "additional_hidden_imports": [
                    "openpyxl", "battery_analysis.utils.version",
                    "battery_analysis.utils.file_writer",
                    "battery_analysis.utils.battery_analysis",
                    "battery_analysis.ui.ui_main_window"
                ],
                "pyinstaller_args": []
            }
        ]

    def run_build(self):
        """执行完整的构建流程

        包括文件复制、构建和文件移动等步骤
        """
        try:
            # 执行构建流程
            self.copy2dir()
            self.build()
            self.move_programs()

            # 构建完成后自动打开exe所在文件夹
            final_build_dir = self.project_root / 'build' / self.build_type
            logger.info("正在打开构建文件夹: %s", final_build_dir)
            os.startfile(final_build_dir)
        except (OSError, IOError, FileNotFoundError, PermissionError) as e:
            logger.error("构建过程中出错: %s", e)

    def clean_build_dirs(self):
        """清理构建目录和缓存"""
        logger.info("开始清理构建目录和缓存...")

        # 清理临时构建目录
        if self.temp_build_dir.exists():
            logger.info("清理临时构建目录: %s", self.temp_build_dir)
            shutil.rmtree(self.temp_build_dir)

        # 清理最终构建目录（对应当前构建类型）
        final_build_type_dir = self.project_root / 'build' / self.build_type
        if final_build_type_dir.exists():
            logger.info("清理最终构建目录: %s", final_build_type_dir)
            shutil.rmtree(final_build_type_dir)

        # 创建必要的目录
        self.temp_build_dir.mkdir(parents=True, exist_ok=True)
        logger.info("构建目录清理完成")


    def move_programs(self):
        """移动构建好的程序到最终位置"""
        logger.info('开始移动文件...')
        # 使用项目根目录作为基础路径，添加构建类型子目录
        build_dir = self.project_root / 'build' / self.build_type
        build_dir.mkdir(parents=True, exist_ok=True)

        # 使用build()中已生成的可执行文件名
        exe_names = []
        for app_config in self.apps_config:
            exe_name = f'{app_config["exe_name"]}.exe'
            exe_names.append(exe_name)

        # 检查可执行文件是否存在于正确的位置（由于使用了--distpath，文件直接生成在build_dir）
        for exe_name in exe_names:
            exe_path = build_dir / exe_name
            if exe_path.exists():
                logger.info("确认: %s 已在目标目录中", exe_path)
            else:
                logger.warning("警告: %s 不存在", exe_path)

        # 不再复制pyproject.toml到构建目录，版本号已直接在构建脚本中处理

        # 创建setting.ini - 保留原始注释
        config_path = self.project_root / "config" / "setting.ini"
        if config_path.exists():
            # 直接读取原始文件内容
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 手动修改需要更改的部分
            import re
            # 先找到PltConfig section的位置
            plt_config_pattern = re.compile(r'(\[PltConfig\])(.*?)(?:\[|$)', re.DOTALL)
            match = plt_config_pattern.search(content)
            if match:
                # 替换整个PltConfig section
                updated_plt_config = '[PltConfig]\nPath=\nTitle=\n'
                content = plt_config_pattern.sub(updated_plt_config, content)
            
            # 写入修改后的内容
            with open(build_dir / "setting.ini", 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("已创建: %s", build_dir / 'setting.ini')
        else:
            logger.warning("%s 不存在，无法创建setting.ini", config_path)

        # 清理临时构建目录
        build_path = Path(self.build_path)
        if build_path.exists():
            shutil.rmtree(build_path)
            logger.info("已清理临时构建目录: %s", build_path)

    def _copy_app_resources(self, build_dir, app_name, main_file_path):
        """复制主程序文件到构建目录（PyInstaller 入口脚本所需）

        Args:
            build_dir: 构建目录路径
            app_name: 应用名称
            main_file_path: 主程序文件路径
        """
        # 复制主程序文件（PyInstaller 以它为入口分析依赖）
        shutil.copy(main_file_path, build_dir)
        logger.info("已复制主程序文件到%s: %s", app_name, main_file_path.name)

    def copy2dir(self):
        """复制源文件到构建目录"""
        build_path = Path(self.build_path)
        if build_path.exists():
            shutil.rmtree(build_path)
        build_path.mkdir(parents=True, exist_ok=True)

        # 复制pyproject.toml到临时目录，确保Version类能读取到正确的版本号
        pyproject_src = self.project_root / "pyproject.toml"
        pyproject_dest = build_path / "pyproject.toml"
        if pyproject_src.exists():
            shutil.copy2(pyproject_src, pyproject_dest)
            logger.info("已将pyproject.toml复制到构建目录: %s", pyproject_dest)

        # 复制所有应用的资源
        for app_config in self.apps_config:
            # 创建构建目录
            app_config["build_dir"].mkdir(parents=True, exist_ok=True)
            logger.info("创建应用构建目录: %s", app_config["name"])

            # 复制应用资源
            self._copy_app_resources(
                app_config["build_dir"],
                app_config["name"],
                app_config["main_file_path"]
            )

    def _find_python_dll(self):
        """查找Python DLL路径"""
        # 1. 优先检查CI环境变量中设置的DLL路径（用于GitHub Actions）
        ci_dll_path = os.environ.get('PYTHON_DLL_PATH')
        if ci_dll_path and os.path.exists(ci_dll_path):
            logger.info("使用CI环境变量中的Python DLL路径: %s", ci_dll_path)
            return ci_dll_path

        # 2. 本地环境查找，使用当前Python版本动态构造DLL名称
        python_dll = f"python{sys.version_info.major}{sys.version_info.minor}.dll"
        python_exec_dir = Path(sys.executable).parent
        candidates = [
            python_exec_dir / python_dll,
            Path(sys.prefix) / python_dll,
            Path(sys.prefix) / "DLLs" / python_dll,
            Path(python_dll),  # 让PyInstaller尝试在PATH中查找
        ]

        for path in candidates:
            if path.exists():
                logger.info("找到Python DLL: %s", path)
                return str(path)

        logger.warning("未找到Python DLL %s，PyInstaller可能无法在某些环境中正常运行", python_dll)
        logger.debug("尝试过的路径: %s", [str(p) for p in candidates])
        return None

    def _execute_pyinstaller_command(self, app_dir, cmd_args):
        """执行PyInstaller命令"""
        try:
            result = subprocess.run(
                cmd_args,
                cwd=app_dir,
                check=False,
                capture_output=True,
                encoding='utf-8'
            )
            logger.info("构建结果: %s", result.returncode)
            if result.stderr:
                logger.error("错误输出: %s", result.stderr)
            return result
        except (FileNotFoundError, PermissionError, OSError, subprocess.SubprocessError) as e:
            logger.error("执行命令时出错: %s", e)
            return subprocess.CompletedProcess(cmd_args, 1)

    def _generate_exe_name(self, base_name, architecture):
        """生成可执行文件名
        
        Args:
            base_name: 基础文件名
            architecture: 系统架构
            
        Returns:
            完整的可执行文件名（不带.exe后缀）
        """
        suffix = "_debug" if self.build_type != "Release" else ""
        return f"{base_name}_{self.version}_{architecture}{suffix}"

    def _build_pyinstaller_args(self, app_config, temp_path, src_path, final_build_dir):
        """构建PyInstaller命令参数
        
        Args:
            app_config: 应用程序配置
            temp_path: 临时目录路径
            src_path: 源代码目录路径
            final_build_dir: 最终构建目录路径
            
        Returns:
            list: PyInstaller命令参数列表
        """
        # 构建通用PyInstaller参数
        cmd_args = [
            sys.executable, '-m', 'PyInstaller',
            '--log-level=INFO',
            '--hidden-import=pywintypes',
            f'--name={app_config["exe_name"]}',
            f'--icon={app_config["icon_name"]}',
            f'--distpath={final_build_dir}',
            f'--workpath={temp_path}/{app_config["name"]}',
            '--onefile',  # 使用统一的单文件模式
            f'--add-data={src_path};.'
        ]
        
        # 应用特定参数（battery_analysis 整体已通过 src;. 包含，无需重复添加）

        # 添加所有隐藏导入
        for hidden_import in app_config["spec_hidden_imports"] + app_config["additional_hidden_imports"]:
            cmd_args.append(f'--hidden-import={hidden_import}')
        
        # 添加main文件
        import ast
        main_files = ast.literal_eval(app_config["main_file"])
        cmd_args.append(main_files[0])
        
        # 添加应用程序特定参数
        cmd_args.extend(app_config["pyinstaller_args"])
        
        # 添加通用参数
        cmd_args.extend([
            '--add-data', f'{os.path.abspath(os.path.join(self.project_root, "config"))};config',
            '--add-data', f'{os.path.abspath(os.path.join(self.project_root, "config", "setting.ini"))};.',
            '--add-data', f'{os.path.abspath(os.path.join(self.project_root, "pyproject.toml"))};.',
            '--add-data', f'{os.path.abspath(os.path.join(self.project_root, "locale"))};locale',
            '--path', f'{src_path}',
            '--path', f'{self.project_root}'
        ])
        
        # 添加必要的隐藏导入
        cmd_args.extend([
            '--hidden-import', 'xlsxwriter',
            '--hidden-import', 'openpyxl',
            '--hidden-import', 'xlrd'
        ])
        
        # 添加排除不必要模块的配置
        excluded_modules = [
            'pytest', 'pylint', 'black', 'astroid', 'pylint_json2html',  # 开发测试工具
            'matplotlib.tests', 'matplotlib.backends.backend_qt4', 'matplotlib.backends.backend_qt5',  # 不使用的matplotlib模块
            'numpy.testing', 'numpy.distutils',  # numpy测试和构建模块
            'openpyxl.tests',  # openpyxl测试模块
            'pandas.tests',  # pandas测试模块
            'tkinter',  # 只使用PyQt6
            'IPython', 'jupyter',  # 交互式环境（非依赖，但体量大，防误打包）
            'setuptools', 'pip',  # 构建工具
        ]
        for module in excluded_modules:
            cmd_args.append(f'--exclude-module={module}')
        
        # 添加调试/控制台参数
        debug_mode = self.build_type == "Debug"
        if self.console_mode or debug_mode:
            cmd_args.append('--console')
        else:
            cmd_args.append('--noconsole')
        
        if not debug_mode:
            cmd_args.append('--strip')
        
        # 查找Python DLL并添加到命令参数
        python_dll = self._find_python_dll()
        if python_dll:
            cmd_args.append(f'--add-binary={python_dll};.')
        else:
            logger.warning("Could not find python313.dll")
        
        return cmd_args
    
    def build(self):
        """构建应用程序"""
        logger.info('开始构建...')
        # 确保临时目录存在
        temp_path = self.temp_build_dir
        temp_path.mkdir(parents=True, exist_ok=True)

        # 确保构建目录存在
        build_path = Path(self.build_path)
        build_path.mkdir(parents=True, exist_ok=True)

        # 确保最终构建目录存在
        final_build_dir = self.project_root / 'build' / self.build_type
        final_build_dir.mkdir(parents=True, exist_ok=True)

        src_path = self.project_root / 'src'
        architecture = "x64"

        # 复制必要的图标
        icon_path = self.project_root / 'config' / 'resources' / 'icons' / 'Icon_BatteryTestGUI.ico'
        if icon_path.exists():
            for app in self.apps_config:
                shutil.copy2(icon_path, app["build_dir"] / app["icon_name"])
                logger.info("已复制图标文件到%s: %s", app["name"], app["icon_name"])

        # 构建两个应用程序
        for app_config in self.apps_config:
            # 生成可执行文件名
            app_config["exe_name"] = self._generate_exe_name(app_config["base_exe_name"], architecture)

            # 构建PyInstaller命令参数
            cmd_args = self._build_pyinstaller_args(app_config, temp_path, src_path, final_build_dir)
            
            # 执行PyInstaller命令
            self._execute_pyinstaller_command(app_config["build_dir"], cmd_args)

        # 清理临时文件
        if temp_path.exists():
            shutil.rmtree(temp_path)
        logger.info('构建完成，可执行文件位于: %s', final_build_dir)


def main():
    """
    主函数，处理命令行参数并执行构建流程
    """
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='构建BatteryAnalysis和ImageMaker应用程序')
    parser.add_argument('build_type', choices=['Debug', 'Release'], 
                       help='构建类型: Debug 或 Release')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='显示详细日志信息')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 如果请求详细日志，将日志级别设置为DEBUG
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # 创建BuildManager实例并执行构建
        build_manager = BuildManager(args.build_type)
        build_manager.run_build()  # 调用run_build方法执行完整构建流程
        logger.info('%s 构建完成', args.build_type)
    except (OSError, IOError, FileNotFoundError, PermissionError, ValueError) as e:
        logger.error("构建失败: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
