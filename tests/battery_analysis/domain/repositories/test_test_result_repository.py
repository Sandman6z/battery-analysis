import pytest
from unittest.mock import Mock


class TestTestResultRepositoryInterface:
    """测试TestResultRepository接口"""
    
    def test_interface_methods_exist(self):
        """测试接口方法是否存在"""
        from battery_analysis.domain.repositories.test_result_repository import TestResultRepository
        
        repository = Mock(spec=TestResultRepository)
        assert hasattr(repository, 'save')
        assert hasattr(repository, 'find_by_id')
        assert hasattr(repository, 'find_all')
        assert hasattr(repository, 'delete')
        assert hasattr(repository, 'update')
        assert hasattr(repository, 'find_by_battery_serial')
        assert hasattr(repository, 'find_by_date_range')
        assert hasattr(repository, 'count_by_battery_serial')

    def test_method_signatures(self):
        """测试方法签名"""
        from battery_analysis.domain.repositories.test_result_repository import TestResultRepository
        
        repository = Mock(spec=TestResultRepository)
        
        # 测试save方法
        test_result = Mock()
        repository.save(test_result)
        repository.save.assert_called_once_with(test_result)
        
        # 测试find_by_id方法
        result_id = "test-id"
        repository.find_by_id(result_id)
        repository.find_by_id.assert_called_once_with(result_id)
        
        # 测试find_all方法
        repository.find_all()
        repository.find_all.assert_called_once()
        
        # 测试delete方法
        repository.delete(result_id)
        repository.delete.assert_called_once_with(result_id)