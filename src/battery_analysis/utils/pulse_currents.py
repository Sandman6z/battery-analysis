"""脉冲电流档位查表模块

依据 BatteryQualityRequirements_v2.3 §7.1.1 测试标准，按电池类型/容量给出脉冲电流档位序列（mA）：

- Coin Cell CR2450 标准型:                       30 / 26 / 15 / 6
- Coin Cell CR2450 Freezer 型（单体）:            15 / 13 / 7.5 / 3
- Coin Cell CR2450 Freezer 型 1S2P Pack:         30 / 26 / 15 / 6（与标准型相同）
- Pouch Cell 按 QNOM 分档:
  - QNOM < 1200mAh:                              30 / 26 / 15 / 6
  - 1200 <= QNOM < 2000mAh:                      60 / 30 / 15 / 6
  - 2000 <= QNOM < 3000mAh:                      100 / 60 / 30 / 15 / 6
  - QNOM >= 3000mAh:                             150 / 100 / 60 / 30 / 15 / 6
- 特例 CP583083 ("Hermes", §7.1.1.11):            500 / 250 / 100 / 50 / 25

优先级约定：文件名解析（如 "(30-26-15-6mA)"）优先，本查表作为容量档位兜底。
"""

from __future__ import annotations

import re

from battery_analysis.utils.battery_classifier import (
    classify_spec,
    extract_capacity,
    extract_spec_name,
)

# Coin Cell CR2450 标准型档位（Freezer 型 1S2P Pack 同此档）
COIN_STANDARD_PULSE_CURRENTS = [30, 26, 15, 6]
# Coin Cell CR2450 Freezer 型单体档位（降额档）
COIN_FREEZER_SINGLE_PULSE_CURRENTS = [15, 13, 7.5, 3]

# Pouch Cell 容量档位：(QNOM 上限 mAh, 档位)，按顺序取第一个满足 QNOM < 上限的档
_POUCH_CAPACITY_BANDS = (
    (1200, [30, 26, 15, 6]),
    (2000, [60, 30, 15, 6]),
    (3000, [100, 60, 30, 15, 6]),
)
# QNOM >= 3000mAh 档位
_POUCH_LARGE_PULSE_CURRENTS = [150, 100, 60, 30, 15, 6]

# 特殊型号覆盖：型号名包含关键字时直接取对应档位（CP583083 / CF583083 拼写兼容）
_MODEL_OVERRIDES = (
    ("583083", [500, 250, 100, 50, 25]),
)


def normalize_current_levels(values) -> list:
    """将电流档位规整为数值列表

    整数值转为 int（避免输出文件名/报表出现 "30.0mA"），非整数值（如 7.5）保留 float。
    无法转换的项被丢弃。

    Args:
        values: 任意可迭代的数值/字符串

    Returns:
        规整后的电流档位列表
    """
    result = []
    for value in values:
        try:
            number = float(str(value).strip())
        except (TypeError, ValueError):
            continue
        result.append(int(number) if number.is_integer() else number)
    return result


# 冷冻型判定：规则中「要求可用容量」等于此值时视为冷冻（Freezer）型
# 与 temperature_handler.set_temperature_by_capacity 的既有约定一致（280 → Freezer, 380 → Room）
FREEZER_REQUIRED_CAPACITY_MAH = 280


def required_useable_capacity_from_rule(rule: str, construction: str = "") -> int | None:
    """从单条规则解析「要求可用容量」（第 5 段，规则格式 "型号/成组方式/容量/计算容量/要求可用容量/CC电流"）

    支持三种形式（BatteryQualityRequirements_v2.3 对齐）：

    - 绝对值（如 "380"、"280"、"3000"）；
    - 单百分比（如 "80%"，按计算标称容量换算）；
    - 构造相关双百分比（如 "85%|75%"，螺旋/叠片两档，依 construction
      选取；Pouch §7.1.1.3–.10 期望 = QNOM × 85%（螺旋）/ 75%（叠片）；
      construction 为空或未识别时默认取第一个（螺旋 85%））。

    Args:
        rule: 规则字符串
        construction: 构造方法（如 "Spiral Type" / "Laminate Type"），
            用于双百分比规则选取；空串时取第一个百分比

    Returns:
        要求可用容量（mAh），无法解析返回 None
    """
    parts = str(rule).split("/")
    if len(parts) < 5:
        return None
    segment = parts[4].strip()
    if "%" in segment:
        dual = re.fullmatch(r"(\d+(?:\.\d+)?)%\s*\|\s*(\d+(?:\.\d+)?)%", segment)
        if dual:
            pct_text = dual.group(2) if "laminate" in str(construction or "").lower() else dual.group(1)
        else:
            match = re.search(r"(\d+(?:\.\d+)?)%", segment)
            if not match:
                return None
            pct_text = match.group(1)
        if len(parts) < 4:
            return None
        try:
            return int(float(parts[3]) * float(pct_text) / 100)
        except ValueError:
            return None
    try:
        return int(float(segment))
    except ValueError:
        return None


def is_freezer_from_rules(rules, spec_name: str) -> bool:
    """判断指定型号是否为冷冻（Freezer）型

    判定唯一依据：该型号规则的「要求可用容量」（第 5 段）为
    FREEZER_REQUIRED_CAPACITY_MAH（280mAh，冷冻）或 380mAh（常温）。

    不按型号名判定：CR2450 之后的后缀（D、HE4 等）各厂商命名不同，不可靠；
    文件名含 freezer 的检测由调用方先行处理（与 temperature_handler 的
    XML 优先约定一致），本函数只负责规则侧的 280/380 判定。

    Args:
        rules: 规则字符串列表
        spec_name: 规格型号名

    Returns:
        是否为冷冻型；型号未匹配或无法解析时返回 False
    """
    target = (spec_name or "").strip()
    if not target:
        return False
    for rule in rules or []:
        if extract_spec_name(rule) != target:
            continue
        required = required_useable_capacity_from_rule(rule)
        if required is not None:
            return required == FREEZER_REQUIRED_CAPACITY_MAH
    return False


def capacity_from_rules(rules, spec_name: str) -> float:
    """从规则列表中查找指定型号的容量（mAh）

    规则格式："型号/成组方式/容量/..."（如 "CR2450/1S1P/600/550/380/1.0"）。

    Args:
        rules: 规则字符串列表
        spec_name: 规格型号名

    Returns:
        匹配型号的容量，未找到返回 0.0
    """
    target = (spec_name or "").strip()
    if not target:
        return 0.0
    for rule in rules or []:
        rule_str = str(rule)
        if extract_spec_name(rule_str) == target:
            return float(extract_capacity(rule_str))
    return 0.0


def lookup_pulse_currents(
    spec_name: str,
    capacity_mah: float = 0,
    spec_method: str = "1S1P",
    is_freezer: bool = False,
) -> list:
    """按型号/容量/成组方式/冷冻标志查表获取脉冲电流档位

    Args:
        spec_name: 规格型号名（如 "CR2450"、"CP305050"）
        capacity_mah: 额定容量 QNOM（mAh），型号未知容量时传 0
        spec_method: 成组方式（如 "1S1P"、"1S2P"）
        is_freezer: 是否冷冻（Freezer）型/冷冻工况

    Returns:
        脉冲电流档位列表（mA），型号名为空或 Pouch 型容量未知时返回空列表（不覆盖已有配置）
    """
    name = (spec_name or "").strip()
    if not name:
        return []

    upper = name.upper()
    for keyword, currents in _MODEL_OVERRIDES:
        if keyword in upper:
            return list(currents)

    if classify_spec(name, int(capacity_mah or 0)) == "Coin Cell":
        # Freezer 型单体使用降额档位；1S2P Pack 使用标准档位（§7.1.1.2）
        if is_freezer and (spec_method or "").strip() != "1S2P":
            return list(COIN_FREEZER_SINGLE_PULSE_CURRENTS)
        return list(COIN_STANDARD_PULSE_CURRENTS)

    # Pouch 档位取决于 QNOM，容量未知时无法定档，返回空列表（不覆盖已有配置）
    if not capacity_mah or capacity_mah <= 0:
        return []

    for upper_limit, currents in _POUCH_CAPACITY_BANDS:
        if capacity_mah < upper_limit:
            return list(currents)
    return list(_POUCH_LARGE_PULSE_CURRENTS)
