# -*- coding: utf-8 -*-
"""
并行处理工具
提供通用的并行处理框架，支持多种任务类型
"""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Any, Callable, List, Dict, Optional, TypeVar, Generic
from dataclasses import dataclass
import logging
import time


T = TypeVar('T')
R = TypeVar('R')


@dataclass
class ExecutionParams:
    """
    执行参数配置
    """
    func: Callable[[T], R]
    args_list: List[T]
    task_ids: Optional[List[str]] = None
    pool_type: Optional[str] = None
    max_workers: Optional[int] = None
    progress_callback: Optional[Callable[[int, int], None]] = None


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
        
    def execute_tasks(
        self,
        tasks: List[Task],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        执行任务列表
        
        Args:
            tasks: 任务列表
            progress_callback: 进度回调函数，接收(已完成数, 总数)作为参数
        
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
            for task in tasks:
                future = executor.submit(self._execute_task, task)
                future_to_task[future] = task
            
            # 收集结果
            completed_count = 0
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                completed_count += 1
                
                try:
                    result = future.result()
                    task.result = result
                    task.status = "completed"
                    task.end_time = time.time()
                    results["success"].append(task)
                    self.logger.debug("Task %s completed successfully", task.id)
                except Exception as e:
                    task.error = e
                    task.status = "failed"
                    task.end_time = time.time()
                    results["failed"].append(task)
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
    
    def _execute_task(self, task: Task) -> Any:
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
        params: ExecutionParams
    ) -> Dict[str, Any]:
        """
        执行单个函数的多个参数
        
        Args:
            params: 执行参数配置
        
        Returns:
            Dict[str, Any]: 执行结果
        """
        # 创建任务列表
        tasks = []
        for i, args in enumerate(params.args_list):
            task_id = params.task_ids[i] if params.task_ids and i < len(params.task_ids) else f"task_{i}"
            task = Task(task_id, params.func, args)
            tasks.append(task)
        
        # 执行任务
        original_pool_type = self.pool_type
        original_max_workers = self.max_workers
        
        if params.pool_type:
            self.pool_type = params.pool_type
        if params.max_workers:
            self.max_workers = params.max_workers
        
        try:
            return self.execute_tasks(tasks, params.progress_callback)
        finally:
            # 恢复原始设置
            self.pool_type = original_pool_type
            self.max_workers = original_max_workers
    
    def map(
        self,
        func: Callable[[T], R],
        iterable: List[T],
        pool_type: Optional[str] = None,
        max_workers: Optional[int] = None
    ) -> List[R]:
        """
        类似内置map函数的并行版本
        
        Args:
            func: 要执行的函数
            iterable: 可迭代对象
            pool_type: 池类型，覆盖实例设置
            max_workers: 最大工作线程/进程数，覆盖实例设置
        
        Returns:
            List[R]: 函数结果列表
        """
        # 转换为列表
        args_list = list(iterable)
        
        # 执行任务
        execution_params = ExecutionParams(
            func=func,
            args_list=args_list,
            pool_type=pool_type,
            max_workers=max_workers
        )
        results = self.execute_function(execution_params)
        
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
    max_workers: Optional[int] = None
) -> List[R]:
    """
    并行map函数
    
    Args:
        func: 要执行的函数
        iterable: 可迭代对象
        pool_type: 池类型，"process"或"thread"
        max_workers: 最大工作线程/进程数
    
    Returns:
        List[R]: 函数结果列表
    """
    processor = ParallelProcessor(pool_type=pool_type, max_workers=max_workers)
    return processor.map(func, iterable)


def parallel_execute(
    func: Callable[[T], R],
    args_list: List[T],
    task_ids: Optional[List[str]] = None,
    pool_type: str = "process",
    max_workers: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
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
    
    Returns:
        Dict[str, Any]: 执行结果
    """
    processor = ParallelProcessor(pool_type=pool_type, max_workers=max_workers)
    execution_params = ExecutionParams(
        func=func,
        args_list=args_list,
        task_ids=task_ids,
        progress_callback=progress_callback
    )
    return processor.execute_function(execution_params)


# 导出公共API
__all__ = [
    'Task',
    'ParallelProcessor',
    'ExecutionParams',
    'parallel_map',
    'parallel_execute'
]
