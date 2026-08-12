# src/battery_analysis/utils/json_config_manager.py
"""
JSON 配置管理器
提供 JSON 配置文件的读取、写入、原子替换功能。
键访问使用点号路径格式，如 "battery.types"。
"""
import json
import os
import tempfile
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class JsonConfigManager:
    """JSON 配置管理器，支持原子写入和键路径访问"""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._loaded = False

    def read_config(self, config_path: str) -> bool:
        """读取 JSON 配置文件"""
        path = Path(config_path)
        if not path.exists():
            logger.warning("Config file does not exist: %s", config_path)
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            self._loaded = True
            logger.info("Config file read successfully: %s", config_path)
            return True
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger.error("Failed to read config file: %s", e)
            self._data = {}
            self._loaded = False
            return False

    def write_config(self, config_path: str) -> bool:
        """原子写入 JSON 配置文件（写临时文件 → os.replace）"""
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(
                suffix=".tmp",
                prefix="config_",
                dir=os.path.dirname(config_path)
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(self._data, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, config_path)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
            logger.info("Config file written successfully: %s", config_path)
            return True
        except (IOError, OSError, PermissionError) as e:
            logger.error("Failed to write config file: %s", e)
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """通过点号路径获取值，如 'battery.types' → ['Coin Cell', ...]
        空字符串返回完整数据字典。"""
        if not self._loaded:
            return default
        if not key_path:
            return self._data
        keys = key_path.split(".")
        value = self._data
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError, IndexError):
            return default

    def set(self, key_path: str, value: Any) -> bool:
        """通过点号路径设置值"""
        keys = key_path.split(".")
        target = self._data
        try:
            for k in keys[:-1]:
                if k not in target or not isinstance(target[k], dict):
                    target[k] = {}
                target = target[k]
            target[keys[-1]] = value
            return True
        except (TypeError, KeyError) as e:
            logger.error("Failed to set config value: %s", e)
            return False

    def get_all(self) -> Dict[str, Any]:
        """获取完整配置数据"""
        return self._data

    def replace_all(self, data: Dict[str, Any]):
        """替换整个配置数据"""
        self._data = data
        self._loaded = True

    def set_defaults(self, defaults: Dict[str, Any]):
        """用默认数据填充（仅当文件初次创建时调用）"""
        self._data = defaults
        self._loaded = True

    def is_loaded(self) -> bool:
        return self._loaded

    def clear(self):
        self._data = {}
        self._loaded = False
