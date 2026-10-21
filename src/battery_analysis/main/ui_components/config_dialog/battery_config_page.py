"""电池配置编辑页面"""

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
        # Battery Types / Construction Methods 不再在 UI 展示：
        # 值固定（Coin Cell/Pouch Cell、Spiral/Laminate），由主窗口下拉框
        # 代码兜底 + 规格自动匹配控制（check_specification），
        # 数据保留在 config.json 中继续生效
        # Specification Methods 同样移出 UI（只读词表）：仅作文件名
        # 匹配与 Rules 表格 Spec Method 列的下拉选项，由
        # load_data 从配置读入后直接喂给 _rules_editor
        self._rules_editor = _RulesEditor(_("Rules"))
        layout.addWidget(self._rules_editor)

        self._list_mfrs = _ListEditor(_("Manufacturers"))
        layout.addWidget(self._list_mfrs)

        # ── Test Parameters ──
        # 原 "Test Parameters" 组已整体移出 UI（数据保留在 config.json 生效）：
        # - 脉冲电流档位（pulseCurrents）：由 BatteryQualityRequirements_v2.3
        #   §7.1.1 查表自动匹配（文件名 (x-x-xmA) 优先，型号/容量查表兜底）
        # - 截止电压档位（cutOffVoltages）：分析网格由测试协议固定
        #   （标准 6 档 + Hermes 2.5V + 超集档），无需手动调整；
        #   配置为空时初始化步骤回退 DEFAULT_CONFIG（见 battery_config_initialization_step）
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def load_data(self, data: dict) -> None:
        rules = data.get("rules", [])
        methods = data.get("specificationMethods", [])
        # 方法词表不展示 UI，直接灌给规则编辑器，
        # Spec Method 列的下拉框才能拿到可选项
        self._rules_editor.set_methods(methods)
        self._rules_editor.set_rules(rules)
        self._list_mfrs.set_items(data.get("manufacturers", []))

    def collect_data(self) -> None:
        battery = self._dialog._working_data.setdefault("battery", {})
        # types / constructionMethods 不从 UI 写回：保持 _working_data 中的
        # 既有值（固定值，由代码兜底控制，见 ui_manager.init_combobox）
        rules = self._rules_editor.rules()
        battery["rules"] = rules
        # specificationMethods / types / constructionMethods / pulseCurrents /
        # cutOffVoltages 均不从 UI 写回：保持 _working_data 中的既有值
        #（词表/固定档位，见上方注释及 data_processor、初始化步骤）
        battery["manufacturers"] = self._list_mfrs.items()
