"""
配置文件迁移机制

版本化的迁移脚本，自动按序执行。
当 config.json 中 version 低于当前代码期望版本时，依次执行未完成的迁移。
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ── 迁移脚本注册 ──────────────────────────────────────────────

_MIGRATIONS: dict[int, str] = {}  # version -> description
_MIGRATION_FUNCS: dict[int, callable] = {}


def register_migration(version: int, description: str):
    """装饰器：注册指定版本的迁移脚本。"""

    def decorator(func):
        _MIGRATIONS[version] = description
        _MIGRATION_FUNCS[version] = func
        logger.debug("Registering migration v%s: %s", version, description)
        return func

    return decorator


# ── 内置迁移 ──────────────────────────────────────────────────


@register_migration(2, "Populate test.equipment presets")
def _migrate_v2(config: dict[str, Any]) -> dict[str, Any]:
    """从默认配置补充 equipment 字段。"""
    from battery_analysis.utils.config_defaults import DEFAULT_CONFIG

    test = config.setdefault("test", {})
    if not test.get("equipment"):
        test["equipment"] = DEFAULT_CONFIG.get("test", {}).get("equipment", {})
        logger.info("Migration v2: equipment presets filled in")
    return config


@register_migration(3, "Remove orphan top-level INI-style keys")
def _migrate_v3(config: dict[str, Any]) -> dict[str, Any]:
    """移除旧版代码误写的字面顶级键（如 "BatteryConfig/PulseCurrent"）。

    旧版 data_processor 用 INI 路径写 JSON 顶级键，读取方
    （battery.pulseCurrents）永远读不到，属无害孤儿数据，此处统一清理。
    """
    orphan_keys = [k for k in list(config.keys()) if isinstance(k, str) and "/" in k]
    for key in orphan_keys:
        config.pop(key, None)
    if orphan_keys:
        logger.info("Migration v3: removed orphan keys: %s", orphan_keys)
    return config


# ── 执行引擎 ──────────────────────────────────────────────


@register_migration(4, "Drop battery.specifications (spec lists derive from battery.rules)")
def _migrate_v4(config: dict[str, Any]) -> dict[str, Any]:
    """移除 battery.specifications 存储副本。

    specifications 不再是配置项：规格列表由各读取方（ConfigManager 的规格键、
    data_loader 等）直接从 battery.rules 派生（battery_classifier.derive_specifications），
    存储副本只会造成不同步。
    """
    battery = config.get("battery")
    if isinstance(battery, dict) and "specifications" in battery:
        battery.pop("specifications")
        logger.info("Migration v4: removed battery.specifications (specs derive from rules)")
    return config


# ── 迁移 v5：默认规则对齐 BatteryQualityRequirements_v2.3 ──────

# 旧默认规则 → 新默认规则（§7.1.1）。仅当规则行与旧默认完全一致时才替换，
# 用户改过的规则不动：
# - CP224642A（Pouch <1200，§7.1.1.3/.4）：期望 85%|75%（螺旋/叠片），CC 段流 2mA/10h(20mAh)
# - CF583083（"Hermes"，§7.1.1.11）：主期望 >3000mAh@2.25V/500mA，CC 段流 50mA/1h(50mAh)
# - CP305050（Pouch 2000-3000，§7.1.1.7/.8）：期望 85%|75%，CC 段流 5mA/4h
# CR2450 系列四条默认规则与 PDF 一致，不迁移。
_PDF_RULE_REPLACEMENTS = {
    "CP224642A/1S1P/920/920/80%/5.0": "CP224642A/1S1P/920/920/85%|75%/2",
    "CF583083/1S1P/4000/4000/80%/5.0": "CF583083/1S1P/4000/4000/3000/50",
    "CP305050/1S1P/2000/2000/80%/1.0": "CP305050/1S1P/2000/2000/85%|75%/5",
}


@register_migration(5, "Align default rules with BatteryQualityRequirements_v2.3")
def _migrate_v5(config: dict[str, Any]) -> dict[str, Any]:
    """默认规则对齐 BatteryQualityRequirements_v2.3 §7.1.1。

    - 要求可用容量：Pouch 80% → 85%|75%（螺旋/叠片，按构造方法换算）；
      Hermes 80% → 绝对值 3000（>3000mAh@2.25V/500mA）；
    - CC 段流电流：2mA（<1200）/ 50mA（Hermes）/ 5mA（2000-3000）。
    只替换与旧默认完全一致的规则行；用户自定义修改过的规则保持不变。
    """
    battery = config.get("battery")
    rules = battery.get("rules") if isinstance(battery, dict) else None
    if isinstance(rules, list):
        new_rules = [_PDF_RULE_REPLACEMENTS.get(str(rule), rule) for rule in rules]
        if new_rules != rules:
            battery["rules"] = new_rules
            logger.info("Migration v5: default rules aligned to BatteryQualityRequirements_v2.3")
    return config


CURRENT_CONFIG_VERSION = 5  # 代码期望的配置版本


def run_migrations(config: dict[str, Any]) -> dict[str, Any]:
    """从当前版本依次执行到目标版本。"""
    current_version = config.get("version", 1)

    if current_version >= CURRENT_CONFIG_VERSION:
        return config

    logger.info(
        "Config version %d → %d, running %d migration script(s)",
        current_version,
        CURRENT_CONFIG_VERSION,
        CURRENT_CONFIG_VERSION - current_version,
    )

    for ver in range(current_version + 1, CURRENT_CONFIG_VERSION + 1):
        if ver in _MIGRATION_FUNCS:
            logger.info("Running migration v%d: %s", ver, _MIGRATIONS.get(ver, ""))
            try:
                config = _MIGRATION_FUNCS[ver](config)
                config["version"] = ver
            except Exception as e:
                logger.error("Migration v%d failed: %s", ver, e)
                raise
        else:
            config["version"] = ver

    return config
