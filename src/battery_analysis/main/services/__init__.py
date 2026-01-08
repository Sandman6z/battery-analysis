# -*- coding: utf-8 -*-
"""
服务模块初始化文件
导出所有服务类和接口
"""

# 服务类
from .application_service import ApplicationService
from .config_service import ConfigService
from .environment_service import EnvironmentService
from .event_bus import EventBus
from .file_service import FileService
from .i18n_service import I18nService
from .progress_service import ProgressService
from .service_container import ServiceContainer, get_service_container
from .validation_service import ValidationService

# 服务接口
from .config_service_interface import IConfigService
from .data_processing_service_interface import IDataProcessingService
from .document_service_interface import IDocumentService
from .file_service_interface import IFileService
from .validation_service_interface import IValidationService

__all__ = [
    # 服务类
    "ApplicationService",
    "ConfigService",
    "EnvironmentService",
    "EventBus",
    "FileService",
    "I18nService",
    "ProgressService",
    "ServiceContainer",
    "get_service_container",
    "ValidationService",
    
    # 服务接口
    "IConfigService",
    "IDataProcessingService",
    "IDocumentService",
    "IFileService",
    "IValidationService"
]