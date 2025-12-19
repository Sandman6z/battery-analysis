"""配置文件工具模块

该模块提供了配置文件相关的工具函数，如查找配置文件路径等。
"""

import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# 配置文件路径缓存
_config_path_cache = {}


def find_config_file(file_name: str = "setting.ini", config_dir: str = "config", use_cache: bool = True) -> str:
    """
    在多个可能的位置查找配置文件，并返回第一个找到的配置文件的路径。

    Args:
        file_name: 配置文件名，默认为"setting.ini"
        config_dir: 配置文件所在的目录名，默认为"config"
        use_cache: 是否使用缓存的配置文件路径，默认为True

    Returns:
        第一个找到的配置文件的路径，如果没有找到则返回None
    """
    # 生成缓存键
    cache_key = (file_name, config_dir)

    # 如果使用缓存且缓存中存在，则直接返回
    if use_cache and cache_key in _config_path_cache:
        return _config_path_cache[cache_key]

    # 获取当前文件的目录，用于计算绝对路径
    current_file_dir = Path(__file__).resolve().parent

    # 检查是否在PyInstaller环境中
    if hasattr(os, '_MEIPASS'):
        # PyInstaller环境
        base_dir = os.path.join(os.environ.get('_MEIPASS', ''))
    else:
        # 开发环境
        base_dir = current_file_dir.parent.parent.parent

    # 定义可能的配置文件路径列表
    possible_config_paths = [
        # 1. 当前工作目录下的config目录
        Path.cwd() / config_dir / file_name,
        # 2. 基础目录下的config目录
        Path(base_dir) / config_dir / file_name,
        # 3. 当前工作目录下直接查找
        Path.cwd() / file_name,
        # 4. 基础目录下直接查找
        Path(base_dir) / file_name,
        # 5. 基于当前文件的绝对路径查找（确保在任何位置都能找到）
        current_file_dir.parent.parent.parent / config_dir / file_name
    ]

    # 遍历查找第一个存在的配置文件
    for path in possible_config_paths:
        if path.exists():
            logger.info("找到配置文件: %s", path)
            # 将结果存入缓存
            _config_path_cache[cache_key] = str(path)
            return str(path)

    logger.warning("未找到配置文件: %s", file_name)
    # 将结果存入缓存
    _config_path_cache[cache_key] = None
    return None
