from unittest.mock import Mock, patch

from battery_analysis.utils.resource_manager import ResourceManager


class TestResourceManager:
    def setup_method(self):
        self.manager = ResourceManager()

    def test_get_optimal_process_count(self):
        result = self.manager.get_optimal_process_count()
        assert isinstance(result, int)
        assert result >= 1

    def test_cpu_percent_uses_non_blocking_sample(self):
        """cpu_percent 用 interval=None 非阻塞采样，且高负载时缩容进程数。

        原 interval=1 会阻塞调用线程整整 1 秒——在 GUI 主线程触发时直接冻结 UI。
        """
        fake_psutil = Mock()
        fake_psutil.cpu_percent.return_value = 90.0  # 高负载
        fake_psutil.virtual_memory.return_value = Mock(available=32 * 1024**3)
        with patch("battery_analysis.utils.resource_manager.psutil", fake_psutil):
            result = ResourceManager.get_optimal_process_count(max_processes_default=8)
        fake_psutil.cpu_percent.assert_called_once_with(interval=None, percpu=False)
        # 高负载 → 上限 min(8, 2)=2；32GB 内存 → 320 进程不进一步缩
        assert result == 2

    def test_get_processing_context(self):
        result = self.manager.get_processing_context()
        ctx_name = result.get_start_method()
        assert ctx_name == "spawn"
