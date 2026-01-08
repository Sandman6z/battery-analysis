"""
ConfigurationRepository接口定义

Domain层的仓库接口，定义配置数据的访问契约
"""

from abc import ABC, abstractmethod
from battery_analysis.domain.entities.configuration import Configuration


class ConfigurationRepository(ABC):
    """配置仓库接口"""
    
    @abstractmethod
    def load(self) -> Configuration:
        """加载配置数据
        
        Returns:
            配置实体对象
        """
        pass
    
    @abstractmethod
    def save(self, configuration: Configuration) -> Configuration:
        """保存配置数据
        
        Args:
            configuration: 配置实体对象
            
        Returns:
            保存后的配置实体对象
        """
        pass
    
    @abstractmethod
    def reset_to_default(self) -> Configuration:
        """重置配置为默认值
        
        Returns:
            默认配置实体对象
        """
        pass
