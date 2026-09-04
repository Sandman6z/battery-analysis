"""JSON 配置管理器 (json_config_manager) 测试

测试 json_config_manager.py 中 JsonConfigManager 的读取、写入、
原子替换、点号路径访问、错误处理等逻辑。
"""

import json
import os

import pytest

from battery_analysis.utils.json_config_manager import JsonConfigManager


class TestReadConfig:
    """read_config 测试。"""

    def test_read_valid_json(self, tmp_path):
        """正常读取合法 JSON 文件。"""
        cfg = tmp_path / "config.json"
        cfg.write_text(json.dumps({"battery": {"types": ["A", "B"]}}), encoding="utf-8")
        mgr = JsonConfigManager()
        assert mgr.read_config(str(cfg)) is True
        assert mgr.is_loaded() is True
        assert mgr.get("battery.types") == ["A", "B"]

    def test_read_nonexistent_file(self, tmp_path):
        """读取不存在的文件应返回 False。"""
        mgr = JsonConfigManager()
        assert mgr.read_config(str(tmp_path / "nope.json")) is False
        assert mgr.is_loaded() is False

    def test_read_invalid_json(self, tmp_path):
        """读取 JSON 格式错误的文件应返回 False。"""
        cfg = tmp_path / "bad.json"
        cfg.write_text("{invalid json", encoding="utf-8")
        mgr = JsonConfigManager()
        assert mgr.read_config(str(cfg)) is False
        assert mgr.is_loaded() is False

    def test_read_empty_file(self, tmp_path):
        """读取空文件应返回 False（JSONDecodeError）。"""
        cfg = tmp_path / "empty.json"
        cfg.write_text("", encoding="utf-8")
        mgr = JsonConfigManager()
        assert mgr.read_config(str(cfg)) is False


class TestWriteConfig:
    """write_config 原子写入测试。"""

    def test_write_creates_file(self, tmp_path):
        """write_config 应创建目标文件。"""
        cfg_path = str(tmp_path / "out.json")
        mgr = JsonConfigManager()
        mgr.replace_all({"key": "value"})
        assert mgr.write_config(cfg_path) is True
        assert os.path.exists(cfg_path)
        with open(cfg_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data == {"key": "value"}

    def test_write_creates_parent_dirs(self, tmp_path):
        """write_config 应自动创建父目录。"""
        cfg_path = str(tmp_path / "sub" / "dir" / "config.json")
        mgr = JsonConfigManager()
        mgr.replace_all({"a": 1})
        assert mgr.write_config(cfg_path) is True
        assert os.path.exists(cfg_path)

    def test_write_preserves_unicode(self, tmp_path):
        """写入应保留中文等 Unicode 字符。"""
        cfg_path = str(tmp_path / "cn.json")
        mgr = JsonConfigManager()
        mgr.replace_all({"name": "电池分析"})
        mgr.write_config(cfg_path)
        with open(cfg_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["name"] == "电池分析"

    def test_atomic_write_no_temp残留(self, tmp_path):
        """写入后不应残留临时文件。"""
        cfg_path = str(tmp_path / "atomic.json")
        mgr = JsonConfigManager()
        mgr.replace_all({"x": 1})
        mgr.write_config(cfg_path)
        tmp_files = [f for f in os.listdir(tmp_path) if f.startswith("config_")]
        assert len(tmp_files) == 0


class TestGetSet:
    """get/set 点号路径访问测试。"""

    def test_get_simple_key(self):
        """简单 key 路径应返回对应值。"""
        mgr = JsonConfigManager()
        mgr.replace_all({"a": 1})
        assert mgr.get("a") == 1

    def test_get_nested_key(self):
        """嵌套 key 路径应返回对应值。"""
        mgr = JsonConfigManager()
        mgr.replace_all({"a": {"b": {"c": 42}}})
        assert mgr.get("a.b.c") == 42

    def test_get_missing_key_returns_default(self):
        """不存在的 key 应返回默认值。"""
        mgr = JsonConfigManager()
        mgr.replace_all({"a": 1})
        assert mgr.get("missing") is None
        assert mgr.get("missing", "fallback") == "fallback"

    def test_get_empty_path_returns_all(self):
        """空字符串路径应返回完整数据字典。"""
        mgr = JsonConfigManager()
        data = {"a": 1, "b": 2}
        mgr.replace_all(data)
        assert mgr.get("") == data

    def test_get_before_load_returns_default(self):
        """未加载时 get 应返回默认值。"""
        mgr = JsonConfigManager()
        assert mgr.get("any", "default") == "default"

    def test_set_simple_key(self):
        """set 简单 key 应成功。"""
        mgr = JsonConfigManager()
        mgr.replace_all({})
        assert mgr.set("a", 1) is True
        assert mgr.get("a") == 1

    def test_set_nested_key(self):
        """set 嵌套 key 应创建中间层。"""
        mgr = JsonConfigManager()
        mgr.replace_all({})
        mgr.set("a.b.c", 42)
        assert mgr.get("a.b.c") == 42

    def test_set_overwrites_existing(self):
        """set 已有 key 应覆盖值。"""
        mgr = JsonConfigManager()
        mgr.replace_all({"a": 1})
        mgr.set("a", 2)
        assert mgr.get("a") == 2


class TestReplaceAllAndClear:
    """replace_all / set_defaults / clear 测试。"""

    def test_replace_all(self):
        """replace_all 应替换整个数据。"""
        mgr = JsonConfigManager()
        mgr.replace_all({"a": 1})
        mgr.replace_all({"b": 2})
        assert mgr.get("a") is None
        assert mgr.get("b") == 2

    def test_set_defaults(self):
        """set_defaults 应填充默认数据并标记为已加载。"""
        mgr = JsonConfigManager()
        mgr.set_defaults({"default_key": "default_value"})
        assert mgr.is_loaded() is True
        assert mgr.get("default_key") == "default_value"

    def test_clear(self):
        """clear 应清空数据并标记为未加载。"""
        mgr = JsonConfigManager()
        mgr.replace_all({"a": 1})
        mgr.clear()
        assert mgr.is_loaded() is False
        assert mgr.get("a") is None

    def test_get_all(self):
        """get_all 应返回完整数据字典。"""
        mgr = JsonConfigManager()
        data = {"x": 1, "y": [1, 2, 3]}
        mgr.replace_all(data)
        assert mgr.get_all() == data


class TestRoundTrip:
    """读写往返测试。"""

    def test_write_then_read(self, tmp_path):
        """写入后重新读取应得到相同数据。"""
        cfg_path = str(tmp_path / "roundtrip.json")
        original_data = {"battery": {"types": ["Coin", "Pouch"]}, "version": 2}

        mgr1 = JsonConfigManager()
        mgr1.replace_all(original_data)
        mgr1.write_config(cfg_path)

        mgr2 = JsonConfigManager()
        mgr2.read_config(cfg_path)
        assert mgr2.get_all() == original_data
