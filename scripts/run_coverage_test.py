#!/usr/bin/env python3
"""
运行覆盖率测试的脚本

此脚本可通过VS Code的运行按钮直接执行，无需依赖VS Code的测试发现机制。

用法:
    uv run python scripts/run_coverage_test.py                          # 全项目覆盖率
    uv run python scripts/run_coverage_test.py tests/battery_analysis/  # 指定目录
    uv run python scripts/run_coverage_test.py --module battery_analysis.utils  # 指定模块
"""

import argparse
import os
import subprocess
import sys


def run_coverage_test(test_path="tests/", cov_module="battery_analysis"):
    """运行覆盖率测试"""
    print("开始运行覆盖率测试...")
    print(f"当前工作目录: {os.getcwd()}")

    # 构建测试命令
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        test_path,
        f"--cov={cov_module}",
        "--cov-report=html",
        "-v",
    ]

    print(f"执行命令: {' '.join(cmd)}")

    # 执行测试
    result = subprocess.run(cmd, capture_output=True, text=True)

    # 输出结果
    print("\n测试输出:")
    print(result.stdout)

    if result.stderr:
        print("\n错误信息:")
        print(result.stderr)

    print(f"\n测试完成，返回码: {result.returncode}")

    if result.returncode == 0:
        print("\n🎉 测试成功完成！")
        print("📊 覆盖率报告已生成在 htmlcov/ 目录中")
        print("🔍 请打开 htmlcov/index.html 文件查看详细报告")
    else:
        print("\n❌ 测试失败，请查看上面的错误信息")


def main():
    parser = argparse.ArgumentParser(description="运行项目覆盖率测试")
    parser.add_argument("test_path", nargs="?", default="tests/", help="测试路径（默认：tests/）")
    parser.add_argument(
        "-m",
        "--module",
        default="battery_analysis",
        help="覆盖率测量的模块（默认：battery_analysis）",
    )

    args = parser.parse_args()
    run_coverage_test(args.test_path, args.module)


if __name__ == "__main__":
    main()
