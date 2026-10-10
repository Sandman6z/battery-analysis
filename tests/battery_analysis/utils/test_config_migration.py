"""config_migration 测试

覆盖 v3 迁移（清理旧版 data_processor 误写的字面顶级 INI 键）
和 v4 迁移（移除 battery.specifications 存储副本，改为读取时从 rules 派生）。
"""

from battery_analysis.utils.config_migration import (
    CURRENT_CONFIG_VERSION,
    run_migrations,
)


class TestVersion:
    def test_current_version_is_4(self):
        assert CURRENT_CONFIG_VERSION == 4


class TestMigrateV3OrphanKeys:
    def test_orphan_ini_style_key_removed(self):
        config = {
            "version": 2,
            "battery": {"pulseCurrents": [30.0, 26.0, 15.0, 6.0]},
            "BatteryConfig/PulseCurrent": "30, 26, 15, 6",
        }
        result = run_migrations(config)
        assert "BatteryConfig/PulseCurrent" not in result
        assert result["battery"]["pulseCurrents"] == [30.0, 26.0, 15.0, 6.0]
        assert result["version"] == CURRENT_CONFIG_VERSION

    def test_normal_keys_untouched(self):
        config = {"version": 2, "battery": {}, "test": {"locations": ["loc1"]}}
        result = run_migrations(config)
        assert result["test"] == {"locations": ["loc1"]}
        assert result["battery"] == {}

    def test_already_migrated_config_skipped(self):
        config = {"version": CURRENT_CONFIG_VERSION, "keep": 1}
        result = run_migrations(config)
        assert result["version"] == CURRENT_CONFIG_VERSION
        assert result["keep"] == 1

    def test_multiple_orphan_keys(self):
        config = {
            "version": 1,
            "BatteryConfig/PulseCurrent": "30",
            "BatteryConfig/CutOffVoltage": "2.25",
        }
        result = run_migrations(config)
        assert not any("/" in k for k in result)
        assert result["version"] == CURRENT_CONFIG_VERSION


class TestMigrateV4DerivedSpecs:
    def test_stale_specifications_removed(self):
        config = {
            "version": 3,
            "battery": {
                "rules": ["CR2450/1S1P/600/550/380/1.0"],
                "specifications": {"Coin Cell": ["OBSOLETE-NAME"], "Pouch Cell": []},
            },
        }
        result = run_migrations(config)
        assert "specifications" not in result["battery"]
        assert result["battery"]["rules"] == ["CR2450/1S1P/600/550/380/1.0"]
        assert result["version"] == CURRENT_CONFIG_VERSION

    def test_battery_without_specifications_untouched(self):
        config = {"version": 3, "battery": {"rules": ["CR2450/1S1P/600/550/380/1.0"]}}
        result = run_migrations(config)
        assert result["battery"] == {"rules": ["CR2450/1S1P/600/550/380/1.0"]}
        assert result["version"] == CURRENT_CONFIG_VERSION
