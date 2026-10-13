"""compute_report_content_base 的 §6.2.11 合格判定测试

验证 Excel/Word 共享的 Pass/Fail 结论与 Remarks：
- PDF 期望格判定（单样本 ≥ 期望 且 µ-2σ > 期望）
- 期望格派生失败时回退到历史单点（最高电流 × 2.25V）
- 期望格不在实测档位时回退原有单点逻辑（安全网）
"""

import pytest

from battery_analysis.utils.report_coordinator import compute_report_content_base

VOLTAGES = [2.6, 2.5, 2.4, 2.3, 2.25, 2.2, 2.1, 2.0, 1.8]
V225_IDX = VOLTAGES.index(2.25)  # 4
V250_IDX = VOLTAGES.index(2.5)  # 1


def make_test_info(
    construction="Spiral Type",
    spec="CP224642A",
    method="1S1P",
    qnom=920,
    required=782,
):
    items = [""] * 19
    items[1] = construction
    items[2] = spec
    items[3] = method
    items[5] = "B01"
    items[9] = str(qnom)
    items[13] = "C:/data/profile.xml"
    items[17] = str(required)
    return items


def make_stats(num_current, num_voltage):
    keys = ("mean", "med", "std", "mm3s", "mm2s", "mp2s", "mp3s", "min", "max")
    return {key: [[0.0] * num_voltage for _ in range(num_current)] for key in keys}


def run(test_info, stats, currents=(30, 26, 15, 6), voltages=None):
    voltages = VOLTAGES if voltages is None else voltages
    return compute_report_content_base(
        list(currents),
        len(currents),
        list(voltages),
        len(voltages),
        test_info,
        ["", "", ["2026-01-01 00:00:00", "2026-01-02 00:00:00"]],
        "C:/data/sample.xlsx",
        "C:/data/result.xlsx",
        "C:/data/report.docx",
        stats,
    )


class TestPouchVerdict:
    def test_pass(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 790
        result = run(make_test_info(), stats)
        assert result["strResult"] == "Pass"
        assert result["strRemarks"] == "OK"
        # 展示用百分比 = required / QNOM（85%）
        assert result["strRequiredUseableCapacityPercentage"] == "85%"

    def test_fail_on_single_sample(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 780  # < 782
        stats["mm2s"][0][V225_IDX] = 790
        result = run(make_test_info(), stats)
        assert result["strResult"] == "Fail"
        assert "no single sample" in result["strRemarks"]
        assert "782" in result["strRemarks"]

    def test_fail_on_mu_minus_2sigma(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 700  # ≤ 782
        result = run(make_test_info(), stats)
        assert result["strResult"] == "Fail"
        assert "μ-2σ" in result["strRemarks"]

    def test_laminate_threshold_75_percent(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 700
        stats["mm2s"][0][V225_IDX] = 695
        result = run(make_test_info(construction="Laminate Type"), stats)
        # 叠片 920 × 75% = 690 → 695 > 690 且 700 ≥ 690 → Pass
        assert result["strResult"] == "Pass"


class TestHermesVerdict:
    """§7.1.1.11：多格判定（2.25V 与 2.5V、500mA 与 100mA）"""

    def run_hermes(self, stats):
        return run(
            make_test_info(spec="CF583083", qnom=4000, required=3000),
            stats,
            currents=(500, 250, 100, 50, 25),
        )

    def test_all_cells_pass(self):
        stats = make_stats(5, 9)
        for c in (0, 2):  # 500mA / 100mA
            for v in (V225_IDX, V250_IDX):
                stats["min"][c][v] = 4000
                stats["mm2s"][c][v] = 3900
        result = self.run_hermes(stats)
        assert result["strResult"] == "Pass"
        assert result["strRemarks"] == "OK"

    def test_single_failing_cell_fails_overall(self):
        stats = make_stats(5, 9)
        for c in (0, 2):
            for v in (V225_IDX, V250_IDX):
                stats["min"][c][v] = 4000
                stats["mm2s"][c][v] = 3900
        # 100mA/2.25V 期望 3600 → µ-2σ 3500 不达标
        stats["min"][2][V225_IDX] = 3550
        stats["mm2s"][2][V225_IDX] = 3500
        result = self.run_hermes(stats)
        assert result["strResult"] == "Fail"
        assert "100mA → 2.25V" in result["strRemarks"]
        assert "μ-2σ" in result["strRemarks"]


class TestFallbacks:
    def test_unknown_construction_uses_legacy_cell(self):
        # Pouch 构造未知 → 回退历史判定位置（最高电流 × 2.25V，阈值 = required）
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 790
        result = run(make_test_info(construction=""), stats)
        assert result["strResult"] == "Pass"

    def test_unknown_construction_fail_keeps_pdf_criteria(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 700  # < 782
        result = run(make_test_info(construction=""), stats)
        assert result["strResult"] == "Fail"
        assert "μ-2σ" in result["strRemarks"]

    def test_hermes_expectation_outside_levels_uses_legacy_logic(self):
        # 期望格（500/100mA）不在实测档位 → 期望格全部跳过，
        # 走原有单点逻辑（mm2s[最高电流][2.25V] / QNOM ≥ required / QNOM）
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 800
        result = run(make_test_info(spec="CF583083", qnom=4000, required=3000), stats)
        # 800/4000 = 20% < 75% → 旧逻辑 Fail，备注保持历史英文措辞
        assert result["strResult"] == "Fail"
        assert "The expected usable Q(stat) should be more than 75%" in result["strRemarks"]


class TestCoinVerdict:
    """§7.1.1.1/§7.1.1.2：Coin Cell 期望格回归（标准 30mA/380、冷冻 15mA/280）。"""

    @staticmethod
    def coin_info(spec="CR2450", method="1S1P", qnom=600, required=380):
        return make_test_info(
            construction="", spec=spec, method=method, qnom=qnom, required=required
        )

    def test_standard_room_pass(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 395
        stats["mm2s"][0][V225_IDX] = 390  # > 380
        result = run(self.coin_info(), stats)
        assert result["strResult"] == "Pass"
        assert result["strRemarks"] == "OK"
        assert result["strRequiredUseableCapacityPercentage"] == "63%"

    def test_standard_fail_on_single_sample(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 370  # < 380
        stats["mm2s"][0][V225_IDX] = 390
        result = run(self.coin_info(), stats)
        assert result["strResult"] == "Fail"
        assert "no single sample" in result["strRemarks"]
        assert "380" in result["strRemarks"]

    def test_standard_fail_on_mu_minus_2sigma(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 395
        stats["mm2s"][0][V225_IDX] = 375  # ≤ 380
        result = run(self.coin_info(), stats)
        assert result["strResult"] == "Fail"
        assert "μ-2σ" in result["strRemarks"]

    def test_freezer_single_cell_judged_at_15ma(self):
        # 冷冻单体：15mA 档（levels[0]=15）× 2.25V，阈值 280
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 300
        stats["mm2s"][0][V225_IDX] = 295
        result = run(
            self.coin_info(spec="CR2450D", required=280),
            stats,
            currents=(15, 13, 7.5, 3),
        )
        assert result["strResult"] == "Pass"

    def test_freezer_single_cell_fail_reported_at_15ma(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 270  # < 280
        stats["mm2s"][0][V225_IDX] = 265
        result = run(
            self.coin_info(spec="CR2450D", required=280),
            stats,
            currents=(15, 13, 7.5, 3),
        )
        assert result["strResult"] == "Fail"
        assert "15mA → 2.25V" in result["strRemarks"]

    def test_freezer_1s2p_judged_at_30ma(self):
        # 冷冻 1S2P：PDF §7.1.1.2.5 回到 30mA 标准档，阈值 280
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 300
        stats["mm2s"][0][V225_IDX] = 295
        result = run(self.coin_info(spec="CR2450D", method="1S2P", required=280), stats)
        assert result["strResult"] == "Pass"
        assert result["strRemarks"] == "OK"

    def test_freezer_1s2p_fail_at_30ma(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 275  # < 280
        stats["mm2s"][0][V225_IDX] = 290
        result = run(self.coin_info(spec="CR2450D", method="1S2P", required=280), stats)
        assert result["strResult"] == "Fail"
        assert "30mA → 2.25V" in result["strRemarks"]


class TestValueGuard:
    """空值/零值防护：抛带字段名的 ValueError，供 Report Generation Error 弹窗定位。"""

    def test_empty_required_capacity_raises_field_named_error(self):
        stats = make_stats(4, 9)
        with pytest.raises(ValueError, match="Required Useable Capacity must be a positive"):
            run(make_test_info(required=""), stats)

    def test_empty_calculated_capacity_raises_field_named_error(self):
        stats = make_stats(4, 9)
        with pytest.raises(ValueError, match="Calculated Capacity must be a positive"):
            run(make_test_info(qnom=""), stats)

    def test_zero_calculated_capacity_raises_field_named_error(self):
        stats = make_stats(4, 9)
        with pytest.raises(ValueError, match="Calculated Capacity must be a positive"):
            run(make_test_info(qnom="0"), stats)

    def test_zero_required_capacity_raises_field_named_error(self):
        stats = make_stats(4, 9)
        with pytest.raises(ValueError, match="Required Useable Capacity must be a positive"):
            run(make_test_info(required="0"), stats)


class TestP1VoltageMatch:
    """P1：2.25V 档位容差匹配 + 未命中告警标注"""

    def test_string_voltage_levels_still_match_225(self):
        # 档位为字符串 "2.25" 时旧代码 == 比较失败 → 静默落 index 0（2.6V）
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 800
        stats["min"][0][0] = 0
        stats["mm2s"][0][0] = 0
        voltages = [str(v) for v in VOLTAGES]
        result = run(make_test_info(), stats, voltages=voltages)
        # 容差匹配命中 2.25V（index 4）→ 期望格 min=800 ≥ 782 且 µ-2σ=800 > 782 → Pass
        assert result["strResult"] == "Pass"
        assert "2.25V cutoff level not found" not in result["strRemarks"]

    def test_missing_225_level_appends_note(self):
        voltages = [2.6, 2.5, 2.4, 2.3, 2.2, 2.1]  # 无 2.25V
        stats = make_stats(4, len(voltages))
        stats["min"][0][0] = 800
        stats["mm2s"][0][0] = 800
        result = run(make_test_info(), stats, voltages=voltages)
        assert "2.25V cutoff level not found in voltage table" in result["strRemarks"]


class TestP2LegacyMinCheck:
    """P2：legacy 单点分支补最小值判据 + 标注"""

    def test_legacy_pass_with_min_check_annotated(self):
        # Hermes 期望格不在档位 → legacy 分支；min=800 < 3000 → 补 min 判据后 Fail
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 3200  # 3200/4000 = 80% ≥ 75%（旧逻辑会 Pass）
        result = run(make_test_info(spec="CF583083", qnom=4000, required=3000), stats)
        assert result["strResult"] == "Fail"
        assert "No single sample below expected usable Q 3000mAh" in result["strRemarks"]
        assert "(legacy single-point verdict)" in result["strRemarks"]

    def test_legacy_pass_min_and_stat_ok(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 3100
        stats["mm2s"][0][V225_IDX] = 3200
        result = run(make_test_info(spec="CF583083", qnom=4000, required=3000), stats)
        assert result["strResult"] == "Pass"
        assert result["strRemarks"] == "OK (legacy single-point verdict)"


class TestP3ThreeState:
    """P3：counts 驱动的三态判定（Incomplete 绝不聚合 Pass）"""

    def _stats_with_counts(self, n=4, v=9):
        stats = make_stats(n, v)
        stats["counts"] = [[3] * v for _ in range(n)]
        return stats

    def test_no_data_cell_yields_incomplete_not_pass(self):
        # 期望格 30mA/2.25V 无样本：min/mm2s 为 0 但 counts=0 → Incomplete
        stats = self._stats_with_counts()
        stats["counts"][0][V225_IDX] = 0
        stats["min"][0][V225_IDX] = 0
        stats["mm2s"][0][V225_IDX] = 0
        result = run(make_test_info(), stats)
        assert result["strResult"] == "Incomplete"
        assert "no measured samples at 30mA → 2.25V" in result["strRemarks"]
        assert "retest required" in result["strRemarks"]

    def test_real_failure_dominates_incomplete(self):
        # 有数据的格真失败 + 另一格无数据 → Fail（failed 优先）
        stats = self._stats_with_counts()
        stats["counts"][0][V225_IDX] = 3
        stats["min"][0][V225_IDX] = 100
        stats["mm2s"][0][V225_IDX] = 100
        result = run(make_test_info(), stats)
        assert result["strResult"] == "Fail"

    def test_single_sample_keeps_verdict_with_sigma_note(self):
        # n=1：保留判定但标注 σ=0 退化
        stats = self._stats_with_counts()
        stats["counts"][0][V225_IDX] = 1
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 800
        result = run(make_test_info(), stats)
        assert result["strResult"] == "Pass"
        assert "single sample at 30mA → 2.25V" in result["strRemarks"]
        assert "σ=0" in result["strRemarks"]

    def test_missing_counts_key_behaves_like_old_stats(self):
        # 旧 stats 桩无 counts → sample_count=None，行为与旧版一致
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 800
        result = run(make_test_info(), stats)
        assert result["strResult"] == "Pass"
        assert result["strRemarks"] == "OK"
