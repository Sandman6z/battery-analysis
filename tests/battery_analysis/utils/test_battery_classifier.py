"""测试电池分类工具"""

import pytest
from battery_analysis.utils.battery_classifier import (
    classify_spec,
    extract_spec_name,
    extract_capacity,
    derive_specifications,
    DEFAULT_CAPACITY_THRESHOLD,
)


class TestClassifySpec:
    def test_cr_prefix_is_coin_cell(self):
        assert classify_spec("CR2450", 600) == "Coin Cell"

    def test_cr_without_capacity_is_coin_cell(self):
        assert classify_spec("CR2450") == "Coin Cell"

    def test_cp_prefix_is_pouch_cell(self):
        assert classify_spec("CP224642A", 920) == "Pouch Cell"

    def test_cf_prefix_is_pouch_cell(self):
        assert classify_spec("CF583083", 4000) == "Pouch Cell"

    def test_lower_case_input(self):
        assert classify_spec("cr2450", 600) == "Coin Cell"
        assert classify_spec("cp305050", 2000) == "Pouch Cell"

    def test_fallback_by_capacity_above_threshold(self):
        name = "XYZ9999"
        assert classify_spec(name, DEFAULT_CAPACITY_THRESHOLD + 1) == "Pouch Cell"

    def test_fallback_by_capacity_below_threshold(self):
        name = "XYZ100"
        assert classify_spec(name, DEFAULT_CAPACITY_THRESHOLD - 1) == "Coin Cell"

    def test_fallback_zero_capacity_coin(self):
        assert classify_spec("UNKNOWN", 0) == "Coin Cell"


class TestExtractSpecName:
    def test_first_part_of_rule(self):
        assert extract_spec_name("CR2450/1S1P/600/550/380/1.0") == "CR2450"

    def test_empty_string(self):
        assert extract_spec_name("") == ""

    def test_single_part(self):
        assert extract_spec_name("CR2450") == "CR2450"


class TestExtractCapacity:
    def test_third_part_of_rule(self):
        assert extract_capacity("CR2450/1S1P/600/550/380/1.0") == 600

    def test_not_a_number(self):
        assert extract_capacity("CR2450/1S1P/abc/550/380/1.0") == 0

    def test_too_few_parts(self):
        assert extract_capacity("CR2450/1S1P") == 0


class TestDeriveSpecifications:
    def test_mixed_rules(self):
        rules = [
            "CR2450/1S1P/600/550/380/1.0",
            "CR2450D/1S1P/600/550/280/1.0",
            "CP224642A/1S1P/920/920/80%/5.0",
            "CF583083/1S1P/4000/4000/80%/5.0",
            "CP305050/1S1P/2000/2000/80%/1.0",
        ]
        result = derive_specifications(rules)
        assert "CR2450" in result["Coin Cell"]
        assert "CR2450D" in result["Coin Cell"]
        assert "CP224642A" in result["Pouch Cell"]
        assert "CF583083" in result["Pouch Cell"]
        assert "CP305050" in result["Pouch Cell"]

    def test_duplicate_specs_are_deduplicated(self):
        rules = [
            "CR2450/1S1P/600/550/380/1.0",
            "CR2450/1S2P/600/550/380/1.0",
        ]
        result = derive_specifications(rules)
        assert result["Coin Cell"].count("CR2450") == 1

    def test_empty_rules(self):
        assert derive_specifications([]) == {"Coin Cell": [], "Pouch Cell": []}
