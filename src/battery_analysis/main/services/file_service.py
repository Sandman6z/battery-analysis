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
        # 初始化缓存，用于存储文件系统操作结果
        self._cache = {
            'list_files': {},
            'get_file_size': {},
            'is_file_hidden': {},
            'get_directory_info': {},
            'get_file_info': {}
        }
    
    def _invalidate_cache(self, path=None):
        """
        使缓存失效
        
        Args:
            path: 可选的路径，用于更精确地失效缓存
        """
        if path:
            # 失效与特定路径相关的缓存
            path_str = str(path)
            for cache_type in self._cache:
                if cache_type == 'list_files':
                    # 失效包含此路径的目录列表缓存
                    keys_to_remove = []
                    for key in self._cache[cache_type]:
                        if path_str in key:
                            keys_to_remove.append(key)
                    for key in keys_to_remove:
                        del self._cache[cache_type][key]
                elif cache_type in ['get_file_size', 'is_file_hidden', 'get_file_info']:
                    # 失效特定文件的缓存
                    if path_str in self._cache[cache_type]:
                        del self._cache[cache_type][path_str]
                elif cache_type == 'get_directory_info':
                    # 失效特定目录的缓存
                    if path_str in self._cache[cache_type]:
                        del self._cache[cache_type][path_str]
        else:
            # 完全清空缓存
            self._cache = {
                'list_files': {},
                'get_file_size': {},
                'is_file_hidden': {},
                'get_directory_info': {},
                'get_file_info': {}
            }
    
    def clear_cache(self):
        """
        清空所有缓存
        """
        self._invalidate_cache()
        self.logger.info("FileService cache cleared")
    
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
            self.logger.info("Directory created: %s", path)
            
            # 使缓存失效
            self._invalidate_cache(path)
            
            return True, ""
            
        except (OSError, PermissionError, IsADirectoryError) as e:
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
            
            self.logger.info("Directory deleted: %s", path)
            
            # 使缓存失效
            self._invalidate_cache(path)
            
            return True, ""
            
        except (OSError, PermissionError, FileNotFoundError, NotADirectoryError) as e:
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
            # 构建缓存键
            cache_key = f"{str(directory)}:{pattern}"
            
            # 检查缓存
            if cache_key in self._cache['list_files']:
                return self._cache['list_files'][cache_key]
            
            dir_path = Path(directory)
            if not dir_path.exists() or not dir_path.is_dir():
                self.logger.error("Directory not found: %s", directory)
                return []
            
            if pattern:
                files = [f.name for f in dir_path.glob(pattern) if f.is_file()]
            else:
                files = [f.name for f in dir_path.iterdir() if f.is_file()]
            
            # 缓存结果
            self._cache['list_files'][cache_key] = files
            
            return files
            
        except (OSError, PermissionError, FileNotFoundError, NotADirectoryError) as e:
            self.logger.error("Failed to list files in %s: %s", directory, e)
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
            file_path_str = str(file_path)
            
            # 检查缓存
            if file_path_str in self._cache['get_file_size']:
                return self._cache['get_file_size'][file_path_str]
            
            path = Path(file_path)
            if path.exists() and path.is_file():
                size = path.stat().st_size
                # 缓存结果
                self._cache['get_file_size'][file_path_str] = size
                return size
            else:
                return None
                
        except (OSError, PermissionError, FileNotFoundError, IsADirectoryError) as e:
            self.logger.error("Failed to get file size for %s: %s", file_path, e)
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
            file_path_str = str(file_path)
            
            # 检查缓存
            if file_path_str in self._cache['is_file_hidden']:
                return self._cache['is_file_hidden'][file_path_str]
            
            import win32api
            import win32con
            
            path = file_path_str
            attrs = win32api.GetFileAttributes(path)
            hidden = bool(attrs & win32con.FILE_ATTRIBUTE_HIDDEN)
            
            # 缓存结果
            self._cache['is_file_hidden'][file_path_str] = hidden
            
            return hidden
            
        except ImportError:
            self.logger.warning("win32api不可用，无法检查文件隐藏属性")
            return False
        except (OSError, PermissionError, FileNotFoundError, IsADirectoryError) as e:
            self.logger.error("检查文件隐藏属性失败: %s", e)
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
            self.logger.info("文件复制成功: %s -> %s", source, destination)
            
            # 使缓存失效
            self._invalidate_cache(source)
            self._invalidate_cache(destination)
            
            return True, ""
            
        except (OSError, PermissionError, FileNotFoundError, IsADirectoryError) as e:
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
            self.logger.info("文件移动成功: %s -> %s", source, destination)
            
            # 使缓存失效
            self._invalidate_cache(source)
            self._invalidate_cache(destination)
            
            return True, ""
            
        except (OSError, PermissionError, FileNotFoundError, IsADirectoryError) as e:
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
            self.logger.info("文件删除成功: %s", file_path)
            
            # 使缓存失效
            self._invalidate_cache(file_path)
            
            return True, ""
            
        except (OSError, PermissionError, FileNotFoundError, IsADirectoryError) as e:
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
            
            self.logger.info("File attributes set for %s: %s", file_path, attributes)
            
            # 使缓存失效
            self._invalidate_cache(file_path)
            
            return True, ""
            
        except ImportError:
            error_msg = "win32api不可用，无法设置文件属性"
            self.logger.warning(error_msg)
            return False, error_msg
        except (OSError, PermissionError, FileNotFoundError, IsADirectoryError) as e:
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
            # 检查缓存
            if directory in self._cache['get_directory_info']:
                return self._cache['get_directory_info'][directory]
            
            dir_path = Path(directory)
            if not dir_path.exists():
                return {}
            
            info = {
                'path': str(dir_path),
                'exists': True,
                'is_directory': True,
                'is_file': False,
                'size': 0,  # 目录大小
                'modified': dir_path.stat().st_mtime,
                'files': self.list_files(directory),
                'subdirectories': [str(p) for p in dir_path.iterdir() if p.is_dir()]
            }
            
            # 缓存结果
            self._cache['get_directory_info'][directory] = info
            
            return info
            
        except (OSError, PermissionError, FileNotFoundError, NotADirectoryError) as e:
            self.logger.error("Failed to get directory info for %s: %s", directory, e)
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
            # 检查缓存
            if file_path in self._cache['get_file_info']:
                return self._cache['get_file_info'][file_path]
            
            path = Path(file_path)
            if not path.exists():
                return {}
            
            stat = path.stat()
            info = {
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
            
            # 缓存结果
            self._cache['get_file_info'][file_path] = info
            
            return info
            
        except (OSError, PermissionError, FileNotFoundError, IsADirectoryError) as e:
            self.logger.error("Failed to get file info for %s: %s", file_path, e)
            return {}
