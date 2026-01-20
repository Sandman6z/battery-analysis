"""
并发控制模块

提供任务并发控制功能，限制同时执行的任务数量，防止系统过载，
确保系统资源的合理使用。
"""
import logging
import threading
import time
import multiprocessing


try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ConcurrencyController:
    """
    并发控制器类，用于限制同时执行的任务数量
    """
    
    def __init__(self, max_concurrent_tasks: int = 4):
        """
        初始化并发控制器
        
        Args:
            max_concurrent_tasks: 最大并发任务数
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.active_tasks = 0
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self.last_resource_check = 0
        self.resource_check_interval = 5  # 资源检查间隔（秒）
    
    def acquire_task_slot(self) -> bool:
        """
        获取任务槽位
        
        Returns:
            bool: 是否成功获取任务槽位
        """
        with self.lock:
            # 检查系统资源状况，动态调整最大并发任务数
            self._check_system_resources()
            
            if self.active_tasks < self.max_concurrent_tasks:
                self.active_tasks += 1
                self.logger.debug(f"获取任务槽位，当前活跃任务数: {self.active_tasks}/{self.max_concurrent_tasks}")
                return True
            else:
                self.logger.warning(f"任务槽位已满，当前活跃任务数: {self.active_tasks}/{self.max_concurrent_tasks}")
                return False
    
    def release_task_slot(self) -> None:
        """
        释放任务槽位
        """
        with self.lock:
            if self.active_tasks > 0:
                self.active_tasks -= 1
                self.logger.debug(f"释放任务槽位，当前活跃任务数: {self.active_tasks}/{self.max_concurrent_tasks}")
            else:
                self.logger.warning("尝试释放不存在的任务槽位")
    
    def _check_system_resources(self) -> None:
        """
        检查系统资源状况，动态调整最大并发任务数
        """
        current_time = time.time()
        
        # 如果上次资源检查时间超过检查间隔，更新系统资源状况
        if current_time - self.last_resource_check > self.resource_check_interval:
            if PSUTIL_AVAILABLE:
                try:
                    # 获取CPU使用率
                    cpu_usage = psutil.cpu_percent(interval=0.1)
                    # 获取内存使用情况
                    memory = psutil.virtual_memory()
                    memory_usage = memory.percent
                    
                    # 根据系统负载调整最大并发任务数
                    cpu_count = multiprocessing.cpu_count()
                    
                    if cpu_usage > 80 or memory_usage > 80:
                        # 系统高负载，减少并发任务数
                        new_max_tasks = max(2, cpu_count // 2)
                        if new_max_tasks != self.max_concurrent_tasks:
                            self.max_concurrent_tasks = new_max_tasks
                            self.logger.info(f"系统高负载，调整最大并发任务数为: {self.max_concurrent_tasks}")
                    elif cpu_usage < 30 and memory_usage < 40:
                        # 系统低负载，增加并发任务数
                        new_max_tasks = min(8, cpu_count)
                        if new_max_tasks != self.max_concurrent_tasks:
                            self.max_concurrent_tasks = new_max_tasks
                            self.logger.info(f"系统低负载，调整最大并发任务数为: {self.max_concurrent_tasks}")
                    
                    self.last_resource_check = current_time
                except Exception as e:
                    self.logger.error(f"检查系统资源失败: {str(e)}")
    
    def get_active_task_count(self) -> int:
        """
        获取当前活跃任务数
        
        Returns:
            int: 当前活跃任务数
        """
        with self.lock:
            return self.active_tasks
    
    def get_max_concurrent_tasks(self) -> int:
        """
        获取最大并发任务数
        
        Returns:
            int: 最大并发任务数
        """
        with self.lock:
            self._check_system_resources()  # 确保返回最新值
            return self.max_concurrent_tasks
    
    def set_max_concurrent_tasks(self, max_tasks: int) -> None:
        """
        设置最大并发任务数
        
        Args:
            max_tasks: 最大并发任务数
        """
        with self.lock:
            if max_tasks > 0:
                self.max_concurrent_tasks = max_tasks
                self.logger.info(f"设置最大并发任务数为: {self.max_concurrent_tasks}")
            else:
                self.logger.error("最大并发任务数必须大于0")
    
    def is_overloaded(self) -> bool:
        """
        判断系统是否过载
        
        Returns:
            bool: 系统是否过载
        """
        with self.lock:
            self._check_system_resources()
            # 如果活跃任务数达到或超过最大并发任务数的80%，认为系统接近过载
            return self.active_tasks >= self.max_concurrent_tasks * 0.8


# 全局并发控制器实例
_global_concurrency_controller = ConcurrencyController()


def get_concurrency_controller() -> ConcurrencyController:
    """
    获取全局并发控制器实例
    
    Returns:
        ConcurrencyController: 全局并发控制器实例
    """
    return _global_concurrency_controller
