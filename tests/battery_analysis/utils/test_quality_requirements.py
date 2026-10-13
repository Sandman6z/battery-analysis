"""quality_requirements 测试

覆盖 BatteryQualityRequirements_v2.3 对齐逻辑：
- build_expectations：§7.1.1 各 profile 的期望可用容量派生
- evaluate_expectations：§6.2.11 合格判定（① 单样本 ≥ 期望 ② µ-2σ > 期望）
- 报表标注与失败说明
"""

from battery_analysis.utils.quality_requirements import (
    PDF_CUTOFF_VOLTAGES,
    PULSE_BURSTS,
    PULSE_STEP_SCHEDULES,
    build_expectations,
    evaluate_expectations,
    expected_requirement_text,
    format_failure_remarks,
    verdict_map,
)

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
    """构造 19 位位置列表（TestInfo.to_list 兼容格式）"""
    items = [""] * 19
    items[1] = construction
    items[2] = spec
    items[3] = method
    items[9] = str(qnom)
    items[17] = str(required)
    return items


def make_stats(num_current, num_voltage):
    """compute_statistics 输出骨架（全 0.0）"""
    keys = ("mean", "med", "std", "mm3s", "mm2s", "mp2s", "mp3s", "min", "max")
    return {key: [[0.0] * num_voltage for _ in range(num_current)] for key in keys}


class TestPdfConstants:
    """PDF 内置参数表的回归钉（数值必须与 PDF 一致，不可漂移）"""

    def test_pulse_bursts_is_10(self):
        assert PULSE_BURSTS == 10

    def test_step_schedules(self):
        # 4 档：1s/1s/2s/5s，暂停 59/59/58/55（§7.1.1.1 等）
        assert PULSE_STEP_SCHEDULES[4] == ((1, 59), (1, 59), (2, 58), (5, 55))
        # 5 档（§7.1.1.7/.11）与 6 档（§7.1.1.9/.10）
        assert len(PULSE_STEP_SCHEDULES[5]) == 5
        assert PULSE_STEP_SCHEDULES[5][-1] == (5, 55)
        assert len(PULSE_STEP_SCHEDULES[6]) == 6
        assert PULSE_STEP_SCHEDULES[6][-1] == (5, 55)

    def test_pdf_cutoff_voltages(self):
        # 标准 6 档（2.6V/2.1V 为配置超集，不在 PDF 内）
        assert PDF_CUTOFF_VOLTAGES == (2.4, 2.3, 2.25, 2.2, 2.0, 1.8)


class TestBuildExpectations:
    def test_pouch_spiral_uses_85_percent(self):
        # §7.1.1.3-.4：CP224642A 920mAh < 1200 → 30mA；螺旋 85% = 782
        expectations = build_expectations(make_test_info())
        assert len(expectations) == 1
        exp = expectations[0]
        assert exp.current_ma == 30
        assert exp.cutoff_v == 2.25
        assert exp.threshold_mah == 782

    def test_pouch_laminate_uses_75_percent(self):
        expectations = build_expectations(make_test_info(construction="Laminate Type"))
        assert expectations[0].threshold_mah == 690  # 920 × 75%
        assert expectations[0].current_ma == 30

    def test_pouch_unknown_construction_returns_empty(self):
        # 构造未知 → 调用方回退历史判定位置
        assert build_expectations(make_test_info(construction="")) == []

    def test_pouch_band_2000_to_3000(self):
        # §7.1.1.7/.8：2000 ≤ QNOM < 3000 → 最高档 100mA；螺旋 85% = 1700
        expectations = build_expectations(make_test_info(spec="CP305050", qnom=2000, required=1700))
        assert expectations[0].current_ma == 100
        assert expectations[0].threshold_mah == 1700

    def test_hermes_has_four_absolute_cells(self):
        # §7.1.1.11 CF583083 "Hermes"：4 个绝对值判定格
        expectations = build_expectations(make_test_info(spec="CF583083", qnom=4000, required=3000))
        assert [(e.current_ma, e.cutoff_v, e.threshold_mah) for e in expectations] == [
            (500, 2.25, 3000),
            (100, 2.25, 3600),
            (500, 2.5, 2600),
            (100, 2.5, 3200),
        ]

    def test_coin_standard_room(self):
        # §7.1.1.1：CR2450 常温 30mA / >380mAh
        expectations = build_expectations(
            make_test_info(
                construction="",
                spec="CR2450",
                qnom=600,
                required=380,
            )
        )
        assert len(expectations) == 1
        assert expectations[0].current_ma == 30
        assert expectations[0].threshold_mah == 380

    def test_coin_freezer_single_cell(self):
        # §7.1.1.2.4：冷冻单体 15mA / >280mAh
        expectations = build_expectations(
            make_test_info(construction="", spec="CR2450D", method="1S1P", qnom=600, required=280)
        )
        assert expectations[0].current_ma == 15
        assert expectations[0].threshold_mah == 280

    def test_coin_freezer_1s2p(self):
        # §7.1.1.2.5：冷冻 1S2P 30mA / >280mAh
        expectations = build_expectations(
            make_test_info(construction="", spec="CR2450D", method="1S2P", qnom=600, required=280)
        )
        assert expectations[0].current_ma == 30

    def test_coin_missing_required_returns_empty(self):
        assert (
            build_expectations(
                make_test_info(construction="", spec="CR2450", qnom=600, required="")
            )
            == []
        )

    def test_empty_spec_returns_empty(self):
        assert build_expectations(make_test_info(spec="")) == []


class TestEvaluateExpectations:
    def test_pass(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 790
        verdicts = evaluate_expectations(
            stats, [30, 26, 15, 6], VOLTAGES, build_expectations(make_test_info())
        )
        assert len(verdicts) == 1
        assert verdicts[0].sample_ok and verdicts[0].stat_ok
        assert verdicts[0].passed
        assert format_failure_remarks(verdicts) == "OK"

    def test_fail_on_single_sample(self):
        # ① 单样本 < 期望 → Fail（备注点名最小值）
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 780
        stats["mm2s"][0][V225_IDX] = 790
        verdicts = evaluate_expectations(
            stats, [30, 26, 15, 6], VOLTAGES, build_expectations(make_test_info())
        )
        assert not verdicts[0].sample_ok
        assert verdicts[0].stat_ok
        assert not verdicts[0].passed
        remarks = format_failure_remarks(verdicts)
        assert "no single sample" in remarks
        assert "782" in remarks

    def test_fail_on_mu_minus_2sigma(self):
        # ② µ-2σ ≤ 期望 → Fail（PDF："must be higher than"，严格）
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 782  # 等于期望 → 不满足 higher than
        verdicts = evaluate_expectations(
            stats, [30, 26, 15, 6], VOLTAGES, build_expectations(make_test_info())
        )
        assert verdicts[0].sample_ok
        assert not verdicts[0].stat_ok
        remarks = format_failure_remarks(verdicts)
        assert "μ-2σ" in remarks
        assert "782" in remarks

    def test_expectation_outside_measured_levels_skipped(self):
        # 期望格电流不在实测档位 → 跳过不判（如 Hermes 期望配了 30mA 档的文件）
        stats = make_stats(4, 9)
        expectations = build_expectations(make_test_info(spec="CF583083", qnom=4000, required=3000))
        verdicts = evaluate_expectations(stats, [30, 26, 15, 6], VOLTAGES, expectations)
        assert verdicts == []

    def test_hermes_partial_fail_only_failing_cell(self):
        stats = make_stats(5, 9)
        currents = [500, 250, 100, 50, 25]
        for c in (0, 2):  # 500mA / 100mA
            for v in (V225_IDX, V250_IDX):
                stats["min"][c][v] = 9999
                stats["mm2s"][c][v] = 9999
        stats["min"][2][V225_IDX] = 3500  # 100mA/2.25V 期望 3600 → 低于期望
        expectations = build_expectations(make_test_info(spec="CF583083", qnom=4000, required=3000))
        verdicts = evaluate_expectations(stats, currents, VOLTAGES, expectations)
        assert len(verdicts) == 4
        failed = [v for v in verdicts if not v.passed]
        assert len(failed) == 1
        assert failed[0].expectation.threshold_mah == 3600
        assert not failed[0].sample_ok
        # verdict_map：按格定位
        assert verdict_map(verdicts)[failed[0].current_index, failed[0].voltage_index] is failed[0]

    def test_expected_requirement_text_contains_verdict(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 800
        stats["mm2s"][0][V225_IDX] = 790
        verdicts = evaluate_expectations(
            stats, [30, 26, 15, 6], VOLTAGES, build_expectations(make_test_info())
        )
        text = expected_requirement_text(verdicts[0])
        assert "Expected: 782mAh" in text
        assert "30mA → 2.25V" in text
        assert "Verdict: Pass" in text

    def test_expected_requirement_text_shows_fail_values(self):
        stats = make_stats(4, 9)
        stats["min"][0][V225_IDX] = 700
        stats["mm2s"][0][V225_IDX] = 710
        verdicts = evaluate_expectations(
            stats, [30, 26, 15, 6], VOLTAGES, build_expectations(make_test_info())
        )
        text = expected_requirement_text(verdicts[0])
        assert "Verdict: Fail" in text
        assert "min 700" in text


class TestP4Defensive:
    """P4：中文构造关键词与 Coin 阈值防御"""

    def test_chinese_laminate_keyword(self):
        # 规则/界面回填 "叠片" 时按 75% 派生，不再静默返回 []
        expectations = build_expectations(make_test_info(construction="叠片 Type"))
        assert len(expectations) == 1
        assert expectations[0].threshold_mah == 690  # 920 × 75%

    def test_chinese_spiral_keyword(self):
        expectations = build_expectations(make_test_info(construction="螺旋 Type"))
        assert expectations[0].threshold_mah == 782  # 920 × 85%

    def test_freezer_temperature_field_flips_coin_current(self):
        # 报告侧无文件名：temperature 字段（ti[7]）含 freezer → 15mA（§7.1.1.2.4）
        items = make_test_info(construction="", spec="CR2450", qnom=600, required=380)
        items[7] = "Freezer Temperature:-20"
        expectations = build_expectations(items)
        assert expectations[0].current_ma == 15.0
