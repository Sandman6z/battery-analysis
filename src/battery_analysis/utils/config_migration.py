# -*- coding: utf-8 -*-
"""
配置文件迁移机制

版本化的迁移脚本，自动按序执行。
当 config.json 中 version 低于当前代码期望版本时，依次执行未完成的迁移。
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── 迁移脚本注册 ──────────────────────────────────────────────

_MIGRATIONS: Dict[int, str] = {}  # version -> description
_MIGRATION_FUNCS: Dict[int, callable] = {}


def register_migration(version: int, description: str):
    """装饰器：注册指定版本的迁移脚本。"""
    def decorator(func):
        _MIGRATIONS[version] = description
        _MIGRATION_FUNCS[version] = func
        logger.debug("注册迁移 v%s: %s", version, description)
        return func
    return decorator


# ── 内置迁移 ──────────────────────────────────────────────────


@register_migration(2, "补全 test.equipment 预设数据")
def _migrate_v2(config: Dict[str, Any]) -> Dict[str, Any]:
    """从默认配置补充 equipment 字段。"""
    from battery_analysis.utils.config_defaults import DEFAULT_CONFIG
    test = config.setdefault("test", {})
    if not test.get("equipment"):
        test["equipment"] = DEFAULT_CONFIG.get("test", {}).get("equipment", {})
        logger.info("迁移 v2: 已补全 equipment 预设数据")
    return config


# ── 执行引擎 ──────────────────────────────────────────────────


CURRENT_CONFIG_VERSION = 2  # 代码期望的配置版本


def run_migrations(config: Dict[str, Any]) -> Dict[str, Any]:
    """从当前版本依次执行到目标版本。"""
    current_version = config.get("version", 1)

    if current_version >= CURRENT_CONFIG_VERSION:
        return config

    logger.info("配置版本 %d → %d，执行 %d 个迁移脚本",
                current_version, CURRENT_CONFIG_VERSION,
                CURRENT_CONFIG_VERSION - current_version)

    for ver in range(current_version + 1, CURRENT_CONFIG_VERSION + 1):
        if ver in _MIGRATION_FUNCS:
            logger.info("执行迁移 v%d: %s", ver, _MIGRATIONS.get(ver, ""))
            try:
                config = _MIGRATION_FUNCS[ver](config)
                config["version"] = ver
            except Exception as e:
                logger.error("迁移 v%d 失败: %s", ver, e)
                raise
        else:
            config["version"] = ver

    return config
