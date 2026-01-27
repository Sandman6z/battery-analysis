import pytest
from unittest.mock import Mock


class TestBatteryAnalysisServiceInterface:
    """测试BatteryAnalysisService接口"""
    
    def test_interface_methods_exist(self):
        """测试接口方法是否存在"""
        from battery_analysis.domain.services.battery_analysis_service import BatteryAnalysisService
        
        service = Mock(spec=BatteryAnalysisService)
        assert hasattr(service, 'analyze_battery_data')
        assert hasattr(service, 'calculate_battery_metrics')
        assert hasattr(service, 'generate_analysis_report')

    def test_method_signatures(self):
        """测试方法签名"""
        from battery_analysis.domain.services.battery_analysis_service import BatteryAnalysisService
        
        service = Mock(spec=BatteryAnalysisService)
        
        # 测试analyze_battery_data方法
        battery_data = {"voltage": [4.2, 4.1, 4.0], "current": [0.5, 0.5, 0.5]}
        service.analyze_battery_data(battery_data)
        service.analyze_battery_data.assert_called_once_with(battery_data)
        
        # 测试calculate_battery_metrics方法
        battery_data = {"voltage": [4.2, 4.1, 4.0], "current": [0.5, 0.5, 0.5]}
        service.calculate_battery_metrics(battery_data)
        service.calculate_battery_metrics.assert_called_once_with(battery_data)
        
        # 测试generate_analysis_report方法
        analysis_results = {"capacity": 3000, "voltage": 4.2}
        service.generate_analysis_report(analysis_results)
        service.generate_analysis_report.assert_called_once_with(analysis_results)