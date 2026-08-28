#!/usr/bin/env python3
"""
测试运行脚本
用于执行项目的自动测试流程
"""

import argparse
import os
import subprocess
import sys


def run_tests(test_path=None, generate_report=False, report_format="html"):
    """
    运行测试

    Args:
        test_path: 测试路径（可选），如果提供则只运行该路径下的测试
        generate_report: 是否生成测试报告
        report_format: 测试报告格式（html、xml、junit-xml等）
    """
    print("开始运行测试...")

    # 构建 pytest 命令（通过 uv run 确保使用项目虚拟环境）
    pytest_cmd = ["uv", "run", "pytest"]

    if test_path:
        pytest_cmd.append(test_path)

    if generate_report:
        report_file = f"test_report.{report_format}"
        if report_format == "html":
            pytest_cmd.extend(["--html", report_file, "--self-contained-html"])
        elif report_format in ["xml", "junit-xml"]:
            pytest_cmd.extend(["--junitxml", report_file])
        else:
            print(f"不支持的报告格式: {report_format}")
            return False

    # 执行测试命令
    try:
        result = subprocess.run(
            pytest_cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
        )

        # 打印测试输出
        print(result.stdout)
        if result.stderr:
            print("测试错误:")
            print(result.stderr)

        # 检查测试结果
        if result.returncode == 0:
            print("所有测试通过!")
            return True
        else:
            print(f"测试失败，返回码: {result.returncode}")
            return False

    except (subprocess.SubprocessError, OSError) as e:
        print(f"运行测试时出错: {e}")
        return False


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description="项目自动测试脚本")
    parser.add_argument(
        "test_path",
        nargs="?",
        default=None,
        help="测试路径（可选），如果提供则只运行该路径下的测试",
    )
    parser.add_argument("-r", "--report", action="store_true", help="生成测试报告")
    parser.add_argument(
        "-f",
        "--format",
        default="html",
        choices=["html", "xml", "junit-xml"],
        help="测试报告格式（默认：html）",
    )

    args = parser.parse_args()

    # 运行测试（依赖由 uv sync 管理，无需手动安装）
    success = run_tests(args.test_path, args.report, args.format)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
