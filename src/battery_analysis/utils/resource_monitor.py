"""
资源监控模块

提供系统资源的实时监控功能，包括CPU使用率、内存使用情况、磁盘使用情况等，
并根据资源状况提供处理策略建议。
"""
import logging
import time
from typing import Dict, Any, Optional


try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ResourceMonitor:
    """
    系统资源监控器，用于实时监控系统资源使用情况
    """
    
    def __init__(self, monitor_interval: int = 5):
        """
        初始化资源监控器
        
        Args:
            monitor_interval: 监控间隔（秒）
        """
        self.monitor_interval = monitor_interval
        self.last_update = 0
        self.system_status = {
            'cpu_usage': 0.0,
            'memory_available': 0.0,
            'memory_total': 0.0,
            'memory_usage': 0.0,
            'disk_available': 0.0,
            'disk_total': 0.0,
            'disk_usage': 0.0,
            'last_update': 0
        }
        self.logger = logging.getLogger(__name__)
        
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil模块不可用，资源监控功能将被禁用")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统资源状态
        
        Returns:
            Dict[str, Any]: 系统资源状态
        """
        current_time = time.time()
        
        # 如果上次更新时间超过监控间隔，更新系统状态
        if current_time - self.last_update > self.monitor_interval:
            self._update_system_status()
        
        return self.system_status
    
    def _update_system_status(self) -> None:
        """
        更新系统资源状态
        """
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            # 获取CPU使用率
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # 获取内存使用情况
            memory = psutil.virtual_memory()
            
            # 获取磁盘使用情况
            disk = psutil.disk_usage('.')
            
            # 更新系统状态
            self.system_status.update({
                'cpu_usage': cpu_usage,
                'memory_available': memory.available,
                'memory_total': memory.total,
                'memory_usage': memory.percent,
                'disk_available': disk.free,
                'disk_total': disk.total,
                'disk_usage': disk.percent,
                'last_update': time.time()
            })
            
            # 记录系统状态
            self.logger.debug(
                f"系统资源状态 - CPU: {cpu_usage:.2f}%, "
                f"内存: {memory.percent:.2f}% (可用: {memory.available / (1024 * 1024 * 1024):.2f}GB), "
                f"磁盘: {disk.percent:.2f}% (可用: {disk.free / (1024 * 1024 * 1024):.2f}GB)"
            )
        except Exception as e:
            self.logger.error(f"更新系统资源状态失败: {str(e)}")
    
    def should_throttle_processing(self) -> bool:
        """
        判断是否应该节流处理
        
        Returns:
            bool: 是否应该节流
        """
        status = self.get_system_status()
        
        # 检查CPU使用率
        if status['cpu_usage'] > 80:
            self.logger.warning(f"CPU使用率过高 ({status['cpu_usage']:.2f}%)，建议节流处理")
            return True
        
        # 检查内存使用率
        if status['memory_usage'] > 80:
            self.logger.warning(f"内存使用率过高 ({status['memory_usage']:.2f}%)，建议节流处理")
            return True
        
        # 检查磁盘使用率
        if status['disk_usage'] > 90:
            self.logger.warning(f"磁盘使用率过高 ({status['disk_usage']:.2f}%)，建议节流处理")
            return True
        
        return False
    
    def get_recommended_process_count(self, default_count: int = 4) -> int:
        """
        根据系统资源状态获取推荐的进程数
        
        Args:
            default_count: 默认进程数
            
        Returns:
            int: 推荐的进程数
        """
        status = self.get_system_status()
        
        # 基础推荐进程数
        recommended_count = default_count
        
        # 根据CPU使用率调整
        if status['cpu_usage'] > 80:
            recommended_count = max(1, default_count // 2)
            self.logger.info(f"CPU使用率过高，调整推荐进程数为: {recommended_count}")
        elif status['cpu_usage'] < 30:
            recommended_count = min(default_count * 2, 8)  # 最多8个进程
            self.logger.info(f"CPU使用率较低，调整推荐进程数为: {recommended_count}")
        
        # 根据内存使用率调整
        if status['memory_usage'] > 80:
            recommended_count = max(1, recommended_count // 2)
            self.logger.info(f"内存使用率过高，调整推荐进程数为: {recommended_count}")
        
        return recommended_count
    
    def get_recommended_file_size_limit(self) -> int:
        """
        根据系统资源状态获取推荐的文件大小限制
        
        Returns:
            int: 文件大小限制（字节）
        """
        status = self.get_system_status()
        
        # 默认文件大小限制为100MB
        default_limit = 100 * 1024 * 1024
        
        # 根据可用内存调整
        if 'memory_available' in status and status['memory_available'] > 0:
            # 限制为可用内存的10%
            memory_based_limit = int(status['memory_available'] * 0.1)
            default_limit = min(default_limit, memory_based_limit)
        
        # 根据可用磁盘空间调整
        if 'disk_available' in status and status['disk_available'] > 0:
            # 限制为可用磁盘空间的5%
            disk_based_limit = int(status['disk_available'] * 0.05)
            default_limit = min(default_limit, disk_based_limit)
        
        # 确保限制在合理范围内（最小10MB，最大1GB）
        default_limit = max(default_limit, 10 * 1024 * 1024)  # 最小10MB
        default_limit = min(default_limit, 1024 * 1024 * 1024)  # 最大1GB
        
        self.logger.debug(f"推荐文件大小限制: {default_limit / (1024 * 1024):.2f}MB")
        return default_limit
    
    def get_processing_strategy(self) -> Dict[str, Any]:
        """
        根据系统资源状态获取处理策略建议
        
        Returns:
            Dict[str, Any]: 处理策略建议
        """
        status = self.get_system_status()
        strategy = {
            'should_throttle': self.should_throttle_processing(),
            'recommended_process_count': self.get_recommended_process_count(),
            'recommended_file_size_limit': self.get_recommended_file_size_limit(),
            'recommended_timeout_factor': 1.0,
            'resource_status': status
        }
        
        # 根据系统负载调整超时因子
        if status['cpu_usage'] > 80 or status['memory_usage'] > 80:
            # 系统高负载，增加超时时间
            strategy['recommended_timeout_factor'] = 1.5
        elif status['cpu_usage'] < 30 and status['memory_usage'] < 40:
            # 系统低负载，减少超时时间
            strategy['recommended_timeout_factor'] = 0.8
        
        return strategy
    
    def log_system_status(self) -> None:
        """
        记录系统资源状态
        """
        status = self.get_system_status()
        self.logger.info(
            f"系统资源状态 - "
            f"CPU: {status['cpu_usage']:.2f}%, "
            f"内存: {status['memory_usage']:.2f}% (可用: {status['memory_available'] / (1024 * 1024 * 1024):.2f}GB), "
            f"磁盘: {status['disk_usage']:.2f}% (可用: {status['disk_available'] / (1024 * 1024 * 1024):.2f}GB)"
        )


# 全局资源监控器实例
_global_resource_monitor = ResourceMonitor()


def get_resource_monitor() -> ResourceMonitor:
    """
    获取全局资源监控器实例
    
    Returns:
        ResourceMonitor: 全局资源监控器实例
    """
    return _global_resource_monitor
