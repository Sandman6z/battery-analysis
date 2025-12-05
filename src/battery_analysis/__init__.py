"""电池测试数据分析App包初始化"""

import os
import sys
import tomllib
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _get_version_from_pyproject():
    """从pyproject.toml文件中读取版本号（版本号中心化管理）"""
    # 检查是否在PyInstaller环境中运行
    if hasattr(sys, '_MEIPASS'):
        logging.info("在PyInstaller环境中运行，使用构建时嵌入的版本号")
        # 构建时嵌入的实际版本号
        return "2.0.1"
    
    # 获取项目根目录
    package_dir = Path(__file__).parent.parent.parent  # 向上三层到项目根目录
    pyproject_path = package_dir / "pyproject.toml"
    
    try:
        # 使用tomllib解析TOML文件（Python 3.11+）
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        
        # 从pyproject.toml中获取版本号，使用安全的字典访问方式
        version = pyproject_data.get("project", {}).get("version", "2.0.0")
        logging.info(f"从pyproject.toml读取版本号: {version}")
        return version
    except Exception as e:
        # 如果无法读取版本号，使用默认版本作为回退
        logging.warning(f"无法从pyproject.toml读取版本号: {e}")
        logging.info("使用默认版本: 2.0.0")
        return "2.0.1"

# 从pyproject.toml读取版本号
__version__ = _get_version_from_pyproject()

# 导出版本号供外部使用
__all__ = ["__version__"]
