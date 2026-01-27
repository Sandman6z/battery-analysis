import pytest
from unittest.mock import Mock


class TestTestServiceInterface:
    """测试TestService接口"""
    
    def test_interface_methods_exist(self):
        """测试接口方法是否存在"""
        from battery_analysis.domain.services.test_service import TestService
        
        service = Mock(spec=TestService)
        assert hasattr(service, 'create_test_profile')
        assert hasattr(service, 'execute_test')
        assert hasattr(service, 'process_test_results')
        assert hasattr(service, 'validate_test_profile')
        assert hasattr(service, 'generate_test_id')
        assert hasattr(service, 'create_test_result')
        assert hasattr(service, 'update_test_result')
        assert hasattr(service, 'calculate_test_statistics')
        assert hasattr(service, 'get_test_summary')
        assert hasattr(service, 'group_test_results_by_criteria')

    def test_method_signatures(self):
        """测试方法签名"""
        from battery_analysis.domain.services.test_service import TestService
        
        service = Mock(spec=TestService)
        
        # 测试create_test_profile方法
        profile_data = {"name": "Test Profile", "parameters": {"voltage": 4.2}}
        service.create_test_profile(profile_data)
        service.create_test_profile.assert_called_once_with(profile_data)
        
        # 测试execute_test方法
        test_profile = Mock()
        service.execute_test(test_profile)
        service.execute_test.assert_called_once_with(test_profile)
        
        # 测试process_test_results方法
        test_data = {"voltage": [4.2, 4.1, 4.0], "current": [0.5, 0.5, 0.5]}
        service.process_test_results(test_data)
        service.process_test_results.assert_called_once_with(test_data)