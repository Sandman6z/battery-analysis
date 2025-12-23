"""版本管理模块

该模块负责获取项目的版本号，支持开发环境和PyInstaller打包环境。
"""

import sys
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# 构建时会被替换的版本常量
# BUILD_VERSION = "2.0.0"
BUILD_VERSION = None

# 兼容性导入：优先使用标准库 tomllib，若不可用则回退到第三方 tomli
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # 作为备选
    except ImportError:
        tomllib = None
        logger.warning("Neither tomllib nor tomli is available")


class Version:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Version, cls).__new__(cls)
            cls._instance.version = cls._instance._get_version()
        return cls._instance

    def __init__(self):
        """初始化版本对象，从pyproject.toml读取版本号或使用默认值"""
        # 显式定义version属性，解决pylint no-member错误
        # 仅在第一次初始化时设置，避免重复调用_get_version()
        if not hasattr(self, 'version'):
            self.version = self._get_version()

    def _get_version(self) -> str:
        """获取项目版本号"""
        try:
            # 首先检查构建时嵌入的版本号
            if BUILD_VERSION is not None:
                logger.info("Using version embedded at build time")
                return BUILD_VERSION
            
            # 然后检查是否在PyInstaller打包环境中
            if getattr(sys, 'frozen', False):
                return self._get_version_from_pyinstaller_environment()
            
            # 最后在开发环境中读取pyproject.toml
            return self._get_version_from_development_environment()
        except (FileNotFoundError, ImportError, IOError) as e:
            logger.error("Error reading version: %s", e)
            return self._get_default_version()

    def _get_version_from_pyinstaller_environment(self) -> str:
        """从PyInstaller打包环境获取版本号
        读取打包在可执行文件中的pyproject.toml文件
        """
        logger.info(
            "Running in PyInstaller environment, reading version from embedded pyproject.toml")
        # 在PyInstaller环境中，当前目录是可执行文件所在目录
        current_dir = Path('.').resolve()
        pyproject_path = current_dir / "pyproject.toml"
        logger.info("Looking for embedded pyproject.toml at: %s", pyproject_path)
        
        return self._read_version_from_file(pyproject_path)

    def _get_version_from_development_environment(self) -> str:
        """从开发环境获取版本号，读取pyproject.toml文件

        Returns:
            版本号字符串
        """
        logger.info(
            "Running in development environment, reading version from pyproject.toml")
        # 获取项目根目录（假设这个文件位于src/battery_analysis/utils/下）
        current_dir = Path(__file__).resolve().parent
        # src/battery_analysis/utils -> src/battery_analysis -> src -> project_root
        project_root = current_dir.parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"
        logger.info("Looking for pyproject.toml at: %s", pyproject_path)

        # 检查文件是否存在
        if not pyproject_path.exists():
            raise FileNotFoundError(
                f"pyproject.toml not found at: {pyproject_path}")

        # 读取pyproject.toml
        if tomllib is None:
            raise ImportError("tomllib/tomli not available for reading TOML")

        version = self._read_version_from_file(pyproject_path)
        return version

    def _read_version_from_file(self, file_path: Path) -> str:
        """从文件中读取版本号"""
        try:
            with open(file_path, "rb") as f:
                pyproject_data = tomllib.load(f)
            version = pyproject_data["project"]["version"]
            return version
        except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError, OSError) as e:
            logger.error("Failed to read version from pyproject.toml: %s", e)
            logger.info("Using default version")
            return self._get_default_version()

    def _get_default_version(self) -> str:
        """获取默认版本号

        Returns:
            默认版本号字符串
        """
        logger.info("Using default version: 2.0.0")
        return "2.0.0"
