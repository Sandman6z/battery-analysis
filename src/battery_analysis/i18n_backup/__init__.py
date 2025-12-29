"""
Internationalization (i18n) module for Battery Analysis application.

This module provides standard gettext-based internationalization support
following industry best practices for Python applications.
"""

import gettext
import os
import locale
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Application domain for translations
DOMAIN = "messages"
LOCALEDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "locale")

# Current locale setting
_current_locale = "en"

# Translation cache
_translations: Dict[str, gettext.NullTranslations] = {}


def _(text: str, context: Optional[str] = None) -> str:
    """
    Translation function following gettext conventions.
    
    Args:
        text: Text to translate
        context: Optional context for disambiguation
        
    Returns:
        Translated text or original if translation not found
    """
    if context:
        text_with_context = f"{context}\x04{text}"
    else:
        text_with_context = text
    
    try:
        if _current_locale in _translations:
            translation = _translations[_current_locale].gettext(text_with_context)
            if translation != text_with_context:
                return translation
            # Fallback to context-aware lookup
            if context:
                return _translations[_current_locale].gettext(text)
    except Exception as e:
        logging.warning(f"Translation error for '{text}': {e}")
    
    return text


def ngettext(singular: str, plural: str, n: int) -> str:
    """
    Plural forms translation function.
    
    Args:
        singular: Singular form
        plural: Plural form
        n: Number to determine plural form
        
    Returns:
        Appropriate translation based on n
    """
    try:
        if _current_locale in _translations:
            return _translations[_current_locale].ngettext(singular, plural, n)
    except Exception as e:
        logging.warning(f"Plural translation error: {e}")
    
    return singular if n == 1 else plural


def pgettext(context: str, text: str) -> str:
    """
    Context-aware translation function.
    
    Args:
        context: Context for disambiguation
        text: Text to translate
        
    Returns:
        Translated text
    """
    try:
        if _current_locale in _translations:
            return _translations[_current_locale].pgettext(context, text)
    except Exception as e:
        logging.warning(f"Context translation error: {e}")
    
    return text


def get_available_locales() -> Dict[str, str]:
    """
    Get available locales based on existing .mo files.
    
    Returns:
        Dictionary mapping locale codes to display names
    """
    locales = {
        "en": "English",
        "zh_CN": "中文(简体)"
    }
    
    # Check which locales actually have translations
    available = {}
    for locale_code, display_name in locales.items():
        mo_file = os.path.join(LOCALEDIR, locale_code, "LC_MESSAGES", f"{DOMAIN}.mo")
        if os.path.exists(mo_file):
            available[locale_code] = display_name
    
    return available


def set_locale(locale_code: str) -> bool:
    """
    Set the current locale for translations.
    
    Args:
        locale_code: Locale code (e.g., 'en', 'zh_CN')
        
    Returns:
        True if locale was set successfully
    """
    global _current_locale
    
    if locale_code not in get_available_locales():
        logging.warning(f"Locale '{locale_code}' not available")
        return False
    
    try:
        # Load translation
        translation = gettext.translation(
            DOMAIN,
            localedir=LOCALEDIR,
            languages=[locale_code],
            fallback=True
        )
        
        _translations[locale_code] = translation
        _current_locale = locale_code
        
        # Install the translation globally
        translation.install()
        
        logging.info(f"Locale set to: {locale_code}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to set locale '{locale_code}': {e}")
        return False


def get_current_locale() -> str:
    """
    Get the current locale code.
    
    Returns:
        Current locale code
    """
    return _current_locale


def detect_system_locale() -> str:
    """
    Detect the system locale for initial setup.
    
    Returns:
        Detected locale code or 'en' as fallback
    """
    try:
        # Try to get system locale
        try:
            system_locale = locale.getdefaultlocale()[0]
        except ValueError:
            # getdefaultlocale() can throw ValueError on some systems
            system_locale = None
        
        if system_locale:
            # Map system locale to our supported locales
            if system_locale.startswith("zh"):
                return "zh_CN"
            elif system_locale.startswith("en"):
                return "en"
                
    except Exception as e:
        logging.warning(f"Could not detect system locale: {e}")
    
    return "en"  # Default fallback


def initialize_i18n(default_locale: Optional[str] = None) -> bool:
    """
    Initialize internationalization system.
    
    Args:
        default_locale: Default locale to use, if None will detect system locale
        
    Returns:
        True if initialization successful
    """
    if default_locale is None:
        default_locale = detect_system_locale()
    
    logging.info(f"Initializing i18n with locale: {default_locale}")
    
    return set_locale(default_locale)


# Initialize on import
initialize_i18n()