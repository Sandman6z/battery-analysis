import sys
import tomllib
from pathlib import Path

from battery_analysis._version import __version__
from battery_analysis.utils.version import Version, get_version


class TestVersion:
    def test_version_is_nonempty_string(self):
        assert isinstance(Version().version, str)
        assert len(Version().version) > 0

    def test_version_matches_single_source(self, monkeypatch):
        """非 debug 环境下，Version().version 与 _version.py 单一源一致"""
        monkeypatch.delenv("DEBUG", raising=False)
        monkeypatch.delenv("APP_DEBUG", raising=False)
        monkeypatch.setattr(sys, "argv", ["pytest"])
        assert Version().version == __version__

    def test_get_version_matches_package_version(self, monkeypatch):
        monkeypatch.delenv("DEBUG", raising=False)
        monkeypatch.delenv("APP_DEBUG", raising=False)
        monkeypatch.setattr(sys, "argv", ["pytest"])
        assert get_version() == __version__

    def test_debug_suffix_appended(self, monkeypatch):
        """DEBUG 环境下版本号附加 .debug 后缀"""
        monkeypatch.setenv("DEBUG", "1")
        monkeypatch.delenv("APP_DEBUG", raising=False)
        assert get_version() == __version__ + ".debug"

    def test_pyproject_declares_dynamic_version(self):
        """pyproject.toml 不写死版本号，声明为动态并从 _version.py 读取"""
        root = Path(__file__).resolve().parents[3]
        with open(root / "pyproject.toml", "rb") as f:
            data = tomllib.load(f)

        project = data["project"]
        assert "version" not in project
        assert "version" in project["dynamic"]

        dynamic = data["tool"]["setuptools"]["dynamic"]
        assert dynamic["version"]["attr"] == "battery_analysis._version.__version__"
