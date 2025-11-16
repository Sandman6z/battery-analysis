# BOEDT Battery test GUI Tool

## Develop Quote
- use `uv` manage including python version, requirment...
	- **when first use `uv sync` on new PC, remember use `Administrator` run `Terminal`, or maybe lots of `errors`**
	- in order to avoid the well-known speed problem in the country, you can use  
	> uv sync -i https://mirrors.aliyun.com/pypi/simple/
- use `nuitka` pack .exe

- use `Qt Designer` to design UI
	- `Qt Designer` need to use `pip` to install `PySide6`
	- installed package location: 
	> %userprofile%\AppData\Roaming\Python\Python313\site-packages\PySide6

- use `.\.venv\Scripts\activate` to enable virtual enviroment, then you can use `nuitka` to pack
- `nuitka` don't need to be installed in the project.  
So we don't use `uv add`, we can use  
> uv pip install nuitka -i https://mirrors.aliyun.com/pypi/simple/

## How to convert UI to py

In `ui_main_window.py`, it shows use `pyuic5` to convert. So use
> pyuic5 ./config/resources/ui/UI_BatteryAnalysis.ui -o ./src/battery_analysis/ui/ui_main_window.py

This will generate ui_main_window.py, which contains the Ui_MainWindow class.
The `Main class` inherits `ui_main_window.Ui_MainWindow` and calls `self.setupUi(self)` in the constructor, which loads the UI elements into the current window object.

## How to convert qrc to py
Compile `.qrc` to Python file, usually named `resources_rc.py`
> .\.venv\Scripts\pyrcc5.exe .\__resources__\resources.qrc -o src\battery_analysis\resources_rc.py  # 保持不变，因为__resources__文件夹仍在根目录        

- Make sure `resources.qrc` in right folder.
- .py 文件生成后需放在与你的 UI Python 文件同目录下（或符合模块导入路径）

---

## How to Packaging
Before packaging the project, remember to use **`Administrator`** to run the **`Terminal`**  
Or you will see like this:
![alt text](image.png)

- Also, **remember to acrivate the venv**

### Use nuitka command
>python -m nuitka  --mingw64 --standalone --onefile --show-progress --show-memory --windows-console-mode=disable --plugin-enable=pyqt5 --include-data-dir=".venv/Lib/site-packages/PyQt5/Qt5/plugins=plugins" --noinclude-setuptools-mode=nofollow --noinclude-pytest-mode=nofollow --remove-output --output-dir=dist ./src/battery_analysis/main/main_window.py

### Use pyinstaller to pack

I think must install pyinstaller under project env:
	use `uv pip install pyinstaller`
	why not `uv add`, because pyinstaller not env need, just a convert tool
	Then use 
	> pyinstaller --onefile --windowed --clean --noupx src/battery_analysis/main/main_window.py --hidden-import=PyQt5 --hidden-import=PyQt5.QtWidgets --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui

	after pack is ok, no error, can run into exe
	but cannot click any UI components
	Need to be solve..........................................................

---

- if use pyinstaller to pack, first need install pyinstaller into the `.venv` environment, then the command is:
> .\.venv\Scripts\pyinstaller --onefile --windowed --collect-all=matplotlib --icon=".\config\icon\Icon_BatteryAnalysis.ico"  .\src\battery_analysis\main\main_window.py
- if failed, the clean command
> pyinstaller --clean --onefile .\src\battery_analysis\main\main_window.py


---
<!-- This section describes the update to the Test Information UI, which now supports adjustment using a scroll bar for better usability. -->



## 环境配置流程
> uv init
> rm .\main.py #remove no useful auto-create file
> uv venv --python 3.11
> .\venv\Scripts\activate
> uv add -r .\requirements.txt

## Q&A

1. Test Information UI part change to can adjust with **scroll bar**.
2. Add running progress bar.
3. The window size can be stretched freely without problems
4. The window able to be maximized



- 一定在激活虚拟环境
- 一定在虚拟环境下安装打包工具，否则无法生成各种hook，运行会各种缺失，用什么命令添加都无效
- 遇到task version问题，去修改`CHANGELOG.md`和`Utility_Version.py`

## bug list
1. 第五页有空白页

## 运行方式

> 已移除顶层 `main.py`，请使用以下统一入口运行或打包。

### 开发运行（推荐）
- 使用虚拟环境：
  - ` .\.venv\Scripts\activate `
  - ` python -m battery_analysis.main.main_window `
- 使用 uv：
  - ` uv run python -m battery_analysis.main.main_window `

### 安装后脚本入口
- ` uv run battery-analysis `

### 构建与打包
- Debug 构建：
  - 仅构建 Analyzer：` python -m scripts.build Debug 1 0 `
  - 仅构建 Visualizer：` python -m scripts.build Debug 0 1 `
  - 同时构建二者：` python -m scripts.build Debug 1 1 `
- Release 构建：
  - ` python -m scripts.build Release `

### 打包后运行
- Debug：
  - ` .\build\Debug\battery-analyzer_1_0_1.exe `
  - ` .\build\Debug\battery-analysis-visualizer_1_0_1.exe `
- Release：
  - ` .\build\Release\battery-analyzer_1_0_1.exe `
  - ` .\build\Release\battery-analysis-visualizer_1_0_1.exe `

### 注意事项
- 始终在已激活的虚拟环境中运行或打包。
- 模块入口与打包后的 exe 在资源定位上保持一致（基于 `sys.executable`）。
- 已移除临时测试脚本：`test_config_read.py`、`test_exe.py`、`test_exe_start.py`、`test_ui_events.py`，如需本地检查请直接使用上述“开发运行”命令并验证界面与配置读取是否正常。