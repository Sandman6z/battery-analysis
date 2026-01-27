import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.ui_components.table_manager import TableManager


class TestTableManager:
    def setup_method(self):
        self.manager = TableManager()

    def test_create_table(self):
        data = {"headers": ["Column1", "Column2"], "rows": [[1, 2], [3, 4]]}
        result = self.manager.create_table(data)
        assert result is not None

    def test_update_table(self):
        table_widget = Mock()
        data = {"rows": [[5, 6], [7, 8]]}
        result = self.manager.update_table(table_widget, data)
        assert result is True

    def test_export_table(self):
        table_widget = Mock()
        file_path = "table.csv"
        result = self.manager.export_table(table_widget, file_path)
        assert result is True