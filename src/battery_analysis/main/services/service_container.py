# -*- coding: utf-8 -*-
"""
服务容器模块

提供依赖注入和服务生命周期管理功能
实现控制反转和单例模式
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any, Type, Callable, TypeVar, Generic, List
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
        
        # 延迟注册函数列表
        self._service_registrations: Dict[str, Callable[[], bool]] = {}
        
        # 是否已初始化服务注册
        self._services_initialized = False
    
    def _initialize_services(self):
        """
        初始化默认服务，按照分层架构注册服务
        """
        if self._services_initialized:
            return
        
        try:
            # 1. 注册核心基础设施服务
            self._register_infrastructure_services()
            
            # 2. 注册应用层服务（Use Cases）
            self._register_application_services()
            
            # 3. 注册表现层服务
            self._register_presentation_services()
            
            # 4. 注册控制器
            self._register_controllers()
            
            self.logger.info("Default services initialized successfully according to layered architecture")
            self._services_initialized = True
            
        except ImportError as e:
            self.logger.warning("Failed to import services: %s", e)
    
    def _register_infrastructure_services(self):
        """
        注册基础设施层服务
        """
        try:
            # 注册核心技术服务
            from battery_analysis.main.services.config_service import ConfigService
            from battery_analysis.main.services.event_bus import EventBus
            from battery_analysis.main.services.environment_service import EnvironmentService
            from battery_analysis.main.services.file_service import FileService
            from battery_analysis.main.services.i18n_service import I18nService
            from battery_analysis.main.services.progress_service import ProgressService
            from battery_analysis.main.services.validation_service import ValidationService
            
            core_tech_services = [
                ("config", ConfigService),
                ("event_bus", EventBus),
                ("environment", EnvironmentService),
                ("file", FileService),
                ("i18n", I18nService),
                ("progress", ProgressService),
                ("validation", ValidationService)
            ]
            
            for name, service_class in core_tech_services:
                try:
                    self.register(name, service_class)
                    self.logger.debug("Infrastructure service registered: %s", name)
                except (ImportError, ValueError, TypeError) as e:
                    self.logger.error("Failed to register infrastructure service %s: %s", name, e)
            
            # 注册领域基础设施实现
            try:
                from battery_analysis.infrastructure.repositories.battery_repository_impl import BatteryRepositoryImpl
                from battery_analysis.infrastructure.services.battery_analysis_service_impl import BatteryAnalysisServiceImpl
                
                domain_infra_services = [
                    ("battery_repository", BatteryRepositoryImpl),
                    ("battery_analysis_service", BatteryAnalysisServiceImpl)
                ]
                
                for name, service_class in domain_infra_services:
                    try:
                        self.register(name, service_class)
                        self.logger.debug("Domain infrastructure service registered: %s", name)
                    except (ImportError, ValueError, TypeError) as e:
                        self.logger.error("Failed to register domain infrastructure service %s: %s", name, e)
            except ImportError as e:
                self.logger.warning("Failed to import domain infrastructure services: %s", e)
        except ImportError as e:
            self.logger.warning("Failed to import infrastructure services: %s", e)
    
    def _register_application_services(self):
        """
        注册应用层服务（Use Cases）
        """
        try:
            from battery_analysis.application.usecases.calculate_battery_use_case import CalculateBatteryUseCase
            from battery_analysis.application.usecases.analyze_data_use_case import AnalyzeDataUseCase
            from battery_analysis.application.usecases.generate_report_use_case import GenerateReportUseCase
            
            # 注册use cases并指定依赖
            use_cases = [
                {
                    "name": "calculate_battery",
                    "class": CalculateBatteryUseCase,
                    "dependencies": {
                        "battery_repository": "battery_repository",
                        "battery_analysis_service": "battery_analysis_service"
                    }
                },
                {
                    "name": "analyze_data",
                    "class": AnalyzeDataUseCase,
                    "dependencies": {
                        "battery_repository": "battery_repository",
                        "battery_analysis_service": "battery_analysis_service"
                    }
                },
                {
                    "name": "generate_report",
                    "class": GenerateReportUseCase,
                    "dependencies": {
                        "battery_repository": "battery_repository"
                    }
                }
            ]
            
            for use_case in use_cases:
                try:
                    self.register_with_dependencies(
                        use_case["name"],
                        use_case["class"],
                        use_case["dependencies"]
                    )
                    self.logger.debug("Application service registered: %s", use_case["name"])
                except (ImportError, ValueError, TypeError) as e:
                    self.logger.error("Failed to register application service %s: %s", use_case["name"], e)
        except ImportError as e:
            self.logger.warning("Failed to import application services: %s", e)
    
    def _register_presentation_services(self):
        """
        注册表现层服务
        """
        try:
            from battery_analysis.main.services.application_service import ApplicationService
            
            presentation_services = [
                ("application", ApplicationService)
            ]
            
            for name, service_class in presentation_services:
                try:
                    self.register(name, service_class)
                    self.logger.debug("Presentation service registered: %s", name)
                except (ImportError, ValueError, TypeError) as e:
                    self.logger.error("Failed to register presentation service %s: %s", name, e)
        except ImportError as e:
            self.logger.warning("Failed to import presentation services: %s", e)
    
    def _register_controllers(self):
        """
        注册表现层控制器
        """
        try:
            from battery_analysis.main.controllers.file_controller import FileController
            from battery_analysis.main.controllers.main_controller import MainController
            from battery_analysis.main.controllers.validation_controller import ValidationController
            from battery_analysis.main.controllers.visualizer_controller import VisualizerController
            
            controllers = [
                ("file_controller", FileController),
                ("main_controller", MainController),
                ("validation_controller", ValidationController),
                ("visualizer_controller", VisualizerController)
            ]
            
            for name, controller_class in controllers:
                try:
                    self.register(name, controller_class)
                    self.logger.debug("Controller registered: %s", name)
                except (ImportError, ValueError, TypeError) as e:
                    self.logger.error("Failed to register controller %s: %s", name, e)
        except ImportError as e:
            self.logger.warning("Failed to import controllers: %s", e)
    
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
        获取服务，支持依赖注入和延迟注册

        Args:
            name: 服务名称

        Returns:
            T: 服务实例，如果不存在则返回None
        """
        try:
            # 如果实例已存在，直接返回
            if name in self._instances:
                return self._instances[name]
            
            # 如果服务未注册，尝试初始化服务注册
            if not self._services_initialized:
                self.logger.debug("Initializing services...")
                self._initialize_services()
            
            # 如果服务仍未注册，返回None
            if name not in self._services:
                self.logger.warning("Service not found: %s", name)
                return None
            
            # 使用迭代方式解析依赖，避免递归调用
            return self._resolve_service_with_dependencies(name)
            
        except (TypeError, AttributeError, KeyError, RecursionError) as e:
            self.logger.error("Failed to get service %s: %s", name, e)
            return None
    
    def _resolve_service_with_dependencies(self, name: str) -> Optional[T]:
        """
        使用迭代方式解析服务依赖，避免递归调用

        Args:
            name: 服务名称

        Returns:
            T: 服务实例，如果不存在则返回None
        """
        # 已解析的服务
        resolved = {}
        # 待解析的服务队列
        queue = [name]
        # 服务依赖关系图
        dependency_graph = {}
        
        # 构建依赖关系图
        while queue:
            current_name = queue.pop(0)
            
            # 如果服务已实例化，直接使用
            if current_name in self._instances:
                resolved[current_name] = self._instances[current_name]
                continue
            
            # 如果服务已解析，跳过
            if current_name in resolved:
                continue
            
            # 如果服务未注册，返回None
            if current_name not in self._services:
                self.logger.error("Service not found in dependency resolution: %s", current_name)
                return None
            
            # 获取服务依赖
            dependencies = self._dependencies.get(current_name, {})
            dependency_graph[current_name] = list(dependencies.values())
            
            # 将依赖添加到队列
            for dep_name in dependencies.values():
                if dep_name not in resolved and dep_name not in queue:
                    queue.append(dep_name)
        
        # 拓扑排序，解决依赖顺序
        sorted_services = self._topological_sort(dependency_graph)
        if not sorted_services:
            self.logger.error("Circular dependency detected in services")
            return None
        
        # 按照拓扑顺序实例化服务
        for service_name in sorted_services:
            if service_name in resolved or service_name in self._instances:
                continue
            
            # 获取服务类
            service_class = self._services[service_name]
            dependencies = self._dependencies.get(service_name, {})
            
            # 解析依赖
            resolved_dependencies = {}
            for param_name, dep_name in dependencies.items():
                if dep_name not in resolved and dep_name not in self._instances:
                    self.logger.error("Failed to resolve dependency %s for service %s", dep_name, service_name)
                    return None
                resolved_dependencies[param_name] = resolved.get(dep_name, self._instances[dep_name])
            
            # 创建服务实例
            try:
                instance = service_class(**resolved_dependencies)
            except (ImportError, TypeError, ValueError, OSError) as e:
                self.logger.error("Failed to create service instance %s: %s", service_name, e)
                self.logger.debug("Service %s constructor parameters: %s", service_name, list(resolved_dependencies.keys()))
                return None
            
            # 缓存实例
            if self._singletons.get(service_name, True):
                self._instances[service_name] = instance
            resolved[service_name] = instance
        
        # 返回目标服务实例
        return resolved.get(name, self._instances.get(name))
    
    def _topological_sort(self, graph: Dict[str, list]) -> list:
        """
        对服务依赖图进行拓扑排序

        Args:
            graph: 服务依赖关系图

        Returns:
            list: 拓扑排序后的服务列表，空列表表示存在循环依赖
        """
        # 计算每个节点的入度
        in_degree = {}
        for node in graph:
            in_degree[node] = 0
        
        for node in graph:
            for neighbor in graph[node]:
                if neighbor not in in_degree:
                    in_degree[neighbor] = 0
                in_degree[neighbor] += 1
        
        # 将入度为0的节点加入队列
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # 更新邻接节点的入度
            for neighbor in graph.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # 检查是否存在循环依赖
        if len(result) != len(in_degree):
            self.logger.warning("Circular dependency detected in services: %s", set(in_degree.keys()) - set(result))
            return []
        
        return result
    
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
