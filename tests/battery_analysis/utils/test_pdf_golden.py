"""PDF golden fixtures 断言测试（P5）

把 `tests/fixtures/pdf_golden.py` 中从 PDF 转录的事实源值，逐条对到实现输出：
  - lookup_pulse_currents 的分档/边界/override/Coin 三态
  - build_expectations 的判定格（电流/截止电压/阈值）
  - 截止电压常量、构造比例、§6.2.11 双条件语义
  - 端到端：统计 → 报告 Pass/Fail（对齐 PDF 双条件）

原则：golden 值必须来自 PDF，测试断言实现 == golden，从而让实现侧漂移可被捕获。
"""

import pytest

from battery_analysis.utils.pulse_currents import (
    COIN_FREEZER_SINGLE_PULSE_CURRENTS,
    COIN_STANDARD_PULSE_CURRENTS,
    lookup_pulse_currents,
    required_useable_capacity_from_rule,
)
from battery_analysis.utils.quality_requirements import (
    PDF_CUTOFF_VOLTAGES,
    PDF_HERMES_CUTOFF_VOLTAGES,
    build_expectations,
    evaluate_expectations,
)
from battery_analysis.utils.report_coordinator import compute_report_content_base
from battery_analysis.utils.writers.statistics_utils import (
    compute_list_cpt,
    compute_statistics,
)
from tests.fixtures.pdf_golden import (
    GOLDEN_COIN,
    GOLDEN_CONSTRUCTION_RATIO,
    GOLDEN_CONSTRUCTION_RATIO_ZH,
    GOLDEN_CUTOFF_VOLTAGES,
    GOLDEN_DUAL_CONDITION,
    GOLDEN_HERMES_CUTOFF_VOLTAGES,
    GOLDEN_HERMES_EXPECTATIONS,
    GOLDEN_HERMES_PULSE_CURRENTS,
    GOLDEN_HERMES_SPEC_KEYWORD,
    GOLDEN_JUDGMENT_CURRENT,
    GOLDEN_POUCH_BAND_PROBES,
    GOLDEN_POUCH_BANDS,
    GOLDEN_POUCH_LARGE_BAND,
    GOLDEN_RULE_PERCENT_SAMPLES,
)

# ── helpers（与 e2e test_new_model_analysis 同口径的 19 位 TestInfo）──


def make_test_info(spec, construction, method, qnom, required, currents, voltages):
    return [
        "Pouch Cell" if construction else "Coin Cell",
        construction,
        spec,
        method,
        "Ewin",
        "DC2401",
        "3",
        "25",
        str(qnom),
        str(qnom),
        "0",
        "Lab-A",
        "Tester",
        "/path/to/test.profile",
        ",".join(str(c) for c in currents),
        ",".join(str(v) for v in voltages),
        "2026-01-01",
        str(required),
        "OK",
    ]


def make_charge(target_values, currents, voltages):
    n = len(currents) * len(voltages)
    return [[1500.0] * n for _ in range(3)]


class TestPouchBandsMatchPdf:
    """§7.1.1.3–.10 脉冲电流分档与边界（golden 来自 PDF Pause Period 表）"""

    # 各档下界（QNOM 恰好落在下界时应进入本档，即"下限含"）
    _BAND_LOWER_BOUNDS = (
        (1, (30, 26, 15, 6)),  # §7.1.1.3/.4  QNOM < 1200
        (1200, (60, 30, 15, 6)),  # §7.1.1.5/.6  1200 ≤ QNOM < 2000
        (2000, (100, 60, 30, 15, 6)),  # §7.1.1.7/.8  2000 ≤ QNOM < 3000
        (3000, GOLDEN_POUCH_LARGE_BAND),  # §7.1.1.9/.10 QNOM ≥ 3000
    )

    @pytest.mark.parametrize("lower_bound,expected", _BAND_LOWER_BOUNDS)
    def test_band_lower_bound_is_inclusive(self, lower_bound, expected):
        """下限含：QNOM 恰好等于本档下界时进入本档"""
        assert tuple(lookup_pulse_currents("CPTEST", lower_bound)) == expected

    @pytest.mark.parametrize("capacity,expected", GOLDEN_POUCH_BAND_PROBES)
    def test_band_boundaries(self, capacity, expected):
        """边界开闭：1199→第一档、1200→第二档、2000→第三档、3000→大档"""
        assert tuple(lookup_pulse_currents("CPTEST", capacity)) == expected

    def test_large_band_exact(self):
        assert tuple(lookup_pulse_currents("CPTEST", 3000)) == GOLDEN_POUCH_LARGE_BAND

    def test_bands_transcribed_constant_order(self):
        # golden 表本身自洽（顺序即查找顺序）
        assert [b[0] for b in GOLDEN_POUCH_BANDS] == [1200, 2000, 3000]

    @pytest.mark.parametrize("upper_limit,currents", GOLDEN_POUCH_BANDS)
    def test_lookup_matches_golden_band(self, upper_limit, currents):
        # 档内探针：取 [lower, upper) 中点，稳落在本档
        lower = {1200: 1, 2000: 1200, 3000: 2000}[upper_limit]
        probe = (upper_limit + lower) // 2
        assert tuple(lookup_pulse_currents("CPTEST", probe)) == currents


class TestCoinMatchPdf:
    """§7.1.1.1/.2 Coin 三态（脉冲档 + 判定电流 + 阈值）"""

    def test_room_currents(self):
        assert tuple(COIN_STANDARD_PULSE_CURRENTS) == GOLDEN_COIN["room"]["currents"]

    def test_freezer_single_currents(self):
        assert (
            tuple(COIN_FREEZER_SINGLE_PULSE_CURRENTS)
            == GOLDEN_COIN["freezer_single"]["currents"]
        )

    def test_freezer_1s2p_uses_standard_currents(self):
        assert (
            tuple(lookup_pulse_currents("CR2450", 600, "1S2P", is_freezer=True))
            == GOLDEN_COIN["freezer_1s2p"]["currents"]
        )

    def test_room_expectation(self):
        ti = make_test_info(
            "CR2450", "", "1S1P", 600, 380,
            GOLDEN_COIN["room"]["currents"], GOLDEN_CUTOFF_VOLTAGES,
        )
        exps = build_expectations(ti)
        assert len(exps) == 1
        e = exps[0]
        assert e.cutoff_v == 2.25
        assert e.threshold_mah == float(GOLDEN_COIN["room"]["threshold_mah"])
        assert e.current_ma == GOLDEN_COIN["room"]["judgment_current_ma"]

    def test_freezer_single_expectation(self):
        ti = make_test_info(
            "CR2450", "", "1S1P", 600, 280,
            GOLDEN_COIN["freezer_single"]["currents"], GOLDEN_CUTOFF_VOLTAGES,
        )
        ti[7] = "Freezer Temperature:-20"  # 温度字段命中 is_freezer_context
        exps = build_expectations(ti)
        assert len(exps) == 1
        e = exps[0]
        assert e.threshold_mah == float(GOLDEN_COIN["freezer_single"]["threshold_mah"])
        assert e.current_ma == GOLDEN_COIN["freezer_single"]["judgment_current_ma"]

    def test_freezer_1s2p_expectation(self):
        ti = make_test_info(
            "CR2450", "", "1S2P", 600, 280,
            GOLDEN_COIN["freezer_1s2p"]["currents"], GOLDEN_CUTOFF_VOLTAGES,
        )
        ti[7] = "Freezer Temperature:-20"
        exps = build_expectations(ti)
        assert len(exps) == 1
        e = exps[0]
        assert e.threshold_mah == float(GOLDEN_COIN["freezer_1s2p"]["threshold_mah"])
        # 1S2P 冷冻仍走 30mA（PDF: >280mAh to 2.25V at 30mA for 1S2P pack）
        assert e.current_ma == GOLDEN_COIN["freezer_1s2p"]["judgment_current_ma"]


class TestHermesMatchPdf:
    """§7.1.1.11 CP583083 Hermes 4 判定格 + 5 脉冲档"""

    @pytest.mark.parametrize("spec", ["CP583083", "CF583083", "cp583083"])
    def test_pulse_override(self, spec):
        assert tuple(lookup_pulse_currents(spec, 4000)) == GOLDEN_HERMES_PULSE_CURRENTS

    @pytest.mark.parametrize("spec", ["CP583083", "CF583083"])
    def test_four_expectation_cells(self, spec):
        ti = make_test_info(spec, "Spiral Type", "1S1P", 4000, 3000, [500], [2.5, 2.25])
        exps = build_expectations(ti)
        assert len(exps) == len(GOLDEN_HERMES_EXPECTATIONS)
        for e, (cutoff, current, threshold) in zip(exps, GOLDEN_HERMES_EXPECTATIONS):
            assert e.cutoff_v == cutoff
            assert e.current_ma == float(current)
            assert e.threshold_mah == float(threshold)

    def test_keyword_is_substring_match(self):
        # 实现按 "583083" 子串匹配（PDF 型号 CP583083）
        assert GOLDEN_HERMES_SPEC_KEYWORD in "CP583083"

    def test_hermes_cutoff_voltage_table(self):
        assert tuple(PDF_HERMES_CUTOFF_VOLTAGES) == GOLDEN_HERMES_CUTOFF_VOLTAGES


class TestConstructionRatioMatchPdf:
    """§7.1.1.3–.10 螺旋 85% / 叠片 75%"""

    @pytest.mark.parametrize("keyword,expected", sorted(GOLDEN_CONSTRUCTION_RATIO.items()))
    def test_english_keywords(self, keyword, expected):
        ti = make_test_info(
            "XYZ1430", f"{keyword.title()} Type", "1S1P", 1500, 1275, [60, 30, 15, 6],
            GOLDEN_CUTOFF_VOLTAGES,
        )
        exps = build_expectations(ti)
        assert len(exps) == 1
        assert exps[0].threshold_mah == round(1500 * expected)

    @pytest.mark.parametrize("keyword,expected", sorted(GOLDEN_CONSTRUCTION_RATIO_ZH.items()))
    def test_chinese_keywords(self, keyword, expected):
        # P4：中文构造关键词（叠片/螺旋）也能命中
        ti = make_test_info(
            "XYZ1430", keyword, "1S1P", 1500, 1275, [60, 30, 15, 6],
            GOLDEN_CUTOFF_VOLTAGES,
        )
        exps = build_expectations(ti)
        assert len(exps) == 1
        assert exps[0].threshold_mah == round(1500 * expected)

    def test_judgment_current_is_highest_in_band(self):
        """§6.2.11: highest specified pulse current value should be used"""
        assert GOLDEN_JUDGMENT_CURRENT == "highest_in_band"
        ti = make_test_info(
            "XYZ1430", "Spiral Type", "1S1P", 1500, 1275, [60, 30, 15, 6],
            GOLDEN_CUTOFF_VOLTAGES,
        )
        exps = build_expectations(ti)
        assert exps[0].current_ma == 60.0  # 1200-2000 档最高档


class TestCutoffVoltageTables:
    def test_standard_cutoffs(self):
        assert tuple(PDF_CUTOFF_VOLTAGES) == GOLDEN_CUTOFF_VOLTAGES

    def test_hermes_cutoffs(self):
        assert tuple(PDF_HERMES_CUTOFF_VOLTAGES) == GOLDEN_HERMES_CUTOFF_VOLTAGES


class TestRulePercentConversion:
    @pytest.mark.parametrize("rule,construction,expected", GOLDEN_RULE_PERCENT_SAMPLES)
    def test_dual_percent_and_absolute(self, rule, construction, expected):
        got = required_useable_capacity_from_rule(rule, construction)
        if expected == 0:
            # 绝对值规则（无 % 时返回绝对值本身，非 0）
            assert got == 380
        else:
            assert got == round(1500 * expected / 100)


class TestDualConditionEndToEnd:
    """§6.2.11 双条件端到端（golden：sample ≥ 期望 且 µ-2σ > 期望）"""

    VOLTAGES = [2.4, 2.3, 2.25, 2.2, 2.0, 1.8]
    CURRENTS = [60, 30, 15, 6]

    def _run(self, charge, qnom=1500, required=1275):
        ti = make_test_info(
            "XYZ1430", "Spiral Type", "1S1P", qnom, required,
            self.CURRENTS, self.VOLTAGES,
        )
        cpt = compute_list_cpt(charge, 3, len(self.CURRENTS), len(self.VOLTAGES))
        stats = compute_statistics(cpt, len(self.CURRENTS), len(self.VOLTAGES))
        battery_info = [
            charge,
            ["BAT-001", "BAT-002", "BAT-003"],
            ["2024-01-15 10:00:00", "2024-01-15 14:30:00"],
        ]
        return compute_report_content_base(
            self.CURRENTS,
            len(self.CURRENTS),
            self.VOLTAGES,
            len(self.VOLTAGES),
            ti,
            battery_info,
            "/tmp/in.xlsx",
            "/tmp/out.xlsx",
            "/tmp/report.docx",
            stats,
        )

    def test_dual_condition_pass(self):
        # 全样本 1300 ≥ 1275 且 µ-2σ = 1300 > 1275
        charge = [[1300.0] * (len(self.CURRENTS) * len(self.VOLTAGES))] * 3
        out = self._run(charge)
        assert out["strResult"] == "Pass"
        assert GOLDEN_DUAL_CONDITION["sample_cmp"] == ">="
        assert GOLDEN_DUAL_CONDITION["mu2sigma_cmp"] == ">"

    def test_dual_condition_fail_single_sample(self):
        # min = 1200 < 1275 → 违反条件①
        charge = [[1500.0] * (len(self.CURRENTS) * len(self.VOLTAGES))] * 2 + [
            [1200.0] * (len(self.CURRENTS) * len(self.VOLTAGES))
        ]
        out = self._run(charge)
        assert out["strResult"] == "Fail"
        assert "The minimum sample capacity should be at least 1275mAh" in out["strRemarks"]

    def test_dual_condition_fail_mu2sigma(self):
        # µ-2σ < 期望但 min ≥ 期望 → 违反条件②
        cfg = [1500.0, 1400.0, 1290.0]
        charge = [[v] * (len(self.CURRENTS) * len(self.VOLTAGES)) for v in cfg]
        cpt = compute_list_cpt(charge, 3, len(self.CURRENTS), len(self.VOLTAGES))
        stats = compute_statistics(cpt, len(self.CURRENTS), len(self.VOLTAGES))
        ti = make_test_info(
            "XYZ1430", "Spiral Type", "1S1P", 1500, 1275,
            self.CURRENTS, self.VOLTAGES,
        )
        battery_info = [
            charge,
            ["BAT-001", "BAT-002", "BAT-003"],
            ["2024-01-15 10:00:00", "2024-01-15 14:30:00"],
        ]
        out = compute_report_content_base(
            self.CURRENTS,
            len(self.CURRENTS),
            self.VOLTAGES,
            len(self.VOLTAGES),
            ti,
            battery_info,
            "/tmp/in.xlsx",
            "/tmp/out.xlsx",
            "/tmp/report.docx",
            stats,
        )
        assert out["strResult"] == "Fail"
        assert "The expected usable Q(stat) should be more than 85%" in out["strRemarks"]
