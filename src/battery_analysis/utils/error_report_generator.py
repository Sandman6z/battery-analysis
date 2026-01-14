"""
错误报告生成器模块

该模块提供了错误报告生成功能，方便客户反馈问题，包括：
- 系统环境信息收集
- 最近日志文件收集
- 错误报告压缩包生成
"""

import os
import sys
import datetime
import platform
import psutil
import zipfile
import tempfile
from pathlib import Path
from battery_analysis.utils.log_manager import get_logger, get_log_directory


class ErrorReportGenerator:
    """错误报告生成器类"""
    
    def __init__(self):
        """初始化错误报告生成器"""
        self.logger = get_logger('error_report_generator')
        self.log_dir = get_log_directory()
    
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
    
    def _collect_system_info(self):
        """收集系统信息
        
        Returns:
            dict: 系统信息字典
        """
        try:
            system_info = {
                'timestamp': datetime.datetime.now().isoformat(),
                'python_version': sys.version,
                'os': {
                    'name': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'architecture': platform.architecture()[0],
                    'machine': platform.machine(),
                    'node': platform.node()
                },
                'hardware': {
                    'processor': platform.processor(),
                    'cpu_count': psutil.cpu_count(logical=True),
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory': {
                        'total': psutil.virtual_memory().total,
                        'available': psutil.virtual_memory().available,
                        'percent': psutil.virtual_memory().percent
                    },
                    'disk': {
                        'total': psutil.disk_usage('/').total,
                        'used': psutil.disk_usage('/').used,
                        'free': psutil.disk_usage('/').free,
                        'percent': psutil.disk_usage('/').percent
                    }
                },
                'application': {
                    'path': sys.argv[0],
                    'cwd': os.getcwd(),
                    'pid': os.getpid()
                }
            }
            
            # 添加Windows系统详细信息
            if platform.system() == 'Windows':
                system_info['os']['windows_edition'] = self._get_windows_edition()
                system_info['os']['activation_status'] = self._get_windows_activation_status()
            
            return system_info
        except Exception as e:
            self.logger.error(f"收集系统信息失败: {e}")
            return {'error': str(e), 'timestamp': datetime.datetime.now().isoformat()}
    
    def _get_recent_log_files(self, max_count=10):
        """获取最近的日志文件
        
        Args:
            max_count: 要获取的最大日志文件数量
            
        Returns:
            list: 日志文件路径列表
        """
        try:
            # 获取所有日志文件
            all_logs = []
            # 匹配所有日志文件：主日志文件和归档日志文件
            for log_file in self.log_dir.glob('battery_analysis*.log*'):
                # 排除压缩包文件
                if not log_file.name.endswith('.zip'):
                    all_logs.append(log_file)
            
            # 按修改时间排序（最新的在前）
            all_logs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # 只返回最近的max_count个文件
            return all_logs[:max_count]
        except Exception as e:
            self.logger.error(f"获取最近日志文件失败: {e}")
            return []
    
    def _cleanup_old_reports(self, keep_count=10):
        """清理旧的错误报告压缩包，只保留指定数量
        
        Args:
            keep_count: 要保留的压缩包数量
        """
        try:
            # 获取所有压缩包文件
            all_reports = list(self.log_dir.glob('battery_analysis_error_report_*.zip'))
            
            # 按修改时间排序（最新的在前）
            all_reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # 如果压缩包数量超过要保留的数量，删除旧的
            if len(all_reports) > keep_count:
                reports_to_delete = all_reports[keep_count:]
                for report in reports_to_delete:
                    try:
                        report.unlink()
                        self.logger.info(f"已清理旧压缩包: {report}")
                    except Exception as e:
                        self.logger.warning(f"清理压缩包 {report} 失败: {e}")
        except Exception as e:
            self.logger.error(f"清理旧压缩包失败: {e}")
    
    def _create_system_info_file(self, temp_dir):
        """创建系统信息文件
        
        Args:
            temp_dir: 临时目录路径
            
        Returns:
            Path: 系统信息文件路径
        """
        try:
            system_info = self._collect_system_info()
            info_file = temp_dir / 'system_info.txt'
            
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + '\n')
                f.write("电池分析应用 - 错误报告\n")
                f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + '\n\n')
                
                # 写入系统信息
                f.write("【系统信息】\n")
                if 'error' in system_info:
                    f.write(f"收集系统信息时出错: {system_info['error']}\n\n")
                else:
                    f.write(f"Python版本: {system_info['python_version']}\n")
                    f.write(f"操作系统: {system_info['os']['name']} {system_info['os']['release']} {system_info['os']['version']}\n")
                    
                    # 写入Windows系统详细信息
                    if system_info['os']['name'] == 'Windows':
                        if 'windows_edition' in system_info['os']:
                            f.write(f"Windows版本: {system_info['os']['windows_edition']}\n")
                        if 'activation_status' in system_info['os']:
                            f.write(f"激活状态: {system_info['os']['activation_status']}\n")
                    
                    f.write(f"计算机名称: {system_info['os']['node']}\n")
                    f.write(f"处理器: {system_info['hardware']['processor']}\n")
                    f.write(f"CPU核心数: {system_info['hardware']['cpu_count']}\n")
                    f.write(f"CPU使用率: {system_info['hardware']['cpu_percent']}%\n")
                    
                    mem = system_info['hardware']['memory']
                    f.write(f"总内存: {mem['total'] / (1024**3):.2f} GB\n")
                    f.write(f"可用内存: {mem['available'] / (1024**3):.2f} GB\n")
                    f.write(f"内存使用率: {mem['percent']}%\n")
                    
                    disk = system_info['hardware']['disk']
                    f.write(f"磁盘总空间: {disk['total'] / (1024**3):.2f} GB\n")
                    f.write(f"磁盘已用空间: {disk['used'] / (1024**3):.2f} GB\n")
                    f.write(f"磁盘可用空间: {disk['free'] / (1024**3):.2f} GB\n")
                    f.write(f"磁盘使用率: {disk['percent']}%\n")
                    
                    f.write(f"应用程序路径: {system_info['application']['path']}\n")
                    f.write(f"当前工作目录: {system_info['application']['cwd']}\n\n")
            
            return info_file
        except Exception as e:
            self.logger.error(f"创建系统信息文件失败: {e}")
            return None
    
    def generate_error_report(self, max_logs_per_report=10, max_reports=10):
        """生成错误报告，保存在日志目录中
        
        Args:
            max_logs_per_report: 每个报告包含的最大日志文件数量
            max_reports: 最多保留的报告数量
            
        Returns:
            str: 生成的报告文件路径，失败则返回None
        """
        try:
            self.logger.info("开始生成错误报告...")
            
            # 输出目录使用日志目录
            output_dir = self.log_dir
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建临时目录用于组装报告内容
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                
                # 创建系统信息文件
                system_info_file = self._create_system_info_file(temp_dir_path)
                if system_info_file is None:
                    self.logger.error("生成系统信息文件失败")
                    return None
                
                # 获取最近的日志文件，每个报告包含指定数量的日志
                recent_logs = self._get_recent_log_files(max_logs_per_report)
                logs_dir = temp_dir_path / 'logs'
                logs_dir.mkdir(exist_ok=True)
                
                # 复制日志文件到临时目录
                for log_file in recent_logs:
                    try:
                        # 复制日志文件到临时目录
                        dest_path = logs_dir / log_file.name
                        dest_path.write_bytes(log_file.read_bytes())
                        self.logger.debug(f"已复制日志文件: {log_file.name}")
                    except Exception as e:
                        self.logger.warning(f"复制日志文件 {log_file.name} 失败: {e}")
                
                # 创建报告文件名
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                report_filename = f'battery_analysis_error_report_{timestamp}.zip'
                report_path = output_dir / report_filename
                
                # 创建压缩包
                with zipfile.ZipFile(report_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # 添加系统信息文件
                    zipf.write(system_info_file, arcname='system_info.txt')
                    
                    # 添加日志文件
                    for log_file in logs_dir.glob('*'):
                        zipf.write(log_file, arcname=f'logs/{log_file.name}')
                
                self.logger.info(f"错误报告已生成: {report_path}")
                
                # 清理旧的压缩包，只保留指定数量
                self._cleanup_old_reports(max_reports)
                
                return str(report_path)
                
        except Exception as e:
            self.logger.error(f"生成错误报告失败: {e}", exc_info=True)
            return None
    
    def get_report_info(self):
        """获取报告相关信息
        
        Returns:
            dict: 报告信息
        """
        recent_logs = self._get_recent_log_files()
        return {
            'log_directory': str(self.log_dir),
            'recent_log_files': [str(f) for f in recent_logs],
            'log_file_count': len(recent_logs)
        }


# 创建全局错误报告生成器实例
_error_report_generator = ErrorReportGenerator()


def generate_error_report(max_logs_per_report=10, max_reports=10):
    """生成错误报告的便捷函数
    
    Args:
        max_logs_per_report: 每个报告包含的最大日志文件数量
        max_reports: 最多保留的报告数量
        
    Returns:
        str: 生成的报告文件路径，失败则返回None
    """
    return _error_report_generator.generate_error_report(max_logs_per_report, max_reports)


def get_report_info():
    """获取报告相关信息的便捷函数
    
    Returns:
        dict: 报告信息
    """
    return _error_report_generator.get_report_info()
