import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.temperature_utils import detect_temperature_type_from_xml, is_freezer_temperature, is_room_temperature


class TestTemperatureUtils:
    def test_detect_temperature_type_from_xml_freezer(self):
        # 测试冷冻温度检测
        freezer_xml_path = "path/to/Freezer_Test.xml"
        result = detect_temperature_type_from_xml(freezer_xml_path)
        assert result == "Freezer Temperature"

    def test_detect_temperature_type_from_xml_room(self):
        # 测试常温检测
        room_xml_path = "path/to/Room_Test.xml"
        result = detect_temperature_type_from_xml(room_xml_path)
        assert result == "Room Temperature"

    def test_detect_temperature_type_from_xml_error(self):
        # 测试错误处理
        # 传入None应该返回默认值
        result = detect_temperature_type_from_xml(None)
        assert result == "Room Temperature"

    def test_is_freezer_temperature(self):
        # 测试是否为冷冻温度
        freezer_xml_path = "path/to/Freezer_Test.xml"
        result = is_freezer_temperature(freezer_xml_path)
        assert result is True

        room_xml_path = "path/to/Room_Test.xml"
        result = is_freezer_temperature(room_xml_path)
        assert result is False

    def test_is_room_temperature(self):
        # 测试是否为常温
        room_xml_path = "path/to/Room_Test.xml"
        result = is_room_temperature(room_xml_path)
        assert result is True

        freezer_xml_path = "path/to/Freezer_Test.xml"
        result = is_room_temperature(freezer_xml_path)
        assert result is False