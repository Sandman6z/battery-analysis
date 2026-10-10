"""电池配置编辑页面"""

import logging

from PyQt6 import QtWidgets as QW

from battery_analysis.i18n.language_manager import _
from battery_analysis.main.ui_components.config_dialog.list_editor import _ListEditor
from battery_analysis.main.ui_components.config_dialog.rules_editor import _RulesEditor


class _BatteryConfigPage(QW.QWidget):
    """电池配置编辑页面（逐条化编辑，唯一数据源：battery.rules）"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog

        main_layout = QW.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QW.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QW.QFrame.Shape.NoFrame)

        content = QW.QWidget()
        layout = QW.QVBoxLayout(content)

        # ── Test Data Dictionary ──
        dict_group = QW.QGroupBox(_("Test Data Dictionary"))
        dict_layout = QW.QVBoxLayout(dict_group)

        self._list_types = _ListEditor(_("Battery Types"), editable=False)
        dict_layout.addWidget(self._list_types)

        self._rules_editor = _RulesEditor(_("Rules"))
        dict_layout.addWidget(self._rules_editor)

        self._list_construction = _ListEditor(_("Construction Methods"), editable=False)
        dict_layout.addWidget(self._list_construction)

        self._list_spec_method = _ListEditor(_("Specification Methods"), editable=False)
        dict_layout.addWidget(self._list_spec_method)

        self._list_mfrs = _ListEditor(_("Manufacturers"))
        dict_layout.addWidget(self._list_mfrs)

        layout.addWidget(dict_group)

        # ── Test Parameters ──
        params_group = QW.QGroupBox(_("Test Parameters"))
        params_layout = QW.QVBoxLayout(params_group)

        # 脉冲电流档位由 BatteryQualityRequirements_v2.3 §7.1.1 查表自动匹配
        # （文件名 (x-x-xmA) 优先，型号/容量查表兜底），此处只读展示
        self._list_pulse = _ListEditor(_("Pulse Currents"), editable=False)
        self._list_pulse.setToolTip(
            _("Auto-matched from battery rules (BatteryQualityRequirements_v2.3 §7.1.1) — not editable here")
        )
        params_layout.addWidget(self._list_pulse)

        self._list_voltage = _ListEditor(_("Cut-off Voltages"))
        params_layout.addWidget(self._list_voltage)

        layout.addWidget(params_group)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def load_data(self, data: dict) -> None:
        rules = data.get("rules", [])
        methods = data.get("specificationMethods", [])
        self._list_types.set_items(data.get("types", []))
        self._list_construction.set_items(data.get("constructionMethods", []))
        # 先灌 method 列表再填规则，Spec Method 列的下拉框才能拿到可选项
        self._list_spec_method.set_items(methods)
        self._rules_editor.set_methods(methods)
        self._rules_editor.set_rules(rules)
        self._list_mfrs.set_items(data.get("manufacturers", []))
        self._list_pulse.set_items([str(v) for v in data.get("pulseCurrents", [])])
        self._list_voltage.set_items([str(v) for v in data.get("cutOffVoltages", [])])

    def collect_data(self) -> None:
        battery = self._dialog._working_data.setdefault("battery", {})
        battery["types"] = self._list_types.items()
        battery["constructionMethods"] = self._list_construction.items()
        rules = self._rules_editor.rules()
        battery["rules"] = rules
        battery["specificationMethods"] = self._list_spec_method.items()
        battery["manufacturers"] = self._list_mfrs.items()
        # pulseCurrents 不再从 UI 写回：保持 _working_data 中的既有值
        #（由文件名解析/容量查表自动更新，见 data_processor）
        battery["cutOffVoltages"] = self._parse_float_list(self._list_voltage.items())

    @staticmethod
    def _parse_float_list(raw: list) -> list:
        result = []
        for v in raw:
            try:
                result.append(float(v))
            except ValueError:
                logging.getLogger(__name__).warning("Ignoring non-float value: %s", v)
        return result
