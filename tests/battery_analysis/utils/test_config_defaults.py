"""配置默认值回归测试——specifications 不再落盘，唯一数据源是 battery.rules"""

from battery_analysis.utils.battery_classifier import derive_specifications
from battery_analysis.utils.config_defaults import DEFAULT_CONFIG


def test_specifications_not_stored_in_defaults():
    assert "specifications" not in DEFAULT_CONFIG["battery"]


def test_default_rules_derive_expected_specifications():
    specs = derive_specifications(DEFAULT_CONFIG["battery"]["rules"])
    assert specs["Coin Cell"]  # 非空
    assert "CP305050" in specs["Pouch Cell"]
    assert "CR2450" in specs["Coin Cell"]
