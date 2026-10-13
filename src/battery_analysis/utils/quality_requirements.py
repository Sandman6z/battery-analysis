"""BatteryQualityRequirements_v2.3 内置要求与合格判定（§6.2.11 / §7.1.1）

数据来源：BatteryQualityRequirements_v2.3.pdf

- §6.2.11 General Battery Performance Characterization：
    - "no single measured sample must have a usable capacity of less than
      the specified expected usable capacity"      → 最小值 ≥ 期望值
    - "the µ - 2 value of the corresponding pulse current / cut-off voltage
      step must be higher than the specified usable capacity"（≈96% 正态覆盖）
                                                  → µ-2σ > 期望值（严格大于）
    - "if not specified otherwise, the highest specified pulse current value
      should be used to calculate the usable capacity"
- §7.1.1.1–§7.1.1.11：各 profile 的期望可用容量（limit value 或 QNOM 百分比）
  与指定的 (脉冲电流, 截止电压) 格。

判定范围约定（用户口径）：只对 PDF 指定的 (脉冲电流, 截止电压) 格做合格判定；
配置里的 9 档超集（2.6V / 2.1V 等非 PDF 列）照常参与统计分析，但不参与判定。
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from battery_analysis.utils.battery_classifier import classify_spec
from battery_analysis.utils.pulse_currents import (
    FREEZER_REQUIRED_CAPACITY_MAH,
    is_freezer_context,
    lookup_pulse_currents,
)

logger = logging.getLogger(__name__)

# ── §7.1.1 脉冲簇参数（10 次 burst；时长/暂停单位秒）────────────
PULSE_BURSTS = 10
# 档位数 → 各档 (脉冲持续时间, 暂停时长)
PULSE_STEP_SCHEDULES = {
    4: ((1, 59), (1, 59), (2, 58), (5, 55)),
    5: ((1, 59), (1, 59), (1, 59), (2, 58), (5, 55)),
    6: ((1, 59), (1, 59), (1, 59), (1, 59), (2, 58), (5, 55)),
}

# §7.1.1 标准截止电压 6 档；§7.1.1.11 Hermes 额外含 2.5V
PDF_CUTOFF_VOLTAGES = (2.4, 2.3, 2.25, 2.2, 2.0, 1.8)
PDF_HERMES_CUTOFF_VOLTAGES = (2.5, 2.4, 2.3, 2.25, 2.2, 2.0, 1.8)

# 期望值格的截止电压（§7.1.1 各表的 Expected Usable Q 均指定 to 2.25V；
# Hermes 另有 2.5V 档）
_EXPECTATION_CUTOFF_V = 2.25

# 最小值比较容差（浮点噪声；PDF 语义为 "less than 才算不合格"）。
# 注意非对称：① 最小值用 "≥ 阈值 - ε" 容忍浮点噪声；
# ② µ-2σ 按 PDF 原文 "must be higher than" 严格比较，不加 ε。
_MIN_EPSILON = 1e-6


@dataclass(frozen=True)
class Expectation:
    """PDF 指定的单个判定格：某脉冲电流 / 某截止电压下的期望可用容量"""

    current_ma: float
    cutoff_v: float
    threshold_mah: float
    source: str = ""

    @property
    def label(self) -> str:
        return f"{self.current_ma:g}mA → {self.cutoff_v:g}V"


@dataclass(frozen=True)
class CellVerdict:
    """一个判定格的 §6.2.11 合格判定结果"""

    expectation: Expectation
    current_index: int
    voltage_index: int
    minimum: float
    mu2sigma: float
    sample_ok: bool  # ① 所有单样本 ≥ 期望（无样本低于期望值）
    stat_ok: bool  # ② µ-2σ > 期望（严格大于）
    sample_count: int | None = None  # 该格有效样本数（stats 含 "counts" 时）

    @property
    def passed(self) -> bool:
        return self.sample_ok and self.stat_ok

    @property
    def no_data(self) -> bool:
        """该判定格无任何有效样本 → 结论不完整（三态之 Incomplete，绝不聚合为 Pass）"""
        return self.sample_count == 0

    def failure_texts(self) -> list[str]:
        """失败项的英文说明（报告 Remarks 使用，报告语言为英文）"""
        texts = []
        exp = self.expectation
        if self.no_data:
            # 空格 ≠ 低容量：min=0 是缺失造成的，不能报 "minimum 0mAh" 误导
            texts.append(
                f"no measured samples at {exp.label}: data incomplete, retest required"
            )
            return texts
        if not self.sample_ok:
            texts.append(
                f"no single sample below expected usable Q "
                f"{round(exp.threshold_mah)}mAh at {exp.label}: "
                f"minimum {round(self.minimum)}mAh"
            )
        if not self.stat_ok:
            texts.append(
                f"μ-2σ {round(self.mu2sigma)}mAh not higher than expected "
                f"usable Q {round(exp.threshold_mah)}mAh at {exp.label}"
            )
        return texts


def _as_list(list_test_info) -> list:
    """兼容 TestInfo 实例与 19 位位置列表，并补齐缺省位"""
    if hasattr(list_test_info, "to_list"):
        items = list(list_test_info.to_list())
    else:
        items = list(list_test_info)
    return (items + [""] * 19)[:19]


def _to_float(value) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return 0.0


def _to_int(value) -> int | None:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def build_expectations(list_test_info) -> list[Expectation]:
    """按 PDF §7.1.1 派生当前测试的期望可用容量判定格

    优先级（用户口径：数据准确 > PDF > 原有行为）：
    - Hermes（型号含 583083，§7.1.1.11）：4 个绝对值判定格；
    - Coin Cell（§7.1.1.1/.2）：阈值取规则侧期望（380 常温 / 280 冷冻，
      与 PDF 一致），电流按冷冻/成组方式取最高档；
    - Pouch Cell（§7.1.1.3–.10）：按 QNOM 分档取最高脉冲电流，
      阈值 = QNOM × 85%（螺旋）/ 75%（叠片）；构造方法未知时返回 []
      （调用方回退到历史单点判定位置）。

    Args:
        list_test_info: TestInfo 实例或 19 位位置列表

    Returns:
        判定格列表；无法派生时为空列表
    """
    ti = _as_list(list_test_info)
    spec = str(ti[2] or "").strip()
    if not spec:
        return []
    construction = str(ti[1] or "")
    spec_method = str(ti[3] or "1S1P")
    qnom = _to_float(ti[9])
    required = _to_int(ti[17])

    # §7.1.1.11 CP583083 "Hermes"（CF583083 拼写兼容，与脉冲档位 override 同口径）
    if "583083" in spec.upper():
        return [
            Expectation(500, 2.25, 3000, "§7.1.1.11"),
            Expectation(100, 2.25, 3600, "§7.1.1.11"),
            Expectation(500, 2.5, 2600, "§7.1.1.11"),
            Expectation(100, 2.5, 3200, "§7.1.1.11"),
        ]

    if classify_spec(spec, int(qnom)) == "Coin Cell":
        # §7.1.1.1 常温 30mA/>380mAh；§7.1.1.2 冷冻单体 15mA、1S2P 30mA/>280mAh
        if required is None:
            return []
        # 三入口收敛：required==280 与温度字段（listTestInfo[7]）OR 判定，
        # 与 data_processor 文件名/规则口径同步（data_processor.py 共调本 helper）
        is_freezer = is_freezer_context(required=required, temperature=str(ti[7] or ""))
        if required not in (FREEZER_REQUIRED_CAPACITY_MAH, 380):
            # PDF §7.1.1.1/.2 只给 380（常温）/ 280（冷冻）；其他值属规则侧自定义，提示核对
            logger.warning(
                "Coin Cell required useable capacity %s mAh is neither 380 (room) nor "
                "280 (freezer) per PDF §7.1.1.1/.2; check rule derivation (spec=%s)",
                required,
                spec,
            )
        current = 15.0 if (is_freezer and spec_method != "1S2P") else 30.0
        return [Expectation(current, _EXPECTATION_CUTOFF_V, float(required), "§7.1.1.1/.2")]

    # Pouch Cell：构造方法决定 85%（螺旋）/ 75%（叠片）
    if qnom <= 0:
        return []
    lower = construction.lower()
    if "laminate" in lower or "叠片" in construction:
        ratio = 0.75
    elif "spiral" in lower or "螺旋" in construction:
        ratio = 0.85
    else:
        return []  # 构造未知 → 调用方回退历史判定
    currents = lookup_pulse_currents(spec, qnom, spec_method)
    if not currents:
        return []
    return [
        Expectation(
            float(currents[0]),  # 最高档脉冲电流（未特别说明时以最高电流计算）
            _EXPECTATION_CUTOFF_V,
            float(round(qnom * ratio)),
            "§7.1.1.3-.10",
        )
    ]


def _match_index(levels, value: float) -> int | None:
    """在档位列表中按数值匹配下标（容差 1e-6）"""
    for index, level in enumerate(levels):
        try:
            if abs(float(level) - value) < 1e-6:
                return index
        except (TypeError, ValueError):
            continue
    return None


def evaluate_expectations(
    stats: dict,
    list_current_level,
    list_voltage_level,
    expectations,
) -> list[CellVerdict]:
    """对每个 PDF 期望格执行 §6.2.11 合格判定

    不在实测档位中的期望格（如文件档位与 profile 不符）跳过不判。

    Args:
        stats: compute_statistics 输出（需含 "min" 与 "mm2s" 键）
        list_current_level: 实测脉冲电流档位列表
        list_voltage_level: 实测截止电压档位列表
        expectations: build_expectations 输出

    Returns:
        可判定格的 CellVerdict 列表
    """
    # P3：counts 缺失（旧 stats 桩）时 sample_count=None，行为与旧版完全一致
    counts = stats.get("counts") if isinstance(stats, dict) else None
    verdicts: list[CellVerdict] = []
    for exp in expectations or []:
        c = _match_index(list_current_level, exp.current_ma)
        v = _match_index(list_voltage_level, exp.cutoff_v)
        if c is None or v is None:
            continue
        try:
            minimum = float(stats["min"][c][v])
            mu2sigma = float(stats["mm2s"][c][v])
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        sample_count = None
        if counts is not None:
            try:
                sample_count = int(counts[c][v])
            except (IndexError, TypeError, ValueError):
                sample_count = None
        verdicts.append(
            CellVerdict(
                expectation=exp,
                current_index=c,
                voltage_index=v,
                minimum=minimum,
                mu2sigma=mu2sigma,
                sample_ok=minimum >= exp.threshold_mah - _MIN_EPSILON,
                stat_ok=mu2sigma > exp.threshold_mah,
                sample_count=sample_count,
            )
        )
    return verdicts


def format_failure_remarks(verdicts) -> str:
    """汇总失败判定格的英文说明；全部通过返回 "OK"（与旧版 Remarks 口径一致）"""
    failures = [v for v in verdicts or [] if not v.passed]
    if not failures:
        return "OK"
    texts: list[str] = []
    for verdict in failures:
        texts.extend(verdict.failure_texts())
    return "; ".join(texts)


def verdict_map(verdicts) -> dict:
    """判定格列表 → {(电流下标, 电压下标): CellVerdict}，供报表按格标注"""
    return {(v.current_index, v.voltage_index): v for v in verdicts or []}


def expected_requirement_text(verdict: CellVerdict) -> str:
    """判定格的报表标注行（Excel Overview 单元格附加文本）"""
    exp = verdict.expectation
    lines = [
        f"Expected: {round(exp.threshold_mah)}mAh ({exp.label})",
    ]
    if verdict.no_data:
        lines.append("Verdict: Incomplete (no samples)")
        return "\n".join(lines)
    if verdict.passed:
        lines.append("Verdict: Pass")
    else:
        problems = []
        if not verdict.sample_ok:
            problems.append(f"min {round(verdict.minimum)}")
        if not verdict.stat_ok:
            problems.append(f"μ-2σ {round(verdict.mu2sigma)}")
        lines.append(f"Verdict: Fail ({', '.join(problems)})")
    return "\n".join(lines)
