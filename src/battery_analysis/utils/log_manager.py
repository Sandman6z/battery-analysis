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
        # 获取日志目录
        self.log_dir = self._get_log_directory()
        
        # 创建带时间戳的日志文件名 - 每次启动生成一个新日志文件
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        # 所有日志文件都带时间戳，不再使用无时间戳的主日志文件
        log_file = self.log_dir / f'battery_analysis_{timestamp}.log'
        
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
        console_handler.setLevel(logging.INFO)  # 控制台只显示INFO及以上级别
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
        
        # 记录环境信息
        self._log_environment_info()
    
    def _get_windows_activation_status(self):
        """获取Windows系统激活状态
        
        Returns:
            str: 激活状态信息
        """
        if platform.system() != 'Windows':
            return "非Windows系统"
        
        try:
            import subprocess
            import winreg
            
            # 方法1: 尝试从注册表获取激活状态
            try:
                # 尝试从注册表获取激活状态，但不记录过多调试日志
                # 只在成功获取时记录，失败时直接尝试其他方法
                try:
                    key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform"
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, access=winreg.KEY_READ) as key:
                        license_status = winreg.QueryValueEx(key, "LicenseStatus")[0]
                        
                        status_map = {
                            0: "未激活",
                            1: "已激活",
                            2: "OOBGrace",
                            3: "OOTGrace",
                            4: "NonGenuineGrace",
                            5: "Notification",
                            6: "ExtendedGrace"
                        }
                        
                        return f"Windows 激活状态: {status_map.get(license_status, f'未知状态 ({license_status})')}"
                except Exception:
                    # 注册表访问失败，不记录详细日志，直接尝试下一种方法
                    pass
                
                # 不尝试Wow6432Node路径，减少不必要的日志
            except Exception:
                # 捕获所有注册表相关异常，不记录详细日志
                pass
                
            # 方法2: 尝试使用cscript执行slmgr.vbs
            try:
                slmgr_path = "C:\\Windows\\System32\\slmgr.vbs"
                result = subprocess.run(
                    ['cscript', slmgr_path, '/xpr'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return result.stdout.strip() if result.stdout.strip() else "无法获取激活状态"
            except Exception as slmgr_error:
                self.logger.debug(f"使用slmgr获取激活状态失败: {slmgr_error}")
                
            # 方法3: 尝试使用wmic命令
            try:
                result = subprocess.run(
                    ['wmic', 'path', 'SoftwareLicensingProduct', 'where', 'ApplicationID="55c92734-d682-4d71-983e-d6ec3f16059f"', 'get', 'LicenseStatus', '/value'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if "LicenseStatus=1" in result.stdout:
                    return "Windows 已激活"
                elif "LicenseStatus=0" in result.stdout:
                    return "Windows 未激活"
                else:
                    return "无法获取激活状态"
            except Exception as wmic_error:
                self.logger.debug(f"使用wmic获取激活状态失败: {wmic_error}")
                
            return "无法获取激活状态"
        except Exception as e:
            self.logger.debug(f"获取Windows激活状态失败: {e}")
            return "获取激活状态失败"
    
    def _get_windows_edition(self):
        """获取Windows系统版本类型
        
        Returns:
            str: 系统版本类型
        """
        if platform.system() != 'Windows':
            return "非Windows系统"
        
        try:
            import winreg
            # 从注册表获取系统版本
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
                return product_name
        except Exception as e:
            self.logger.debug(f"获取Windows版本类型失败: {e}")
            return "获取版本类型失败"
    
    def _log_environment_info(self):
        """记录应用程序运行环境信息"""
        self.logger.info("=" * 50)
        self.logger.info("应用程序启动")
        self.logger.info(f"Python版本: {sys.version}")
        self.logger.info(f"操作系统: {platform.system()} {platform.release()} {platform.version()}")
        
        # 记录Windows系统详细信息
        if platform.system() == 'Windows':
            self.logger.info(f"Windows版本: {self._get_windows_edition()}")
            self.logger.info(f"激活状态: {self._get_windows_activation_status()}")
        
        self.logger.info(f"计算机名称: {platform.node()}")
        self.logger.info(f"处理器: {platform.processor()}")
        
        # 记录内存信息
        mem = psutil.virtual_memory()
        self.logger.info(f"总内存: {mem.total / (1024**3):.2f} GB")
        self.logger.info(f"可用内存: {mem.available / (1024**3):.2f} GB")
        self.logger.info(f"内存使用率: {mem.percent}%")
        
        # 记录CPU信息
        self.logger.info(f"CPU核心数: {psutil.cpu_count(logical=True)}")
        self.logger.info(f"CPU使用率: {psutil.cpu_percent(interval=1)}%")
        
        # 记录应用程序路径
        self.logger.info(f"应用程序路径: {sys.argv[0]}")
        self.logger.info(f"当前工作目录: {os.getcwd()}")
        self.logger.info(f"日志文件路径: {self.log_dir}")
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
        
        Args:
            keep_count: 要保留的日志文件数量
        """
        try:
            # 获取所有日志文件
            all_logs = []
            # 匹配所有日志文件：主日志文件和归档日志文件
            for log_file in self.log_dir.glob('battery_analysis*.log*'):
                all_logs.append(log_file)
            
            # 按修改时间排序（最新的在前）
            all_logs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # 如果日志文件数量超过要保留的数量，删除旧的
            if len(all_logs) > keep_count:
                logs_to_delete = all_logs[keep_count:]
                for log_file in logs_to_delete:
                    try:
                        log_file.unlink()
                        self.logger.info(f"已清理旧日志文件: {log_file}")
                    except Exception as e:
                        self.logger.warning(f"清理日志文件 {log_file} 失败: {e}")
        except Exception as e:
            self.logger.error(f"清理旧日志文件失败: {e}")
    
    def clear_old_logs(self, keep_count=10):
        """清理旧日志文件，只保留指定数量的最新日志
        
        Args:
            keep_count: 要保留的日志文件数量
        """
        self._cleanup_old_logs(keep_count)


# 创建全局日志管理器实例
_log_manager = LogManager()


def get_logger(name=None):
    """获取日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return _log_manager.get_logger(name)


def get_log_directory():
    """获取日志目录的便捷函数
    
    Returns:
        Path: 日志目录路径
    """
    return _log_manager.get_log_directory()


def clear_old_logs(days=30):
    """清理旧日志文件的便捷函数
    
    Args:
        days: 保留日志的天数
    """
    _log_manager.clear_old_logs(days)
