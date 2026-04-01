#!/usr/bin/env python3
"""
运行覆盖率测试的脚本

此脚本可通过VS Code的运行按钮直接执行，无需依赖VS Code的测试发现机制。
"""

import subprocess
import sys
import os


def run_coverage_test():
    """运行覆盖率测试"""
    print("开始运行覆盖率测试...")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 构建测试命令
    cmd = [
        sys.executable,
        "-m", "pytest",
        "tests/battery_analysis/utils/test_config_utils.py",
        "--cov=battery_analysis.utils.config_utils",
        "--cov-report=html",
        "-v"
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


if __name__ == "__main__":
    run_coverage_test()
