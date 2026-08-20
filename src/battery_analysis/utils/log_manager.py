"""
日志管理器模块

该模块提供了统一的日志配置和管理功能，包括：
- 控制台日志输出
- 文件日志输出（带轮转功能）
- 环境信息记录
- 统一的日志获取接口
"""

import logging
import logging.handlers
import os
import sys
import datetime
import platform
import psutil
from pathlib import Path


class LogManager:
    """日志管理器类，负责配置和管理应用程序日志"""
    
    def __init__(self):
        """初始化日志管理器"""
        self.log_dir = None
        self.logger = None
        self._current_log_file = None
        self._configure_logging()
    
    def _get_log_directory(self):
        """获取日志文件存储目录
        
        Returns:
            Path: 日志文件目录路径
        """
        if os.name == 'nt':
            # Windows系统，使用AppData\Local目录
            app_data = os.environ.get('LOCALAPPDATA', os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local'))
            log_dir = Path(app_data) / 'BatteryAnalysis' / 'logs'
        else:
            # 非Windows系统，使用用户主目录下的.logs目录
            log_dir = Path.home() / '.logs' / 'battery_analysis'
        
        # 创建目录（如果不存在）
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def _configure_logging(self):
        """配置日志系统"""
        # Windows 下確保 stdout/stderr 使用 UTF-8 編碼，避免中文亂碼
        if os.name == 'nt':
            for stream in (sys.stdout, sys.stderr):
                if hasattr(stream, 'reconfigure') and str(getattr(stream, 'encoding', '')).upper() != 'UTF-8':
                    try:
                        stream.reconfigure(encoding='utf-8')
                    except Exception:
                        pass

        # 获取日志目录
        self.log_dir = self._get_log_directory()
        
        # 创建带时间戳的日志文件名 - 每次启动生成一个新日志文件
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        # 所有日志文件都带时间戳，不再使用无时间戳的主日志文件
        log_file = self.log_dir / f'battery_analysis_{timestamp}.log'
        self._current_log_file = log_file
        
        # 创建主日志记录器
        self.logger = logging.getLogger('battery_analysis')
        self.logger.setLevel(logging.DEBUG)  # 捕获所有级别的日志
        self.logger.propagate = False
        
        # 移除已有的处理器（避免重复配置）
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            handler.close()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)  # 控制台只显示WARNING及以上级别
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器 - 直接创建带时间戳的新日志文件
        file_handler = logging.FileHandler(
            log_file,
            mode='w',  # 每次启动创建新文件
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 清理旧日志文件，只保留10个
        self._cleanup_old_logs(10)
        
        # 环境信息延后记录，不阻塞启动
        # self._log_environment_info() 改由外部在适当时机调用

    def log_environment_info(self):
        """对外暴露：记录环境信息，可在启动完成后调用"""
        self._log_environment_info()

    def _log_environment_info(self):
        """记录应用程序运行环境信息"""
        self.logger.info("=" * 50)
        self.logger.info("Application started")
        self.logger.info(f"Python version: {sys.version}")
        self.logger.info(f"Operating system: {platform.system()} {platform.release()} {platform.version()}")
        self.logger.info(f"Processor: {platform.processor()}")

        # 记录内存信息
        mem = psutil.virtual_memory()
        self.logger.info(f"Total memory: {mem.total / (1024**3):.2f} GB")
        self.logger.info(f"Available memory: {mem.available / (1024**3):.2f} GB")
        self.logger.info(f"Memory usage: {mem.percent}%")

        # 记录CPU信息（interval=0 避免模块导入时的阻塞）
        self.logger.info(f"CPU cores: {psutil.cpu_count(logical=True)}")
        self.logger.info(f"CPU usage: {psutil.cpu_percent(interval=0)}%")

        # 记录应用程序路径
        self.logger.info(f"Application path: {sys.argv[0]}")
        self.logger.info(f"Current working directory: {os.getcwd()}")
        self.logger.info(f"Log file path: {self.log_dir}")
        self.logger.info("=" * 50)
    
    def get_logger(self, name=None):
        """获取日志记录器
        
        Args:
            name: 日志记录器名称，如果为None则返回主日志记录器
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        if name:
            return logging.getLogger(f'battery_analysis.{name}')
        return self.logger
    
    def get_log_directory(self):
        """获取日志目录
        
        Returns:
            Path: 日志目录路径
        """
        return self.log_dir
    
    def _cleanup_old_logs(self, keep_count=10):
        """清理旧日志文件，只保留指定数量的最新日志
        此方法在后台线程中异步执行，避免阻塞应用启动

        Args:
            keep_count: 要保留的日志文件数量
        """
        try:
            # 获取所有日志文件
            all_logs = []
            # 匹配所有日志文件：主日志文件和归档日志文件
            for log_file in self.log_dir.glob('battery_analysis*.log*'):
                try:
                    if self._current_log_file and log_file.samefile(self._current_log_file):
                        continue
                    all_logs.append(log_file)
                except (OSError, PermissionError):
                    continue

            # 按修改时间排序（最新的在前），跳过已被刪除的文件
            def _safe_mtime(p):
                try:
                    return p.stat().st_mtime
                except OSError:
                    return None
            all_logs = [p for p in all_logs if _safe_mtime(p) is not None]
            all_logs.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # 如果日志文件数量超过要保留的数量，删除旧的
            if len(all_logs) > keep_count:
                logs_to_delete = all_logs[keep_count:]
                for log_file in logs_to_delete:
                    self._delete_log_file_with_retry(log_file, max_retries=3)
        except (OSError, PermissionError) as e:
            self.logger.error(f"Failed to clean up old log files: {e}")

    def _delete_log_file_with_retry(self, log_file, max_retries=3):
        """尝试删除日志文件，失败时重试（处理Windows文件锁）

        Args:
            log_file: 要删除的日志文件路径
            max_retries: 最大重试次数
        """
        import time
        for attempt in range(max_retries):
            try:
                log_file.unlink()
                self.logger.info(f"Cleaned up old log file: {log_file}")
                return
            except (OSError, PermissionError) as e:
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))  # 递增等待: 0.1s, 0.2s, 0.3s
                else:
                    self.logger.debug(f"Failed to clean up log file {log_file} (retried {max_retries} times): {e}")

    def clear_old_logs(self, keep_count=10):
        """清理旧日志文件，只保留指定数量的最新日志
        使用线程池异步执行，避免阻塞主线程

        Args:
            keep_count: 要保留的日志文件数量
        """
        import threading
        cleanup_thread = threading.Thread(
            target=self._cleanup_old_logs,
            args=(keep_count,),
            daemon=True,
            name="LogCleanupThread"
        )
        cleanup_thread.start()
        self.logger.debug("Log cleanup task started in the background")


# 创建全局日志管理器实例
_log_manager = None


def get_logger(name=None):
    """获取日志记录器的便捷函数

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器实例
    """
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager.get_logger(name)


def get_log_manager():
    """获取 LogManager 单例

    Returns:
        LogManager: 日志管理器实例
    """
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager


def get_log_directory():
    """获取日志目录的便捷函数
    
    Returns:
        Path: 日志目录路径
    """
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager.get_log_directory()


def clear_old_logs(days=30):
    """清理旧日志文件的便捷函数

    Args:
        days: 保留日志的天数
    """
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    _log_manager.clear_old_logs(days)
