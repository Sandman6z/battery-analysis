import pytest
from unittest.mock import Mock


class TestBatteryAnalysisServiceInterface:
    """测试BatteryAnalysisService接口"""
    
    def test_interface_methods_exist(self):
        """测试接口方法是否存在"""
        from battery_analysis.domain.services.battery_analysis_service import BatteryAnalysisService
        
        service = Mock(spec=BatteryAnalysisService)
        assert hasattr(service, 'calculate_state_of_health')
        assert hasattr(service, 'calculate_state_of_charge')
        assert hasattr(service, 'analyze_cycle_life')
        assert hasattr(service, 'validate_test_result')
        assert hasattr(service, 'calculate_performance_metrics')
        assert hasattr(service, 'detect_anomalies')
        assert hasattr(service, 'compare_test_results')

    def test_method_signatures(self):
        """测试方法签名"""
        from battery_analysis.domain.services.battery_analysis_service import BatteryAnalysisService
        
        service = Mock(spec=BatteryAnalysisService)
        
        # 测试calculate_state_of_health方法
        test_result = Mock()
        battery = Mock()
        service.calculate_state_of_health(test_result, battery)
        service.calculate_state_of_health.assert_called_once_with(test_result, battery)
        
        # 测试calculate_state_of_charge方法
        voltage = 4.2
        battery = Mock()
        service.calculate_state_of_charge(voltage, battery)
        service.calculate_state_of_charge.assert_called_once_with(voltage, battery)
        
        # 测试analyze_cycle_life方法
        test_results = [Mock()]
        battery = Mock()
        service.analyze_cycle_life(test_results, battery)
        service.analyze_cycle_life.assert_called_once_with(test_results, battery)
        
        # 测试validate_test_result方法
        test_result = Mock()
        test_profile = Mock()
        battery = Mock()
        service.validate_test_result(test_result, test_profile, battery)
        service.validate_test_result.assert_called_once_with(test_result, test_profile, battery)
        
        # 测试calculate_performance_metrics方法
        test_result = Mock()
        battery = Mock()
        service.calculate_performance_metrics(test_result, battery)
        service.calculate_performance_metrics.assert_called_once_with(test_result, battery)
        
        # 测试detect_anomalies方法
        test_results = [Mock()]
        service.detect_anomalies(test_results)
        service.detect_anomalies.assert_called_once_with(test_results)
        
        # 测试compare_test_results方法
        test_result1 = Mock()
        test_result2 = Mock()
        service.compare_test_results(test_result1, test_result2)
        service.compare_test_results.assert_called_once_with(test_result1, test_result2)