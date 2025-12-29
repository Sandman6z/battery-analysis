"""
环境检测和适配工具模块

该模块提供了跨平台的环境检测功能，能够：
1. 检测GUI环境是否可用
2. 适配开发环境和生产环境
3. 提供统一的路径处理机制
4. 检测操作系统和显示环境
"""

import os
import sys
import platform
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """环境类型枚举"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    CONTAINER = "container"
    IDE = "ide"
    UNKNOWN = "unknown"


class PlatformType(Enum):
    """平台类型枚举"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"


class EnvironmentDetector:
    """环境检测器类"""
    
    def __init__(self):
        """初始化环境检测器"""
        self._environment_info = None
        self._gui_available = None
        self._is_frozen = getattr(sys, 'frozen', False)
        self._meipass = getattr(sys, '_MEIPASS', None)
        
    def get_environment_info(self) -> Dict[str, Any]:
        """获取完整的环境信息"""
        if self._environment_info is None:
            self._environment_info = {
                'platform': self._detect_platform(),
                'environment_type': self._detect_environment_type(),
                'gui_available': self._detect_gui_availability(),
                'display_available': self._detect_display(),
                'python_executable': sys.executable,
                'python_version': sys.version,
                'is_frozen': self._is_frozen,
                'meipass': self._meipass,
                'working_directory': os.getcwd(),
                'current_file_dir': Path(__file__).parent,
                'project_root': self._find_project_root(),
            }
        return self._environment_info
    
    def _detect_platform(self) -> PlatformType:
        """检测操作系统平台"""
        system = platform.system().lower()
        if system == 'windows':
            return PlatformType.WINDOWS
        elif system == 'linux':
            return PlatformType.LINUX
        elif system == 'darwin':
            return PlatformType.MACOS
        else:
            return PlatformType.UNKNOWN
    
    def _detect_environment_type(self) -> EnvironmentType:
        """检测环境类型"""
        # 检测是否为IDE环境
        if self._is_ide_environment():
            return EnvironmentType.IDE
        
        # 检测是否为容器环境
        if self._is_container_environment():
            return EnvironmentType.CONTAINER
        
        # 检测是否为打包环境
        if self._is_frozen:
            return EnvironmentType.PRODUCTION
        
        # 检测是否为开发环境
        if self._is_development_environment():
            return EnvironmentType.DEVELOPMENT
        
        return EnvironmentType.UNKNOWN
    
    def _is_ide_environment(self) -> bool:
        """检测是否为IDE环境"""
        # 检查常见IDE环境变量
        ide_indicators = [
            'VSCODE_INJECTION',
            'PYCHARM_HOSTED',
            'COMSPEC',  # Windows IDE
            'TERM_PROGRAM',  # macOS/Linux IDE
            'TRAE',
        ]
        
        for indicator in ide_indicators:
            if os.environ.get(indicator):
                logger.debug(f"IDE environment detected via {indicator}")
                return True
        
        # 检查是否在Trae IDE中
        if 'Trae' in str(sys.executable) or 'trae' in str(sys.executable).lower():
            logger.debug("Trae IDE environment detected")
            return True
        
        return False
    
    def _is_container_environment(self) -> bool:
        """检测是否为容器环境"""
        container_indicators = [
            '.dockerenv',
            '/run/.containerenv',
            'container',
            'docker',
            'k8s',
        ]
        
        # 检查文件系统标识
        for indicator in container_indicators:
            if os.path.exists(f'/{indicator}'):
                logger.debug(f"Container environment detected via /{indicator}")
                return True
        
        # 检查环境变量
        env_vars = ['CONTAINER', 'DOCKER', 'KUBERNETES_SERVICE_HOST']
        for var in env_vars:
            if os.environ.get(var):
                logger.debug(f"Container environment detected via {var}")
                return True
        
        return False
    
    def _is_development_environment(self) -> bool:
        """检测是否为开发环境"""
        # 检查是否在虚拟环境中
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.debug("Development environment detected: virtual environment")
            return True
        
        # 检查是否存在开发文件
        dev_indicators = [
            'pyproject.toml',
            '.git',
            'setup.py',
            'requirements.txt',
        ]
        
        project_root = self._find_project_root()
        for indicator in dev_indicators:
            if (project_root / indicator).exists():
                logger.debug(f"Development environment detected: found {indicator}")
                return True
        
        return False
    
    def _detect_gui_availability(self) -> bool:
        """检测GUI环境是否可用"""
        if self._gui_available is not None:
            return self._gui_available
        
        try:
            # 尝试导入PyQt6
            import PyQt6.QtWidgets as QW
            from PyQt6.QtGui import QGuiApplication
            
            # 检查是否有显示环境
            if hasattr(QGuiApplication, 'screens'):
                screens = QGuiApplication.screens()
                if screens:
                    logger.debug(f"GUI available: {len(screens)} screen(s) detected")
                    self._gui_available = True
                    return True
            
            # 检查DISPLAY环境变量（Linux）
            display = os.environ.get('DISPLAY')
            if display:
                logger.debug(f"GUI available: DISPLAY={display}")
                self._gui_available = True
                return True
            
            # Windows下默认有GUI支持
            if self._detect_platform() == PlatformType.WINDOWS:
                logger.debug("GUI available: Windows platform detected")
                self._gui_available = True
                return True
            
            logger.debug("GUI not available: no display environment")
            self._gui_available = False
            return False
            
        except ImportError as e:
            logger.debug(f"GUI not available: PyQt6 import failed: {e}")
            self._gui_available = False
            return False
        except Exception as e:
            logger.debug(f"GUI detection error: {e}")
            self._gui_available = False
            return False
    
    def _detect_display(self) -> Optional[str]:
        """检测显示环境"""
        display = os.environ.get('DISPLAY')
        if display:
            return display
        
        # Windows下检查是否有显示器
        if self._detect_platform() == PlatformType.WINDOWS:
            try:
                import ctypes
                user32 = ctypes.windll.user32
                screens = user32.GetSystemMetrics(80)  # SM_CMONITORS
                if screens > 0:
                    return f"windows_monitor_{screens}"
            except:
                pass
        
        return None
    
    def _find_project_root(self) -> Path:
        """查找项目根目录"""
        current_dir = Path(__file__).parent
        
        # 在打包环境中
        if self._meipass:
            return Path(self._meipass)
        
        # 向上查找项目根目录
        for parent in current_dir.parents:
            if (parent / 'pyproject.toml').exists() or (parent / 'setup.py').exists():
                return parent
        
        # 如果没找到，返回当前工作目录
        return Path.cwd()
    
    def is_gui_mode(self) -> bool:
        """检查是否应该使用GUI模式"""
        info = self.get_environment_info()
        return info['gui_available'] and info['environment_type'] != EnvironmentType.CONTAINER
    
    def is_cli_mode(self) -> bool:
        """检查是否应该使用命令行模式"""
        return not self.is_gui_mode()
    
    def get_project_root(self) -> Path:
        """获取项目根目录的公共接口"""
        return self._find_project_root()
    
    def get_resource_path(self, relative_path: str) -> Path:
        """获取资源文件的正确路径"""
        info = self.get_environment_info()
        
        if self._meipass:
            # PyInstaller环境
            return Path(self._meipass) / relative_path
        else:
            # 开发环境
            return info['project_root'] / relative_path
    
    def get_config_path(self, config_file: str = "setting.ini") -> Optional[Path]:
        """获取配置文件的路径"""
        possible_paths = [
            self.get_resource_path(f"config/{config_file}"),
            Path.cwd() / "config" / config_file,
            Path.cwd() / config_file,
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.debug(f"Config file found: {path}")
                return path
        
        logger.warning(f"Config file not found: {config_file}")
        return None
    
    def get_locale_path(self, locale_file: str = "messages.po") -> Optional[Path]:
        """获取国际化文件的路径"""
        info = self.get_environment_info()
        
        # 尝试多个可能的locale目录
        possible_locale_dirs = [
            self.get_resource_path("locale"),
            info['project_root'] / "locale",
            Path.cwd() / "locale",
        ]
        
        # 尝试多种locale名称
        locale_variants = ["zh_CN", "zh", "en"]
        
        for locale_dir in possible_locale_dirs:
            for locale_name in locale_variants:
                locale_path = locale_dir / locale_name / "LC_MESSAGES" / locale_file
                if locale_path.exists():
                    logger.debug(f"Locale file found: {locale_path}")
                    return locale_path
        
        logger.warning(f"Locale file not found: {locale_file}")
        return None


# 全局环境检测器实例
_environment_detector = None


def get_environment_detector() -> EnvironmentDetector:
    """获取全局环境检测器实例"""
    global _environment_detector
    if _environment_detector is None:
        _environment_detector = EnvironmentDetector()
    return _environment_detector


def is_gui_available() -> bool:
    """检查GUI是否可用（便捷函数）"""
    return get_environment_detector().is_gui_mode()


def get_resource_path(relative_path: str) -> Path:
    """获取资源文件路径（便捷函数）"""
    return get_environment_detector().get_resource_path(relative_path)


def get_config_path(config_file: str = "setting.ini") -> Optional[Path]:
    """获取配置文件路径（便捷函数）"""
    return get_environment_detector().get_config_path(config_file)