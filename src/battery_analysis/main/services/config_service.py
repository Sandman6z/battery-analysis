# -*- coding: utf-8 -*-
"""
配置服务实现模块

提供配置文件读取、写入和管理功能的实现
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from battery_analysis.utils.base_service import BaseService
from battery_analysis.utils.json_config_manager import JsonConfigManager
import os


class ConfigService(BaseService):
    """
    配置服务实现类

    作为系统内配置文件(config.json)的唯一入口，所有模块均应通过此服务读取配置。
    底层使用 JsonConfigManager，支持点号路径键访问（如 "battery.types"）。
    """

    def __init__(self):
        """
        初始化配置服务
        """
        BaseService.__init__(self)
        self._config_manager = JsonConfigManager()
        self._config_path = None
        self._loaded = False

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点号路径格式（如 "battery.types"）
            default: 默认值

        Returns:
            Any: 配置值
        """
        try:
            if not self._config_manager.is_loaded():
                self.load_config()
            return self._config_manager.get(key, default)
        except (KeyError, TypeError, ValueError) as e:
            self.logger.error("获取配置值失败: %s", e)
            return default

    def get_config_value_raw(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取配置值的原始字符串表示（不做类型推断）

        Args:
            key: 配置键，支持点号路径格式（如 "battery.types"）
            default: 默认值

        Returns:
            Optional[str]: 原始字符串值
        """
        try:
            value = self.get_config_value(key, default)
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            if value is None:
                return None
            return str(value)
        except (KeyError, TypeError, ValueError, OSError) as e:
            self.logger.error("获取原始配置值失败: %s", e)
            return default

    def set_config_value(self, key: str, value: Any) -> bool:
        """
        设置配置值

        Args:
            key: 配置键，支持点号路径格式（如 "battery.types"）
            value: 配置值

        Returns:
            bool: 设置是否成功
        """
        try:
            return self._config_manager.set(key, value)
        except (KeyError, TypeError, ValueError, OSError) as e:
            self.logger.error("设置配置值失败: %s", e)
            return False

    def replace_all_config(self, data: Dict[str, Any]) -> bool:
        """
        用默认数据替换整个配置（不写文件，需调用 save_config）

        Args:
            data: 完整配置数据字典

        Returns:
            bool: 设置是否成功
        """
        try:
            self._config_manager.replace_all(data)
            self._loaded = True
            return True
        except (KeyError, TypeError, ValueError, OSError) as e:
            self.logger.error("设置默认配置失败: %s", e)
            return False

    def save_config(self) -> bool:
        """
        保存配置到文件

        Returns:
            bool: 保存是否成功
        """
        try:
            if self._config_path and self._config_manager.is_loaded():
                success = self._config_manager.write_config(str(self._config_path))
                if success:
                    self.logger.info("配置已保存到: %s", self._config_path)
                return success
            else:
                self.logger.warning("无法保存配置：未指定配置路径或配置未加载")
                return False
        except (KeyError, TypeError, ValueError, OSError) as e:
            self.logger.error("保存配置失败: %s", e)
            return False

    def load_config(self, config_path: Optional[str] = None, use_cache: bool = True) -> bool:
        """
        从文件加载配置

        Args:
            config_path: 配置文件路径，None表示使用默认路径
            use_cache: 是否使用缓存（仅当文件未修改时跳过重读）

        Returns:
            bool: 加载是否成功
        """
        try:
            if config_path:
                self._config_path = Path(config_path)
            else:
                self._config_path = self._resolve_config_path()

            if not self._config_path or not self._config_path.exists():
                # 首次运行：用默认数据创建
                from battery_analysis.utils.config_defaults import DEFAULT_CONFIG
                self._config_manager.set_defaults(DEFAULT_CONFIG)
                self._config_manager.write_config(str(self._config_path))
                self._loaded = True
                self.logger.info("首次运行，已创建默认配置文件: %s", self._config_path)
                return True

            success = self._config_manager.read_config(str(self._config_path))
            self._loaded = success
            if success:
                # Schema 验证
                try:
                    from battery_analysis.utils.config_schema import AppConfigSchema
                    all_data = self._config_manager.get_all()
                    schema = AppConfigSchema.from_dict(all_data)
                    warnings = schema.validate()
                    for w in warnings:
                        self.logger.warning("配置警告: %s", w)
                except Exception as schema_err:
                    self.logger.warning("配置 schema 验证失败（不影响运行）: %s", schema_err)

                # 版本化迁移
                try:
                    from battery_analysis.utils.config_migration import run_migrations
                    all_data = self._config_manager.get_all()
                    migrated = run_migrations(all_data)
                    if migrated.get("version", 0) > all_data.get("version", 0):
                        self._config_manager.replace_all(migrated)
                        self._config_manager.write_config(str(self._config_path))
                        self.logger.info("配置已迁移至 v%d", migrated["version"])
                except Exception as migrate_err:
                    self.logger.warning("配置迁移失败（使用旧版配置继续）: %s", migrate_err)

                self.logger.info("配置已加载: %s", self._config_path)
            else:
                self.logger.warning("配置文件加载失败: %s", self._config_path)
            return success
        except (OSError, IOError, PermissionError) as e:
            self.logger.error("加载配置 I/O 错误: %s", e)
            self._loaded = False
            return False

    def reload_config(self) -> bool:
        """
        重新加载配置（清除缓存后强制重读）

        Returns:
            bool: 加载是否成功
        """
        self.clear_cache()
        self._loaded = False
        return self.load_config(use_cache=False)

    def clear_cache(self) -> None:
        """
        清除内部配置缓存
        当配置文件可能已变更时调用
        """
        self._config_manager.clear()

    def get_config_sections(self) -> List[str]:
        """
        获取所有配置节名称

        Returns:
            List[str]: 配置节名称列表
        """
        try:
            if not self._config_manager.is_loaded():
                self.load_config()
            data = self._config_manager.get_all()
            return [k for k in data.keys() if isinstance(data[k], dict)]
        except (KeyError, TypeError, ValueError, OSError) as e:
            self.logger.error("获取配置节失败: %s", e)
            return []

    def get_all_values(self) -> Dict[str, Any]:
        """
        获取所有配置节及其键值对

        Returns:
            Dict[str, Any]: 完整配置数据字典
        """
        try:
            if not self._config_manager.is_loaded():
                self.load_config()
            return self._config_manager.get_all()
        except (KeyError, TypeError, ValueError, OSError) as e:
            self.logger.error("获取全部配置值失败: %s", e)
            return {}

    def get_section_options(self, section: str) -> List[str]:
        """
        获取指定配置节的所有选项名称

        Args:
            section: 配置节名称

        Returns:
            List[str]: 选项名称列表
        """
        try:
            if not self._config_manager.is_loaded():
                self.load_config()
            section_data = self._config_manager.get(section, {})
            if isinstance(section_data, dict):
                return list(section_data.keys())
            return []
        except (KeyError, TypeError, ValueError, OSError) as e:
            self.logger.error("获取配置节选项失败: %s", e)
            return []

    def get_section_config(self, section: str) -> Dict[str, Any]:
        """
        获取指定配置节的所有键值对

        Args:
            section: 配置节名称

        Returns:
            Dict[str, Any]: 配置节内容
        """
        try:
            if not self._config_manager.is_loaded():
                self.load_config()
            result = self._config_manager.get(section, {})
            return result if isinstance(result, dict) else {}
        except (KeyError, TypeError, ValueError, OSError) as e:
            self.logger.error("获取配置节失败: %s", e)
            return {}

    def has_config_key(self, key: str) -> bool:
        """
        检查配置键是否存在

        Args:
            key: 配置键，支持点号路径格式（如 "battery.types"）

        Returns:
            bool: 键是否存在
        """
        try:
            if not self._config_manager.is_loaded():
                self.load_config()
            return self._config_manager.get(key) is not None
        except (KeyError, TypeError, ValueError, OSError) as e:
            self.logger.error("检查配置键失败: %s", e)
            return False

    def _resolve_config_path(self) -> Path:
        """解析配置文件的 %APPDATA% 路径"""
        appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(appdata) / "battery-analysis" / "config.json"

    def find_config_file(self, file_name: str = "config.json", use_cache: bool = False) -> Optional[Path]:
        """
        查找配置文件路径

        Args:
            file_name: 配置文件名称（兼容旧接口，默认改为 config.json）
            use_cache: 是否使用缓存的配置文件路径，默认为False

        Returns:
            Optional[Path]: 配置文件路径
        """
        return self._resolve_config_path()
