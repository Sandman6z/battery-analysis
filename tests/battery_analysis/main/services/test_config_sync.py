"""
测试配置保存/重新加载/刷新同步的完整性
模拟 ConfigDialog._on_save → ConfigManager.reload_config() → get_config 的完整流程
"""

import copy
import json
import os
import tempfile
from pathlib import Path

from battery_analysis.main.services.config_service import ConfigService
from battery_analysis.utils.config_defaults import DEFAULT_CONFIG


class TestConfigSync:
    def setup_method(self):
        """每个测试前创建临时 APPDATA 目录"""
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.appdata_roaming = self.tmp_dir / "Roaming"
        self.config_dir = self.appdata_roaming / "battery-analysis"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.config_dir / "config.json"
        self.config_path.write_text(
            json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # 保存原始 APPDATA 用于还原
        self._orig_appdata = os.environ.get("APPDATA")

    def teardown_method(self):
        """清理临时文件和环境变量"""
        import shutil

        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        if self._orig_appdata:
            os.environ["APPDATA"] = self._orig_appdata
        elif "APPDATA" in os.environ:
            del os.environ["APPDATA"]

    def _init_env(self):
        """设置 APPDATA 指向临时目录，使 ConfigService 解析到我们控制的路径"""
        os.environ["APPDATA"] = str(self.appdata_roaming)

    def _make_service(self) -> ConfigService:
        """创建一个配置正确的 ConfigService"""
        self._init_env()
        service = ConfigService()
        # 触发 load_config（无参数，内部调用 _resolve_config_path）
        service.load_config(use_cache=False)
        # 验证指向我们控制的路径
        assert service._config_path == self.config_path, (
            f"Expected {self.config_path}, got {service._config_path}"
        )
        return service

    def test_real_app_flow_preserves_locations(self):
        """精确模拟真实 App 流程：add equipment copy → save → reload_config → clear_cache → get_config_value("test.locations")"""
        service = self._make_service()

        # 1. 模拟 ConfigDialog.__init__: 深拷贝
        working_data = copy.deepcopy(service.get_config_value(""))

        # 验证初始状态
        orig_equipment = working_data.get("test", {}).get("equipment", {})
        orig_locations = working_data.get("test", {}).get("locations", [])
        assert len(orig_equipment) == 7
        assert len(orig_locations) == 7

        # 2. 模拟 copy equipment
        source_key = "BOEDT.Qual"
        source_info = copy.deepcopy(orig_equipment[source_key])
        new_key = source_key + " (Copy)"
        working_data.setdefault("test", {})["equipment"][new_key] = source_info

        # 3. 模拟 _on_save: collect_data → replace_all_config → save_config
        #    先重新生成 locations
        test = working_data["test"]
        equipment = test["equipment"]
        locations = []
        for loc_key, info in equipment.items():
            eq = info.get("testEquipment", "")
            parts = loc_key.split(".")
            if len(parts) == 2:
                site, lab = parts
                model = eq.replace("NEWARE Battery Testing System ", "").strip()
                lab_display = lab + "." if lab == "Qual" else lab
                locations.append(f"{model} ({lab_display}), {site}")
            else:
                locations.append(loc_key)
        test["locations"] = locations
        test["equipment"] = equipment

        service.replace_all_config(working_data)
        save_ok = service.save_config()
        assert save_ok, "save_config() returned False!"

        # 验证文件确实包含新条目
        saved = json.loads(self.config_path.read_text(encoding="utf-8"))
        assert any("Copy" in loc for loc in saved.get("test", {}).get("locations", [])), (
            "Saved file on disk is missing the new location"
        )

        # 4. 模拟 ConfigManager.reload_config():
        #    第一步: _config_service.reload_config()
        service.reload_config()
        assert service._config_manager.is_loaded()

        # 此时 locations 应该包含新条目
        locations_after_reload = service.get_config_value("test.locations", [])
        print(
            f"After reload_config(), locations ({len(locations_after_reload)}): {locations_after_reload}"
        )
        assert any("Copy" in loc for loc in locations_after_reload), (
            f"After reload_config(), locations missing copy: {locations_after_reload}"
        )

        # 5. 模拟 ConfigManager.reload_config() 的第二步: _initialize_config() → clear_cache()
        service.clear_cache()
        assert not service._config_manager.is_loaded()

        # 6. 模拟 init_combobox() → get_config("TestConfig/TesterLocation")
        #    → get_config_value("test.locations") → 内部触发 load_config()
        locations_final = service.get_config_value("test.locations", [])
        print(f"After clear_cache+load, locations ({len(locations_final)}): {locations_final}")
        assert any("Copy" in loc for loc in locations_final), (
            f"Final locations missing copy: {locations_final}"
        )
