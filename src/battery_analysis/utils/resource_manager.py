"""
资源管理器模块，用于根据系统负载动态调整并行处理的资源使用

提供了获取最优进程数和处理上下文的功能，能够根据CPU使用率和内存情况
动态调整并行处理的资源分配，以确保系统性能和稳定性。
"""
import multiprocessing
import logging
import os
import time
import threading
from typing import Dict, Optional, Tuple, Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ResourceManager:
    """
    系统资源管理器，用于根据系统负载动态调整并行处理的资源使用
    """
    
    # 资源监控间隔（秒）
    MONITOR_INTERVAL = 5
    
    # 资源池管理
    _resource_pools: Dict[str, Any] = {}
    _resource_pool_lock = threading.Lock()
    
    # 系统资源状态
    _system_status = {
        'cpu_usage': 0.0,
        'memory_available': 0.0,
        'disk_usage': 0.0,
        'last_update': 0
    }
    
    # 并发控制
    _active_tasks = 0
    _max_concurrent_tasks = 4
    _task_lock = threading.Lock()

    @staticmethod
    def get_optimal_process_count(max_processes_default: int = 8,
                                  min_processes: int = 1) -> int:
        """
        根据系统CPU使用率和内存情况，获取最优的进程数

        Args:
            max_processes_default: 默认的最大进程数上限
            min_processes: 最小进程数

        Returns:
            计算得到的最优进程数
        """
        # 获取CPU核心数
        cpu_count = multiprocessing.cpu_count()
        # 设置合理的进程数上限
        max_processes = min(cpu_count, max_processes_default)

        if PSUTIL_AVAILABLE:
            try:
                # 检测系统CPU使用率（1秒平均值）
                cpu_usage = psutil.cpu_percent(interval=1, percpu=False)
                logging.info("当前系统CPU使用率: %.2f%%", cpu_usage)

                # 根据CPU使用率动态调整进程数
                if cpu_usage > 80:
                    # 系统高负载：仅使用较少核心
                    max_processes = min(max_processes_default, 2)
                    logging.info("系统高负载，调整进程数为: %d", max_processes)
                elif cpu_usage > 50:
                    # 系统中负载：使用一半核心
                    max_processes = min(max_processes_default,
                                        max(2, cpu_count // 2))
                    logging.info("系统中负载，调整进程数为: %d", max_processes)
                else:
                    # 系统低负载：使用默认进程数
                    max_processes = max_processes_default
                    logging.info("系统低负载，使用进程数: %d", max_processes)

                # 考虑内存限制（每个进程约100MB内存）
                available_memory_gb = psutil.virtual_memory().available / (1024 ** 3)
                memory_based_processes = int(
                    available_memory_gb * 10)  # 每100MB内存一个进程
                max_processes = min(max_processes, memory_based_processes)
                logging.info("考虑内存限制后，调整进程数为: %d", max_processes)
            except (psutil.Error, OSError) as e:
                # 捕获psutil相关的具体异常
                logging.error("获取系统资源信息whenerror occurred: %s", str(e))
        else:
            # 如果psutil不可用，使用默认值
            logging.warning("psutil库不可用，使用默认进程数")

        # 确保进程数在合理范围内
        max_processes = max(max_processes, min_processes)

        return max_processes

    @staticmethod
    def get_processing_context():
        """
        获取适合当前平台的进程上下文

        Returns:
            进程上下文对象
        """
        # 在Windows下使用spawn启动方式，避免递归启动问题
        ctx = multiprocessing.get_context('spawn')
        return ctx
    
    @staticmethod
    def get_dynamic_file_size_limit() -> int:
        """
        根据系统资源状况动态调整文件大小限制
        
        Returns:
            int: 文件大小限制（字节）
        """
        # 默认文件大小限制为100MB
        default_limit = 100 * 1024 * 1024
        
        if PSUTIL_AVAILABLE:
            try:
                # 获取可用内存
                available_memory = psutil.virtual_memory().available
                # 获取可用磁盘空间
                disk_usage = psutil.disk_usage('.')
                available_disk = disk_usage.free
                
                # 根据可用资源调整文件大小限制
                # 限制为可用内存的10%或可用磁盘的5%，取较小值
                memory_based_limit = int(available_memory * 0.1)
                disk_based_limit = int(available_disk * 0.05)
                
                # 确保限制在合理范围内（最小10MB，最大1GB）
                limit = min(memory_based_limit, disk_based_limit)
                limit = max(limit, 10 * 1024 * 1024)  # 最小10MB
                limit = min(limit, 1024 * 1024 * 1024)  # 最大1GB
                
                logging.info(f"动态文件大小限制: {limit / (1024 * 1024):.2f}MB")
                return limit
            except Exception as e:
                logging.error(f"获取动态文件大小限制失败: {str(e)}")
                return default_limit
        else:
            return default_limit
    
    @staticmethod
    def get_layered_timeout(file_operation: str) -> float:
        """
        分层超时机制：不同文件操作阶段设置不同的超时阈值
        
        Args:
            file_operation: 文件操作类型
                - "open": 文件打开
                - "read": 文件读取
                - "write": 文件写入
                - "process": 文件处理
                - "close": 文件关闭
        
        Returns:
            float: 超时时间（秒）
        """
        # 基础超时时间
        base_timeouts = {
            "open": 30.0,    # 文件打开：30秒
            "read": 60.0,    # 文件读取：60秒
            "write": 45.0,   # 文件写入：45秒
            "process": 120.0, # 文件处理：120秒
            "close": 10.0    # 文件关闭：10秒
        }
        
        # 根据系统资源状况调整超时时间
        timeout = base_timeouts.get(file_operation, 60.0)
        
        if PSUTIL_AVAILABLE:
            try:
                # 获取系统负载
                cpu_usage = psutil.cpu_percent(interval=0.1)
                memory_available = psutil.virtual_memory().available
                memory_total = psutil.virtual_memory().total
                memory_usage = 1 - (memory_available / memory_total)
                
                # 根据系统负载调整超时时间
                if cpu_usage > 80 or memory_usage > 0.8:
                    # 系统高负载，增加超时时间
                    timeout *= 1.5
                    logging.info(f"系统高负载，调整{file_operation}超时时间为: {timeout:.2f}秒")
                elif cpu_usage < 30 and memory_usage < 0.4:
                    # 系统低负载，减少超时时间
                    timeout *= 0.8
                    logging.info(f"系统低负载，调整{file_operation}超时时间为: {timeout:.2f}秒")
            except Exception as e:
                logging.error(f"获取分层超时失败: {str(e)}")
        
        return timeout
    
    @staticmethod
    def get_resource_pool(pool_name: str, create_func, max_size: int = 10):
        """
        资源池管理：获取或创建资源池
        
        Args:
            pool_name: 资源池名称
            create_func: 创建资源的函数
            max_size: 资源池最大大小
            
        Returns:
            Any: 资源池
        """
        with ResourceManager._resource_pool_lock:
            if pool_name not in ResourceManager._resource_pools:
                # 创建新的资源池
                ResourceManager._resource_pools[pool_name] = {
                    'resources': [],
                    'max_size': max_size,
                    'create_func': create_func,
                    'in_use': set()
                }
                logging.info(f"创建资源池: {pool_name}, 最大大小: {max_size}")
            
            return ResourceManager._resource_pools[pool_name]
    
    @staticmethod
    def acquire_resource(pool_name: str) -> Optional[Any]:
        """
        从资源池获取资源
        
        Args:
            pool_name: 资源池名称
            
        Returns:
            Optional[Any]: 获取的资源，如果获取失败返回None
        """
        with ResourceManager._resource_pool_lock:
            if pool_name not in ResourceManager._resource_pools:
                logging.error(f"资源池不存在: {pool_name}")
                return None
            
            pool = ResourceManager._resource_pools[pool_name]
            
            # 尝试从资源池中获取可用资源
            for i, resource in enumerate(pool['resources']):
                if i not in pool['in_use']:
                    pool['in_use'].add(i)
                    logging.debug(f"从资源池{pool_name}获取资源: {i}")
                    return resource
            
            # 如果没有可用资源且未达到最大大小，创建新资源
            if len(pool['resources']) < pool['max_size']:
                try:
                    new_resource = pool['create_func']()
                    pool['resources'].append(new_resource)
                    resource_index = len(pool['resources']) - 1
                    pool['in_use'].add(resource_index)
                    logging.debug(f"在资源池{pool_name}创建新资源: {resource_index}")
                    return new_resource
                except Exception as e:
                    logging.error(f"创建资源失败: {str(e)}")
                    return None
            
            logging.warning(f"资源池{pool_name}已满，无法获取资源")
            return None
    
    @staticmethod
    def release_resource(pool_name: str, resource: Any) -> bool:
        """
        释放资源回资源池
        
        Args:
            pool_name: 资源池名称
            resource: 要释放的资源
            
        Returns:
            bool: 释放是否成功
        """
        with ResourceManager._resource_pool_lock:
            if pool_name not in ResourceManager._resource_pools:
                logging.error(f"资源池不存在: {pool_name}")
                return False
            
            pool = ResourceManager._resource_pools[pool_name]
            
            # 查找资源索引
            for i, res in enumerate(pool['resources']):
                if res is resource:
                    if i in pool['in_use']:
                        pool['in_use'].remove(i)
                        logging.debug(f"释放资源回资源池{pool_name}: {i}")
                        return True
                    break
            
            logging.warning(f"资源不在使用中: {resource}")
            return False
    
    @staticmethod
    def cleanup_resource_pool(pool_name: str) -> bool:
        """
        清理资源池
        
        Args:
            pool_name: 资源池名称
            
        Returns:
            bool: 清理是否成功
        """
        with ResourceManager._resource_pool_lock:
            if pool_name in ResourceManager._resource_pools:
                del ResourceManager._resource_pools[pool_name]
                logging.info(f"清理资源池: {pool_name}")
                return True
            return False
    
    @staticmethod
    def get_memory_mapped_file(file_path: str, mode: str = 'r') -> Optional[Any]:
        """
        内存映射：大文件使用内存映射技术，减少内存使用
        
        Args:
            file_path: 文件路径
            mode: 打开模式
            
        Returns:
            Optional[Any]: 内存映射对象
        """
        try:
            import mmap
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            
            # 对于大文件（超过10MB）使用内存映射
            if file_size > 10 * 1024 * 1024:
                logging.info(f"使用内存映射打开大文件: {file_path} ({file_size / (1024 * 1024):.2f}MB)")
                
                with open(file_path, 'rb' if 'b' in mode else 'r') as f:
                    # 创建内存映射
                    mm = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)
                    return mm
            else:
                # 小文件直接返回None，使用常规读取方式
                return None
        except ImportError:
            logging.warning("mmap模块不可用，无法使用内存映射")
            return None
        except Exception as e:
            logging.error(f"创建内存映射失败: {str(e)}")
            return None
    
    @staticmethod
    def acquire_task_slot() -> bool:
        """
        并发控制：获取任务槽位
        
        Returns:
            bool: 是否成功获取任务槽位
        """
        with ResourceManager._task_lock:
            # 更新最大并发任务数
            ResourceManager._update_max_concurrent_tasks()
            
            if ResourceManager._active_tasks < ResourceManager._max_concurrent_tasks:
                ResourceManager._active_tasks += 1
                logging.debug(f"获取任务槽位，当前活跃任务数: {ResourceManager._active_tasks}")
                return True
            else:
                logging.warning(f"任务槽位已满，最大并发任务数: {ResourceManager._max_concurrent_tasks}")
                return False
    
    @staticmethod
    def release_task_slot() -> None:
        """
        并发控制：释放任务槽位
        """
        with ResourceManager._task_lock:
            if ResourceManager._active_tasks > 0:
                ResourceManager._active_tasks -= 1
                logging.debug(f"释放任务槽位，当前活跃任务数: {ResourceManager._active_tasks}")
    
    @staticmethod
    def _update_max_concurrent_tasks() -> None:
        """
        根据系统资源状况更新最大并发任务数
        """
        if PSUTIL_AVAILABLE:
            try:
                # 获取CPU使用率
                cpu_usage = psutil.cpu_percent(interval=0.1)
                # 获取可用内存
                available_memory = psutil.virtual_memory().available
                memory_total = psutil.virtual_memory().total
                memory_usage = 1 - (available_memory / memory_total)
                
                # 根据系统负载调整最大并发任务数
                cpu_count = multiprocessing.cpu_count()
                
                if cpu_usage > 80 or memory_usage > 0.8:
                    # 系统高负载：减少并发任务数
                    ResourceManager._max_concurrent_tasks = max(2, cpu_count // 2)
                elif cpu_usage < 30 and memory_usage < 0.4:
                    # 系统低负载：增加并发任务数
                    ResourceManager._max_concurrent_tasks = min(8, cpu_count)
                else:
                    # 系统正常负载
                    ResourceManager._max_concurrent_tasks = min(4, cpu_count)
                
                logging.debug(f"更新最大并发任务数: {ResourceManager._max_concurrent_tasks}")
            except Exception as e:
                logging.error(f"更新最大并发任务数失败: {str(e)}")
    
    @staticmethod
    def get_system_resource_status() -> Dict[str, Any]:
        """
        资源监控：获取系统资源使用情况
        
        Returns:
            Dict[str, Any]: 系统资源状态
        """
        current_time = time.time()
        
        # 如果上次更新时间超过监控间隔，更新系统状态
        if current_time - ResourceManager._system_status['last_update'] > ResourceManager.MONITOR_INTERVAL:
            if PSUTIL_AVAILABLE:
                try:
                    # 获取CPU使用率
                    cpu_usage = psutil.cpu_percent(interval=0.1)
                    # 获取可用内存
                    memory = psutil.virtual_memory()
                    # 获取磁盘使用率
                    disk = psutil.disk_usage('.')
                    
                    ResourceManager._system_status.update({
                        'cpu_usage': cpu_usage,
                        'memory_available': memory.available,
                        'memory_total': memory.total,
                        'disk_available': disk.free,
                        'disk_total': disk.total,
                        'last_update': current_time
                    })
                except Exception as e:
                    logging.error(f"获取系统资源状态失败: {str(e)}")
        
        return ResourceManager._system_status
    
    @staticmethod
    def should_throttle_processing() -> bool:
        """
        根据系统资源状态判断是否应该节流处理
        
        Returns:
            bool: 是否应该节流
        """
        status = ResourceManager.get_system_resource_status()
        
        # 如果CPU使用率超过80%或内存使用率超过80%，应该节流
        if status['cpu_usage'] > 80:
            logging.warning(f"CPU使用率过高 ({status['cpu_usage']}%)，建议节流处理")
            return True
        
        if 'memory_total' in status and 'memory_available' in status:
            memory_usage = 1 - (status['memory_available'] / status['memory_total'])
            if memory_usage > 0.8:
                logging.warning(f"内存使用率过高 ({memory_usage * 100:.1f}%)，建议节流处理")
                return True
        
        return False
