"""
语言管理模块

提供应用程序的国际化支持，包括：
- 多语言翻译文件管理
- 动态语言切换
- 翻译文本获取
- 语言偏好设置保存和加载
"""

import json
import os
import logging
import locale
import platform
from pathlib import Path
from typing import Dict, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal, QSettings


class LanguageManager(QObject):
    """语言管理器类，负责管理应用程序的多语言支持"""
    
    # 信号定义
    language_changed = pyqtSignal(str)  # 语言切换信号
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_language = "en"
        self.supported_languages = {
            "en": "English",
            "zh_CN": "简体中文"
        }
        
        # 初始化设置
        self.settings = QSettings()
        
        # 加载翻译文件
        self._load_translations()
        
        # 初始化语言设置（首次启动检测系统语言）
        self._initialize_language_settings()
        
        # 设置默认语言
        self._set_default_language()
    
    def _load_settings(self):
        """从设置中加载语言偏好"""
        try:
            saved_language = self.settings.value("language", None)
            if saved_language and saved_language in self.supported_languages:
                self.current_language = saved_language
                self.logger.info(f"已加载保存的语言设置: {self.current_language}")
                return True
        except Exception as e:
            self.logger.error(f"加载语言设置失败: {e}")
        return False
    
    def _initialize_language_settings(self):
        """初始化语言设置 - 首次启动时使用英文作为默认语言"""
        # 首先尝试加载保存的设置
        if self._load_settings():
            # 有保存的设置，使用保存的语言
            return
        
        # 没有保存的设置，默认使用英文
        self.current_language = "en"
        self.logger.info("首次启动，使用默认语言: en")
        
        # 标记已完成首次启动设置
        self._save_settings()
    
    def _detect_system_language(self) -> Optional[str]:
        """检测系统默认语言"""
        try:
            # 尝试多种方法检测系统语言
            system_lang = None
            
            # 方法1: 使用locale模块
            try:
                # 获取系统默认locale
                system_locale = locale.getdefaultlocale()[0]
                if system_locale:
                    # 将 locale 转换为语言代码
                    if system_locale.startswith('zh'):
                        system_lang = 'zh_CN'
                    elif system_locale.startswith('en'):
                        system_lang = 'en'
                    self.logger.debug(f"通过locale检测到系统语言: {system_locale} -> {system_lang}")
            except Exception as e:
                self.logger.debug(f"locale语言检测失败: {e}")
            
            # 方法2: 使用platform模块（Windows特定）
            if not system_lang and platform.system() == "Windows":
                try:
                    import ctypes
                    # 获取系统默认UI语言
                    user_language = ctypes.windll.kernel32.GetUserDefaultUILanguage()
                    if user_language == 2052:  # 中文(简体) LCID
                        system_lang = 'zh_CN'
                    elif user_language == 1033:  # 英语(美国) LCID
                        system_lang = 'en'
                    self.logger.debug(f"通过Windows API检测到系统语言: {user_language} -> {system_lang}")
                except Exception as e:
                    self.logger.debug(f"Windows API语言检测失败: {e}")
            
            # 方法3: 环境变量
            if not system_lang:
                env_lang = os.environ.get('LANG', os.environ.get('LC_ALL', ''))
                if env_lang:
                    if env_lang.startswith('zh'):
                        system_lang = 'zh_CN'
                    elif env_lang.startswith('en'):
                        system_lang = 'en'
                    self.logger.debug(f"通过环境变量检测到系统语言: {env_lang} -> {system_lang}")
            
            # 方法4: 系统区域设置（Windows）
            if not system_lang and platform.system() == "Windows":
                try:
                    import ctypes
                    # 获取系统默认语言
                    system_language = ctypes.windll.kernel32.GetSystemDefaultLangID()
                    if system_language == 2052:  # 中文(简体) LCID
                        system_lang = 'zh_CN'
                    elif system_language == 1033:  # 英语(美国) LCID
                        system_lang = 'en'
                    self.logger.debug(f"通过系统默认语言检测到: {system_language} -> {system_lang}")
                except Exception as e:
                    self.logger.debug(f"系统默认语言检测失败: {e}")
            
            return system_lang
            
        except Exception as e:
            self.logger.error(f"检测系统语言时发生错误: {e}")
            return None
    
    def _save_settings(self):
        """保存语言偏好到设置"""
        try:
            self.settings.setValue("language", self.current_language)
            self.logger.info(f"已保存语言设置: {self.current_language}")
        except Exception as e:
            self.logger.error(f"保存语言设置失败: {e}")
    
    def _load_translations(self):
        """加载所有翻译文件"""
        i18n_dir = Path(__file__).parent
        self.logger.info(f"正在加载翻译文件，目录: {i18n_dir}")
        
        for lang_code in self.supported_languages.keys():
            translation_file = i18n_dir / f"{lang_code}.json"
            
            if translation_file.exists():
                try:
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                    self.logger.info(f"成功加载翻译文件: {translation_file}")
                except Exception as e:
                    self.logger.error(f"加载翻译文件失败 {translation_file}: {e}")
                    self.translations[lang_code] = {}
            else:
                self.logger.warning(f"翻译文件不存在: {translation_file}")
                self.translations[lang_code] = {}
    
    def _set_default_language(self):
        """设置默认语言"""
        if self.current_language not in self.translations:
            self.logger.warning(f"当前语言 {self.current_language} 没有翻译文件，使用英语")
            self.current_language = "en"
    
    def get_available_languages(self) -> Dict[str, str]:
        """获取支持的语言列表"""
        return self.supported_languages.copy()
    
    def get_current_language(self) -> str:
        """获取当前语言代码"""
        return self.current_language
    
    def get_current_language_name(self) -> str:
        """获取当前语言显示名称"""
        return self.supported_languages.get(self.current_language, self.current_language)
    
    def set_language(self, language_code: str) -> bool:
        """设置当前语言"""
        if language_code not in self.supported_languages:
            self.logger.error(f"不支持的语言代码: {language_code}")
            return False
        
        if language_code not in self.translations:
            self.logger.error(f"语言 {language_code} 的翻译文件不存在")
            return False
        
        if language_code == self.current_language:
            return True
        
        old_language = self.current_language
        self.current_language = language_code
        self._save_settings()
        
        self.logger.info(f"语言已切换: {old_language} -> {language_code}")
        self.language_changed.emit(language_code)
        return True
    
    def translate(self, key: str, default: str = None) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键名
            default: 默认文本（当翻译不存在时使用）
        
        Returns:
            翻译后的文本
        """
        # 首先尝试当前语言
        translation = self.translations.get(self.current_language, {}).get(key)
        
        # 如果当前语言没有翻译，尝试英语
        if translation is None and self.current_language != "en":
            translation = self.translations.get("en", {}).get(key)
        
        # 如果都没有找到，返回默认值或键名
        if translation is None:
            if default is not None:
                return default
            self.logger.warning(f"翻译键 '{key}' 不存在")
            return key
        
        return translation
    
    def translate_with_context(self, key: str, context: str, default: str = None) -> str:
        """
        获取带上下文的翻译文本
        
        Args:
            key: 翻译键名
            context: 上下文信息
            default: 默认文本
        
        Returns:
            翻译后的文本
        """
        # 构建上下文键名
        context_key = f"{key}_{context}"
        translation = self.translate(context_key, default)
        
        # 如果上下文翻译不存在，使用普通翻译
        if translation == context_key and default is None:
            return self.translate(key)
        
        return translation
    
    def get_translation_dict(self, language_code: str = None) -> Dict[str, str]:
        """
        获取指定语言的完整翻译字典
        
        Args:
            language_code: 语言代码，默认为当前语言
        
        Returns:
            翻译字典
        """
        if language_code is None:
            language_code = self.current_language
        
        return self.translations.get(language_code, {}).copy()
    
    def has_translation(self, key: str, language_code: str = None) -> bool:
        """
        检查指定语言是否有指定的翻译
        
        Args:
            key: 翻译键名
            language_code: 语言代码，默认为当前语言
        
        Returns:
            是否存在翻译
        """
        if language_code is None:
            language_code = self.current_language
        
        return key in self.translations.get(language_code, {})
    
    def reload_translations(self) -> bool:
        """重新加载所有翻译文件"""
        try:
            self.translations.clear()
            self._load_translations()
            self.logger.info("翻译文件重新加载完成")
            return True
        except Exception as e:
            self.logger.error(f"重新加载翻译文件失败: {e}")
            return False
    
    def export_translations(self, language_code: str, output_file: str) -> bool:
        """
        导出指定语言的翻译到文件
        
        Args:
            language_code: 语言代码
            output_file: 输出文件路径
        
        Returns:
            是否导出成功
        """
        try:
            translations = self.translations.get(language_code, {})
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            self.logger.info(f"成功导出翻译文件: {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"导出翻译文件失败: {e}")
            return False
    
    def get_language_display_name(self, language_code: str) -> str:
        """获取语言的显示名称"""
        return self.supported_languages.get(language_code, language_code)
    
    def reset_to_system_language(self) -> bool:
        """重置为系统语言"""
        system_language = self._detect_system_language()
        if system_language and system_language in self.supported_languages:
            return self.set_language(system_language)
        return False
    
    def is_first_launch(self) -> bool:
        """检查是否为首次启动"""
        return not self.settings.contains("language")
    
    def get_system_language_info(self) -> Dict[str, Any]:
        """获取系统语言信息"""
        system_lang = self._detect_system_language()
        return {
            "detected_language": system_lang,
            "is_supported": system_lang in self.supported_languages if system_lang else False,
            "display_name": self.supported_languages.get(system_lang, system_lang) if system_lang else None,
            "is_first_launch": self.is_first_launch()
        }


# 全局语言管理器实例
_language_manager_instance: Optional[LanguageManager] = None


def get_language_manager() -> LanguageManager:
    """获取全局语言管理器实例"""
    global _language_manager_instance
    if _language_manager_instance is None:
        _language_manager_instance = LanguageManager()
    return _language_manager_instance


def _(key: str, default: str = None) -> str:
    """
    简化的翻译函数
    
    Args:
        key: 翻译键名
        default: 默认文本
    
    Returns:
        翻译后的文本
    """
    return get_language_manager().translate(key, default)


def set_language(language_code: str) -> bool:
    """
    设置当前语言
    
    Args:
        language_code: 语言代码
    
    Returns:
        是否设置成功
    """
    return get_language_manager().set_language(language_code)