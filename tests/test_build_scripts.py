"""测试 scripts/build.py 的构建失败检测逻辑"""
from unittest.mock import Mock

from scripts.build import _build_failed


class TestBuildFailed:
    def test_returncode_zero_is_success(self):
        assert _build_failed(Mock(returncode=0)) is False

    def test_returncode_nonzero_is_failure(self):
        assert _build_failed(Mock(returncode=1)) is True
        assert _build_failed(Mock(returncode=-1)) is True

    def test_none_result_is_failure(self):
        # _execute_pyinstaller_command 异常时返回 CompletedProcess(_, 1)，不可能为 None，
        # 但防御性处理 None 为失败
        assert _build_failed(None) is True
