"""测试 scripts/build.py 的构建失败检测逻辑"""
from unittest.mock import Mock

import pytest

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


class TestBuildFailurePropagation:
    """集成回归：PyInstaller 命令非零时 build() 必须 SystemExit(1)，堵住 CI 假绿。"""

    def _make_manager(self, monkeypatch):
        import subprocess
        from scripts.build import BuildConfig, BuildManager

        # 避免 BuildManager.__init__ 清理/创建真实构建目录
        monkeypatch.setattr(BuildManager, "clean_build_dirs", lambda self: None)
        manager = BuildManager("Release")
        # 直接调用 build() 不会执行 copy2dir()，需预创建各应用构建目录，否则图标复制失败
        for app in manager.apps_config:
            app["build_dir"].mkdir(parents=True, exist_ok=True)
        return manager, subprocess

    def test_pyinstaller_nonzero_exits(self, monkeypatch):
        manager, subprocess = self._make_manager(monkeypatch)
        monkeypatch.setattr(
            manager, "_execute_pyinstaller_command",
            lambda app_dir, cmd_args: subprocess.CompletedProcess(cmd_args, 1),
        )
        with pytest.raises(SystemExit) as excinfo:
            manager.build()
        assert excinfo.value.code == 1

    def test_pyinstaller_zero_does_not_exit(self, monkeypatch):
        manager, subprocess = self._make_manager(monkeypatch)
        monkeypatch.setattr(
            manager, "_execute_pyinstaller_command",
            lambda app_dir, cmd_args: subprocess.CompletedProcess(cmd_args, 0),
        )
        manager.build()  # 不抛 SystemExit 即通过
