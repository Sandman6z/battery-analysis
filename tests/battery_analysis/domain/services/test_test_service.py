import pytest
from unittest.mock import Mock


class TestTestServiceInterface:
    """测试TestService接口"""
    
    def test_interface_methods_exist(self):
        """测试接口方法是否存在"""
        from battery_analysis.domain.services.test_service import TestService
        
        service = Mock(spec=TestService)
        assert hasattr(service, 'create_test_result')
        assert hasattr(service, 'update_test_result')
        assert hasattr(service, 'validate_test_profile')
        assert hasattr(service, 'generate_test_id')
        assert hasattr(service, 'get_test_summary')
        assert hasattr(service, 'calculate_test_statistics')
        assert hasattr(service, 'group_test_results_by_criteria')

    def test_method_signatures(self):
        """测试方法签名"""
        from battery_analysis.domain.services.test_service import TestService
        
        service = Mock(spec=TestService)
        
        # 测试create_test_result方法
        battery = Mock()
        test_profile = Mock()
        test_data = {"voltage": [4.2, 4.1, 4.0], "current": [0.5, 0.5, 0.5]}
        operator = "Test Operator"
        equipment = "Test Equipment"
        service.create_test_result(battery, test_profile, test_data, operator, equipment)
        service.create_test_result.assert_called_once_with(battery, test_profile, test_data, operator, equipment)
        
        # 测试update_test_result方法
        test_result = Mock()
        test_data = {"voltage": [4.2, 4.1, 4.0], "current": [0.5, 0.5, 0.5]}
        service.update_test_result(test_result, test_data)
        service.update_test_result.assert_called_once_with(test_result, test_data)
        
        # 测试validate_test_profile方法
        test_profile = Mock()
        service.validate_test_profile(test_profile)
        service.validate_test_profile.assert_called_once_with(test_profile)
        
        # 测试generate_test_id方法
        battery = Mock()
        service.generate_test_id(battery)
        service.generate_test_id.assert_called_once_with(battery)
        
        # 测试get_test_summary方法
        test_results = [Mock()]
        service.get_test_summary(test_results)
        service.get_test_summary.assert_called_once_with(test_results)
        
        # 测试calculate_test_statistics方法
        test_results = [Mock()]
        service.calculate_test_statistics(test_results)
        service.calculate_test_statistics.assert_called_once_with(test_results)
        
        # 测试group_test_results_by_criteria方法
        test_results = [Mock()]
        criteria = "date"
        service.group_test_results_by_criteria(test_results, criteria)
        service.group_test_results_by_criteria.assert_called_once_with(test_results, criteria)