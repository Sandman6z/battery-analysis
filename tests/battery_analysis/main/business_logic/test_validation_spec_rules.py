"""validation_spec_rules 测试：规则填充与构造方法联动

覆盖 _fill_spec_rule_fields（绝对值 / 单百分比 / 85%|75% 双百分比）、
_apply_specification_rules 匹配逻辑与 check_construction 重算入口。
"""

from types import SimpleNamespace

import pytest

from battery_analysis.main.business_logic.validation_spec_rules import (
    ValidationSpecRulesMixin,
)

RULES = [
    "CR2450/1S1P/600/550/380/1.0",
    "CP224642A/1S1P/920/920/85%|75%/2",
    "CF583083/1S1P/4000/4000/3000/50",
    "CP305050/1S1P/2000/2000/85%|75%/5",
]


class FakeLineEdit:
    def __init__(self):
        self.value = None

    def setText(self, text):
        self.value = text


class FakeCombo:
    def __init__(self, text=""):
        self._text = text

    def currentText(self):
        return self._text


class FakeConfigManager:
    def __init__(self, rules):
        self._rules = rules

    def get_config(self, key):
        if key == "BatteryConfig/Rules":
            return self._rules
        return None


def make_mixin(spec="CP224642A", method="1S1P", construction="Spiral Type", rules=None,
               temperature="Room Temperature"):
    mixin = ValidationSpecRulesMixin()
    mixin.main_window = SimpleNamespace(
        lineEdit_DatasheetNominalCapacity=FakeLineEdit(),
        lineEdit_CalculationNominalCapacity=FakeLineEdit(),
        lineEdit_RequiredUseableCapacity=FakeLineEdit(),
        comboBox_Specification_Type=FakeCombo(spec),
        comboBox_Specification_Method=FakeCombo(method),
        comboBox_ConstructionMethod=FakeCombo(construction),
        comboBox_Temperature=FakeCombo(temperature),
        config_manager=FakeConfigManager(RULES if rules is None else rules),
    )
    return mixin


class TestApplySpecificationRules:
    def test_dual_percent_spiral(self):
        mixin = make_mixin(construction="Spiral Type")
        mixin._apply_specification_rules()
        mw = mixin.main_window
        assert mw.lineEdit_DatasheetNominalCapacity.value == "920"
        assert mw.lineEdit_CalculationNominalCapacity.value == "920"
        assert mw.lineEdit_RequiredUseableCapacity.value == "782"  # 920 × 85%

    def test_dual_percent_laminate(self):
        mixin = make_mixin(construction="Laminate Type")
        mixin._apply_specification_rules()
        assert mixin.main_window.lineEdit_RequiredUseableCapacity.value == "690"  # 920 × 75%

    def test_absolute_value_rule(self):
        mixin = make_mixin(spec="CF583083")
        mixin._apply_specification_rules()
        mw = mixin.main_window
        assert mw.lineEdit_RequiredUseableCapacity.value == "3000"
        assert mw.lineEdit_CalculationNominalCapacity.value == "4000"

    def test_coin_rule_unchanged(self):
        mixin = make_mixin(spec="CR2450", construction="")
        mixin._apply_specification_rules()
        mw = mixin.main_window
        assert mw.lineEdit_DatasheetNominalCapacity.value == "600"
        assert mw.lineEdit_RequiredUseableCapacity.value == "380"

    @pytest.mark.parametrize("reverse", [False, True])
    @pytest.mark.parametrize("temperature, required", [
        ("Freezer Temperature", "280"), ("Room Temperature", "380"),
    ])
    def test_same_model_rules_follow_ndax_temperature(self, reverse, temperature, required):
        rules = ["CR2450/1S1P/600/550/380/1.0", "CR2450/1S1P/600/550/280/1.0"]
        mixin = make_mixin(spec="CR2450", rules=rules[::-1] if reverse else rules,
                           temperature=temperature)
        mixin._apply_specification_rules()
        assert mixin.main_window.lineEdit_RequiredUseableCapacity.value == required

    def test_missing_freezer_rule_does_not_reuse_room_capacity(self):
        mixin = make_mixin(spec="CR2450", temperature="Freezer Temperature")
        mixin.main_window.lineEdit_RequiredUseableCapacity.setText("380")
        mixin._apply_specification_rules()
        assert mixin.main_window.lineEdit_RequiredUseableCapacity.value == ""

    def test_matching_method_is_not_hidden_by_first_rule(self):
        mixin = make_mixin(spec="CR2450", method="1S2P", temperature="Freezer Temperature",
                           rules=["CR2450/1S1P/600/550/280/1.0",
                                  "CR2450/1S2P/1200/1100/280/1.0"])
        mixin._apply_specification_rules()
        assert mixin.main_window.lineEdit_CalculationNominalCapacity.value == "1100"
        assert mixin.main_window.lineEdit_RequiredUseableCapacity.value == "280"

    def test_exact_model_is_not_hidden_by_shorter_prefix(self):
        mixin = make_mixin(spec="CR2450D", temperature="Freezer Temperature",
                           rules=["CR2450/1S1P/600/550/380/1.0",
                                  "CR2450D/1S1P/600/550/280/1.0"])
        mixin._apply_specification_rules()
        assert mixin.main_window.lineEdit_RequiredUseableCapacity.value == "280"

    def test_method_mismatch_clears_fields(self):
        mixin = make_mixin(method="2S1P")
        mixin._apply_specification_rules()
        mw = mixin.main_window
        assert mw.lineEdit_DatasheetNominalCapacity.value == ""
        assert mw.lineEdit_RequiredUseableCapacity.value == ""

    def test_no_spec_noop(self):
        mixin = make_mixin(spec="")
        mixin._apply_specification_rules()  # 不抛异常即可
        assert mixin.main_window.lineEdit_RequiredUseableCapacity.value is None

    def test_legacy_single_percent_still_supported(self):
        # 旧格式 "80%" 单百分比规则继续可用（未迁移的用户配置）
        mixin = make_mixin(
            spec="OLDMODEL",
            construction="Spiral Type",
            rules=["OLDMODEL/1S1P/920/920/80%/5.0"],
        )
        mixin._apply_specification_rules()
        assert mixin.main_window.lineEdit_RequiredUseableCapacity.value == "736"


class TestCheckConstruction:
    def test_recompute_on_construction_change(self):
        mixin = make_mixin(construction="Spiral Type")
        mixin._apply_specification_rules()
        assert mixin.main_window.lineEdit_RequiredUseableCapacity.value == "782"
        # 切换构造方法 → check_construction 重算（782 → 690）
        mixin.main_window.comboBox_ConstructionMethod._text = "Laminate Type"
        mixin.check_construction()
        assert mixin.main_window.lineEdit_RequiredUseableCapacity.value == "690"

    def test_check_construction_does_not_touch_temperature(self):
        # main_window 无 temperature_handler：若触碰会 AttributeError
        mixin = make_mixin(construction="Spiral Type")
        mixin.check_construction()
        assert mixin.main_window.lineEdit_RequiredUseableCapacity.value == "782"
