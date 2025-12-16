import sys
import os
import shutil
import datetime
import configparser
import subprocess
from pathlib import Path
from git import Repo
import logging
from abc import ABC, abstractmethod

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 检查PyInstaller是否已安装，如果未安装则提示用户安装build依赖
try:
    import PyInstaller
    logger.info(f"PyInstaller已安装: {PyInstaller.__version__}")
except ImportError:
    logger.warning("警告: 未找到PyInstaller模块。构建功能将不可用。")
    logger.warning("要启用构建功能，请先安装build依赖组:")
    logger.warning("  uv pip install -e '.[build]'")
    logger.warning("或")
    logger.warning("  pip install -e '.[build]'")
    # 仅在测试时跳过检查，实际使用时应取消注释下面的sys.exit(1)
    # sys.exit(1)

# 添加项目根目录到Python路径，确保能正确导入模块
script_dir = Path(__file__).absolute().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from battery_analysis.utils.exception_type import BuildException


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


class BuildTask(ABC):
    """构建任务基类"""
    def __init__(self, config: BuildConfig):
        self.config = config
        
    @abstractmethod
    def execute(self):
        """执行构建任务"""
        pass


class VersionEmbeddingTask(BuildTask):
    """版本号嵌入任务"""
    def execute(self):
        """在构建前将版本号嵌入到__init__.py文件中"""
        init_file_path = self.config.project_root / "src" / "battery_analysis" / "__init__.py"
        
        try:
            # 读取原始文件内容
            with open(init_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换版本号占位符 - 使用更健壮的方式匹配和替换
            # 分别替换两行，避免因为不可见字符导致的精确匹配失败
            content = content.replace('# 版本号将在构建时被替换为实际值', '# 构建时嵌入的实际版本号')
            content = content.replace('return "2.0.0"', f'return "{self.config.version}"')
            
            updated_content = content
            
            # 写回文件
            with open(init_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"已将版本号 {self.config.version} 嵌入到 {init_file_path}")
            
            # 返回原始内容，以便稍后恢复
            return content
        except Exception as e:
            logger.error(f"嵌入版本号时出错: {e}")
            return None


class DirectoryCleanTask(BuildTask):
    """目录清理任务"""
    def execute(self):
        """清理构建目录和缓存"""
        logger.info(f"开始清理构建目录和缓存...")
        
        # 清理临时构建目录
        if self.config.temp_build_dir.exists():
            logger.info(f"清理临时构建目录: {self.config.temp_build_dir}")
            shutil.rmtree(self.config.temp_build_dir)
        
        # 清理最终构建目录（对应当前构建类型）
        final_build_type_dir = self.config.project_root / 'build' / self.config.build_type
        if final_build_type_dir.exists():
            logger.info(f"清理最终构建目录: {final_build_type_dir}")
            shutil.rmtree(final_build_type_dir)
        
        # 创建必要的目录
        self.config.temp_build_dir.mkdir(parents=True, exist_ok=True)
        logger.info("构建目录清理完成")


class FileCopyTask(BuildTask):
    """文件复制任务"""
    def execute(self):
        """复制源文件到构建目录"""
        build_path = Path(self.config.temp_build_dir)
        if build_path.exists():
            shutil.rmtree(build_path)
        build_path.mkdir(parents=True, exist_ok=True)
        
        # 创建两个应用的构建目录
        battery_analysis_dir = build_path / "Build_BatteryAnalysis"
        image_show_dir = build_path / "Build_ImageShow"
        battery_analysis_dir.mkdir()
        image_show_dir.mkdir()
        
        # 定义源文件路径
        main_window_path = self.config.project_root / "src" / "battery_analysis" / "main" / "main_window.py"
        image_show_path = self.config.project_root / "src" / "battery_analysis" / "main" / "image_show.py"
        resources_rc_path = self.config.project_root / "src" / "battery_analysis" / "resources" / "resources_rc.py"
        icon_path = self.config.project_root / "config" / "resources" / "icons" / "Icon_BatteryTestGUI.ico"
        ui_path = self.config.project_root / "src" / "battery_analysis" / "ui" / "resources" / "ui_battery_analysis.ui"
        battery_analysis_src = self.config.project_root / "src" / "battery_analysis"
        
        # 复制BatteryAnalysis的文件
        shutil.copy(main_window_path, battery_analysis_dir)
        shutil.copy(resources_rc_path, battery_analysis_dir / "resources")
        shutil.copy(icon_path, battery_analysis_dir / "Icon_BatteryAnalysis.ico")
        
        # 复制SVG图标文件到构建目录的config/resources/icons文件夹
        svg_dir = self.config.project_root / "config" / "resources" / "icons"
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


class VersionInfoTask(BuildTask):
    """版本信息生成任务"""
    def execute(self):
        """生成版本信息文件"""
        # 在构建目录中创建version.txt文件（统一为两个应用生成）
        build_path = Path(self.config.temp_build_dir)
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
        version_split = self.config.version.split(".")
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
                    StringStruct(u'ProductVersion', u'{self.config.build_type}_{commit_id}')
                ]
            )
        ]),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])]) # 语言, USA
    ]
)"""
    
    def _write_file(self, content, file_path):
        """写入文件的辅助方法"""
        # 确保目录存在
        file_path_obj = Path(file_path)
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path_obj, "w", encoding='utf-8') as f:
            f.write(content)


class ApplicationBuildTask(BuildTask):
    """应用程序构建任务"""
    def execute(self):
        """构建应用程序"""
        logger.info('开始构建...')
        
        # 确保临时目录存在
        temp_path = self.config.project_root / '__temp__'
        temp_path.mkdir(parents=True, exist_ok=True)
        
        # 确保构建目录存在
        build_path = Path(self.config.temp_build_dir)
        build_path.mkdir(parents=True, exist_ok=True)

        # 确保 Build_BatteryAnalysis 和 Build_ImageShow 目录存在
        battery_analysis_dir = build_path / 'Build_BatteryAnalysis'
        image_show_dir = build_path / 'Build_ImageShow'
        battery_analysis_dir.mkdir(exist_ok=True)
        image_show_dir.mkdir(exist_ok=True)

        # 确保 build 目录存在并添加构建类型子目录
        final_build_dir = self.config.project_root / 'build' / self.config.build_type
        final_build_dir.mkdir(parents=True, exist_ok=True)

        # 获取Python解释器路径
        python_exe = sys.executable
        
        # 复制必要的图标（如果copy2dir方法未处理）
        icon_path = self.config.project_root / 'config' / 'resources' / 'icons' / 'Icon_BatteryTestGUI.ico'
        if icon_path.exists():
            shutil.copy2(icon_path, battery_analysis_dir / 'Icon_BatteryAnalysis.ico')
            shutil.copy2(icon_path, image_show_dir / 'Icon_ImageShow.ico')
        
        src_path = self.config.project_root / 'src'

        # 确定系统架构
        architecture = "x64"
        
        # 根据构建类型生成相应的文件名格式（注意：这里不带.exe后缀，PyInstaller会自动添加）
        if self.config.build_type == "Release":
            # Release版本：battery-analyzer_2.0.0_x64
            dataconverter_exe_name = f"battery-analyzer_{self.config.version}_{architecture}"
            imagemaker_exe_name = f"battery-analysis-visualizer_{self.config.version}_{architecture}"
        else:
            # Debug版本：battery-analyzer_2.0.0_x64_debug
            dataconverter_exe_name = f"battery-analyzer_{self.config.version}_{architecture}_debug"
            imagemaker_exe_name = f"battery-analysis-visualizer_{self.config.version}_{architecture}_debug"

        # 构建BatteryAnalysis应用
        self._build_battery_analysis(python_exe, temp_path, final_build_dir, battery_analysis_dir, src_path, dataconverter_exe_name)
        
        # 构建ImageShow应用
        self._build_image_show(python_exe, temp_path, final_build_dir, image_show_dir, src_path, imagemaker_exe_name)
        
        # 清理临时文件
        if temp_path.exists():
            shutil.rmtree(temp_path)
        logger.info(f'构建完成，可执行文件位于: {final_build_dir}')
    
    def _build_battery_analysis(self, python_exe, temp_path, final_build_dir, build_dir, src_path, exe_name):
        """构建BatteryAnalysis应用"""
        logger.info(f"开始构建 {exe_name}...")
        
        # 构建命令参数列表
        cmd_args = [
            python_exe, '-m', 'PyInstaller',
            '-F', 'main_window.py',
            f'--name={exe_name}',
            f'--icon=Icon_BatteryAnalysis.ico',
            f'--distpath={final_build_dir}',
            f'--workpath={temp_path}/DataConverter',
            '--log-level=DEBUG',
            '--noupx',
            *(['--strip'] if not self.config.debug_mode else []),
            *(['--noconsole'] if not (self.config.console_mode or self.config.debug_mode) else ['--console']),
            f'--version-file=version.txt',
            # 确保Python DLL正确包含
            '--collect-all=pywin32'
        ]
        
        # 添加Python DLL路径（如果找到）
        python_dll = self._find_python_dll()
        if python_dll:
            cmd_args.append('--add-binary=' + python_dll + ';.')
        
        # 添加其他参数
        cmd_args.extend([
            # 确保src目录被正确添加
            f'--add-data={src_path};.',
            # 添加battery_analysis包目录
            f'--add-data={os.path.join(src_path, "battery_analysis")};battery_analysis',
            # 添加配置文件 - 使用绝对路径并确保正确的目标目录结构
            f'--add-data={os.path.abspath(os.path.join(self.config.project_root, "config"))};config',
            # 添加图标资源目录
            f'--add-data={os.path.abspath(os.path.join(self.config.project_root, "config", "resources", "icons"))};config/resources/icons',
            # 额外添加配置文件到根目录，确保file_writer.py能找到
            f'--add-data={os.path.abspath(os.path.join(self.config.project_root, "config", "setting.ini"))};.',
            f'--add-data={os.path.join(self.config.project_root, "pyproject.toml")};.',
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
            '--path', f'{self.config.project_root}'
        ])
        
        try:
            # 在指定目录下执行命令
            result = subprocess.run(
                cmd_args,
                cwd=build_dir,
                check=False,
                capture_output=True,
                encoding='utf-8'
            )
            logger.info(f"BatteryAnalysis构建结果: {result.returncode}")
            if result.stderr:
                logger.error(f"错误输出: {result.stderr}")
        except Exception as e:
            logger.error(f"执行命令时出错: {e}")
    
    def _build_image_show(self, python_exe, temp_path, final_build_dir, build_dir, src_path, exe_name):
        """构建ImageShow应用"""
        logger.info(f"开始构建 {exe_name}...")
        
        # 构建命令参数列表
        cmd_args = [
            python_exe, '-m', 'PyInstaller', 'image_show.py', 
            f'--name={exe_name}',
            '--onefile',  # 添加此参数生成单个可执行文件
            f'--icon=Icon_ImageShow.ico',
            f'--distpath={final_build_dir}', 
            f'--workpath={temp_path}/ImageMaker',
            '--log-level=DEBUG',
            '--noupx',
            f'--version-file=version.txt',
            # 确保Python DLL正确包含
            '--collect-all=pywin32'
        ]
        
        # 添加Python DLL路径（如果找到）
        python_dll = self._find_python_dll()
        if python_dll:
            cmd_args.append('--add-binary=' + python_dll + ';.')
        
        # 添加其他参数
        cmd_args.extend([
            f'--add-data={src_path};src',
            f'--add-data={self.config.project_root / "config"};config',
            f'--add-data={self.config.project_root / "config" / "resources" / "icons"};config/resources/icons',
            f'--add-data={self.config.project_root / "pyproject.toml"};.',
            f'--add-data={self.config.project_root / "config" / "setting.ini"};.',
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
            '--path', f'{self.config.project_root}',
            *(['--console'] if self.config.console_mode or self.config.debug_mode else ['--noconsole'])
        ])

        try:
            # 在指定目录下执行命令
            result = subprocess.run(
                cmd_args,
                cwd=build_dir,
                check=False,
                capture_output=True,
                encoding='utf-8'
            )
            logger.info(f"ImageShow构建结果: {result.returncode}")
            if result.stderr:
                logger.error(f"错误输出: {result.stderr}")
        except Exception as e:
            logger.error(f"执行命令时出错: {e}")
    
    def _find_python_dll(self):
        """查找Python DLL路径"""
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
        
        return python_dll


class FileMoveTask(BuildTask):
    """文件移动任务"""
    def execute(self):
        """移动构建好的程序到最终位置"""
        logger.info('开始移动文件...')
        # 使用项目根目录作为基础路径，添加构建类型子目录
        build_dir = self.config.project_root / 'build' / self.config.build_type
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # 确定系统架构
        architecture = "x64"
        
        # 根据构建类型生成相应的文件名格式
        if self.config.build_type == "Release":
            # Release版本：battery-analyzer_2.0.0_x64.exe
            dataconverter_exe_name = f"battery-analyzer_{self.config.version}_{architecture}.exe"
            imagemaker_exe_name = f"battery-analysis-visualizer_{self.config.version}_{architecture}.exe"
        else:
            # Debug版本：battery-analyzer_2.0.0_x64_debug.exe
            dataconverter_exe_name = f"battery-analyzer_{self.config.version}_{architecture}_debug.exe"
            imagemaker_exe_name = f"battery-analysis-visualizer_{self.config.version}_{architecture}_debug.exe"
        
        # 检查可执行文件是否存在于正确的位置
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
        
        # 创建setting.ini
        config = CaseSensitiveConfigParser()
        config_path = self.config.project_root / "config" / "setting.ini"
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
        build_path = Path(self.config.temp_build_dir)
        if build_path.exists():
            shutil.rmtree(build_path)
            logger.info(f"已清理临时构建目录: {build_path}")


    def __init__(self, build_type):
        super().__init__(build_type)
        # 只支持Debug和Release两种构建类型
        if build_type not in ['Debug', 'Release']:
            raise ValueError(f"不支持的构建类型: {build_type}。只支持'Debug'和'Release'，或请检查大小写")
        self.build_type = build_type
        self.build_path = self.temp_build_dir
        self.console = self.console_mode
        
        # 初始化任务列表
        self.tasks = [
            DirectoryCleanTask(self),
            FileCopyTask(self),
            VersionInfoTask(self),
            ApplicationBuildTask(self),
            FileMoveTask(self)
        ]
    
    def run(self):
        """执行构建流程"""
        # 保存原始__init__.py内容，以便构建后恢复
        original_init_content = None
        
        try:
            # 在构建前嵌入版本号
            version_task = VersionEmbeddingTask(self)
            original_init_content = version_task.execute()
            
            # 执行构建流程中的各个任务
            for task in self.tasks:
                task.execute()
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
    
