"""config_migration 测试

覆盖 v3 迁移（清理旧版 data_processor 误写的字面顶级 INI 键）、
v4 迁移（移除 battery.specifications 存储副本，改为读取时从 rules 派生）
和 v5 迁移（默认规则对齐 BatteryQualityRequirements_v2.3 §7.1.1）。
"""

from battery_analysis.utils.config_migration import (
    CURRENT_CONFIG_VERSION,
    run_migrations,
)


class TestVersion:
    def test_current_version_is_5(self):
        assert CURRENT_CONFIG_VERSION == 5


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


class TestMigrateV5PdfRules:
    """v5：旧默认规则行 → BatteryQualityRequirements_v2.3 对齐值"""

    OLD_DEFAULTS = [
        "CP224642A/1S1P/920/920/80%/5.0",
        "CF583083/1S1P/4000/4000/80%/5.0",
        "CP305050/1S1P/2000/2000/80%/1.0",
    ]
    NEW_DEFAULTS = [
        "CP224642A/1S1P/920/920/85%|75%/2",
        "CF583083/1S1P/4000/4000/3000/50",
        "CP305050/1S1P/2000/2000/85%|75%/5",
    ]

    def test_old_default_rules_replaced(self):
        config = {"version": 4, "battery": {"rules": list(self.OLD_DEFAULTS)}}
        result = run_migrations(config)
        assert result["battery"]["rules"] == self.NEW_DEFAULTS
        assert result["version"] == CURRENT_CONFIG_VERSION

    def test_user_modified_rules_kept(self):
        # 用户改过的规则（与旧默认不一致）不被触碰
        custom = "CP224642A/1S1P/920/920/70%/3.0"
        config = {"version": 4, "battery": {"rules": [custom, "CR2450/1S1P/600/550/380/1.0"]}}
        result = run_migrations(config)
        assert result["battery"]["rules"][0] == custom
        assert result["battery"]["rules"][1] == "CR2450/1S1P/600/550/380/1.0"

    def test_already_aligned_rules_untouched(self):
        config = {"version": 4, "battery": {"rules": list(self.NEW_DEFAULTS)}}
        result = run_migrations(config)
        assert result["battery"]["rules"] == self.NEW_DEFAULTS

    def test_migrated_values_match_pdf(self):
        """迁移后的期望值/CC 电流与 PDF 口径一致（螺旋 85%、Hermes 3000、CC 2/50/5）"""
        from battery_analysis.utils.pulse_currents import (
            required_useable_capacity_from_rule,
        )

        config = {"version": 4, "battery": {"rules": list(self.OLD_DEFAULTS)}}
        result = run_migrations(config)
        rules = result["battery"]["rules"]
        assert required_useable_capacity_from_rule(rules[0], "Spiral Type") == 782  # 920×85%
        assert required_useable_capacity_from_rule(rules[0], "Laminate Type") == 690  # 920×75%
        assert required_useable_capacity_from_rule(rules[1]) == 3000  # Hermes 主期望
        assert required_useable_capacity_from_rule(rules[2], "Spiral Type") == 1700  # 2000×85%
        assert required_useable_capacity_from_rule(rules[2], "Laminate Type") == 1500  # 2000×75%
        assert rules[0].split("/")[5] == "2"  # <1200: 2mA/10h
        assert rules[1].split("/")[5] == "50"  # Hermes: 50mA/1h
        assert rules[2].split("/")[5] == "5"  # 2000-3000: 5mA/4h
