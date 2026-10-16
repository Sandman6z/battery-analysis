"""profile xml 与 ndax sidecar 档位校验决策树（会议裁决①③④）。

三段式：
- extract_profile_levels：读 profile 测试配置 xml 的 PulseData 声明档位；
- check_step_completeness：声明档位 vs sidecar 实测档位（转换时写入）
  的工步完成性判定（裁决④ 的 complete / truncated / missing）；
- decide_profile_validation：完整决策树，产出 Info_Plot.json.profile_validation
  留痕记录 {result, mismatch_type, decision, policy_version}；
- check_batch_consistency：多 ndax 文件间档位一致性（裁决③ 硬阻断）。

政策版本：2026.10（会议 Final 条目裁决⑤）。
"""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from battery_analysis.utils.ndax_meta import _as_float, _parse_xml

logger = logging.getLogger(__name__)

POLICY_VERSION = "2026.10"

# 单档实测容差（裁决②/④）：max(声明值 1%, 0.5mA)
LEVEL_TOLERANCE = (0.01, 0.5)

# 决策结果常量
RESULT_MATCH = "match"
RESULT_VALUE_MISMATCH = "value_mismatch"
RESULT_COUNT_MISMATCH = "level_count_mismatch"
RESULT_BATCH_INCONSISTENT = "batch_inconsistent"

DECISION_PROCEED = "proceed"
DECISION_OFFER_OVERRIDE = "offer_override"
DECISION_BLOCK = "block"

COMPLETENESS_COMPLETE = "complete"
COMPLETENESS_TRUNCATED = "truncated"
COMPLETENESS_MISSING = "missing"


def _level_tolerance(level: float) -> float:
    """单档容差 = max(|level| * 1%, 0.5mA)。"""
    return max(abs(level) * LEVEL_TOLERANCE[0], LEVEL_TOLERANCE[1])


def extract_profile_levels(profile_path) -> list[float] | None:
    """提取 profile 测试配置 xml 的脉冲档位（与 Step.xml PulseData 同构）。

    缺文件 / 不可解析 / 无脉冲档位 → None（调用方按"无 profile"处理，
    属于声明弹框范畴，不在本决策树内）。
    """
    path = Path(profile_path)
    try:
        data = path.read_bytes()
    except OSError as exc:
        logger.warning("Cannot read profile %s: %s", path, exc)
        return None
    root = _parse_xml(data)
    if root is None:
        return None
    levels: list[float] = []
    for pulse_data in root.iter("PulseData"):
        for child in pulse_data:
            value = _as_float(child.get("Value"))
            if value:  # 奇数 PulseN Value=0（休息段）跳过
                levels.append(abs(value))
    levels = list(dict.fromkeys(levels))  # 去重保序
    return levels or None


def check_step_completeness(declared_levels, observed_levels) -> str:
    """裁决④ 完成性判定。

    Args:
        declared_levels: Step.xml / sidecar 声明的脉冲档位。
        observed_levels: 转换时从实测数据算出的已执行档位
            （sidecar 旧版缺该字段 → None → missing，从严）。

    Returns:
        "complete"（全部档位实测出现）/ "truncated"（有档位缺失）
        / "missing"（无完成性证据）。
    """
    if not declared_levels or observed_levels is None:
        return COMPLETENESS_MISSING
    observed = [float(x) for x in observed_levels]
    if not observed and declared_levels:
        return COMPLETENESS_TRUNCATED
    for level in declared_levels:
        tol = _level_tolerance(float(level))
        if not any(abs(o - float(level)) <= tol for o in observed):
            return COMPLETENESS_TRUNCATED
    return COMPLETENESS_COMPLETE


def _measured_drift(medians) -> dict:
    """裁决②：|中位数-档位| > max(1%, 0.5mA) 的档位 → {档位(str): 偏差}。"""
    drift: dict = {}
    for key, median in (medians or {}).items():
        try:
            level = float(key)
            value = float(median)
        except (TypeError, ValueError):
            continue
        deviation = abs(value - level)
        if deviation > _level_tolerance(level):
            drift[f"{level:g}"] = round(deviation, 6)
    return drift


def decide_profile_validation(
    profile_levels, ndax_levels, observed_levels=None, medians=None
) -> dict:
    """完整决策树（裁决①③④），返回 Info_Plot.json.profile_validation 记录。

    Args:
        profile_levels: profile xml 声明档位（extract_profile_levels 结果，
            调用方保证非 None——无 profile 走声明弹框，不进本树）。
        ndax_levels: ndax sidecar 档位（Step.xml 权威）。
        observed_levels: sidecar 实测档位（observed_pulse_currents，
            旧版 sidecar 缺字段 → None）。
        medians: sidecar 实测中位数 {档位(str): 中位数}
            （observed_pulse_medians，裁决② 输入，可缺）。

    Returns:
        dict: {result, mismatch_type, decision, policy_version}；
        实测漂移超阈值时附 measured_drift {档位: 偏差}（裁决② 留痕）。
    """
    record = {
        "result": RESULT_MATCH,
        "mismatch_type": None,
        "decision": DECISION_PROCEED,
        "policy_version": POLICY_VERSION,
    }
    if not profile_levels or not ndax_levels:
        # 一侧无档位可比：无证据不裁决，放行（调用方通常已提前短路）
        record["result"] = "no_evidence"
        return record

    profile = [float(x) for x in profile_levels]
    ndax = [float(x) for x in ndax_levels]

    # 裁决② 实测层：中位数偏差 > max(1%, 0.5mA) → 黄警放行留痕
    drift = _measured_drift(medians)
    if drift:
        record["measured_drift"] = drift

    if len(ndax) != len(profile):
        record["result"] = RESULT_COUNT_MISMATCH
        if len(ndax) > len(profile):
            # ndax 多于 profile = 数据完整仅 profile 陈旧 → 直接给按钮（不查工步）
            record["mismatch_type"] = "level_count_mismatch_excess"
            record["decision"] = DECISION_OFFER_OVERRIDE
        else:
            # ndax 少于 profile = 可能测试截断 → 查完成性：
            # ndax(Step.xml) 自身声明档位 vs 实测档位，判测试是否
            # 跑完自己配置的工步（profile 不参与完成性，否则 observed ⊆
            # ndax ⊂ profile 恒不全，complete 分支永不可达）
            status = check_step_completeness(ndax, observed_levels)
            if status == COMPLETENESS_COMPLETE:
                record["mismatch_type"] = "level_count_mismatch_complete"
                record["decision"] = DECISION_OFFER_OVERRIDE
            elif status == COMPLETENESS_TRUNCATED:
                record["mismatch_type"] = "level_count_mismatch_truncated"
                record["decision"] = DECISION_BLOCK
            else:
                record["mismatch_type"] = "level_count_missing_evidence"
                record["decision"] = DECISION_BLOCK
        return record

    # 档数相同、逐档比值（裁决①：0 容差）
    if profile != ndax:
        record["result"] = RESULT_VALUE_MISMATCH
        record["mismatch_type"] = "value_mismatch"
        record["decision"] = DECISION_OFFER_OVERRIDE
    return record


def check_batch_consistency(levels_by_file) -> dict | None:
    """裁决③：多 ndax 文件间档位一致性。

    Args:
        levels_by_file: {文件名: pulse_currents}（仅含非空档位条目）。

    Returns:
        不一致 → 硬阻断记录 {result, mismatch_type, decision, policy_version}
        （无放行选项）；一致或样本不足 → None。
    """
    level_sets = {tuple(sorted(float(x) for x in v)) for v in levels_by_file.values() if v}
    if len(level_sets) > 1:
        return {
            "result": RESULT_BATCH_INCONSISTENT,
            "mismatch_type": "batch_level_mismatch",
            "decision": DECISION_BLOCK,
            "policy_version": POLICY_VERSION,
        }
    return None
