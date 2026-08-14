"""配置默认值回归测试——specifications 必须从 rules 自动派生"""

from battery_analysis.utils.config_defaults import DEFAULT_CONFIG
from battery_analysis.utils.battery_classifier import derive_specifications


def test_specifications_derived_from_rules():
    assert DEFAULT_CONFIG["battery"]["specifications"] == derive_specifications(
        DEFAULT_CONFIG["battery"]["rules"])
    assert DEFAULT_CONFIG["battery"]["specifications"]["Coin Cell"]  # 非空
    assert "CP305050" in DEFAULT_CONFIG["battery"]["specifications"]["Pouch Cell"]
