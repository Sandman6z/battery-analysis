# -*- coding: utf-8 -*-
"""
文件服务接口模块

提供文件操作相关的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Optional, Union, List, Tuple
from pathlib import Path


class IFileService(ABC):
    """
    文件服务接口
    提供文件操作相关功能
    """
    
    @abstractmethod
    def create_directory(self, path: Union[str, Path]) -> Tuple[bool, str]:
        """
        创建目录
        
        Args:
            path: 目录路径
            
        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
    
    @abstractmethod
    def delete_directory(self, path: Union[str, Path], recursive: bool = False) -> Tuple[bool, str]:
        """
        删除目录
        
        Args:
            path: 目录路径
            recursive: 是否递归删除
            
        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
    
    @abstractmethod
    def list_files(self, directory: Union[str, Path], pattern: Optional[str] = None) -> List[str]:
        """
        列出目录中的文件
        
        Args:
            directory: 目录路径
            pattern: 文件名模式
            
        Returns:
            List[str]: 文件名列表
        """
        pass
    
    @abstractmethod
    def get_file_size(self, file_path: Union[str, Path]) -> Optional[int]:
        """
        获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[int]: 文件大小，失败返回None
        """
        pass
    
    @abstractmethod
    def set_file_attributes(self, file_path: Union[str, Path], attributes: dict) -> Tuple[bool, str]:
        """
        设置文件属性
        
        Args:
            file_path: 文件路径
            attributes: 属性字典
            
        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
    
    @abstractmethod
    def hide_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        隐藏文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
    
    @abstractmethod
    def is_file_hidden(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否隐藏
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 文件是否隐藏
        """
        pass
    
    @abstractmethod
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        复制文件
        
        Args:
            source: 源文件路径
            destination: 目标文件路径
            
        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
    
    @abstractmethod
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        移动文件
        
        Args:
            source: 源文件路径
            destination: 目标文件路径
            
        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
    
    @abstractmethod
    def delete_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
