import sys
import os
import shutil
import datetime
import configparser
import subprocess
from pathlib import Path
from git import Repo
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 检查PyInstaller是否已安装，如果未安装则提示用户安装build依赖
try:
    import PyInstaller
    logger.info(f"PyInstaller已安装: {PyInstaller.__version__}")
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

from src.battery_analysis.utils.exception_type import BuildException


class CaseSensitiveConfigParser(configparser.ConfigParser):
    """大小写敏感的配置解析器"""
    def optionxform(self, option_str):
        return option_str


class BuildConfig:
    """构建配置基类"""
    def __init__(self, build_type=None):
        self.script_dir = Path(__file__).absolute().parent
        # 项目根目录是scripts的上一级目录
        self.project_root = self.script_dir.parent
        self.temp_build_dir = self.project_root / "__temp__"
        self.final_build_dir = self.project_root / "build"
        
        # 从pyproject.toml读取版本号（版本号中心化管理）
        try:
            import tomllib
            with open(self.project_root / "pyproject.toml", "rb") as f:
                pyproject_data = tomllib.load(f)
            self.version = pyproject_data.get("project", {}).get("version", "0.0.0")
        except Exception as e:
            logger.warning(f"无法从pyproject.toml读取版本号: {e}，使用默认版本")
            self.version = "0.0.0"
        
        # 根据构建类型决定是否显示控制台窗口
        # Debug构建默认显示控制台窗口，Release构建默认不显示控制台窗口
        self.debug_mode = build_type == "Debug"
        self.console_mode = self.debug_mode
        # 补充说明：Release模式下，self.debug_mode为False，因此self.console_mode也为False
        # 这样就自动实现了Release模式不显示控制台的功能，无需额外编写Release模式的逻辑
        
        # 定义构建应用相关目录
        self.dataconverter_build_dir = self.temp_build_dir / "Build_BatteryAnalysis"
        self.imagemaker_build_dir = self.temp_build_dir / "Build_ImageShow"


class BuildManager(BuildConfig):
    """构建管理器"""
    def __init__(self, build_type):
        super().__init__(build_type)
        # 只支持Debug和Release两种构建类型
        if build_type not in ['Debug', 'Release']:
            raise ValueError(f"不支持的构建类型: {build_type}。只支持'Debug'和'Release'，或请检查大小写")
        self.build_type = build_type
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
                except Exception as e:
                    logger.error(f"恢复原始__init__.py文件时出错: {e}")
    
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
            content = content.replace('return "2.0.0"', f'return "{self.version}"')
            
            updated_content = content
            
            # 写回文件
            with open(init_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"已将版本号 {self.version} 嵌入到 {init_file_path}")
            
            # 返回原始内容，以便稍后恢复
            return content
        except Exception as e:
            logger.error(f"嵌入版本号时出错: {e}")
            return None
    
    def clean_build_dirs(self):
        """清理构建目录和缓存"""
        logger.info(f"开始清理构建目录和缓存...")
        
        # 清理临时构建目录
        if self.temp_build_dir.exists():
            logger.info(f"清理临时构建目录: {self.temp_build_dir}")
            shutil.rmtree(self.temp_build_dir)
        
        # 清理最终构建目录（对应当前构建类型）
        final_build_type_dir = self.project_root / 'build' / self.build_type
        if final_build_type_dir.exists():
            logger.info(f"清理最终构建目录: {final_build_type_dir}")
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
        if (build_path / 'Build_BatteryAnalysis').exists():
            self._write_file(
                self._generate_vs_version_info("test", "BatteryTest-DataConverter"),
                build_path / 'Build_BatteryAnalysis' / 'version.txt'
            )

        if (build_path / 'Build_ImageShow').exists():
            self._write_file(
                self._generate_vs_version_info("test", "BatteryTest-ImageMaker"),
                build_path / 'Build_ImageShow' / 'version.txt'
            )
    
    def _generate_vs_version_info(self, commit_id, app_name):
        """生成Visual Studio版本信息结构"""
        version_split = self.version.split(".")
        for i in range(len(version_split)):
            if version_split[i] == "-1":
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
            imagemaker_exe_name = f"battery-analysis-visualizer_{self.version}_{architecture}_debug.exe"
        
        # 检查可执行文件是否存在于正确的位置（由于使用了--distpath，文件直接生成在build_dir）
        exe_path = build_dir / dataconverter_exe_name
        if exe_path.exists():
            logger.info(f"确认: {exe_path} 已在目标目录中")
        else:
            logger.warning(f"警告: {exe_path} 不存在")

        exe_path = build_dir / imagemaker_exe_name
        if exe_path.exists():
            logger.info(f"确认: {exe_path} 已在目标目录中")
        else:
            logger.warning(f"警告: {exe_path} 不存在")
        
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
            logger.info(f"已创建: {build_dir / 'setting.ini'}")
        else:
            logger.warning(f"{config_path} 不存在，无法创建setting.ini")
        
        # 清理临时构建目录
        build_path = Path(self.build_path)
        if build_path.exists():
            shutil.rmtree(build_path)
            logger.info(f"已清理临时构建目录: {build_path}")

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
        """更新版本并提交更改"""
        if not self.git_repo or not self.git_index or not self.git:
            # 如果没有Git仓库，直接跳过版本更新检查
            logger.warning("Git仓库未初始化，跳过版本更新检查")
            return
        
        version_split = self.version.split(".")
        # 确保版本号至少有三位
        while len(version_split) < 3:
            version_split.append("0")
        
        if self.build_type == "Release":
            try:
                # 更新版本号，使用三位版本号格式
                try:
                    if self.git_repo.commit().message and "Release" in self.git_repo.commit().message:
                        # 保持主版本和次版本不变，修订号重置为0
                        self.version = f"{version_split[0]}.{version_split[1]}.0"
                    else:
                        # 增加修订号
                        self.version = f"{version_split[0]}.{version_split[1]}.{int(version_split[2])+1}"
                except Exception as e:
                    logger.warning(f"无法获取或解析提交消息: {e}，使用默认版本更新")
                    self.version = f"{version_split[0]}.{version_split[1]}.{int(version_split[2])+1}"
                
                self._update_version_files()
            except Exception as e:
                logger.warning(f"Release模式版本更新失败: {e}，使用当前版本继续")

    def _update_version_files(self):
        """更新版本相关文件 - Config_BatteryAnalysis.ini已在初始化时同步"""
        # 确保配置文件在根目录的config文件夹中也保持更新
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)

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
        main_window_path = self.project_root / "src" / "battery_analysis" / "main" / "main_window.py"
        image_show_path = self.project_root / "src" / "battery_analysis" / "main" / "image_show.py"
        resources_rc_path = self.project_root / "src" / "battery_analysis" / "resources" / "resources_rc.py"
        icon_path = self.project_root / "config" / "resources" / "icons" / "Icon_BatteryTestGUI.ico"
        ui_path = self.project_root / "src" / "battery_analysis" / "ui" / "resources" / "ui_battery_analysis.ui"
        battery_analysis_src = self.project_root / "src" / "battery_analysis"
        
        # 复制BatteryAnalysis的文件
        shutil.copy(main_window_path, battery_analysis_dir)
        shutil.copy(resources_rc_path, battery_analysis_dir / "resources")
        shutil.copy(icon_path, battery_analysis_dir / "Icon_BatteryAnalysis.ico")
        
        # 复制SVG图标文件到构建目录的config/resources/icons文件夹
        svg_dir = self.project_root / "config" / "resources" / "icons"
        if svg_dir.exists():
            # 创建目标目录
            dest_svg_dir = battery_analysis_dir / "config" / "resources" / "icons"
            dest_svg_dir.mkdir(parents=True, exist_ok=True)
            # 复制所有SVG文件
            for svg_file in svg_dir.glob("*.svg"):
                shutil.copy(svg_file, dest_svg_dir)
                logger.info(f"已复制SVG图标: {svg_file.name}")
        # 确保UI目录存在并复制UI文件
        ui_dest_dir = battery_analysis_dir / "battery_analysis" / "ui" / "resources"
        ui_dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(ui_path, ui_dest_dir)
        
        # 创建完整的battery_analysis包结构
        battery_analysis_dest = battery_analysis_dir / "battery_analysis"
        # 使用dirs_exist_ok=True参数来允许目标目录存在
        shutil.copytree(battery_analysis_src, battery_analysis_dest, dirs_exist_ok=True)

        # 复制ImageShow的文件
        shutil.copy(image_show_path, image_show_dir)
        shutil.copy(resources_rc_path, image_show_dir / "resources")
        shutil.copy(icon_path, image_show_dir / "Icon_ImageShow.ico")
        
        # 复制SVG图标文件到ImageShow的config/resources/icons文件夹
        if svg_dir.exists():
            # 创建目标目录
            dest_svg_dir_img = image_show_dir / "config" / "resources" / "icons"
            dest_svg_dir_img.mkdir(parents=True, exist_ok=True)
            # 复制所有SVG文件
            for svg_file in svg_dir.glob("*.svg"):
                shutil.copy(svg_file, dest_svg_dir_img)
                logger.info(f"已复制SVG图标到ImageShow: {svg_file.name}")
        
        # 为ImageShow也创建完整的battery_analysis包结构
        battery_analysis_dest_img = image_show_dir / "battery_analysis"
        # 使用dirs_exist_ok=True参数来允许目标目录存在
        shutil.copytree(battery_analysis_src, battery_analysis_dest_img, dirs_exist_ok=True)

    def build(self):
        """构建应用程序"""
        logger.info('开始构建...')
        # 确保临时目录存在
        temp_path = self.project_root / '__temp__'
        temp_path.mkdir(parents=True, exist_ok=True)
        
        # 确保构建目录存在
        build_path = Path(self.build_path)
        build_path.mkdir(parents=True, exist_ok=True)

        # 确保 Build_BatteryAnalysis 和 Build_ImageShow 目录存在
        battery_analysis_dir = build_path / 'Build_BatteryAnalysis'
        image_show_dir = build_path / 'Build_ImageShow'
        battery_analysis_dir.mkdir(exist_ok=True)
        image_show_dir.mkdir(exist_ok=True)

        # 确保 build 目录存在并添加构建类型子目录
        final_build_dir = self.project_root / 'build' / self.build_type
        final_build_dir.mkdir(parents=True, exist_ok=True)

        # 获取Python解释器路径
        python_exe = sys.executable
        
        # 复制必要的图标（如果copy2dir方法未处理）
        icon_path = self.project_root / 'config' / 'resources' / 'icons' / 'Icon_BatteryTestGUI.ico'
        if icon_path.exists():
            shutil.copy2(icon_path, battery_analysis_dir / 'Icon_BatteryAnalysis.ico')
            shutil.copy2(icon_path, image_show_dir / 'Icon_ImageShow.ico')
        
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

        # 为DataConverter生成spec文件
        # 构建参数设置，Debug模式和Release模式有所区别
        debug_mode = self.build_type == "Debug"

        # 使用简单的字符串拼接方式，并处理路径转义
        project_root_escaped = str(project_root).replace('\\', '\\\\')
        src_path_escaped = str(src_path).replace('\\', '\\\\')
        
        spec_content = '# -*- mode: python ; coding: utf-8 -*-\n'
        spec_content += 'block_cipher = None\n'
        spec_content += 'a = Analysis(\n'
        spec_content += '    ["main_window.py"],\n'
        spec_content += '    pathex=["' + project_root_escaped + '", "' + src_path_escaped + '"],\n'
        spec_content += '    binaries=[],\n'
        spec_content += '    datas=[("' + src_path_escaped + '", "."), ("' + os.path.join(src_path_escaped, 'battery_analysis').replace('\\', '\\\\') + '", "battery_analysis"), ("' + os.path.join(self.project_root, 'config').replace('\\', '\\\\') + '", "config"), ("' + os.path.join(self.project_root, 'pyproject.toml').replace('\\', '\\\\') + '", ".")],\n'
        spec_content += '    hiddenimports=["matplotlib.backends.backend_svg", "battery_analysis", "battery_analysis.main", "battery_analysis.ui", "battery_analysis.utils", "docx"],\n'
        spec_content += '    hookspath=[],\n'
        spec_content += '    hooksconfig={},\n' 
        spec_content += '    runtime_hooks=[],\n'
        spec_content += '    excludes=[],\n'
        spec_content += '    win_no_prefer_redirects=False,\n'
        spec_content += '    win_private_assemblies=False,\n'
        spec_content += '    cipher=block_cipher,\n'
        spec_content += '    noarchive=False,\n'
        spec_content += ')\n'
        spec_content += 'pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)\n'
        spec_content += 'exe = EXE(\n'
        spec_content += '    pyz,\n'
        spec_content += '    a.scripts,\n'
        spec_content += '    a.binaries,\n'
        spec_content += '    a.zipfiles,\n'
        spec_content += '    a.datas,\n'
        spec_content += '    [],\n'
        spec_content += '    name="' + dataconverter_exe_name + '",\n'
        spec_content += f'    debug={debug_mode},\n'
        spec_content += '    bootloader_ignore_signals=False,\n'
        spec_content += f'    strip={not debug_mode},\n'
        spec_content += f'    upx={not debug_mode},\n'
        spec_content += '    upx_exclude=[],\n'
        spec_content += '    runtime_tmpdir=None,\n'
        spec_content += f'    console={self.console_mode or debug_mode},\n'
        spec_content += '    disable_windowed_traceback=False,\n'
        spec_content += '    argv_emulation=False,\n'
        spec_content += '    target_arch=None,\n'
        spec_content += '    codesign_identity=None,\n'
        spec_content += '    entitlements_file=None,\n'
        spec_content += '    icon="./Icon_BatteryAnalysis.ico",\n'
        spec_content += '    version="version.txt",\n'
        spec_content += ')' 

        with open(os.path.join(self.build_path, 'Build_BatteryAnalysis', 'build.spec'), 'w', encoding='utf-8') as f:
            f.write(spec_content)

            # 执行 pyinstaller 命令
            logger.info(f"开始构建 {dataconverter_exe_name}...")
            # 在PowerShell中正确处理命令执行，使用subprocess模块自动处理路径中的空格
            import subprocess
            
            # 查找Python DLL路径 - 改进版本，适配GitHub Actions环境
            python_dll = None
            
            # 首先尝试直接从Python安装目录查找
            python_home = os.path.dirname(os.path.dirname(sys.executable))
            
            # 添加更多可能的DLL路径，包括GitHub Actions环境中的常见位置
            possible_dll_paths = [
                os.path.join(os.path.dirname(sys.executable), 'python311.dll'),
                os.path.join(python_home, 'python311.dll'),
                os.path.join(python_home, 'DLLs', 'python311.dll'),
                os.path.join(os.environ.get('PYTHONHOME', ''), 'python311.dll'),
                'python311.dll'  # 让PyInstaller尝试在PATH中查找
            ]
            
            # 查找python311.dll
            for path in possible_dll_paths:
                if os.path.exists(path):
                    python_dll = path
                    break
                    
            # 如果找到DLL，则添加警告
            if not python_dll:
                logger.warning("Could not find python311.dll")
            
            # 构建命令参数列表（切换为命令行方式，避免 spec 执行异常）
            # Windows 下 --add-data 使用分号分隔： 源路径;目标目录
            cmd_args = [
                sys.executable, '-m', 'PyInstaller',
                '-F', 'main_window.py',
                f'--name={dataconverter_exe_name}',
                f'--icon=Icon_BatteryAnalysis.ico',
                f'--distpath={final_build_dir}',
                f'--workpath={temp_path}/DataConverter',
                '--log-level=DEBUG',
                '--noupx',
                *(['--strip'] if not debug_mode else []),
                *(['--noconsole'] if not (self.console_mode or debug_mode) else ['--console']),
                f'--version-file=version.txt',
                # 禁用UPX压缩以避免DLL加载问题
                '--noupx',
                # 确保Python DLL正确包含
                # 移除--runtime-tmpdir参数，让PyInstaller使用默认的临时目录处理机制
                # 这样可以避免硬编码路径带来的权限和路径格式问题
                # 确保所有依赖的DLL都被正确包含
                '--collect-all=pywin32'
            ]
            
            # 添加Python DLL路径（如果找到）
            if python_dll:
                cmd_args.append('--add-binary=' + python_dll + ';.')
            
            # 添加其他参数
            cmd_args.extend([
                # 确保src目录被正确添加
                f'--add-data={src_path};.',
                # 添加battery_analysis包目录
                f'--add-data={os.path.join(src_path, "battery_analysis")};battery_analysis',
                # 添加配置文件 - 使用绝对路径并确保正确的目标目录结构
                f'--add-data={os.path.abspath(os.path.join(self.project_root, "config"))};config',
                # 添加图标资源目录
                f'--add-data={os.path.abspath(os.path.join(self.project_root, "config", "resources", "icons"))};config/resources/icons',
                # 额外添加配置文件到根目录，确保file_writer.py能找到
                f'--add-data={os.path.abspath(os.path.join(self.project_root, "config", "setting.ini"))};.',
                f'--add-data={os.path.join(self.project_root, "pyproject.toml")};.',
                # 添加必要的hidden-import，确保模块能被找到
                '--hidden-import=matplotlib.backends.backend_svg',
                '--hidden-import=docx',
                '--hidden-import=openpyxl',
                '--hidden-import=battery_analysis',
                '--hidden-import=battery_analysis.main',
                '--hidden-import=battery_analysis.ui',
                '--hidden-import=battery_analysis.utils',
                '--hidden-import=battery_analysis.utils.version',
                '--hidden-import=battery_analysis.utils.file_writer',
                '--hidden-import=battery_analysis.utils.battery_analysis',
                '--hidden-import=battery_analysis.ui.ui_main_window',
                
                '--hidden-import=xlsxwriter',
                '--collect-all=xlsxwriter',
                '--collect-all=openpyxl',
                '--hidden-import=xlrd',
                '--collect-all=xlrd',
                # 增加导入路径，确保能找到battery_analysis模块
                '--path', f'{src_path}',
                '--path', f'{self.project_root}'
            ])
            
            try:
                # 在指定目录下执行命令
                result = subprocess.run(
                    cmd_args,
                    cwd=os.path.join(self.build_path, 'Build_BatteryAnalysis'),
                    check=False,
                    capture_output=True,
                    encoding='utf-8'
                )
                logger.info(f"BatteryAnalysis构建结果: {result.returncode}")
                if result.stderr:
                    logger.error(f"错误输出: {result.stderr}")
            except Exception as e:
                logger.error(f"执行命令时出错: {e}")
                result = subprocess.CompletedProcess(cmd_args, 1)

        # 为ImageMaker生成spec文件
        # 构建参数设置，Debug模式和Release模式有所区别
        debug_mode = self.build_type == "Debug"

        # 使用简单的字符串拼接方式，并处理路径转义
        # 重新定义转义路径变量，确保在ImageMaker部分也能正确使用
        project_root_escaped = str(project_root).replace('\\', '\\\\')
        src_path_escaped = str(src_path).replace('\\', '\\\\')
        
        spec_content = '# -*- mode: python ; coding: utf-8 -*-\n'
        spec_content += 'block_cipher = None\n'
        spec_content += 'a = Analysis(\n'
        spec_content += '    ["image_show.py", "resources/resources_rc.py"],\n'
        spec_content += '    pathex=["' + project_root_escaped + '", "' + src_path_escaped + '"],\n'
        spec_content += '    binaries=[],\n'
        spec_content += '    datas=[("' + src_path_escaped + '", "src"), ("' + os.path.join(self.project_root, 'config').replace('\\', '\\\\') + '", "config"), ("' + os.path.join(self.project_root, 'pyproject.toml').replace('\\', '\\\\') + '", ".")],\n'
        spec_content += '    hiddenimports=["matplotlib.backends.backend_svg", "src", "src.battery_analysis", "src.battery_analysis.utils", "docx"],\n'
        spec_content += '    hookspath=[],\n'
        spec_content += '    hooksconfig={},\n'
        spec_content += '    runtime_hooks=[],\n'
        spec_content += '    excludes=[],\n'
        spec_content += '    win_no_prefer_redirects=False,\n'
        spec_content += '    win_private_assemblies=False,\n'
        spec_content += '    cipher=block_cipher,\n'
        spec_content += '    noarchive=False,\n'
        spec_content += ')\n'
        spec_content += 'pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)\n'
        spec_content += 'exe = EXE(\n'
        spec_content += '    pyz,\n'
        spec_content += '    a.scripts,\n'
        spec_content += '    a.binaries,\n'
        spec_content += '    a.zipfiles,\n'
        spec_content += '    a.datas,\n'
        spec_content += '    [],\n'
        spec_content += '    name="' + imagemaker_exe_name + '",\n'
        spec_content += f'    debug={debug_mode},\n'
        spec_content += '    bootloader_ignore_signals=False,\n'
        spec_content += f'    strip={not debug_mode},\n'
        spec_content += f'    upx={not debug_mode},\n'
        spec_content += '    upx_exclude=[],\n'
        spec_content += '    runtime_tmpdir=None,\n'
        spec_content += f'    console={self.console_mode or debug_mode},\n'
        spec_content += '    disable_windowed_traceback=False,\n'
        spec_content += '    argv_emulation=False,\n'
        spec_content += '    target_arch=None,\n'
        spec_content += '    codesign_identity=None,\n'
        spec_content += '    entitlements_file=None,\n'
        spec_content += '    icon="./Icon_ImageShow.ico",\n'
        spec_content += '    version="version.txt",\n'
        spec_content += ')'

        with open(os.path.join(self.build_path, 'Build_ImageShow', 'build.spec'), 'w', encoding='utf-8') as f:
            f.write(spec_content)

        # 执行 pyinstaller 命令
        logger.info(f"开始构建 {imagemaker_exe_name}...")
        # 在PowerShell中正确处理命令执行，使用subprocess模块自动处理路径中的空格
        import subprocess

        # 简化Python DLL处理，优先使用CI环境变量中的路径
        # 将复杂的环境特定逻辑移至CI配置中，本地构建仍能工作
        python_dll = None
        
        # 1. 优先检查CI环境变量中设置的DLL路径（用于GitHub Actions）
        ci_dll_path = os.environ.get('PYTHON_DLL_PATH')
        if ci_dll_path and os.path.exists(ci_dll_path):
            logger.info(f"使用CI环境变量中的Python DLL路径: {ci_dll_path}")
            python_dll = ci_dll_path
        else:
            logger.info("未找到CI环境变量中的Python DLL路径，尝试本地路径")
            # 2. 本地环境的基本路径查找
            python_exec_dir = Path(sys.executable).parent
            basic_paths = [
                python_exec_dir / 'python311.dll',
                Path(sys.prefix) / 'python311.dll'
            ]
            
            for path in basic_paths:
                logger.debug(f"检查本地DLL路径: {path}")
                if path.exists():
                    logger.info(f"找到本地Python DLL: {path}")
                    python_dll = str(path)
                    break
            
            # 添加错误处理
            if not python_dll:
                logger.warning("未找到Python DLL，这可能会导致构建的可执行文件在某些环境中无法正常运行")
                logger.warning(f"尝试过的路径: {', '.join(str(p) for p in basic_paths)}")
                # 即使未找到DLL，也继续构建过程，但添加警告

        # 构建命令参数列表 - 添加DLL修复参数，不使用spec文件而是直接使用命令行参数
        cmd_args = [sys.executable, '-m', 'PyInstaller', 'image_show.py', 
                  f'--name={imagemaker_exe_name}',
                  '--onefile',  # 添加此参数生成单个可执行文件
                  f'--icon=Icon_ImageShow.ico',
                  f'--distpath={final_build_dir}', 
                  f'--workpath={temp_path}/ImageMaker',
                  '--log-level=DEBUG',
                  '--noupx',
                  f'--version-file=version.txt',
                  # 移除--runtime-tmpdir参数，让PyInstaller使用默认的临时目录处理机制
                  # 这样可以避免硬编码路径带来的权限和路径格式问题
                  '--collect-all=pywin32']
        
        # 如果找到DLL，添加到命令参数
        if python_dll:
            cmd_args.append('--add-binary=' + python_dll + ';.')
        else:
            logger.warning("Could not find python311.dll")
        
        # 添加剩余参数
        cmd_args.extend([
                  f'--add-data={src_path};src',
                  f'--add-data={self.project_root / "config"};config',
                  f'--add-data={self.project_root / "config" / "resources" / "icons"};config/resources/icons',
                  f'--add-data={self.project_root / "pyproject.toml"};.',
                  f'--add-data={self.project_root / "config" / "setting.ini"};.',
                  '--hidden-import=matplotlib.backends.backend_svg',
                  '--hidden-import=docx',
                  '--hidden-import=openpyxl',
                  '--hidden-import=battery_analysis',
                  '--hidden-import=battery_analysis.main',
                  '--hidden-import=battery_analysis.ui',
                  '--hidden-import=battery_analysis.utils',

                  '--hidden-import=xlsxwriter',
                  '--collect-all=xlsxwriter',
                  '--collect-all=openpyxl',
                  '--hidden-import=xlrd',
                  '--collect-all=xlrd',
                  '--path', f'{src_path}',
                  '--path', f'{self.project_root}',
                  *(['--console'] if self.console_mode or debug_mode else ['--noconsole'])
        ])

        try:
            # 在指定目录下执行命令
            result = subprocess.run(
                cmd_args,
                cwd=image_show_dir,
                check=False,
                capture_output=True,
                encoding='utf-8'
            )
            logger.info(f"ImageShow构建结果: {result.returncode}")
            if result.stderr:
                logger.error(f"错误输出: {result.stderr}")
        except Exception as e:
            logger.error(f"执行命令时出错: {e}")
            result = subprocess.CompletedProcess(cmd_args, 1)

        # 清理临时文件
        if temp_path.exists():
            shutil.rmtree(temp_path)
        logger.info(f'构建完成，可执行文件位于: {final_build_dir}')


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        build_type = sys.argv[1]
        if build_type in ['--help', '-h']:
            logger.info("用法: python -m scripts.build [构建类型]")
            logger.info("\n构建类型:")
            logger.info("  Debug    - 构建调试版本")
            logger.info("  Release  - 构建发布版本")
            logger.info("\n示例:")
            logger.info("  python -m scripts.build Debug")
            logger.info("  python -m scripts.build Release")
            sys.exit(0)
        elif build_type not in ['Debug', 'Release']:
            raise ValueError(f"不支持的构建类型: {build_type}。只支持Debug和Release。")
        logger.info(f"开始{build_type}模式构建...")
        BuildManager(build_type)
    else:
        logger.info("用法: python -m scripts.build [构建类型]")
        logger.info("\n构建类型:")
        logger.info("  Debug    - 构建调试版本")
        logger.info("  Release  - 构建发布版本")
        logger.info("\n示例:")
        logger.info("  python -m scripts.build Debug")
        logger.info("  python -m scripts.build Release")
        sys.exit(1)