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

# tomllib 仅在 Python 3.11+ 可用，用于读取 pyproject.toml
import tomllib

# 配置日志记录
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

        # 从pyproject.toml读取版本号（版本号中心化管理）
        try:
            with open(self.project_root / "pyproject.toml", "rb") as f:
                pyproject_data = tomllib.load(f)
            self.version = pyproject_data.get(
                "project", {}).get("version", "0.0.0")
        except (FileNotFoundError, PermissionError, OSError, tomllib.TOMLDecodeError) as e:
            logger.warning("无法从pyproject.toml读取版本号: %s，使用默认版本", e)
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
        self.console = self.console_mode

        # 清理构建目录和缓存
        self.clean_build_dirs()

        # 保存原始__init__.py内容，以便构建后恢复
        original_init_content = None

        try:
            # 在构建前嵌入版本号
            original_init_content = self.embed_version_in_init()

            # 执行构建流程
            self.setup_version()
            self.copy_source_files()
            self.generate_version_info()
            self.build_applications()
            self.move_programs()
        finally:
            # 构建完成后恢复原始__init__.py文件
            if original_init_content:
                try:
                    init_file_path = self.project_root / "src" / "battery_analysis" / "__init__.py"
                    with open(init_file_path, 'w', encoding='utf-8') as f:
                        f.write(original_init_content)
                    logger.info("已恢复原始__init__.py文件")
                except (FileNotFoundError, PermissionError, IsADirectoryError,
                    OSError, UnicodeEncodeError) as e:
                    logger.error("恢复原始__init__.py文件时出错: %s", e)

    def embed_version_in_init(self):
        """在构建前将版本号嵌入到__init__.py文件中"""
        init_file_path = self.project_root / "src" / "battery_analysis" / "__init__.py"

        try:
            # 读取原始文件内容
            with open(init_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换版本号占位符 - 使用更健壮的方式匹配和替换
            # 分别替换两行，避免因为不可见字符导致的精确匹配失败
            content = content.replace('# 版本号将在构建时被替换为实际值', '# 构建时嵌入的实际版本号')
            content = content.replace(
                'return "2.0.0"', f'return "{self.version}"')

            updated_content = content

            # 写回文件
            with open(init_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            logger.info("已将版本号 %s 嵌入到 %s", self.version, init_file_path)

            # 返回原始内容，以便稍后恢复
            return content
        except (FileNotFoundError, PermissionError, IsADirectoryError,
                    OSError, UnicodeDecodeError) as e:
            logger.error("嵌入版本号时出错: %s", e)
            return None

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

    def copy_source_files(self):
        """复制源代码文件到构建目录"""
        return self.copy2dir()

    def generate_version_info(self):
        """生成版本信息文件"""
        # 在构建目录中创建version.txt文件（统一为两个应用生成）
        build_path = Path(self.build_path)
        
        # 定义应用程序列表，包含目录名和显示名
        apps = [
            {'dir_name': 'Build_BatteryAnalysis', 'app_name': 'BatteryTest-DataConverter'},
            {'dir_name': 'Build_ImageShow', 'app_name': 'BatteryTest-ImageMaker'}
        ]
        
        # 循环处理每个应用程序
        for app in apps:
            app_dir = build_path / app['dir_name']
            if app_dir.exists():
                self._write_file(
                    self._generate_vs_version_info("test", app['app_name']),
                    app_dir / 'version.txt'
                )

    def _generate_vs_version_info(self, commit_id, app_name):
        """生成Visual Studio版本信息结构"""
        version_split = self.version.split(".")
        for i, version_part in enumerate(version_split):
            if version_part == "-1":
                version_split[i] = "0"

        # 确保版本号至少有三位，不足则补0
        while len(version_split) < 3:
            version_split.append("0")

        # Windows版本信息需要四位数字，第四位使用0或构建号
        build_number = "0"
        if len(version_split) > 3:
            build_number = version_split[3]

        return f"""# UTF-8
VSVersionInfo(
    ffi=FixedFileInfo(
        #filevers和prodvers应该始终是包含四个项的元组:(1、2、3、4),将不需要的项设置为0
        filevers=({version_split[0]}, {version_split[1]}, {version_split[2]}, {build_number}),  # 文件版本
        prodvers=({version_split[0]}, {version_split[1]}, {version_split[2]}, {build_number}), # 产品版本
        mask=0x3f, # 两个位掩码
        flags=0x0,
        OS=0x4, # 为其设计此文件的操作系统,0x4-NT
        fileType=0x1, # 文件的常规类型, 0x1-该文件是一个应用程序
        subtype=0x0, # 文件的功能, 0x0表示该文件类型未定义
        date=(0, 0) # 创建日期和时间戳
    ),
    kids=[
        StringFileInfo([
            StringTable(
                u'040904B0', 
                [
                    StringStruct(u'CompanyName', u'BOE Digital Technology Co., Ltd.'),
                    StringStruct(u'FileDescription', u'{app_name}'),
                    StringStruct(u'LegalCopyright', u'Copyright (C) 2023 BOE Digital Technology Co., Ltd.'),
                    StringStruct(u'ProductName', u'{app_name}'),
                    StringStruct(u'ProductVersion', u'{self.build_type}_{commit_id}')
                ]
            )
        ]),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])]) # 语言, USA
    ]
)"""

    def build_applications(self):
        """构建应用程序"""
        return self.build()

    def move_programs(self):
        """移动构建好的程序到最终位置"""
        logger.info('开始移动文件...')
        # 使用项目根目录作为基础路径，添加构建类型子目录
        build_dir = self.project_root / 'build' / self.build_type
        build_dir.mkdir(parents=True, exist_ok=True)

        # 确定系统架构
        architecture = "x64"

        # 根据构建类型生成相应的文件名格式
        if self.build_type == "Release":
            # Release版本：battery-analyzer_2.0.0_x64.exe
            dataconverter_exe_name = f"battery-analyzer_{self.version}_{architecture}.exe"
            imagemaker_exe_name = f"battery-analysis-visualizer_{self.version}_{architecture}.exe"
        else:
            # Debug版本：battery-analyzer_2.0.0_x64_debug.exe
            dataconverter_exe_name = f"battery-analyzer_{self.version}_{architecture}_debug.exe"
            # 使用字符串拼接代替f-string以减少行长度
            imagemaker_exe_name = "battery-analysis-visualizer_" + \
                f"{self.version}_{architecture}_debug.exe"

        # 检查可执行文件是否存在于正确的位置（由于使用了--distpath，文件直接生成在build_dir）
        exe_path = build_dir / dataconverter_exe_name
        if exe_path.exists():
            logger.info("确认: %s 已在目标目录中", exe_path)
        else:
            logger.warning("警告: %s 不存在", exe_path)

        exe_path = build_dir / imagemaker_exe_name
        if exe_path.exists():
            logger.info("确认: %s 已在目标目录中", exe_path)
        else:
            logger.warning("警告: %s 不存在", exe_path)

        # 不再复制pyproject.toml到构建目录，版本号已直接在构建脚本中处理

        # 创建setting.ini
        config = CaseSensitiveConfigParser()
        config_path = self.project_root / "config" / "setting.ini"
        if config_path.exists():
            config.read(str(config_path), encoding='utf-8')
            if config.has_section("PltConfig"):
                config.set("PltConfig", "Path", "")
                config.set("PltConfig", "Title", "")
            with open(build_dir / "setting.ini", 'w', encoding='utf-8') as f:
                config.write(f)
            logger.info("已创建: %s", build_dir / 'setting.ini')
        else:
            logger.warning("%s 不存在，无法创建setting.ini", config_path)

        # 清理临时构建目录
        build_path = Path(self.build_path)
        if build_path.exists():
            shutil.rmtree(build_path)
            logger.info("已清理临时构建目录: %s", build_path)

    def setup_version(self):
        """设置版本信息"""
        # 无论是Debug还是Release模式，版本号都直接从pyproject.toml读取，不进行版本更新操作

    def _write_file(self, content, file_path):
        """写入文件的辅助方法"""
        # 确保目录存在
        file_path_obj = Path(file_path)
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path_obj, "w", encoding='utf-8') as f:
            f.write(content)

    def update_version_and_commit(self):
        """更新版本并提交更改 - 该方法已废弃，版本号直接从pyproject.toml读取"""
        logger.warning("版本号管理已简化，直接从pyproject.toml读取，不再需要更新版本和提交更改")

    def _update_version_files(self):
        """更新版本相关文件 - 该方法已废弃"""
        logger.warning("版本号管理已简化，不再需要更新版本文件")

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

    def copy2dir(self):
        """复制源文件到构建目录"""
        build_path = Path(self.build_path)
        if build_path.exists():
            shutil.rmtree(build_path)
        build_path.mkdir(parents=True, exist_ok=True)

        # 创建两个应用的构建目录
        battery_analysis_dir = build_path / "Build_BatteryAnalysis"
        image_show_dir = build_path / "Build_ImageShow"
        battery_analysis_dir.mkdir()
        image_show_dir.mkdir()

        # 定义源文件路径
        main_window_path = self.project_root / "src" / \
            "battery_analysis" / "main" / "main_window.py"
        image_show_path = self.project_root / "src" / \
            "battery_analysis" / "main" / "image_show.py"
        resources_rc_path = self.project_root / "src" / \
            "battery_analysis" / "resources" / "resources_rc.py"
        icon_path = self.project_root / "config" / \
            "resources" / "icons" / "Icon_BatteryTestGUI.ico"
        ui_path = self.project_root / "src" / "battery_analysis" / \
            "ui" / "resources" / "ui_battery_analysis.ui"
        battery_analysis_src = self.project_root / "src" / "battery_analysis"

        # 复制BatteryAnalysis的文件
        shutil.copy(main_window_path, battery_analysis_dir)
        shutil.copy(resources_rc_path, battery_analysis_dir / "resources")

        # 复制SVG图标文件到构建目录
        self._copy_svg_icons(battery_analysis_dir, "BatteryAnalysis")
        
        # 确保UI目录存在并复制UI文件
        ui_dest_dir = battery_analysis_dir / "battery_analysis" / "ui" / "resources"
        ui_dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(ui_path, ui_dest_dir)

        # 创建完整的battery_analysis包结构
        battery_analysis_dest = battery_analysis_dir / "battery_analysis"
        # 使用dirs_exist_ok=True参数来允许目标目录存在
        shutil.copytree(battery_analysis_src,
                        battery_analysis_dest, dirs_exist_ok=True)

        # 复制ImageShow的文件
        shutil.copy(image_show_path, image_show_dir)
        shutil.copy(resources_rc_path, image_show_dir / "resources")

        # 复制SVG图标文件到ImageShow目录
        self._copy_svg_icons(image_show_dir, "ImageShow")

        # 为ImageShow也创建完整的battery_analysis包结构
        battery_analysis_dest_img = image_show_dir / "battery_analysis"
        # 使用dirs_exist_ok=True参数来允许目标目录存在
        shutil.copytree(battery_analysis_src,
                        battery_analysis_dest_img, dirs_exist_ok=True)

    def _find_python_dll(self):
        """查找Python DLL路径"""
        # 1. 优先检查CI环境变量中设置的DLL路径（用于GitHub Actions）
        ci_dll_path = os.environ.get('PYTHON_DLL_PATH')
        if ci_dll_path and os.path.exists(ci_dll_path):
            logger.info("使用CI环境变量中的Python DLL路径: %s", ci_dll_path)
            return ci_dll_path
        else:
            logger.info("未找到CI环境变量中的Python DLL路径，尝试本地路径")
            # 2. 本地环境的基本路径查找
            python_exec_dir = Path(sys.executable).parent
            basic_paths = [
                os.path.join(os.path.dirname(sys.executable), 'python311.dll'),
                os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'python311.dll'),
                os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'DLLs', 'python311.dll'),
                os.path.join(os.environ.get('PYTHONHOME', ''), 'python311.dll'),
                python_exec_dir / 'python311.dll',
                Path(sys.prefix) / 'python311.dll',
                'python311.dll'  # 让PyInstaller尝试在PATH中查找
            ]

            for path in basic_paths:
                logger.debug("检查DLL路径: %s", path)
                if os.path.exists(path):
                    logger.info("找到Python DLL: %s", path)
                    return str(path)

            # 如果未找到DLL，记录警告
            logger.warning("未找到Python DLL，这可能会导致构建的可执行文件在某些环境中无法正常运行")
            logger.warning("尝试过的路径: %s", ', '.join(str(p) for p in basic_paths))
            return None

    def _generate_spec_content(self, app_name, exe_name, icon_name, main_file, datas_mapping):
        """生成PyInstaller spec文件内容"""
        debug_mode = self.build_type == "Debug"
        project_root_escaped = str(self.project_root).replace('\\', '\\\\')
        src_path_escaped = str(self.project_root / 'src').replace('\\', '\\\\')

        # 构建hiddenimports
        hiddenimports = [
            "matplotlib.backends.backend_svg", "battery_analysis",
            "battery_analysis.main", "battery_analysis.ui",
            "battery_analysis.utils", "docx"
        ]
        if app_name == "ImageShow":
            hiddenimports.extend(["src", "src.battery_analysis", "src.battery_analysis.utils"])

        # 构建datas
        config_path = os.path.join(self.project_root, "config").replace("\\", "\\\\")
        pyproject_path = os.path.join(self.project_root, "pyproject.toml").replace("\\", "\\\\")
        
        # 先构建datas的各个元素
        datas_elements = [
            f'"{src_path_escaped}", "{datas_mapping.get("src", ".")}"',
            f'"{config_path}", "config"',
            f'"{pyproject_path}", "."'
        ]
        
        if app_name == "BatteryAnalysis":
            battery_analysis_path = os.path.join(src_path_escaped, "battery_analysis").replace("\\", "\\\\")
            datas_elements.insert(1, f'"{battery_analysis_path}", "battery_analysis"')
        
        # 然后用括号包裹每个元素
        datas = [f'({elem})' for elem in datas_elements]

        # 构建hiddenimports字符串
        hiddenimports_str = ', '.join(['"' + imp + '"' for imp in hiddenimports])
        
        # 构建控制台模式字符串
        console_mode = str(self.console_mode or debug_mode).lower()
        debug_mode_str = str(debug_mode).lower()
        strip_mode = str(not debug_mode).lower()
        upx_mode = str(not debug_mode).lower()
        
        # 使用字符串格式方法来构建完整的spec_content
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-
block_cipher = None
a = Analysis(
    [{0}],
    pathex=["{1}", "{2}"],
    binaries=[],
    datas=[
        {3}
    ],
    hiddenimports=[
        {4}
    ],
    hookspath=[],
    hooksconfig={{}},
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
    name="{5}",
    debug={6},
    bootloader_ignore_signals=False,
    strip={7},
    upx={8},
    upx_exclude=[],
    runtime_tmpdir=None,
    console={9},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="./{10}",
    version="version.txt",
)
'''.format(
    main_file,
    project_root_escaped,
    src_path_escaped,
    ',\n        '.join(datas),
    hiddenimports_str,
    exe_name,
    debug_mode_str,
    strip_mode,
    upx_mode,
    console_mode,
    icon_name
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

    def build(self):
        """构建应用程序"""
        logger.info('开始构建...')
        # 确保临时目录存在
        temp_path = self.project_root / '__temp__'
        temp_path.mkdir(parents=True, exist_ok=True)

        # 确保构建目录存在
        build_path = Path(self.build_path)
        build_path.mkdir(parents=True, exist_ok=True)

        # 确保 build 目录存在并添加构建类型子目录
        final_build_dir = self.project_root / 'build' / self.build_type
        final_build_dir.mkdir(parents=True, exist_ok=True)

        src_path = self.project_root / 'src'

        # 确定系统架构
        architecture = "x64"

        # 根据构建类型生成相应的文件名格式（注意：这里不带.exe后缀，PyInstaller会自动添加）
        if self.build_type == "Release":
            # Release版本：battery-analyzer_2.0.0_x64
            dataconverter_exe_name = f"battery-analyzer_{self.version}_{architecture}"
            imagemaker_exe_name = f"battery-analysis-visualizer_{self.version}_{architecture}"
        else:
            # Debug版本：battery-analyzer_2.0.0_x64_debug
            dataconverter_exe_name = f"battery-analyzer_{self.version}_{architecture}_debug"
            imagemaker_exe_name = f"battery-analysis-visualizer_{self.version}_{architecture}_debug"

        # 定义共同的隐藏导入
        common_spec_hidden_imports = [
            "matplotlib.backends.backend_svg",
            "docx"
        ]
        
        # 应用程序配置列表：统一管理BatteryAnalysis和ImageShow参数
        apps_config = [
            {
                "name": "BatteryAnalysis",
                "build_dir": build_path / "Build_BatteryAnalysis",
                "exe_name": dataconverter_exe_name,
                "icon_name": "Icon_BatteryAnalysis.ico",
                "main_file": '["main_window.py"]',
                "datas_mapping": {".": ".", "battery_analysis": "battery_analysis"},
                "spec_hidden_imports": common_spec_hidden_imports + [
                    "battery_analysis",
                    "battery_analysis.main", 
                    "battery_analysis.ui",
                    "battery_analysis.utils"
                ],
                "pyinstaller_args": [
                    '-F', 'main_window.py',
                    '--add-data', f'{src_path};.',
                    '--add-data', f'{os.path.join(src_path, "battery_analysis")};battery_analysis',
                    '--hidden-import', 'matplotlib.backends.backend_svg',
                    '--hidden-import', 'docx',
                    '--hidden-import', 'openpyxl',
                    '--hidden-import', 'battery_analysis',
                    '--hidden-import', 'battery_analysis.main',
                    '--hidden-import', 'battery_analysis.ui',
                    '--hidden-import', 'battery_analysis.utils',
                    '--hidden-import', 'battery_analysis.utils.version',
                    '--hidden-import', 'battery_analysis.utils.file_writer',
                    '--hidden-import', 'battery_analysis.utils.battery_analysis',
                    '--hidden-import', 'battery_analysis.ui.ui_main_window'
                ]
            },
            {
                "name": "ImageShow",
                "build_dir": build_path / "Build_ImageShow",
                "exe_name": imagemaker_exe_name,
                "icon_name": "Icon_ImageShow.ico",
                "main_file": '["image_show.py", "resources/resources_rc.py"]',
                "datas_mapping": {"src": "src"},
                "spec_hidden_imports": common_spec_hidden_imports + [
                    "src",
                    "src.battery_analysis", 
                    "src.battery_analysis.utils"
                ],
                "pyinstaller_args": [
                    '--onefile', 'image_show.py'
                ]
            }
        ]

        # 复制必要的图标
        icon_path = self.project_root / 'config' / 'resources' / 'icons' / 'Icon_BatteryTestGUI.ico'
        if icon_path.exists():
            for app in apps_config:
                app["build_dir"].mkdir(exist_ok=True)
                shutil.copy2(icon_path, app["build_dir"] / app["icon_name"])

        # 构建两个应用程序
        for app_config in apps_config:
            # 生成spec文件内容
            spec_content = self._generate_spec_content(
                app_config["name"],
                app_config["exe_name"],
                app_config["icon_name"],
                app_config["main_file"],
                app_config["datas_mapping"]
            )
            
            # 写入spec文件
            spec_file_path = app_config["build_dir"] / 'build.spec'
            with open(spec_file_path, 'w', encoding='utf-8') as f:
                f.write(spec_content)
            
            # 构建PyInstaller命令参数
            cmd_args = [
                sys.executable, '-m', 'PyInstaller',
                f'--name={app_config["exe_name"]}',
                f'--icon={app_config["icon_name"]}',
                f'--distpath={final_build_dir}',
                f'--workpath={temp_path}/{app_config["name"]}',
                '--log-level=DEBUG',
                '--noupx',
                '--version-file=version.txt',
                '--collect-all=pywin32'
            ]
            
            # 添加应用程序特定参数
            cmd_args.extend(app_config["pyinstaller_args"])
            
            # 添加通用参数
            cmd_args.extend([
                '--add-data', f'{os.path.abspath(os.path.join(self.project_root, "config"))};config',
                '--add-data', f'{os.path.abspath(os.path.join(self.project_root, "config", "resources", "icons"))};config/resources/icons',
                '--add-data', f'{os.path.abspath(os.path.join(self.project_root, "config", "setting.ini"))};.',
                '--add-data', f'{self.project_root / "pyproject.toml"};.',
                '--path', f'{src_path}',
                '--path', f'{self.project_root}'
            ])
            
            # 添加通用的隐藏导入和收集项
            cmd_args.extend([
                '--hidden-import', 'xlsxwriter',
                '--collect-all', 'xlsxwriter',
                '--collect-all', 'openpyxl',
                '--hidden-import', 'xlrd',
                '--collect-all', 'xlrd'
            ])
            
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
                logger.warning("Could not find python311.dll")
            
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
        logger.info(f'{args.build_type} 构建完成')
    except Exception as e:
        logger.error(f'构建失败: {e}')
        sys.exit(1)


if __name__ == "__main__":
    main()