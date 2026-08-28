from unittest.mock import Mock

from battery_analysis.utils.processors.data_utils import (
    detect_outliers,
    filter_data,
    generate_current_type_string,
)


class TestDataUtils:
    def test_filter_data(self):
        """测试数据过滤函数"""
        # 测试数据
        plt_charge_list = [[1, 2, 3, 4, 5]]
        plt_voltage_list = [[4.2, 4.1, 4.0, 3.9, 3.8]]

        # 调用函数
        result_charge, result_voltage = filter_data(plt_charge_list, plt_voltage_list)

        # 验证结果
        assert isinstance(result_charge, list)
        assert isinstance(result_voltage, list)
        assert len(result_charge) == 1
        assert len(result_voltage) == 1

    def test_generate_current_type_string(self):
        """测试生成电流类型字符串函数"""
        # 测试数据
        list_current_level = [500, 1000, 1500]

        # 调用函数
        result = generate_current_type_string(list_current_level)

        # 验证结果
        assert isinstance(result, str)
        assert result == "500-1000-1500"

    def test_detect_outliers(self):
        """测试异常值检测函数"""
        # 测试数据：需要足够的数据量使3σ规则能检测出明显异常值
        data = [5, 6, 5, 7, 6, 5, 6, 7, 5, 6, 100]  # 100是明显异常值
        data_name = "test_data"
        result_index = 10

        # 创建模拟测试结果对象
        mock_test_result = Mock()
        mock_test_result.test_id = "test-001"
        mock_test_result.cycle_count = 1
        test_results = [mock_test_result] * 11

        # 调用函数
        result = detect_outliers(data, data_name, result_index, test_results)

        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0

    def test_filter_data_fallback_no_name_error(self):
        """numpy 转换失败走 fallback 分支时不抛 NameError（修复缺 import logging）"""
        # 'x' 无法 float()，触发 numpy 转换失败 → fallback 分支 → logging.warning
        plt_charge_list = [["1", "x", "2"]]
        plt_voltage_list = [["4", "5", "3.9"]]

        result_charge, result_voltage = filter_data(plt_charge_list, plt_voltage_list)

        assert isinstance(result_charge, list)
        assert result_charge[0][0] == 1.0  # fallback 保留第一个点
