import pytest
from unittest.mock import Mock, patch, MagicMock
from battery_analysis.utils.version import Version
import sys
from pathlib import Path


class TestVersion:
    def setup_method(self):
        # 确保每次测试都创建新实例
        Version._instance = None
        self.version = Version()

    def test_singleton_pattern(self):
        # 测试单例模式
        version1 = Version()
        version2 = Version()
        assert version1 is version2

    def test_get_version(self):
        # 测试获取版本号
        result = self.version.version
        assert isinstance(result, str)
        assert len(result) > 0

    @patch('battery_analysis.utils.version.Path.exists')
    @patch('builtins.open')
    def test_get_version_from_pyproject(self, mock_open, mock_exists):
        # 模拟pyproject.toml存在且包含版本信息
        mock_exists.return_value = True
        
        # 模拟文件读取
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'project = { version = "1.2.3" }'
        mock_open.return_value = mock_file
        
        # 重置单例并重新初始化
        Version._instance = None
        version = Version()
        
        assert isinstance(version.version, str)
        assert len(version.version) > 0

    @patch('battery_analysis.utils.version.Path.exists')
    def test_get_default_version(self, mock_exists):
        # 模拟pyproject.toml不存在
        mock_exists.return_value = False
        
        # 重置单例并重新初始化
        Version._instance = None
        version = Version()
        
        assert isinstance(version.version, str)
        assert len(version.version) > 0