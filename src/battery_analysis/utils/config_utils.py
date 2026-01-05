"""配置文件工具模块

该模块提供了配置文件相关的工具函数，如查找配置文件路径等。
已优化为支持多种环境（开发、IDE、容器、PyInstaller打包）
"""

import os
import sys
from pathlib import Path
import logging

# 导入新的环境检测工具
from .environment_utils import get_environment_detector, EnvironmentType

logger = logging.getLogger(__name__)

# 配置文件路径缓存
_config_path_cache = {}


def find_config_file(
    file_name: str = "setting.ini", 
    config_dir: str = "config", 
    use_cache: bool = True
) -> str:
    """
    在多个可能的位置查找配置文件，并返回第一个找到的配置文件的路径。
    
    支持的环境：
    - 开发环境（IDE、命令行）
    - PyInstaller打包环境
    - 容器环境
    - 生产环境

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

    # 使用新的环境检测器
    env_detector = get_environment_detector()
    env_info = env_detector.get_environment_info()
    
    # 根据环境类型调整搜索策略
    if env_info['environment_type'] == EnvironmentType.CONTAINER:
        logger.debug("容器环境：优先使用标准路径")
        possible_config_paths = _get_container_config_paths(file_name, config_dir, env_info)
    elif env_info['environment_type'] == EnvironmentType.PRODUCTION:
        logger.debug("生产环境：使用打包资源路径")
        possible_config_paths = _get_production_config_paths(file_name, config_dir, env_info)
    else:
        logger.debug("开发环境：使用灵活路径搜索")
        possible_config_paths = _get_development_config_paths(file_name, config_dir, env_info)

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


def _get_container_config_paths(file_name: str, config_dir: str, env_info: dict) -> list:
    """获取容器环境的配置路径列表"""
    paths = []
    
    # 容器环境优先使用标准路径
    standard_paths = [
        # 标准配置路径
        Path("/etc") / "battery_analysis" / config_dir / file_name,
        # 用户配置路径
        Path.home() / ".config" / "battery_analysis" / config_dir / file_name,
        # 应用数据路径
        Path.home() / ".local" / "share" / "battery_analysis" / config_dir / file_name,
    ]
    
    # 开发相关路径
    dev_paths = [
        # 基于项目根目录
        env_info.get('project_root', Path.cwd()) / config_dir / file_name,
        # 当前工作目录
        Path.cwd() / config_dir / file_name,
        # 基于当前文件的路径
        env_info.get('current_file_dir', Path(__file__).parent).parent.parent.parent / config_dir / file_name,
    ]
    
    return standard_paths + dev_paths


def _get_production_config_paths(file_name: str, config_dir: str, env_info: dict) -> list:
    """获取生产环境的配置路径列表"""
    paths = []
    
    # 生产环境优先使用PyInstaller资源路径
    if env_info.get('meipass'):
        # PyInstaller _MEIPASS路径
        meipass_path = Path(env_info['meipass'])
        paths.extend([
            meipass_path / config_dir / file_name,
            meipass_path / file_name,
        ])
    
    # 标准的生产配置路径
    production_paths = [
        # 当前可执行文件目录
        Path(env_info.get('python_executable', sys.executable)).parent / config_dir / file_name,
        # 当前工作目录
        Path.cwd() / config_dir / file_name,
        # 用户配置目录
        Path.home() / ".battery_analysis" / config_dir / file_name,
    ]
    
    return paths + production_paths


def _get_development_config_paths(file_name: str, config_dir: str, env_info: dict) -> list:
    """获取开发环境的配置路径列表"""
    paths = []
    
    # 开发环境使用灵活的路径搜索
    current_file_dir = env_info.get('current_file_dir', Path(__file__).parent)
    project_root = env_info.get('project_root', Path.cwd())
    
    # 优先级顺序：从高到低
    dev_paths = [
        # 1. 项目根目录的config子目录（最优先）
        project_root / config_dir / file_name,
        # 2. 项目根目录的直接文件
        project_root / file_name,
        # 3. 基于当前文件位置的相对路径
        current_file_dir.parent.parent.parent / config_dir / file_name,
        # 4. 当前工作目录
        Path.cwd() / config_dir / file_name,
        # 5. 当前工作目录直接文件
        Path.cwd() / file_name,
        # 6. 相对于脚本位置的config目录
        current_file_dir.parent.parent / config_dir / file_name,
        # 7. 源代码目录的config
        current_file_dir.parent.parent.parent / config_dir / file_name,
    ]
    
    return dev_paths


def get_config_content(file_name: str = "setting.ini", config_dir: str = "config") -> dict:
    """
    获取配置文件内容
    
    Args:
        file_name: 配置文件名
        config_dir: 配置文件目录
        
    Returns:
        配置字典，如果文件不存在则返回空字典
    """
    config_path = find_config_file(file_name, config_dir)
    if not config_path:
        logger.warning("配置文件未找到: %s", file_name)
        return {}
    
    try:
        config = {}
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        
        logger.debug("成功加载配置文件: %s", config_path)
        return config
    except (IOError, OSError, UnicodeDecodeError, ValueError) as e:
        logger.error("读取配置文件失败: %s, 错误: %s", config_path, str(e))
        return {}


def save_config_content(config_data: dict, file_name: str = "setting.ini", config_dir: str = "config") -> bool:
    """
    保存配置到文件
    
    Args:
        config_data: 配置数据字典
        file_name: 配置文件名
        config_dir: 配置文件目录
        
    Returns:
        是否保存成功
    """
    try:
        # 确定保存路径
        env_detector = get_environment_detector()
        save_path = env_detector.get_resource_path(config_dir) / file_name
        
        # 确保目录存在
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存配置
        with open(save_path, 'w', encoding='utf-8') as f:
            for key, value in config_data.items():
                f.write(f"{key}={value}\n")
        
        logger.info("配置文件保存成功: %s", save_path)
        return True
    except (IOError, OSError, UnicodeEncodeError, TypeError, ValueError) as e:
        logger.error("保存配置文件失败: %s", str(e))
        return False
