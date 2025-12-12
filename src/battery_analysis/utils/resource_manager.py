import multiprocessing
import logging


class ResourceManager:
    """
    系统资源管理器，用于根据系统负载动态调整并行处理的资源使用
    """
    
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
        
        try:
            import psutil
            
            # 检测系统CPU使用率（1秒平均值）
            cpu_usage = psutil.cpu_percent(interval=1, percpu=False)
            logging.info(f"当前系统CPU使用率: {cpu_usage}%")
            
            # 根据CPU使用率动态调整进程数
            if cpu_usage > 80:
                # 系统高负载：仅使用较少核心
                max_processes = min(max_processes_default, 2)
                logging.info(f"系统高负载，调整进程数为: {max_processes}")
            elif cpu_usage > 50:
                # 系统中负载：使用一半核心
                max_processes = min(max_processes_default, max(2, cpu_count // 2))
                logging.info(f"系统中负载，调整进程数为: {max_processes}")
            else:
                # 系统低负载：使用默认进程数
                max_processes = max_processes_default
                logging.info(f"系统低负载，使用进程数: {max_processes}")
            
            # 考虑内存限制（每个进程约100MB内存）
            available_memory_gb = psutil.virtual_memory().available / (1024 ** 3)
            memory_based_processes = int(available_memory_gb * 10)  # 每100MB内存一个进程
            max_processes = min(max_processes, memory_based_processes)
            logging.info(f"考虑内存限制后，调整进程数为: {max_processes}")
            
        except ImportError:
            # 如果psutil不可用，使用默认值
            logging.warning("psutil库不可用，使用默认进程数")
        except Exception as e:
            # 捕获其他异常，避免影响程序运行
            logging.error(f"动态调整进程数时出错: {str(e)}")
        
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