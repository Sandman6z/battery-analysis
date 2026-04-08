# Nuitka 打包指南

本文档提供使用 Nuitka 打包 Battery Analysis 应用程序的完整指南。

## 环境要求

### 必需软件
- Python 3.13+
- Nuitka >= 2.0
- C 编译器（Windows 推荐使用 MSVC 或 MinGW64）
- 项目依赖（见 pyproject.toml）

### 安装 Nuitka

```bash
pip install nuitka
```

### Windows C 编译器安装

**选项 1: Visual Studio Build Tools（推荐）**
- 下载并安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
- 选择 "Desktop development with C++" 工作负载

**选项 2: MinGW64**
```bash
# 使用 Nuitka 自动下载
python -m nuitka --mingw64 --help
```

## 快速开始

### 基础打包命令

```bash
python -m nuitka \
    --standalone \
    --onefile \
    --enable-plugin=pyqt6 \
    --windows-icon-from-ico=config/resources/icons/Icon_BatteryTestGUI.ico \
    --windows-console-mode=disable \
    --output-dir=dist \
    --output-filename=BatteryAnalysis.exe \
    --company-name="Ewin Hardware Group" \
    --product-name="Battery Analysis" \
    --file-version=2.8.1 \
    --product-version=2.8.1 \
    --file-description="Battery test data analysis application" \
    --copyright="Copyright (c) 2024 Ewin Hardware Group" \
    src/battery_analysis/main/main_window.py
```

### 优化打包命令（推荐）

```bash
python -m nuitka \
    --standalone \
    --onefile \
    --enable-plugin=pyqt6 \
    --enable-plugin=numpy \
    --windows-icon-from-ico=config/resources/icons/Icon_BatteryTestGUI.ico \
    --windows-console-mode=disable \
    --output-dir=dist \
    --output-filename=BatteryAnalysis.exe \
    --company-name="Ewin Hardware Group" \
    --product-name="Battery Analysis" \
    --file-version=2.8.1 \
    --product-version=2.8.1 \
    --file-description="Battery test data analysis application" \
    --copyright="Copyright (c) 2024 Ewin Hardware Group" \
    --include-package=battery_analysis \
    --include-package-data=battery_analysis \
    --include-data-dir=config=config \
    --nofollow-import-to=pytest \
    --nofollow-import-to=black \
    --nofollow-import-to=flake8 \
    --nofollow-import-to=pylint \
    --assume-yes-for-downloads \
    --show-progress \
    --show-memory \
    src/battery_analysis/main/main_window.py
```

## 详细参数说明

### 核心参数

| 参数 | 说明 |
|------|------|
| `--standalone` | 创建独立可执行文件，包含所有依赖 |
| `--onefile` | 打包为单个 exe 文件 |
| `--enable-plugin=pyqt6` | 启用 PyQt6 插件支持 |
| `--enable-plugin=numpy` | 启用 NumPy 优化 |

### Windows 特定参数

| 参数 | 说明 |
|------|------|
| `--windows-icon-from-ico` | 设置应用程序图标 |
| `--windows-console-mode=disable` | 禁用控制台窗口（GUI 应用） |
| `--windows-console-mode=attach` | 调试时使用，显示控制台输出 |

### 包含/排除参数

| 参数 | 说明 |
|------|------|
| `--include-package=battery_analysis` | 包含整个包 |
| `--include-package-data=battery_analysis` | 包含包内的数据文件 |
| `--include-data-dir=config=config` | 包含配置目录 |
| `--nofollow-import-to=pytest` | 排除测试依赖 |

### 元数据参数

| 参数 | 说明 |
|------|------|
| `--company-name` | 公司名称 |
| `--product-name` | 产品名称 |
| `--file-version` | 文件版本 |
| `--product-version` | 产品版本 |
| `--file-description` | 文件描述 |
| `--copyright` | 版权信息 |

## 打包配置文件

创建 `nuitka-build.py` 脚本以简化打包流程：

```python
#!/usr/bin/env python
"""
Nuitka 打包脚本
使用方法: python nuitka-build.py
"""
import subprocess
import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent
SRC_DIR = ROOT_DIR / "src"
DIST_DIR = ROOT_DIR / "dist"
ICON_PATH = ROOT_DIR / "config/resources/icons/Icon_BatteryTestGUI.ico"
ENTRY_POINT = SRC_DIR / "battery_analysis/main/main_window.py"

# 版本信息
VERSION = "2.8.1"
COMPANY = "Ewin Hardware Group"
PRODUCT = "Battery Analysis"

def build():
    """执行 Nuitka 打包"""
    
    # 确保输出目录存在
    DIST_DIR.mkdir(exist_ok=True)
    
    # Nuitka 命令参数
    nuitka_args = [
        sys.executable, "-m", "nuitka",
        
        # 基础配置
        "--standalone",
        "--onefile",
        
        # 插件
        "--enable-plugin=pyqt6",
        "--enable-plugin=numpy",
        
        # Windows 配置
        f"--windows-icon-from-ico={ICON_PATH}",
        "--windows-console-mode=disable",
        
        # 输出配置
        f"--output-dir={DIST_DIR}",
        "--output-filename=BatteryAnalysis.exe",
        
        # 元数据
        f"--company-name={COMPANY}",
        f"--product-name={PRODUCT}",
        f"--file-version={VERSION}",
        f"--product-version={VERSION}",
        "--file-description=Battery test data analysis application",
        f"--copyright=Copyright (c) 2024 {COMPANY}",
        
        # 包含配置
        "--include-package=battery_analysis",
        "--include-package-data=battery_analysis",
        "--include-data-dir=config=config",
        
        # 排除开发依赖
        "--nofollow-import-to=pytest",
        "--nofollow-import-to=black",
        "--nofollow-import-to=flake8",
        "--nofollow-import-to=pylint",
        "--nofollow-import-to=astroid",
        
        # 优化选项
        "--assume-yes-for-downloads",
        "--show-progress",
        "--show-memory",
        
        # 入口点
        str(ENTRY_POINT)
    ]
    
    print("=" * 60)
    print(f"开始打包 {PRODUCT} v{VERSION}")
    print("=" * 60)
    print(f"入口点: {ENTRY_POINT}")
    print(f"输出目录: {DIST_DIR}")
    print("=" * 60)
    
    # 执行打包
    try:
        result = subprocess.run(nuitka_args, check=True)
        print("\n" + "=" * 60)
        print("✓ 打包成功!")
        print(f"可执行文件位置: {DIST_DIR / 'BatteryAnalysis.exe'}")
        print("=" * 60)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("✗ 打包失败!")
        print(f"错误代码: {e.returncode}")
        print("=" * 60)
        return e.returncode

if __name__ == "__main__":
    sys.exit(build())
```

## 调试模式打包

如果需要查看控制台输出进行调试：

```bash
python -m nuitka \
    --standalone \
    --onefile \
    --enable-plugin=pyqt6 \
    --windows-console-mode=attach \
    --output-dir=dist \
    --output-filename=BatteryAnalysis-Debug.exe \
    src/battery_analysis/main/main_window.py
```

## 性能优化选项

### LTO（链接时优化）

```bash
--lto=yes
```

### PGO（配置文件引导优化）

```bash
# 第一步：生成配置文件
python -m nuitka --pgo --output-dir=dist src/battery_analysis/main/main_window.py

# 运行程序收集性能数据
dist/main_window.exe

# 第二步：使用配置文件优化编译
python -m nuitka --pgo-use --output-dir=dist src/battery_analysis/main/main_window.py
```

### 并行编译

```bash
--jobs=8  # 使用 8 个并行任务
```

## 常见问题

### 1. 缺少 DLL 文件

如果运行时提示缺少 DLL，添加：
```bash
--include-data-files=path/to/missing.dll=.
```

### 2. 导入错误

如果某些模块未被正确包含：
```bash
--include-module=module_name
```

### 3. 资源文件缺失

确保包含所有资源文件：
```bash
--include-data-dir=config=config
--include-data-dir=src/battery_analysis/resources=battery_analysis/resources
```

### 4. PyQt6 插件问题

确保启用 PyQt6 插件：
```bash
--enable-plugin=pyqt6
```

### 5. 打包体积过大

排除不必要的依赖：
```bash
--nofollow-import-to=pytest
--nofollow-import-to=matplotlib.tests
```

## 与 PyInstaller 对比

| 特性 | Nuitka | PyInstaller |
|------|--------|-------------|
| 启动速度 | 快（原生代码） | 慢（解压+解释） |
| 运行性能 | 优秀（编译优化） | 一般（解释执行） |
| 打包体积 | 较小 | 较大 |
| 打包速度 | 慢（需编译） | 快 |
| 兼容性 | 好 | 很好 |
| 调试难度 | 较高 | 较低 |

## 推荐工作流

1. **开发阶段**: 直接运行 Python 脚本
2. **测试阶段**: 使用 PyInstaller 快速打包测试
3. **发布阶段**: 使用 Nuitka 优化打包发布

## 完整打包脚本

将以下内容保存为 `build.bat`（Windows）：

```batch
@echo off
echo ========================================
echo Battery Analysis - Nuitka Build Script
echo ========================================
echo.

REM 激活虚拟环境（如果使用）
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM 清理旧的构建文件
if exist dist\BatteryAnalysis.exe (
    echo Cleaning old build...
    del /Q dist\BatteryAnalysis.exe
)

REM 执行打包
echo Starting Nuitka build...
python -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=pyqt6 ^
    --enable-plugin=numpy ^
    --windows-icon-from-ico=config/resources/icons/Icon_BatteryTestGUI.ico ^
    --windows-console-mode=disable ^
    --output-dir=dist ^
    --output-filename=BatteryAnalysis.exe ^
    --company-name="Ewin Hardware Group" ^
    --product-name="Battery Analysis" ^
    --file-version=2.8.1 ^
    --product-version=2.8.1 ^
    --file-description="Battery test data analysis application" ^
    --copyright="Copyright (c) 2024 Ewin Hardware Group" ^
    --include-package=battery_analysis ^
    --include-package-data=battery_analysis ^
    --include-data-dir=config=config ^
    --nofollow-import-to=pytest ^
    --nofollow-import-to=black ^
    --nofollow-import-to=flake8 ^
    --nofollow-import-to=pylint ^
    --assume-yes-for-downloads ^
    --show-progress ^
    --show-memory ^
    src/battery_analysis/main/main_window.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo Output: dist\BatteryAnalysis.exe
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Build failed with error code %ERRORLEVEL%
    echo ========================================
)

pause
```

## 参考资源

- [Nuitka 官方文档](https://nuitka.net/doc/user-manual.html)
- [Nuitka GitHub](https://github.com/Nuitka/Nuitka)
- [PyQt6 打包指南](https://nuitka.net/doc/user-manual.html#pyqt6)
