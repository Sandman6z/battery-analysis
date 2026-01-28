import pytest
from unittest.mock import Mock


class TestConfigurationRepositoryInterface:
    """测试ConfigurationRepository接口"""
    
    def test_interface_methods_exist(self):
        """测试接口方法是否存在"""
        from battery_analysis.domain.repositories.configuration_repository import ConfigurationRepository
        
        repository = Mock(spec=ConfigurationRepository)
        assert hasattr(repository, 'load')
        assert hasattr(repository, 'save')
        assert hasattr(repository, 'reset_to_default')

    def test_save_method_signature(self):
        """测试save方法签名"""
        from battery_analysis.domain.repositories.configuration_repository import ConfigurationRepository
        from battery_analysis.domain.entities.configuration import Configuration
        
        repository = Mock(spec=ConfigurationRepository)
        config = Mock(spec=Configuration)
        repository.save(config)
        repository.save.assert_called_once_with(config)

    def test_load_method_signature(self):
        """测试load方法签名"""
        from battery_analysis.domain.repositories.configuration_repository import ConfigurationRepository
        
        repository = Mock(spec=ConfigurationRepository)
        repository.load()
        repository.load.assert_called_once()

    def test_reset_to_default_method_signature(self):
        """测试reset_to_default方法签名"""
        from battery_analysis.domain.repositories.configuration_repository import ConfigurationRepository
        
        repository = Mock(spec=ConfigurationRepository)
        repository.reset_to_default()
        repository.reset_to_default.assert_called_once()