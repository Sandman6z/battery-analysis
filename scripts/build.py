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
logging.basicConfig(level=logging.INFO,
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
            logger.warning("无法从Version类获取版本号: %s，使用默认版本", e)
            self.version = "0.0.0"

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
                "datas_mapping": {"src": ".", "battery_analysis": "battery_analysis"},
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

        # 确定系统架构
        architecture = "x64"

        # 使用_generate_exe_name方法生成文件名，避免重复逻辑
        exe_names = []
        for app_config in self.apps_config:
            exe_name = f"{self._generate_exe_name(app_config['base_exe_name'], architecture)}.exe"
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

    def _write_file(self, content, file_path):
        """写入文件的辅助方法"""
        # 确保目录存在
        file_path_obj = Path(file_path)
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path_obj, "w", encoding='utf-8') as f:
            f.write(content)

    def _copy_svg_icons(self, target_dir, app_name):
        """复制SVG图标文件到目标目录"""
        svg_dir = self.project_root / "config" / "resources" / "icons"
        if svg_dir.exists():
            # 创建目标目录
            dest_svg_dir = target_dir / "config" / "resources" / "icons"
            dest_svg_dir.mkdir(parents=True, exist_ok=True)
            # 复制所有SVG文件
            for svg_file in svg_dir.glob("*.svg"):
                shutil.copy(svg_file, dest_svg_dir)
                logger.info("已复制SVG图标到%s: %s", app_name, svg_file.name)

    def _copy_app_resources(self, build_dir, app_name, main_file_path):
        """复制单个应用的资源文件到构建目录

        Args:
            build_dir: 构建目录路径
            app_name: 应用名称
            main_file_path: 主程序文件路径
        """
        # 定义源文件路径
        resources_rc_path = self.project_root / "src" / \
            "battery_analysis" / "resources" / "resources_rc.py"
        ui_path = self.project_root / "src" / "battery_analysis" / \
            "ui" / "resources" / "ui_battery_analysis.ui"
        battery_analysis_src = self.project_root / "src" / "battery_analysis"

        # 复制主程序文件
        shutil.copy(main_file_path, build_dir)
        logger.info("已复制主程序文件到%s: %s", app_name, main_file_path.name)

        # 复制资源文件
        resources_dest = build_dir / "resources"
        resources_dest.mkdir(exist_ok=True)
        shutil.copy(resources_rc_path, resources_dest)
        logger.info("已复制资源文件到%s: %s", app_name, resources_rc_path.name)

        # 复制SVG图标文件
        self._copy_svg_icons(build_dir, app_name)

        # 确保UI目录存在并复制UI文件
        if app_name == "BatteryAnalysis":
            ui_dest_dir = build_dir / "battery_analysis" / "ui" / "resources"
            ui_dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(ui_path, ui_dest_dir)
            logger.info("已复制UI文件到%s: %s", app_name, ui_path.name)

        # 创建完整的battery_analysis包结构
        battery_analysis_dest = build_dir / "battery_analysis"
        shutil.copytree(battery_analysis_src,
                        battery_analysis_dest, dirs_exist_ok=True)
        logger.info("已复制battery_analysis包结构到%s", app_name)

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
        else:
            logger.debug("未找到CI环境变量中的Python DLL路径，尝试本地路径")
            
            # 获取当前Python版本号（如311, 313）
            import sys
            python_version = f"python{sys.version_info.major}{sys.version_info.minor}.dll"
            logger.debug(f"当前Python版本DLL: {python_version}")
            
            # 2. 本地环境的基本路径查找，包括更全面的可能路径
            python_exec_dir = Path(sys.executable).parent
            basic_paths = [
                # 当前Python版本的DLL
                os.path.join(os.path.dirname(sys.executable), python_version),
                python_exec_dir / python_version,
                os.path.join(os.path.dirname(os.path.dirname(sys.executable)), python_version),
                os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'DLLs', python_version),
                os.path.join(os.environ.get('PYTHONHOME', ''), python_version),
                Path(sys.prefix) / python_version,
                # 常见的Python 3.13版本DLL
                os.path.join(os.path.dirname(sys.executable), 'python313.dll'),
                python_exec_dir / 'python313.dll',
                os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'python313.dll'),
                os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'DLLs', 'python313.dll'),
                os.path.join(os.environ.get('PYTHONHOME', ''), 'python313.dll'),
                Path(sys.prefix) / 'python313.dll',
                # CI环境中常见的Python安装路径
                r'C:\Program Files\python313\python313.dll',
                r'C:\Program Files (x86)\python313\python313.dll',
                # 让PyInstaller尝试在PATH中查找
                python_version,
                'python313.dll'
            ]

            # 去重路径列表
            basic_paths = list(set(basic_paths))

            for path in basic_paths:
                logger.debug("检查DLL路径: %s", path)
                if os.path.exists(path):
                    logger.info("找到Python DLL: %s", path)
                    return str(path)

            # 如果未找到DLL，记录警告
            logger.warning("未找到Python DLL，这可能会导致构建的可执行文件在某些环境中无法正常运行")
            logger.debug("尝试过的路径: %s", ', '.join(str(p) for p in basic_paths))
            return None

    def _generate_spec_content(self, app_name, exe_name, icon_name, main_file, datas_mapping, spec_hidden_imports):
        """生成PyInstaller spec文件内容"""
        debug_mode = self.build_type == "Debug"

        # 获取应用程序的显示名
        app_display_name = None
        for config in self.apps_config:
            if config["name"] == app_name:
                app_display_name = config.get("display_name", config["name"])
                break
        if app_display_name is None:
            app_display_name = app_name

        # 使用pathlib的as_posix()方法自动处理路径分隔符
        project_root_posix = self.project_root.as_posix()
        src_path = self.project_root / 'src'
        src_path_posix = src_path.as_posix()
        config_path_posix = (self.project_root / 'config').as_posix()
        pyproject_path_posix = (
            self.project_root / 'pyproject.toml').as_posix()

        # 构建datas
        datas = []
        datas.append(
            f'("{src_path_posix}", "{datas_mapping.get("src", ".")}")')

        if app_name == "BatteryAnalysis":
            battery_analysis_path_posix = (
                src_path / "battery_analysis").as_posix()
            datas.append(
                f'("{battery_analysis_path_posix}", "battery_analysis")')

        datas.append(f'("{config_path_posix}", "config")')
        datas.append(f'("{pyproject_path_posix}", ".")')
        
        # 添加locale目录，确保翻译文件被正确包含
        locale_path_posix = (self.project_root / 'locale').as_posix()
        datas.append(f'("{locale_path_posix}", "locale")')
        
        datas_str = ',\n        '.join(datas)

        # 构建hiddenimports字符串
        hiddenimports_str = ', '.join(
            f'"{imp}"' for imp in spec_hidden_imports)

        # 构建控制台模式字符串
        console_mode = str(self.console_mode or debug_mode).lower()
        debug_mode_str = str(debug_mode).lower()
        strip_mode = str(not debug_mode).lower()
        upx_mode = "false"  # 禁用UPX压缩，避免可能的问题

        # 先处理版本号分割，以便在spec模板中使用
        # 确保版本号严格按照pyproject.toml中的3位语义化格式处理
        version_split = self.version.split(".")
        # 只保留前3位（MAJOR.MINOR.PATCH），移除任何额外的后缀（如.debug）
        if len(version_split) > 3:
            version_split = version_split[:3]
        while len(version_split) < 3:
            version_split.append("0")
        # Windows VERSIONINFO需要4位版本号，但我们固定build number为0
        # 确保不影响用户看到的3位语义化版本格式
        build_number = "0"
            
        # 使用字符串拼接构建spec_content，确保变量正确解析
        # 先定义VSVersionInfo模板
        vs_version_info_template = '''VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=({0}, {1}, {2}, {3}),
        prodvers=({0}, {1}, {2}, {3}),
        mask=0x3f,
        flags=0x0,
        OS=0x4,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(
                u'040904B0',
                [
                    StringStruct(u'CompanyName',
                                 u'BOE Digital Technology Co., Ltd.'),
                    StringStruct(u'FileDescription', u'{4}'),
                    StringStruct(
                        u'LegalCopyright', u'Copyright (C) 2023 BOE Digital Technology Co., Ltd.'),
                    StringStruct(u'ProductName', u'{4}'),
                    StringStruct(u'ProductVersion', version)
                ]
            )
        ]),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
    ]
)'''
        
        # 格式化VSVersionInfo模板
        vs_version_info = vs_version_info_template.format(
            version_split[0], version_split[1], version_split[2], build_number, app_name
        )
        
        # 构建完整的spec_content
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-

# 这段代码用于创建Windows文件属性中显示的版本信息
def generate_version_info(app_name):
    version = "{version_str}"
    return '''"""
{vs_version_info}
"""'''

block_cipher = None
a = Analysis(
    [{main_file}],
    pathex=["{project_root_posix}", "{src_path_posix}"],
    binaries=[],
    datas=[
        {datas_str}
    ],
    hiddenimports=[
        {hiddenimports_str}
    ],
    hookspath=[],
    hooksconfig={{
    }},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="{exe_name}",
    debug={debug_mode_str},
    bootloader_ignore_signals=False,
    strip={strip_mode},
    upx={upx_mode},
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_mode},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="./{icon_name}",
    version=generate_version_info("{app_display_name}"),
)'''.format(
            version_str=self.version,
            vs_version_info=vs_version_info,
            app_display_name=app_display_name,
            main_file=main_file,
            project_root_posix=project_root_posix,
            src_path_posix=src_path_posix,
            datas_str=datas_str,
            hiddenimports_str=hiddenimports_str,
            exe_name=exe_name,
            debug_mode_str=debug_mode_str,
            strip_mode=strip_mode,
            upx_mode=upx_mode,
            console_mode=console_mode,
            icon_name=icon_name
        )
        return spec_content

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
        
        # 添加应用特定的数据文件
        if app_config["name"] == "BatteryAnalysis":
            cmd_args.append(f'--add-data={os.path.join(src_path, "battery_analysis")};battery_analysis')
        
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
            '--add-data', f'{os.path.abspath(os.path.join(self.project_root, "config", "resources", "icons"))};config/resources/icons',
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
            'scipy', 'sympy',  # 如果没有使用这些科学计算库
            'tkinter',  # 如果只使用PyQt6
            'IPython', 'jupyter',  # 交互式环境
            'setuptools', 'pip',  # 构建工具
            'unittest', 'doctest',  # 测试框架
            'urllib3', 'requests',  # 如果没有网络请求
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
            
            # 生成spec文件内容
            spec_content = self._generate_spec_content(
                app_config["name"],
                app_config["exe_name"],
                app_config["icon_name"],
                app_config["main_file"],
                app_config["datas_mapping"],
                app_config["spec_hidden_imports"]
            )
            
            # 写入spec文件
            spec_file_path = app_config["build_dir"] / 'build.spec'
            self._write_file(spec_content, spec_file_path)
            logger.info("已生成spec文件: %s", spec_file_path)
            
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
