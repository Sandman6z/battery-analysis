import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.numeric_utils import np_mean, np_std, np_max, np_min, np_med


class TestNumericUtils:
    def test_np_mean(self):
        # 测试非空列表
        test_list = [1, 2, 3, 4, 5]
        result = np_mean(test_list)
        assert isinstance(result, float)
        assert result == 3.0
        
        # 测试空列表
        empty_list = []
        result = np_mean(empty_list)
        assert isinstance(result, float)
        assert result == 0

    def test_np_std(self):
        # 测试非空列表（元素数>1）
        test_list = [1, 2, 3, 4, 5]
        result = np_std(test_list)
        assert isinstance(result, float)
        # 验证结果是否在合理范围内（预期约为1.414）
        assert 1.41 < result < 1.42
        
        # 测试只有一个元素的列表
        single_element_list = [5]
        result = np_std(single_element_list)
        assert isinstance(result, float)
        assert result == 0
        
        # 测试空列表
        empty_list = []
        result = np_std(empty_list)
        assert isinstance(result, float)
        assert result == 0

    def test_np_max(self):
        # 测试非空列表
        test_list = [1, 3, 5, 2, 4]
        result = np_max(test_list)
        assert isinstance(result, float)
        assert result == 5.0
        
        # 测试空列表
        empty_list = []
        result = np_max(empty_list)
        assert isinstance(result, float)
        assert result == 0

    def test_np_min(self):
        # 测试非空列表
        test_list = [1, 3, 5, 2, 4]
        result = np_min(test_list)
        assert isinstance(result, float)
        assert result == 1.0
        
        # 测试空列表
        empty_list = []
        result = np_min(empty_list)
        assert isinstance(result, float)
        assert result == 0

    def test_np_med(self):
        # 测试非空列表（奇数长度）
        test_list_odd = [1, 2, 3, 4, 5]
        result_odd = np_med(test_list_odd)
        assert isinstance(result_odd, float)
        assert result_odd == 3.0
        
        # 测试非空列表（偶数长度）
        test_list_even = [1, 2, 3, 4]
        result_even = np_med(test_list_even)
        assert isinstance(result_even, float)
        assert result_even == 2.5
        
        # 测试空列表
        empty_list = []
        result_empty = np_med(empty_list)
        assert isinstance(result_empty, float)
        assert result_empty == 0