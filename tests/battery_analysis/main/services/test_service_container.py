"""
测试服务容器模块的功能

重构说明：ServiceContainer 已从复杂的 DI 容器（拓扑排序、依赖图解析、
ServiceContext/MultiServiceContext）简化为简单工厂模式。服务实例通过
_initialize_services() 显式创建，register() 不再支持动态注册。
"""
import pytest
from battery_analysis.main.services.service_container import (
    ServiceContainer, Services, get_service_container,
)


class TestServiceContainer:
    """测试服务容器类"""

    def setup_method(self):
        """设置测试环境"""
        # 创建服务容器实例（局部实例，避免触发全局服务初始化）
        self.container = ServiceContainer()
        self.container._services_initialized = True
        self.container._impl = None

    def test_get_existing_service(self):
        """测试获取已注册的服务"""
        # 使用真实初始化获取已知服务
        container = ServiceContainer()
        service = container.get('config')
        assert service is not None

    def test_get_nonexistent_service(self):
        """测试获取不存在的服务"""
        # 获取不存在的服务
        service = self.container.get('nonexistent_service')

        # 验证返回None
        assert service is None

    def test_has_existing_service(self):
        """测试 has 对已知服务返回 True"""
        container = ServiceContainer()
        assert container.has('config') is True

    def test_has_nonexistent_service(self):
        """测试 has 对未知服务返回 False"""
        assert self.container.has('nonexistent_service') is False

    def test_get_global_service_container(self):
        """测试获取全局服务容器"""
        global_container = get_service_container()
        assert global_container is not None
        assert isinstance(global_container, ServiceContainer)

    def test_get_global_service_container_is_singleton(self):
        """测试全局容器是单例"""
        assert get_service_container() is get_service_container()

    def test_name_map_removed(self):
        """_name_map 死代码已删除，get 改用 getattr"""
        assert not hasattr(Services(), '_name_map')


    def test_register_removed(self):
        """register() 死代码已删除"""
        assert not hasattr(ServiceContainer, 'register')
