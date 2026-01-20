"""
内存映射模块

提供大文件的内存映射功能，减少内存使用，提高文件处理效率。
"""
import os
import logging
from typing import Optional, Any


try:
    import mmap
    MMAP_AVAILABLE = True
except ImportError:
    MMAP_AVAILABLE = False


class MemoryMapper:
    """
    内存映射类，用于处理大文件
    """
    
    def __init__(self):
        """
        初始化内存映射器
        """
        self.logger = logging.getLogger(__name__)
        if not MMAP_AVAILABLE:
            self.logger.warning("mmap模块不可用，内存映射功能将被禁用")
    
    def map_file(self, file_path: str, mode: str = 'r') -> Optional[Any]:
        """
        映射文件到内存
        
        Args:
            file_path: 文件路径
            mode: 打开模式，支持 'r' (读取) 和 'rb' (二进制读取)
            
        Returns:
            Optional[Any]: 内存映射对象，如果失败返回None
        """
        if not MMAP_AVAILABLE:
            self.logger.warning("mmap模块不可用，无法映射文件")
            return None
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.logger.error(f"文件不存在: {file_path}")
                return None
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 对于大文件（超过10MB）使用内存映射
            if file_size < 10 * 1024 * 1024:  # 10MB
                self.logger.debug(f"文件较小 ({file_size / (1024 * 1024):.2f}MB)，不使用内存映射")
                return None
            
            self.logger.info(f"映射文件到内存: {file_path} ({file_size / (1024 * 1024):.2f}MB)")
            
            # 打开文件
            open_mode = 'rb' if 'b' in mode else 'r'
            with open(file_path, open_mode) as f:
                # 创建内存映射
                access_mode = mmap.ACCESS_READ
                mm = mmap.mmap(f.fileno(), length=0, access=access_mode)
                return mm
        except Exception as e:
            self.logger.error(f"映射文件失败: {str(e)}")
            return None
    
    def read_from_mmap(self, mm: Any, offset: int = 0, length: Optional[int] = None) -> Optional[bytes]:
        """
        从内存映射对象读取数据
        
        Args:
            mm: 内存映射对象
            offset: 偏移量
            length: 读取长度
            
        Returns:
            Optional[bytes]: 读取的数据，如果失败返回None
        """
        if not MMAP_AVAILABLE or mm is None:
            return None
        
        try:
            # 确保偏移量有效
            if offset < 0 or offset >= mm.size():
                self.logger.error(f"无效的偏移量: {offset}")
                return None
            
            # 计算读取长度
            if length is None:
                length = mm.size() - offset
            else:
                length = min(length, mm.size() - offset)
            
            # 读取数据
            mm.seek(offset)
            data = mm.read(length)
            return data
        except Exception as e:
            self.logger.error(f"从内存映射读取失败: {str(e)}")
            return None
    
    def search_in_mmap(self, mm: Any, pattern: bytes, start_offset: int = 0) -> Optional[int]:
        """
        在内存映射对象中搜索模式
        
        Args:
            mm: 内存映射对象
            pattern: 要搜索的模式
            start_offset: 开始搜索的偏移量
            
        Returns:
            Optional[int]: 找到的位置，如果未找到返回None
        """
        if not MMAP_AVAILABLE or mm is None:
            return None
        
        try:
            # 确保偏移量有效
            if start_offset < 0 or start_offset >= mm.size():
                self.logger.error(f"无效的偏移量: {start_offset}")
                return None
            
            # 搜索模式
            mm.seek(start_offset)
            position = mm.find(pattern)
            
            if position == -1:
                return None
            else:
                return position
        except Exception as e:
            self.logger.error(f"在内存映射中搜索失败: {str(e)}")
            return None
    
    def close_mmap(self, mm: Any) -> bool:
        """
        关闭内存映射对象
        
        Args:
            mm: 内存映射对象
            
        Returns:
            bool: 是否成功关闭
        """
        if not MMAP_AVAILABLE or mm is None:
            return False
        
        try:
            mm.close()
            self.logger.debug("内存映射已关闭")
            return True
        except Exception as e:
            self.logger.error(f"关闭内存映射失败: {str(e)}")
            return False
    
    @staticmethod
    def is_large_file(file_path: str, threshold: int = 10 * 1024 * 1024) -> bool:
        """
        检查文件是否为大文件
        
        Args:
            file_path: 文件路径
            threshold: 大文件阈值（字节），默认10MB
            
        Returns:
            bool: 是否为大文件
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            file_size = os.path.getsize(file_path)
            return file_size > threshold
        except Exception as e:
            logging.getLogger(__name__).error(f"检查文件大小失败: {str(e)}")
            return False
