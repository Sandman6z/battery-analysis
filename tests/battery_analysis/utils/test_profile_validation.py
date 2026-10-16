"""profile_validation 决策树纯函数测试（会议裁决①③④）。"""

from battery_analysis.utils.profile_validation import (
    COMPLETENESS_COMPLETE,
    COMPLETENESS_MISSING,
    COMPLETENESS_TRUNCATED,
    DECISION_BLOCK,
    DECISION_OFFER_OVERRIDE,
    DECISION_PROCEED,
    POLICY_VERSION,
    check_batch_consistency,
    check_step_completeness,
    decide_profile_validation,
    extract_profile_levels,
)

PROFILE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<config type="Step File" version="17" date="20250610100145">
  <Head_Info>
    <PN Value="CR2450"/>
    <Remark Value="CR2450 QA Test (30-26-15-6mA, CC 10mAh 1mA)"/>
  </Head_Info>
  <Step_Info Num="6">
    <Step4 Step_ID="4" Step_Type="16">
      <PulseData Pulse_Mode="1" Cycle_Count="10" Count="8">
        <Pulse1 Value="0" Time="59000"/>
        <Pulse2 Value="-30" Time="1000"/>
        <Pulse3 Value="0" Time="59000"/>
        <Pulse4 Value="-26" Time="1000"/>
        <Pulse5 Value="0" Time="58000"/>
        <Pulse6 Value="-15" Time="2000"/>
        <Pulse7 Value="0" Time="55000"/>
        <Pulse8 Value="-6" Time="5000"/>
      </PulseData>
    </Step4>
  </Step_Info>
</config>
"""


class TestExtractProfileLevels:
    def test_extracts_positive_deduped_pulses(self, tmp_path):
        profile = tmp_path / "profile.xml"
        profile.write_text(PROFILE_XML, encoding="utf-8")
        assert extract_profile_levels(profile) == [30.0, 26.0, 15.0, 6.0]

    def test_missing_file_returns_none(self, tmp_path):
        assert extract_profile_levels(tmp_path / "nope.xml") is None

    def test_unparsable_returns_none(self, tmp_path):
        profile = tmp_path / "profile.xml"
        profile.write_bytes(b"\xff\xfe not xml at all")
        assert extract_profile_levels(profile) is None

    def test_no_pulses_returns_none(self, tmp_path):
        profile = tmp_path / "profile.xml"
        profile.write_text("<config><Step_Info/></config>", encoding="utf-8")
        assert extract_profile_levels(profile) is None


class TestCheckStepCompleteness:
    def test_complete(self):
        assert check_step_completeness([30, 15, 6], [30, 15, 6]) == COMPLETENESS_COMPLETE

    def test_truncated_when_level_missing(self):
        assert check_step_completeness([30, 15, 6], [30, 15]) == COMPLETENESS_TRUNCATED

    def test_truncated_when_observed_empty(self):
        assert check_step_completeness([30, 15, 6], []) == COMPLETENESS_TRUNCATED

    def test_missing_when_observed_none(self):
        assert check_step_completeness([30, 15, 6], None) == COMPLETENESS_MISSING

    def test_missing_when_no_declared(self):
        assert check_step_completeness([], [30]) == COMPLETENESS_MISSING

    def test_tolerance_within_one_percent(self):
        # 30.2 与 30 差 0.2 < max(0.3, 0.5) 容差 → 已执行
        assert check_step_completeness([30], [30.2]) == COMPLETENESS_COMPLETE


class TestDecideProfileValidation:
    def test_match_proceeds(self):
        record = decide_profile_validation([30, 26], [30, 26], [30, 26])
        assert record["result"] == "match"
        assert record["decision"] == DECISION_PROCEED
        assert record["policy_version"] == POLICY_VERSION

    def test_value_mismatch_offers_override(self):
        # 裁决①：同 4 档不同值 → offer_override
        record = decide_profile_validation([30, 26, 15, 6], [60, 30, 15, 6], None)
        assert record["result"] == "value_mismatch"
        assert record["mismatch_type"] == "value_mismatch"
        assert record["decision"] == DECISION_OFFER_OVERRIDE

    def test_ndax_more_levels_offers_override_directly(self):
        # 裁决④：ndax > profile → 不查工步，直接给按钮
        record = decide_profile_validation([30, 26, 15], [60, 30, 15, 6], None)
        assert record["mismatch_type"] == "level_count_mismatch_excess"
        assert record["decision"] == DECISION_OFFER_OVERRIDE

    def test_ndax_fewer_levels_complete_offers_override(self):
        # ndax < profile 且 ndax 自声明工步全实测 → 按钮 + 留痕
        record = decide_profile_validation([30, 26, 15, 6], [30, 15, 6], [30, 15, 6])
        assert record["mismatch_type"] == "level_count_mismatch_complete"
        assert record["decision"] == DECISION_OFFER_OVERRIDE

    def test_ndax_fewer_levels_truncated_blocks(self):
        # ndax < profile 且声明工步未全执行 → 硬阻断
        record = decide_profile_validation([30, 26, 15, 6], [30, 15, 6], [30, 15])
        assert record["mismatch_type"] == "level_count_mismatch_truncated"
        assert record["decision"] == DECISION_BLOCK

    def test_missing_evidence_blocks(self):
        # 旧 sidecar 无 observed → 从严硬阻断
        record = decide_profile_validation([30, 26, 15, 6], [30, 15, 6], None)
        assert record["mismatch_type"] == "level_count_missing_evidence"
        assert record["decision"] == DECISION_BLOCK

    def test_empty_side_is_no_evidence_proceed(self):
        record = decide_profile_validation([30, 26], None, None)
        assert record["result"] == "no_evidence"
        assert record["decision"] == DECISION_PROCEED


class TestCheckBatchConsistency:
    def test_inconsistent_blocks(self):
        record = check_batch_consistency({"a.xlsx": [30, 26], "b.xlsx": [30, 6]})
        assert record is not None
        assert record["result"] == "batch_inconsistent"
        assert record["decision"] == DECISION_BLOCK

    def test_consistent_returns_none(self):
        assert check_batch_consistency({"a": [30, 26], "b": [30, 26]}) is None

    def test_single_sample_returns_none(self):
        assert check_batch_consistency({"a": [30, 26]}) is None

    def test_order_insensitive(self):
        # 档位顺序差异不算不一致（集合语义）
        assert check_batch_consistency({"a": [30, 15], "b": [15, 30]}) is None


class TestMeasuredDrift:
    """裁决②：实测中位数偏差 > max(1%, 0.5mA) → 黄警放行留痕。"""

    def test_drift_recorded_on_match(self):
        record = decide_profile_validation(
            [30, 26, 15, 6],
            [30, 26, 15, 6],
            [30, 26, 15, 6],
            medians={"30.0": 30.8, "26.0": 26.1, "15.0": 15.3, "6.0": 6.2},
        )
        # 30 偏 0.8 > 0.5；26 偏 0.1 < 0.52；15 偏 0.3 < 0.5；6 偏 0.2 < 0.5
        assert record["result"] == "match"
        assert record["decision"] == DECISION_PROCEED
        assert record["measured_drift"] == {"30": 0.8}

    def test_no_drift_within_tolerance(self):
        record = decide_profile_validation(
            [30, 26], [30, 26], [30, 26], medians={"30.0": 30.4, "26.0": 25.5}
        )
        # 30 偏 0.4 < 0.5；26 偏 0.5 不大于 0.5（严格大于才告警）
        assert "measured_drift" not in record

    def test_missing_medians_key_ok(self):
        record = decide_profile_validation([30], [30], [30])
        assert "measured_drift" not in record
        assert record["decision"] == DECISION_PROCEED

    def test_drift_survives_value_mismatch_path(self):
        record = decide_profile_validation(
            [30, 26], [60, 30], [60, 30], medians={"60.0": 61.2}
        )
        assert record["decision"] == DECISION_OFFER_OVERRIDE
        assert record["measured_drift"] == {"60": 1.2}

    def test_invalid_median_entries_ignored(self):
        record = decide_profile_validation(
            [30], [30], [30], medians={"bad": "worse", "30.0": "nan-ish"}
        )
        # 无法转 float 的项被忽略（ValueError/TypeError 路径）；"nan-ish" 转不成
        assert "measured_drift" not in record
