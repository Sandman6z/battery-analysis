# -*- coding: utf-8 -*-
"""
并行处理工具
提供通用的并行处理框架，支持多种任务类型
"""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Any, Callable, List, Dict, Optional, Tuple, TypeVar, Generic
import logging
import time


T = TypeVar('T')
R = TypeVar('R')


class Task(Generic[T, R]):
    """
    任务类
    """
    
    def __init__(self, id: str, func: Callable[[T], R], args: T, priority: int = 0):
        """
        初始化任务
        
        Args:
            id: 任务ID
            func: 任务函数
            args: 任务参数
            priority: 任务优先级，值越大优先级越高
        """
        self.id = id
        self.func = func
        self.args = args
        self.priority = priority
        self.status = "pending"
        self.result: Optional[R] = None
        self.error: Optional[Exception] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def __lt__(self, other: 'Task') -> bool:
        """
        任务比较，用于优先级排序
        
        Args:
            other: 另一个任务
        
        Returns:
            bool: 当前任务是否小于另一个任务
        """
        return self.priority < other.priority


class ParallelProcessor:
    """
    并行处理器
    """
    
    def __init__(self, pool_type: str = "process", max_workers: Optional[int] = None):
        """
        初始化并行处理器
        
        Args:
            pool_type: 池类型，"process"或"thread"
            max_workers: 最大工作线程/进程数
        """
        self.pool_type = pool_type
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        
    def group_tasks(
        self, 
        tasks: List[Task], 
        num_groups: int
    ) -> List[List[Task]]:
        """
        将任务分组，确保每个组的负载均衡
        
        Args:
            tasks: 任务列表
            num_groups: 分组数量
        
        Returns:
            List[List[Task]]: 分组后的任务列表
        """
        if num_groups <= 0:
            return [tasks]
        
        # 按优先级排序任务（优先级高的任务先处理）
        sorted_tasks = sorted(tasks, reverse=True)
        
        # 初始化任务组
        groups = [[] for _ in range(num_groups)]
        group_loads = [0] * num_groups
        
        # 分配任务到负载最小的组
        for task in sorted_tasks:
            # 假设任务负载与优先级成正比
            task_load = task.priority + 1  # 确保负载至少为1
            
            # 找到负载最小的组
            min_load_idx = group_loads.index(min(group_loads))
            
            # 将任务添加到该组
            groups[min_load_idx].append(task)
            group_loads[min_load_idx] += task_load
        
        return groups
    
    def execute_tasks(
        self, 
        tasks: List[Task], 
        progress_callback: Optional[Callable[[int, int], None]] = None,
        use_task_grouping: bool = True
    ) -> Dict[str, Any]:
        """
        执行任务列表
        
        Args:
            tasks: 任务列表
            progress_callback: 进度回调函数，接收(已完成数, 总数)作为参数
            use_task_grouping: 是否使用任务分组进行负载均衡
        
        Returns:
            Dict[str, Any]: 执行结果，包含成功和失败的任务
        """
        results = {
            "success": [],
            "failed": [],
            "total": len(tasks),
            "completed": 0,
            "start_time": time.time(),
            "end_time": None
        }
        
        if not tasks:
            results["end_time"] = time.time()
            return results
        
        # 创建执行器
        if self.pool_type == "process":
            executor = ProcessPoolExecutor(max_workers=self.max_workers)
        else:
            executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        try:
            # 提交所有任务
            future_to_task = {}
            
            if use_task_grouping and self.max_workers:
                # 对于进程池，不使用任务分组，因为序列化嵌套函数会导致问题
                # 特别是在第二次运行时，可能会导致进程池初始化失败
                if self.pool_type == "process":
                    # 对于进程池，使用传统方式逐个提交任务
                    for task in tasks:
                        future = executor.submit(self._execute_task, task)
                        future_to_task[future] = task
                else:
                    # 对于线程池，可以使用任务分组
                    # 使用任务分组进行负载均衡
                    num_groups = min(self.max_workers, len(tasks))
                    task_groups = self.group_tasks(tasks, num_groups)
                    
                    # 为每个任务组创建一个执行函数
                    def execute_task_group(task_group):
                        group_results = []
                        for task in task_group:
                            try:
                                result = ParallelProcessor._execute_task(task)
                                task.result = result
                                task.status = "completed"
                                task.end_time = time.time()
                                group_results.append((task, True))
                            except Exception as e:
                                task.error = e
                                task.status = "failed"
                                task.end_time = time.time()
                                group_results.append((task, False))
                        return group_results
                    
                    # 提交任务组
                    for i, task_group in enumerate(task_groups):
                        if task_group:
                            future = executor.submit(execute_task_group, task_group)
                            future_to_task[future] = task_group
            else:
                # 传统方式：逐个提交任务
                for task in tasks:
                    future = executor.submit(self._execute_task, task)
                    future_to_task[future] = task
            
            # 收集结果
            completed_count = 0
            for future in as_completed(future_to_task):
                task_or_group = future_to_task[future]
                
                try:
                    result = future.result()
                    
                    # 处理任务组结果
                    if isinstance(result, list):
                        for task, success in result:
                            if success:
                                results["success"].append(task)
                                self.logger.debug("Task %s completed successfully", task.id)
                            else:
                                results["failed"].append(task)
                                self.logger.error("Task %s failed: %s", task.id, str(task.error))
                            completed_count += 1
                            
                            # 调用进度回调
                            if progress_callback:
                                progress_callback(completed_count, len(tasks))
                    else:
                        # 处理单个任务结果
                        task = task_or_group
                        task.result = result
                        task.status = "completed"
                        task.end_time = time.time()
                        results["success"].append(task)
                        completed_count += 1
                        self.logger.debug("Task %s completed successfully", task.id)
                        
                        # 调用进度回调
                        if progress_callback:
                            progress_callback(completed_count, len(tasks))
                except Exception as e:
                    # 处理执行异常
                    if isinstance(task_or_group, list):
                        # 任务组执行失败
                        for task in task_or_group:
                            task.error = e
                            task.status = "failed"
                            task.end_time = time.time()
                            results["failed"].append(task)
                            completed_count += 1
                            
                            # 调用进度回调
                            if progress_callback:
                                progress_callback(completed_count, len(tasks))
                    else:
                        # 单个任务执行失败
                        task = task_or_group
                        task.error = e
                        task.status = "failed"
                        task.end_time = time.time()
                        results["failed"].append(task)
                        completed_count += 1
                        self.logger.error("Task %s failed: %s", task.id, str(e))
                        
                        # 调用进度回调
                        if progress_callback:
                            progress_callback(completed_count, len(tasks))
            
            results["completed"] = completed_count
            results["end_time"] = time.time()
            self.logger.info("Parallel processing completed: %d/%d tasks succeeded", 
                           len(results["success"]), len(tasks))
            
        finally:
            # 关闭执行器
            executor.shutdown(wait=True)
        
        return results
    
    @staticmethod
    def _execute_task(task: Task) -> Any:
        """
        执行单个任务
        
        Args:
            task: 任务对象
        
        Returns:
            Any: 任务结果
        """
        task.start_time = time.time()
        task.status = "running"
        
        try:
            result = task.func(task.args)
            return result
        except Exception as e:
            task.error = e
            raise
    
    def execute_function(
        self, 
        func: Callable[[T], R], 
        args_list: List[T], 
        task_ids: Optional[List[str]] = None,
        pool_type: Optional[str] = None,
        max_workers: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        use_task_grouping: bool = True
    ) -> Dict[str, Any]:
        """
        执行单个函数的多个参数
        
        Args:
            func: 要执行的函数
            args_list: 参数列表
            task_ids: 任务ID列表，可选
            pool_type: 池类型，覆盖实例设置
            max_workers: 最大工作线程/进程数，覆盖实例设置
            progress_callback: 进度回调函数
            use_task_grouping: 是否使用任务分组进行负载均衡
        
        Returns:
            Dict[str, Any]: 执行结果
        """
        # 创建任务列表
        tasks = []
        for i, args in enumerate(args_list):
            task_id = task_ids[i] if task_ids and i < len(task_ids) else f"task_{i}"
            task = Task(task_id, func, args)
            tasks.append(task)
        
        # 执行任务
        original_pool_type = self.pool_type
        original_max_workers = self.max_workers
        
        if pool_type:
            self.pool_type = pool_type
        if max_workers:
            self.max_workers = max_workers
        
        try:
            return self.execute_tasks(tasks, progress_callback, use_task_grouping)
        finally:
            # 恢复原始设置
            self.pool_type = original_pool_type
            self.max_workers = original_max_workers
    
    def map(
        self, 
        func: Callable[[T], R], 
        iterable: List[T], 
        pool_type: Optional[str] = None,
        max_workers: Optional[int] = None,
        use_task_grouping: bool = True
    ) -> List[R]:
        """
        类似内置map函数的并行版本
        
        Args:
            func: 要执行的函数
            iterable: 可迭代对象
            pool_type: 池类型，覆盖实例设置
            max_workers: 最大工作线程/进程数，覆盖实例设置
            use_task_grouping: 是否使用任务分组进行负载均衡
        
        Returns:
            List[R]: 函数结果列表
        """
        # 转换为列表
        args_list = list(iterable)
        
        # 执行任务
        results = self.execute_function(func, args_list, pool_type=pool_type, max_workers=max_workers, use_task_grouping=use_task_grouping)
        
        # 提取结果
        result_list = []
        for task in results["success"] + results["failed"]:
            if task.result is not None:
                result_list.append(task.result)
        
        return result_list


def parallel_map(
    func: Callable[[T], R], 
    iterable: List[T], 
    pool_type: str = "process",
    max_workers: Optional[int] = None,
    use_task_grouping: bool = True
) -> List[R]:
    """
    并行map函数
    
    Args:
        func: 要执行的函数
        iterable: 可迭代对象
        pool_type: 池类型，"process"或"thread"
        max_workers: 最大工作线程/进程数
        use_task_grouping: 是否使用任务分组进行负载均衡
    
    Returns:
        List[R]: 函数结果列表
    """
    processor = ParallelProcessor(pool_type=pool_type, max_workers=max_workers)
    return processor.map(func, iterable, use_task_grouping=use_task_grouping)


def parallel_execute(
    func: Callable[[T], R], 
    args_list: List[T], 
    task_ids: Optional[List[str]] = None,
    pool_type: str = "process",
    max_workers: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    use_task_grouping: bool = True
) -> Dict[str, Any]:
    """
    并行执行函数
    
    Args:
        func: 要执行的函数
        args_list: 参数列表
        task_ids: 任务ID列表，可选
        pool_type: 池类型，"process"或"thread"
        max_workers: 最大工作线程/进程数
        progress_callback: 进度回调函数
        use_task_grouping: 是否使用任务分组进行负载均衡
    
    Returns:
        Dict[str, Any]: 执行结果
    """
    processor = ParallelProcessor(pool_type=pool_type, max_workers=max_workers)
    return processor.execute_function(func, args_list, task_ids, progress_callback=progress_callback, use_task_grouping=use_task_grouping)


# 导出公共API
__all__ = [
    'Task',
    'ParallelProcessor',
    'parallel_map',
    'parallel_execute'
]