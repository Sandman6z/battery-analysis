import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.parallel_utils import Task, ParallelProcessor, parallel_map, parallel_execute


class TestTask:
    def test_task_creation(self):
        def test_func(x):
            return x * 2
        task = Task("test_task", test_func, 5, priority=1)
        assert task.id == "test_task"
        assert task.args == 5
        assert task.priority == 1
        assert task.status == "pending"

    def test_task_comparison(self):
        def test_func(x):
            return x * 2
        task1 = Task("task1", test_func, 1, priority=1)
        task2 = Task("task2", test_func, 2, priority=2)
        assert task1 < task2
        assert not (task2 < task1)


class TestParallelProcessor:
    def test_initialization(self):
        # 测试默认初始化
        processor = ParallelProcessor()
        assert processor.pool_type == "process"
        assert processor.max_workers is None
        
        # 测试自定义初始化
        processor = ParallelProcessor(pool_type="thread", max_workers=4)
        assert processor.pool_type == "thread"
        assert processor.max_workers == 4

    def test_execute_function(self):
        def test_func(x):
            return x * 2
        data = [1, 2, 3, 4, 5]
        processor = ParallelProcessor(pool_type="thread")  # 使用线程池避免进程创建开销
        results = processor.execute_function(test_func, data)
        assert isinstance(results, dict)
        assert results["total"] == len(data)
        assert results["completed"] == len(data)
        assert len(results["success"]) > 0

    def test_map(self):
        def test_func(x):
            return x * 2
        data = [1, 2, 3, 4, 5]
        processor = ParallelProcessor(pool_type="thread")
        results = processor.map(test_func, data)
        assert isinstance(results, list)
        assert len(results) > 0


class TestParallelUtilsFunctions:
    def test_parallel_map(self):
        def test_func(x):
            return x * 2
        data = [1, 2, 3, 4, 5]
        results = parallel_map(test_func, data, pool_type="thread")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_parallel_execute(self):
        def test_func(x):
            return x * 2
        data = [1, 2, 3, 4, 5]
        results = parallel_execute(test_func, data, pool_type="thread")
        assert isinstance(results, dict)
        assert results["total"] == len(data)
        assert results["completed"] == len(data)
        assert len(results["success"]) > 0