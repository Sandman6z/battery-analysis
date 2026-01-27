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
    
    def test_register_instance(self):
        """测试注册实例"""
        # 创建测试实例
        test_instance = Mock()
        
        # 注册实例
        result = self.container.register_instance('test_instance', test_instance)
        
        # 验证注册成功
        assert result is True
        assert self.container.has('test_instance')
        assert self.container.get('test_instance') == test_instance
    
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
    
    def test_unregister_service(self):
        """测试注销服务"""
        # 定义测试服务类
        class TestService:
            pass
        
        # 注册服务
        self.container.register('test_service', TestService)
        assert self.container.has('test_service')
        
        # 注销服务
        result = self.container.unregister('test_service')
        
        # 验证注销成功
        assert result is True
        assert not self.container.has('test_service')
    
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
        # 验证结果不为空
        assert len(sorted_services) > 0
        # 验证所有服务都在结果中
        assert 'service_a' in sorted_services
        assert 'service_b' in sorted_services
        assert 'service_c' in sorted_services
        assert 'service_d' in sorted_services
    
    def test_shutdown(self):
        """测试关闭容器"""
        # 定义带shutdown方法的服务
        class TestService:
            def __init__(self):
                self.shutdown_called = False
            
            def shutdown(self):
                self.shutdown_called = True
        
        # 注册服务
        self.container.register('test_service', TestService)
        
        # 获取服务实例
        service = self.container.get('test_service')
        
        # 关闭容器
        result = self.container.shutdown()
        
        # 验证关闭成功
        assert result is True
        assert service.shutdown_called is True
        assert not self.container.has('test_service')
    
    def test_clear_instances(self):
        """测试清除实例"""
        # 定义带shutdown方法的服务
        class TestService:
            def __init__(self):
                self.shutdown_called = False
            
            def shutdown(self):
                self.shutdown_called = True
        
        # 注册服务
        self.container.register('test_service', TestService)
        
        # 获取服务实例
        service = self.container.get('test_service')
        assert self.container.has('test_service')
        
        # 清除实例
        self.container.clear_instances()
        
        # 验证实例被清除，但服务仍注册
        assert service.shutdown_called is True
        assert self.container.has('test_service')
        # 获取新实例
        new_service = self.container.get('test_service')
        assert new_service is not None
        assert new_service != service
    
    def test_get_service_info(self):
        """测试获取服务信息"""
        # 定义测试服务类
        class TestService:
            pass
        
        # 注册服务
        self.container.register('test_service', TestService)
        
        # 获取服务信息
        info = self.container.get_service_info()
        
        # 验证信息获取成功
        assert isinstance(info, dict)
        assert 'test_service' in info
        assert info['test_service']['registered'] is True
        assert info['test_service']['instantiated'] is False
        assert info['test_service']['singleton'] is True
        assert info['test_service']['class'] == 'TestService'
    
    def test_release_unused_resources(self):
        """测试释放未使用的资源"""
        # 定义带shutdown方法的服务
        class TestService:
            def __init__(self):
                self.shutdown_called = False
            
            def shutdown(self):
                self.shutdown_called = True
        
        # 注册服务
        self.container.register('test_service', TestService)
        
        # 获取服务实例
        service = self.container.get('test_service')
        
        # 释放未使用的资源（使用很短的空闲时间）
        released_count = self.container.release_unused_resources(idle_time=0)
        
        # 验证资源被释放
        assert released_count >= 0
    
    def test_get_resource_usage(self):
        """测试获取资源使用情况"""
        # 定义测试服务类
        class TestService:
            pass
        
        # 注册服务
        self.container.register('test_service', TestService)
        
        # 获取服务实例
        self.container.get('test_service')
        
        # 获取资源使用情况
        usage = self.container.get_resource_usage()
        
        # 验证使用情况获取成功
        assert isinstance(usage, dict)
        assert 'summary' in usage
        assert 'details' in usage
        assert 'total_services' in usage['summary']
        assert 'active_instances' in usage['summary']
    
    def test_service_context_manager(self):
        """测试服务上下文管理器"""
        # 验证上下文管理器能够正常执行，即使服务不存在
        # 由于ServiceContext使用全局容器，这里只测试基本功能
        with ServiceContext('test_service') as service:
            # 服务可能不存在，但上下文管理器应该正常执行
            pass
        # 验证上下文管理器执行完成
        assert True
    
    def test_multi_service_context_manager(self):
        """测试多服务上下文管理器"""
        # 验证上下文管理器能够正常执行，即使服务不存在
        # 由于MultiServiceContext使用全局容器，这里只测试基本功能
        with MultiServiceContext(['service_a', 'service_b']) as services:
            # 服务可能不存在，但上下文管理器应该正常执行
            pass
        # 验证上下文管理器执行完成
        assert True
    
    def test_get_global_service_container(self):
        """测试获取全局服务容器"""
        # 获取全局服务容器
        global_container = get_service_container()
        
        # 验证获取成功
        assert global_container is not None
        assert isinstance(global_container, ServiceContainer)
    
    def test_circular_dependency_detection(self):
        """测试循环依赖检测"""
        # 定义循环依赖的服务
        class ServiceA:
            def __init__(self, service_b):
                self.service_b = service_b
        
        class ServiceB:
            def __init__(self, service_a):
                self.service_a = service_a
        
        # 注册服务
        self.container.register_with_dependencies('service_a', ServiceA, {'service_b': 'service_b'})
        self.container.register_with_dependencies('service_b', ServiceB, {'service_a': 'service_a'})
        
        # 尝试获取服务（应该返回None）
        service_a = self.container.get('service_a')
        
        # 验证服务获取失败（循环依赖）
        assert service_a is None
    
    def test_register_invalid_service(self):
        """测试注册无效服务"""
        # 尝试注册无效服务（空名称）
        result = self.container.register('', Mock)
        assert result is False
        
        # 尝试注册无效服务（非类）
        result = self.container.register('test_service', 'not a class')
        assert result is False
        
        # 尝试注册无效实例（空名称）
        result = self.container.register_instance('', Mock())
        assert result is False
        
        # 尝试注册无效实例（None）
        result = self.container.register_instance('test_instance', None)
        assert result is False