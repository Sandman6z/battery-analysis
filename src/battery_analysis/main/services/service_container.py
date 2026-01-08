# -*- coding: utf-8 -*-
"""
服务容器模块

提供依赖注入和服务生命周期管理功能
实现控制反转和单例模式
"""

import logging
from typing import Optional, Dict, Any, Type, Callable, TypeVar, Generic
from abc import ABC, abstractmethod


T = TypeVar('T')


class IServiceContainer(Generic[T], ABC):
    """
    服务容器接口
    """
    
    @abstractmethod
    def register(self, name: str, implementation: Type[T], singleton: bool = True) -> bool:
        """
        注册服务

        Args:
            name: 服务名称
            implementation: 实现类
            singleton: 是否单例

        Returns:
            bool: 注册是否成功
        """
        pass
    
    @abstractmethod
    def register_instance(self, name: str, instance: T) -> bool:
        """
        注册实例

        Args:
            name: 服务名称
            instance: 服务实例

        Returns:
            bool: 注册是否成功
        """
        pass
    
    @abstractmethod
    def get(self, name: str) -> Optional[T]:
        """
        获取服务

        Args:
            name: 服务名称

        Returns:
            T: 服务实例，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    def has(self, name: str) -> bool:
        """
        检查服务是否存在

        Args:
            name: 服务名称

        Returns:
            bool: 服务是否存在
        """
        pass
    
    @abstractmethod
    def unregister(self, name: str) -> bool:
        """
        注销服务

        Args:
            name: 服务名称

        Returns:
            bool: 注销是否成功
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """
        关闭容器

        Returns:
            bool: 关闭是否成功
        """
        pass


class ServiceContainer(IServiceContainer):
    """
    服务容器实现
    """
    
    def __init__(self):
        """
        初始化服务容器
        """
        self.logger = logging.getLogger(__name__)
        
        # 服务注册表
        self._services: Dict[str, Type] = {}
        self._instances: Dict[str, Any] = {}
        self._singletons: Dict[str, bool] = {}
        
        # 工厂方法
        self._factories: Dict[str, Callable] = {}
        
        # 服务依赖映射
        self._dependencies: Dict[str, Dict[str, str]] = {}
        
        # 初始化服务
        self._initialize_services()
    
    def _initialize_services(self):
        """
        初始化默认服务
        """
        try:
            # 导入应用服务
            from battery_analysis.main.services.application_service import ApplicationService
            from battery_analysis.main.services.config_service import ConfigService
            from battery_analysis.main.services.event_bus import EventBus
            from battery_analysis.main.services.environment_service import EnvironmentService
            from battery_analysis.main.services.file_service import FileService
            from battery_analysis.main.services.i18n_service import I18nService
            from battery_analysis.main.services.progress_service import ProgressService
            from battery_analysis.main.services.validation_service import ValidationService
            
            # 注册核心服务
            services_to_register = [
                ("application", ApplicationService),
                ("config", ConfigService),
                ("event_bus", EventBus),
                ("environment", EnvironmentService),
                ("file", FileService),
                ("i18n", I18nService),
                ("progress", ProgressService),
                ("validation", ValidationService)
            ]
            
            for name, service_class in services_to_register:
                try:
                    self.register(name, service_class)
                    self.logger.debug("Service registered: %s", name)
                except (ImportError, ValueError, TypeError) as e:
                    self.logger.error("Failed to register service %s: %s", name, e)
            
            # 导入并注册use cases
            try:
                from battery_analysis.application.usecases.calculate_battery_use_case import CalculateBatteryUseCase
                from battery_analysis.application.usecases.analyze_data_use_case import AnalyzeDataUseCase
                from battery_analysis.application.usecases.generate_report_use_case import GenerateReportUseCase
                
                # 注册use cases
                use_cases_to_register = [
                    ("calculate_battery", CalculateBatteryUseCase),
                    ("analyze_data", AnalyzeDataUseCase),
                    ("generate_report", GenerateReportUseCase)
                ]
                
                for name, use_case_class in use_cases_to_register:
                    try:
                        self.register(name, use_case_class)
                        self.logger.debug("Use case registered: %s", name)
                    except (ImportError, ValueError, TypeError) as e:
                        self.logger.error("Failed to register use case %s: %s", name, e)
            except ImportError as e:
                self.logger.warning("Failed to import use cases: %s", e)
            
            # 延迟导入控制器
            try:
                # 导入控制器
                from battery_analysis.main.controllers.file_controller import FileController
                from battery_analysis.main.controllers.main_controller import MainController
                from battery_analysis.main.controllers.validation_controller import ValidationController
                from battery_analysis.main.controllers.visualizer_controller import VisualizerController
                
                # 注册控制器
                controllers_to_register = [
                    ("file_controller", FileController),
                    ("main_controller", MainController),
                    ("validation_controller", ValidationController),
                    ("visualizer_controller", VisualizerController)
                ]
                
                for name, controller_class in controllers_to_register:
                    try:
                        self.register(name, controller_class)
                        self.logger.debug("Controller registered: %s", name)
                    except (ImportError, ValueError, TypeError) as e:
                        self.logger.error("Failed to register controller %s: %s", name, e)
            except ImportError as e:
                self.logger.warning("Failed to import controllers: %s", e)
            
            self.logger.info("Default services, use cases and controllers initialized")
            
        except ImportError as e:
            self.logger.warning("Failed to import services: %s", e)
    
    def register(self, name: str, implementation: Type[T], singleton: bool = True) -> bool:
        """
        注册服务

        Args:
            name: 服务名称
            implementation: 实现类
            singleton: 是否单例

        Returns:
            bool: 注册是否成功
        """
        return self.register_with_dependencies(name, implementation, {}, singleton)
    
    def register_with_dependencies(self, name: str, implementation: Type[T], 
                                  dependencies: Dict[str, str], singleton: bool = True) -> bool:
        """
        注册服务并指定依赖关系

        Args:
            name: 服务名称
            implementation: 实现类
            dependencies: 依赖映射，键为构造函数参数名，值为服务名称
            singleton: 是否单例

        Returns:
            bool: 注册是否成功
        """
        try:
            if not isinstance(name, str) or not name:
                raise ValueError("Service name must be a non-empty string")
            
            if not isinstance(implementation, type):
                raise ValueError("Implementation must be a class type")
            
            if not isinstance(dependencies, dict):
                raise ValueError("Dependencies must be a dictionary")
            
            self._services[name] = implementation
            self._dependencies[name] = dependencies
            self._singletons[name] = singleton
            
            # 清除已存在的实例（如果重新注册）
            if name in self._instances:
                del self._instances[name]
            
            self.logger.debug("Service registered: %s (%s) with dependencies: %s", 
                            name, implementation.__name__, dependencies)
            return True
            
        except (ValueError, TypeError, MemoryError) as e:
            self.logger.error("Failed to register service %s: %s", name, e)
            return False
    
    def register_instance(self, name: str, instance: T) -> bool:
        """
        注册实例

        Args:
            name: 服务名称
            instance: 服务实例

        Returns:
            bool: 注册是否成功
        """
        try:
            if not isinstance(name, str) or not name:
                raise ValueError("Service name must be a non-empty string")
            
            if instance is None:
                raise ValueError("Instance cannot be None")
            
            self._instances[name] = instance
            self._singletons[name] = True
            
            self.logger.debug("Service instance registered: %s", name)
            return True
            
        except (ValueError, TypeError, MemoryError) as e:
            self.logger.error("Failed to register service instance %s: %s", name, e)
            return False
    
    def get(self, name: str) -> Optional[T]:
        """
        获取服务，支持依赖注入

        Args:
            name: 服务名称

        Returns:
            T: 服务实例，如果不存在则返回None
        """
        try:
            # 如果实例已存在，直接返回
            if name in self._instances:
                return self._instances[name]
            
            # 如果没有注册该服务，返回None
            if name not in self._services:
                self.logger.warning("Service not found: %s", name)
                return None
            
            # 获取服务类
            service_class = self._services[name]
            
            # 获取服务依赖
            dependencies = self._dependencies.get(name, {})
            
            # 解析依赖
            resolved_dependencies = {}
            for param_name, service_dependency in dependencies.items():
                dependency_instance = self.get(service_dependency)
                if dependency_instance is None:
                    self.logger.error("Failed to resolve dependency %s for service %s", 
                                     service_dependency, name)
                    return None
                resolved_dependencies[param_name] = dependency_instance
            
            # 创建服务实例（带依赖注入）
            try:
                instance = service_class(**resolved_dependencies)
            except (ImportError, TypeError, ValueError, OSError) as e:
                self.logger.error("Failed to create service instance %s: %s", name, e)
                self.logger.debug("Service %s constructor parameters: %s", 
                                name, list(resolved_dependencies.keys()))
                return None
            
            # 如果是单例，缓存实例
            if self._singletons.get(name, True):
                self._instances[name] = instance
            
            return instance
            
        except (TypeError, AttributeError, KeyError) as e:
            self.logger.error("Failed to get service %s: %s", name, e)
            return None
    
    def has(self, name: str) -> bool:
        """
        检查服务是否存在

        Args:
            name: 服务名称

        Returns:
            bool: 服务是否存在
        """
        return name in self._services or name in self._instances
    
    def unregister(self, name: str) -> bool:
        """
        注销服务

        Args:
            name: 服务名称

        Returns:
            bool: 注销是否成功
        """
        try:
            removed = False
            
            # 移除服务注册
            if name in self._services:
                del self._services[name]
                removed = True
            
            # 移除服务实例
            if name in self._instances:
                del self._instances[name]
                removed = True
            
            # 移除单例标记
            if name in self._singletons:
                del self._singletons[name]
            
            # 移除依赖映射
            if name in self._dependencies:
                del self._dependencies[name]
            
            if removed:
                self.logger.debug("Service unregistered: %s", name)
            
            return removed
            
        except (TypeError, KeyError, ValueError) as e:
            self.logger.error("Failed to unregister service %s: %s", name, e)
            return False
    
    def get_all_services(self) -> Dict[str, Any]:
        """
        获取所有服务

        Returns:
            Dict[str, Any]: 所有服务实例
        """
        result = {}
        
        # 添加已实例化的服务
        for name, instance in self._instances.items():
            result[name] = instance
        
        # 添加未实例化的服务（但需要实例化）
        for name, service_class in self._services.items():
            if name not in self._instances:
                try:
                    instance = self.get(name)
                    if instance:
                        result[name] = instance
                except (TypeError, ImportError, OSError) as e:
                    self.logger.error("Failed to instantiate service %s: %s", name, e)
        
        return result
    
    def shutdown(self) -> bool:
        """
        关闭容器

        Returns:
            bool: 关闭是否成功
        """
        try:
            self.logger.info("Shutting down ServiceContainer...")
            
            # 调用服务的shutdown方法
            for name, instance in self._instances.items():
                try:
                    if hasattr(instance, 'shutdown'):
                        instance.shutdown()
                        self.logger.debug("Service %s shutdown", name)
                except (TypeError, AttributeError) as e:
                    self.logger.error("Failed to shutdown service %s: %s", name, e)
            
            # 清空所有注册
            self._services.clear()
            self._instances.clear()
            self._singletons.clear()
            self._dependencies.clear()
            self._factories.clear()
            
            self.logger.info("ServiceContainer shutdown complete")
            return True
            
        except (TypeError, AttributeError, OSError) as e:
            self.logger.error("Failed to shutdown ServiceContainer: %s", e)
            return False
    
    def clear_instances(self):
        """
        清除所有服务实例（但保留注册）
        """
        try:
            # 调用shutdown方法
            for name, instance in self._instances.items():
                try:
                    if hasattr(instance, 'shutdown'):
                        instance.shutdown()
                except (TypeError, AttributeError) as e:
                    self.logger.error("Failed to shutdown service %s: %s", name, e)
            
            self._instances.clear()
            self.logger.info("All service instances cleared")
            
        except (TypeError, AttributeError, OSError) as e:
            self.logger.error("Failed to clear service instances: %s", e)
    
    def get_service_info(self) -> Dict[str, Dict[str, Any]]:
        """
        获取服务信息

        Returns:
            Dict[str, Dict[str, Any]]: 服务信息
        """
        info = {}
        
        for name in set(list(self._services.keys()) + list(self._instances.keys())):
            service_info = {
                'registered': name in self._services,
                'instantiated': name in self._instances,
                'singleton': self._singletons.get(name, True)
            }
            
            if name in self._services:
                service_info['class'] = self._services[name].__name__
            
            if name in self._instances:
                service_info['instance'] = type(self._instances[name]).__name__
            
            info[name] = service_info
        
        return info


# 全局服务容器实例
_global_container: Optional[ServiceContainer] = None


def get_service_container() -> ServiceContainer:
    """
    获取全局服务容器

    Returns:
        ServiceContainer: 全局服务容器实例
    """
    global _global_container
    if _global_container is None:
        _global_container = ServiceContainer()
    return _global_container


def set_service_container(container: ServiceContainer):
    """
    设置全局服务容器

    Args:
        container: 服务容器实例
    """
    global _global_container
    _global_container = container
