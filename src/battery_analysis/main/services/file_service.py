# -*- coding: utf-8 -*-
"""
文件服务模块

提供文件操作的抽象接口和实现
"""

import logging
import os
import shutil
from typing import Optional, List, Dict, Any, Tuple, Union
from pathlib import Path
from .file_service_interface import IFileService


class FileService(IFileService):
    """
    文件服务实现
    """
    
    def __init__(self):
        """
        初始化文件服务
        """
        self.logger = logging.getLogger(__name__)
    
    def create_directory(self, path: Union[str, Path]) -> Tuple[bool, str]:
        """
        创建目录

        Args:
            path: 目录路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        try:
            directory = Path(path)
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Directory created: {path}")
            return True, ""
            
        except Exception as e:
            error_msg = f"创建目录失败: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def delete_directory(self, path: Union[str, Path], recursive: bool = False) -> Tuple[bool, str]:
        """
        删除目录

        Args:
            path: 目录路径
            recursive: 是否递归删除

        Returns:
            tuple: (是否成功, 错误消息)
        """
        try:
            dir_path = Path(path)
            if not dir_path.exists():
                return False, f"目录不存在: {path}"
            
            if not dir_path.is_dir():
                return False, f"路径不是目录: {path}"
            
            if recursive:
                shutil.rmtree(path)
            else:
                dir_path.rmdir()
            
            self.logger.info(f"Directory deleted: {path}")
            return True, ""
            
        except Exception as e:
            error_msg = f"删除目录失败: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def list_files(self, directory: Union[str, Path], pattern: Optional[str] = None) -> List[str]:
        """
        列出目录中的文件

        Args:
            directory: 目录路径
            pattern: 文件名模式

        Returns:
            List[str]: 文件名列表
        """
        try:
            dir_path = Path(directory)
            if not dir_path.exists() or not dir_path.is_dir():
                self.logger.error(f"Directory not found: {directory}")
                return []
            
            if pattern:
                files = [f.name for f in dir_path.glob(pattern) if f.is_file()]
            else:
                files = [f.name for f in dir_path.iterdir() if f.is_file()]
            
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to list files in {directory}: {e}")
            return []
    
    def get_file_size(self, file_path: Union[str, Path]) -> Optional[int]:
        """
        获取文件大小

        Args:
            file_path: 文件路径

        Returns:
            Optional[int]: 文件大小，失败返回None
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                return path.stat().st_size
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get file size for {file_path}: {e}")
            return None
    
    def is_file_hidden(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否隐藏

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否隐藏
        """
        try:
            import win32api
            import win32con
            
            path = str(file_path)
            attrs = win32api.GetFileAttributes(path)
            return bool(attrs & win32con.FILE_ATTRIBUTE_HIDDEN)
            
        except ImportError:
            self.logger.warning("win32api不可用，无法检查文件隐藏属性")
            return False
        except Exception as e:
            self.logger.error(f"检查文件隐藏属性失败: {e}")
            return False
    
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        复制文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        try:
            # 确保目标目录存在
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            shutil.copy2(source, destination)
            self.logger.info(f"文件复制成功: {source} -> {destination}")
            return True, ""
            
        except Exception as e:
            error_msg = f"复制文件失败: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        移动文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        try:
            # 确保目标目录存在
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 移动文件
            shutil.move(str(source), str(destination))
            self.logger.info(f"文件移动成功: {source} -> {destination}")
            return True, ""
            
        except Exception as e:
            error_msg = f"移动文件失败: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def delete_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        删除文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False, f"文件不存在: {file_path}"
            
            if not path.is_file():
                return False, f"路径不是文件: {file_path}"
            
            path.unlink()
            self.logger.info(f"文件删除成功: {file_path}")
            return True, ""
            
        except Exception as e:
            error_msg = f"删除文件失败: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def set_file_attributes(self, file_path: Union[str, Path], attributes: dict) -> Tuple[bool, str]:
        """
        设置文件属性

        Args:
            file_path: 文件路径
            attributes: 属性字典

        Returns:
            tuple: (是否成功, 错误消息)
        """
        try:
            import win32api
            import win32con
            
            path = str(file_path)
            
            # 设置文件属性
            if 'hidden' in attributes and attributes['hidden']:
                win32api.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_HIDDEN)
            
            if 'readonly' in attributes and attributes['readonly']:
                current_attrs = win32api.GetFileAttributes(path)
                win32api.SetFileAttributes(path, current_attrs | win32con.FILE_ATTRIBUTE_READONLY)
            
            self.logger.info(f"File attributes set for {file_path}: {attributes}")
            return True, ""
            
        except ImportError:
            error_msg = "win32api不可用，无法设置文件属性"
            self.logger.warning(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"设置文件属性失败: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def hide_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        隐藏文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        return self.set_file_attributes(file_path, {'hidden': True})
    
    def get_directory_info(self, directory: str) -> Dict[str, Any]:
        """
        获取目录信息

        Args:
            directory: 目录路径

        Returns:
            Dict[str, Any]: 目录信息
        """
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return {}
            
            return {
                'path': str(dir_path),
                'exists': True,
                'is_directory': True,
                'is_file': False,
                'size': 0,  # 目录大小
                'modified': dir_path.stat().st_mtime,
                'files': self.list_files(directory),
                'subdirectories': [str(p) for p in dir_path.iterdir() if p.is_dir()]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get directory info for {directory}: {e}")
            return {}
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: 文件信息
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {}
            
            stat = path.stat()
            return {
                'path': str(path),
                'exists': True,
                'is_directory': False,
                'is_file': True,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': path.suffix,
                'name': path.name,
                'stem': path.stem
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {e}")
            return {}
