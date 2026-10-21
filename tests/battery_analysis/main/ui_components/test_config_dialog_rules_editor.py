"""_RulesEditor 的 Spec Method 列必须是下拉框（可选项来自 battery.specificationMethods）"""

from PyQt6.QtWidgets import QApplication, QComboBox

from battery_analysis.main.ui_components.config_dialog import (
    RULE_COLUMNS,
    SPEC_METHOD_COL,
    _RulesEditor,
)

METHODS = ["1S1P", "1S2P", "2S1P"]


class TestRulesEditorSpecMethodCombo:
    def setup_method(self):
        if QApplication.instance() is None:
            self._test_app = QApplication([])
        self.editor = _RulesEditor()
        self.editor.set_methods(METHODS)

    def test_battery_page_has_flat_editors(self):
        from unittest.mock import Mock

        from PyQt6.QtWidgets import QGroupBox

        from battery_analysis.main.ui_components.config_dialog.battery_config_page import (
            _BatteryConfigPage,
        )

        page = _BatteryConfigPage(Mock())
        assert page._rules_editor.parentWidget() is page._list_mfrs.parentWidget()
        assert not isinstance(page._rules_editor.parentWidget(), QGroupBox)
        page.load_data({"rules": ["CP5022121/1S1P/3500/3500/85%/10"],
                        "specificationMethods": METHODS, "manufacturers": ["Ewin"]})
        assert page._rules_editor.rules() == ["CP5022121/1S1P/3500/3500/85%/10"]
        assert page._list_mfrs.items() == ["Ewin"]

    def test_dictionary_is_the_tab_name(self):
        from unittest.mock import Mock

        from PyQt6.QtWidgets import QMainWindow

        from battery_analysis.i18n.language_manager import _
        from battery_analysis.main.ui_components.config_dialog import ConfigDialog

        window = QMainWindow()
        window._get_service = Mock(return_value=Mock())
        dialog = ConfigDialog(window)
        assert dialog._tab_widget.tabText(0) == _("Test Data Dictionary")
        dialog.close()
        window.close()

    def test_spec_method_col_is_a_constant(self):
        assert RULE_COLUMNS[SPEC_METHOD_COL] == "Spec Method"

    def test_filled_rule_gets_readonly_combo(self):
        self.editor.set_rules(["CR2450/1S1P/600/550/380/1.0"])
        table = self.editor._table_coin
        widget = table.cellWidget(0, SPEC_METHOD_COL)
        assert isinstance(widget, QComboBox)
        assert not widget.isEditable()
        assert widget.currentText() == "1S1P"
        assert widget.count() == len(METHODS)
        # 单元格 item 已被下拉框取代，不可再手输
        assert table.item(0, SPEC_METHOD_COL) is None

    def test_combo_options_come_from_methods(self):
        self.editor.set_rules(["CR2450/1S1P/600/550/380/1.0"])
        widget = self.editor._table_coin.cellWidget(0, SPEC_METHOD_COL)
        assert [widget.itemText(i) for i in range(widget.count())] == METHODS

    def test_rules_roundtrip_preserves_value(self):
        rules = ["CR2450/1S1P/600/550/380/1.0", "CP305050/1S2P/2000/2000/80%/10"]
        self.editor.set_rules(rules)
        assert self.editor.rules() == rules

    def test_unknown_method_kept_visible_not_dropped(self):
        # 规则里的 method 不在方法列表中：仍要显示出来，避免静默丢数据
        self.editor.set_rules(["CR2450/1S9P/600/550/380/1.0"])
        widget = self.editor._table_coin.cellWidget(0, SPEC_METHOD_COL)
        assert widget.currentText() == "1S9P"

    def test_add_row_installs_combo(self):
        self.editor._add_row()  # 默认在 Coin Cell 分栏
        table = self.editor._table_coin
        widget = table.cellWidget(0, SPEC_METHOD_COL)
        assert isinstance(widget, QComboBox)
        widget.setCurrentText("2S1P")
        parts = self.editor.rules()[0].split("/")
        assert parts[SPEC_METHOD_COL] == "2S1P"

    def test_set_methods_refreshes_existing_rows(self):
        self.editor.set_rules(["CR2450/1S1P/600/550/380/1.0"])
        self.editor.set_methods(["1S1P", "4S1P"])
        widget = self.editor._table_coin.cellWidget(0, SPEC_METHOD_COL)
        assert [widget.itemText(i) for i in range(widget.count())] == ["1S1P", "4S1P"]
        assert widget.currentText() == "1S1P"  # 已有值不丢
