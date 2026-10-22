"""测试包装脚本的工作目录、报告参数和失败状态。"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from scripts import run_coverage_test, run_tests

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("returncode", [0, 1, 5])
def test_test_runner_uses_project_root(monkeypatch, returncode):
    run = Mock(return_value=subprocess.CompletedProcess([], returncode, "", ""))
    monkeypatch.setattr(run_tests.subprocess, "run", run)
    assert run_tests.run_tests("tests/test_build_scripts.py") is (returncode == 0)
    assert run.call_args.kwargs["cwd"] == ROOT
    assert run.call_args.args[0][-1] == "tests/test_build_scripts.py"


@pytest.mark.parametrize("report_format, option", [("html", "--html"), ("xml", "--junitxml")])
def test_report_options(monkeypatch, report_format, option):
    run = Mock(return_value=subprocess.CompletedProcess([], 0, "", ""))
    monkeypatch.setattr(run_tests.subprocess, "run", run)
    assert run_tests.run_tests(generate_report=True, report_format=report_format)
    assert option in run.call_args.args[0]


@pytest.mark.parametrize("returncode", [0, 1, 5])
def test_coverage_propagates_exit_code_and_uses_project_root(monkeypatch, returncode):
    run = Mock(return_value=subprocess.CompletedProcess([], returncode, "", ""))
    monkeypatch.setattr(run_coverage_test.subprocess, "run", run)
    monkeypatch.setattr(sys, "argv", ["run_coverage_test.py"])
    assert run_coverage_test.main() == returncode
    assert run.call_args.kwargs["cwd"] == ROOT


def test_coverage_launch_error_is_failure(monkeypatch):
    monkeypatch.setattr(
        run_coverage_test.subprocess, "run", Mock(side_effect=OSError("cannot start"))
    )
    assert run_coverage_test.run_coverage_test() == 1
