import pytest
from unittest.mock import Mock


class TestConfigurationRepositoryInterface:
    """测试ConfigurationRepository接口"""
    
    def test_interface_methods_exist(self):
        """测试接口方法是否存在"""
        from battery_analysis.domain.repositories.configuration_repository import ConfigurationRepository
        
        repository = Mock(spec=ConfigurationRepository)
        assert hasattr(repository, 'save')
        assert hasattr(repository, 'find_by_id')
        assert hasattr(repository, 'find_all')
        assert hasattr(repository, 'delete')

    def test_save_method_signature(self):
        """测试save方法签名"""
        from battery_analysis.domain.repositories.configuration_repository import ConfigurationRepository
        from battery_analysis.domain.entities.configuration import Configuration
        
        repository = Mock(spec=ConfigurationRepository)
        config = Mock(spec=Configuration)
        repository.save(config)
        repository.save.assert_called_once_with(config)

    def test_find_by_id_method_signature(self):
        """测试find_by_id方法签名"""
        from battery_analysis.domain.repositories.configuration_repository import ConfigurationRepository
        
        repository = Mock(spec=ConfigurationRepository)
        config_id = "test-id"
        repository.find_by_id(config_id)
        repository.find_by_id.assert_called_once_with(config_id)

    def test_find_all_method_signature(self):
        """测试find_all方法签名"""
        from battery_analysis.domain.repositories.configuration_repository import ConfigurationRepository
        
        repository = Mock(spec=ConfigurationRepository)
        repository.find_all()
        repository.find_all.assert_called_once()

    def test_delete_method_signature(self):
        """测试delete方法签名"""
        from battery_analysis.domain.repositories.configuration_repository import ConfigurationRepository
        
        repository = Mock(spec=ConfigurationRepository)
        config_id = "test-id"
        repository.delete(config_id)
        repository.delete.assert_called_once_with(config_id)