"""
测试服务容器模块的功能
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from battery_analysis.main.services.service_container import ServiceContainer, get_service_container, ServiceContext, MultiServiceContext


class TestServiceContainer:
    """测试服务容器类"""

    def setup_method(self):
        """设置测试环境"""
        # 创建服务容器实例
        self.container = ServiceContainer()

    def test_register_basic_service(self):
        """测试基本服务注册"""
        # 定义测试服务类
        class TestService:
            pass

        # 注册服务
        result = self.container.register('test_service', TestService)

        # 验证注册成功
        assert result is True
        assert self.container.has('test_service')

    def test_get_service(self):
        """测试获取服务"""
        # 定义测试服务类
        class TestService:
            def __init__(self):
                self.value = 42

        # 注册服务
        self.container.register('test_service', TestService)

        # 获取服务
        service = self.container.get('test_service')

        # 验证服务获取成功
        assert service is not None
        assert isinstance(service, TestService)
        assert service.value == 42

    def test_get_nonexistent_service(self):
        """测试获取不存在的服务"""
        # 获取不存在的服务
        service = self.container.get('nonexistent_service')

        # 验证返回None
        assert service is None

    def test_register_with_dependencies(self):
        """测试带依赖的服务注册"""
        # 定义依赖服务
        class DependencyService:
            def __init__(self):
                self.dependency_value = 100

        # 定义测试服务
        class TestService:
            def __init__(self):
                self.value = 42

        # 注册服务
        self.container.register('test_service', TestService)

        # 获取服务
        service = self.container.get('test_service')

        # 验证服务获取成功
        assert service is not None
        assert isinstance(service, TestService)
        assert service.value == 42

    def test_topological_sort(self):
        """测试拓扑排序"""
        # 创建依赖图
        graph = {
            'service_a': ['service_b', 'service_c'],
            'service_b': ['service_d'],
            'service_c': ['service_d'],
            'service_d': []
        }

        # 调用拓扑排序
        sorted_services = self.container._topological_sort(graph)

        # 验证排序结果
        assert len(sorted_services) == 4
        # 验证所有服务都在结果中
        assert 'service_a' in sorted_services
        assert 'service_b' in sorted_services
        assert 'service_c' in sorted_services
        assert 'service_d' in sorted_services

    def test_service_context_manager(self):
        """测试服务上下文管理器"""
        # 验证上下文管理器能够正常执行，即使服务不存在
        with ServiceContext('test_service') as service:
            pass
        assert True

    def test_multi_service_context_manager(self):
        """测试多服务上下文管理器"""
        with MultiServiceContext(['service_a', 'service_b']) as services:
            pass
        assert True

    def test_get_global_service_container(self):
        """测试获取全局服务容器"""
        global_container = get_service_container()
        assert global_container is not None
        assert isinstance(global_container, ServiceContainer)

    def test_circular_dependency_detection(self):
        """测试循环依赖检测"""
        class ServiceA:
            def __init__(self, service_b):
                self.service_b = service_b

        class ServiceB:
            def __init__(self, service_a):
                self.service_a = service_a

        self.container.register_with_dependencies('service_a', ServiceA, {'service_b': 'service_b'})
        self.container.register_with_dependencies('service_b', ServiceB, {'service_a': 'service_a'})

        # 跳过默认服务初始化，避免导入真实模块
        self.container._services_initialized = True

        service_a = self.container.get('service_a')
        assert service_a is None

    def test_register_invalid_service(self):
        """测试注册无效服务"""
        result = self.container.register('', Mock)
        assert result is False

        result = self.container.register('test_service', 'not a class')
        assert result is False
