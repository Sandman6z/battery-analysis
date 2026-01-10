"""文件和路径工具类"""
import hashlib
import os
from pathlib import Path


class FileUtils:
    """文件和路径处理工具类"""
    
    @staticmethod
    def find_file(filename, search_paths):
        """
        在多个路径中查找文件
        
        Args:
            filename: 要查找的文件名
            search_paths: 搜索路径列表
            
        Returns:
            找到的文件路径，否则返回None
        """
        for path in search_paths:
            file_path = Path(path) / filename
            if file_path.exists():
                return file_path
        return None
    
    @staticmethod
    def get_manual_paths(current_directory):
        """
        获取用户手册的可能路径列表
        
        Args:
            current_directory: 当前工作目录
            
        Returns:
            用户手册的可能路径列表
        """
        return [
            # 相对路径
            Path(current_directory) / "docs" / "user_manual.pdf",
            Path(current_directory) / "user_manual.pdf",
            # 绝对路径 - 项目目录
            Path(__file__).parent.parent.parent.parent / "docs" / "user_manual.pdf",
            Path(__file__).parent.parent.parent.parent / "user_manual.pdf",
            # 常见的文档位置
            Path(os.getcwd()) / "docs" / "user_manual.pdf",
            Path(os.getcwd()) / "user_manual.pdf",
        ]
    
    @staticmethod
    def get_icon_paths(env_detector, current_directory):
        """
        获取应用图标的可能路径列表
        
        Args:
            env_detector: 环境检测器
            current_directory: 当前工作目录
            
        Returns:
            应用图标的可能路径列表
        """
        icon_paths = []
        
        # 如果环境检测器可用，使用它来解析路径
        if env_detector:
            icon_paths.extend([
                env_detector.get_resource_path("config/resources/icons/Icon_BatteryTestGUI.ico"),
                env_detector.get_resource_path("resources/icons/Icon_BatteryTestGUI.ico"),
            ])
        
        # 始终尝试相对路径（工程中的图标）
        icon_paths.extend([
            Path(current_directory) / "config" / "resources" / "icons" / "Icon_BatteryTestGUI.ico",
            Path(current_directory) / "resources" / "icons" / "Icon_BatteryTestGUI.ico",
        ])
        
        return icon_paths
    
    @staticmethod
    def calc_md5checksum(file_list):
        """
        计算文件列表的MD5校验和
        
        Args:
            file_list: 要计算MD5的文件路径列表
            
        Returns:
            计算得到的MD5校验和字符串
        """
        try:
            # 确保file_list是列表
            if not isinstance(file_list, list):
                file_list = [file_list]
            
            # 创建MD5对象
            md5 = hashlib.md5()
            
            # 遍历文件列表，计算MD5
            for file_path in file_list:
                with open(file_path, 'rb') as f:
                    # 分块读取文件，避免内存问题
                    for chunk in iter(lambda: f.read(4096), b''):
                        md5.update(chunk)
            
            # 返回MD5校验和
            return md5.hexdigest()
        except Exception as e:
            # 记录错误但不中断程序
            import logging
            logger = logging.getLogger(__name__)
            logger.error("计算MD5校验和失败: %s", e)
            return ""
