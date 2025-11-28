"""电池测试数据分析App包初始化"""

import os
import tomllib
from pathlib import Path

def _get_version_from_pyproject():
    """从pyproject.toml文件中读取版本号"""
    # 获取项目根目录
    package_dir = Path(__file__).parent.parent.parent  # 向上三层到项目根目录
    pyproject_path = package_dir / "pyproject.toml"
    
    try:
        # 使用tomllib解析TOML文件（Python 3.11+）
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        
        # 从pyproject.toml中获取版本号
        return pyproject_data["project"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError) as e:
        # 如果无法读取版本号，使用默认版本作为回退
        print(f"Warning: Could not read version from pyproject.toml: {e}")
        return "2.0.0"

# 从pyproject.toml读取版本号
__version__ = _get_version_from_pyproject()

# 导出版本号供外部使用
__all__ = ["__version__"]
