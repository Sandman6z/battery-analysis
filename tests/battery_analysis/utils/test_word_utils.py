import pytest
from unittest.mock import Mock, patch, MagicMock
from battery_analysis.utils.word_utils import table_set_bg_color, get_item, add_hyperlink


class TestWordUtils:
    def test_table_set_bg_color(self):
        # 测试表格单元格背景色设置
        mock_cell = Mock()
        mock_tc = Mock()
        mock_tcPr = Mock()
        mock_cell._tc = mock_tc
        mock_tc.get_or_add_tcPr.return_value = mock_tcPr
        
        table_set_bg_color(mock_cell, "FF0000")
        assert mock_tc.get_or_add_tcPr.called
        assert mock_tcPr.append.called

    def test_get_item(self):
        # 测试获取配置项
        mock_config = Mock()
        mock_config.has_section.return_value = True
        mock_config.has_option.return_value = True
        mock_config.get.return_value = "value1,value2,value3"
        
        result = get_item(mock_config, "section", "item")
        assert isinstance(result, str)
        assert "value1" in result

    def test_get_item_nonexistent_section(self):
        # 测试获取不存在的section
        mock_config = Mock()
        mock_config.has_section.return_value = False
        
        result = get_item(mock_config, "nonexistent_section", "item")
        assert result == ""

    def test_get_item_nonexistent_option(self):
        # 测试获取不存在的option
        mock_config = Mock()
        mock_config.has_section.return_value = True
        mock_config.has_option.return_value = False
        
        result = get_item(mock_config, "section", "nonexistent_item")
        assert result == ""

    def test_add_hyperlink(self):
        # 测试添加超链接
        mock_paragraph = Mock()
        mock_part = Mock()
        mock_paragraph.part = mock_part
        mock_part.relate_to.return_value = "rId1"
        mock_p = Mock()
        mock_paragraph._p = mock_p
        
        add_hyperlink(mock_paragraph, "https://example.com", "Example Link")
        assert mock_part.relate_to.called
        assert mock_p.append.called