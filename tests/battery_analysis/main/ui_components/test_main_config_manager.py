import logging
from unittest.mock import Mock

from battery_analysis.main.services.config_service import ConfigService
from battery_analysis.main.ui_components.config_manager import ConfigManager


class TestConfigManager:
    def setup_method(self):
        mock_main_window = Mock()
        self.manager = ConfigManager(mock_main_window)

    def test_get_config(self):
        result = self.manager.get_config("test_key")
        assert isinstance(result, list)

    def test_has_config(self):
        result = self.manager.has_config()
        assert isinstance(result, bool)

    def test_reload_config(self):
        self.manager.reload_config()

    def test_get_current_config_path(self):
        result = self.manager.get_current_config_path()
        assert result is None or isinstance(result, str)


class TestSpecificationKeysDerivedFromRules:
    """SpecificationTypeCoinCell/PouchCell 不再存储，读取时由 battery.rules 派生"""

    def _make_manager(self, tmp_path):
        manager = ConfigManager.__new__(ConfigManager)
        manager.logger = logging.getLogger("test_config_manager")
        manager.main_window = None
        manager._config_service = ConfigService()
        assert manager._config_service.load_config(str(tmp_path / "config.json"))
        manager.b_has_config = True
        return manager

    def test_not_in_ini_mapping(self):
        # 旧的 battery.specifications 别名已删除
        assert "BatteryConfig/SpecificationTypeCoinCell" not in ConfigManager._INI_TO_JSON_KEY
        assert "BatteryConfig/SpecificationTypePouchCell" not in ConfigManager._INI_TO_JSON_KEY

    def test_derives_from_default_rules(self, tmp_path):
        manager = self._make_manager(tmp_path)
        coin = manager.get_config("BatteryConfig/SpecificationTypeCoinCell")
        pouch = manager.get_config("BatteryConfig/SpecificationTypePouchCell")
        assert "CR2450" in coin
        assert "CF583083" in pouch
        # 两个分栏合起来恰好覆盖 rules 中的所有型号
        rules = manager.get_config("BatteryConfig/Rules")
        assert set(coin) | set(pouch) == {r.split("/")[0] for r in rules}

    def test_reflects_rules_edits(self, tmp_path):
        manager = self._make_manager(tmp_path)
        manager._config_service.set_config_value(
            "battery.rules",
            [
                "CR2032/1S1P/200/180/120/1.0",
                "CP305050/1S1P/2000/2000/80%/1.0",
            ],
        )
        assert manager.get_config("BatteryConfig/SpecificationTypeCoinCell") == ["CR2032"]
        assert manager.get_config("BatteryConfig/SpecificationTypePouchCell") == [
            "CP305050"
        ]


class TestUpdateConfigCcCurrent:
    """update_config 的 cc_current 兜底必须取当前规格匹配规则的 rule_parts[5]（CC 电流 mA）"""

    RULES = [
        "CR2450/1S1P/600/550/380/1.0",
        "CP305050/1S1P/2000/2000/80%/10",
    ]

    def _make_manager(self, spec: str, rules=None, cc_current: str = ""):
        manager = ConfigManager.__new__(ConfigManager)
        manager.logger = logging.getLogger("test_config_manager")
        mw = Mock()
        mw.cc_current = cc_current
        mw.listCurrentLevel = []
        mw.comboBox_Specification_Type.currentText.return_value = spec
        mw.config_manager.get_config.return_value = rules or self.RULES
        manager.main_window = mw
        return manager, mw

    def test_takes_cc_current_from_matched_rule(self):
        manager, mw = self._make_manager("CP305050")
        manager.update_config([])
        # 旧行为：取第一条规则的 1.0（与所选规格无关）
        assert mw.cc_current == "10"

    def test_keeps_filename_parsed_cc_current(self):
        manager, mw = self._make_manager("CP305050", cc_current="2")
        manager.update_config([])
        assert mw.cc_current == "2"  # 文件名解析优先，不被规则兜底覆盖

    def test_unknown_spec_leaves_cc_current_empty(self):
        manager, mw = self._make_manager("CP999999X")
        manager.update_config([])
        assert mw.cc_current == ""
        mw.checker_update_config.set_error.assert_called_with("PltTitle")

    def test_short_rule_does_not_raise(self):
        manager, mw = self._make_manager("CR2450", rules=["CR2450/1S1P"])
        manager.update_config([])
        assert mw.cc_current == ""
