"""版本管理模块

该模块负责获取项目的版本号，支持开发环境和PyInstaller打包环境。
"""

import sys
import os
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

# 版本管理现在统一从pyproject.toml读取

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
        """初始化版本对象，从pyproject.toml读取版本号"""
        # 显式定义version属性，解决pylint no-member错误
        # 仅在第一次初始化时设置，避免重复调用_get_version()
        if not hasattr(self, 'version'):
            self.version = self._get_version()

    def _get_version(self) -> str:
        """获取项目版本号
        直接从pyproject.toml读取版本号，适用于所有环境
        唯一区别是debug环境可能会添加额外后缀
        """
        try:
            # 从pyproject.toml读取版本号（适用于所有环境）
            version = self._get_version_from_pyproject_toml()

            # 添加debug后缀（如果是debug环境）
            if self._is_debug_environment():
                version += ".debug"
                logger.info("Debug environment detected, version with suffix: %s", version)

            return version
        except (FileNotFoundError, ImportError, IOError, PermissionError) as e:
            logger.error("Error reading version: %s", e)
            return self._get_default_version()

    def _get_version_from_pyproject_toml(self) -> str:
        """从pyproject.toml文件获取版本号
        支持开发环境和PyInstaller打包环境

        Returns:
            版本号字符串
        """
        # 确定pyproject.toml文件的路径
        pyproject_path = None

        # 检查是否在PyInstaller环境中
        if getattr(sys, '_MEIPASS', False):
            # PyInstaller 1.6+ 会设置 _MEIPASS 环境变量
            base_path = Path(sys._MEIPASS)  # pylint: disable=protected-access
            pyproject_path = base_path / "pyproject.toml"
            logger.info(
                "Running in PyInstaller environment, "
                "looking for pyproject.toml at: %s", pyproject_path
            )
        else:
            # 开发环境或构建环境：从文件系统路径查找
            # 尝试多种可能的路径
            possible_paths = [
                # 1. 当前脚本所在目录的上级目录（开发环境）
                Path(__file__).resolve().parent.parent.parent / "pyproject.toml",
                # 2. 当前工作目录
                Path.cwd() / "pyproject.toml",
                # 3. 构建过程中的临时目录
                Path("__temp__") / "pyproject.toml",
                # 4. 构建脚本所在目录的上级目录
                Path(sys.argv[0]).resolve().parent.parent / "pyproject.toml"
            ]
            
            for path in possible_paths:
                if path.exists():
                    pyproject_path = path
                    logger.info(
                        "Found pyproject.toml at: %s", pyproject_path
                    )
                    break
            
            # 如果没有找到，使用默认路径
            if pyproject_path is None:
                current_dir = Path(__file__).resolve().parent
                project_root = current_dir.parent.parent.parent
                pyproject_path = project_root / "pyproject.toml"
                logger.info(
                    "Defaulting to pyproject.toml at: %s", pyproject_path
                )

        # 检查文件是否存在
        if not pyproject_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at: {pyproject_path}")

        # 读取pyproject.toml
        if tomllib is None:
            raise ImportError("tomllib/tomli not available for reading TOML")

        version = self._read_version_from_file(pyproject_path)
        return version

    def _read_version_from_file(self, file_path: Path) -> str:
        """从文件中读取版本号"""
        try:
            # 先尝试按TOML文件读取（开发环境）
            if "pyproject.toml" in file_path.name:
                with open(file_path, "rb") as f:
                    pyproject_data = tomllib.load(f)
                return pyproject_data["project"]["version"]
            # 否则按纯文本文件读取（生产环境）
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError, OSError) as e:
            logger.error("Failed to read version from %s: %s", file_path.name, e)
            logger.info("Using default version")
            return self._get_default_version()

    def _get_default_version(self) -> str:
        """获取默认版本号

        Returns:
            默认版本号字符串
        """
        logger.info("Using default version: 2.0.0")
        return "2.0.0"

    def _is_debug_environment(self) -> bool:
        """检测是否为debug环境

        Returns:
            True if debug environment, False otherwise
        """
        # 检查环境变量
        if os.environ.get("DEBUG", "").lower() in ("true", "1", "yes"):
            logger.debug("Debug environment detected via DEBUG environment variable")
            return True

        if os.environ.get("APP_DEBUG", "").lower() in ("true", "1", "yes"):
            logger.debug("Debug environment detected via APP_DEBUG environment variable")
            return True

        # 检查命令行参数
        if "--debug" in sys.argv:
            logger.debug("Debug environment detected via --debug command line argument")
            return True

        # 检查PyInstaller的debug标志
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            # 在PyInstaller环境中，可以通过检查构建类型来判断
            # 这里可以根据实际构建过程中的标志来扩展
            pass

        logger.debug("Not in debug environment")
        return False
