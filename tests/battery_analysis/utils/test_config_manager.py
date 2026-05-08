import pytest
import tempfile
import os
from pathlib import Path
from battery_analysis.utils.config_manager import IniFileManager


class TestIniFileManager:
    def setup_method(self):
        self.manager = IniFileManager()
        # 创建临时 INI 文件用于测试
        self.tmp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmp_dir, "test.ini")
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("[Section1]\nkey1 = value1\nkey2 = 42\nkey3 = true\n\n[Section2]\nfoo = bar\n")

    def teardown_method(self):
        # 清理临时文件
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.tmp_dir)

    def test_read_config(self):
        result = self.manager.read_config(self.config_path)
        assert result is True

    def test_read_config_file_not_exists(self):
        result = self.manager.read_config("/nonexistent/path.ini")
        assert result is False

    def test_get_value_string(self):
        self.manager.read_config(self.config_path)
        value = self.manager.get_value("Section1/key1")
        assert value == "value1"

    def test_get_value_int(self):
        self.manager.read_config(self.config_path)
        value = self.manager.get_value("Section1/key2")
        assert value == 42

    def test_get_value_bool(self):
        self.manager.read_config(self.config_path)
        value = self.manager.get_value("Section1/key3")
        assert value is True

    def test_get_value_default(self):
        self.manager.read_config(self.config_path)
        value = self.manager.get_value("Section1/nonexistent", default="fallback")
        assert value == "fallback"

    def test_get_value_raw(self):
        self.manager.read_config(self.config_path)
        value = self.manager.get_value_raw("Section1/key2")
        assert value == "42"

    def test_set_value_and_write(self):
        self.manager.read_config(self.config_path)
        self.manager.set_value("Section1/key1", "new_value")
        # 读取同一 key 验证已修改
        assert self.manager.get_value("Section1/key1") == "new_value"

    def test_write_config(self):
        self.manager.read_config(self.config_path)
        self.manager.set_value("Section1/key1", "written")
        result = self.manager.write_config(self.config_path)
        assert result is True
        # 重新读取验证写入成功
        new_manager = IniFileManager()
        new_manager.read_config(self.config_path)
        assert new_manager.get_value("Section1/key1") == "written"

    def test_has_key_exists(self):
        self.manager.read_config(self.config_path)
        assert self.manager.has_key("Section1/key1") is True

    def test_has_key_not_exists(self):
        self.manager.read_config(self.config_path)
        assert self.manager.has_key("Section1/nonexistent") is False

    def test_get_section(self):
        self.manager.read_config(self.config_path)
        section = self.manager.get_section("Section1")
        assert section["key1"] == "value1"
        assert section["key2"] == "42"

    def test_get_section_not_exists(self):
        self.manager.read_config(self.config_path)
        section = self.manager.get_section("NonExistentSection")
        assert section == {}

    def test_get_sections(self):
        self.manager.read_config(self.config_path)
        sections = self.manager.get_sections()
        assert "Section1" in sections
        assert "Section2" in sections

    def test_get_all_values(self):
        self.manager.read_config(self.config_path)
        all_values = self.manager.get_all_values()
        assert "Section1" in all_values
        assert "Section2" in all_values
        assert all_values["Section1"]["key1"] == "value1"

    def test_clear_cache_clears_specific(self):
        self.manager.read_config(self.config_path)
        assert self.manager.get_value("Section1/key1") == "value1"
        self.manager.clear_cache(self.config_path)
        # 清除后再次读取应能重新加载
        assert self.manager.read_config(self.config_path) is True
        assert self.manager.get_value("Section1/key1") == "value1"

    def test_clear_cache_clears_all(self):
        self.manager.read_config(self.config_path)
        self.manager.clear_cache()
        assert self.manager.read_config(self.config_path) is True
        assert self.manager.get_value("Section1/key1") == "value1"
