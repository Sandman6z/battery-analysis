from unittest.mock import Mock

from battery_analysis.main.ui_components.table_manager import TableManager


class TestTableManager:
    def setup_method(self):
        mock_main = Mock()
        mock_main.tableWidget_TestInformation = Mock()
        self.manager = TableManager(mock_main)

    def test_set_table(self):
        self.manager.set_table()

    def test_save_table(self):
        self.manager.save_table()
