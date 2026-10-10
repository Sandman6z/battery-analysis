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


CURRENT_CONFIG_VERSION = 4  # 代码期望的配置版本


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
