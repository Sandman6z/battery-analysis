"""pulse_currents 查表模块测试

依据 BatteryQualityRequirements_v2.3 §7.1.1：
- Coin 标准型 30/26/15/6；Freezer 单体 15/13/7.5/3；Freezer 1S2P 30/26/15/6
- Pouch 容量档：<1200 → 30/26/15/6；1200-2000 → 60/30/15/6；2000-3000 → 100/60/30/15/6；>=3000 → 150/100/60/30/15/6
- CP583083 特例 → 500/250/100/50/25
"""

from battery_analysis.utils.pulse_currents import (
    COIN_FREEZER_SINGLE_PULSE_CURRENTS,
    COIN_STANDARD_PULSE_CURRENTS,
    capacity_from_rules,
    is_freezer_from_rules,
    lookup_pulse_currents,
    normalize_current_levels,
    required_useable_capacity_from_rule,
)

RULES = [
    "CR2450/1S1P/600/550/380/1.0",
    "CR2450D/1S1P/600/550/280/1.0",
    "CR2450HE1/1S1P/600/550/380/1.0",
    "CR2450HE4/1S1P/600/550/280/1.0",
    "CP224642A/1S1P/920/920/80%/5.0",
    "CP305050/1S1P/2000/2000/80%/1.0",
    "CF583083/1S1P/4000/4000/80%/5.0",
]


class TestFreezerFromRules:
    """冷冻型识别：规则「要求可用容量」= 280mAh → 冷冻（temperature_handler 既有约定）"""

    def test_required_capacity_absolute_value(self):
        assert required_useable_capacity_from_rule("CR2450/1S1P/600/550/380/1.0") == 380
        assert required_useable_capacity_from_rule("CR2450D/1S1P/600/550/280/1.0") == 280

    def test_required_capacity_percentage_form(self):
        assert required_useable_capacity_from_rule("CP305050/1S1P/2000/2000/80%/1.0") == 1600

    def test_required_capacity_malformed_returns_none(self):
        assert required_useable_capacity_from_rule("bad") is None
        assert required_useable_capacity_from_rule("a/b/c/d/notanumber/1.0") is None

    def test_freezer_model_without_freezer_in_name(self):
        # CR2450D、CR2450HE4 是冷冻型号但名字不含 freezer，靠 280mAh 规则识别
        assert is_freezer_from_rules(RULES, "CR2450D") is True
        assert is_freezer_from_rules(RULES, "CR2450HE4") is True

    def test_room_temperature_model(self):
        assert is_freezer_from_rules(RULES, "CR2450") is False
        assert is_freezer_from_rules(RULES, "CR2450HE1") is False

    def test_unknown_or_empty_model(self):
        assert is_freezer_from_rules(RULES, "ZZ999") is False
        assert is_freezer_from_rules(RULES, "") is False
        assert is_freezer_from_rules([], "CR2450D") is False
        assert is_freezer_from_rules(None, None) is False

    def test_model_name_freezer_suffix_is_ignored(self):
        # 型号名不可靠（各厂商后缀不同）：名字带 freezer 字样但规则是 380 → 不算冷冻
        rules = ["CR2450FREEZER/1S1P/600/550/380/1.0"]
        assert is_freezer_from_rules(rules, "CR2450FREEZER") is False
        # 反之规则 280 但名字不带 freezer → 算冷冻
        rules_280 = ["CR2450X/1S1P/600/550/280/1.0"]
        assert is_freezer_from_rules(rules_280, "CR2450X") is True


class TestNormalizeCurrentLevels:
    def test_integer_values_become_int(self):
        assert normalize_current_levels([30.0, 26.0, 15.0, 6.0]) == [30, 26, 15, 6]

    def test_fractional_values_are_preserved(self):
        assert normalize_current_levels(["15", "13", "7.5", "3"]) == [15, 13, 7.5, 3]

    def test_unparseable_entries_are_dropped(self):
        assert normalize_current_levels([30, "abc", None, 15]) == [30, 15]

    def test_empty_input(self):
        assert normalize_current_levels([]) == []


class TestCapacityFromRules:
    def test_finds_matching_model(self):
        assert capacity_from_rules(RULES, "CR2450") == 600.0
        assert capacity_from_rules(RULES, "CP305050") == 2000.0

    def test_unknown_model_returns_zero(self):
        assert capacity_from_rules(RULES, "UNKNOWN") == 0.0

    def test_empty_spec_or_rules_returns_zero(self):
        assert capacity_from_rules(RULES, "") == 0.0
        assert capacity_from_rules([], "CR2450") == 0.0
        assert capacity_from_rules(None, "CR2450") == 0.0


class TestLookupPulseCurrents:
    def test_empty_name_returns_empty(self):
        assert lookup_pulse_currents("") == []
        assert lookup_pulse_currents(None) == []

    def test_coin_standard(self):
        assert lookup_pulse_currents("CR2450", 600) == [30, 26, 15, 6]
        assert lookup_pulse_currents("CR2450", 600) == COIN_STANDARD_PULSE_CURRENTS

    def test_coin_freezer_single_cell(self):
        assert lookup_pulse_currents("CR2450", 600, "1S1P", is_freezer=True) == [15, 13, 7.5, 3]
        assert (
            lookup_pulse_currents("CR2450", 600, "1S1P", is_freezer=True)
            == COIN_FREEZER_SINGLE_PULSE_CURRENTS
        )

    def test_coin_freezer_1s2p_uses_standard(self):
        assert lookup_pulse_currents("CR2450", 600, "1S2P", is_freezer=True) == [30, 26, 15, 6]

    def test_pouch_band_below_1200(self):
        assert lookup_pulse_currents("CP224642A", 920) == [30, 26, 15, 6]

    def test_pouch_band_1200_to_2000(self):
        assert lookup_pulse_currents("CP150050", 1200) == [60, 30, 15, 6]
        assert lookup_pulse_currents("CP150050", 1999) == [60, 30, 15, 6]

    def test_pouch_band_2000_to_3000(self):
        assert lookup_pulse_currents("CP305050", 2000) == [100, 60, 30, 15, 6]
        assert lookup_pulse_currents("CP305050", 2999) == [100, 60, 30, 15, 6]

    def test_pouch_band_3000_and_above(self):
        assert lookup_pulse_currents("CP405060", 3000) == [150, 100, 60, 30, 15, 6]
        assert lookup_pulse_currents("CP405060", 5000) == [150, 100, 60, 30, 15, 6]

    def test_pouch_unknown_capacity_returns_empty(self):
        assert lookup_pulse_currents("CP305050", 0) == []
        assert lookup_pulse_currents("CP305050") == []

    def test_model_override_583083(self):
        assert lookup_pulse_currents("CP583083", 4000) == [500, 250, 100, 50, 25]
        assert lookup_pulse_currents("CF583083", 4000) == [500, 250, 100, 50, 25]

    def test_result_is_a_copy(self):
        result = lookup_pulse_currents("CR2450", 600)
        result.append(999)
        assert lookup_pulse_currents("CR2450", 600) == [30, 26, 15, 6]
