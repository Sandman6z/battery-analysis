#!/usr/bin/env python3
"""
Internationalization (i18n) Module

This module provides internationalization support using .po files directly.
"""

import os
import locale
import logging
import re
from pathlib import Path
from typing import Dict, Optional, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Module constants
LOCALEDIR = Path(__file__).parent.parent.parent.parent / "locale"

# Global translation registry (legacy - now using PO translator)
_translations: Dict[str, Dict[str, str]] = {}
_current_locale = "en"  # Default locale


class SimplePOTranslator:
    """Simple translator that uses .po files directly"""
    
    def __init__(self):
        self.translations = {}
        self.current_locale = 'en'
    
    def parse_po_file(self, po_file_path: Path):
        """Parse a .po file and extract translations"""
        translations = {}
        
        try:
            with open(po_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex-based parsing
            msgid_pattern = r'msgid\s+"([^"]*)"'
            msgstr_pattern = r'msgstr\s+"([^"]*)"'
            
            msgid_matches = list(re.finditer(msgid_pattern, content))
            msgstr_matches = list(re.finditer(msgstr_pattern, content))
            
            for i in range(min(len(msgid_matches), len(msgstr_matches))):
                msgid = msgid_matches[i].group(1)
                msgstr = msgstr_matches[i].group(1)
                
                # Skip empty msgid (header)
                if not msgid.strip():
                    continue
                
                translations[msgid] = msgstr
            
            logger.info(f"Parsed {len(translations)} translations from {po_file_path}")
            return translations
            
        except Exception as e:
            logger.error(f"Error parsing {po_file_path}: {e}")
            return {}
    
    def load_locale(self, locale_code: str):
        """Load translations for a specific locale"""
        po_file = LOCALEDIR / locale_code / "LC_MESSAGES" / "messages.po"
        
        if not po_file.exists():
            logger.warning(f"Translation file not found: {po_file}")
            return False
        
        self.translations = self.parse_po_file(po_file)
        self.current_locale = locale_code
        
        logger.info(f"Loaded {len(self.translations)} translations for {locale_code}")
        return True
    
    def _(self, text: str, context: Optional[str] = None):
        """Get translation for text"""
        if context:
            # Handle context-aware translations if needed
            key = f"{context}:{text}"
        else:
            key = text
        
        return self.translations.get(key, text)


def get_available_locales() -> List[str]:
    """
    Get list of available locales with translation files.
    
    Returns:
        List of available locale codes
    """
    available = []
    locale_dir = LOCALEDIR
    
    if not locale_dir.exists():
        logger.warning(f"Locale directory not found: {locale_dir}")
        return available
    
    for locale_path in locale_dir.iterdir():
        if locale_path.is_dir():
            po_file = locale_path / "LC_MESSAGES" / "messages.po"
            if po_file.exists():
                available.append(locale_path.name)
    
    return sorted(available)


def set_locale(locale_code: str) -> bool:
    """
    Set the current locale for translations.
    
    Args:
        locale_code: Locale code (e.g., 'en', 'zh_CN')
        
    Returns:
        True if locale was set successfully
    """
    global _current_locale
    
    logger.info(f"Setting locale to: {locale_code}")
    
    if locale_code not in get_available_locales():
        logger.warning(f"Locale '{locale_code}' not available")
        return False
    
    try:
        # Load translation using PO translator
        logger.info(f"Loading translation for {locale_code}")
        if _po_translator.load_locale(locale_code):
            _translations[locale_code] = _po_translator.translations
            _current_locale = locale_code
            logger.info(f"Locale set to: {locale_code}")
            return True
        else:
            logger.error(f"Failed to load translations for {locale_code}")
            return False
        
    except Exception as e:
        logger.error(f"Failed to set locale '{locale_code}': {e}")
        import traceback
        traceback.print_exc()
        return False


def _(text: str, context: Optional[str] = None) -> str:
    """
    Translation function following gettext conventions.
    
    Args:
        text: Text to translate
        context: Optional context for disambiguation
        
    Returns:
        Translated text or original if translation not found
    """
    try:
        # Use the PO translator to get the translation
        return _po_translator._(text, context)
    except Exception as e:
        logging.warning(f"Translation error for '{text}': {e}")
        return text


def pgettext(context: str, text: str) -> str:
    """
    Context-aware translation function.
    
    Args:
        context: Context for disambiguation
        text: Text to translate
        
    Returns:
        Translated text or original if translation not found
    """
    try:
        return _(text, context)
    except Exception as e:
        logging.warning(f"Context translation error for '{context}:{text}': {e}")
        return text


# Global translator instance
_po_translator = SimplePOTranslator()


def detect_system_locale() -> str:
    """
    Detect the system locale.
    
    Returns:
        Locale code (e.g., 'en', 'zh_CN') or 'en' as fallback
    """
    try:
        # Try to get system locale
        try:
            # 使用推荐的替代方法获取系统区域设置
            try:
                # Python 3.11+ 推荐的方法
                import locale
                system_locale = locale.getlocale()[0]
            except (AttributeError, TypeError):
                # 降级到旧方法（仍然支持向后兼容）
                locale_result = locale.getdefaultlocale()
                
                # Handle different possible return types from getdefaultlocale()
                if isinstance(locale_result, tuple):
                    if len(locale_result) >= 2:
                        system_locale = locale_result[0]  # First element is usually the locale
                    elif len(locale_result) == 1:
                        system_locale = locale_result[0] if locale_result[0] else None
                    else:
                        system_locale = None
                else:
                    # Handle case where getdefaultlocale() returns a single value
                    system_locale = locale_result if locale_result else None
                
        except ValueError:
            # getdefaultlocale() can throw ValueError on some systems
            system_locale = None
        except Exception:
            # Handle any other unexpected errors
            system_locale = None
        
        if system_locale:
            # Extract language code from locale (e.g., 'en_US' -> 'en')
            if isinstance(system_locale, str):
                lang_code = system_locale.split('_')[0]
                
                # Check if we have translations for this language
                if lang_code in get_available_locales():
                    return lang_code
                
                # Special case for Chinese variants
                if lang_code == 'zh':
                    if 'CN' in system_locale:
                        return 'zh_CN'
                    elif 'TW' in system_locale:
                        return 'zh_TW'
    except Exception as e:
        logger.error(f"Failed to detect system locale: {e}")
    
    # Fallback to English
    return 'en'


def ngettext(singular: str, plural: str, n: int) -> str:
    """
    Plural form translation function.
    
    Args:
        singular: Singular form
        plural: Plural form
        n: Number for plural selection
        
    Returns:
        Translated text in appropriate plural form
    """
    try:
        if _current_locale in _translations:
            return _translations[_current_locale].ngettext(singular, plural, n)
    except Exception as e:
        logging.warning(f"Translation error for plural '{singular}/{plural}': {e}")
    
    return singular if n == 1 else plural


def get_current_locale() -> str:
    """
    Get the current locale.
    
    Returns:
        Current locale code
    """
    return _current_locale


def initialize_default_locale() -> bool:
    """
    Initialize locale based on system settings or default.
    
    Returns:
        True if initialization successful
    """
    # Try to detect system locale
    try:
        # 使用推荐的替代方法获取系统区域设置
        try:
            # Python 3.11+ 推荐的方法
            system_locale = locale.getlocale()[0]
        except (AttributeError, TypeError):
            # 降级到旧方法（仍然支持向后兼容）
            locale_result = locale.getdefaultlocale()
            
            # Handle different possible return types from getdefaultlocale()
            if isinstance(locale_result, tuple):
                if len(locale_result) >= 2:
                    system_locale = locale_result[0]
                elif len(locale_result) == 1:
                    system_locale = locale_result[0] if locale_result[0] else None
                else:
                    system_locale = None
            else:
                # Handle case where getdefaultlocale() returns a single value
                system_locale = locale_result if locale_result else None
            
    except ValueError:
        # getdefaultlocale() can throw ValueError on some systems
        system_locale = None
    except Exception:
        # Handle any other unexpected errors
        system_locale = None
    
    if system_locale and isinstance(system_locale, str):
        # Extract language code
        if '_' in system_locale:
            locale_code = system_locale.split('_')[0]
        else:
            locale_code = system_locale
    else:
        locale_code = "en"  # Default fallback
    
    # Try to set locale
    if set_locale(locale_code):
        return True
    
    # Fallback to English
    return set_locale("en")


# Global translator instance
_po_translator = SimplePOTranslator()

# Initialize with default locale
initialize_default_locale()

logger.info(f"i18n module initialized with locale: {_current_locale}")