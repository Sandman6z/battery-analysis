"""
资源管理器模块，用于根据系统负载动态调整并行处理的资源使用

提供了获取最优进程数和处理上下文的功能，能够根据CPU使用率和内存情况
动态调整并行处理的资源分配，以确保系统性能和稳定性。
"""

import logging
import multiprocessing

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ResourceManager:
    """
    系统资源管理器，用于根据系统负载动态调整并行处理的资源使用
    """

    @staticmethod
    def get_optimal_process_count(max_processes_default: int = 8, min_processes: int = 1) -> int:
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
                # 检测系统CPU使用率（非阻塞采样）
                # interval=None 立即返回自上次调用以来的占用率（首次调用返回 0.0）；
                # 原 interval=1 会阻塞调用线程整整 1 秒，GUI 主线程调用时直接冻结 UI
                # （roadmap #12）。首次调用返回 0.0 → 走低负载默认分支，语义安全。
                cpu_usage = psutil.cpu_percent(interval=None, percpu=False)
                logging.info("Current system CPU usage: %.2f%%", cpu_usage)

                # 根据CPU使用率动态调整进程数
                if cpu_usage > 80:
                    # 系统高负载：仅使用较少核心
                    max_processes = min(max_processes_default, 2)
                    logging.info(
                        "System under high load, adjusted process count to: %d", max_processes
                    )
                elif cpu_usage > 50:
                    # 系统中负载：使用一半核心
                    max_processes = min(max_processes_default, max(2, cpu_count // 2))
                    logging.info(
                        "System under medium load, adjusted process count to: %d", max_processes
                    )
                else:
                    # 系统低负载：使用默认进程数
                    max_processes = max_processes_default
                    logging.info("System under low load, using process count: %d", max_processes)

                # 考虑内存限制（每个进程约100MB内存）
                available_memory_gb = psutil.virtual_memory().available / (1024**3)
                memory_based_processes = int(available_memory_gb * 10)  # 每100MB内存一个进程
                max_processes = min(max_processes, memory_based_processes)
                logging.info(
                    "After considering memory limits, adjusted process count to: %d", max_processes
                )
            except (psutil.Error, OSError) as e:
                # 捕获psutil相关的具体异常
                logging.error("Error getting system resource info: %s", str(e))
        else:
            # 如果psutil不可用，使用默认值
            logging.warning("psutil library unavailable, using default process count")

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
        ctx = multiprocessing.get_context("spawn")
        return ctx
