import json

from battery_analysis.main.services.config_service import ConfigService


class TestConfigService:
    def setup_method(self):
        self.service = ConfigService()

    def test_initialization(self):
        assert self.service is not None

    def test_get_config_value_default(self):
        result = self.service.get_config_value("nonexistent.key", "default_val")
        assert result == "default_val"

    def test_get_config_sections(self):
        result = self.service.get_config_sections()
        assert isinstance(result, list)


class TestSpecificationsKeyRemoved:
    """specifications 已彻底移除：不存储、不可读（规格列表由读取方从 rules 派生）"""

    def setup_method(self):
        self.service = ConfigService()

    def _load_fresh(self, tmp_path):
        path = tmp_path / "config.json"
        assert self.service.load_config(str(path))
        return path

    def test_specifications_key_not_readable(self, tmp_path):
        self._load_fresh(tmp_path)
        assert self.service.get_config_value("battery.specifications", None) is None
        assert self.service.has_config_key("battery.specifications") is False

    def test_saved_config_has_no_specifications_key(self, tmp_path):
        path = self._load_fresh(tmp_path)
        assert self.service.save_config()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "specifications" not in data.get("battery", {})

    def test_legacy_stale_copy_removed_on_load(self, tmp_path):
        """旧版 v3 config.json 中的陈旧 specifications 在加载（迁移 v4）时被删除"""
        path = tmp_path / "config.json"
        path.write_text(
            json.dumps(
                {
                    "version": 3,
                    "battery": {
                        "rules": ["CR2450/1S1P/600/550/380/1.0"],
                        "specifications": {"Coin Cell": ["STALE-NAME"], "Pouch Cell": []},
                    },
                }
            ),
            encoding="utf-8",
        )
        assert self.service.load_config(str(path))
        assert "specifications" not in self.service.get_config_value("").get("battery", {})
        assert self.service.get_config_value("battery.specifications", None) is None
        # rules 原样保留，规格列表由读取方从它派生
        assert self.service.get_config_value("battery.rules", []) == [
            "CR2450/1S1P/600/550/380/1.0"
        ]
