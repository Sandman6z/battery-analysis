# -*- coding: utf-8 -*-
"""
国际化服务模块

提供国际化的抽象接口和实现
"""

import logging
from typing import Optional, List, Dict, Any


class II18nService:
    """
    国际化服务接口
    """
    
    def _(self, text: str, context: Optional[str] = None) -> str:
        """
        获取翻译文本

        Args:
            text: 原文
            context: 上下文

        Returns:
            str: 翻译后的文本
        """
        raise NotImplementedError
    
    def set_language(self, language_code: str) -> bool:
        """
        设置语言

        Args:
            language_code: 语言代码

        Returns:
            bool: 设置是否成功
        """
        raise NotImplementedError
    
    def get_current_language(self) -> str:
        """
        获取当前语言

        Returns:
            str: 当前语言代码
        """
        raise NotImplementedError
    
    def get_available_languages(self) -> List[str]:
        """
        获取可用语言列表

        Returns:
            List[str]: 可用语言代码列表
        """
        raise NotImplementedError


class I18nService(II18nService):
    """
    国际化服务实现
    """
    
    def __init__(self):
        """
        初始化国际化服务
        """
        self.logger = logging.getLogger(__name__)
        self._language_manager = None
        self._current_language = "zh_CN"  # 默认中文
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """
        初始化国际化服务

        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("Initializing I18nService...")
            
            # 导入语言管理器
            try:
                from battery_analysis.i18n.language_manager import get_language_manager
                self._language_manager = get_language_manager()
                self.logger.info("I18nService initialized with language manager")
            except ImportError as e:
                self.logger.warning("Language manager not available: %s", e)
                # 使用简单的内部实现
                self._current_language = "zh_CN"
                self.is_initialized = True
                return True
            
            self.is_initialized = True
            self.logger.info("I18nService initialized successfully")
            return True
            
        except (ImportError, ValueError, TypeError, OSError) as e:
            self.logger.error("Failed to initialize I18nService: %s", e)
            return False
    
    def _(self, text: str, context: Optional[str] = None) -> str:
        """
        获取翻译文本

        Args:
            text: 原文
            context: 上下文

        Returns:
            str: 翻译后的文本
        """
        try:
            if self._language_manager:
                if context:
                    return self._language_manager.pgettext(context, text)
                else:
                    return self._language_manager.gettext(text)
            else:
                # 简单的回退实现
                return text
                
        except (AttributeError, KeyError, TypeError) as e:
            self.logger.error("Translation error for '%s': %s", text, e)
            return text
    
    def set_language(self, language_code: str) -> bool:
        """
        设置语言

        Args:
            language_code: 语言代码

        Returns:
            bool: 设置是否成功
        """
        try:
            if self._language_manager:
                success = self._language_manager.set_locale(language_code)
                if success:
                    self._current_language = language_code
                    self.logger.info("Language set to: %s", language_code)
                    return True
                else:
                    self.logger.error("Failed to set language: %s", language_code)
                    return False
            else:
                self._current_language = language_code
                self.logger.info("Language set to (simple): %s", language_code)
                return True
                
        except (AttributeError, ValueError, OSError) as e:
            self.logger.error("Failed to set language %s: %s", language_code, e)
            return False
    
    def get_current_language(self) -> str:
        """
        获取当前语言

        Returns:
            str: 当前语言代码
        """
        try:
            if self._language_manager:
                return self._language_manager.get_current_locale()
            else:
                return self._current_language
                
        except (AttributeError, OSError) as e:
            self.logger.error("Failed to get current language: %s", e)
            return self._current_language
    
    def get_available_languages(self) -> List[str]:
        """
        获取可用语言列表

        Returns:
            List[str]: 可用语言代码列表
        """
        try:
            if self._language_manager:
                return self._language_manager.get_available_locales()
            else:
                # 默认返回支持的语言
                return ["zh_CN", "en"]
                
        except (AttributeError, OSError) as e:
            self.logger.error("Failed to get available languages: %s", e)
            return ["zh_CN", "en"]
    
    def reload_translations(self) -> bool:
        """
        重新加载翻译

        Returns:
            bool: 重新加载是否成功
        """
        try:
            if self._language_manager:
                return self._language_manager.reload_translations()
            else:
                self.logger.info("Translation reload skipped (simple implementation)")
                return True
                
        except (AttributeError, OSError, IOError) as e:
            self.logger.error("Failed to reload translations: %s", e)
            return False
    
    def translate_ui_text(self, ui_element: str, default_text: str = "") -> str:
        """
        翻译UI文本

        Args:
            ui_element: UI元素标识
            default_text: 默认文本

        Returns:
            str: 翻译后的UI文本
        """
        # 使用上下文进行翻译
        return self._(ui_element, context="ui")
    
    def translate_status_message(self, message: str) -> str:
        """
        翻译状态消息

        Args:
            message: 状态消息

        Returns:
            str: 翻译后的状态消息
        """
        # 使用上下文进行翻译
        return self._(message, context="status")
