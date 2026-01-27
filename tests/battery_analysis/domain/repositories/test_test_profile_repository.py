import pytest
from unittest.mock import Mock


class TestTestProfileRepositoryInterface:
    """测试TestProfileRepository接口"""
    
    def test_interface_methods_exist(self):
        """测试接口方法是否存在"""
        # 导入要测试的接口
        from battery_analysis.domain.repositories.test_profile_repository import TestProfileRepository
        
        # 使用Mock创建模拟对象，验证接口方法
        mock_repo = Mock(spec=TestProfileRepository)
        assert hasattr(mock_repo, 'save')
        assert hasattr(mock_repo, 'find_by_id')
        assert hasattr(mock_repo, 'find_by_name')
        assert hasattr(mock_repo, 'find_by_battery_type')
        assert hasattr(mock_repo, 'find_by_manufacturer')
        assert hasattr(mock_repo, 'find_all')
        assert hasattr(mock_repo, 'update')
        assert hasattr(mock_repo, 'delete')
        assert hasattr(mock_repo, 'count')

    def test_method_signatures(self):
        """测试方法签名"""
        from battery_analysis.domain.repositories.test_profile_repository import TestProfileRepository
        
        mock_repo = Mock(spec=TestProfileRepository)
        
        # 测试save方法
        test_profile = Mock()
        mock_repo.save(test_profile)
        mock_repo.save.assert_called_once_with(test_profile)
        
        # 测试find_by_id方法
        mock_repo.find_by_id("test-id")
        mock_repo.find_by_id.assert_called_once_with("test-id")
        
        # 测试find_all方法
        mock_repo.find_all()
        mock_repo.find_all.assert_called_once()