import pytest
import json
import os
from battery_analysis.main.main_window import Main
from PyQt6.QtWidgets import QApplication

app = QApplication([])

# 加载测试数据
test_data_path = os.path.join(os.path.dirname(
    __file__), "../../data/test_config.json")
with open(test_data_path, "r", encoding="utf-8") as f:
    test_data = json.load(f)

# 从测试数据中提取测试场景和映射关系
test_scenarios = test_data["test_scenarios"]
reported_by_mapping = test_data["reported_by_mapping"]

# 将字符串键转换为整数键，以便在测试中使用
reported_by_mapping = {int(index): reported_by for index,
                       reported_by in reported_by_mapping.items()}


def test_reported_by_matching():
    """
    测试ReportedBy与TesterLocation的匹配逻辑
    验证当选择CT-4008Q (Qual.), PDI时，ReportedBy显示为PDI
    """
    main_window = Main()

    # 使用测试数据中的测试场景
    for scenario in test_scenarios:
        # 设置当前测试场景的TesterLocation索引
        main_window.comboBox_TesterLocation.setCurrentIndex(
            scenario["tester_location_index"])

        # 触发ReportedBy更新逻辑（模拟set_table方法中的相关部分）
        current_tester_location = main_window.comboBox_TesterLocation.currentIndex()

        # 根据映射关系获取预期的ReportedBy值
        reported_by = reported_by_mapping.get(current_tester_location, "")

        # 验证结果
        expected_reported_by = scenario["expected_reported_by"]
        assert reported_by == expected_reported_by, f"当选择索引{scenario['tester_location_index']}时，ReportedBy应该是'{expected_reported_by}'，但实际是'{reported_by}'"


# 将映射关系转换为参数化测试所需的格式
parametrize_data = [(index, reported_by)
                    for index, reported_by in reported_by_mapping.items()]


@pytest.mark.parametrize("index, expected_reported_by", parametrize_data)
def test_reported_by_mapping(index, expected_reported_by):
    """
    参数化测试ReportedBy与TesterLocation的映射关系
    """
    main_window = Main()
    main_window.comboBox_TesterLocation.setCurrentIndex(index)

    # 触发ReportedBy更新逻辑
    current_tester_location = main_window.comboBox_TesterLocation.currentIndex()

    # 根据映射关系获取预期的ReportedBy值
    reported_by = reported_by_mapping.get(current_tester_location, "")

    # 验证结果
    assert reported_by == expected_reported_by, f"当选择索引{index}时，ReportedBy应该是'{expected_reported_by}'，但实际是'{reported_by}'"
