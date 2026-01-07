"""
文件工具类

提供各种文件操作相关的工具函数
"""

import hashlib
import logging
from pathlib import Path
from typing import List


class FileUtils:
    """
    文件工具类，提供各种文件操作相关的工具函数
    """
    
    @staticmethod
    def calc_md5checksum(file_paths: List[str]) -> str:
        """
        计算文件列表的MD5校验和
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            文件列表的MD5校验和
        """
        md5_hash = hashlib.md5()
        for file_path in file_paths:
            if Path(file_path).exists():
                with open(file_path, "rb") as file:
                    data = file.read()
                    md5_hash.update(data)
        return md5_hash.hexdigest()
