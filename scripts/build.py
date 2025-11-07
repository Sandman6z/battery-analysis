import os
import sys
import setuptools_scm

# 尝试使用setuptools_scm获取版本号
try:
    VERSION = setuptools_scm.get_version(root='..', relative_to=__file__)
except Exception:
    VERSION = "0.0.0"
    
# 添加项目根目录到Python路径，确保能正确导入模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

import shutil
import datetime
import configparser

from git import Repo

from src.battery_analysis.utils.exception_type import BuildException


class CaseSensitiveConfigParser(configparser.ConfigParser):
    """大小写敏感的配置解析器"""
    def optionxform(self, option_str):
        return option_str


class BuildConfig:
    """构建配置基类"""
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        # 项目根目录是scripts的上一级目录
        self.project_root = os.path.dirname(self.script_dir)
        self.temp_build_dir = os.path.join(self.project_root, "__temp__")
        self.final_build_dir = os.path.join(self.project_root, "build")
        
        # 初始化Git仓库
        self.git_repo = None
        self.git_index = None
        self.git = None
        try:
            self.git_repo = Repo(self.project_root)
            self.git_index = self.git_repo.index
            self.git = self.git_repo.git
        except Exception as e:
            print(f"警告: 无法初始化Git仓库: {e}")
            print("继续构建过程，但不进行Git相关操作")
        
        # 读取配置文件
        self.config = CaseSensitiveConfigParser()
        self.config_path = os.path.join(self.project_root, "config", "Config_BatteryAnalysis.ini")
        self.config.read(self.config_path, encoding='utf-8')
        self.version = self.config.get("BuildConfig", "Version")
        self.console_mode = self.config.getboolean("BuildConfig", "Console")
        
        # 定义构建应用相关目录
        self.dataconverter_build_dir = os.path.join(self.temp_build_dir, "Build_BatteryAnalysis")
        self.imagemaker_build_dir = os.path.join(self.temp_build_dir, "Build_ImageShow")


class BuildManager(BuildConfig):
    """构建管理器"""
    def __init__(self, build_type, build_dataconverter=True, build_imagemaker=True):
        super().__init__()
        # 只支持Debug和Release两种构建类型
        if build_type not in ['Debug', 'Release']:
            raise ValueError(f"不支持的构建类型: {build_type}。只支持Debug和Release。")
        self.build_type = build_type  # 构建类型: Debug或Release
        self.build_dataconverter = build_dataconverter  # 是否构建DataConverter
        self.build_imagemaker = build_imagemaker  # 是否构建ImageMaker
        
        # 兼容旧代码的属性名
        self.bBuildDataConverter = build_dataconverter
        self.bBuildImageMaker = build_imagemaker
        self.build_path = self.temp_build_dir
        self.console = self.console_mode
        
        # 清理构建目录和缓存
        self.clean_build_dirs()
        
        # 初始化时执行构建流程
        self.setup_version()
        self.copy_source_files()
        self.generate_version_info()
        self.build_applications()
        self.move_programs()
    
    def clean_build_dirs(self):
        """清理构建目录和缓存"""
        print(f"开始清理构建目录和缓存...")
        
        # 清理临时构建目录
        if os.path.exists(self.temp_build_dir):
            print(f"清理临时构建目录: {self.temp_build_dir}")
            shutil.rmtree(self.temp_build_dir)
        
        # 清理最终构建目录（对应当前构建类型）
        final_build_type_dir = os.path.join(self.project_root, 'build', self.build_type)
        if os.path.exists(final_build_type_dir):
            print(f"清理最终构建目录: {final_build_type_dir}")
            shutil.rmtree(final_build_type_dir)
        
        # 创建必要的目录
        os.makedirs(self.temp_build_dir, exist_ok=True)
        print("构建目录清理完成")
    
    def copy_source_files(self):
        """复制源代码文件到构建目录"""
        return self.copy2dir()
    
    def generate_version_info(self):
        """生成版本信息文件"""
        # 在构建目录中创建version.txt文件
        if self.build_dataconverter and os.path.exists(os.path.join(self.build_path, 'Build_BatteryAnalysis')):
            self._write_file(self._generate_vs_version_info("test", "BatteryTest-DataConverter"), 
                            os.path.join(self.build_path, 'Build_BatteryAnalysis', 'version.txt'))
            
        if self.build_imagemaker and os.path.exists(os.path.join(self.build_path, 'Build_ImageShow')):
            self._write_file(self._generate_vs_version_info("test", "BatteryTest-ImageMaker"), 
                            os.path.join(self.build_path, 'Build_ImageShow', 'version.txt'))
    
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
        print('开始移动文件...')
        # 使用项目根目录作为基础路径，添加构建类型子目录
        build_dir = os.path.join(self.project_root, 'build', self.build_type)
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
        
        # 准备文件名，添加版本号和构建类型信息
        version_suffix = self.version.replace('.', '_')
        dataconverter_exe_name = f"BatteryTest-DataConverter_{self.build_type}_{version_suffix}.exe"
        imagemaker_exe_name = f"BatteryTest-ImageMaker_{self.build_type}_{version_suffix}.exe"
        
        # 检查可执行文件是否存在于正确的位置（由于使用了--distpath，文件直接生成在build_dir）
        if self.build_dataconverter:
            exe_path = os.path.join(build_dir, dataconverter_exe_name)
            if os.path.exists(exe_path):
                print(f"确认: {exe_path} 已在目标目录中")
            else:
                print(f"警告: {exe_path} 不存在")
        
        if self.build_imagemaker:
            exe_path = os.path.join(build_dir, imagemaker_exe_name)
            if os.path.exists(exe_path):
                print(f"确认: {exe_path} 已在目标目录中")
            else:
                print(f"警告: {exe_path} 不存在")
        
        # BTSDA.cfg文件不再需要复制到构建目录（保留文件本身但不拷贝到运行环境）
        # config_file = os.path.join(self.project_root, 'config', 'BTSDA.cfg')
        # if os.path.exists(config_file):
        #     shutil.copy(config_file, build_dir)
        #     print(f"已复制配置文件到: {build_dir}")
        # else:
        #     print(f"警告: {config_file} 不存在，跳过复制")
        
        # 创建setting.ini
        config = CaseSensitiveConfigParser()
        config_path = os.path.join(self.project_root, "config", "Config_BatteryAnalysis.ini")
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
            if config.has_section("PltConfig"):
                config.set("PltConfig", "Path", "")
                config.set("PltConfig", "Title", "")
            if config.has_section("BuildConfig"):
                config.remove_section("BuildConfig")
            with open(os.path.join(build_dir, "setting.ini"), 'w', encoding='utf-8') as f:
                config.write(f)
            print(f"已创建: {os.path.join(build_dir, 'setting.ini')}")
        else:
            print(f"警告: {config_path} 不存在，无法创建setting.ini")
        
        # 清理临时构建目录
        if os.path.exists(self.build_path):
            shutil.rmtree(self.build_path)
            print(f"已清理临时构建目录: {self.build_path}")

    def setup_version(self):
        """设置版本信息 - 使用setuptools_scm获取的版本号"""
        global VERSION
        # 使用setuptools_scm获取的版本号
        self.version = VERSION
        
        # 生成版本文件
        version_content = f"""class Version(object):
    def __init__(self):
        self.version = "{self.version}"
"""
        self._write_file(version_content, os.path.join(self.script_dir, "Utility_Version.py"))
        
        # 更新配置中的版本号
        self.config.set("BuildConfig", "Version", self.version)

    def _write_file(self, content, file_path):
        """写入文件的辅助方法"""
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(content)

    def update_version_and_commit(self):
        """更新版本并提交更改 - 使用setuptools_scm自动管理版本"""
        global VERSION
        # 版本管理已切换为使用setuptools_scm
        print("版本管理已切换为Git标签模式。请使用Git标签来管理版本号：")
        print("1. 创建新标签: git tag -a vX.Y.Z -m \"Release vX.Y.Z\"")
        print("2. 推送标签: git push origin vX.Y.Z")
        print("3. setuptools-scm将自动从标签生成版本号")
        
        # 使用setuptools_scm获取的版本号
        self.version = VERSION
        
        # 更新版本文件
        self._update_version_files()

    def _update_version_files(self):
        """更新版本相关文件"""
        self.config.set("BuildConfig", "Version", self.version)
        
        version_content = f"""class Version(object):
    def __init__(self):
        self.version = "{self.version}"
"""
        self._write_file(version_content, os.path.join(self.script_dir, "Utility_Version.py"))
        
        # 写入配置文件
        config_output_path = os.path.join(self.script_dir, "config", "Config_BatteryAnalysis.ini")
        with open(config_output_path, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def copy2dir(self):
        """复制源文件到构建目录"""
        if os.path.exists(self.build_path):
            shutil.rmtree(self.build_path)
        os.mkdir(self.build_path)
        if self.bBuildDataConverter:
            os.mkdir(f"{self.build_path}/Build_BatteryAnalysis")
            shutil.copy(f"{self.project_root}/src/battery_analysis/main/main_window.py", f"{self.build_path}/Build_BatteryAnalysis")
            shutil.copy(f"{self.project_root}/src/battery_analysis/ui/ui_main_window.py", f"{self.build_path}/Build_BatteryAnalysis")
            shutil.copy(f"{self.project_root}/src/battery_analysis/utils/battery_analysis.py", f"{self.build_path}/Build_BatteryAnalysis")
            shutil.copy(f"{self.project_root}/src/battery_analysis/utils/exception_type.py", f"{self.build_path}/Build_BatteryAnalysis")
            shutil.copy(f"{self.project_root}/src/battery_analysis/utils/file_writer.py", f"{self.build_path}/Build_BatteryAnalysis")
            shutil.copy(f"{self.project_root}/src/battery_analysis/utils/version.py", f"{self.build_path}/Build_BatteryAnalysis")
            shutil.copy(f"{self.project_root}/src/battery_analysis/resources_rc.py", f"{self.build_path}/Build_BatteryAnalysis")
            shutil.copy(f"{self.project_root}/config/resources/icons/icon_battery_test_gui.ico", f"{self.build_path}/Build_BatteryAnalysis/Icon_BatteryAnalysis.ico")
        
        if self.bBuildImageMaker:
            os.mkdir(f"{self.build_path}/Build_ImageShow")
            shutil.copy(f"{self.project_root}/src/battery_analysis/main/image_show.py", f"{self.build_path}/Build_ImageShow")
            shutil.copy(f"{self.project_root}/src/battery_analysis/resources_rc.py", f"{self.build_path}/Build_ImageShow")
            shutil.copy(f"{self.project_root}/config/resources/icons/icon_battery_test_gui.ico", f"{self.build_path}/Build_ImageShow/Icon_ImageShow.ico")

    def build(self):
        """构建应用程序"""
        print('开始构建...')
        # 确保临时目录存在
        temp_path = os.path.join(self.project_root, '__temp__')
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        
        # 确保构建目录存在
        if not os.path.exists(self.build_path):
            os.makedirs(self.build_path)

        # 确保 Build_BatteryAnalysis 目录存在
        if not os.path.exists(os.path.join(self.build_path, 'Build_BatteryAnalysis')):
            os.makedirs(os.path.join(self.build_path, 'Build_BatteryAnalysis'))
        # 确保 Build_ImageShow 目录存在
        if not os.path.exists(os.path.join(self.build_path, 'Build_ImageShow')):
            os.makedirs(os.path.join(self.build_path, 'Build_ImageShow'))

        # 确保 build 目录存在
        build_dir = os.path.join(self.project_root, 'build')
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
            
        # 为构建目录添加构建类型子目录，便于区分不同构建版本
        final_build_dir = os.path.join(build_dir, self.build_type)
        if not os.path.exists(final_build_dir):
            os.makedirs(final_build_dir)

        # 获取Python解释器路径和PyInstaller命令
        python_exe = sys.executable
        pyinstaller_cmd = f"{python_exe} -m PyInstaller"
        
        # 复制必要的配置文件和图标
        # BTSDA.cfg文件不再需要复制到构建目录（保留文件本身但不拷贝到运行环境）
        # if os.path.exists(os.path.join(self.project_root, 'config', 'BTSDA.cfg')):
        #     shutil.copy2(os.path.join(self.project_root, 'config', 'BTSDA.cfg'), final_build_dir)
        
        # 复制图标
        icon_path = os.path.join(self.project_root, 'config', 'resources', 'icons', 'icon_battery_test_gui.ico')
        if os.path.exists(icon_path):
            shutil.copy2(icon_path, os.path.join(self.build_path, 'Build_BatteryAnalysis', 'Icon_BatteryAnalysis.ico'))
            shutil.copy2(icon_path, os.path.join(self.build_path, 'Build_ImageShow', 'Icon_ImageShow.ico'))
        
        src_path = os.path.join(self.project_root, 'src')

        # 对路径进行转义处理，确保在Python代码中正确使用
        project_root_escaped = self.project_root.replace('\\', '\\\\')
        src_path_escaped = src_path.replace('\\', '\\\\')
        
        # 准备文件名，添加版本号和构建类型信息
        version_suffix = self.version.replace('.', '_')
        dataconverter_exe_name = f"BatteryTest-DataConverter_{self.build_type}_{version_suffix}"
        imagemaker_exe_name = f"BatteryTest-ImageMaker_{self.build_type}_{version_suffix}"

        # 为DataConverter生成spec文件
        if self.bBuildDataConverter:
            # 构建参数设置，Debug模式和Release模式有所区别
            debug_mode = self.build_type == "Debug"
            
            # 使用简单的字符串拼接方式，并处理路径转义
            spec_content = '# -*- mode: python ; coding: utf-8 -*-\n'
            spec_content += 'block_cipher = None\n'
            spec_content += 'a = Analysis(\n'
            spec_content += '    ["main_window.py", "ui_main_window.py", "battery_analysis.py", "exception_type.py", "file_writer.py", "version.py", "resources_rc.py"],\n'
            spec_content += '    pathex=["' + project_root_escaped + '", "' + src_path_escaped + '"],\n'
            spec_content += '    binaries=[],\n'
            spec_content += '    datas=[("' + src_path_escaped + '", "src")],\n'
            spec_content += '    hiddenimports=["matplotlib.backends.backend_svg", "src", "src.battery_analysis", "src.battery_analysis.utils", "src.battery_analysis.ui", "docx"],\n'
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
            spec_content += f'    debug={debug_mode},\n'  # Debug模式启用调试，使用Python的布尔值True/False
            spec_content += '    bootloader_ignore_signals=False,\n'
            spec_content += f'    strip={not debug_mode},\n'  # Debug模式不剥离符号
            spec_content += f'    upx={not debug_mode},\n'  # Debug模式不使用UPX压缩
            spec_content += '    upx_exclude=[],\n'
            spec_content += '    runtime_tmpdir=None,\n'
            spec_content += f'    console={self.console_mode or debug_mode},\n'  # Debug模式总是显示控制台
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
            print(f"开始构建 {dataconverter_exe_name}...")
            # 在PowerShell中正确处理命令执行，使用subprocess模块自动处理路径中的空格
            import subprocess
            
            # 构建命令参数列表
            cmd_args = [sys.executable, '-m', 'PyInstaller', 'build.spec', 
                      f'--distpath={final_build_dir}', 
                      f'--workpath={temp_path}/DataConverter']
            
            print(f"执行命令: {' '.join(cmd_args)}")
            try:
                # 在指定目录下执行命令
                result = subprocess.run(cmd_args, cwd=os.path.join(self.build_path, 'Build_BatteryAnalysis'), 
                                      check=False, capture_output=True, text=True)
                print(f"BatteryAnalysis构建结果: {result.returncode}")
                print(f"标准输出: {result.stdout}")
                if result.stderr:
                    print(f"错误输出: {result.stderr}")
            except Exception as e:
                print(f"执行命令时出错: {e}")
                result = subprocess.CompletedProcess(cmd_args, 1)

        # 为ImageMaker生成spec文件
        if self.bBuildImageMaker:
            # 构建参数设置，Debug模式和Release模式有所区别
            debug_mode = self.build_type == "Debug"
            
            # 使用简单的字符串拼接方式，并处理路径转义
            spec_content = '# -*- mode: python ; coding: utf-8 -*-\n'
            spec_content += 'block_cipher = None\n'
            spec_content += 'a = Analysis(\n'
            spec_content += '    ["image_show.py", "resources_rc.py"],\n'
            spec_content += '    pathex=["' + project_root_escaped + '", "' + src_path_escaped + '"],\n'
            spec_content += '    binaries=[],\n'
            spec_content += '    datas=[("' + src_path_escaped + '", "src")],\n'
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
            spec_content += f'    debug={debug_mode},\n'  # Debug模式启用调试，使用Python的布尔值True/False
            spec_content += '    bootloader_ignore_signals=False,\n'
            spec_content += f'    strip={not debug_mode},\n'  # Debug模式不剥离符号
            spec_content += f'    upx={not debug_mode},\n'  # Debug模式不使用UPX压缩
            spec_content += '    upx_exclude=[],\n'
            spec_content += '    runtime_tmpdir=None,\n'
            spec_content += f'    console={self.console_mode or debug_mode},\n'  # Debug模式总是显示控制台
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
            print(f"开始构建 {imagemaker_exe_name}...")
            # 在PowerShell中正确处理命令执行，使用subprocess模块自动处理路径中的空格
            import subprocess
            
            # 构建命令参数列表
            cmd_args = [sys.executable, '-m', 'PyInstaller', 'build.spec', 
                      f'--distpath={final_build_dir}', 
                      f'--workpath={temp_path}/ImageMaker']
            
            print(f"执行命令: {' '.join(cmd_args)}")
            try:
                # 在指定目录下执行命令
                result = subprocess.run(cmd_args, cwd=os.path.join(self.build_path, 'Build_ImageShow'), 
                                      check=False, capture_output=True, text=True)
                print(f"ImageShow构建结果: {result.returncode}")
                print(f"标准输出: {result.stdout}")
                if result.stderr:
                    print(f"错误输出: {result.stderr}")
            except Exception as e:
                print(f"执行命令时出错: {e}")
                result = subprocess.CompletedProcess(cmd_args, 1)

        # 清理临时文件
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        print(f'构建完成，可执行文件位于: {final_build_dir}')


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        build_type = sys.argv[1]
        if build_type not in ['Debug', 'Release']:
            raise ValueError(f"不支持的构建类型: {build_type}。只支持Debug和Release。")
        print(f"开始{build_type}模式构建...")
        BuildManager(build_type)
    else:
        raise ValueError("需要1个参数: 构建类型名称（Debug或Release）")
