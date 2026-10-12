"""测试配置编辑页面"""

from PyQt6 import QtWidgets as QW

from battery_analysis.i18n.language_manager import _
from battery_analysis.main.ui_components.config_dialog.list_editor import _ListEditor


class _TestConfigPage(QW.QWidget):
    """测试配置编辑页面"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog

        layout = QW.QVBoxLayout(self)
        self._list_tested_by = _ListEditor(_("Tested By"))
        layout.addWidget(self._list_tested_by)
        layout.addStretch()

    @staticmethod
    def _location_from_equipment(loc_key: str, test_equipment: str) -> str:
        parts = loc_key.split(".")
        if len(parts) != 2:
            return loc_key
        site, lab = parts
        prefix = "NEWARE Battery Testing System "
        model = (
            test_equipment[len(prefix) :].strip()
            if test_equipment.startswith(prefix)
            else test_equipment.strip()
        )
        lab_display = lab + "." if lab == "Qual" else lab
        return f"{model} ({lab_display}), {site}"

    def load_data(self, data: dict) -> None:
        # Tester locations 从 equipment 数据自动生成
        equipment = self._dialog._working_data.get("test", {}).get("equipment", {})
        locations = []
        for loc_key, info in equipment.items():
            locations.append(self._location_from_equipment(loc_key, info.get("testEquipment", "")))
        self._dialog._working_data.setdefault("test", {})["locations"] = locations
        self._list_tested_by.set_items(data.get("testedBy", []))

    def collect_data(self) -> None:
        test = self._dialog._working_data.setdefault("test", {})
        equipment = test.get("equipment", {})
        locations = []
        for loc_key, info in equipment.items():
            locations.append(self._location_from_equipment(loc_key, info.get("testEquipment", "")))
        test["locations"] = locations
        test["testedBy"] = self._list_tested_by.items()
