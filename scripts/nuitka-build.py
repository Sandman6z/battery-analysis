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
CONFIG_DIR = ROOT_DIR / "config"
ICON_PATH = CONFIG_DIR / "resources/icons/Icon_BatteryTestGUI.ico"
ENTRY_POINT = SRC_DIR / "battery_analysis/main/main_window.py"

# 版本信息
VERSION = "2.8.2"
COMPANY = "Ewin Hardware Group"
PRODUCT = "Battery Analysis"


def check_requirements():
    """检查打包环境"""
    print("检查打包环境...")

    # 检查入口文件
    if not ENTRY_POINT.exists():
        print(f"✗ 错误: 入口文件不存在: {ENTRY_POINT}")
        return False

    # 检查图标文件
    if not ICON_PATH.exists():
        print(f"⚠ 警告: 图标文件不存在: {ICON_PATH}")
        print("  将使用默认图标")

    # 检查 Nuitka 是否安装
    try:
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ Nuitka 版本: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ 错误: Nuitka 未安装")
        print("  请运行: pip install nuitka")
        return False

    return True


def build(debug=False):
    """执行 Nuitka 打包

    Args:
        debug: 是否启用调试模式（显示控制台）
    """

    # 确保输出目录存在
    DIST_DIR.mkdir(exist_ok=True)

    # 输出文件名
    output_name = "BatteryAnalysis-Debug.exe" if debug else "BatteryAnalysis.exe"
    console_mode = "attach" if debug else "disable"

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
        f"--windows-console-mode={console_mode}",

        # 输出配置
        f"--output-dir={DIST_DIR}",
        f"--output-filename={output_name}",

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
        f"--include-data-dir={CONFIG_DIR}=config",

        # 排除开发依赖
        "--nofollow-import-to=pytest",
        "--nofollow-import-to=black",
        "--nofollow-import-to=flake8",
        "--nofollow-import-to=pylint",
        "--nofollow-import-to=astroid",
        "--nofollow-import-to=pylint_json2html",

        # 优化选项
        "--assume-yes-for-downloads",
        "--show-progress",
        "--show-memory",

        # 入口点
        str(ENTRY_POINT)
    ]

    # 添加图标（如果存在）
    if ICON_PATH.exists():
        nuitka_args.insert(-1, f"--windows-icon-from-ico={ICON_PATH}")

    print("=" * 70)
    print(f"开始打包 {PRODUCT} v{VERSION}")
    if debug:
        print("模式: 调试模式（显示控制台）")
    else:
        print("模式: 发布模式（无控制台）")
    print("=" * 70)
    print(f"入口点: {ENTRY_POINT}")
    print(f"输出目录: {DIST_DIR}")
    print(f"输出文件: {output_name}")
    print("=" * 70)
    print()

    # 执行打包
    try:
        result = subprocess.run(nuitka_args, check=True)
        print()
        print("=" * 70)
        print("✓ 打包成功!")
        print(f"可执行文件位置: {DIST_DIR / output_name}")
        print("=" * 70)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 70)
        print("✗ 打包失败!")
        print(f"错误代码: {e.returncode}")
        print("=" * 70)
        return e.returncode
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("⚠ 打包被用户中断")
        print("=" * 70)
        return 1


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Battery Analysis Nuitka 打包脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python nuitka-build.py              # 正常打包
  python nuitka-build.py --debug      # 调试模式打包（显示控制台）
        """
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式（显示控制台窗口）"
    )

    args = parser.parse_args()

    # 检查环境
    if not check_requirements():
        return 1

    print()

    # 执行打包
    return build(debug=args.debug)


if __name__ == "__main__":
    sys.exit(main())
