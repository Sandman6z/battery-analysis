# BOEDT Battery test GUI Tool

## 项目文档

本项目提供了以下专项文档，位于`docs/`目录下：

- **[Pylint静态代码分析使用指南](docs/README_PYLINT.md)**：介绍如何使用Pylint进行代码质量检查
- **[文档字符串编写指南](docs/DOCSTRING_GUIDE.md)**：说明项目的文档字符串编写规范

## 开发环境配置

### 环境配置流程
> uv init
> rm .\main.py #删除自动创建的无用文件
> uv venv --python 3.11
> .\venv\Scripts\activate
> uv sync -i https://mirrors.aliyun.com/pypi/simple/

**注意：** 在新电脑上首次使用`uv sync`时，请以管理员权限运行终端，否则可能会出现多个错误。

### 开发工具安装
- **Qt Designer**：设计UI界面
  - 可以通过pip安装PyQt6或PySide6获取：`pip install PyQt6`或`pip install PySide6`
  - 安装位置：`%userprofile%\AppData\Roaming\Python\Python313\site-packages\PyQt6` 或 `PySide6`

- **打包工具**：
  - 使用nuitka进行打包：`uv pip install nuitka -i https://mirrors.aliyun.com/pypi/simple/`
  - 或使用pyinstaller：`uv pip install pyinstaller -i https://mirrors.aliyun.com/pypi/simple/`

## Qt 资源系统使用说明

### 1. 资源文件结构
我们使用 Qt 资源系统（.qrc）管理应用图标和其他资源文件，这使得资源文件能够被正确地打包到可执行文件中。

资源文件位置：
- `config/resources/icons/resources.qrc` - 主资源文件
- SVG图标存放在 `config/resources/icons/` 目录下

### 2. UI文件转换为Python
使用pyuic6将UI文件转换为Python文件：
> pyuic6 ./src/battery_analysis/ui/resources/ui_battery_analysis.ui -o ./src/battery_analysis/ui/ui_main_window.py

这将生成包含Ui_MainWindow类的ui_main_window.py文件。
主类继承自`ui_main_window.Ui_MainWindow`，并在构造函数中调用`self.setupUi(self)`来加载UI元素。

### 3. 资源文件(qrc)转换为Python
编译.qrc文件为Python文件，通常命名为`resources_rc.py`：
> .\.venv\Scripts\pyrcc6.exe .\config\resources\icons\resources.qrc -o src\battery_analysis\resources\resources_rc.py        

**重要注意事项：**
- 确保resources.qrc文件在正确的文件夹中
- 生成的.py文件需放在与UI Python文件相同目录或符合模块导入路径
- 在应用中使用资源时，使用`:/icons/icon_name.svg`格式的路径
- 所有SVG图标引用已更新为使用资源系统路径

## 配置文件说明

项目使用`config/setting.ini`作为主配置文件，应用会按以下顺序查找配置文件：

1. 当前工作目录下的`config/setting.ini`
2. 应用基础目录下的`config/setting.ini`
3. 当前工作目录下的`setting.ini`
4. 应用基础目录下的`setting.ini`
5. 项目根目录下的`config/setting.ini`（基于当前文件位置的绝对路径，确保在任何位置都能找到）

这种设计确保了应用在开发环境和打包后的可执行文件环境中都能正确找到配置文件。

## 运行方式

### 开发运行（推荐）
- 使用虚拟环境：
  - ` .\.venv\Scripts\activate `
  - ` python -m src.battery_analysis.main.main_window `
- 使用 uv：
  - ` uv run python -m src.battery_analysis.main.main_window `

### 安装后脚本入口
- ` uv run battery-analysis `

## 代码质量检查

项目使用Pylint进行静态代码分析，以确保代码质量和一致性。

### 运行完整代码检查

您可以使用以下命令运行整个工程的代码质量检查：

```bash
# 使用uv运行pylint脚本
uv run scripts/run_pylint.py

# 或者直接使用Python运行（确保在虚拟环境中）
python scripts/run_pylint.py
```

该脚本会执行以下操作：
- 递归查找并分析所有Python文件（包括`src`、`scripts`和`tests`目录）
- 实时显示分析结果
- 生成JSON格式的详细报告 (`pylint_report.json`)
- 生成HTML格式的可视化报告 (`pylint_report.html`)
- 生成Markdown格式的重构计划 (`refactoring_plan.md`)

### 详细使用指南

关于Pylint的详细配置和使用说明，请参考：
- **[Pylint静态代码分析使用指南](docs/README_PYLINT.md)**

## 构建与打包

在打包项目之前，请确保：
- 以**管理员权限**运行终端
- 已**激活虚拟环境**

### 使用构建脚本（推荐）

项目提供了自动化构建脚本，支持Debug和Release两种模式：

- Debug 构建：
  > python -m scripts.build Debug

- Release 构建：
  > python -m scripts.build Release

### 手动使用 nuitka 命令

> python -m nuitka --mingw64 --standalone --onefile --show-progress --show-memory --windows-console-mode=disable --plugin-enable=pyqt6 --include-data-dir=".venv/Lib/site-packages/PyQt6/Qt6/plugins=plugins" --noinclude-setuptools-mode=nofollow --noinclude-pytest-mode=nofollow --remove-output --output-dir=dist ./src/battery_analysis/main/main_window.py --include-data-file="./config/resources/icons=./config/resources/icons" --include-data-file="./src/battery_analysis/ui/resources/ui_battery_analysis.ui=./src/battery_analysis/ui/resources/ui_battery_analysis.ui"

### 使用 pyinstaller 打包

首先需要在虚拟环境中安装pyinstaller：
> uv pip install pyinstaller

然后使用以下命令进行打包：
> .\.venv\Scripts\pyinstaller --onefile --windowed --collect-all=matplotlib --icon=".\config\resources\icons\Icon_BatteryTestGUI.ico" .\src\battery_analysis\main\main_window.py --add-data=".\config\resources\icons;config\resources\icons" --add-data=".\src\battery_analysis\ui\resources\ui_battery_analysis.ui;src\battery_analysis\ui\resources"

## 重要注意事项

- 始终在已激活的虚拟环境中运行或打包
- 一定在虚拟环境下安装打包工具，否则无法生成各种hook，运行会各种缺失
- 模块入口与打包后的exe在资源定位上保持一致（基于`sys.executable`）
- 已移除临时测试脚本：`test_config_read.py`、`test_exe.py`、`test_exe_start.py`、`test_ui_events.py`
- 如需本地检查，请直接使用上述"开发运行"命令并验证界面与配置读取是否正常
- 遇到task version问题，去修改`CHANGELOG.md`和`src/battery_analysis/utils/version.py`

## 已知问题
1. 第五页存在空白页

## 功能更新
1. Test Information UI部分已更改为使用**滚动条**进行调整，提高了可用性
2. 添加了运行进度条显示
3. 窗口大小可自由拉伸
4. 窗口支持最大化显示