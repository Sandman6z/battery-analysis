from unittest.mock import Mock, patch
from battery_analysis.infrastructure.services.battery_analysis_service_impl import BatteryAnalysisServiceImpl
from battery_analysis.domain.entities.battery import Battery


class TestInfrastructureBatteryAnalysisServiceImpl:
    def setup_method(self):
        self.service = BatteryAnalysisServiceImpl()

    def _make_test_battery(self):
        from datetime import datetime
        return Battery(
            model_number="M001",
            manufacturer="Test",
            serial_number="SN001",
            battery_type="Li-ion",
            nominal_capacity=2.0,
            nominal_voltage=3.7,
            max_voltage=4.2,
            min_voltage=3.0,
            max_current=5.0,
            weight=0.5,
            production_date=datetime(2024, 1, 1)
        )

    def test_validate_battery_data(self):
        battery = self._make_test_battery()
        result = self.service.validate_battery_data(battery)
        assert isinstance(result, dict)
        assert result["valid"] is True

    def test_calculate_battery_health(self):
        battery = self._make_test_battery()
        result = self.service.calculate_battery_health(battery)
        assert result.health_status == "good"

    def test_get_cache_stats(self):
        result = self.service.get_cache_stats()
        assert isinstance(result, dict)
        assert "hits" in result
        assert "misses" in result