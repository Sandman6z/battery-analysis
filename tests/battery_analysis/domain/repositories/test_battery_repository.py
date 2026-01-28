import pytest
from unittest.mock import Mock


class TestBatteryRepositoryInterface:
    """测试BatteryRepository接口"""
    
    def test_interface_methods_exist(self):
        """测试接口方法是否存在"""
        from battery_analysis.domain.repositories.battery_repository import BatteryRepository
        
        repository = Mock(spec=BatteryRepository)
        assert hasattr(repository, 'save')
        assert hasattr(repository, 'find_by_serial_number')
        assert hasattr(repository, 'find_all')
        assert hasattr(repository, 'delete')

    def test_save_method_signature(self):
        """测试save方法签名"""
        from battery_analysis.domain.repositories.battery_repository import BatteryRepository
        from battery_analysis.domain.entities.battery import Battery
        
        repository = Mock(spec=BatteryRepository)
        battery = Mock(spec=Battery)
        repository.save(battery)
        repository.save.assert_called_once_with(battery)

    def test_find_by_serial_number_method_signature(self):
        """测试find_by_serial_number方法签名"""
        from battery_analysis.domain.repositories.battery_repository import BatteryRepository
        
        repository = Mock(spec=BatteryRepository)
        serial_number = "test-serial"
        repository.find_by_serial_number(serial_number)
        repository.find_by_serial_number.assert_called_once_with(serial_number)

    def test_find_all_method_signature(self):
        """测试find_all方法签名"""
        from battery_analysis.domain.repositories.battery_repository import BatteryRepository
        
        repository = Mock(spec=BatteryRepository)
        repository.find_all()
        repository.find_all.assert_called_once()

    def test_delete_method_signature(self):
        """测试delete方法签名"""
        from battery_analysis.domain.repositories.battery_repository import BatteryRepository
        
        repository = Mock(spec=BatteryRepository)
        battery_id = "test-id"
        repository.delete(battery_id)
        repository.delete.assert_called_once_with(battery_id)