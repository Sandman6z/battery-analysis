"""环境管理器模块"""
import logging


class EnvironmentManager:
    """环境信息管理器"""
    
    def __init__(self, main_window):
        """
        初始化环境管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def initialize_environment_info(self):
        """
        初始化环境信息
        """
        try:
            environment_service = self.main_window._get_service("environment")
            if environment_service:
                if hasattr(environment_service, 'env_info'):
                    self.main_window.env_info = environment_service.env_info
                elif hasattr(environment_service, 'initialize'):
                    if environment_service.initialize() and hasattr(environment_service, 'env_info'):
                        self.main_window.env_info = environment_service.env_info
        except (AttributeError, TypeError, ImportError, OSError) as e:
            self.logger.warning("Failed to initialize environment service: %s", e)
    
    def ensure_env_info_keys(self):
        """
        确保环境信息包含必要的键
        """
        # 确保environment_type键存在
        if 'environment_type' not in self.main_window.env_info:
            try:
                environment_service = self.main_window._get_service("environment")
                if environment_service and hasattr(environment_service, 'EnvironmentType'):
                    self.main_window.env_info['environment_type'] = environment_service.EnvironmentType.DEVELOPMENT
                else:
                    # 降级到直接导入
                    from battery_analysis.utils.environment_utils import EnvironmentType
                    self.main_window.env_info['environment_type'] = EnvironmentType.DEVELOPMENT
            except (AttributeError, TypeError, ImportError) as e:
                self.logger.warning("Failed to get EnvironmentType: %s", e)
                from battery_analysis.utils.environment_utils import EnvironmentType
                self.main_window.env_info['environment_type'] = EnvironmentType.DEVELOPMENT
        
        # 确保gui_available键存在
        if 'gui_available' not in self.main_window.env_info:
            self.main_window.env_info['gui_available'] = True
    
    def initialize_all(self):
        """
        初始化所有环境信息
        """
        self.initialize_environment_info()
        self.ensure_env_info_keys()
